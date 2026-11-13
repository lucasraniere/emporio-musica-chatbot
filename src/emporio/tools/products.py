import json
import unicodedata

from typing import Literal
from langchain_core.tools import tool

from emporio.db_helper import query


def _normalize(text: str) -> str:
    """Lowercase and strip accents"""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _availability(p: dict) -> str:
    if p["status"] == "discontinued":
        return "DESCONTINUADO: não faz mais parte do catálogo"
    if p["status"] == "coming_soon":
        return "EM BREVE: ainda não está à venda"
    if p["stock_quantity"] == 0:
        return "INDISPONÍVEL: sem estoque no momento"
    return f"Disponível ({p['stock_quantity']} em estoque)"


def _price(p: dict) -> str:
    if p["discount_percent"] is None:
        return f"{_brl(p['list_price_brl'])} (no PIX: {_brl(p['pix_price_brl'])})"
    return (
        f"{_brl(p['final_price_brl'])} na promoção \"{p['promotion_name']}\" "
        f"({p['discount_percent']:g}% de desconto sobre {_brl(p['list_price_brl'])}; "
        "o desconto do PIX não se aplica a preço promocional)"
    )


def _find(product: str) -> list[dict]:
    rows = query("SELECT * FROM product_catalog")
    if product.strip().isdigit():
        return [p for p in rows if p["product_id"] == int(product)]
    words = _normalize(product).split()
    return [p for p in rows if all(w in _normalize(p["name"]) for w in words)]


@tool
def get_product_details(product: str) -> str:
    """Consulta os dados atuais de UM produto: preço, promoção, estoque e especificações.

    Use quando o cliente perguntar sobre um produto específico (ex.: "quanto custa o
    Takamine GD20?", "tem o Yamaha C40?"). Sempre consulte antes de informar preço
    ou disponibilidade. Para listar ou filtrar vários produtos, use search_products.

    Args:
        product: nome (ou parte do nome) do produto, ex.: "Takamine GD20", ou o ID numérico.
    """
    matches = _find(product)
    if not matches:
        return f'Nenhum produto encontrado para "{product}". Tente search_products com outros termos.'
    if len(matches) > 1:
        options = "\n".join(f"- {p['name']} (ID {p['product_id']})" for p in matches[:8])
        return f"{len(matches)} produtos correspondem. Pergunte ao cliente qual deles:\n{options}"

    p = matches[0]
    specs = ", ".join(f"{k}: {v}" for k, v in json.loads(p["specs"]).items())
    return (
        f"{p['name']} (ID {p['product_id']})\n"
        f"Categoria: {p['category']}\n"
        f"Situação: {_availability(p)}\n"
        f"Preço: {_price(p)}\n"
        f"Descrição: {p['description']}\n"
        f"Especificações: {specs}"
    )


Category = Literal[
    "Guitarras",
    "Baixos",
    "Baterias e Percussão",
    "Teclados e Pianos",
    "Violões",
    "Instrumentos de Sopro (Madeiras)",
    "Instrumentos de Sopro (Metais)",
    "Cordas Orquestrais",
    "Ukuleles",
]

MAX_RESULTS = 10


def _keyword_filter(rows: list[dict], keywords: str) -> list[dict]:
    """Keep the rows that match the most keywords (name, category, description, specs)."""
    words = [w for w in _normalize(keywords).split() if len(w) > 2]
    if not words:
        return rows

    def score(p: dict) -> int:
        text = _normalize(f"{p['name']} {p['category']} {p['description']} {p['specs']}")
        return sum(w in text for w in words)

    best = max((score(p) for p in rows), default=0)
    return [p for p in rows if score(p) == best] if best else []


@tool
def search_products(
    keywords: str | None = None,
    category: Category | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    only_available: bool = True,
) -> str:
    """Lista produtos do catálogo com preço e disponibilidade atuais, do mais barato ao mais caro.

    Use para perguntas de busca ou comparação (ex.: "violões até R$ 1000", "tem ukulele
    tenor?", "guitarras da Fender"). Todos os filtros são opcionais e combináveis.
    Para os detalhes completos de um produto específico, use get_product_details.

    Args:
        keywords: palavras-chave soltas (marca, modelo, característica), ex.: "yamaha nylon".
            Não envie frases inteiras.
        category: categoria exata do catálogo.
        min_price: preço mínimo em reais.
        max_price: preço máximo em reais.
        only_available: True (padrão) mostra só o que pode ser vendido agora. Use False
            para incluir itens sem estoque, descontinuados ou em breve.
    """
    rows = query("SELECT * FROM product_catalog ORDER BY final_price_brl")
    if category:
        rows = [p for p in rows if p["category"] == category]
    if min_price is not None:
        rows = [p for p in rows if p["final_price_brl"] >= min_price]
    if max_price is not None:
        rows = [p for p in rows if p["final_price_brl"] <= max_price]
    if keywords:
        rows = _keyword_filter(rows, keywords)

    hidden = [p for p in rows if not p["is_available"]]
    if only_available:
        rows = [p for p in rows if p["is_available"]]

    if not rows:
        note = f" ({len(hidden)} item(ns) indisponível(is) omitido(s))" if only_available and hidden else ""
        return f"Nenhum produto encontrado com esses filtros{note}."

    lines = [
        f"- {p['name']} (ID {p['product_id']}) | {p['category']} | {_price(p)} | {_availability(p)}"
        for p in rows[:MAX_RESULTS]
    ]
    header = f"{len(rows)} produto(s) encontrado(s)"
    if len(rows) > MAX_RESULTS:
        header += f", mostrando os {MAX_RESULTS} mais baratos"
    if only_available and hidden:
        header += f" ({len(hidden)} indisponível(is) omitido(s))"
    return header + ":\n" + "\n".join(lines)


@tool
def list_active_promotions() -> str:
    """Lista os produtos que estão em promoção AGORA, com preço original e promocional.

    Use quando o cliente perguntar por promoções, descontos ou ofertas em geral, ou
    para confirmar se uma campanha (ex.: Black Friday) está valendo. Só o que esta
    tool retorna está em promoção; nunca prometa desconto que não apareça aqui.
    """
    rows = query(
        "SELECT * FROM product_catalog WHERE discount_percent IS NOT NULL "
        "ORDER BY discount_percent DESC"
    )
    if not rows:
        return "Não há nenhuma promoção ativa no momento."
    lines = [
        f"- {p['name']} (ID {p['product_id']}) | {p['category']} | {_price(p)} | {_availability(p)}"
        for p in rows
    ]
    return f"{len(rows)} produto(s) em promoção no momento:\n" + "\n".join(lines)


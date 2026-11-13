from langchain_core.tools import tool

from emporio.config import settings
from emporio.rag.embeddings import get_vector_store

@tool
def search_policies(query: str) -> str:
    """Busca trechos do manual de políticas e procedimentos da Empório da Música.

    Use para regras e informações gerais da loja: trocas e devoluções, garantia,
    formas de pagamento e parcelamento, frete e prazos de entrega, horário de
    funcionamento, endereço e contatos, regras de promoções e privacidade.
    NÃO use para preço, estoque ou status de pedido; para isso existem outras tools.

    Se os trechos retornados não responderem à pergunta, busque de novo com outras
    palavras (ex.: "avaria no transporte" em vez de "chegou quebrado").

    Args:
        query: pergunta ou palavras-chave em português, ex.: "prazo para devolução".
    """
    docs = get_vector_store().similarity_search(query, k=settings.retriever_k)
    if not docs:
        return "Nenhum trecho do manual encontrado para essa busca."
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

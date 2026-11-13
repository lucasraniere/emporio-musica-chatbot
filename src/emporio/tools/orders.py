import re
from datetime import date

from langchain_core.tools import tool

from emporio.config import settings
from emporio.db_helper import query
from emporio.tools.products import _brl

NOT_FOUND = (
    "Pedido não localizado com esses dados. Confirme com o cliente o número do pedido "
    "e o e-mail ou telefone usados na compra."
)

STATUS = {
    "pending": "Pendente (ainda não confirmado)",
    "confirmed": "Confirmado (ainda não enviado)",
    "shipped": "Enviado",
    "delivered": "Entregue",
    "cancelled": "Cancelado",
}


def _today() -> date:
    # Same clock as the system prompt, so REFERENCE_DATE applies to both.
    return settings.now().date()


def _date(iso: str | None) -> str:
    return date.fromisoformat(iso).strftime("%d/%m/%Y") if iso else "não informado"


def _payment(method: str) -> str:
    names = {"pix": "PIX", "boleto": "Boleto bancário", "debit": "Cartão de débito"}
    if method.startswith("credit_"):
        return f"Cartão de crédito em {method.removeprefix('credit_')}"
    return names.get(method, method)


def _contact_matches(order: dict, contact: str) -> bool:
    contact = contact.strip().lower()
    if "@" in contact:
        return contact == order["email"]
    digits = re.sub(r"\D", "", contact)
    # Accept the phone with or without the area code.
    return len(digits) >= 9 and order["phone_digits"].endswith(digits)


@tool
def get_order_status(order_id: int, contact: str) -> str:
    """Consulta o status de um pedido: situação, itens, valor, rastreio e previsão de entrega.

    Use quando o cliente perguntar sobre um pedido (status, rastreamento, entrega) ou
    quiser trocar/devolver algo que comprou. Exige o número do pedido E o e-mail ou
    telefone do cadastro, para confirmar a identidade. Se o cliente não informou os
    dois, peça antes de chamar esta tool. Nunca chame com dados inventados.

    Args:
        order_id: número do pedido informado pelo cliente.
        contact: e-mail ou telefone que o cliente usou na compra.
    """
    rows = query(
        """
        SELECT o.*, c.name AS customer_name, c.email, c.phone_digits
        FROM orders o JOIN customers c ON c.customer_id = o.customer_id
        WHERE o.order_id = ?
        """,
        (order_id,),
    )
    # Same answer for "no such order" and "wrong contact": never confirm an order exists.
    if not rows or not _contact_matches(rows[0], contact):
        return NOT_FOUND

    order = rows[0]
    items = query(
        """
        SELECT i.quantity, p.name
        FROM order_items i JOIN products p ON p.product_id = i.product_id
        WHERE i.order_id = ?
        """,
        (order_id,),
    )
    lines = [
        f"Pedido {order['order_id']} de {order['customer_name'].split()[0]}",
        f"Situação: {STATUS.get(order['status'], order['status'])}",
        f"Data da compra: {_date(order['order_date'])}",
        "Itens: " + "; ".join(f"{i['quantity']}x {i['name']}" for i in items),
        f"Valor total: {_brl(order['total_brl'])} ({_payment(order['payment_method'])})",
    ]
    if order["tracking_code"]:
        lines.append(f"Código de rastreio: {order['tracking_code']}")
    if order["estimated_delivery"]:
        lines.append(f"Previsão de entrega: {_date(order['estimated_delivery'])}")
    if order["notes"]:
        lines.append(f"Observação: {order['notes']}")
    if order["status"] == "delivered" and order["estimated_delivery"]:
        days = (_today() - date.fromisoformat(order["estimated_delivery"])).days
        lines.append(
            f"Dias desde a entrega prevista: {days} (hoje é {_today().strftime('%d/%m/%Y')}). "
            "Use esse número para avaliar prazos de devolução, troca e garantia."
        )
    return "\n".join(lines)

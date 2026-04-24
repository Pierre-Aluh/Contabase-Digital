"""Utilitarios de formatacao pt-BR e Decimal."""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation


def parse_decimal(value: str | int | float | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))

    raw = str(value).strip().replace("R$", "").replace(" ", "")
    if not raw:
        raise ValueError(f"Valor decimal invalido: {value}")

    if "," in raw and "." in raw:
        # Decide decimal separator by the rightmost symbol.
        if raw.rfind(",") > raw.rfind("."):
            # pt-BR style: 1.234,56
            normalized = raw.replace(".", "").replace(",", ".")
        else:
            # en-US style: 1,234.56
            normalized = raw.replace(",", "")
    elif "," in raw:
        # 1234,56
        normalized = raw.replace(",", ".")
    else:
        # Keep single decimal dot. If there are multiple dots, treat as thousand separators.
        dot_count = raw.count(".")
        normalized = raw if dot_count <= 1 else raw.replace(".", "")

    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"Valor decimal invalido: {value}") from exc


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_brl(value: Decimal | int | float | str) -> str:
    amount = quantize_money(parse_decimal(value))
    raw = f"{amount:.2f}"
    integer, cents = raw.split(".")
    integer = f"{int(integer):,}".replace(",", ".")
    return f"R$ {integer},{cents}"


def format_date_br(value: date | datetime) -> str:
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d/%m/%Y")

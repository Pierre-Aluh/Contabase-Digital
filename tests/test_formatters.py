from decimal import Decimal

from app.utils.formatters import parse_decimal


def test_parse_decimal_accepts_pt_br_and_en_us_formats() -> None:
    assert parse_decimal("50.000,00") == Decimal("50000.00")
    assert parse_decimal("1000.00") == Decimal("1000.00")
    assert parse_decimal("1,000.25") == Decimal("1000.25")
    assert parse_decimal("1000,25") == Decimal("1000.25")

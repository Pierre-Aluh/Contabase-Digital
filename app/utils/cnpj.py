"""Validacao de CNPJ."""

from __future__ import annotations

import re


def sanitize_cnpj(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cnpj(value: str) -> bool:
    cnpj = sanitize_cnpj(value)
    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    def calc_digit(base: str, multipliers: list[int]) -> int:
        total = sum(int(n) * m for n, m in zip(base, multipliers))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    digit1 = calc_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    digit2 = calc_digit(cnpj[:12] + str(digit1), [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])

    return cnpj[-2:] == f"{digit1}{digit2}"

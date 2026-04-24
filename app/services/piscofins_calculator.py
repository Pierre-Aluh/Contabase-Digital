"""Calculadora de PIS e COFINS com Decimal e arredondamento financeiro."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.utils.formatters import quantize_money


@dataclass(frozen=True)
class PISCOFINSResult:
    base_original: Decimal
    adicoes: Decimal
    reducoes: Decimal
    base_final: Decimal
    aliquota: Decimal
    imposto_devido: Decimal


class PISCOFINSCalculator:
    """Apura PIS/COFINS por competencia com base ajustada."""

    @staticmethod
    def calculate(
        base_original: Decimal,
        adicoes: Decimal,
        reducoes: Decimal,
        aliquota: Decimal,
    ) -> PISCOFINSResult:
        base = quantize_money(base_original + adicoes - reducoes)
        base_final = base if base > 0 else Decimal("0.00")
        imposto = quantize_money(base_final * aliquota)
        return PISCOFINSResult(
            base_original=quantize_money(base_original),
            adicoes=quantize_money(adicoes),
            reducoes=quantize_money(reducoes),
            base_final=quantize_money(base_final),
            aliquota=aliquota,
            imposto_devido=imposto,
        )

"""Calculadora de IRPJ/CSLL no lucro presumido."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.utils.formatters import quantize_money


@dataclass(frozen=True)
class IRPJCSLLResult:
    base_original: Decimal
    adicoes: Decimal
    reducoes: Decimal
    base_final: Decimal
    percentual_presuncao: Decimal
    aliquota: Decimal
    imposto_devido: Decimal


class IRPJCSLLCalculator:
    """Apura IRPJ e CSLL aplicando presuncao apos ajustes de receita."""

    @staticmethod
    def calculate(
        receita_base: Decimal,
        adicoes_receita: Decimal,
        reducoes_receita: Decimal,
        percentual_presuncao: Decimal,
        aliquota: Decimal,
    ) -> IRPJCSLLResult:
        base_original = quantize_money(receita_base * percentual_presuncao)
        adicoes = quantize_money(adicoes_receita * percentual_presuncao)
        reducoes = quantize_money(reducoes_receita * percentual_presuncao)
        base_final = quantize_money(base_original + adicoes - reducoes)
        if base_final < 0:
            base_final = Decimal("0.00")

        imposto = quantize_money(base_final * aliquota)
        return IRPJCSLLResult(
            base_original=base_original,
            adicoes=adicoes,
            reducoes=reducoes,
            base_final=base_final,
            percentual_presuncao=percentual_presuncao,
            aliquota=aliquota,
            imposto_devido=imposto,
        )

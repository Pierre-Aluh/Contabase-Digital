"""Consolidacao de memoria fiscal entre obras."""

from __future__ import annotations

from decimal import Decimal

from app.models.enums import TributoAlvo
from app.utils.formatters import quantize_money


class ConsolidationService:
    """Soma memoria de calculo por tributo para visao consolidada."""

    @staticmethod
    def consolidate_summaries(
        summaries: list[dict[str, dict[str, Decimal]]],
    ) -> dict[str, dict[str, Decimal]]:
        consolidated: dict[str, dict[str, Decimal]] = {
            tributo.value: {
                "base_original": Decimal("0.00"),
                "adicoes": Decimal("0.00"),
                "reducoes": Decimal("0.00"),
                "base_final": Decimal("0.00"),
                "imposto_devido": Decimal("0.00"),
            }
            for tributo in TributoAlvo
        }

        for summary in summaries:
            for tributo, values in summary.items():
                for key in ["base_original", "adicoes", "reducoes", "base_final", "imposto_devido"]:
                    consolidated[tributo][key] += values.get(key, Decimal("0.00"))

        for tributo in consolidated.values():
            for key in ["base_original", "adicoes", "reducoes", "base_final", "imposto_devido"]:
                tributo[key] = quantize_money(tributo[key])

        return consolidated

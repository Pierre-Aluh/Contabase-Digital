"""Servico de vencimentos fiscais parametrizados."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.competencia import Competencia
from app.models.enums import TributoAlvo
from app.models.parametro_sistema import ParametroSistema


@dataclass(frozen=True)
class DueDateRule:
    tributo: TributoAlvo
    codigo_receita: str
    dia_vencimento: int


class DueDateService:
    """Resolve codigo de receita e vencimento com fallback seguro."""

    def resolve_rules(self) -> dict[TributoAlvo, DueDateRule]:
        defaults: dict[TributoAlvo, tuple[str, int]] = {
            TributoAlvo.PIS: ("8109", 25),
            TributoAlvo.COFINS: ("2172", 25),
            TributoAlvo.IRPJ: ("2089", 25),
            TributoAlvo.CSLL: ("2372", 25),
            TributoAlvo.IRPJ_ADICIONAL: ("2089", 25),
            TributoAlvo.ISS: ("ISS", 5),
        }

        with get_session() as session:
            params = session.execute(
                select(ParametroSistema).where(
                    ParametroSistema.chave.in_(
                        [
                            "COD_RECEITA_PIS",
                            "COD_RECEITA_COFINS",
                            "COD_RECEITA_IRPJ",
                            "COD_RECEITA_CSLL",
                            "COD_RECEITA_IRPJ_ADICIONAL",
                            "COD_RECEITA_ISS",
                            "VENCIMENTO_DIA_PIS_COFINS",
                            "VENCIMENTO_DIA_IRPJ_CSLL",
                            "VENCIMENTO_DIA_ISS_PADRAO",
                        ]
                    ),
                    ParametroSistema.ativo.is_(True),
                )
            ).scalars().all()

        by_key = {p.chave: p for p in params}

        def _text(key: str, fallback: str) -> str:
            p = by_key.get(key)
            if p and p.valor_texto:
                return str(p.valor_texto)
            return fallback

        def _int(key: str, fallback: int) -> int:
            p = by_key.get(key)
            if p and p.valor_inteiro:
                return int(p.valor_inteiro)
            return fallback

        return {
            TributoAlvo.PIS: DueDateRule(
                tributo=TributoAlvo.PIS,
                codigo_receita=_text("COD_RECEITA_PIS", defaults[TributoAlvo.PIS][0]),
                dia_vencimento=_int("VENCIMENTO_DIA_PIS_COFINS", defaults[TributoAlvo.PIS][1]),
            ),
            TributoAlvo.COFINS: DueDateRule(
                tributo=TributoAlvo.COFINS,
                codigo_receita=_text("COD_RECEITA_COFINS", defaults[TributoAlvo.COFINS][0]),
                dia_vencimento=_int("VENCIMENTO_DIA_PIS_COFINS", defaults[TributoAlvo.COFINS][1]),
            ),
            TributoAlvo.IRPJ: DueDateRule(
                tributo=TributoAlvo.IRPJ,
                codigo_receita=_text("COD_RECEITA_IRPJ", defaults[TributoAlvo.IRPJ][0]),
                dia_vencimento=_int("VENCIMENTO_DIA_IRPJ_CSLL", defaults[TributoAlvo.IRPJ][1]),
            ),
            TributoAlvo.CSLL: DueDateRule(
                tributo=TributoAlvo.CSLL,
                codigo_receita=_text("COD_RECEITA_CSLL", defaults[TributoAlvo.CSLL][0]),
                dia_vencimento=_int("VENCIMENTO_DIA_IRPJ_CSLL", defaults[TributoAlvo.CSLL][1]),
            ),
            TributoAlvo.IRPJ_ADICIONAL: DueDateRule(
                tributo=TributoAlvo.IRPJ_ADICIONAL,
                codigo_receita=_text(
                    "COD_RECEITA_IRPJ_ADICIONAL",
                    defaults[TributoAlvo.IRPJ_ADICIONAL][0],
                ),
                dia_vencimento=_int(
                    "VENCIMENTO_DIA_IRPJ_CSLL",
                    defaults[TributoAlvo.IRPJ_ADICIONAL][1],
                ),
            ),
            TributoAlvo.ISS: DueDateRule(
                tributo=TributoAlvo.ISS,
                codigo_receita=_text("COD_RECEITA_ISS", defaults[TributoAlvo.ISS][0]),
                dia_vencimento=_int("VENCIMENTO_DIA_ISS_PADRAO", defaults[TributoAlvo.ISS][1]),
            ),
        }

    @staticmethod
    def compute_due_date(competencia: Competencia, day: int) -> date:
        next_month = competencia.mes + 1
        year = competencia.ano
        if next_month > 12:
            next_month = 1
            year += 1

        safe_day = max(1, min(day, 28))
        return date(year, next_month, safe_day)

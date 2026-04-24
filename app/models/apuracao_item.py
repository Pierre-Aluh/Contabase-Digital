"""Modelo da memoria de calculo detalhada da apuracao."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin
from app.models.enums import TributoAlvo

if TYPE_CHECKING:
    from app.models.apuracao import Apuracao


class ApuracaoItem(Base, IdMixin, TimestampMixin):
    __tablename__ = "apuracao_itens"

    apuracao_id: Mapped[int] = mapped_column(ForeignKey("apuracoes.id"), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    tributo: Mapped[TributoAlvo] = mapped_column(Enum(TributoAlvo), nullable=False)
    descricao_passo: Mapped[str] = mapped_column(String(255), nullable=False)
    base_calculo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    aliquota: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    valor_calculado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    apuracao: Mapped["Apuracao"] = relationship(back_populates="itens")


Index("ix_apuracao_itens_apuracao_id", ApuracaoItem.apuracao_id)

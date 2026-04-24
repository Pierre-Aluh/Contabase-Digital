"""Modelo de ajustes fiscais por lancamento e tributo."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin
from app.models.enums import TipoAjuste, TributoAlvo

if TYPE_CHECKING:
    from app.models.lancamento_fiscal import LancamentoFiscal


class AjusteFiscal(Base, IdMixin, TimestampMixin):
    __tablename__ = "ajustes_fiscais"

    lancamento_fiscal_id: Mapped[int] = mapped_column(
        ForeignKey("lancamentos_fiscais.id"),
        nullable=False,
    )
    tributo_alvo: Mapped[TributoAlvo] = mapped_column(Enum(TributoAlvo), nullable=False)
    tipo_ajuste: Mapped[TipoAjuste] = mapped_column(Enum(TipoAjuste), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    justificativa: Mapped[str] = mapped_column(String(500), nullable=False)
    documento_referencia: Mapped[str] = mapped_column(String(255), nullable=True)
    observacao: Mapped[str] = mapped_column(String(500), nullable=True)

    lancamento: Mapped["LancamentoFiscal"] = relationship(back_populates="ajustes")


Index("ix_ajustes_lancamento_id", AjusteFiscal.lancamento_fiscal_id)
Index("ix_ajustes_tributo_tipo", AjusteFiscal.tributo_alvo, AjusteFiscal.tipo_ajuste)

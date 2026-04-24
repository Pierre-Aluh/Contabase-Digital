"""Modelo de resultados de apuracao por obra ou consolidado."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.apuracao_item import ApuracaoItem
    from app.models.competencia import Competencia
    from app.models.empresa import Empresa
    from app.models.obra import Obra
    from app.models.obrigacao_vencimento import ObrigacaoVencimento


class Apuracao(Base, IdMixin, TimestampMixin):
    __tablename__ = "apuracoes"

    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=False)
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id"), nullable=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencias.id"), nullable=False)
    consolidada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    versao: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    apuracao_valida: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_impostos: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    memoria_resumo: Mapped[str] = mapped_column(String(1000), nullable=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="apuracoes")
    obra: Mapped["Obra"] = relationship(back_populates="apuracoes")
    competencia: Mapped["Competencia"] = relationship(back_populates="apuracoes")
    itens: Mapped[list["ApuracaoItem"]] = relationship(
        back_populates="apuracao",
        cascade="all, delete-orphan",
    )
    obrigacoes: Mapped[list["ObrigacaoVencimento"]] = relationship(back_populates="apuracao")


Index("ix_apuracoes_empresa_id", Apuracao.empresa_id)
Index("ix_apuracoes_obra_id", Apuracao.obra_id)
Index("ix_apuracoes_competencia_id", Apuracao.competencia_id)

"""Modelo de obrigacoes e vencimentos fiscais."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin
from app.models.enums import StatusObrigacao, TributoAlvo

if TYPE_CHECKING:
    from app.models.apuracao import Apuracao
    from app.models.competencia import Competencia
    from app.models.empresa import Empresa
    from app.models.obra import Obra


class ObrigacaoVencimento(Base, IdMixin, TimestampMixin):
    __tablename__ = "obrigacoes_vencimento"

    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=False)
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id"), nullable=True)
    apuracao_id: Mapped[int] = mapped_column(ForeignKey("apuracoes.id"), nullable=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencias.id"), nullable=False)

    tributo: Mapped[TributoAlvo] = mapped_column(Enum(TributoAlvo), nullable=False)
    codigo_receita: Mapped[str] = mapped_column(String(30), nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[StatusObrigacao] = mapped_column(
        Enum(StatusObrigacao),
        nullable=False,
        default=StatusObrigacao.EM_ABERTO,
    )
    pago_em: Mapped[date] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str] = mapped_column(String(500), nullable=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="obrigacoes")
    obra: Mapped["Obra"] = relationship(back_populates="obrigacoes")
    apuracao: Mapped["Apuracao"] = relationship(back_populates="obrigacoes")
    competencia: Mapped["Competencia"] = relationship(back_populates="obrigacoes")


Index("ix_obrigacoes_empresa_id", ObrigacaoVencimento.empresa_id)
Index("ix_obrigacoes_data_vencimento", ObrigacaoVencimento.data_vencimento)

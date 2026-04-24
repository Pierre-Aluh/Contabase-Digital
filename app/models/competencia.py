"""Modelo de competencias fiscais (MM/YYYY)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.apuracao import Apuracao
    from app.models.lancamento_fiscal import LancamentoFiscal
    from app.models.obrigacao_vencimento import ObrigacaoVencimento


class Competencia(Base, IdMixin, TimestampMixin):
    __tablename__ = "competencias"
    __table_args__ = (UniqueConstraint("ano", "mes", name="uq_competencias_ano_mes"),)

    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    referencia: Mapped[str] = mapped_column(String(7), nullable=False, unique=True)

    lancamentos: Mapped[list["LancamentoFiscal"]] = relationship(back_populates="competencia")
    apuracoes: Mapped[list["Apuracao"]] = relationship(back_populates="competencia")
    obrigacoes: Mapped[list["ObrigacaoVencimento"]] = relationship(back_populates="competencia")

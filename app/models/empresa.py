"""Modelo de empresas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.apuracao import Apuracao
    from app.models.auditoria_evento import AuditoriaEvento
    from app.models.lancamento_fiscal import LancamentoFiscal
    from app.models.obra import Obra
    from app.models.obrigacao_vencimento import ObrigacaoVencimento


class Empresa(Base, IdMixin, TimestampMixin):
    __tablename__ = "empresas"

    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    razao_social: Mapped[str] = mapped_column(String(180), nullable=False)
    nome_fantasia: Mapped[str] = mapped_column(String(180), nullable=True)
    email: Mapped[str] = mapped_column(String(150), nullable=True)
    telefone: Mapped[str] = mapped_column(String(30), nullable=True)
    status_ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    obras: Mapped[list["Obra"]] = relationship(back_populates="empresa")
    lancamentos: Mapped[list["LancamentoFiscal"]] = relationship(back_populates="empresa")
    apuracoes: Mapped[list["Apuracao"]] = relationship(back_populates="empresa")
    obrigacoes: Mapped[list["ObrigacaoVencimento"]] = relationship(back_populates="empresa")
    auditorias: Mapped[list["AuditoriaEvento"]] = relationship(back_populates="empresa")


Index("ix_empresas_razao_social", Empresa.razao_social)

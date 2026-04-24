"""Modelo de obras vinculadas a empresas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.apuracao import Apuracao
    from app.models.lancamento_fiscal import LancamentoFiscal
    from app.models.obrigacao_vencimento import ObrigacaoVencimento
    from app.models.empresa import Empresa
    from app.models.perfil_tributario import PerfilTributario


class Obra(Base, IdMixin, TimestampMixin):
    __tablename__ = "obras"
    __table_args__ = (
        UniqueConstraint("empresa_id", "codigo_interno", name="uq_obras_empresa_codigo"),
    )

    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=False)
    perfil_tributario_id: Mapped[int] = mapped_column(
        ForeignKey("perfis_tributarios.id"),
        nullable=False,
    )
    codigo_interno: Mapped[str] = mapped_column(String(40), nullable=False)
    nome: Mapped[str] = mapped_column(String(180), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=True)
    cidade: Mapped[str] = mapped_column(String(80), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    atividade_principal: Mapped[str] = mapped_column(String(120), nullable=False)
    aliquota_iss: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=True)
    data_fim: Mapped[date] = mapped_column(Date, nullable=True)
    status_ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    observacoes: Mapped[str] = mapped_column(String(500), nullable=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="obras")
    perfil_tributario: Mapped["PerfilTributario"] = relationship(back_populates="obras")
    lancamentos: Mapped[list["LancamentoFiscal"]] = relationship(back_populates="obra")
    apuracoes: Mapped[list["Apuracao"]] = relationship(back_populates="obra")
    obrigacoes: Mapped[list["ObrigacaoVencimento"]] = relationship(back_populates="obra")


Index("ix_obras_empresa_id", Obra.empresa_id)
Index("ix_obras_status_ativo", Obra.status_ativo)

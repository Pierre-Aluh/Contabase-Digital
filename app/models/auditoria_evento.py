"""Modelo de auditoria de eventos relevantes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.empresa import Empresa


class AuditoriaEvento(Base, IdMixin, TimestampMixin):
    __tablename__ = "auditoria_eventos"

    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=True)
    entidade: Mapped[str] = mapped_column(String(80), nullable=False)
    entidade_id: Mapped[int] = mapped_column(nullable=True)
    acao: Mapped[str] = mapped_column(String(60), nullable=False)
    dados_antes: Mapped[str] = mapped_column(String(2000), nullable=True)
    dados_depois: Mapped[str] = mapped_column(String(2000), nullable=True)
    usuario: Mapped[str] = mapped_column(String(120), nullable=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="auditorias")


Index("ix_auditoria_entidade", AuditoriaEvento.entidade)
Index("ix_auditoria_empresa_id", AuditoriaEvento.empresa_id)

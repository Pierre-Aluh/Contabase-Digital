"""Modelo de perfis tributarios."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.obra import Obra


class PerfilTributario(Base, IdMixin, TimestampMixin):
    __tablename__ = "perfis_tributarios"

    nome: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=True)
    percentual_presuncao_irpj: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    percentual_presuncao_csll: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    obras: Mapped[list["Obra"]] = relationship(back_populates="perfil_tributario")

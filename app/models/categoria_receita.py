"""Modelo de categorias de receita."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class CategoriaReceita(Base, IdMixin, TimestampMixin):
    __tablename__ = "categorias_receita"

    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=True)
    percentual_presuncao_irpj: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    percentual_presuncao_csll: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

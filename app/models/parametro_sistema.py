"""Modelo de parametros configuraveis do sistema."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class ParametroSistema(Base, IdMixin, TimestampMixin):
    __tablename__ = "parametros_sistema"

    chave: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(String(255), nullable=True)
    valor_texto: Mapped[str] = mapped_column(String(255), nullable=True)
    valor_decimal: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=True)
    valor_inteiro: Mapped[int] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

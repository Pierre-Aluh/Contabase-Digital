"""Modelo de lancamentos fiscais por obra e competencia."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.ajuste_fiscal import AjusteFiscal
    from app.models.competencia import Competencia
    from app.models.empresa import Empresa
    from app.models.obra import Obra


class LancamentoFiscal(Base, IdMixin, TimestampMixin):
    __tablename__ = "lancamentos_fiscais"
    __table_args__ = (
        UniqueConstraint("obra_id", "competencia_id", name="uq_lancamentos_obra_competencia"),
    )

    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), nullable=False)
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id"), nullable=False)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencias.id"), nullable=False)

    receita_bruta: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    receita_juros: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    atualizacao_monetaria: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    variacoes_monetarias_mora: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    vendas_servicos_vista: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    vendas_servicos_prazo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    aplicacao_financeira: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    alienacao_investimentos: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    vendas_bens_imobilizado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    juros_recebidos_auferidos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    receita_aluguel: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    receitas_contrato_mutuo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    multas_mora: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    juros_mora: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    acrescimos_financeiros: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    descontos_financeiros_obtidos: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    taxa_emissao_documentos: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    taxa_cobranca_judicial_extrajudicial: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    recuperacao_custos_despesas: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00")
    )
    outras_receitas_operacionais: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    devolucoes_cancelamentos_descontos: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    receita_tributavel_pis_cofins: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    observacoes: Mapped[str] = mapped_column(String(500), nullable=True)
    documento_referencia: Mapped[str] = mapped_column(String(255), nullable=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="lancamentos")
    obra: Mapped["Obra"] = relationship(back_populates="lancamentos")
    competencia: Mapped["Competencia"] = relationship(back_populates="lancamentos")
    ajustes: Mapped[list["AjusteFiscal"]] = relationship(
        back_populates="lancamento",
        cascade="all, delete-orphan",
    )


Index("ix_lancamentos_empresa_id", LancamentoFiscal.empresa_id)
Index("ix_lancamentos_competencia_id", LancamentoFiscal.competencia_id)

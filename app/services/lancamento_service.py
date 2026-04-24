"""Servicos de negocio para lancamentos fiscais por obra e competencia."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session_manager import get_session
from app.models.ajuste_fiscal import AjusteFiscal
from app.models.auditoria_evento import AuditoriaEvento
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.enums import TipoAjuste, TributoAlvo
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.parametro_sistema import ParametroSistema
from app.models.perfil_tributario import PerfilTributario
from app.services.errors import BusinessRuleError
from app.utils.formatters import parse_decimal, quantize_money


LANCAMENTO_DETALHE_FIELDS: list[tuple[str, str]] = [
    ("receita_juros", "Receita de Juros"),
    ("atualizacao_monetaria", "Atualizacao monetaria"),
    ("variacoes_monetarias_mora", "Variacoes monetarias de Mora"),
    ("vendas_servicos_vista", "Vendas de servicos a Vista"),
    ("vendas_servicos_prazo", "Vendas de servicos a Prazo"),
    ("aplicacao_financeira", "Aplicacao financeira"),
    ("alienacao_investimentos", "Alienacao de investimentos"),
    ("vendas_bens_imobilizado", "Vendas de bens do imobilizado"),
    ("juros_recebidos_auferidos", "Juros recebidos ou auferidos"),
    ("receita_aluguel", "Receita de aluguel"),
    ("receitas_contrato_mutuo", "Receitas de contrato de mutuo"),
    ("multas_mora", "Multas de mora"),
    ("juros_mora", "Juros de mora"),
    ("acrescimos_financeiros", "Acrescimos financeiros"),
    ("descontos_financeiros_obtidos", "Descontos financeiros obtidos"),
    ("taxa_emissao_documentos", "Taxa emissao de documentos"),
    (
        "taxa_cobranca_judicial_extrajudicial",
        "Taxa de cobranca judicial e extrajudicial",
    ),
    ("recuperacao_custos_despesas", "Recuperacao de custos e despesas"),
]


@dataclass
class AjusteFiscalInput:
    tributo_alvo: str
    tipo_ajuste: str
    valor: str | int | float | Decimal
    descricao: str
    justificativa: str
    documento_referencia: str | None = None
    observacao: str | None = None


@dataclass
class LancamentoFiscalInput:
    empresa_id: int
    obra_id: int
    competencia_id: int
    receita_bruta: str | int | float | Decimal
    receita_juros: str | int | float | Decimal = Decimal("0.00")
    atualizacao_monetaria: str | int | float | Decimal = Decimal("0.00")
    variacoes_monetarias_mora: str | int | float | Decimal = Decimal("0.00")
    vendas_servicos_vista: str | int | float | Decimal = Decimal("0.00")
    vendas_servicos_prazo: str | int | float | Decimal = Decimal("0.00")
    aplicacao_financeira: str | int | float | Decimal = Decimal("0.00")
    alienacao_investimentos: str | int | float | Decimal = Decimal("0.00")
    vendas_bens_imobilizado: str | int | float | Decimal = Decimal("0.00")
    juros_recebidos_auferidos: str | int | float | Decimal = Decimal("0.00")
    receita_aluguel: str | int | float | Decimal = Decimal("0.00")
    receitas_contrato_mutuo: str | int | float | Decimal = Decimal("0.00")
    multas_mora: str | int | float | Decimal = Decimal("0.00")
    juros_mora: str | int | float | Decimal = Decimal("0.00")
    acrescimos_financeiros: str | int | float | Decimal = Decimal("0.00")
    descontos_financeiros_obtidos: str | int | float | Decimal = Decimal("0.00")
    taxa_emissao_documentos: str | int | float | Decimal = Decimal("0.00")
    taxa_cobranca_judicial_extrajudicial: str | int | float | Decimal = Decimal("0.00")
    recuperacao_custos_despesas: str | int | float | Decimal = Decimal("0.00")
    observacoes: str | None = None
    documento_referencia: str | None = None


class LancamentoFiscalService:
    def list_empresas(self) -> list[Empresa]:
        with get_session() as session:
            return list(
                session.execute(select(Empresa).order_by(Empresa.razao_social.asc())).scalars().all()
            )

    def list_obras(self, empresa_id: int | None = None) -> list[Obra]:
        with get_session() as session:
            stmt = select(Obra).order_by(Obra.nome.asc())
            if empresa_id:
                stmt = stmt.where(Obra.empresa_id == empresa_id)
            return list(session.execute(stmt).scalars().all())

    def list_competencias(self) -> list[Competencia]:
        with get_session() as session:
            return list(
                session.execute(select(Competencia).order_by(Competencia.ano.asc(), Competencia.mes.asc()))
                .scalars()
                .all()
            )

    def list_perfis_tributarios(self) -> list[PerfilTributario]:
        with get_session() as session:
            return list(
                session.execute(
                    select(PerfilTributario)
                    .where(PerfilTributario.ativo.is_(True))
                    .order_by(PerfilTributario.nome.asc())
                )
                .scalars()
                .all()
            )

    def list_lancamentos(
        self,
        empresa_id: int | None = None,
        obra_id: int | None = None,
        competencia_id: int | None = None,
    ) -> list[LancamentoFiscal]:
        with get_session() as session:
            stmt = (
                select(LancamentoFiscal)
                .options(
                    selectinload(LancamentoFiscal.empresa),
                    selectinload(LancamentoFiscal.obra),
                    selectinload(LancamentoFiscal.competencia),
                    selectinload(LancamentoFiscal.ajustes),
                )
                .order_by(LancamentoFiscal.created_at.desc())
            )
            if empresa_id:
                stmt = stmt.where(LancamentoFiscal.empresa_id == empresa_id)
            if obra_id:
                stmt = stmt.where(LancamentoFiscal.obra_id == obra_id)
            if competencia_id:
                stmt = stmt.where(LancamentoFiscal.competencia_id == competencia_id)

            return list(session.execute(stmt).scalars().all())

    def get_lancamento_with_ajustes(self, lancamento_id: int) -> tuple[LancamentoFiscal, list[AjusteFiscal]]:
        with get_session() as session:
            lancamento = session.execute(
                select(LancamentoFiscal)
                .options(
                    selectinload(LancamentoFiscal.empresa),
                    selectinload(LancamentoFiscal.obra),
                    selectinload(LancamentoFiscal.competencia),
                )
                .where(LancamentoFiscal.id == lancamento_id)
            ).scalar_one_or_none()
            if not lancamento:
                raise BusinessRuleError("Lancamento nao encontrado")

            ajustes = list(
                session.execute(
                    select(AjusteFiscal)
                    .where(AjusteFiscal.lancamento_fiscal_id == lancamento_id)
                    .order_by(AjusteFiscal.id.asc())
                )
                .scalars()
                .all()
            )
            return lancamento, ajustes

    def save_lancamento(
        self,
        payload: LancamentoFiscalInput,
        ajustes: list[AjusteFiscalInput],
        lancamento_id: int | None = None,
    ) -> LancamentoFiscal:
        self._validate_payload(payload, ajustes)
        aggregates = self.calculate_aggregate_values(payload)

        with get_session() as session:
            obra = session.get(Obra, payload.obra_id)
            if not obra:
                raise BusinessRuleError("Obra nao encontrada")
            if obra.empresa_id != payload.empresa_id:
                raise BusinessRuleError("Obra selecionada nao pertence a empresa selecionada")

            duplicado_stmt = select(LancamentoFiscal).where(
                LancamentoFiscal.obra_id == payload.obra_id,
                LancamentoFiscal.competencia_id == payload.competencia_id,
            )
            if lancamento_id:
                duplicado_stmt = duplicado_stmt.where(LancamentoFiscal.id != lancamento_id)

            duplicado = session.execute(duplicado_stmt).scalar_one_or_none()
            if duplicado:
                raise BusinessRuleError("Ja existe lancamento para esta obra na competencia selecionada")

            if lancamento_id:
                entity = session.get(LancamentoFiscal, lancamento_id)
                if not entity:
                    raise BusinessRuleError("Lancamento nao encontrado")
                acao = "EDITAR"
                dados_antes = self._serialize_lancamento(entity)
            else:
                entity = LancamentoFiscal(
                    empresa_id=payload.empresa_id,
                    obra_id=payload.obra_id,
                    competencia_id=payload.competencia_id,
                    receita_bruta=Decimal("0.00"),
                    receita_juros=Decimal("0.00"),
                    atualizacao_monetaria=Decimal("0.00"),
                    variacoes_monetarias_mora=Decimal("0.00"),
                    vendas_servicos_vista=Decimal("0.00"),
                    vendas_servicos_prazo=Decimal("0.00"),
                    aplicacao_financeira=Decimal("0.00"),
                    alienacao_investimentos=Decimal("0.00"),
                    vendas_bens_imobilizado=Decimal("0.00"),
                    juros_recebidos_auferidos=Decimal("0.00"),
                    receita_aluguel=Decimal("0.00"),
                    receitas_contrato_mutuo=Decimal("0.00"),
                    multas_mora=Decimal("0.00"),
                    juros_mora=Decimal("0.00"),
                    acrescimos_financeiros=Decimal("0.00"),
                    descontos_financeiros_obtidos=Decimal("0.00"),
                    taxa_emissao_documentos=Decimal("0.00"),
                    taxa_cobranca_judicial_extrajudicial=Decimal("0.00"),
                    recuperacao_custos_despesas=Decimal("0.00"),
                    outras_receitas_operacionais=Decimal("0.00"),
                    devolucoes_cancelamentos_descontos=Decimal("0.00"),
                    receita_tributavel_pis_cofins=Decimal("0.00"),
                    observacoes=None,
                    documento_referencia=None,
                )
                session.add(entity)
                acao = "CRIAR"
                dados_antes = None

            entity.empresa_id = payload.empresa_id
            entity.obra_id = payload.obra_id
            entity.competencia_id = payload.competencia_id
            entity.receita_bruta = aggregates["receita_bruta"]
            for field_name, _ in LANCAMENTO_DETALHE_FIELDS:
                setattr(entity, field_name, aggregates[field_name])
            entity.outras_receitas_operacionais = aggregates["outras_receitas_operacionais"]
            entity.devolucoes_cancelamentos_descontos = Decimal("0.00")
            entity.receita_tributavel_pis_cofins = aggregates["receita_tributavel_pis_cofins"]
            entity.observacoes = (payload.observacoes or "").strip() or None
            entity.documento_referencia = (payload.documento_referencia or "").strip() or None
            session.flush()

            session.execute(
                AjusteFiscal.__table__.delete().where(AjusteFiscal.lancamento_fiscal_id == entity.id)
            )

            for ajuste in ajustes:
                session.add(
                    AjusteFiscal(
                        lancamento_fiscal_id=entity.id,
                        tributo_alvo=TributoAlvo(ajuste.tributo_alvo),
                        tipo_ajuste=TipoAjuste(ajuste.tipo_ajuste),
                        valor=quantize_money(parse_decimal(ajuste.valor)),
                        descricao=ajuste.descricao.strip(),
                        justificativa=ajuste.justificativa.strip(),
                        documento_referencia=(ajuste.documento_referencia or "").strip() or None,
                        observacao=(ajuste.observacao or "").strip() or None,
                    )
                )

            dados_depois = self._serialize_lancamento(entity)
            session.add(
                AuditoriaEvento(
                    empresa_id=payload.empresa_id,
                    entidade="LancamentoFiscal",
                    entidade_id=entity.id,
                    acao=acao,
                    dados_antes=dados_antes,
                    dados_depois=dados_depois,
                    usuario="sistema",
                )
            )

            session.commit()
            session.refresh(entity)

            # Reprocessamento fiscal: altera lancamento invalida apuracoes vigentes do escopo.
            from app.services.fiscal_calculation_service import FiscalCalculationService

            FiscalCalculationService().invalidate_apuracoes_for_lancamento(
                empresa_id=entity.empresa_id,
                obra_id=entity.obra_id,
                competencia_id=entity.competencia_id,
            )
            return entity

    def delete_lancamento(self, lancamento_id: int) -> None:
        with get_session() as session:
            entity = session.get(LancamentoFiscal, lancamento_id)
            if not entity:
                raise BusinessRuleError("Lancamento nao encontrado")

            dados_antes = self._serialize_lancamento(entity)
            session.execute(
                AjusteFiscal.__table__.delete().where(AjusteFiscal.lancamento_fiscal_id == lancamento_id)
            )
            session.delete(entity)
            session.add(
                AuditoriaEvento(
                    empresa_id=entity.empresa_id,
                    entidade="LancamentoFiscal",
                    entidade_id=lancamento_id,
                    acao="EXCLUIR",
                    dados_antes=dados_antes,
                    dados_depois="excluido",
                    usuario="sistema",
                )
            )
            empresa_id = entity.empresa_id
            obra_id = entity.obra_id
            competencia_id = entity.competencia_id
            session.commit()

            from app.services.fiscal_calculation_service import FiscalCalculationService

            FiscalCalculationService().invalidate_apuracoes_for_lancamento(
                empresa_id=empresa_id,
                obra_id=obra_id,
                competencia_id=competencia_id,
            )

    def duplicate_from_previous_month(
        self,
        empresa_id: int,
        obra_id: int,
        competencia_id: int,
    ) -> LancamentoFiscal:
        with get_session() as session:
            competencia = session.get(Competencia, competencia_id)
            if not competencia:
                raise BusinessRuleError("Competencia nao encontrada")

            obra = session.get(Obra, obra_id)
            if not obra:
                raise BusinessRuleError("Obra nao encontrada")
            if obra.empresa_id != empresa_id:
                raise BusinessRuleError("Obra selecionada nao pertence a empresa selecionada")

            exists = session.execute(
                select(LancamentoFiscal).where(
                    LancamentoFiscal.obra_id == obra_id,
                    LancamentoFiscal.competencia_id == competencia_id,
                )
            ).scalar_one_or_none()
            if exists:
                raise BusinessRuleError(
                    "Ja existe lancamento nesta competencia. Abra o registro para editar."
                )

            competencia_anterior = session.execute(
                select(Competencia)
                .where((Competencia.ano < competencia.ano) | ((Competencia.ano == competencia.ano) & (Competencia.mes < competencia.mes)))
                .order_by(Competencia.ano.desc(), Competencia.mes.desc())
                .limit(1)
            ).scalar_one_or_none()
            if not competencia_anterior:
                raise BusinessRuleError("Nao existe competencia anterior cadastrada")

            origem = session.execute(
                select(LancamentoFiscal).where(
                    LancamentoFiscal.obra_id == obra_id,
                    LancamentoFiscal.competencia_id == competencia_anterior.id,
                )
            ).scalar_one_or_none()
            if not origem:
                raise BusinessRuleError("Nao existe lancamento no mes anterior para duplicar")

            novo = LancamentoFiscal(
                empresa_id=empresa_id,
                obra_id=obra_id,
                competencia_id=competencia_id,
                receita_bruta=origem.receita_bruta,
                receita_juros=origem.receita_juros,
                atualizacao_monetaria=origem.atualizacao_monetaria,
                variacoes_monetarias_mora=origem.variacoes_monetarias_mora,
                vendas_servicos_vista=origem.vendas_servicos_vista,
                vendas_servicos_prazo=origem.vendas_servicos_prazo,
                aplicacao_financeira=origem.aplicacao_financeira,
                alienacao_investimentos=origem.alienacao_investimentos,
                vendas_bens_imobilizado=origem.vendas_bens_imobilizado,
                juros_recebidos_auferidos=origem.juros_recebidos_auferidos,
                receita_aluguel=origem.receita_aluguel,
                receitas_contrato_mutuo=origem.receitas_contrato_mutuo,
                multas_mora=origem.multas_mora,
                juros_mora=origem.juros_mora,
                acrescimos_financeiros=origem.acrescimos_financeiros,
                descontos_financeiros_obtidos=origem.descontos_financeiros_obtidos,
                taxa_emissao_documentos=origem.taxa_emissao_documentos,
                taxa_cobranca_judicial_extrajudicial=origem.taxa_cobranca_judicial_extrajudicial,
                recuperacao_custos_despesas=origem.recuperacao_custos_despesas,
                outras_receitas_operacionais=origem.outras_receitas_operacionais,
                devolucoes_cancelamentos_descontos=origem.devolucoes_cancelamentos_descontos,
                receita_tributavel_pis_cofins=origem.receita_tributavel_pis_cofins,
                observacoes=origem.observacoes,
                documento_referencia=origem.documento_referencia,
            )
            session.add(novo)
            session.flush()

            ajustes_origem = list(
                session.execute(
                    select(AjusteFiscal).where(AjusteFiscal.lancamento_fiscal_id == origem.id)
                )
                .scalars()
                .all()
            )
            for ajuste in ajustes_origem:
                session.add(
                    AjusteFiscal(
                        lancamento_fiscal_id=novo.id,
                        tributo_alvo=ajuste.tributo_alvo,
                        tipo_ajuste=ajuste.tipo_ajuste,
                        valor=ajuste.valor,
                        descricao=ajuste.descricao,
                        justificativa=ajuste.justificativa,
                        documento_referencia=ajuste.documento_referencia,
                        observacao=ajuste.observacao,
                    )
                )

            session.add(
                AuditoriaEvento(
                    empresa_id=empresa_id,
                    entidade="LancamentoFiscal",
                    entidade_id=novo.id,
                    acao="DUPLICAR_MES_ANTERIOR",
                    dados_antes=f"origem={origem.id}",
                    dados_depois=f"destino={novo.id}",
                    usuario="sistema",
                )
            )

            session.commit()
            session.refresh(novo)

            from app.services.fiscal_calculation_service import FiscalCalculationService

            FiscalCalculationService().invalidate_apuracoes_for_lancamento(
                empresa_id=novo.empresa_id,
                obra_id=novo.obra_id,
                competencia_id=novo.competencia_id,
            )
            return novo

    def calculate_adjustment_summary(
        self,
        receita_bruta: str | int | float | Decimal,
        receita_tributavel_pis_cofins: str | int | float | Decimal,
        ajustes: list[AjusteFiscalInput],
        obra_id: int | None = None,
        perfil_tributario_id: int | None = None,
    ) -> dict[str, dict[str, Decimal]]:
        limite_irpj_adicional, aliquota_irpj_adicional = self._get_irpj_adicional_rules()
        aliquotas = self._get_aliquotas_tributos()
        base_receita = quantize_money(parse_decimal(receita_bruta))
        base_piscofins = quantize_money(parse_decimal(receita_tributavel_pis_cofins))
        percentual_irpj, percentual_csll = self.resolve_presuncao(
            obra_id=obra_id,
            perfil_tributario_id=perfil_tributario_id,
        )

        summary: dict[str, dict[str, Decimal]] = {
            TributoAlvo.PIS.value: {"base_original": base_piscofins, "adicoes": Decimal("0.00"), "reducoes": Decimal("0.00")},
            TributoAlvo.COFINS.value: {"base_original": base_piscofins, "adicoes": Decimal("0.00"), "reducoes": Decimal("0.00")},
            TributoAlvo.CSLL.value: {"base_original": base_receita, "adicoes": Decimal("0.00"), "reducoes": Decimal("0.00")},
            TributoAlvo.IRPJ.value: {"base_original": base_receita, "adicoes": Decimal("0.00"), "reducoes": Decimal("0.00")},
            TributoAlvo.IRPJ_ADICIONAL.value: {"base_original": base_receita, "adicoes": Decimal("0.00"), "reducoes": Decimal("0.00")},
        }

        for ajuste in ajustes:
            tributo = TributoAlvo(ajuste.tributo_alvo).value
            valor = quantize_money(parse_decimal(ajuste.valor))
            if TributoAlvo(ajuste.tributo_alvo) == TributoAlvo.ISS:
                continue
            if TipoAjuste(ajuste.tipo_ajuste) == TipoAjuste.ADICAO:
                summary[tributo]["adicoes"] += valor
            else:
                summary[tributo]["reducoes"] += valor

        for chave_tributo in [TributoAlvo.PIS.value, TributoAlvo.COFINS.value, TributoAlvo.IRPJ_ADICIONAL.value]:
            tributo = summary[chave_tributo]
            final = tributo["base_original"] + tributo["adicoes"] - tributo["reducoes"]
            tributo["base_final"] = final if final > 0 else Decimal("0.00")
            tributo["adicoes"] = quantize_money(tributo["adicoes"])
            tributo["reducoes"] = quantize_money(tributo["reducoes"])
            tributo["base_final"] = quantize_money(tributo["base_final"])
            tributo["imposto_devido"] = Decimal("0.00")

        # IRPJ/CSLL: adicoes e reducoes sao aplicadas antes da presuncao.
        for chave_tributo, percentual_presuncao, chave_aliquota in [
            (TributoAlvo.IRPJ.value, percentual_irpj, "IRPJ"),
            (TributoAlvo.CSLL.value, percentual_csll, "CSLL"),
        ]:
            tributo = summary[chave_tributo]
            base_original = quantize_money(tributo["base_original"] * percentual_presuncao)
            adicoes = quantize_money(tributo["adicoes"] * percentual_presuncao)
            reducoes = quantize_money(tributo["reducoes"] * percentual_presuncao)
            base_final = base_original + adicoes - reducoes
            base_final = quantize_money(base_final if base_final > 0 else Decimal("0.00"))

            tributo["base_original"] = base_original
            tributo["adicoes"] = adicoes
            tributo["reducoes"] = reducoes
            tributo["base_final"] = base_final

            aliquota = aliquotas.get(chave_aliquota)
            tributo["imposto_devido"] = (
                quantize_money(base_final * aliquota)
                if aliquota is not None
                else Decimal("0.00")
            )

        for chave_tributo, chave_aliquota in [
            (TributoAlvo.PIS.value, "PIS"),
            (TributoAlvo.COFINS.value, "COFINS"),
        ]:
            aliquota = aliquotas.get(chave_aliquota)
            if aliquota is not None:
                base_final = summary[chave_tributo]["base_final"]
                summary[chave_tributo]["imposto_devido"] = quantize_money(base_final * aliquota)

        irpj_adicional = summary[TributoAlvo.IRPJ_ADICIONAL.value]
        base_original_total = summary[TributoAlvo.IRPJ.value]["base_final"]
        base_final_total = summary[TributoAlvo.IRPJ.value]["base_final"] + irpj_adicional["adicoes"] - irpj_adicional["reducoes"]
        base_final_total = quantize_money(base_final_total if base_final_total > 0 else Decimal("0.00"))

        base_original_excedente = base_original_total - limite_irpj_adicional
        base_final_excedente = base_final_total - limite_irpj_adicional

        irpj_adicional["base_original"] = quantize_money(
            base_original_excedente if base_original_excedente > 0 else Decimal("0.00")
        )
        irpj_adicional["base_final"] = quantize_money(
            base_final_excedente if base_final_excedente > 0 else Decimal("0.00")
        )
        irpj_adicional["imposto_devido"] = quantize_money(
            irpj_adicional["base_final"] * aliquota_irpj_adicional
        )

        return summary

    def build_presuncao_memoria(
        self,
        receita_bruta: str | int | float | Decimal,
        receita_tributavel_pis_cofins: str | int | float | Decimal,
        obra_id: int | None = None,
        perfil_tributario_id: int | None = None,
    ) -> dict[str, Decimal]:
        base_receita = quantize_money(parse_decimal(receita_bruta))
        base_piscofins = quantize_money(parse_decimal(receita_tributavel_pis_cofins))
        percentual_irpj, percentual_csll = self.resolve_presuncao(
            obra_id=obra_id,
            perfil_tributario_id=perfil_tributario_id,
        )
        return {
            "receita_bruta": base_receita,
            "receita_tributavel_pis_cofins": base_piscofins,
            "percentual_irpj": percentual_irpj,
            "percentual_csll": percentual_csll,
            "base_presumida_irpj": quantize_money(base_receita * percentual_irpj),
            "base_presumida_csll": quantize_money(base_receita * percentual_csll),
        }

    def resolve_presuncao(
        self,
        obra_id: int | None = None,
        perfil_tributario_id: int | None = None,
    ) -> tuple[Decimal, Decimal]:
        if perfil_tributario_id and perfil_tributario_id > 0:
            return self.get_presuncao_for_perfil(perfil_tributario_id)
        return self.get_presuncao_for_obra(obra_id)

    def get_presuncao_for_perfil(self, perfil_tributario_id: int | None) -> tuple[Decimal, Decimal]:
        percentual_irpj_default = Decimal("1.00")
        percentual_csll_default = Decimal("1.00")
        if not perfil_tributario_id or perfil_tributario_id <= 0:
            return percentual_irpj_default, percentual_csll_default

        with get_session() as session:
            perfil = session.get(PerfilTributario, perfil_tributario_id)

        if not perfil:
            return percentual_irpj_default, percentual_csll_default

        percentual_irpj = self._normalize_presuncao_percentual(
            perfil.percentual_presuncao_irpj,
            percentual_irpj_default,
        )
        percentual_csll = self._normalize_presuncao_percentual(
            perfil.percentual_presuncao_csll,
            percentual_csll_default,
        )
        return percentual_irpj, percentual_csll

    def get_presuncao_for_obra(self, obra_id: int | None) -> tuple[Decimal, Decimal]:
        percentual_irpj_default = Decimal("1.00")
        percentual_csll_default = Decimal("1.00")
        if not obra_id or obra_id <= 0:
            return percentual_irpj_default, percentual_csll_default

        with get_session() as session:
            obra = session.execute(
                select(Obra)
                .options(selectinload(Obra.perfil_tributario))
                .where(Obra.id == obra_id)
            ).scalar_one_or_none()

        if not obra or not obra.perfil_tributario:
            return percentual_irpj_default, percentual_csll_default

        percentual_irpj = self._normalize_presuncao_percentual(
            obra.perfil_tributario.percentual_presuncao_irpj,
            percentual_irpj_default,
        )
        percentual_csll = self._normalize_presuncao_percentual(
            obra.perfil_tributario.percentual_presuncao_csll,
            percentual_csll_default,
        )
        return percentual_irpj, percentual_csll

    def _get_aliquotas_tributos(self) -> dict[str, Decimal]:
        defaults = {
            "PIS": Decimal("0.0065"),
            "COFINS": Decimal("0.03"),
            "CSLL": Decimal("0.09"),
            "IRPJ": Decimal("0.15"),
        }
        chaves_param = {
            "PIS": "ALIQUOTA_PIS",
            "COFINS": "ALIQUOTA_COFINS",
            "CSLL": "ALIQUOTA_CSLL",
            "IRPJ": "ALIQUOTA_IRPJ",
        }
        with get_session() as session:
            params = session.execute(
                select(ParametroSistema).where(
                    ParametroSistema.chave.in_(list(chaves_param.values())),
                    ParametroSistema.ativo.is_(True),
                )
            ).scalars().all()

        param_map = {p.chave: p for p in params}
        result: dict[str, Decimal] = {}
        for tributo, chave in chaves_param.items():
            param = param_map.get(chave)
            if param and param.valor_decimal is not None:
                result[tributo] = Decimal(str(param.valor_decimal))
            else:
                result[tributo] = defaults[tributo]
        return result

    def _get_irpj_adicional_rules(self) -> tuple[Decimal, Decimal]:
        limite_default = Decimal("20000.00")
        aliquota_default = Decimal("0.10")

        with get_session() as session:
            limite_param = session.execute(
                select(ParametroSistema).where(
                    ParametroSistema.chave == "LIMITE_IRPJ_ADICIONAL_TRIMESTRAL",
                    ParametroSistema.ativo.is_(True),
                )
            ).scalar_one_or_none()
            aliquota_param = session.execute(
                select(ParametroSistema).where(
                    ParametroSistema.chave == "ALIQUOTA_IRPJ_ADICIONAL",
                    ParametroSistema.ativo.is_(True),
                )
            ).scalar_one_or_none()

        limite = (
            quantize_money(Decimal(str(limite_param.valor_decimal)))
            if limite_param and limite_param.valor_decimal is not None
            else limite_default
        )
        aliquota = (
            Decimal(str(aliquota_param.valor_decimal))
            if aliquota_param and aliquota_param.valor_decimal is not None
            else aliquota_default
        )
        return limite, aliquota

    @staticmethod
    def _normalize_presuncao_percentual(raw_value: Decimal | None, default: Decimal) -> Decimal:
        if raw_value is None:
            return default

        value = Decimal(str(raw_value))
        if value <= 0:
            return default
        if value <= Decimal("1.00"):
            return value
        if value <= Decimal("100.00"):
            return value / Decimal("100")
        return default

    def calculate_aggregate_values(self, payload: LancamentoFiscalInput) -> dict[str, Decimal]:
        values: dict[str, Decimal] = {
            "receita_bruta": quantize_money(parse_decimal(payload.receita_bruta)),
        }
        adicionais = Decimal("0.00")
        for field_name, _ in LANCAMENTO_DETALHE_FIELDS:
            parsed_value = quantize_money(parse_decimal(getattr(payload, field_name)))
            values[field_name] = parsed_value
            adicionais += parsed_value

        values["outras_receitas_operacionais"] = quantize_money(adicionais)
        values["receita_tributavel_pis_cofins"] = quantize_money(values["receita_bruta"] + adicionais)
        return values

    def _validate_payload(
        self,
        payload: LancamentoFiscalInput,
        ajustes: list[AjusteFiscalInput],
    ) -> None:
        if payload.empresa_id <= 0:
            raise BusinessRuleError("Empresa e obrigatoria")
        if payload.obra_id <= 0:
            raise BusinessRuleError("Obra e obrigatoria")
        if payload.competencia_id <= 0:
            raise BusinessRuleError("Competencia e obrigatoria")

        for field_name, value in [
            ("receita bruta", payload.receita_bruta),
        ]:
            numeric = parse_decimal(value)
            if numeric < 0:
                raise BusinessRuleError(f"O campo {field_name} nao pode ser negativo")

        for field_name, field_label in LANCAMENTO_DETALHE_FIELDS:
            numeric = parse_decimal(getattr(payload, field_name))
            if numeric < 0:
                raise BusinessRuleError(f"O campo {field_label} nao pode ser negativo")

        for idx, ajuste in enumerate(ajustes, start=1):
            try:
                TributoAlvo(ajuste.tributo_alvo)
                TipoAjuste(ajuste.tipo_ajuste)
            except ValueError as exc:
                raise BusinessRuleError(f"Ajuste {idx} possui tributo/tipo invalido") from exc
            if parse_decimal(ajuste.valor) < 0:
                raise BusinessRuleError(f"Ajuste {idx} possui valor negativo")
            if not ajuste.descricao.strip():
                raise BusinessRuleError(f"Ajuste {idx} sem descricao")
            if not ajuste.justificativa.strip():
                raise BusinessRuleError(f"Ajuste {idx} sem justificativa")

    def _serialize_lancamento(self, entity: LancamentoFiscal) -> str:
        return (
            f"obra={entity.obra_id}|competencia={entity.competencia_id}|"
            f"receita_bruta={entity.receita_bruta}|"
            f"tributavel={entity.receita_tributavel_pis_cofins}"
        )

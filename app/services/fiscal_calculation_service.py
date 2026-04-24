"""Motor fiscal do lucro presumido com persistencia de apuracao."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from app.db.session_manager import get_session
from app.models.apuracao import Apuracao
from app.models.apuracao_item import ApuracaoItem
from app.models.competencia import Competencia
from app.models.enums import StatusObrigacao, TributoAlvo
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.obrigacao_vencimento import ObrigacaoVencimento
from app.models.parametro_sistema import ParametroSistema
from app.services.consolidation_service import ConsolidationService
from app.services.due_date_service import DueDateService
from app.services.errors import BusinessRuleError
from app.services.lancamento_service import AjusteFiscalInput, LancamentoFiscalService
from app.utils.formatters import quantize_money


@dataclass(frozen=True)
class FiscalCalculationOutput:
    competencia_id: int
    consolidada: bool
    obra_id: int | None
    fechamento_trimestral: bool
    tributos: dict[str, dict[str, Decimal]]
    total_impostos: Decimal
    apuracao_id: int | None = None


class FiscalCalculationService:
    """Orquestra calculo mensal/trimestral, persistencia e reprocessamento."""

    def __init__(self) -> None:
        self._lancamento_service = LancamentoFiscalService()
        self._consolidation_service = ConsolidationService()
        self._due_date_service = DueDateService()

    def calculate_for_scope(
        self,
        empresa_id: int,
        competencia_id: int,
        obra_id: int | None = None,
        consolidada: bool = False,
        persist: bool = False,
    ) -> FiscalCalculationOutput:
        if obra_id and consolidada:
            raise BusinessRuleError("Nao e permitido calcular consolidado informando obra especifica")

        competencia = self._get_competencia(competencia_id)
        lancamentos_mes = self._list_lancamentos(
            empresa_id=empresa_id,
            competencia_id=competencia_id,
            obra_id=obra_id,
        )
        if not lancamentos_mes:
            raise BusinessRuleError("Nao existem lancamentos para os filtros informados")

        summaries_mes = [self._build_lancamento_summary(l) for l in lancamentos_mes]
        consolidated = self._consolidation_service.consolidate_summaries(summaries_mes)

        iss_value = self._calculate_iss(lancamentos_mes)
        consolidated[TributoAlvo.ISS.value]["base_original"] = quantize_money(
            sum((Decimal(str(l.receita_bruta)) for l in lancamentos_mes), start=Decimal("0.00"))
        )
        consolidated[TributoAlvo.ISS.value]["base_final"] = consolidated[TributoAlvo.ISS.value]["base_original"]
        consolidated[TributoAlvo.ISS.value]["imposto_devido"] = iss_value

        quarter_lancamentos = self._list_lancamentos_for_quarter_to_date(
            empresa_id=empresa_id,
            competencia=competencia,
            obra_id=obra_id,
        )
        quarter_summaries = [self._build_lancamento_summary(l) for l in quarter_lancamentos]
        consolidated_quarter = self._consolidation_service.consolidate_summaries(quarter_summaries)

        limite_irpj_adicional, aliquota_irpj_adicional = self._get_irpj_adicional_rules()
        base_irpj_trimestre = consolidated_quarter[TributoAlvo.IRPJ.value]["base_final"]
        adicional_trimestre = base_irpj_trimestre - limite_irpj_adicional
        adicional_trimestre = adicional_trimestre if adicional_trimestre > 0 else Decimal("0.00")
        adicional_trimestre = quantize_money(adicional_trimestre)

        fechamento_trimestral = competencia.mes in {3, 6, 9, 12}
        # Fora do fechamento, valor representa projecao acumulada do trimestre ate a competencia.
        base_adicional_mes = adicional_trimestre
        imposto_adicional_mes = quantize_money(base_adicional_mes * aliquota_irpj_adicional)

        consolidated[TributoAlvo.IRPJ_ADICIONAL.value]["base_original"] = base_adicional_mes
        consolidated[TributoAlvo.IRPJ_ADICIONAL.value]["base_final"] = base_adicional_mes
        consolidated[TributoAlvo.IRPJ_ADICIONAL.value]["imposto_devido"] = imposto_adicional_mes

        total_impostos = quantize_money(
            sum((values["imposto_devido"] for values in consolidated.values()), start=Decimal("0.00"))
        )

        output = FiscalCalculationOutput(
            competencia_id=competencia_id,
            consolidada=consolidada,
            obra_id=obra_id,
            fechamento_trimestral=fechamento_trimestral,
            tributos=consolidated,
            total_impostos=total_impostos,
        )

        if not persist:
            return output

        apuracao_id = self._persist_apuracao(
            empresa_id=empresa_id,
            competencia=competencia,
            obra_id=obra_id,
            consolidada=consolidada,
            fechamento_trimestral=fechamento_trimestral,
            tributos=consolidated,
            total_impostos=total_impostos,
        )

        return FiscalCalculationOutput(
            competencia_id=output.competencia_id,
            consolidada=output.consolidada,
            obra_id=output.obra_id,
            fechamento_trimestral=output.fechamento_trimestral,
            tributos=output.tributos,
            total_impostos=output.total_impostos,
            apuracao_id=apuracao_id,
        )

    def invalidate_apuracoes_for_lancamento(
        self,
        empresa_id: int,
        obra_id: int,
        competencia_id: int,
    ) -> None:
        with get_session() as session:
            session.execute(
                Apuracao.__table__.update()
                .where(
                    Apuracao.empresa_id == empresa_id,
                    Apuracao.competencia_id == competencia_id,
                    Apuracao.apuracao_valida.is_(True),
                    or_(
                        Apuracao.obra_id == obra_id,
                        and_(Apuracao.obra_id.is_(None), Apuracao.consolidada.is_(True)),
                    ),
                )
                .values(apuracao_valida=False)
            )
            session.commit()

    def _persist_apuracao(
        self,
        empresa_id: int,
        competencia: Competencia,
        obra_id: int | None,
        consolidada: bool,
        fechamento_trimestral: bool,
        tributos: dict[str, dict[str, Decimal]],
        total_impostos: Decimal,
    ) -> int:
        with get_session() as session:
            versao_atual = session.execute(
                select(Apuracao)
                .where(
                    Apuracao.empresa_id == empresa_id,
                    Apuracao.competencia_id == competencia.id,
                    Apuracao.consolidada.is_(consolidada),
                    Apuracao.obra_id == obra_id,
                    Apuracao.apuracao_valida.is_(True),
                )
                .order_by(Apuracao.versao.desc())
                .limit(1)
            ).scalar_one_or_none()

            nova_versao = (versao_atual.versao + 1) if versao_atual else 1

            if versao_atual:
                versao_atual.apuracao_valida = False

            memoria_resumo = (
                f"periodicidade={'TRIMESTRAL' if fechamento_trimestral else 'MENSAL_PROJECAO'};"
                f" total={total_impostos}"
            )
            apuracao = Apuracao(
                empresa_id=empresa_id,
                obra_id=obra_id,
                competencia_id=competencia.id,
                consolidada=consolidada,
                total_impostos=total_impostos,
                memoria_resumo=memoria_resumo,
                versao=nova_versao,
                apuracao_valida=True,
            )
            session.add(apuracao)
            session.flush()

            ordem = 1
            for tributo_name in [
                TributoAlvo.PIS.value,
                TributoAlvo.COFINS.value,
                TributoAlvo.CSLL.value,
                TributoAlvo.IRPJ.value,
                TributoAlvo.IRPJ_ADICIONAL.value,
                TributoAlvo.ISS.value,
            ]:
                values = tributos[tributo_name]
                descricao = (
                    f"Base original {values['base_original']} + adicoes {values['adicoes']}"
                    f" - reducoes {values['reducoes']} = base final {values['base_final']}"
                )
                session.add(
                    ApuracaoItem(
                        apuracao_id=apuracao.id,
                        ordem=ordem,
                        tributo=TributoAlvo(tributo_name),
                        descricao_passo=descricao,
                        base_calculo=values["base_final"],
                        aliquota=values["imposto_devido"] / values["base_final"]
                        if values["base_final"] > 0
                        else Decimal("0.0000"),
                        valor_calculado=values["imposto_devido"],
                    )
                )
                ordem += 1

            self._save_due_dates(
                session=session,
                apuracao=apuracao,
                competencia=competencia,
                tributos=tributos,
                obra_id=obra_id,
            )
            session.commit()
            return apuracao.id

    def _save_due_dates(
        self,
        session,
        apuracao: Apuracao,
        competencia: Competencia,
        tributos: dict[str, dict[str, Decimal]],
        obra_id: int | None,
    ) -> None:
        rules = self._due_date_service.resolve_rules()

        for tributo in [
            TributoAlvo.PIS,
            TributoAlvo.COFINS,
            TributoAlvo.CSLL,
            TributoAlvo.IRPJ,
            TributoAlvo.IRPJ_ADICIONAL,
            TributoAlvo.ISS,
        ]:
            valor = tributos[tributo.value]["imposto_devido"]
            if valor <= 0:
                continue

            rule = rules[tributo]
            vencimento = self._due_date_service.compute_due_date(competencia, rule.dia_vencimento)
            session.add(
                ObrigacaoVencimento(
                    empresa_id=apuracao.empresa_id,
                    obra_id=obra_id,
                    apuracao_id=apuracao.id,
                    competencia_id=competencia.id,
                    tributo=tributo,
                    codigo_receita=rule.codigo_receita,
                    data_vencimento=vencimento,
                    valor=valor,
                    status=StatusObrigacao.EM_ABERTO,
                )
            )

    def _list_lancamentos(
        self,
        empresa_id: int,
        competencia_id: int,
        obra_id: int | None = None,
    ) -> list[LancamentoFiscal]:
        with get_session() as session:
            stmt = (
                select(LancamentoFiscal)
                .options(
                    selectinload(LancamentoFiscal.ajustes),
                    selectinload(LancamentoFiscal.obra).selectinload(Obra.perfil_tributario),
                )
                .where(
                    LancamentoFiscal.empresa_id == empresa_id,
                    LancamentoFiscal.competencia_id == competencia_id,
                )
            )
            if obra_id:
                stmt = stmt.where(LancamentoFiscal.obra_id == obra_id)
            return list(session.execute(stmt).scalars().all())

    def _list_lancamentos_for_quarter_to_date(
        self,
        empresa_id: int,
        competencia: Competencia,
        obra_id: int | None,
    ) -> list[LancamentoFiscal]:
        quarter_start_month = ((competencia.mes - 1) // 3) * 3 + 1

        with get_session() as session:
            competencia_ids = [
                comp.id
                for comp in session.execute(
                    select(Competencia)
                    .where(
                        Competencia.ano == competencia.ano,
                        Competencia.mes >= quarter_start_month,
                        Competencia.mes <= competencia.mes,
                    )
                    .order_by(Competencia.mes.asc())
                )
                .scalars()
                .all()
            ]

            if not competencia_ids:
                return []

            stmt = (
                select(LancamentoFiscal)
                .options(
                    selectinload(LancamentoFiscal.ajustes),
                    selectinload(LancamentoFiscal.obra).selectinload(Obra.perfil_tributario),
                )
                .where(
                    LancamentoFiscal.empresa_id == empresa_id,
                    LancamentoFiscal.competencia_id.in_(competencia_ids),
                )
            )
            if obra_id:
                stmt = stmt.where(LancamentoFiscal.obra_id == obra_id)

            return list(session.execute(stmt).scalars().all())

    def _build_lancamento_summary(self, lancamento: LancamentoFiscal) -> dict[str, dict[str, Decimal]]:
        ajustes = [
            AjusteFiscalInput(
                tributo_alvo=a.tributo_alvo.value,
                tipo_ajuste=a.tipo_ajuste.value,
                valor=a.valor,
                descricao=a.descricao,
                justificativa=a.justificativa,
                documento_referencia=a.documento_referencia,
                observacao=a.observacao,
            )
            for a in (lancamento.ajustes or [])
        ]

        return self._lancamento_service.calculate_adjustment_summary(
            receita_bruta=lancamento.receita_bruta,
            receita_tributavel_pis_cofins=lancamento.receita_tributavel_pis_cofins,
            ajustes=ajustes,
            obra_id=lancamento.obra_id,
        )

    def _calculate_iss(self, lancamentos: list[LancamentoFiscal]) -> Decimal:
        total = Decimal("0.00")
        for lancamento in lancamentos:
            aliquota = Decimal(str(lancamento.obra.aliquota_iss))
            base = Decimal(str(lancamento.receita_bruta))
            total += quantize_money(base * aliquota)
        return quantize_money(total)

    def _get_competencia(self, competencia_id: int) -> Competencia:
        with get_session() as session:
            competencia = session.get(Competencia, competencia_id)
        if not competencia:
            raise BusinessRuleError("Competencia nao encontrada")
        return competencia

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

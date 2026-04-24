"""Testes unitarios do motor fiscal (etapa 7)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.db.init_db import initialize_database
from app.db.session_manager import get_session
from app.models.apuracao import Apuracao
from app.models.apuracao_item import ApuracaoItem
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.obra import Obra
from app.models.perfil_tributario import PerfilTributario
from app.services import AjusteFiscalInput, FiscalCalculationService, LancamentoFiscalInput, LancamentoFiscalService


def _next_cnpj() -> str:
    with get_session() as session:
        max_id = session.execute(select(Empresa.id).order_by(Empresa.id.desc()).limit(1)).scalar_one_or_none()
    base = (max_id or 0) + 1
    return f"9900000000{base:04d}"[:14]


def _create_empresa_obra(perfil_nome: str, codigo: str, aliquota_iss: str = "0.05") -> tuple[int, int]:
    initialize_database()
    with get_session() as session:
        perfil = session.execute(
            select(PerfilTributario).where(PerfilTributario.nome == perfil_nome)
        ).scalar_one()

        empresa = Empresa(
            cnpj=_next_cnpj(),
            razao_social=f"Empresa Fiscal {codigo}",
            status_ativo=True,
        )
        session.add(empresa)
        session.flush()

        obra = Obra(
            empresa_id=empresa.id,
            perfil_tributario_id=perfil.id,
            codigo_interno=f"OBR-{codigo}",
            nome=f"Obra {codigo}",
            cidade="Sao Paulo",
            uf="SP",
            atividade_principal="Servicos",
            aliquota_iss=aliquota_iss,
            status_ativo=True,
        )
        session.add(obra)
        session.commit()
        return empresa.id, obra.id


def _competencia_id(ref: str) -> int:
    with get_session() as session:
        return session.execute(select(Competencia).where(Competencia.referencia == ref)).scalar_one().id


def _save_lancamento(
    empresa_id: int,
    obra_id: int,
    competencia_id: int,
    receita_bruta: str,
    ajustes: list[AjusteFiscalInput] | None = None,
) -> None:
    service = LancamentoFiscalService()
    payload = LancamentoFiscalInput(
        empresa_id=empresa_id,
        obra_id=obra_id,
        competencia_id=competencia_id,
        receita_bruta=receita_bruta,
    )
    service.save_lancamento(payload, ajustes or [])


def test_fiscal_motor_simple_services_case_with_persistence() -> None:
    empresa_id, obra_id = _create_empresa_obra("SERVICOS_PADRAO", "SIMPLE", aliquota_iss="0.05")
    comp_1 = _competencia_id("01/2026")
    _save_lancamento(empresa_id, obra_id, comp_1, "10000,00")

    service = FiscalCalculationService()
    result = service.calculate_for_scope(
        empresa_id=empresa_id,
        competencia_id=comp_1,
        obra_id=obra_id,
        consolidada=False,
        persist=True,
    )

    assert result.apuracao_id is not None
    assert str(result.tributos["PIS"]["imposto_devido"]) == "65.00"
    assert str(result.tributos["COFINS"]["imposto_devido"]) == "300.00"
    assert str(result.tributos["IRPJ"]["imposto_devido"]) == "480.00"
    assert str(result.tributos["CSLL"]["imposto_devido"]) == "108.00"
    assert str(result.tributos["ISS"]["imposto_devido"]) == "500.00"

    with get_session() as session:
        apuracao = session.get(Apuracao, result.apuracao_id)
        itens = list(
            session.execute(select(ApuracaoItem).where(ApuracaoItem.apuracao_id == result.apuracao_id)).scalars().all()
        )

    assert apuracao is not None
    assert apuracao.apuracao_valida is True
    assert apuracao.versao == 1
    assert len(itens) == 6


def test_fiscal_motor_applies_individual_adjustments_by_tributo() -> None:
    empresa_id, obra_id = _create_empresa_obra("SERVICOS_PADRAO", "ADJ")
    comp_1 = _competencia_id("01/2026")
    _save_lancamento(
        empresa_id,
        obra_id,
        comp_1,
        "50000,00",
        ajustes=[
            AjusteFiscalInput(
                tributo_alvo="PIS",
                tipo_ajuste="ADICAO",
                valor="1000,00",
                descricao="Ajuste PIS +",
                justificativa="Teste",
            ),
            AjusteFiscalInput(
                tributo_alvo="PIS",
                tipo_ajuste="REDUCAO",
                valor="300,00",
                descricao="Ajuste PIS -",
                justificativa="Teste",
            ),
            AjusteFiscalInput(
                tributo_alvo="IRPJ",
                tipo_ajuste="ADICAO",
                valor="700,00",
                descricao="Ajuste IRPJ +",
                justificativa="Teste",
            ),
            AjusteFiscalInput(
                tributo_alvo="CSLL",
                tipo_ajuste="REDUCAO",
                valor="1000,00",
                descricao="Ajuste CSLL -",
                justificativa="Teste",
            ),
        ],
    )

    result = FiscalCalculationService().calculate_for_scope(
        empresa_id=empresa_id,
        competencia_id=comp_1,
        obra_id=obra_id,
        persist=False,
    )

    assert str(result.tributos["PIS"]["base_final"]) == "50700.00"
    assert str(result.tributos["PIS"]["imposto_devido"]) == "329.55"
    assert str(result.tributos["IRPJ"]["base_final"]) == "16224.00"
    assert str(result.tributos["IRPJ"]["imposto_devido"]) == "2433.60"
    assert str(result.tributos["CSLL"]["base_final"]) == "5880.00"
    assert str(result.tributos["CSLL"]["imposto_devido"]) == "529.20"


def test_fiscal_motor_handles_irpj_additional_on_quarter_close() -> None:
    empresa_id, obra_id = _create_empresa_obra("SERVICOS_PADRAO", "TRI")
    comp_1 = _competencia_id("01/2026")
    comp_2 = _competencia_id("02/2026")
    comp_3 = _competencia_id("03/2026")

    _save_lancamento(empresa_id, obra_id, comp_1, "100000,00")
    _save_lancamento(empresa_id, obra_id, comp_2, "100000,00")
    _save_lancamento(empresa_id, obra_id, comp_3, "100000,00")

    service = FiscalCalculationService()
    proj_fev = service.calculate_for_scope(
        empresa_id=empresa_id,
        competencia_id=comp_2,
        obra_id=obra_id,
        persist=False,
    )
    fechamento_mar = service.calculate_for_scope(
        empresa_id=empresa_id,
        competencia_id=comp_3,
        obra_id=obra_id,
        persist=False,
    )

    assert proj_fev.fechamento_trimestral is False
    assert str(proj_fev.tributos["IRPJ_ADICIONAL"]["base_final"]) == "44000.00"
    assert str(proj_fev.tributos["IRPJ_ADICIONAL"]["imposto_devido"]) == "4400.00"

    assert fechamento_mar.fechamento_trimestral is True
    assert str(fechamento_mar.tributos["IRPJ_ADICIONAL"]["base_final"]) == "76000.00"
    assert str(fechamento_mar.tributos["IRPJ_ADICIONAL"]["imposto_devido"]) == "7600.00"


def test_fiscal_motor_consolidates_multiple_obras_and_versions() -> None:
    empresa_id, obra_1 = _create_empresa_obra("SERVICOS_PADRAO", "CONS1", aliquota_iss="0.05")

    with get_session() as session:
        perfil_comercio = session.execute(
            select(PerfilTributario).where(PerfilTributario.nome == "COMERCIO_PADRAO")
        ).scalar_one()
        obra_2_entity = Obra(
            empresa_id=empresa_id,
            perfil_tributario_id=perfil_comercio.id,
            codigo_interno="OBR-CONS2",
            nome="Obra CONS2",
            cidade="Campinas",
            uf="SP",
            atividade_principal="Comercio",
            aliquota_iss=Decimal("0.02"),
            status_ativo=True,
        )
        session.add(obra_2_entity)
        session.commit()
        obra_2 = obra_2_entity.id

    comp_1 = _competencia_id("01/2026")
    _save_lancamento(empresa_id, obra_1, comp_1, "100000,00")
    _save_lancamento(empresa_id, obra_2, comp_1, "50000,00")

    service = FiscalCalculationService()
    first = service.calculate_for_scope(
        empresa_id=empresa_id,
        competencia_id=comp_1,
        consolidada=True,
        persist=True,
    )
    second = service.calculate_for_scope(
        empresa_id=empresa_id,
        competencia_id=comp_1,
        consolidada=True,
        persist=True,
    )

    assert first.apuracao_id is not None
    assert second.apuracao_id is not None
    assert str(second.tributos["PIS"]["imposto_devido"]) == "975.00"
    assert str(second.tributos["ISS"]["imposto_devido"]) == "6000.00"

    with get_session() as session:
        apuracoes = list(
            session.execute(
                select(Apuracao)
                .where(
                    Apuracao.empresa_id == empresa_id,
                    Apuracao.competencia_id == comp_1,
                    Apuracao.consolidada.is_(True),
                )
                .order_by(Apuracao.versao.asc())
            )
            .scalars()
            .all()
        )

    assert len(apuracoes) == 2
    assert apuracoes[0].apuracao_valida is False
    assert apuracoes[1].apuracao_valida is True
    assert apuracoes[1].versao == 2

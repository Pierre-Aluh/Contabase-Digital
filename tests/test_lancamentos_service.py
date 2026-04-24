"""Testes de integracao para lancamentos fiscais e ajustes."""

from __future__ import annotations

from sqlalchemy import select

from app.db.init_db import initialize_database
from app.db.session_manager import get_session
from app.models.ajuste_fiscal import AjusteFiscal
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.perfil_tributario import PerfilTributario
from app.services import AjusteFiscalInput, LancamentoFiscalInput, LancamentoFiscalService


def _ensure_base_data() -> tuple[int, int, int, int]:
    initialize_database()
    with get_session() as session:
        competencia_1 = session.execute(
            select(Competencia).where(Competencia.referencia == "01/2026")
        ).scalar_one()

        competencia_2 = session.execute(
            select(Competencia).where(Competencia.referencia == "02/2026")
        ).scalar_one()
        perfil = session.execute(select(PerfilTributario).limit(1)).scalar_one()

        empresa = session.execute(
            select(Empresa).where(Empresa.cnpj == "37483967000185")
        ).scalar_one_or_none()
        if empresa is None:
            empresa = Empresa(cnpj="37483967000185", razao_social="Empresa Lancamentos LTDA", status_ativo=True)
            session.add(empresa)
            session.flush()

        obra = session.execute(
            select(Obra).where(Obra.empresa_id == empresa.id, Obra.codigo_interno == "OBR-LCT-01")
        ).scalar_one_or_none()
        if obra is None:
            obra = Obra(
                empresa_id=empresa.id,
                perfil_tributario_id=perfil.id,
                codigo_interno="OBR-LCT-01",
                nome="Obra Lancamentos",
                cidade="Sao Paulo",
                uf="SP",
                atividade_principal="Construcao",
                aliquota_iss="0.05",
                status_ativo=True,
            )
            session.add(obra)
            session.flush()

        session.commit()
        return empresa.id, obra.id, competencia_1.id, competencia_2.id


def test_persist_multiple_ajustes_for_same_period() -> None:
    service = LancamentoFiscalService()
    empresa_id, obra_id, comp_1, _ = _ensure_base_data()

    existing = service.list_lancamentos(
        empresa_id=empresa_id,
        obra_id=obra_id,
        competencia_id=comp_1,
    )
    for lancamento in existing:
        service.delete_lancamento(lancamento.id)

    payload = LancamentoFiscalInput(
        empresa_id=empresa_id,
        obra_id=obra_id,
        competencia_id=comp_1,
        receita_bruta="50000,00",
        receita_juros="1500,00",
        atualizacao_monetaria="1000,00",
        observacoes="Lcto com ajustes",
        documento_referencia="C:/docs/nf-lote.pdf",
    )

    ajustes = [
        AjusteFiscalInput(
            tributo_alvo="PIS",
            tipo_ajuste="ADICAO",
            valor="1000,00",
            descricao="Receita omitida",
            justificativa="Inclusao apos conferencia",
        ),
        AjusteFiscalInput(
            tributo_alvo="PIS",
            tipo_ajuste="REDUCAO",
            valor="300,00",
            descricao="Desconto incondicional",
            justificativa="Ajuste de base permitido",
        ),
        AjusteFiscalInput(
            tributo_alvo="IRPJ",
            tipo_ajuste="ADICAO",
            valor="700,00",
            descricao="Ajuste de presuncao",
            justificativa="Memoria de calculo interna",
        ),
    ]

    saved = service.save_lancamento(payload, ajustes)

    with get_session() as session:
        lancamento = session.get(LancamentoFiscal, saved.id)
        ajustes_db = list(
            session.execute(
                select(AjusteFiscal).where(AjusteFiscal.lancamento_fiscal_id == saved.id).order_by(AjusteFiscal.id.asc())
            )
            .scalars()
            .all()
        )

    assert lancamento is not None
    assert lancamento.obra_id == obra_id
    assert lancamento.competencia_id == comp_1
    assert len(ajustes_db) == 3
    assert str(lancamento.receita_juros) == "1500.00"
    assert str(lancamento.atualizacao_monetaria) == "1000.00"
    assert ajustes_db[0].tributo_alvo.value == "PIS"
    assert ajustes_db[1].tipo_ajuste.value == "REDUCAO"
    assert ajustes_db[2].tributo_alvo.value == "IRPJ"

    resumo = service.calculate_adjustment_summary(
        receita_bruta=lancamento.receita_bruta,
        receita_tributavel_pis_cofins=lancamento.receita_tributavel_pis_cofins,
        ajustes=[
            AjusteFiscalInput(
                tributo_alvo=a.tributo_alvo.value,
                tipo_ajuste=a.tipo_ajuste.value,
                valor=a.valor,
                descricao=a.descricao,
                justificativa=a.justificativa,
                documento_referencia=a.documento_referencia,
                observacao=a.observacao,
            )
            for a in ajustes_db
        ],
    )

    assert str(resumo["PIS"]["base_original"]) == "52500.00"
    assert str(resumo["PIS"]["adicoes"]) == "1000.00"
    assert str(resumo["PIS"]["reducoes"]) == "300.00"
    assert str(resumo["PIS"]["base_final"]) == "53200.00"


def test_duplicate_previous_month_without_id_reuse() -> None:
    service = LancamentoFiscalService()
    empresa_id, obra_id, comp_1, comp_2 = _ensure_base_data()

    base = service.list_lancamentos(empresa_id=empresa_id, obra_id=obra_id, competencia_id=comp_1)
    if not base:
        service.save_lancamento(
            LancamentoFiscalInput(
                empresa_id=empresa_id,
                obra_id=obra_id,
                competencia_id=comp_1,
                receita_bruta="10000,00",
                receita_juros="350,00",
            ),
            [
                AjusteFiscalInput(
                    tributo_alvo="COFINS",
                    tipo_ajuste="ADICAO",
                    valor="200,00",
                    descricao="Ajuste duplicacao",
                    justificativa="Base de teste",
                )
            ],
        )

    existing_target = service.list_lancamentos(
        empresa_id=empresa_id,
        obra_id=obra_id,
        competencia_id=comp_2,
    )
    for lct in existing_target:
        service.delete_lancamento(lct.id)

    novo = service.duplicate_from_previous_month(
        empresa_id=empresa_id,
        obra_id=obra_id,
        competencia_id=comp_2,
    )

    with get_session() as session:
        origem = session.execute(
            select(LancamentoFiscal).where(
                LancamentoFiscal.obra_id == obra_id,
                LancamentoFiscal.competencia_id == comp_1,
            )
        ).scalar_one()
        ajustes_origem = list(
            session.execute(select(AjusteFiscal).where(AjusteFiscal.lancamento_fiscal_id == origem.id)).scalars().all()
        )
        ajustes_novo = list(
            session.execute(select(AjusteFiscal).where(AjusteFiscal.lancamento_fiscal_id == novo.id)).scalars().all()
        )

    assert novo.id != origem.id
    assert novo.competencia_id == comp_2
    assert str(novo.receita_juros) == str(origem.receita_juros)
    assert len(ajustes_novo) == len(ajustes_origem)
    if ajustes_novo:
        assert ajustes_novo[0].id != ajustes_origem[0].id
        assert ajustes_novo[0].descricao == ajustes_origem[0].descricao


def test_irpj_adicional_applies_only_over_exceeding_limit() -> None:
    service = LancamentoFiscalService()

    resumo_sem_excedente = service.calculate_adjustment_summary(
        receita_bruta="18000,00",
        receita_tributavel_pis_cofins="18000,00",
        ajustes=[],
    )
    assert str(resumo_sem_excedente["IRPJ_ADICIONAL"]["base_final"]) == "0.00"
    assert str(resumo_sem_excedente["IRPJ_ADICIONAL"]["imposto_devido"]) == "0.00"

    resumo_com_excedente = service.calculate_adjustment_summary(
        receita_bruta="50000,00",
        receita_tributavel_pis_cofins="50000,00",
        ajustes=[],
    )
    assert str(resumo_com_excedente["IRPJ_ADICIONAL"]["base_final"]) == "30000.00"
    assert str(resumo_com_excedente["IRPJ_ADICIONAL"]["imposto_devido"]) == "3000.00"


def test_summary_applies_presuncao_from_obra_profile() -> None:
    service = LancamentoFiscalService()
    _, obra_id, _, _ = _ensure_base_data()

    resumo = service.calculate_adjustment_summary(
        receita_bruta="50000,00",
        receita_tributavel_pis_cofins="50000,00",
        ajustes=[],
        obra_id=obra_id,
    )

    assert str(resumo["IRPJ"]["base_original"]) == "4000.00"
    assert str(resumo["CSLL"]["base_original"]) == "6000.00"
    assert str(resumo["IRPJ_ADICIONAL"]["base_original"]) == "0.00"
    assert str(resumo["IRPJ_ADICIONAL"]["imposto_devido"]) == "0.00"


def test_summary_applies_adjustments_before_presuncao_for_irpj_csll() -> None:
    service = LancamentoFiscalService()
    _, obra_id, _, _ = _ensure_base_data()

    resumo = service.calculate_adjustment_summary(
        receita_bruta="50000,00",
        receita_tributavel_pis_cofins="50000,00",
        ajustes=[
            AjusteFiscalInput(
                tributo_alvo="IRPJ",
                tipo_ajuste="ADICAO",
                valor="700,00",
                descricao="Ajuste receita IRPJ",
                justificativa="Teste ordem presuncao",
            ),
            AjusteFiscalInput(
                tributo_alvo="CSLL",
                tipo_ajuste="REDUCAO",
                valor="1000,00",
                descricao="Reducao receita CSLL",
                justificativa="Teste ordem presuncao",
            ),
        ],
        obra_id=obra_id,
    )

    # Perfil padrao da obra (8% IRPJ, 12% CSLL): aplica ajuste na receita e depois presuncao.
    assert str(resumo["IRPJ"]["base_original"]) == "4000.00"
    assert str(resumo["IRPJ"]["adicoes"]) == "56.00"
    assert str(resumo["IRPJ"]["base_final"]) == "4056.00"

    assert str(resumo["CSLL"]["base_original"]) == "6000.00"
    assert str(resumo["CSLL"]["reducoes"]) == "120.00"
    assert str(resumo["CSLL"]["base_final"]) == "5880.00"


def test_irpj_adicional_base_original_uses_irpj_base_final() -> None:
    service = LancamentoFiscalService()
    _, obra_id, _, _ = _ensure_base_data()

    resumo = service.calculate_adjustment_summary(
        receita_bruta="500000,00",
        receita_tributavel_pis_cofins="500000,00",
        ajustes=[
            AjusteFiscalInput(
                tributo_alvo="IRPJ",
                tipo_ajuste="ADICAO",
                valor="10000,00",
                descricao="Ajuste receita IRPJ",
                justificativa="Teste base original irpj adicional",
            )
        ],
        obra_id=obra_id,
    )

    # Base final IRPJ = (500000 + 10000) * 8% = 40800.
    # Base original IRPJ adicional deve usar a base final do IRPJ: 40800 - 20000 = 20800.
    assert str(resumo["IRPJ"]["base_final"]) == "40800.00"
    assert str(resumo["IRPJ_ADICIONAL"]["base_original"]) == "20800.00"

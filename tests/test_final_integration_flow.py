"""Testes de integracao da entrega final (relatorios + guias)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.enums import StatusObrigacao
from app.reports.report_export_service import ReportExportService, ReportFilters
from app.services import GuiaGenerationInput
from app.services import GuiaFilter, GuiaService


def _pick_empresa_competencia() -> tuple[int, int] | None:
    with get_session() as session:
        empresa = session.execute(select(Empresa).order_by(Empresa.id.asc())).scalars().first()
        competencia = (
            session.execute(select(Competencia).order_by(Competencia.ano.asc(), Competencia.mes.asc()))
            .scalars()
            .first()
        )
    if not empresa or not competencia:
        return None
    return empresa.id, competencia.id


def test_report_export_pipeline_creates_files(tmp_path: Path) -> None:
    chosen = _pick_empresa_competencia()
    if not chosen:
        pytest.skip("Sem empresa/competencia para validar exportacao")

    empresa_id, competencia_id = chosen
    service = ReportExportService()
    dataset = service.build_dataset(
        ReportFilters(
            empresa_id=empresa_id,
            obra_id=None,
            competencia_id=competencia_id,
            trimestre_ano=None,
            trimestre_numero=None,
            visao="CONSOLIDADA",
            tipo_relatorio="COMPLETO",
        )
    )

    pdf_path = service.export_pdf(dataset, str(tmp_path / "relatorio_final.pdf"))
    xlsx_path = service.export_xlsx(dataset, str(tmp_path / "relatorio_final.xlsx"))

    assert Path(pdf_path).exists()
    assert Path(xlsx_path).exists()
    assert dataset["summary"]["apuracoes"] is not None


def test_guia_status_roundtrip() -> None:
    service = GuiaService()
    obrigacoes = service.list_obrigacoes(GuiaFilter())
    if not obrigacoes:
        pytest.skip("Sem obrigacoes para validar status")

    target = obrigacoes[0]
    original_status = target.status.value

    service.update_status(target.id, StatusObrigacao.PAGO.value)
    after_paid = service.list_obrigacoes(GuiaFilter(status=StatusObrigacao.PAGO.value))
    assert any(item.id == target.id for item in after_paid)

    service.update_status(target.id, original_status)


def test_guia_official_submission_package() -> None:
    chosen = _pick_empresa_competencia()
    if not chosen:
        pytest.skip("Sem empresa/competencia para validar emissao oficial assistida")

    empresa_id, competencia_id = chosen
    service = GuiaService()
    pack = service.build_official_submission_package(
        GuiaGenerationInput(
            empresa_id=empresa_id,
            competencia_id=competencia_id,
            tributo="PIS",
            visao="CONSOLIDADA",
            obra_id=None,
            observacoes="Teste emissao oficial",
        )
    )

    assert pack["portal_url"].startswith("http")
    assert "EMISSAO OFICIAL" in pack["copy_payload"]
    assert "codigo_receita" in pack

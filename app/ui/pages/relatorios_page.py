"""Pagina funcional de relatorios com exportacao PDF e XLSX."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.obra import Obra
from app.reports.report_export_service import ReportExportService, ReportFilters


class RelatoriosPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = ReportExportService()
        self._dataset: dict | None = None

        self._empresa_data: dict[int, Empresa] = {}
        self._obra_data: dict[int, Obra] = {}
        self._competencia_data: dict[int, Competencia] = {}

        self._build_ui()
        self._load_filters_data()
        self._refresh_preview()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel("Relatorios")
        title.setObjectName("AppTitle")
        desc = QLabel("Gere relatorios PDF e XLSX por obra e consolidado da empresa.")
        desc.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(desc)

        filter_card = QFrame()
        filter_card.setObjectName("DashCard")
        form = QGridLayout(filter_card)
        form.setContentsMargins(12, 10, 12, 10)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)

        self.empresa = QComboBox()
        self.obra = QComboBox()
        self.competencia = QComboBox()
        self.trimestre_ano = QComboBox()
        self.trimestre_numero = QComboBox()
        self.visao = QComboBox()
        self.tipo_relatorio = QComboBox()

        self.visao.addItem("Por obra", "POR_OBRA")
        self.visao.addItem("Consolidada", "CONSOLIDADA")

        self.tipo_relatorio.addItem("Completo", "COMPLETO")
        self.tipo_relatorio.addItem("Memoria de calculo", "MEMORIA")
        self.tipo_relatorio.addItem("Composicao dos tributos", "COMPOSICAO")
        self.tipo_relatorio.addItem("Evolucao mensal", "EVOLUCAO")
        self.tipo_relatorio.addItem("Vencimentos", "VENCIMENTOS")

        for q in [1, 2, 3, 4]:
            self.trimestre_numero.addItem(f"{q}o trimestre", q)

        form.addWidget(QLabel("Empresa"), 0, 0)
        form.addWidget(self.empresa, 0, 1)
        form.addWidget(QLabel("Obra"), 0, 2)
        form.addWidget(self.obra, 0, 3)

        form.addWidget(QLabel("Competencia"), 1, 0)
        form.addWidget(self.competencia, 1, 1)
        form.addWidget(QLabel("Ano/Trimestre"), 1, 2)

        quarter_wrap = QWidget()
        qlay = QHBoxLayout(quarter_wrap)
        qlay.setContentsMargins(0, 0, 0, 0)
        qlay.setSpacing(6)
        qlay.addWidget(self.trimestre_ano)
        qlay.addWidget(self.trimestre_numero)
        form.addWidget(quarter_wrap, 1, 3)

        form.addWidget(QLabel("Visao"), 2, 0)
        form.addWidget(self.visao, 2, 1)
        form.addWidget(QLabel("Tipo"), 2, 2)
        form.addWidget(self.tipo_relatorio, 2, 3)

        actions = QWidget()
        act_l = QHBoxLayout(actions)
        act_l.setContentsMargins(0, 0, 0, 0)
        act_l.setSpacing(8)
        self.btn_preview = QPushButton("Atualizar previa")
        self.btn_preview.setObjectName("DashActionSecondary")
        self.btn_pdf = QPushButton("Exportar PDF")
        self.btn_pdf.setObjectName("DashActionPrimary")
        self.btn_xlsx = QPushButton("Exportar XLSX")
        self.btn_xlsx.setObjectName("DashActionSecondary")
        act_l.addWidget(self.btn_preview)
        act_l.addWidget(self.btn_pdf)
        act_l.addWidget(self.btn_xlsx)
        act_l.addStretch(1)
        form.addWidget(actions, 3, 0, 1, 4)

        layout.addWidget(filter_card)

        self.consistency_label = QLabel("Consistencia: -")
        self.consistency_label.setObjectName("DashMuted")
        layout.addWidget(self.consistency_label)

        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setObjectName("DashTributosTable")
        self.preview.setMinimumHeight(260)
        layout.addWidget(self.preview, 1)

        self.empresa.currentIndexChanged.connect(self._on_empresa_changed)
        self.btn_preview.clicked.connect(self._refresh_preview)
        self.btn_pdf.clicked.connect(self._export_pdf)
        self.btn_xlsx.clicked.connect(self._export_xlsx)

    def _load_filters_data(self) -> None:
        with get_session() as session:
            empresas = list(session.execute(select(Empresa).order_by(Empresa.razao_social.asc())).scalars().all())
            obras = list(session.execute(select(Obra).order_by(Obra.nome.asc())).scalars().all())
            competencias = list(
                session.execute(select(Competencia).order_by(Competencia.ano.desc(), Competencia.mes.desc()))
                .scalars()
                .all()
            )

        self._empresa_data = {e.id: e for e in empresas}
        self._obra_data = {o.id: o for o in obras}
        self._competencia_data = {c.id: c for c in competencias}

        self.empresa.clear()
        self.empresa.addItem("Todas", None)
        for e in empresas:
            self.empresa.addItem(e.razao_social, e.id)

        self.competencia.clear()
        self.competencia.addItem("Todas", None)
        for c in competencias:
            self.competencia.addItem(c.referencia, c.id)

        years = sorted({c.ano for c in competencias}, reverse=True)
        if not years:
            years = [datetime.now().year]
        self.trimestre_ano.clear()
        self.trimestre_ano.addItem("Todos", None)
        for y in years:
            self.trimestre_ano.addItem(str(y), y)

        self._populate_obras(None)

    def _populate_obras(self, empresa_id: int | None) -> None:
        self.obra.clear()
        self.obra.addItem("Todas", None)
        for obra in self._obra_data.values():
            if empresa_id and obra.empresa_id != empresa_id:
                continue
            self.obra.addItem(obra.nome, obra.id)

    def _on_empresa_changed(self) -> None:
        emp_id = self.empresa.currentData()
        self._populate_obras(emp_id if isinstance(emp_id, int) else None)

    def _collect_filters(self) -> ReportFilters:
        return ReportFilters(
            empresa_id=self.empresa.currentData(),
            obra_id=self.obra.currentData(),
            competencia_id=self.competencia.currentData(),
            trimestre_ano=self.trimestre_ano.currentData(),
            trimestre_numero=self.trimestre_numero.currentData(),
            visao=str(self.visao.currentData()),
            tipo_relatorio=str(self.tipo_relatorio.currentData()),
        )

    def _refresh_preview(self) -> None:
        try:
            self._dataset = self._service.build_dataset(self._collect_filters())
        except Exception as exc:
            QMessageBox.critical(self, "Relatorios", f"Falha ao montar dados do relatorio:\n{exc}")
            return

        d = self._dataset
        assert d is not None

        status = "OK" if d["consistency_ok"] else "ALERTA"
        self.consistency_label.setText(
            f"Consistencia: {status} | Delta memoria x apuracao: {d['summary']['delta_consistencia']}"
        )

        lines = [
            "PREVIA DO RELATORIO",
            "",
            d["filters_text"],
            f"Gerado em: {d['generated_at']}",
            "",
            "Resumo:",
            f"- Apuracoes: {d['summary']['apuracoes']}",
            f"- Lancamentos: {d['summary']['lancamentos']}",
            f"- Obrigacoes: {d['summary']['obrigacoes']}",
            f"- Total apuracoes: {d['summary']['total_apuracoes']}",
            f"- Total itens memoria: {d['summary']['total_itens']}",
            f"- Delta consistencia: {d['summary']['delta_consistencia']}",
            "",
            f"Memoria de calculo: {len(d['memoria_rows'])} linhas",
            f"Composicao de tributos: {len(d['composicao_rows'])} linhas",
            f"Evolucao mensal: {len(d['evolucao_rows'])} linhas",
            f"Vencimentos: {len(d['vencimento_rows'])} linhas",
        ]

        self.preview.setPlainText("\n".join(lines))

    def _export_pdf(self) -> None:
        if not self._dataset:
            self._refresh_preview()
        if not self._dataset:
            return

        default_name = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        out, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", str(Path.cwd() / default_name), "PDF (*.pdf)")
        if not out:
            return
        try:
            path = self._service.export_pdf(self._dataset, out)
            QMessageBox.information(self, "Relatorios", f"PDF gerado com sucesso:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Relatorios", f"Falha na exportacao PDF:\n{exc}")

    def _export_xlsx(self) -> None:
        if not self._dataset:
            self._refresh_preview()
        if not self._dataset:
            return

        default_name = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        out, _ = QFileDialog.getSaveFileName(self, "Salvar XLSX", str(Path.cwd() / default_name), "Excel (*.xlsx)")
        if not out:
            return
        try:
            path = self._service.export_xlsx(self._dataset, out)
            QMessageBox.information(self, "Relatorios", f"XLSX gerado com sucesso:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Relatorios", f"Falha na exportacao XLSX:\n{exc}")

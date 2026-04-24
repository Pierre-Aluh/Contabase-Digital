"""Pagina funcional de guias, vencimentos e status."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)
from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.enums import StatusObrigacao, TributoAlvo
from app.models.obra import Obra
from app.services import GuiaFilter, GuiaGenerationInput, GuiaPortalConfig, GuiaService
from app.utils.formatters import format_brl


class GuiasPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._service = GuiaService()
        self._obrigacoes = []
        self._empresa_data: dict[int, Empresa] = {}
        self._obra_data: dict[int, Obra] = {}
        self._competencia_data: dict[int, Competencia] = {}

        self._build_ui()
        self._load_filters_data()
        self._load_rules()
        self._refresh_table()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("GuiasScrollContent")
        root.addWidget(scroll)
        scroll.setWidget(content)

        root = QVBoxLayout(content)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        title = QLabel("Guias e Vencimentos")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Cadastre regras, acompanhe obrigacoes e gere demonstrativo interno de recolhimento.")
        subtitle.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(subtitle)

        rules_card = QFrame()
        rules_card.setObjectName("DashCard")
        rules_grid = QGridLayout(rules_card)
        rules_grid.setContentsMargins(12, 10, 12, 10)
        rules_grid.setHorizontalSpacing(8)
        rules_grid.setVerticalSpacing(6)

        self._rule_code: dict[str, QLineEdit] = {}
        self._rule_day: dict[str, QLineEdit] = {}

        headers = ["Tributo", "Codigo Receita", "Dia Vencimento"]
        for col, text in enumerate(headers):
            h = QLabel(text)
            h.setObjectName("DashSectionTitle")
            rules_grid.addWidget(h, 0, col)

        tributos = [
            TributoAlvo.PIS.value,
            TributoAlvo.COFINS.value,
            TributoAlvo.IRPJ.value,
            TributoAlvo.CSLL.value,
            TributoAlvo.IRPJ_ADICIONAL.value,
            TributoAlvo.ISS.value,
        ]
        for row, trib in enumerate(tributos, start=1):
            rules_grid.addWidget(QLabel(trib), row, 0)
            code = QLineEdit()
            code.setMaxLength(30)
            code.setMaximumWidth(220)
            day = QLineEdit()
            day.setMaxLength(2)
            day.setPlaceholderText("1-31")
            day.setMaximumWidth(90)
            self._rule_code[trib] = code
            self._rule_day[trib] = day
            rules_grid.addWidget(code, row, 1)
            rules_grid.addWidget(day, row, 2)

        self.btn_save_rules = QPushButton("Salvar regras de vencimento")
        self.btn_save_rules.setObjectName("DashActionSecondary")
        self.btn_save_rules.setMaximumWidth(280)
        rules_grid.addWidget(self.btn_save_rules, len(tributos) + 1, 0)
        # col 3 absorbe o espaço extra para que cols 0-2 não se estiquem
        rules_grid.setColumnStretch(0, 0)
        rules_grid.setColumnStretch(1, 0)
        rules_grid.setColumnStretch(2, 0)
        rules_grid.setColumnStretch(3, 1)
        root.addWidget(rules_card)

        filter_card = QFrame()
        filter_card.setObjectName("DashCard")
        fgrid = QGridLayout(filter_card)
        fgrid.setContentsMargins(12, 10, 12, 10)
        fgrid.setHorizontalSpacing(8)
        fgrid.setVerticalSpacing(8)

        self.f_empresa = QComboBox()
        self.f_obra = QComboBox()
        self.f_comp = QComboBox()
        self.f_status = QComboBox()
        self.f_tributo = QComboBox()
        for combo in [self.f_empresa, self.f_obra, self.f_comp, self.f_status, self.f_tributo]:
            combo.setMaximumWidth(320)

        self.f_status.addItem("Todos", None)
        self.f_status.addItem("Em aberto", StatusObrigacao.EM_ABERTO.value)
        self.f_status.addItem("Pago", StatusObrigacao.PAGO.value)
        self.f_status.addItem("Vencido", StatusObrigacao.VENCIDO.value)
        self.f_status.addItem("Cancelado", StatusObrigacao.CANCELADO.value)
        self.f_status.addItem("Nao aplicavel", StatusObrigacao.NAO_APLICAVEL.value)

        self.f_tributo.addItem("Todos", None)
        for trib in tributos:
            self.f_tributo.addItem(trib, trib)

        fgrid.addWidget(QLabel("Empresa"), 0, 0)
        fgrid.addWidget(self.f_empresa, 0, 1)
        fgrid.addWidget(QLabel("Obra"), 0, 2)
        fgrid.addWidget(self.f_obra, 0, 3)
        fgrid.addWidget(QLabel("Competencia"), 1, 0)
        fgrid.addWidget(self.f_comp, 1, 1)
        fgrid.addWidget(QLabel("Status"), 1, 2)
        fgrid.addWidget(self.f_status, 1, 3)
        fgrid.addWidget(QLabel("Tributo"), 2, 0)
        fgrid.addWidget(self.f_tributo, 2, 1)

        self.btn_filtrar = QPushButton("Atualizar obrigacoes")
        self.btn_filtrar.setObjectName("DashActionPrimary")
        self.btn_filtrar.setMaximumWidth(280)
        fgrid.addWidget(self.btn_filtrar, 2, 3)
        # cols 0 e 2 são labels fixos; cols 1 e 3 crescem até max-width; col 4 absorve o resto
        fgrid.setColumnStretch(0, 0)
        fgrid.setColumnStretch(1, 1)
        fgrid.setColumnStretch(2, 0)
        fgrid.setColumnStretch(3, 1)
        fgrid.setColumnStretch(4, 2)
        root.addWidget(filter_card)

        self.table = QTableWidget(0, 9)
        self.table.setObjectName("DashTributosTable")
        self.table.setHorizontalHeaderLabels(
            ["ID", "Empresa", "Obra", "Competencia", "Tributo", "Codigo", "Vencimento", "Valor", "Status"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        root.addWidget(self.table, 1)

        action_row = QWidget()
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(8)
        self.btn_pago = QPushButton("Marcar pago")
        self.btn_vencido = QPushButton("Marcar vencido")
        self.btn_cancelado = QPushButton("Marcar cancelado")
        self.btn_reabrir = QPushButton("Reabrir")
        for btn in [self.btn_pago, self.btn_vencido, self.btn_cancelado, self.btn_reabrir]:
            btn.setObjectName("DashActionSecondary")
            action_layout.addWidget(btn)
        action_layout.addStretch(1)
        root.addWidget(action_row)

        guia_card = QFrame()
        guia_card.setObjectName("DashCard")
        ggrid = QGridLayout(guia_card)
        ggrid.setContentsMargins(12, 10, 12, 10)
        ggrid.setHorizontalSpacing(8)
        ggrid.setVerticalSpacing(8)

        self.g_empresa = QComboBox()
        self.g_comp = QComboBox()
        self.g_visao = QComboBox()
        self.g_obra = QComboBox()
        self.g_tributo = QComboBox()
        for combo in [self.g_empresa, self.g_comp, self.g_visao, self.g_obra, self.g_tributo]:
            combo.setMaximumWidth(320)
        self.g_obs = QTextEdit()
        self.g_obs.setFixedHeight(50)
        self.g_obs.setMaximumWidth(420)
        self.btn_gerar_pdf = QPushButton("Gerar demonstrativo PDF")
        self.btn_gerar_pdf.setObjectName("DashActionPrimary")
        self.btn_gerar_pdf.setMaximumWidth(280)
        self.btn_abrir_portal = QPushButton("Abrir portal oficial")
        self.btn_abrir_portal.setObjectName("DashActionSecondary")
        self.btn_abrir_portal.setMaximumWidth(240)
        self.btn_copiar_payload = QPushButton("Copiar dados oficiais")
        self.btn_copiar_payload.setObjectName("DashActionSecondary")
        self.btn_copiar_payload.setMaximumWidth(240)

        self.g_visao.addItem("Consolidada", "CONSOLIDADA")
        self.g_visao.addItem("Por obra", "POR_OBRA")
        for trib in tributos:
            self.g_tributo.addItem(trib, trib)

        ggrid.addWidget(QLabel("Empresa"), 0, 0)
        ggrid.addWidget(self.g_empresa, 0, 1)
        ggrid.addWidget(QLabel("Competencia"), 0, 2)
        ggrid.addWidget(self.g_comp, 0, 3)
        ggrid.addWidget(QLabel("Visao"), 1, 0)
        ggrid.addWidget(self.g_visao, 1, 1)
        ggrid.addWidget(QLabel("Obra"), 1, 2)
        ggrid.addWidget(self.g_obra, 1, 3)
        ggrid.addWidget(QLabel("Tributo"), 2, 0)
        ggrid.addWidget(self.g_tributo, 2, 1)
        ggrid.addWidget(QLabel("Observacoes"), 2, 2)
        ggrid.addWidget(self.g_obs, 2, 3)
        ggrid.addWidget(self.btn_gerar_pdf, 3, 3)
        ggrid.addWidget(self.btn_abrir_portal, 4, 2)
        ggrid.addWidget(self.btn_copiar_payload, 4, 3)

        self.portal_federal = QLineEdit()
        self.portal_federal.setMaximumWidth(620)
        self.portal_iss = QLineEdit()
        self.portal_iss.setMaximumWidth(620)
        self.btn_salvar_portais = QPushButton("Salvar configuracao de portais")
        self.btn_salvar_portais.setObjectName("DashActionSecondary")
        self.btn_salvar_portais.setMaximumWidth(280)
        ggrid.addWidget(QLabel("URL Portal Federal"), 5, 0)
        ggrid.addWidget(self.portal_federal, 5, 1, 1, 3)
        ggrid.addWidget(QLabel("URL Portal ISS"), 6, 0)
        ggrid.addWidget(self.portal_iss, 6, 1, 1, 3)
        ggrid.addWidget(self.btn_salvar_portais, 7, 3)
        # mesma estratégia: cols 1 e 3 crescem até max-width; col 4 absorve o resto
        ggrid.setColumnStretch(0, 0)
        ggrid.setColumnStretch(1, 1)
        ggrid.setColumnStretch(2, 0)
        ggrid.setColumnStretch(3, 1)
        ggrid.setColumnStretch(4, 2)

        root.addWidget(guia_card)

        self.btn_save_rules.clicked.connect(self._save_rules)
        self.btn_filtrar.clicked.connect(self._refresh_table)
        self.btn_pago.clicked.connect(lambda: self._update_selected_status(StatusObrigacao.PAGO.value))
        self.btn_vencido.clicked.connect(lambda: self._update_selected_status(StatusObrigacao.VENCIDO.value))
        self.btn_cancelado.clicked.connect(lambda: self._update_selected_status(StatusObrigacao.CANCELADO.value))
        self.btn_reabrir.clicked.connect(lambda: self._update_selected_status(StatusObrigacao.EM_ABERTO.value))
        self.btn_gerar_pdf.clicked.connect(self._gerar_demonstrativo)
        self.btn_abrir_portal.clicked.connect(self._abrir_portal_oficial)
        self.btn_copiar_payload.clicked.connect(self._copiar_payload_oficial)
        self.btn_salvar_portais.clicked.connect(self._save_portal_config)
        self.f_empresa.currentIndexChanged.connect(self._sync_obras_filter)
        self.g_empresa.currentIndexChanged.connect(self._sync_obras_geracao)

    def _load_filters_data(self) -> None:
        with get_session() as session:
            empresas = list(session.execute(select(Empresa).order_by(Empresa.razao_social.asc())).scalars().all())
            obras = list(session.execute(select(Obra).order_by(Obra.nome.asc())).scalars().all())
            competencias = list(
                session.execute(select(Competencia).order_by(Competencia.ano.desc(), Competencia.mes.desc())).scalars().all()
            )

        self._empresa_data = {e.id: e for e in empresas}
        self._obra_data = {o.id: o for o in obras}
        self._competencia_data = {c.id: c for c in competencias}

        self.f_empresa.clear()
        self.f_empresa.addItem("Todas", None)
        self.g_empresa.clear()
        for e in empresas:
            self.f_empresa.addItem(e.razao_social, e.id)
            self.g_empresa.addItem(e.razao_social, e.id)

        self.f_comp.clear()
        self.f_comp.addItem("Todas", None)
        self.g_comp.clear()
        for c in competencias:
            self.f_comp.addItem(c.referencia, c.id)
            self.g_comp.addItem(c.referencia, c.id)

        self._sync_obras_filter()
        self._sync_obras_geracao()
        self._load_portal_config()

    def _load_portal_config(self) -> None:
        config = self._service.get_portal_config()
        self.portal_federal.setText(config.federal_url)
        self.portal_iss.setText(config.iss_url)

    def _save_portal_config(self) -> None:
        federal = self.portal_federal.text().strip()
        iss = self.portal_iss.text().strip()
        if not federal.lower().startswith("http"):
            QMessageBox.warning(self, "Guias", "URL do portal federal invalida.")
            return
        if not iss.lower().startswith("http"):
            QMessageBox.warning(self, "Guias", "URL do portal ISS invalida.")
            return
        try:
            self._service.save_portal_config(GuiaPortalConfig(federal_url=federal, iss_url=iss))
            QMessageBox.information(self, "Guias", "Configuracao de portais salva.")
        except Exception as exc:
            QMessageBox.critical(self, "Guias", f"Falha ao salvar configuracao de portais:\n{exc}")

    def _sync_obras_filter(self) -> None:
        empresa_id = self.f_empresa.currentData()
        self.f_obra.clear()
        self.f_obra.addItem("Todas", None)
        for obra in self._obra_data.values():
            if empresa_id and obra.empresa_id != empresa_id:
                continue
            self.f_obra.addItem(obra.nome, obra.id)

    def _sync_obras_geracao(self) -> None:
        empresa_id = self.g_empresa.currentData()
        self.g_obra.clear()
        self.g_obra.addItem("Consolidado", None)
        for obra in self._obra_data.values():
            if empresa_id and obra.empresa_id != empresa_id:
                continue
            self.g_obra.addItem(obra.nome, obra.id)

    def _load_rules(self) -> None:
        rules = self._service.get_rules_snapshot()
        for tributo, payload in rules.items():
            self._rule_code[tributo].setText(payload["codigo_receita"])
            self._rule_day[tributo].setText(payload["dia_vencimento"])

    def _save_rules(self) -> None:
        values: dict[str, dict[str, str]] = {}
        for tributo in self._rule_code:
            dia_txt = self._rule_day[tributo].text().strip() or "25"
            try:
                dia = int(dia_txt)
            except ValueError:
                QMessageBox.warning(self, "Guias", f"Dia de vencimento invalido para {tributo}: {dia_txt}")
                return
            if dia < 1 or dia > 31:
                QMessageBox.warning(self, "Guias", f"Dia de vencimento fora da faixa para {tributo}: {dia}")
                return

            values[tributo] = {
                "codigo_receita": self._rule_code[tributo].text().strip(),
                "dia_vencimento": str(dia),
            }
        try:
            self._service.save_rules_snapshot(values)
            QMessageBox.information(self, "Guias", "Regras salvas com sucesso.")
        except Exception as exc:
            QMessageBox.critical(self, "Guias", f"Falha ao salvar regras:\n{exc}")

    def _refresh_table(self) -> None:
        filtro = GuiaFilter(
            empresa_id=self.f_empresa.currentData(),
            obra_id=self.f_obra.currentData(),
            competencia_id=self.f_comp.currentData(),
            tributo=self.f_tributo.currentData(),
            status=self.f_status.currentData(),
        )
        self._obrigacoes = self._service.list_obrigacoes(filtro)
        status_label = {
            StatusObrigacao.EM_ABERTO.value: "Em aberto",
            StatusObrigacao.PAGO.value: "Pago",
            StatusObrigacao.VENCIDO.value: "Vencido",
            StatusObrigacao.CANCELADO.value: "Cancelado",
            StatusObrigacao.NAO_APLICAVEL.value: "Nao aplicavel",
        }

        self.table.setRowCount(len(self._obrigacoes))
        for i, o in enumerate(self._obrigacoes):
            emp = self._empresa_data.get(o.empresa_id)
            obra = self._obra_data.get(o.obra_id) if o.obra_id else None
            comp = self._competencia_data.get(o.competencia_id)
            values = [
                str(o.id),
                emp.razao_social if emp else "-",
                obra.nome if obra else "Consolidado",
                comp.referencia if comp else "-",
                o.tributo.value,
                o.codigo_receita,
                o.data_vencimento.strftime("%d/%m/%Y"),
                format_brl(str(o.valor)),
                status_label.get(o.status.value, o.status.value),
            ]
            for c, val in enumerate(values):
                self.table.setItem(i, c, QTableWidgetItem(val))
        self.table.resizeColumnsToContents()

    def _selected_obrigacao_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        return int(item.text())

    def _update_selected_status(self, status: str) -> None:
        oid = self._selected_obrigacao_id()
        if oid is None:
            QMessageBox.warning(self, "Guias", "Selecione uma obrigacao na tabela.")
            return
        try:
            self._service.update_status(oid, status)
            self._refresh_table()
        except Exception as exc:
            QMessageBox.critical(self, "Guias", f"Falha ao atualizar status:\n{exc}")

    def _gerar_demonstrativo(self) -> None:
        params = self._build_generation_input()
        if params is None:
            return

        payload = self._service.build_demonstrativo_payload(
            params
        )

        filename = f"guia_{payload['tributo'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        out, _ = QFileDialog.getSaveFileName(self, "Salvar demonstrativo", str(Path.cwd() / filename), "PDF (*.pdf)")
        if not out:
            return

        try:
            path = self._service.export_demonstrativo_pdf(payload, out)
            QMessageBox.information(self, "Guias", f"Demonstrativo gerado com sucesso:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Guias", f"Falha ao gerar PDF:\n{exc}")

    def _build_generation_input(self) -> GuiaGenerationInput | None:
        empresa_id = self.g_empresa.currentData()
        competencia_id = self.g_comp.currentData()
        tributo = self.g_tributo.currentData()
        visao = self.g_visao.currentData()
        obra_id = self.g_obra.currentData()

        if empresa_id is None or competencia_id is None or tributo is None:
            QMessageBox.warning(self, "Guias", "Selecione empresa, competencia e tributo.")
            return None
        if visao == "POR_OBRA" and obra_id is None:
            QMessageBox.warning(self, "Guias", "Para visao por obra, selecione uma obra.")
            return None

        return GuiaGenerationInput(
            empresa_id=empresa_id,
            competencia_id=competencia_id,
            tributo=tributo,
            visao=visao,
            obra_id=obra_id,
            observacoes=self.g_obs.toPlainText().strip(),
        )

    def _abrir_portal_oficial(self) -> None:
        params = self._build_generation_input()
        if params is None:
            return
        try:
            pack = self._service.build_official_submission_package(params)
            ok = QDesktopServices.openUrl(QUrl(pack["portal_url"]))
            if not ok:
                QMessageBox.warning(self, "Guias", "Nao foi possivel abrir o portal oficial no navegador.")
        except Exception as exc:
            QMessageBox.critical(self, "Guias", f"Falha ao preparar emissao oficial:\n{exc}")

    def _copiar_payload_oficial(self) -> None:
        params = self._build_generation_input()
        if params is None:
            return
        try:
            pack = self._service.build_official_submission_package(params)
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(pack["copy_payload"])
            QMessageBox.information(self, "Guias", "Dados oficiais copiados para a area de transferencia.")
        except Exception as exc:
            QMessageBox.critical(self, "Guias", f"Falha ao copiar dados oficiais:\n{exc}")

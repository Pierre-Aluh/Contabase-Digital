"""Pagina de cadastro de empresas e obras."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from app.services import BusinessRuleError, EmpresaInput, EmpresaObraService, ObraInput
from app.ui.dialogs import EmpresaDialog, ObraDialog
from app.ui.pages.base_page import BasePage


class EmpresasPage(BasePage):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Empresas e Obras",
            description="Cadastro, consulta e gestao de empresas e obras vinculadas.",
            parent=parent,
        )
        self.service = EmpresaObraService()
        self.selected_empresa_id: int | None = None
        self.selected_obra_id: int | None = None
        self._build_ui()
        self.reload_empresas()

    def _build_ui(self) -> None:
        page_layout = self.layout()
        container = QWidget()
        root = QVBoxLayout(container)
        root.setSpacing(10)

        filter_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filtrar por razao social, nome fantasia ou CNPJ")
        self.search_edit.textChanged.connect(self.reload_empresas)
        filter_row.addWidget(self.search_edit, 1)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["TODOS", "ATIVAS", "INATIVAS"])
        self.status_combo.currentTextChanged.connect(self.reload_empresas)
        filter_row.addWidget(self.status_combo)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self.reload_empresas)
        filter_row.addWidget(btn_refresh)

        root.addLayout(filter_row)

        empresa_actions = QHBoxLayout()
        self.btn_new_empresa = QPushButton("Nova empresa")
        self.btn_new_empresa.clicked.connect(self._new_empresa)
        empresa_actions.addWidget(self.btn_new_empresa)

        self.btn_edit_empresa = QPushButton("Editar empresa")
        self.btn_edit_empresa.clicked.connect(self._edit_empresa)
        empresa_actions.addWidget(self.btn_edit_empresa)

        self.btn_delete_empresa = QPushButton("Excluir empresa")
        self.btn_delete_empresa.clicked.connect(self._delete_empresa)
        empresa_actions.addWidget(self.btn_delete_empresa)

        self.btn_toggle_empresa = QPushButton("Inativar")
        self.btn_toggle_empresa.clicked.connect(self._toggle_empresa)
        empresa_actions.addWidget(self.btn_toggle_empresa)
        empresa_actions.addStretch(1)
        root.addLayout(empresa_actions)

        self.empresas_table = QTableWidget(0, 5)
        self.empresas_table.setHorizontalHeaderLabels(["ID", "CNPJ", "Razao social", "Nome fantasia", "Status"])
        self.empresas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.empresas_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.empresas_table.verticalHeader().setVisible(False)
        self.empresas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.empresas_table.itemSelectionChanged.connect(self._on_empresa_selected)
        self.empresas_table.setAlternatingRowColors(True)
        emp_header = self.empresas_table.horizontalHeader()
        emp_header.setStretchLastSection(False)
        emp_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        emp_header.setSectionResizeMode(2, QHeaderView.Stretch)
        emp_header.setSectionResizeMode(3, QHeaderView.Stretch)
        root.addWidget(self.empresas_table, 2)

        self.empresa_detail_label = QLabel("Nenhuma empresa selecionada")
        self.empresa_detail_label.setObjectName("mutedLabel")
        root.addWidget(self.empresa_detail_label)

        obras_group = QGroupBox("Obras da empresa selecionada")
        obras_layout = QVBoxLayout(obras_group)

        obra_actions = QHBoxLayout()
        self.btn_new_obra = QPushButton("Nova obra")
        self.btn_new_obra.clicked.connect(self._new_obra)
        obra_actions.addWidget(self.btn_new_obra)

        self.btn_edit_obra = QPushButton("Editar obra")
        self.btn_edit_obra.clicked.connect(self._edit_obra)
        obra_actions.addWidget(self.btn_edit_obra)

        self.btn_delete_obra = QPushButton("Excluir obra")
        self.btn_delete_obra.clicked.connect(self._delete_obra)
        obra_actions.addWidget(self.btn_delete_obra)

        self.btn_toggle_obra = QPushButton("Inativar")
        self.btn_toggle_obra.clicked.connect(self._toggle_obra)
        obra_actions.addWidget(self.btn_toggle_obra)
        obra_actions.addStretch(1)

        obras_layout.addLayout(obra_actions)

        self.obras_table = QTableWidget(0, 7)
        self.obras_table.setHorizontalHeaderLabels(["ID", "Codigo", "Nome", "Cidade", "UF", "ISS", "Status"])
        self.obras_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.obras_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.obras_table.verticalHeader().setVisible(False)
        self.obras_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.obras_table.itemSelectionChanged.connect(self._on_obra_selected)
        self.obras_table.setAlternatingRowColors(True)
        obra_header = self.obras_table.horizontalHeader()
        obra_header.setStretchLastSection(False)
        obra_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        obra_header.setSectionResizeMode(2, QHeaderView.Stretch)
        obras_layout.addWidget(self.obras_table)

        root.addWidget(obras_group, 2)

        page_layout.insertWidget(page_layout.count() - 1, container)
        self._sync_buttons()

    def reload_empresas(self) -> None:
        try:
            empresas = self.service.list_empresas(self.search_edit.text(), self.status_combo.currentText())
        except Exception as exc:
            self._show_error(f"Falha ao carregar empresas: {exc}")
            return

        self.empresas_table.setRowCount(len(empresas))
        for row, empresa in enumerate(empresas):
            self._set_row_item(self.empresas_table, row, 0, str(empresa.id), empresa.id)
            self._set_row_item(self.empresas_table, row, 1, empresa.cnpj)
            self._set_row_item(self.empresas_table, row, 2, empresa.razao_social)
            self._set_row_item(self.empresas_table, row, 3, empresa.nome_fantasia or "-")
            self._set_row_item(self.empresas_table, row, 4, "Ativa" if empresa.status_ativo else "Inativa")

        self.empresas_table.resizeColumnsToContents()
        if empresas:
            self.empresas_table.selectRow(0)
        else:
            self.selected_empresa_id = None
            self.reload_obras()
            self._sync_buttons()

    def reload_obras(self) -> None:
        if not self.selected_empresa_id:
            self.obras_table.setRowCount(0)
            self.selected_obra_id = None
            self.empresa_detail_label.setText("Nenhuma empresa selecionada")
            self._sync_buttons()
            return

        try:
            empresa = self.service.get_empresa(self.selected_empresa_id)
            obras = self.service.list_obras(self.selected_empresa_id)
        except Exception as exc:
            self._show_error(f"Falha ao carregar obras: {exc}")
            return

        self.empresa_detail_label.setText(
            f"Empresa: {empresa.razao_social} | CNPJ: {empresa.cnpj} | Obras: {len(obras)}"
        )

        self.obras_table.setRowCount(len(obras))
        for row, obra in enumerate(obras):
            self._set_row_item(self.obras_table, row, 0, str(obra.id), obra.id)
            self._set_row_item(self.obras_table, row, 1, obra.codigo_interno)
            self._set_row_item(self.obras_table, row, 2, obra.nome)
            self._set_row_item(self.obras_table, row, 3, obra.cidade)
            self._set_row_item(self.obras_table, row, 4, obra.uf)
            self._set_row_item(self.obras_table, row, 5, str(obra.aliquota_iss))
            self._set_row_item(self.obras_table, row, 6, "Ativa" if obra.status_ativo else "Inativa")

        self.obras_table.resizeColumnsToContents()
        if obras:
            self.obras_table.selectRow(0)
        else:
            self.selected_obra_id = None
        self._sync_buttons()

    def _on_empresa_selected(self) -> None:
        row = self.empresas_table.currentRow()
        if row < 0:
            self.selected_empresa_id = None
            self.reload_obras()
            return
        item = self.empresas_table.item(row, 0)
        self.selected_empresa_id = int(item.data(Qt.ItemDataRole.UserRole)) if item else None
        self.reload_obras()

    def _on_obra_selected(self) -> None:
        row = self.obras_table.currentRow()
        if row < 0:
            self.selected_obra_id = None
            self._sync_buttons()
            return
        item = self.obras_table.item(row, 0)
        self.selected_obra_id = int(item.data(Qt.ItemDataRole.UserRole)) if item else None
        self._sync_buttons()

    def _new_empresa(self) -> None:
        dialog = EmpresaDialog(self)
        if not dialog.exec():
            return
        payload = dialog.payload()
        try:
            self.service.create_empresa(EmpresaInput(**payload))
            self.reload_empresas()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _edit_empresa(self) -> None:
        if not self.selected_empresa_id:
            return
        try:
            entity = self.service.get_empresa(self.selected_empresa_id)
        except BusinessRuleError as exc:
            self._show_error(str(exc))
            return

        dialog = EmpresaDialog(self, initial=entity)
        if not dialog.exec():
            return
        payload = dialog.payload()
        try:
            self.service.update_empresa(self.selected_empresa_id, EmpresaInput(**payload))
            self.reload_empresas()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _delete_empresa(self) -> None:
        if not self.selected_empresa_id:
            return
        confirmed = QMessageBox.question(
            self,
            "Confirmar exclusao",
            "Deseja excluir esta empresa? Esta acao so e permitida sem vinculos fiscais.",
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.delete_empresa(self.selected_empresa_id)
            self.reload_empresas()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _toggle_empresa(self) -> None:
        if not self.selected_empresa_id:
            return
        row = self.empresas_table.currentRow()
        is_ativa = self.empresas_table.item(row, 4).text() == "Ativa"
        try:
            self.service.set_empresa_status(self.selected_empresa_id, not is_ativa)
            self.reload_empresas()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _new_obra(self) -> None:
        if not self.selected_empresa_id:
            self._show_error("Selecione uma empresa para cadastrar obra")
            return
        perfis = self.service.list_perfis_tributarios()
        dialog = ObraDialog(perfis, self)
        if not dialog.exec():
            return

        payload = dialog.payload()
        payload["empresa_id"] = self.selected_empresa_id
        try:
            self.service.create_obra(ObraInput(**payload))
            self.reload_obras()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _edit_obra(self) -> None:
        if not self.selected_obra_id or not self.selected_empresa_id:
            return
        try:
            obras = self.service.list_obras(self.selected_empresa_id)
            entity = next((x for x in obras if x.id == self.selected_obra_id), None)
            if entity is None:
                raise BusinessRuleError("Obra selecionada nao encontrada")
        except BusinessRuleError as exc:
            self._show_error(str(exc))
            return

        perfis = self.service.list_perfis_tributarios()
        dialog = ObraDialog(perfis, self, initial=entity)
        if not dialog.exec():
            return

        payload = dialog.payload()
        payload["empresa_id"] = self.selected_empresa_id
        try:
            self.service.update_obra(self.selected_obra_id, ObraInput(**payload))
            self.reload_obras()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _delete_obra(self) -> None:
        if not self.selected_obra_id:
            return
        confirmed = QMessageBox.question(
            self,
            "Confirmar exclusao",
            "Deseja excluir esta obra? Esta acao so e permitida sem vinculos fiscais.",
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.delete_obra(self.selected_obra_id)
            self.reload_obras()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _toggle_obra(self) -> None:
        if not self.selected_obra_id:
            return
        row = self.obras_table.currentRow()
        is_ativa = self.obras_table.item(row, 6).text() == "Ativa"
        try:
            self.service.set_obra_status(self.selected_obra_id, not is_ativa)
            self.reload_obras()
        except BusinessRuleError as exc:
            self._show_error(str(exc))

    def _sync_buttons(self) -> None:
        has_empresa = self.selected_empresa_id is not None
        has_obra = self.selected_obra_id is not None

        self.btn_edit_empresa.setEnabled(has_empresa)
        self.btn_delete_empresa.setEnabled(has_empresa)
        self.btn_toggle_empresa.setEnabled(has_empresa)
        self.btn_new_obra.setEnabled(has_empresa)

        self.btn_edit_obra.setEnabled(has_obra)
        self.btn_delete_obra.setEnabled(has_obra)
        self.btn_toggle_obra.setEnabled(has_obra)

        if has_empresa and self.empresas_table.currentRow() >= 0:
            status_text = self.empresas_table.item(self.empresas_table.currentRow(), 4).text()
            self.btn_toggle_empresa.setText("Inativar" if status_text == "Ativa" else "Reativar")
        else:
            self.btn_toggle_empresa.setText("Inativar")

        if has_obra and self.obras_table.currentRow() >= 0:
            status_text = self.obras_table.item(self.obras_table.currentRow(), 6).text()
            self.btn_toggle_obra.setText("Inativar" if status_text == "Ativa" else "Reativar")
        else:
            self.btn_toggle_obra.setText("Inativar")

    @staticmethod
    def _set_row_item(table: QTableWidget, row: int, col: int, text: str, user_data: object | None = None) -> None:
        item = QTableWidgetItem(text)
        if user_data is not None:
            item.setData(Qt.ItemDataRole.UserRole, user_data)
        table.setItem(row, col, item)

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Erro", message)

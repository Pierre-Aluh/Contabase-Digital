"""Pagina de lancamentos fiscais por competencia."""

from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)

from app.services import (
    AjusteFiscalInput,
    BusinessRuleError,
    LANCAMENTO_DETALHE_FIELDS,
    LancamentoFiscalInput,
    LancamentoFiscalService,
)
from app.ui.dialogs import AjusteFiscalDialog
from app.ui.pages.base_page import BasePage
from app.utils.formatters import format_brl


class LancamentosPage(BasePage):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Lancamentos Fiscais",
            description="Registro por obra e competencia com suporte a ajustes de base por tributo.",
            parent=parent,
        )
        self.service = LancamentoFiscalService()
        self.current_lancamento_id: int | None = None
        self.current_ajustes: list[dict] = []
        self.receita_detail_edits: dict[str, QLineEdit] = {}
        self._profile_presuncao_by_id: dict[int, tuple[Decimal, Decimal]] = {}
        self._is_loading_selection = False
        self._is_refreshing_table = False

        self._build_ui()
        self._load_filters()
        self._refresh_lancamentos()

    def _build_ui(self) -> None:
        page_layout = self.layout()
        host = QWidget()
        root = QVBoxLayout(host)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        filter_row = QHBoxLayout()
        self.empresa_combo = QComboBox()
        self.empresa_combo.currentIndexChanged.connect(self._on_empresa_changed)
        filter_row.addWidget(self.empresa_combo)

        self.obra_combo = QComboBox()
        self.obra_combo.currentIndexChanged.connect(self._on_obra_changed)
        filter_row.addWidget(self.obra_combo)

        self.competencia_combo = QComboBox()
        self.competencia_combo.currentIndexChanged.connect(self._refresh_lancamentos)
        filter_row.addWidget(self.competencia_combo)

        btn_refresh = QPushButton("Atualizar")
        btn_refresh.clicked.connect(self._refresh_lancamentos)
        filter_row.addWidget(btn_refresh)
        root.addLayout(filter_row)

        actions_row = QHBoxLayout()
        btn_new = QPushButton("Novo lancamento")
        btn_new.clicked.connect(self._on_click_new_lancamento)
        actions_row.addWidget(btn_new)

        btn_duplicate = QPushButton("Duplicar mes anterior")
        btn_duplicate.clicked.connect(self._duplicate_previous)
        actions_row.addWidget(btn_duplicate)

        btn_delete = QPushButton("Excluir")
        btn_delete.clicked.connect(self._delete_lancamento)
        actions_row.addWidget(btn_delete)
        actions_row.addStretch(1)
        root.addLayout(actions_row)

        content_splitter = QSplitter(Qt.Orientation.Vertical)
        content_splitter.setChildrenCollapsible(False)

        table_group = QGroupBox("Lista de lancamentos")
        table_layout = QVBoxLayout(table_group)
        self.lancamentos_table = QTableWidget(0, 12)
        self.lancamentos_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Empresa",
                "Obra",
                "Competencia",
                "Receita Bruta",
                "Base PIS/COFINS",
                "PIS",
                "COFINS",
                "CSLL",
                "IRPJ",
                "IRPJ Adicional",
                "Ult. Alteracao",
            ]
        )
        self.lancamentos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.lancamentos_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.lancamentos_table.verticalHeader().setVisible(False)
        self.lancamentos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.lancamentos_table.itemSelectionChanged.connect(self._on_select_lancamento)
        self.lancamentos_table.setAlternatingRowColors(True)
        lanc_header = self.lancamentos_table.horizontalHeader()
        lanc_header.setStretchLastSection(False)
        lanc_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        lanc_header.setSectionResizeMode(2, QHeaderView.Stretch)
        table_layout.addWidget(self.lancamentos_table)
        content_splitter.addWidget(table_group)

        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        details_host = QWidget()
        details_scroll.setWidget(details_host)
        details_layout = QVBoxLayout(details_host)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(12)

        form_group = QGroupBox("Cadastro/Edição")
        form_layout = QGridLayout(form_group)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(10)

        self.receita_bruta_edit = QLineEdit("0,00")
        self.receita_bruta_edit.textChanged.connect(self._refresh_summary)
        form_layout.addWidget(QLabel("Receita bruta*"), 0, 0)
        form_layout.addWidget(self.receita_bruta_edit, 0, 1)

        self.presuncao_combo = QComboBox()
        self.presuncao_combo.currentIndexChanged.connect(self._refresh_summary)
        form_layout.addWidget(QLabel("Presuncao"), 0, 2)
        form_layout.addWidget(self.presuncao_combo, 0, 3)

        field_rows_per_column = (len(LANCAMENTO_DETALHE_FIELDS) + 1) // 2
        for index, (field_name, field_label) in enumerate(LANCAMENTO_DETALHE_FIELDS):
            row = (index % field_rows_per_column) + 1
            column_offset = 0 if index < field_rows_per_column else 2
            edit = QLineEdit("0,00")
            edit.textChanged.connect(self._refresh_summary)
            self.receita_detail_edits[field_name] = edit
            form_layout.addWidget(QLabel(field_label), row, column_offset)
            form_layout.addWidget(edit, row, column_offset + 1)

        info_row = field_rows_per_column + 2
        self.base_info_label = QLabel("Base PIS/COFINS calculada automaticamente a partir da receita bruta e das receitas detalhadas.")
        self.base_info_label.setObjectName("mutedLabel")
        form_layout.addWidget(self.base_info_label, info_row, 0, 1, 4)

        self.memoria_calculo_label = QLabel(
            "Memoria de calculo: receita bruta x presuncao IRPJ/CSLL, com detalhamento das bases presumidas."
        )
        self.memoria_calculo_label.setObjectName("mutedLabel")
        self.memoria_calculo_label.setWordWrap(True)
        form_layout.addWidget(self.memoria_calculo_label, info_row + 1, 0, 1, 4)

        doc_row = info_row + 2
        self.documento_edit = QLineEdit()
        self.documento_edit.setPlaceholderText("Caminho local opcional")
        form_layout.addWidget(QLabel("Documento"), doc_row, 0)
        form_layout.addWidget(self.documento_edit, doc_row, 1, 1, 3)

        obs_row = doc_row + 1
        self.observacoes_edit = QTextEdit()
        self.observacoes_edit.setFixedHeight(110)
        form_layout.addWidget(QLabel("Observacoes"), obs_row, 0)
        form_layout.addWidget(self.observacoes_edit, obs_row, 1, 1, 3)

        save_row = obs_row + 1
        save_actions = QHBoxLayout()
        save_actions.addStretch(1)
        btn_save = QPushButton("Salvar lancamento")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self._save_lancamento)
        save_actions.addWidget(btn_save)
        form_layout.addLayout(save_actions, save_row, 0, 1, 4)
        details_layout.addWidget(form_group)

        ajustes_group = QGroupBox("Ajustes fiscais individuais")
        ajustes_layout = QVBoxLayout(ajustes_group)
        ajuste_actions = QHBoxLayout()
        btn_add_ajuste = QPushButton("Adicionar ajuste")
        btn_add_ajuste.clicked.connect(self._add_ajuste)
        ajuste_actions.addWidget(btn_add_ajuste)

        btn_edit_ajuste = QPushButton("Editar ajuste")
        btn_edit_ajuste.clicked.connect(self._edit_ajuste)
        ajuste_actions.addWidget(btn_edit_ajuste)

        btn_remove_ajuste = QPushButton("Remover ajuste")
        btn_remove_ajuste.clicked.connect(self._remove_ajuste)
        ajuste_actions.addWidget(btn_remove_ajuste)
        ajuste_actions.addStretch(1)
        ajustes_layout.addLayout(ajuste_actions)

        self.ajustes_table = QTableWidget(0, 6)
        self.ajustes_table.setHorizontalHeaderLabels(
            ["Tributo", "Tipo", "Valor", "Descricao", "Justificativa", "Documento"]
        )
        self.ajustes_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ajustes_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.ajustes_table.verticalHeader().setVisible(False)
        self.ajustes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ajustes_table.setAlternatingRowColors(True)
        ajuste_header = self.ajustes_table.horizontalHeader()
        ajuste_header.setStretchLastSection(False)
        ajuste_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        ajuste_header.setSectionResizeMode(3, QHeaderView.Stretch)
        ajuste_header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.ajustes_table.setMinimumHeight(160)
        ajustes_layout.addWidget(self.ajustes_table)
        details_layout.addWidget(ajustes_group)

        resumo_group = QGroupBox("Resumo de base: original x adicoes/reducoes x final")
        resumo_layout = QGridLayout(resumo_group)
        self.resumo_labels: dict[str, QLabel] = {}
        headers = ["Tributo", "Base Original", "Adicoes", "Reducoes", "Base Final", "Imposto Devido"]
        for col, text in enumerate(headers):
            header = QLabel(text)
            header.setObjectName("SectionTitle")
            resumo_layout.addWidget(header, 0, col)

        for row, tributo in enumerate(["PIS", "COFINS", "CSLL", "IRPJ", "IRPJ_ADICIONAL"], start=1):
            resumo_layout.addWidget(QLabel(tributo), row, 0)
            for col, key in enumerate(["base_original", "adicoes", "reducoes", "base_final", "imposto_devido"], start=1):
                label = QLabel("R$ 0,00")
                self.resumo_labels[f"{tributo}:{key}"] = label
                resumo_layout.addWidget(label, row, col)
        details_layout.addWidget(resumo_group)
        details_layout.addStretch(1)

        content_splitter.addWidget(details_scroll)
        content_splitter.setStretchFactor(0, 2)
        content_splitter.setStretchFactor(1, 3)
        content_splitter.setSizes([260, 560])
        root.addWidget(content_splitter, 1)

        page_layout.insertWidget(page_layout.count() - 1, host)

    def _load_filters(self) -> None:
        self.empresa_combo.clear()
        self.empresa_combo.addItem("Empresa: todas", None)
        for empresa in self.service.list_empresas():
            self.empresa_combo.addItem(f"{empresa.razao_social} ({empresa.cnpj})", empresa.id)

        self.competencia_combo.clear()
        self.competencia_combo.addItem("Competencia: todas", None)
        for competencia in self.service.list_competencias():
            self.competencia_combo.addItem(competencia.referencia, competencia.id)

        self._reload_obras_combo(None)
        self._load_presuncao_options()
        self._new_lancamento(clear_filters=False)

    def _reload_obras_combo(self, empresa_id: int | None) -> None:
        self.obra_combo.blockSignals(True)
        self.obra_combo.clear()
        self.obra_combo.addItem("Obra: todas", None)
        for obra in self.service.list_obras(empresa_id=empresa_id):
            self.obra_combo.addItem(f"{obra.codigo_interno} - {obra.nome}", obra.id)
        self.obra_combo.blockSignals(False)

    def _on_empresa_changed(self) -> None:
        if self._is_loading_selection:
            return
        empresa_id = self._current_data_int(self.empresa_combo)
        self._reload_obras_combo(empresa_id)
        self._sync_presuncao_from_selected_obra()
        self._refresh_lancamentos()

    def _on_obra_changed(self) -> None:
        if self._is_loading_selection:
            return
        self._sync_presuncao_from_selected_obra()
        self._refresh_lancamentos()

    def _load_presuncao_options(self) -> None:
        self._profile_presuncao_by_id.clear()
        self.presuncao_combo.blockSignals(True)
        try:
            self.presuncao_combo.clear()
            self.presuncao_combo.addItem("Automatica (perfil da obra)", None)
            for perfil in self.service.list_perfis_tributarios():
                percentual_irpj, percentual_csll = self.service.get_presuncao_for_perfil(perfil.id)
                self._profile_presuncao_by_id[perfil.id] = (percentual_irpj, percentual_csll)
                self.presuncao_combo.addItem(
                    f"{perfil.nome} (IRPJ {percentual_irpj * Decimal('100'):.2f}% | CSLL {percentual_csll * Decimal('100'):.2f}%)",
                    perfil.id,
                )
            self.presuncao_combo.setCurrentIndex(0)
        finally:
            self.presuncao_combo.blockSignals(False)

    def _sync_presuncao_from_selected_obra(self) -> None:
        # Keep automatic mode selected by default when changing obra.
        self.presuncao_combo.blockSignals(True)
        try:
            self.presuncao_combo.setCurrentIndex(0)
        finally:
            self.presuncao_combo.blockSignals(False)
        self._refresh_summary()

    def _refresh_lancamentos(self) -> None:
        if self._is_loading_selection or self._is_refreshing_table:
            return
        empresa_id = self._current_data_int(self.empresa_combo)
        obra_id = self._current_data_int(self.obra_combo)
        competencia_id = self._current_data_int(self.competencia_combo)
        lancamentos = self.service.list_lancamentos(
            empresa_id=empresa_id,
            obra_id=obra_id,
            competencia_id=competencia_id,
        )

        self._is_refreshing_table = True
        try:
            self.lancamentos_table.blockSignals(True)
            self.lancamentos_table.setRowCount(len(lancamentos))
            for row, item in enumerate(lancamentos):
                resumo = self.service.calculate_adjustment_summary(
                    receita_bruta=item.receita_bruta,
                    receita_tributavel_pis_cofins=item.receita_tributavel_pis_cofins,
                    ajustes=[
                        AjusteFiscalInput(
                            tributo_alvo=str(ajuste.tributo_alvo.value),
                            tipo_ajuste=str(ajuste.tipo_ajuste.value),
                            valor=ajuste.valor,
                            descricao=str(ajuste.descricao),
                            justificativa=str(ajuste.justificativa),
                            documento_referencia=str(ajuste.documento_referencia or ""),
                            observacao=str(ajuste.observacao or ""),
                        )
                        for ajuste in (item.ajustes or [])
                    ],
                    obra_id=item.obra_id,
                )
                updated_at = item.updated_at.strftime("%d/%m/%Y %H:%M") if item.updated_at else "-"

                self._set_item(self.lancamentos_table, row, 0, str(item.id), item.id)
                self._set_item(self.lancamentos_table, row, 1, str(item.empresa.razao_social))
                self._set_item(self.lancamentos_table, row, 2, str(item.obra.nome))
                self._set_item(self.lancamentos_table, row, 3, str(item.competencia.referencia))
                self._set_item(self.lancamentos_table, row, 4, format_brl(item.receita_bruta))
                self._set_item(self.lancamentos_table, row, 5, format_brl(item.receita_tributavel_pis_cofins))
                self._set_item(self.lancamentos_table, row, 6, format_brl(resumo["PIS"]["imposto_devido"]))
                self._set_item(self.lancamentos_table, row, 7, format_brl(resumo["COFINS"]["imposto_devido"]))
                self._set_item(self.lancamentos_table, row, 8, format_brl(resumo["CSLL"]["imposto_devido"]))
                self._set_item(self.lancamentos_table, row, 9, format_brl(resumo["IRPJ"]["imposto_devido"]))
                self._set_item(self.lancamentos_table, row, 10, format_brl(resumo["IRPJ_ADICIONAL"]["imposto_devido"]))
                self._set_item(self.lancamentos_table, row, 11, updated_at)

            self.lancamentos_table.resizeColumnsToContents()
            if lancamentos and self.current_lancamento_id is not None:
                self._select_lancamento_by_id(self.current_lancamento_id)
            elif lancamentos:
                self.lancamentos_table.selectRow(0)
            else:
                self._new_lancamento(clear_filters=False)
        finally:
            self.lancamentos_table.blockSignals(False)
            self._is_refreshing_table = False

        if self.lancamentos_table.currentRow() >= 0:
            self._on_select_lancamento()

    def _on_select_lancamento(self) -> None:
        if self._is_refreshing_table:
            return
        selected_rows = self.lancamentos_table.selectionModel().selectedRows()
        if not selected_rows:
            self.current_lancamento_id = None
            return

        row = selected_rows[0].row()
        item = self.lancamentos_table.item(row, 0)
        if not item:
            return

        lancamento_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(lancamento_id, int):
            return

        self.current_lancamento_id = lancamento_id
        lancamento, ajustes = self.service.get_lancamento_with_ajustes(lancamento_id)

        self._is_loading_selection = True
        try:
            self.receita_bruta_edit.setText(str(lancamento.receita_bruta))
            for field_name, _ in LANCAMENTO_DETALHE_FIELDS:
                self.receita_detail_edits[field_name].setText(str(getattr(lancamento, field_name)))
            self.documento_edit.setText(str(lancamento.documento_referencia or ""))
            self.observacoes_edit.setPlainText(str(lancamento.observacoes or ""))

            self.current_ajustes = [
                {
                    "tributo_alvo": ajuste.tributo_alvo.value,
                    "tipo_ajuste": ajuste.tipo_ajuste.value,
                    "valor": str(ajuste.valor),
                    "descricao": ajuste.descricao,
                    "justificativa": ajuste.justificativa,
                    "documento_referencia": ajuste.documento_referencia or "",
                    "observacao": ajuste.observacao or "",
                }
                for ajuste in ajustes
            ]
            self._render_ajustes()
            self._refresh_summary()
        finally:
            self._is_loading_selection = False

    def _new_lancamento(self, clear_filters: bool = True) -> None:
        self.current_lancamento_id = None
        self.current_ajustes = []
        self.receita_bruta_edit.setText("0,00")
        for edit in self.receita_detail_edits.values():
            edit.setText("0,00")
        self.documento_edit.clear()
        self.observacoes_edit.clear()
        self.presuncao_combo.setCurrentIndex(0)
        if clear_filters:
            self.lancamentos_table.blockSignals(True)
            self.lancamentos_table.clearSelection()
            self.lancamentos_table.setCurrentItem(None)
            self.lancamentos_table.blockSignals(False)
        self._render_ajustes()
        self._refresh_summary()

    def _on_click_new_lancamento(self) -> None:
        self._new_lancamento(clear_filters=True)

    def _save_lancamento(self) -> None:
        try:
            payload = self._build_payload()
            ajustes = [AjusteFiscalInput(**item) for item in self.current_ajustes]
            saved = self.service.save_lancamento(payload, ajustes, self.current_lancamento_id)
            self.current_lancamento_id = saved.id
            self._refresh_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lancamento salvo com sucesso")
        except BusinessRuleError as exc:
            QMessageBox.critical(self, "Regra de negocio", str(exc))
        except ValueError as exc:
            QMessageBox.critical(self, "Valor invalido", str(exc))

    def _delete_lancamento(self) -> None:
        if not self.current_lancamento_id:
            QMessageBox.warning(self, "Atencao", "Selecione um lancamento para excluir")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmar exclusao",
            "Deseja excluir o lancamento selecionado e todos os seus ajustes?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.delete_lancamento(self.current_lancamento_id)
            self._new_lancamento()
            self._refresh_lancamentos()
        except BusinessRuleError as exc:
            QMessageBox.critical(self, "Regra de negocio", str(exc))

    def _duplicate_previous(self) -> None:
        empresa_id = self._current_data_int(self.empresa_combo)
        obra_id = self._current_data_int(self.obra_combo)
        competencia_id = self._current_data_int(self.competencia_combo)
        if not empresa_id or not obra_id or not competencia_id:
            QMessageBox.warning(
                self,
                "Campos obrigatorios",
                "Selecione empresa, obra e competencia para duplicar o mes anterior.",
            )
            return

        try:
            novo = self.service.duplicate_from_previous_month(empresa_id, obra_id, competencia_id)
            self.current_lancamento_id = novo.id
            self._refresh_lancamentos()
            QMessageBox.information(self, "Sucesso", "Lancamento duplicado do mes anterior")
        except BusinessRuleError as exc:
            QMessageBox.critical(self, "Regra de negocio", str(exc))

    def _add_ajuste(self) -> None:
        dialog = AjusteFiscalDialog(self)
        if not dialog.exec():
            return
        self.current_ajustes.append(dialog.payload())
        self._render_ajustes()
        self._refresh_summary()

    def _edit_ajuste(self) -> None:
        row = self.ajustes_table.currentRow()
        if row < 0 or row >= len(self.current_ajustes):
            QMessageBox.warning(self, "Atencao", "Selecione um ajuste para editar")
            return

        dialog = AjusteFiscalDialog(self, initial=self.current_ajustes[row])
        if not dialog.exec():
            return

        self.current_ajustes[row] = dialog.payload()
        self._render_ajustes()
        self._refresh_summary()

    def _remove_ajuste(self) -> None:
        row = self.ajustes_table.currentRow()
        if row < 0 or row >= len(self.current_ajustes):
            QMessageBox.warning(self, "Atencao", "Selecione um ajuste para remover")
            return
        self.current_ajustes.pop(row)
        self._render_ajustes()
        self._refresh_summary()

    def _render_ajustes(self) -> None:
        self.ajustes_table.setRowCount(len(self.current_ajustes))
        for row, ajuste in enumerate(self.current_ajustes):
            self._set_item(self.ajustes_table, row, 0, str(ajuste["tributo_alvo"]))
            self._set_item(self.ajustes_table, row, 1, str(ajuste["tipo_ajuste"]))
            self._set_item(self.ajustes_table, row, 2, str(ajuste["valor"]))
            self._set_item(self.ajustes_table, row, 3, str(ajuste["descricao"]))
            self._set_item(self.ajustes_table, row, 4, str(ajuste["justificativa"]))
            self._set_item(self.ajustes_table, row, 5, str(ajuste["documento_referencia"]))
        self.ajustes_table.resizeColumnsToContents()

    def _refresh_summary(self) -> None:
        try:
            payload = self._build_payload(allow_missing_filters=True)
            aggregates = self.service.calculate_aggregate_values(payload)
            resumo = self.service.calculate_adjustment_summary(
                aggregates["receita_bruta"],
                aggregates["receita_tributavel_pis_cofins"],
                [AjusteFiscalInput(**item) for item in self.current_ajustes],
                obra_id=payload.obra_id,
                perfil_tributario_id=self._selected_presuncao_perfil_id(),
            )
            memoria = self.service.build_presuncao_memoria(
                receita_bruta=aggregates["receita_bruta"],
                receita_tributavel_pis_cofins=aggregates["receita_tributavel_pis_cofins"],
                obra_id=payload.obra_id,
                perfil_tributario_id=self._selected_presuncao_perfil_id(),
            )
            adicional = resumo["IRPJ_ADICIONAL"]
            percentual_irpj_label = (memoria["percentual_irpj"] * Decimal("100")).quantize(Decimal("0.01"))
            percentual_csll_label = (memoria["percentual_csll"] * Decimal("100")).quantize(Decimal("0.01"))
            self.base_info_label.setText(
                "Base PIS/COFINS calculada automaticamente: "
                f"{format_brl(memoria['receita_tributavel_pis_cofins'])}. "
                f"Presuncao aplicada: IRPJ {percentual_irpj_label}% e CSLL {percentual_csll_label}% sobre a receita bruta."
            )
            self.memoria_calculo_label.setText(
                "Memoria de calculo: "
                f"Receita bruta {format_brl(memoria['receita_bruta'])} x IRPJ {percentual_irpj_label}% = {format_brl(memoria['base_presumida_irpj'])}; "
                f"Receita bruta {format_brl(memoria['receita_bruta'])} x CSLL {percentual_csll_label}% = {format_brl(memoria['base_presumida_csll'])}. "
                f"IRPJ adicional: base excedente {format_brl(adicional['base_final'])}, imposto devido {format_brl(adicional['imposto_devido'])}."
            )
        except Exception:
            return

        for tributo, values in resumo.items():
            self.resumo_labels[f"{tributo}:base_original"].setText(format_brl(values["base_original"]))
            self.resumo_labels[f"{tributo}:adicoes"].setText(format_brl(values["adicoes"]))
            self.resumo_labels[f"{tributo}:reducoes"].setText(format_brl(values["reducoes"]))
            self.resumo_labels[f"{tributo}:base_final"].setText(format_brl(values["base_final"]))
            self.resumo_labels[f"{tributo}:imposto_devido"].setText(format_brl(values["imposto_devido"]))

    def _build_payload(self, allow_missing_filters: bool = False) -> LancamentoFiscalInput:
        empresa_id = self._current_data_int(self.empresa_combo)
        obra_id = self._current_data_int(self.obra_combo)
        competencia_id = self._current_data_int(self.competencia_combo)
        if not allow_missing_filters and (not empresa_id or not obra_id or not competencia_id):
            raise BusinessRuleError("Empresa, obra e competencia sao obrigatorias")

        payload_data: dict[str, object] = {
            "empresa_id": empresa_id or 0,
            "obra_id": obra_id or 0,
            "competencia_id": competencia_id or 0,
            "receita_bruta": self.receita_bruta_edit.text().strip() or "0",
            "observacoes": self.observacoes_edit.toPlainText().strip(),
            "documento_referencia": self.documento_edit.text().strip(),
        }
        for field_name in self.receita_detail_edits:
            payload_data[field_name] = self.receita_detail_edits[field_name].text().strip() or "0"
        return LancamentoFiscalInput(**payload_data)

    def _select_lancamento_by_id(self, lancamento_id: int) -> None:
        for row in range(self.lancamentos_table.rowCount()):
            item = self.lancamentos_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == lancamento_id:
                self.lancamentos_table.selectRow(row)
                return

    @staticmethod
    def _set_item(
        table: QTableWidget,
        row: int,
        col: int,
        text: str,
        user_data: object | None = None,
    ) -> None:
        item = QTableWidgetItem(text)
        if user_data is not None:
            item.setData(Qt.ItemDataRole.UserRole, user_data)
        table.setItem(row, col, item)

    @staticmethod
    def _current_data_int(combo: QComboBox) -> int | None:
        value = combo.currentData()
        return int(value) if isinstance(value, int) else None

    def _selected_presuncao_perfil_id(self) -> int | None:
        value = self.presuncao_combo.currentData()
        return int(value) if isinstance(value, int) else None

    @staticmethod
    def _set_combo_value(combo: QComboBox, value: int) -> None:
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
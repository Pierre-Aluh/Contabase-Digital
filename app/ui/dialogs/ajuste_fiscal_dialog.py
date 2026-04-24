"""Dialogo para cadastro/edicao de ajuste fiscal."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.models.enums import TipoAjuste, TributoAlvo


class AjusteFiscalDialog(QDialog):
    def __init__(self, parent=None, initial: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ajuste fiscal")
        self.setMinimumWidth(520)

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.tributo_combo = QComboBox()
        for tributo in [
            TributoAlvo.PIS,
            TributoAlvo.COFINS,
            TributoAlvo.CSLL,
            TributoAlvo.IRPJ,
            TributoAlvo.IRPJ_ADICIONAL,
        ]:
            self.tributo_combo.addItem(tributo.value, tributo.value)
        form.addRow("Tributo*", self.tributo_combo)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("ADICAO", TipoAjuste.ADICAO.value)
        self.tipo_combo.addItem("REDUCAO", TipoAjuste.REDUCAO.value)
        form.addRow("Tipo*", self.tipo_combo)

        self.valor_edit = QLineEdit()
        self.valor_edit.setPlaceholderText("Ex.: 1500,00")
        form.addRow("Valor*", self.valor_edit)

        self.descricao_edit = QLineEdit()
        form.addRow("Descricao*", self.descricao_edit)

        self.justificativa_edit = QTextEdit()
        self.justificativa_edit.setFixedHeight(90)
        form.addRow("Justificativa*", self.justificativa_edit)

        self.documento_edit = QLineEdit()
        self.documento_edit.setPlaceholderText("Caminho local opcional")
        form.addRow("Documento", self.documento_edit)

        self.observacao_edit = QLineEdit()
        form.addRow("Observacao", self.observacao_edit)

        root.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch(1)

        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        actions.addWidget(cancel)

        save = QPushButton("Salvar")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.accept)
        actions.addWidget(save)

        root.addLayout(actions)

        if initial:
            self.set_initial(initial)

    def set_initial(self, initial: dict) -> None:
        trib_idx = self.tributo_combo.findData(initial.get("tributo_alvo"))
        if trib_idx >= 0:
            self.tributo_combo.setCurrentIndex(trib_idx)

        tipo_idx = self.tipo_combo.findData(initial.get("tipo_ajuste"))
        if tipo_idx >= 0:
            self.tipo_combo.setCurrentIndex(tipo_idx)

        self.valor_edit.setText(str(initial.get("valor", "") or ""))
        self.descricao_edit.setText(str(initial.get("descricao", "") or ""))
        self.justificativa_edit.setPlainText(str(initial.get("justificativa", "") or ""))
        self.documento_edit.setText(str(initial.get("documento_referencia", "") or ""))
        self.observacao_edit.setText(str(initial.get("observacao", "") or ""))

    def payload(self) -> dict:
        return {
            "tributo_alvo": str(self.tributo_combo.currentData()),
            "tipo_ajuste": str(self.tipo_combo.currentData()),
            "valor": self.valor_edit.text().strip(),
            "descricao": self.descricao_edit.text().strip(),
            "justificativa": self.justificativa_edit.toPlainText().strip(),
            "documento_referencia": self.documento_edit.text().strip(),
            "observacao": self.observacao_edit.text().strip(),
        }

"""Dialogo de cadastro/edicao de empresa."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class EmpresaDialog(QDialog):
    def __init__(self, parent=None, initial: object | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Empresa")
        self.setMinimumWidth(520)

        root = QVBoxLayout(self)

        hint = QLabel("Preencha os dados obrigatorios da empresa.")
        hint.setObjectName("mutedLabel")
        root.addWidget(hint)

        form = QFormLayout()
        form.setLabelAlignment(form.labelAlignment())

        self.cnpj_edit = QLineEdit()
        self.cnpj_edit.setPlaceholderText("Somente numeros ou formatado")
        form.addRow("CNPJ*", self.cnpj_edit)

        self.razao_social_edit = QLineEdit()
        form.addRow("Razao social*", self.razao_social_edit)

        self.nome_fantasia_edit = QLineEdit()
        form.addRow("Nome fantasia", self.nome_fantasia_edit)

        self.email_edit = QLineEdit()
        form.addRow("Email", self.email_edit)

        self.telefone_edit = QLineEdit()
        form.addRow("Telefone", self.telefone_edit)

        self.status_ativo = QCheckBox("Empresa ativa")
        self.status_ativo.setChecked(True)
        form.addRow("Status", self.status_ativo)

        root.addLayout(form)

        actions = QHBoxLayout()
        actions.addStretch(1)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.accept)
        actions.addWidget(btn_save)

        root.addLayout(actions)

        if initial is not None:
            self.set_initial(initial)

    def set_initial(self, initial: object) -> None:
        self.cnpj_edit.setText(str(getattr(initial, "cnpj", "") or ""))
        self.razao_social_edit.setText(str(getattr(initial, "razao_social", "") or ""))
        self.nome_fantasia_edit.setText(str(getattr(initial, "nome_fantasia", "") or ""))
        self.email_edit.setText(str(getattr(initial, "email", "") or ""))
        self.telefone_edit.setText(str(getattr(initial, "telefone", "") or ""))
        self.status_ativo.setChecked(bool(getattr(initial, "status_ativo", True)))

    def payload(self) -> dict:
        return {
            "cnpj": self.cnpj_edit.text().strip(),
            "razao_social": self.razao_social_edit.text().strip(),
            "nome_fantasia": self.nome_fantasia_edit.text().strip(),
            "email": self.email_edit.text().strip(),
            "telefone": self.telefone_edit.text().strip(),
            "status_ativo": self.status_ativo.isChecked(),
        }

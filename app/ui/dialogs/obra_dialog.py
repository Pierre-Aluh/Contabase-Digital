"""Dialogo de cadastro/edicao de obra."""

from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ObraDialog(QDialog):
    def __init__(self, perfis: list[object], parent=None, initial: object | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Obra")
        self.setMinimumWidth(640)

        root = QVBoxLayout(self)

        hint = QLabel("Informe os dados operacionais e tributarios da obra.")
        hint.setObjectName("mutedLabel")
        root.addWidget(hint)

        form = QFormLayout()

        self.codigo_edit = QLineEdit()
        form.addRow("Codigo interno*", self.codigo_edit)

        self.nome_edit = QLineEdit()
        form.addRow("Nome*", self.nome_edit)

        self.descricao_edit = QLineEdit()
        form.addRow("Descricao", self.descricao_edit)

        self.cidade_edit = QLineEdit()
        form.addRow("Cidade*", self.cidade_edit)

        self.uf_edit = QLineEdit()
        self.uf_edit.setMaxLength(2)
        form.addRow("UF*", self.uf_edit)

        self.atividade_edit = QLineEdit()
        form.addRow("Atividade principal*", self.atividade_edit)

        self.perfil_combo = QComboBox()
        for perfil in perfis:
            self.perfil_combo.addItem(str(getattr(perfil, "nome", "Perfil")), int(getattr(perfil, "id")))
        form.addRow("Perfil tributario*", self.perfil_combo)

        self.iss_edit = QLineEdit()
        self.iss_edit.setPlaceholderText("Ex.: 0,05 (5%)")
        form.addRow("Aliquota ISS*", self.iss_edit)

        self.inicio_edit = QDateEdit()
        self.inicio_edit.setCalendarPopup(True)
        self.inicio_edit.setDate(QDate.currentDate())
        form.addRow("Data inicio", self.inicio_edit)

        self.fim_edit = QDateEdit()
        self.fim_edit.setCalendarPopup(True)
        self.fim_edit.setSpecialValueText("Sem data")
        self.fim_edit.setDate(QDate(2000, 1, 1))
        self.fim_edit.setMinimumDate(QDate(2000, 1, 1))
        form.addRow("Data fim", self.fim_edit)

        self.status_ativo = QCheckBox("Obra ativa")
        self.status_ativo.setChecked(True)
        form.addRow("Status", self.status_ativo)

        self.observacoes_edit = QTextEdit()
        self.observacoes_edit.setPlaceholderText("Observacoes internas")
        self.observacoes_edit.setFixedHeight(100)
        form.addRow("Observacoes", self.observacoes_edit)

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

        if initial is None:
            self.iss_edit.setText("0.05")
        else:
            self.set_initial(initial)

    def set_initial(self, initial: object) -> None:
        self.codigo_edit.setText(str(getattr(initial, "codigo_interno", "") or ""))
        self.nome_edit.setText(str(getattr(initial, "nome", "") or ""))
        self.descricao_edit.setText(str(getattr(initial, "descricao", "") or ""))
        self.cidade_edit.setText(str(getattr(initial, "cidade", "") or ""))
        self.uf_edit.setText(str(getattr(initial, "uf", "") or ""))
        self.atividade_edit.setText(str(getattr(initial, "atividade_principal", "") or ""))
        self.iss_edit.setText(str(getattr(initial, "aliquota_iss", "0.05") or "0.05"))

        perfil_id = int(getattr(initial, "perfil_tributario_id", 0) or 0)
        idx = self.perfil_combo.findData(perfil_id)
        if idx >= 0:
            self.perfil_combo.setCurrentIndex(idx)

        data_inicio = getattr(initial, "data_inicio", None)
        if data_inicio:
            self.inicio_edit.setDate(QDate(data_inicio.year, data_inicio.month, data_inicio.day))

        data_fim = getattr(initial, "data_fim", None)
        if data_fim:
            self.fim_edit.setDate(QDate(data_fim.year, data_fim.month, data_fim.day))

        self.status_ativo.setChecked(bool(getattr(initial, "status_ativo", True)))
        self.observacoes_edit.setPlainText(str(getattr(initial, "observacoes", "") or ""))

    def payload(self) -> dict:
        fim_date = self.fim_edit.date().toPython()
        fim_value = None if fim_date == date(2000, 1, 1) else fim_date

        return {
            "codigo_interno": self.codigo_edit.text().strip(),
            "nome": self.nome_edit.text().strip(),
            "descricao": self.descricao_edit.text().strip(),
            "cidade": self.cidade_edit.text().strip(),
            "uf": self.uf_edit.text().strip().upper(),
            "atividade_principal": self.atividade_edit.text().strip(),
            "perfil_tributario_id": int(self.perfil_combo.currentData()),
            "aliquota_iss": self.iss_edit.text().strip(),
            "data_inicio": self.inicio_edit.date().toPython(),
            "data_fim": fim_value,
            "status_ativo": self.status_ativo.isChecked(),
            "observacoes": self.observacoes_edit.toPlainText().strip(),
        }

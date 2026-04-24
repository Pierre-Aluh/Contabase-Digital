"""Sidebar principal com navegacao de modulos."""

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout


class SidebarWidget(QFrame):
    def __init__(self, on_navigate: Callable[[str], None], parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(182)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(7)

        brand = QLabel("CONTABASE")
        brand.setObjectName("SidebarBrand")
        layout.addWidget(brand)

        self._buttons: dict[str, QPushButton] = {}
        self._on_navigate = on_navigate

        items = [
            ("dashboard", "◈ Dashboard"),
            ("empresas", "◉ Empresas"),
            ("lancamentos", "◎ Lancamentos"),
            ("apuracoes", "◌ Apuracao"),
            ("relatorios", "◍ Relatorios"),
            ("guias", "◐ Guias"),
            ("configuracoes", "◒ Configuracoes"),
        ]

        for key, label in items:
            btn = QPushButton(label)
            btn.setObjectName("SidebarNavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _checked=False, page=key: self.select_page(page))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch(1)

        self.theme_button = QPushButton("◑ Tema Escuro")
        self.theme_button.setObjectName("SidebarToggle")
        self.theme_button.setCheckable(True)
        self.theme_button.setChecked(True)
        layout.addWidget(self.theme_button)

        self.exit_button = QPushButton("◓ Sair")
        self.exit_button.setObjectName("SidebarExit")
        layout.addWidget(self.exit_button)

    def select_page(self, page: str) -> None:
        for key, button in self._buttons.items():
            button.setChecked(key == page)
        self._on_navigate(page)

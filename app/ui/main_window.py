"""Janela principal com sidebar, topbar e area central navegavel."""

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class _DateErrorBar(QFrame):
    """Barra de aviso estilizada exibida abaixo da topbar em caso de erro de datas."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("DateErrorBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        self._label = QLabel()
        self._label.setObjectName("DateErrorLabel")
        layout.addWidget(self._label)
        self.setVisible(False)
        self.setFixedHeight(0)

    def show_error(self, msg: str) -> None:
        self._label.setText(f"⚠  {msg}")
        self.setFixedHeight(34)
        self.setVisible(True)

    def hide_error(self) -> None:
        self.setFixedHeight(0)
        self.setVisible(False)

from app.core.constants import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from app.ui.pages.apuracoes_page import ApuracoesPage
from app.ui.pages.configuracoes_page import ConfiguracoesPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.empresas_page import EmpresasPage
from app.ui.pages.guias_page import GuiasPage
from app.ui.pages.lancamentos_page import LancamentosPage
from app.ui.pages.relatorios_page import RelatoriosPage
from app.ui.widgets.sidebar import SidebarWidget
from app.ui.widgets.topbar import TopbarWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Contabase Digital")
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = SidebarWidget(self.navigate_to)
        root_layout.addWidget(self.sidebar)

        content_host = QWidget()
        content_layout = QVBoxLayout(content_host)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.topbar = TopbarWidget()
        content_layout.addWidget(self.topbar)

        self._error_bar = _DateErrorBar()
        content_layout.addWidget(self._error_bar)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        root_layout.addWidget(content_host, 1)

        self.pages: dict[str, int] = {}
        self.dashboard_page: DashboardPage | None = None
        self._register_pages()

        if self.dashboard_page is not None:
            self.topbar.filtersChanged.connect(self.dashboard_page.on_filters_changed)
        self.topbar.dateRangeError.connect(self._on_date_range_error)

        status = QStatusBar(self)
        status.showMessage("Aplicacao iniciada")
        self.setStatusBar(status)

        self.sidebar.select_page("dashboard")

    def _register_pages(self) -> None:
        self.dashboard_page = DashboardPage()
        page_map = {
            "dashboard": self.dashboard_page,
            "empresas": EmpresasPage(),
            "lancamentos": LancamentosPage(),
            "apuracoes": ApuracoesPage(),
            "relatorios": RelatoriosPage(),
            "guias": GuiasPage(),
            "configuracoes": ConfiguracoesPage(),
        }

        for key, page in page_map.items():
            index = self.stack.addWidget(page)
            self.pages[key] = index

    def navigate_to(self, page: str) -> None:
        index = self.pages.get(page)
        if index is None:
            return
        self.stack.setCurrentIndex(index)
        show_topbar = page != "relatorios"
        self.topbar.setVisible(show_topbar)
        if not show_topbar:
            self._error_bar.hide_error()
        else:
            self._error_bar.setVisible(self._error_bar.height() > 0)
        self.statusBar().showMessage(f"Modulo ativo: {page}")

    def _on_date_range_error(self, msg: str) -> None:
        if msg:
            self._error_bar.show_error(msg)
        else:
            self._error_bar.hide_error()

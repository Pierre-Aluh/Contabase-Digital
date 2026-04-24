"""Topbar com filtros funcionais para dashboard e demais modulos."""

from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QWidget,
)
from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.empresa import Empresa
from app.models.obra import Obra

_MONTHS = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
_QUARTERS = ["1º Trimestre", "2º Trimestre", "3º Trimestre", "4º Trimestre"]
_CURRENT_YEAR = date.today().year


class TopbarWidget(QFrame):
    filtersChanged = Signal()
    dateRangeError = Signal(str)   # "" = limpar aviso

    MODE_MES = "MES"
    MODE_TRIMESTRE = "TRIMESTRE"
    MODE_ANUAL = "ANUAL"
    MODE_PERSONALIZADO = "PERSONALIZADO"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Topbar")
        self.setFixedHeight(76)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        section_title = QLabel("Contabase Digital")
        section_title.setObjectName("TopbarBrand")

        # ---- Seletor de modo de período ----
        self.period_mode = QComboBox()
        self.period_mode.setObjectName("TopbarFilter")
        self.period_mode.setFixedWidth(112)
        self.period_mode.addItem("Mês", self.MODE_MES)
        self.period_mode.addItem("Trimestre", self.MODE_TRIMESTRE)
        self.period_mode.addItem("Anual", self.MODE_ANUAL)
        self.period_mode.addItem("Personalizado", self.MODE_PERSONALIZADO)

        # ---- Stack de detalhe do período (4 páginas) ----
        self.period_stack = QStackedWidget()
        self.period_stack.setFixedHeight(40)

        # Página 0 – Mês: combo ano + combo mês
        mes_page = QWidget()
        mes_layout = QHBoxLayout(mes_page)
        mes_layout.setContentsMargins(0, 0, 0, 0)
        mes_layout.setSpacing(6)
        self.mes_year = QComboBox()
        self.mes_year.setObjectName("TopbarFilter")
        self.mes_year.setFixedWidth(82)
        self.mes_month = QComboBox()
        self.mes_month.setObjectName("TopbarFilter")
        self.mes_month.setFixedWidth(112)
        for i, name in enumerate(_MONTHS):
            self.mes_month.addItem(name, i + 1)
        mes_layout.addWidget(self.mes_year)
        mes_layout.addWidget(self.mes_month)

        # Página 1 – Trimestre: combo ano + combo trimestre
        tri_page = QWidget()
        tri_layout = QHBoxLayout(tri_page)
        tri_layout.setContentsMargins(0, 0, 0, 0)
        tri_layout.setSpacing(6)
        self.tri_year = QComboBox()
        self.tri_year.setObjectName("TopbarFilter")
        self.tri_year.setFixedWidth(82)
        self.tri_quarter = QComboBox()
        self.tri_quarter.setObjectName("TopbarFilter")
        self.tri_quarter.setFixedWidth(148)
        for i, name in enumerate(_QUARTERS):
            self.tri_quarter.addItem(name, i + 1)
        tri_layout.addWidget(self.tri_year)
        tri_layout.addWidget(self.tri_quarter)

        # Página 2 – Anual: lista de anos 1900–ano atual (mais recente primeiro)
        anual_page = QWidget()
        anual_layout = QHBoxLayout(anual_page)
        anual_layout.setContentsMargins(0, 0, 0, 0)
        self.anual_year = QComboBox()
        self.anual_year.setObjectName("TopbarFilter")
        self.anual_year.setFixedWidth(100)
        for year in range(_CURRENT_YEAR, 1899, -1):
            self.anual_year.addItem(str(year), year)
        anual_layout.addWidget(self.anual_year)

        # Página 3 – Personalizado: data início + data fim
        custom_page = QWidget()
        custom_layout = QHBoxLayout(custom_page)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(4)
        lbl_de = QLabel("De:")
        lbl_de.setObjectName("TopbarFilterLabel")
        self.date_start = QDateEdit()
        self.date_start.setObjectName("TopbarDateEdit")
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate(_CURRENT_YEAR, date.today().month, 1))
        self.date_start.setFixedWidth(112)
        lbl_ate = QLabel("Até:")
        lbl_ate.setObjectName("TopbarFilterLabel")
        self.date_end = QDateEdit()
        self.date_end.setObjectName("TopbarDateEdit")
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setFixedWidth(112)
        custom_layout.addWidget(lbl_de)
        custom_layout.addWidget(self.date_start)
        custom_layout.addWidget(lbl_ate)
        custom_layout.addWidget(self.date_end)

        self.period_stack.addWidget(mes_page)       # 0
        self.period_stack.addWidget(tri_page)       # 1
        self.period_stack.addWidget(anual_page)     # 2
        self.period_stack.addWidget(custom_page)    # 3

        # ---- Empresa / Obra / Busca ----
        self.empresa = QComboBox()
        self.empresa.setObjectName("TopbarFilter")
        self.empresa.setMinimumWidth(160)
        self.empresa.setMaximumWidth(200)

        self.obra = QComboBox()
        self.obra.setObjectName("TopbarFilter")
        self.obra.setMinimumWidth(160)
        self.obra.setMaximumWidth(200)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar empresa ou obra")
        self.search_input.setObjectName("TopbarSearch")
        self.search_input.setMinimumWidth(130)
        self.search_input.setMaximumWidth(170)

        notify_button = QPushButton("◉")
        notify_button.setObjectName("TopbarIconButton")

        user_host = QWidget()
        user_host.setObjectName("TopbarUserHost")
        user_layout = QHBoxLayout(user_host)
        user_layout.setContentsMargins(8, 4, 8, 4)
        user_layout.setSpacing(6)
        avatar = QLabel("●")
        avatar.setObjectName("TopbarAvatar")
        user_name = QLabel("Usuário")
        user_name.setObjectName("TopbarUserName")
        user_layout.addWidget(avatar)
        user_layout.addWidget(user_name)

        layout.addWidget(section_title)
        layout.addStretch(1)
        layout.addWidget(self.period_mode)
        layout.addWidget(self.period_stack)
        layout.addWidget(self.empresa)
        layout.addWidget(self.obra)
        layout.addWidget(self.search_input)
        layout.addWidget(notify_button)
        layout.addWidget(user_host)

        # ---- Sinais ----
        self.period_mode.currentIndexChanged.connect(self._on_period_mode_changed)
        self.mes_year.currentIndexChanged.connect(self._emit_filters_changed)
        self.mes_month.currentIndexChanged.connect(self._emit_filters_changed)
        self.tri_year.currentIndexChanged.connect(self._emit_filters_changed)
        self.tri_quarter.currentIndexChanged.connect(self._emit_filters_changed)
        self.anual_year.currentIndexChanged.connect(self._emit_filters_changed)
        self.date_start.dateChanged.connect(self._on_date_changed)
        self.date_end.dateChanged.connect(self._on_date_changed)
        self.empresa.currentIndexChanged.connect(self._on_empresa_changed)
        self.obra.currentIndexChanged.connect(self._emit_filters_changed)
        self.search_input.textChanged.connect(self._emit_filters_changed)

        self._load_filters()

    # ------------------------------------------------------------------ #

    def get_filter_payload(self) -> dict[str, object | None]:
        mode = self.period_mode.currentData()

        obra_payload = self.obra.currentData()
        obra_id = None
        obra_empresa_id = None
        if isinstance(obra_payload, dict):
            obra_id = obra_payload.get("id")
            obra_empresa_id = obra_payload.get("empresa_id")

        period: dict[str, object] = {"mode": mode}
        if mode == self.MODE_MES:
            period["year"] = self.mes_year.currentData()
            period["month"] = self.mes_month.currentData()
        elif mode == self.MODE_TRIMESTRE:
            period["year"] = self.tri_year.currentData()
            period["quarter"] = self.tri_quarter.currentData()
        elif mode == self.MODE_ANUAL:
            period["year"] = self.anual_year.currentData()
        elif mode == self.MODE_PERSONALIZADO:
            period["start_date"] = self.date_start.date().toPython()
            period["end_date"] = self.date_end.date().toPython()

        return {
            "period": period,
            "empresa_id": self.empresa.currentData(),
            "obra_id": obra_id,
            "obra_empresa_id": obra_empresa_id,
            "search": self.search_input.text().strip(),
        }

    # ------------------------------------------------------------------ #

    def _load_filters(self) -> None:
        self._reload_empresas()
        self._reload_obras(None)
        self._populate_year_combos()
        self._sync_default_month()

    def _populate_year_combos(self) -> None:
        """Preenche os combos de ano (Mês e Trimestre) de 1900 até o ano atual."""
        years = list(range(_CURRENT_YEAR, 1899, -1))

        for combo in (self.mes_year, self.tri_year):
            combo.blockSignals(True)
            combo.clear()
            for year in years:
                combo.addItem(str(year), year)
            combo.blockSignals(False)

    def _sync_default_month(self) -> None:
        today = date.today()
        idx = self.mes_month.findData(today.month)
        if idx >= 0:
            self.mes_month.blockSignals(True)
            self.mes_month.setCurrentIndex(idx)
            self.mes_month.blockSignals(False)

    def _reload_empresas(self) -> None:
        self.empresa.blockSignals(True)
        try:
            self.empresa.clear()
            self.empresa.addItem("Todas as Empresas", None)
            with get_session() as session:
                empresas = list(
                    session.execute(select(Empresa).order_by(Empresa.razao_social.asc()))
                    .scalars()
                    .all()
                )
            for item in empresas:
                self.empresa.addItem(item.razao_social, item.id)
        finally:
            self.empresa.blockSignals(False)

    def _reload_obras(self, empresa_id: int | None) -> None:
        self.obra.blockSignals(True)
        try:
            self.obra.clear()
            self.obra.addItem("Todas as Obras", {"id": None, "empresa_id": None})
            with get_session() as session:
                stmt = select(Obra).order_by(Obra.nome.asc())
                if empresa_id:
                    stmt = stmt.where(Obra.empresa_id == empresa_id)
                obras = list(session.execute(stmt).scalars().all())
            for item in obras:
                self.obra.addItem(item.nome, {"id": item.id, "empresa_id": item.empresa_id})
        finally:
            self.obra.blockSignals(False)

    def _on_period_mode_changed(self) -> None:
        mode = self.period_mode.currentData()
        index_map = {
            self.MODE_MES: 0,
            self.MODE_TRIMESTRE: 1,
            self.MODE_ANUAL: 2,
            self.MODE_PERSONALIZADO: 3,
        }
        self.period_stack.setCurrentIndex(index_map.get(mode, 0))
        self.dateRangeError.emit("")
        self._emit_filters_changed()

    def _on_empresa_changed(self) -> None:
        empresa_id = self.empresa.currentData()
        empresa_id = int(empresa_id) if isinstance(empresa_id, int) else None
        self._reload_obras(empresa_id)
        self._emit_filters_changed()

    def _on_date_changed(self) -> None:
        start = self.date_start.date()
        end = self.date_end.date()
        if start > end:
            self.dateRangeError.emit("A data inicial não pode ser maior que a data final.")
        else:
            self.dateRangeError.emit("")
        self._emit_filters_changed()

    def _emit_filters_changed(self) -> None:
        self.filtersChanged.emit()

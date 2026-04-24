"""Pagina de apuracoes mensais e trimestrais."""

from app.ui.pages.base_page import BasePage


class ApuracoesPage(BasePage):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Apuracoes",
            description="Execucao e acompanhamento das apuracoes por obra e consolidada.",
            parent=parent,
        )

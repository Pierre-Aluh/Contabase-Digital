"""Pagina de configuracoes gerais."""

from app.ui.pages.base_page import BasePage


class ConfiguracoesPage(BasePage):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Configuracoes",
            description="Parametros globais do sistema e preferencias da aplicacao.",
            parent=parent,
        )

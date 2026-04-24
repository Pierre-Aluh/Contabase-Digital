"""Configuracao central da aplicacao."""

from dataclasses import dataclass

from app.core.constants import APP_NAME, APP_VERSION, DB_FILE


@dataclass(frozen=True)
class AppConfig:
    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    db_path: str = str(DB_FILE)
    locale: str = "pt-BR"


def get_config() -> AppConfig:
    return AppConfig()

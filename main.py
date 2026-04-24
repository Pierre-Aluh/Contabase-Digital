"""Entry-point da aplicacao Contabase Digital."""

from __future__ import annotations

import argparse
import sys
from logging import Logger

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.core.config import get_config
from app.core.logger import configure_logging
from app.db.init_db import initialize_database, validate_database_directory
from app.ui.main_window import MainWindow
from app.ui.styles.dark_theme import load_dark_theme


def bootstrap(logger: Logger) -> None:
    config = get_config()
    logger.info("Iniciando %s v%s", config.app_name, config.app_version)

    extras = validate_database_directory()
    if extras:
        names = ", ".join(item.name for item in extras)
        logger.warning("Arquivos extras detectados em banco_de_dados: %s", names)

    initialize_database()
    logger.info("Banco inicializado em: %s", config.db_path)


def run_app(smoke_ui_ms: int = 0) -> int:
    logger = configure_logging()

    try:
        bootstrap(logger)

        app = QApplication(sys.argv)
        app.setStyleSheet(load_dark_theme())

        window = MainWindow()
        window.show()

        if smoke_ui_ms > 0:
            QTimer.singleShot(smoke_ui_ms, app.quit)

        return app.exec()
    except Exception:
        logger.exception("Erro fatal no bootstrap da aplicacao")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Contabase Digital")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Executa apenas bootstrap (imports, logger e banco) sem abrir UI.",
    )
    parser.add_argument(
        "--smoke-ui-ms",
        type=int,
        default=0,
        help="Abre a UI e fecha automaticamente apos N milissegundos.",
    )
    args = parser.parse_args()

    logger = configure_logging()
    if args.check:
        try:
            bootstrap(logger)
            logger.info("Check de bootstrap concluido com sucesso")
            return 0
        except Exception:
            logger.exception("Falha no check de bootstrap")
            return 1

    return run_app(smoke_ui_ms=args.smoke_ui_ms)


if __name__ == "__main__":
    raise SystemExit(main())

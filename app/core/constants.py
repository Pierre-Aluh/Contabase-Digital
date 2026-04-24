"""Constantes globais da aplicacao."""

from pathlib import Path

APP_NAME = "Contabase Digital"
APP_VERSION = "0.1.0"

BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "banco_de_dados"
DB_FILE = DB_DIR / "contabase_digital.db"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "contabase.log"

DEFAULT_WINDOW_WIDTH = 1440
DEFAULT_WINDOW_HEIGHT = 900
SIDEBAR_WIDTH = 170
TOPBAR_HEIGHT = 60

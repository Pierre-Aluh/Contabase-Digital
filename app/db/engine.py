"""Engine e utilitarios de conexao com o SQLite."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from app.core.constants import DB_DIR, DB_FILE


def get_database_url() -> str:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DB_FILE.as_posix()}"


def create_sqlalchemy_engine() -> Engine:
    engine = create_engine(
        get_database_url(),
        echo=False,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine

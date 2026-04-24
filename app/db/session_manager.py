"""Session manager do SQLAlchemy."""

from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import create_sqlalchemy_engine

_engine = create_sqlalchemy_engine()
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_engine():
    return _engine


def get_session() -> Session:
    return SessionLocal()

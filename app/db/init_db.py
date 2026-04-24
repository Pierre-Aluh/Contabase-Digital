"""Inicializacao do banco e validacoes de bootstrap."""

from pathlib import Path

from sqlalchemy import inspect, text

from app.core.constants import DB_DIR, DB_FILE
from app.db.seed import seed_defaults
from app.db.session_manager import get_engine, get_session
from app.models import (  # noqa: F401
    AjusteFiscal,
    Apuracao,
    ApuracaoItem,
    AuditoriaEvento,
    CategoriaReceita,
    Competencia,
    Empresa,
    LancamentoFiscal,
    Obra,
    ObrigacaoVencimento,
    ParametroSistema,
    PerfilTributario,
)
from app.models.base import Base


def validate_database_directory() -> list[Path]:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    extras = []
    for entry in DB_DIR.iterdir():
        if entry.is_file() and entry.name != DB_FILE.name:
            extras.append(entry)
    return extras


def initialize_database() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _migrate_lancamentos_fiscais(engine)
    _migrate_apuracoes(engine)

    with get_session() as session:
        seed_defaults(session)


def _migrate_lancamentos_fiscais(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "lancamentos_fiscais" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("lancamentos_fiscais")}
    required_columns = {
        "receita_juros",
        "atualizacao_monetaria",
        "variacoes_monetarias_mora",
        "vendas_servicos_vista",
        "vendas_servicos_prazo",
        "aplicacao_financeira",
        "alienacao_investimentos",
        "vendas_bens_imobilizado",
        "juros_recebidos_auferidos",
        "receita_aluguel",
        "receitas_contrato_mutuo",
        "multas_mora",
        "juros_mora",
        "acrescimos_financeiros",
        "descontos_financeiros_obtidos",
        "taxa_emissao_documentos",
        "taxa_cobranca_judicial_extrajudicial",
        "recuperacao_custos_despesas",
    }

    missing_columns = sorted(required_columns - existing_columns)
    if not missing_columns:
        return

    with engine.begin() as connection:
        for column_name in missing_columns:
            connection.execute(
                text(
                    f"ALTER TABLE lancamentos_fiscais ADD COLUMN {column_name} NUMERIC NOT NULL DEFAULT 0"
                )
            )


def _migrate_apuracoes(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "apuracoes" not in table_names:
        return

    existing_columns = {column["name"] for column in inspector.get_columns("apuracoes")}

    with engine.begin() as connection:
        if "versao" not in existing_columns:
            connection.execute(
                text("ALTER TABLE apuracoes ADD COLUMN versao INTEGER NOT NULL DEFAULT 1")
            )
        if "apuracao_valida" not in existing_columns:
            connection.execute(
                text("ALTER TABLE apuracoes ADD COLUMN apuracao_valida BOOLEAN NOT NULL DEFAULT 1")
            )

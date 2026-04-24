"""Testes de integridade basica da camada de dados."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError

from app.core.constants import DB_FILE
from app.db.init_db import initialize_database
from app.db.seed import seed_defaults
from app.db.session_manager import get_session
from app.models.apuracao import Apuracao
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.obra import Obra
from app.models.parametro_sistema import ParametroSistema
from app.models.perfil_tributario import PerfilTributario


@pytest.fixture(scope="module", autouse=True)
def reset_database_file() -> None:
    if DB_FILE.exists():
        DB_FILE.unlink()
    initialize_database()


def test_required_tables_exist() -> None:
    with get_session() as session:
        table_names = set(inspect(session.bind).get_table_names())

    expected = {
        "empresas",
        "obras",
        "perfis_tributarios",
        "categorias_receita",
        "competencias",
        "lancamentos_fiscais",
        "ajustes_fiscais",
        "apuracoes",
        "apuracao_itens",
        "obrigacoes_vencimento",
        "parametros_sistema",
        "auditoria_eventos",
    }
    assert expected.issubset(table_names)


def test_seed_is_idempotent() -> None:
    with get_session() as session:
        before_competencias = session.scalar(select(func.count()).select_from(Competencia))
        before_parametros = session.scalar(select(func.count()).select_from(ParametroSistema))

        seed_defaults(session)

        after_competencias = session.scalar(select(func.count()).select_from(Competencia))
        after_parametros = session.scalar(select(func.count()).select_from(ParametroSistema))

    assert before_competencias == after_competencias
    assert before_parametros == after_parametros


def test_unique_constraint_empresa_cnpj() -> None:
    with get_session() as session:
        session.add(
            Empresa(
                cnpj="12345678000190",
                razao_social="Empresa Teste 1",
                status_ativo=True,
            )
        )
        session.commit()

        session.add(
            Empresa(
                cnpj="12345678000190",
                razao_social="Empresa Teste 2",
                status_ativo=True,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_foreign_key_obra_empresa() -> None:
    with get_session() as session:
        perfil = session.execute(
            select(PerfilTributario).where(PerfilTributario.nome == "CONSTRUCAO_CIVIL_PADRAO")
        ).scalar_one()

        obra_invalida = Obra(
            empresa_id=999999,
            perfil_tributario_id=perfil.id,
            codigo_interno="OBR-INV",
            nome="Obra Invalida",
            cidade="Sao Paulo",
            uf="SP",
            atividade_principal="Construcao",
            aliquota_iss=Decimal("0.03"),
            status_ativo=True,
        )
        session.add(obra_invalida)

        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_apuracao_supports_obra_and_consolidada() -> None:
    with get_session() as session:
        empresa = session.execute(
            select(Empresa).where(Empresa.cnpj == "12345678000190")
        ).scalar_one()
        competencia = session.execute(select(Competencia).where(Competencia.referencia == "01/2026")).scalar_one()
        perfil = session.execute(
            select(PerfilTributario).where(PerfilTributario.nome == "CONSTRUCAO_CIVIL_PADRAO")
        ).scalar_one()

        obra = Obra(
            empresa_id=empresa.id,
            perfil_tributario_id=perfil.id,
            codigo_interno="OBR-001",
            nome="Obra Teste",
            cidade="Campinas",
            uf="SP",
            atividade_principal="Construcao",
            aliquota_iss=Decimal("0.03"),
            status_ativo=True,
        )
        session.add(obra)
        session.flush()

        apuracao_por_obra = Apuracao(
            empresa_id=empresa.id,
            obra_id=obra.id,
            competencia_id=competencia.id,
            consolidada=False,
            total_impostos=Decimal("1000.00"),
        )
        apuracao_consolidada = Apuracao(
            empresa_id=empresa.id,
            obra_id=None,
            competencia_id=competencia.id,
            consolidada=True,
            total_impostos=Decimal("5000.00"),
        )

        session.add_all([apuracao_por_obra, apuracao_consolidada])
        session.commit()

        assert apuracao_por_obra.id is not None
        assert apuracao_consolidada.id is not None

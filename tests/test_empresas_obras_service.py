"""Testes de integracao para service de empresas e obras."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.db.session_manager import get_session
from app.models.competencia import Competencia
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.perfil_tributario import PerfilTributario
from app.services import BusinessRuleError, EmpresaInput, EmpresaObraService, ObraInput

@pytest.fixture
def service() -> EmpresaObraService:
    return EmpresaObraService()


def _valid_cnpj_from_seed(seed: int) -> str:
    base = f"{seed:012d}"

    def calc_digit(block: str, multipliers: list[int]) -> str:
        total = sum(int(n) * m for n, m in zip(block, multipliers))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    d1 = calc_digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = calc_digit(base + d1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return f"{base}{d1}{d2}"


def _obra_input(empresa_id: int, perfil_id: int, codigo: str) -> ObraInput:
    return ObraInput(
        empresa_id=empresa_id,
        perfil_tributario_id=perfil_id,
        codigo_interno=codigo,
        nome=f"Obra {codigo}",
        descricao="Teste",
        cidade="Sao Paulo",
        uf="SP",
        atividade_principal="Construcao civil",
        aliquota_iss="0,05",
        observacoes="obra teste",
    )


def test_create_update_and_toggle_empresa(service: EmpresaObraService) -> None:
    empresa = service.create_empresa(
        EmpresaInput(
            cnpj=_valid_cnpj_from_seed(100000000001),
            razao_social="Empresa QA LTDA",
            nome_fantasia="Empresa QA",
            email="qa@empresa.com",
            telefone="11999999999",
        )
    )

    assert empresa.id is not None

    empresa = service.update_empresa(
        empresa.id,
        EmpresaInput(
            cnpj=empresa.cnpj,
            razao_social="Empresa QA Atualizada LTDA",
            nome_fantasia="Empresa QA",
            email="fiscal@empresa.com",
            telefone="11888888888",
            status_ativo=True,
        ),
    )
    assert empresa.razao_social == "Empresa QA Atualizada LTDA"

    empresa = service.set_empresa_status(empresa.id, False)
    assert empresa.status_ativo is False

    empresa = service.set_empresa_status(empresa.id, True)
    assert empresa.status_ativo is True


def test_create_update_and_toggle_obra(service: EmpresaObraService) -> None:
    empresa = service.create_empresa(
        EmpresaInput(cnpj=_valid_cnpj_from_seed(100000000002), razao_social="Empresa Obra LTDA")
    )

    perfis = service.list_perfis_tributarios()
    assert perfis

    obra = service.create_obra(_obra_input(empresa.id, perfis[0].id, "OBR-100"))
    assert obra.id is not None

    updated = _obra_input(empresa.id, perfis[0].id, "OBR-100")
    updated.nome = "Obra 100 Atualizada"
    updated.cidade = "Campinas"
    obra = service.update_obra(obra.id, updated)
    assert obra.nome == "Obra 100 Atualizada"
    assert obra.cidade == "Campinas"

    obra = service.set_obra_status(obra.id, False)
    assert obra.status_ativo is False

    obra = service.set_obra_status(obra.id, True)
    assert obra.status_ativo is True


def test_block_delete_empresa_with_fiscal_link(service: EmpresaObraService) -> None:
    empresa = service.create_empresa(
        EmpresaInput(cnpj=_valid_cnpj_from_seed(100000000003), razao_social="Empresa Fiscal LTDA")
    )
    perfil_id = service.list_perfis_tributarios()[0].id
    obra = service.create_obra(_obra_input(empresa.id, perfil_id, "OBR-FISC-01"))

    with get_session() as session:
        competencia = session.query(Competencia).filter_by(referencia="01/2026").one()
        session.add(
            LancamentoFiscal(
                empresa_id=empresa.id,
                obra_id=obra.id,
                competencia_id=competencia.id,
                receita_bruta=Decimal("10000.00"),
                outras_receitas_operacionais=Decimal("0.00"),
                devolucoes_cancelamentos_descontos=Decimal("0.00"),
                receita_tributavel_pis_cofins=Decimal("10000.00"),
                observacoes="vinculo fiscal",
                documento_referencia="NF-01",
            )
        )
        session.commit()

    with pytest.raises(BusinessRuleError):
        service.delete_empresa(empresa.id)


def test_block_delete_obra_with_fiscal_link(service: EmpresaObraService) -> None:
    empresa = service.create_empresa(
        EmpresaInput(cnpj=_valid_cnpj_from_seed(100000000004), razao_social="Empresa Obra Fiscal LTDA")
    )

    with get_session() as session:
        perfil = session.query(PerfilTributario).first()
        competencia = session.query(Competencia).filter_by(referencia="02/2026").one()

    obra = service.create_obra(_obra_input(empresa.id, perfil.id, "OBR-FISC-02"))

    with get_session() as session:
        session.add(
            LancamentoFiscal(
                empresa_id=empresa.id,
                obra_id=obra.id,
                competencia_id=competencia.id,
                receita_bruta=Decimal("5000.00"),
                outras_receitas_operacionais=Decimal("0.00"),
                devolucoes_cancelamentos_descontos=Decimal("0.00"),
                receita_tributavel_pis_cofins=Decimal("5000.00"),
                observacoes="vinculo fiscal",
                documento_referencia="NF-02",
            )
        )
        session.commit()

    with pytest.raises(BusinessRuleError):
        service.delete_obra(obra.id)

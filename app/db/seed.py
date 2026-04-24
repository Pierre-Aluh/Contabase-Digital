"""Seed idempotente para dados mestres do banco."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.categoria_receita import CategoriaReceita
from app.models.competencia import Competencia
from app.models.parametro_sistema import ParametroSistema
from app.models.perfil_tributario import PerfilTributario


def _upsert(session: Session, model, lookup: dict, values: dict) -> None:
    stmt = select(model).filter_by(**lookup)
    existing = session.execute(stmt).scalar_one_or_none()
    payload = {k: v for k, v in values.items() if k not in lookup}
    if existing is None:
        session.add(model(**lookup, **payload))
        return
    for field, value in payload.items():
        setattr(existing, field, value)


def seed_defaults(session: Session) -> None:
    perfis = [
        {
            "nome": "COMERCIO_PADRAO",
            "descricao": "Perfil padrao para comercio",
            "percentual_presuncao_irpj": Decimal("0.08"),
            "percentual_presuncao_csll": Decimal("0.12"),
            "ativo": True,
        },
        {
            "nome": "SERVICOS_PADRAO",
            "descricao": "Perfil padrao para servicos",
            "percentual_presuncao_irpj": Decimal("0.32"),
            "percentual_presuncao_csll": Decimal("0.12"),
            "ativo": True,
        },
        {
            "nome": "CONSTRUCAO_CIVIL_PADRAO",
            "descricao": "Perfil padrao para construcao civil",
            "percentual_presuncao_irpj": Decimal("0.08"),
            "percentual_presuncao_csll": Decimal("0.12"),
            "ativo": True,
        },
    ]
    for item in perfis:
        _upsert(session, PerfilTributario, {"nome": item["nome"]}, item)

    categorias = [
        {
            "codigo": "COM",
            "nome": "Comercio",
            "descricao": "Receitas de comercio",
            "percentual_presuncao_irpj": Decimal("0.08"),
            "percentual_presuncao_csll": Decimal("0.12"),
            "ativa": True,
        },
        {
            "codigo": "SRV",
            "nome": "Servicos",
            "descricao": "Receitas de servicos",
            "percentual_presuncao_irpj": Decimal("0.32"),
            "percentual_presuncao_csll": Decimal("0.12"),
            "ativa": True,
        },
        {
            "codigo": "CCL",
            "nome": "Construcao Civil",
            "descricao": "Receitas de construcao civil",
            "percentual_presuncao_irpj": Decimal("0.08"),
            "percentual_presuncao_csll": Decimal("0.12"),
            "ativa": True,
        },
    ]
    for item in categorias:
        _upsert(session, CategoriaReceita, {"codigo": item["codigo"]}, item)

    competencias = [
        {"ano": 2026, "mes": 1, "referencia": "01/2026"},
        {"ano": 2026, "mes": 2, "referencia": "02/2026"},
        {"ano": 2026, "mes": 3, "referencia": "03/2026"},
    ]
    for item in competencias:
        _upsert(
            session,
            Competencia,
            {"ano": item["ano"], "mes": item["mes"]},
            {"referencia": item["referencia"]},
        )

    parametros = [
        {
            "chave": "ALIQUOTA_PIS",
            "descricao": "Aliquota padrao PIS (cumulativo)",
            "valor_decimal": Decimal("0.0065"),
            "ativo": True,
        },
        {
            "chave": "ALIQUOTA_COFINS",
            "descricao": "Aliquota padrao COFINS (cumulativo)",
            "valor_decimal": Decimal("0.03"),
            "ativo": True,
        },
        {
            "chave": "ALIQUOTA_CSLL",
            "descricao": "Aliquota CSLL",
            "valor_decimal": Decimal("0.09"),
            "ativo": True,
        },
        {
            "chave": "ALIQUOTA_IRPJ",
            "descricao": "Aliquota IRPJ",
            "valor_decimal": Decimal("0.15"),
            "ativo": True,
        },
        {
            "chave": "ALIQUOTA_IRPJ_ADICIONAL",
            "descricao": "Aliquota adicional IRPJ",
            "valor_decimal": Decimal("0.10"),
            "ativo": True,
        },
        {
            "chave": "LIMITE_IRPJ_ADICIONAL_TRIMESTRAL",
            "descricao": "Limite trimestral para adicional IRPJ",
            "valor_decimal": Decimal("20000"),
            "ativo": True,
        },
        {
            "chave": "COD_RECEITA_PIS",
            "descricao": "Codigo de receita padrao PIS",
            "valor_texto": "8109",
            "ativo": True,
        },
        {
            "chave": "COD_RECEITA_COFINS",
            "descricao": "Codigo de receita padrao COFINS",
            "valor_texto": "2172",
            "ativo": True,
        },
        {
            "chave": "COD_RECEITA_IRPJ",
            "descricao": "Codigo de receita padrao IRPJ",
            "valor_texto": "2089",
            "ativo": True,
        },
        {
            "chave": "COD_RECEITA_CSLL",
            "descricao": "Codigo de receita padrao CSLL",
            "valor_texto": "2372",
            "ativo": True,
        },
        {
            "chave": "COD_RECEITA_IRPJ_ADICIONAL",
            "descricao": "Codigo de receita padrao IRPJ adicional",
            "valor_texto": "2089",
            "ativo": True,
        },
        {
            "chave": "COD_RECEITA_ISS",
            "descricao": "Codigo interno padrao ISS",
            "valor_texto": "ISS",
            "ativo": True,
        },
        {
            "chave": "VENCIMENTO_DIA_PIS_COFINS",
            "descricao": "Dia padrao de vencimento PIS/COFINS",
            "valor_inteiro": 25,
            "ativo": True,
        },
        {
            "chave": "VENCIMENTO_DIA_IRPJ_CSLL",
            "descricao": "Dia padrao de vencimento IRPJ e CSLL",
            "valor_inteiro": 25,
            "ativo": True,
        },
        {
            "chave": "VENCIMENTO_DIA_ISS_PADRAO",
            "descricao": "Dia padrao de vencimento ISS",
            "valor_inteiro": 5,
            "ativo": True,
        },
        {
            "chave": "PORTAL_FEDERAL_ARRECADACAO_URL",
            "descricao": "URL base para emissao oficial de tributos federais",
            "valor_texto": "https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/pagamentos-e-parcelamentos",
            "ativo": True,
        },
        {
            "chave": "PORTAL_ISS_EMISSAO_URL",
            "descricao": "URL base para emissao municipal de ISS",
            "valor_texto": "https://www.gov.br/empresas-e-negocios/pt-br/empreendedor/tributos",
            "ativo": True,
        },
    ]

    for item in parametros:
        chave = item["chave"]
        values = {
            "descricao": item.get("descricao"),
            "valor_texto": item.get("valor_texto"),
            "valor_decimal": item.get("valor_decimal"),
            "valor_inteiro": item.get("valor_inteiro"),
            "ativo": item.get("ativo", True),
        }
        _upsert(session, ParametroSistema, {"chave": chave}, values)

    session.commit()
    _seed_demo_data_if_needed(session)


def _seed_demo_data_if_needed(session: Session) -> None:
    existing_empresa = session.execute(select(Empresa.id).limit(1)).scalar_one_or_none()
    if existing_empresa is not None:
        return

    competencias = _ensure_rolling_competencias(session, months=12)
    empresa, obras = _seed_demo_empresa_obras(session)

    base_a = Decimal("420000.00")
    base_b = Decimal("265000.00")
    for idx, comp in enumerate(competencias):
        fator = Decimal("1.00") + (Decimal(idx) * Decimal("0.022"))
        receita_a = (base_a * fator).quantize(Decimal("0.01"))
        receita_b = (base_b * fator).quantize(Decimal("0.01"))
        _upsert_demo_lancamento(session, empresa.id, obras[0].id, comp.id, receita_a)
        _upsert_demo_lancamento(session, empresa.id, obras[1].id, comp.id, receita_b)

    _upsert(
        session,
        ParametroSistema,
        {"chave": "DEMO_SEED_VERSION"},
        {
            "descricao": "Versao da carga demonstrativa",
            "valor_texto": "2026.04",
            "ativo": True,
        },
    )
    session.commit()

    from app.services.fiscal_calculation_service import FiscalCalculationService

    calc = FiscalCalculationService()
    for comp in competencias:
        for obra in obras:
            calc.calculate_for_scope(
                empresa_id=empresa.id,
                competencia_id=comp.id,
                obra_id=obra.id,
                consolidada=False,
                persist=True,
            )
        calc.calculate_for_scope(
            empresa_id=empresa.id,
            competencia_id=comp.id,
            obra_id=None,
            consolidada=True,
            persist=True,
        )


def _ensure_rolling_competencias(session: Session, months: int) -> list[Competencia]:
    today = date.today()
    refs: list[tuple[int, int]] = []
    for offset in range(months - 1, -1, -1):
        serial_month = (today.year * 12 + today.month - 1) - offset
        ano = serial_month // 12
        mes = (serial_month % 12) + 1
        refs.append((ano, mes))

    for ano, mes in refs:
        _upsert(
            session,
            Competencia,
            {"ano": ano, "mes": mes},
            {"referencia": f"{mes:02d}/{ano}"},
        )
    session.flush()

    competencias = [
        session.execute(select(Competencia).where(Competencia.ano == ano, Competencia.mes == mes)).scalar_one()
        for ano, mes in refs
    ]
    return competencias


def _seed_demo_empresa_obras(session: Session) -> tuple[Empresa, list[Obra]]:
    current_year = date.today().year
    perfil = session.execute(
        select(PerfilTributario).where(PerfilTributario.nome == "CONSTRUCAO_CIVIL_PADRAO")
    ).scalar_one()

    empresa = Empresa(
        cnpj="11222333000181",
        razao_social="Construtora Horizonte Ltda",
        nome_fantasia="Horizonte Obras",
        email="fiscal@horizonte.local",
        telefone="1130302020",
        status_ativo=True,
    )
    session.add(empresa)
    session.flush()

    obra_a = Obra(
        empresa_id=empresa.id,
        perfil_tributario_id=perfil.id,
        codigo_interno="HZ-001",
        nome="Residencial Aurora",
        descricao="Obra residencial vertical",
        cidade="Sao Paulo",
        uf="SP",
        atividade_principal="Construcao civil",
        aliquota_iss=Decimal("0.05"),
        data_inicio=date(current_year - 1, 2, 1),
        data_fim=None,
        status_ativo=True,
        observacoes="Projeto piloto para dashboard",
    )
    obra_b = Obra(
        empresa_id=empresa.id,
        perfil_tributario_id=perfil.id,
        codigo_interno="HZ-002",
        nome="Centro Logistico Vale",
        descricao="Obra comercial e logistica",
        cidade="Campinas",
        uf="SP",
        atividade_principal="Construcao civil",
        aliquota_iss=Decimal("0.04"),
        data_inicio=date(current_year - 1, 5, 1),
        data_fim=None,
        status_ativo=True,
        observacoes="Projeto demonstrativo",
    )
    session.add_all([obra_a, obra_b])
    session.flush()
    return empresa, [obra_a, obra_b]


def _upsert_demo_lancamento(
    session: Session,
    empresa_id: int,
    obra_id: int,
    competencia_id: int,
    receita_bruta: Decimal,
) -> None:
    existing = session.execute(
        select(LancamentoFiscal).where(
            LancamentoFiscal.obra_id == obra_id,
            LancamentoFiscal.competencia_id == competencia_id,
        )
    ).scalar_one_or_none()
    if existing is not None:
        return

    receita_tributavel = (receita_bruta * Decimal("0.94")).quantize(Decimal("0.01"))
    session.add(
        LancamentoFiscal(
            empresa_id=empresa_id,
            obra_id=obra_id,
            competencia_id=competencia_id,
            receita_bruta=receita_bruta,
            receita_juros=Decimal("0.00"),
            atualizacao_monetaria=Decimal("0.00"),
            variacoes_monetarias_mora=Decimal("0.00"),
            vendas_servicos_vista=(receita_bruta * Decimal("0.45")).quantize(Decimal("0.01")),
            vendas_servicos_prazo=(receita_bruta * Decimal("0.35")).quantize(Decimal("0.01")),
            aplicacao_financeira=Decimal("0.00"),
            alienacao_investimentos=Decimal("0.00"),
            vendas_bens_imobilizado=Decimal("0.00"),
            juros_recebidos_auferidos=Decimal("0.00"),
            receita_aluguel=Decimal("0.00"),
            receitas_contrato_mutuo=Decimal("0.00"),
            multas_mora=Decimal("0.00"),
            juros_mora=Decimal("0.00"),
            acrescimos_financeiros=Decimal("0.00"),
            descontos_financeiros_obtidos=Decimal("0.00"),
            taxa_emissao_documentos=Decimal("0.00"),
            taxa_cobranca_judicial_extrajudicial=Decimal("0.00"),
            recuperacao_custos_despesas=Decimal("0.00"),
            outras_receitas_operacionais=Decimal("0.00"),
            devolucoes_cancelamentos_descontos=(receita_bruta * Decimal("0.01")).quantize(Decimal("0.01")),
            receita_tributavel_pis_cofins=receita_tributavel,
            observacoes="Carga demonstrativa automatica",
            documento_referencia=None,
        )
    )

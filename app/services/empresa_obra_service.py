"""Servicos de negocio para empresas e obras."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from app.db.session_manager import get_session
from app.models.apuracao import Apuracao
from app.models.auditoria_evento import AuditoriaEvento
from app.models.empresa import Empresa
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.obrigacao_vencimento import ObrigacaoVencimento
from app.models.perfil_tributario import PerfilTributario
from app.repositories import EmpresaRepository, ObraRepository
from app.services.errors import BusinessRuleError
from app.utils.cnpj import is_valid_cnpj, sanitize_cnpj


@dataclass
class EmpresaInput:
    cnpj: str
    razao_social: str
    nome_fantasia: str | None = None
    email: str | None = None
    telefone: str | None = None
    status_ativo: bool = True


@dataclass
class ObraInput:
    empresa_id: int
    perfil_tributario_id: int
    codigo_interno: str
    nome: str
    descricao: str | None = None
    cidade: str = ""
    uf: str = ""
    atividade_principal: str = ""
    aliquota_iss: str | int | float | Decimal = Decimal("0.05")
    data_inicio: date | None = None
    data_fim: date | None = None
    status_ativo: bool = True
    observacoes: str | None = None


class EmpresaObraService:
    def list_empresas(self, search: str = "", status: str = "TODOS") -> list:
        with get_session() as session:
            repo = EmpresaRepository(session)
            empresas = repo.list_all()
            result = []
            search_norm = (search or "").strip().lower()
            for item in empresas:
                if search_norm:
                    blob = f"{item.razao_social} {item.cnpj} {item.nome_fantasia or ''}".lower()
                    if search_norm not in blob:
                        continue
                if status == "ATIVAS" and not item.status_ativo:
                    continue
                if status == "INATIVAS" and item.status_ativo:
                    continue
                result.append(item)
            return sorted(result, key=lambda x: x.razao_social.lower())

    def get_empresa(self, empresa_id: int):
        with get_session() as session:
            repo = EmpresaRepository(session)
            empresa = repo.get_by_id(empresa_id)
            if not empresa:
                raise BusinessRuleError("Empresa nao encontrada")
            return empresa

    def create_empresa(self, data: EmpresaInput):
        cnpj = sanitize_cnpj(data.cnpj)
        if not is_valid_cnpj(cnpj):
            raise BusinessRuleError("CNPJ invalido")
        if not data.razao_social.strip():
            raise BusinessRuleError("Razao social e obrigatoria")

        with get_session() as session:
            repo = EmpresaRepository(session)
            if repo.exists(cnpj=cnpj):
                raise BusinessRuleError("CNPJ ja cadastrado")

            entity = repo.create(
                {
                    "cnpj": cnpj,
                    "razao_social": data.razao_social.strip(),
                    "nome_fantasia": (data.nome_fantasia or "").strip() or None,
                    "email": (data.email or "").strip() or None,
                    "telefone": (data.telefone or "").strip() or None,
                    "status_ativo": data.status_ativo,
                }
            )
            self._audit(session, entity.id, "Empresa", entity.id, "CRIAR", None, "empresa criada")
            session.commit()
            session.refresh(entity)
            return entity

    def update_empresa(self, empresa_id: int, data: EmpresaInput):
        cnpj = sanitize_cnpj(data.cnpj)
        if not is_valid_cnpj(cnpj):
            raise BusinessRuleError("CNPJ invalido")

        with get_session() as session:
            repo = EmpresaRepository(session)
            entity = repo.get_by_id(empresa_id)
            if not entity:
                raise BusinessRuleError("Empresa nao encontrada")

            existing = (
                session.execute(select(Empresa).where(Empresa.cnpj == cnpj, Empresa.id != empresa_id))
                .scalar_one_or_none()
            )
            if existing:
                raise BusinessRuleError("CNPJ ja cadastrado em outra empresa")

            before = f"{entity.razao_social}|{entity.status_ativo}"
            repo.update(
                entity,
                {
                    "cnpj": cnpj,
                    "razao_social": data.razao_social.strip(),
                    "nome_fantasia": (data.nome_fantasia or "").strip() or None,
                    "email": (data.email or "").strip() or None,
                    "telefone": (data.telefone or "").strip() or None,
                    "status_ativo": data.status_ativo,
                },
            )
            after = f"{entity.razao_social}|{entity.status_ativo}"
            self._audit(session, entity.id, "Empresa", entity.id, "EDITAR", before, after)
            session.commit()
            session.refresh(entity)
            return entity

    def set_empresa_status(self, empresa_id: int, ativo: bool):
        with get_session() as session:
            repo = EmpresaRepository(session)
            entity = repo.get_by_id(empresa_id)
            if not entity:
                raise BusinessRuleError("Empresa nao encontrada")
            old = entity.status_ativo
            entity.status_ativo = ativo
            self._audit(
                session,
                entity.id,
                "Empresa",
                entity.id,
                "REATIVAR" if ativo else "INATIVAR",
                str(old),
                str(ativo),
            )
            session.commit()
            session.refresh(entity)
            return entity

    def delete_empresa(self, empresa_id: int):
        with get_session() as session:
            repo = EmpresaRepository(session)
            entity = repo.get_by_id(empresa_id)
            if not entity:
                raise BusinessRuleError("Empresa nao encontrada")

            has_obras = bool(session.execute(select(Obra.id).where(Obra.empresa_id == empresa_id).limit(1)).scalar_one_or_none())
            has_fiscal = self._empresa_has_fiscal_links(session, empresa_id)

            if has_fiscal:
                raise BusinessRuleError(
                    "Exclusao fisica bloqueada: empresa possui dados fiscais vinculados. Use inativacao."
                )
            if has_obras:
                raise BusinessRuleError(
                    "Exclusao fisica bloqueada: empresa possui obras vinculadas. Remova/inative as obras antes."
                )

            repo.delete(entity)
            self._audit(session, entity.id, "Empresa", entity.id, "EXCLUIR", entity.razao_social, "excluida")
            session.commit()

    def list_obras(self, empresa_id: int) -> list:
        with get_session() as session:
            obras = list(
                session.execute(select(Obra).where(Obra.empresa_id == empresa_id).order_by(Obra.nome.asc())).scalars().all()
            )
            return obras

    def list_perfis_tributarios(self) -> list:
        with get_session() as session:
            return list(
                session.execute(
                    select(PerfilTributario)
                    .where(PerfilTributario.ativo.is_(True))
                    .order_by(PerfilTributario.nome.asc())
                ).scalars().all()
            )

    def create_obra(self, data: ObraInput):
        if not data.codigo_interno.strip():
            raise BusinessRuleError("Codigo interno da obra e obrigatorio")
        if not data.nome.strip():
            raise BusinessRuleError("Nome da obra e obrigatorio")
        if not data.uf or len(data.uf.strip()) != 2:
            raise BusinessRuleError("UF da obra deve ter 2 caracteres")

        aliquota = self._parse_aliquota_iss(data.aliquota_iss)
        if aliquota < Decimal("0.00") or aliquota > Decimal("1.00"):
            raise BusinessRuleError("Aliquota ISS deve estar entre 0 e 1 (ex.: 0.05 para 5%)")

        with get_session() as session:
            obra_repo = ObraRepository(session)

            empresa = session.get(Empresa, data.empresa_id)
            if not empresa:
                raise BusinessRuleError("Empresa da obra nao encontrada")

            perfil = session.get(PerfilTributario, data.perfil_tributario_id)
            if not perfil:
                raise BusinessRuleError("Perfil tributario nao encontrado")

            dup = (
                session.execute(
                    select(Obra)
                    .where(
                        Obra.empresa_id == data.empresa_id,
                        Obra.codigo_interno == data.codigo_interno.strip(),
                    )
                    .limit(1)
                ).scalar_one_or_none()
            )
            if dup:
                raise BusinessRuleError("Codigo interno da obra ja existe para esta empresa")

            entity = obra_repo.create(
                {
                    "empresa_id": data.empresa_id,
                    "perfil_tributario_id": data.perfil_tributario_id,
                    "codigo_interno": data.codigo_interno.strip(),
                    "nome": data.nome.strip(),
                    "descricao": (data.descricao or "").strip() or None,
                    "cidade": data.cidade.strip(),
                    "uf": data.uf.strip().upper(),
                    "atividade_principal": data.atividade_principal.strip(),
                    "aliquota_iss": aliquota,
                    "data_inicio": data.data_inicio,
                    "data_fim": data.data_fim,
                    "status_ativo": data.status_ativo,
                    "observacoes": (data.observacoes or "").strip() or None,
                }
            )
            self._audit(session, data.empresa_id, "Obra", entity.id, "CRIAR", None, "obra criada")
            session.commit()
            session.refresh(entity)
            return entity

    def update_obra(self, obra_id: int, data: ObraInput):
        aliquota = self._parse_aliquota_iss(data.aliquota_iss)
        if aliquota < Decimal("0.00") or aliquota > Decimal("1.00"):
            raise BusinessRuleError("Aliquota ISS deve estar entre 0 e 1 (ex.: 0.05 para 5%)")

        with get_session() as session:
            obra_repo = ObraRepository(session)
            entity = obra_repo.get_by_id(obra_id)
            if not entity:
                raise BusinessRuleError("Obra nao encontrada")

            dup = (
                session.execute(
                    select(Obra)
                    .where(
                        Obra.empresa_id == data.empresa_id,
                        Obra.codigo_interno == data.codigo_interno.strip(),
                        Obra.id != obra_id,
                    )
                    .limit(1)
                ).scalar_one_or_none()
            )
            if dup:
                raise BusinessRuleError("Codigo interno da obra ja existe para esta empresa")

            before = f"{entity.nome}|{entity.status_ativo}"
            obra_repo.update(
                entity,
                {
                    "empresa_id": data.empresa_id,
                    "perfil_tributario_id": data.perfil_tributario_id,
                    "codigo_interno": data.codigo_interno.strip(),
                    "nome": data.nome.strip(),
                    "descricao": (data.descricao or "").strip() or None,
                    "cidade": data.cidade.strip(),
                    "uf": data.uf.strip().upper(),
                    "atividade_principal": data.atividade_principal.strip(),
                    "aliquota_iss": aliquota,
                    "data_inicio": data.data_inicio,
                    "data_fim": data.data_fim,
                    "status_ativo": data.status_ativo,
                    "observacoes": (data.observacoes or "").strip() or None,
                },
            )
            after = f"{entity.nome}|{entity.status_ativo}"
            self._audit(session, data.empresa_id, "Obra", entity.id, "EDITAR", before, after)
            session.commit()
            session.refresh(entity)
            return entity

    def set_obra_status(self, obra_id: int, ativo: bool):
        with get_session() as session:
            obra_repo = ObraRepository(session)
            entity = obra_repo.get_by_id(obra_id)
            if not entity:
                raise BusinessRuleError("Obra nao encontrada")
            old = entity.status_ativo
            entity.status_ativo = ativo
            self._audit(
                session,
                entity.empresa_id,
                "Obra",
                entity.id,
                "REATIVAR" if ativo else "INATIVAR",
                str(old),
                str(ativo),
            )
            session.commit()
            session.refresh(entity)
            return entity

    def delete_obra(self, obra_id: int):
        with get_session() as session:
            obra_repo = ObraRepository(session)
            entity = obra_repo.get_by_id(obra_id)
            if not entity:
                raise BusinessRuleError("Obra nao encontrada")

            has_fiscal = self._obra_has_fiscal_links(session, obra_id)
            if has_fiscal:
                raise BusinessRuleError(
                    "Exclusao fisica bloqueada: obra possui dados fiscais vinculados. Use inativacao."
                )

            obra_repo.delete(entity)
            self._audit(session, entity.empresa_id, "Obra", obra_id, "EXCLUIR", entity.nome, "excluida")
            session.commit()

    def _empresa_has_fiscal_links(self, session, empresa_id: int) -> bool:
        checks = [
            select(LancamentoFiscal.id).where(LancamentoFiscal.empresa_id == empresa_id).limit(1),
            select(Apuracao.id).where(Apuracao.empresa_id == empresa_id).limit(1),
            select(ObrigacaoVencimento.id).where(ObrigacaoVencimento.empresa_id == empresa_id).limit(1),
        ]
        return any(session.execute(stmt).scalar_one_or_none() is not None for stmt in checks)

    def _parse_aliquota_iss(self, value: str | int | float | Decimal) -> Decimal:
        if isinstance(value, Decimal):
            aliquota = value
        elif isinstance(value, (int, float)):
            aliquota = Decimal(str(value))
        else:
            raw = str(value or "").strip().replace("%", "")
            if not raw:
                raise BusinessRuleError("Aliquota ISS e obrigatoria")

            if "," in raw and "." in raw:
                raw = raw.replace(".", "").replace(",", ".")
            elif "," in raw:
                raw = raw.replace(",", ".")

            try:
                aliquota = Decimal(raw)
            except InvalidOperation as exc:
                raise BusinessRuleError("Aliquota ISS invalida") from exc

        if aliquota > Decimal("1") and aliquota <= Decimal("100"):
            aliquota = aliquota / Decimal("100")
        return aliquota

    def _obra_has_fiscal_links(self, session, obra_id: int) -> bool:
        checks = [
            select(LancamentoFiscal.id).where(LancamentoFiscal.obra_id == obra_id).limit(1),
            select(Apuracao.id).where(Apuracao.obra_id == obra_id).limit(1),
            select(ObrigacaoVencimento.id).where(ObrigacaoVencimento.obra_id == obra_id).limit(1),
        ]
        return any(session.execute(stmt).scalar_one_or_none() is not None for stmt in checks)

    def _audit(
        self,
        session,
        empresa_id: int | None,
        entidade: str,
        entidade_id: int | None,
        acao: str,
        dados_antes: str | None,
        dados_depois: str | None,
    ) -> None:
        session.add(
            AuditoriaEvento(
                empresa_id=empresa_id,
                entidade=entidade,
                entidade_id=entidade_id,
                acao=acao,
                dados_antes=dados_antes,
                dados_depois=dados_depois,
                usuario="sistema",
            )
        )

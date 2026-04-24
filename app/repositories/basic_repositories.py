"""Repositorios basicos por entidade de dados."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.ajuste_fiscal import AjusteFiscal
from app.models.apuracao import Apuracao
from app.models.apuracao_item import ApuracaoItem
from app.models.auditoria_evento import AuditoriaEvento
from app.models.categoria_receita import CategoriaReceita
from app.models.competencia import Competencia
from app.models.empresa import Empresa
from app.models.lancamento_fiscal import LancamentoFiscal
from app.models.obra import Obra
from app.models.obrigacao_vencimento import ObrigacaoVencimento
from app.models.parametro_sistema import ParametroSistema
from app.models.perfil_tributario import PerfilTributario
from app.repositories.base_repository import BaseRepository


class EmpresaRepository(BaseRepository[Empresa]):
    def __init__(self, session: Session):
        super().__init__(session, Empresa)


class ObraRepository(BaseRepository[Obra]):
    def __init__(self, session: Session):
        super().__init__(session, Obra)


class PerfilTributarioRepository(BaseRepository[PerfilTributario]):
    def __init__(self, session: Session):
        super().__init__(session, PerfilTributario)


class CategoriaReceitaRepository(BaseRepository[CategoriaReceita]):
    def __init__(self, session: Session):
        super().__init__(session, CategoriaReceita)


class CompetenciaRepository(BaseRepository[Competencia]):
    def __init__(self, session: Session):
        super().__init__(session, Competencia)


class LancamentoFiscalRepository(BaseRepository[LancamentoFiscal]):
    def __init__(self, session: Session):
        super().__init__(session, LancamentoFiscal)


class AjusteFiscalRepository(BaseRepository[AjusteFiscal]):
    def __init__(self, session: Session):
        super().__init__(session, AjusteFiscal)


class ApuracaoRepository(BaseRepository[Apuracao]):
    def __init__(self, session: Session):
        super().__init__(session, Apuracao)


class ApuracaoItemRepository(BaseRepository[ApuracaoItem]):
    def __init__(self, session: Session):
        super().__init__(session, ApuracaoItem)


class ObrigacaoVencimentoRepository(BaseRepository[ObrigacaoVencimento]):
    def __init__(self, session: Session):
        super().__init__(session, ObrigacaoVencimento)


class ParametroSistemaRepository(BaseRepository[ParametroSistema]):
    def __init__(self, session: Session):
        super().__init__(session, ParametroSistema)


class AuditoriaEventoRepository(BaseRepository[AuditoriaEvento]):
    def __init__(self, session: Session):
        super().__init__(session, AuditoriaEvento)

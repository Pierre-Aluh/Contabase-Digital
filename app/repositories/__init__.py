"""Repositories - Acesso a dados"""

from app.repositories.basic_repositories import (
	AjusteFiscalRepository,
	ApuracaoItemRepository,
	ApuracaoRepository,
	AuditoriaEventoRepository,
	CategoriaReceitaRepository,
	CompetenciaRepository,
	EmpresaRepository,
	LancamentoFiscalRepository,
	ObraRepository,
	ObrigacaoVencimentoRepository,
	ParametroSistemaRepository,
	PerfilTributarioRepository,
)

__all__ = [
	"EmpresaRepository",
	"ObraRepository",
	"PerfilTributarioRepository",
	"CategoriaReceitaRepository",
	"CompetenciaRepository",
	"LancamentoFiscalRepository",
	"AjusteFiscalRepository",
	"ApuracaoRepository",
	"ApuracaoItemRepository",
	"ObrigacaoVencimentoRepository",
	"ParametroSistemaRepository",
	"AuditoriaEventoRepository",
]

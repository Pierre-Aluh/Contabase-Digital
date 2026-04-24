# Contabase Digital - Lucro Presumido

Sistema desktop em Python para gestao fiscal no regime de lucro presumido, com:
- cadastro de empresas e obras
- lancamentos por competencia
- motor fiscal com memoria de calculo
- dashboard executiva com dados reais
- relatorios PDF/XLSX
- guias e vencimentos com status operacional

## Stack

- Python 3.12+
- PySide6
- SQLAlchemy 2.x
- SQLite
- ReportLab
- OpenPyXL

## Requisitos

- Windows 10+ (principal)
- PowerShell
- Ambiente virtual Python

## Setup de desenvolvimento

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Como executar

Validar bootstrap:

```powershell
.venv\Scripts\python.exe main.py --check
```

Abrir aplicacao:

```powershell
.venv\Scripts\python.exe main.py
```

## Seed inicial demonstrativo

O bootstrap inicializa dados mestres e, em base vazia, injeta uma carga demonstrativa idempotente para o primeiro uso:
- empresa e obras de exemplo
- competencias rolling (ultimos 12 meses)
- lancamentos para alimentacao da dashboard
- apuracoes e obrigacoes geradas automaticamente

Objetivo: dashboard completa e navegavel no primeiro start.

## Testes

Executar toda a suite:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Inclui testes de:
- integridade de banco
- regras fiscais
- servicos de empresas/obras/lancamentos
- fluxo final de relatorios e guias

## Operacao do banco SQLite

Banco oficial:
- `banco_de_dados/contabase_digital.db`

Backup rapido:

```powershell
.\scripts\backup_db.ps1
```

Reset de desenvolvimento (recria banco + seed):

```powershell
.\scripts\reset_dev_db.ps1 -Force
```

Detalhes em:
- [docs/BACKUP_E_RESTAURACAO.md](docs/BACKUP_E_RESTAURACAO.md)

## Empacotamento com PyInstaller

Build de distribuicao:

```powershell
.\scripts\build_pyinstaller.ps1 -Clean
```

Artefato esperado:
- `dist/ContabaseDigital/ContabaseDigital.exe`

Detalhes em:
- [docs/EMPACOTAMENTO_PYINSTALLER.md](docs/EMPACOTAMENTO_PYINSTALLER.md)

## Estrutura principal

```text
app/
	core/
	db/
	fiscal/
	models/
	reports/
	repositories/
	services/
	ui/
	utils/
banco_de_dados/
docs/
scripts/
tests/
main.py
requirements.txt
ContabaseDigital.spec
```

## Fluxos funcionais

1. Empresa > Obra > Lancamento > Apuracao
2. Dashboard com filtros por periodo/empresa/obra
3. Relatorios completos com exportacao PDF/XLSX
4. Guias e vencimentos com controle de status
5. Demonstrativo interno de recolhimento em PDF
6. Emissao oficial assistida (abrir portal e copiar payload completo da guia)

## Documentacao complementar

- [docs/CONTEXTO_OPERACIONAL.md](docs/CONTEXTO_OPERACIONAL.md)
- [docs/ESPECIFICACAO_FUNCIONAL.md](docs/ESPECIFICACAO_FUNCIONAL.md)
- [docs/ARQUITETURA.md](docs/ARQUITETURA.md)
- [docs/REGRAS_FISCAIS.md](docs/REGRAS_FISCAIS.md)

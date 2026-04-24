# ARQUITETURA - Contabase Digital

**Data:** 24 de abril de 2026  
**Versão:** 1.0.0  
**Status:** Aprovado para Etapa 2

---

## 1. VISÃO GERAL ARQUITETURAL

### 1.1 Padrão de Arquitetura

**Clean Architecture em 3 Camadas:**

```
┌─────────────────────────────────────────┐
│  CAMADA DE APRESENTAÇÃO (UI)            │ PySide6
│  pages/ widgets/ dialogs/ styles/       │
├─────────────────────────────────────────┤
│  CAMADA DE LÓGICA DE NEGÓCIO (Services) │ Orquestração
│  services/ fiscal/                      │
├─────────────────────────────────────────┤
│  CAMADA DE ACESSO A DADOS (Persistence)│ SQLAlchemy
│  repositories/ db/ models/              │
└─────────────────────────────────────────┘
```

### 1.2 Princípios

- ✓ **Separação de Responsabilidades:** UI não conhece DB, Services não conhece PySide6
- ✓ **Injeção de Dependência:** Services recebem repositories, não instanciam
- ✓ **Idempotência:** Recalcular apuração 10x = mesmo resultado
- ✓ **Auditoria:** Todas as mutações registram actor, hora, antes/depois
- ✓ **Type Hints:** 100% das funções com tipos
- ✓ **Decimal:** Todos os valores monetários usam `Decimal`, nunca `float`

---

## 2. ESTRUTURA DE PASTAS E RESPONSABILIDADES

### 2.1 Estrutura Completa

```
contabase/
├── main.py                              # Entrada da aplicação
├── requirements.txt                     # Dependências
├── .gitignore                           # Git ignore
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/                            # 🔧 Configuração Central
│   │   ├── __init__.py
│   │   ├── config.py                    # Variáveis de ambiente, paths
│   │   ├── logger.py                    # Logging centralizado
│   │   └── constants.py                 # Enums, constantes (tributos, status)
│   │
│   ├── db/                              # 🗄️  Gerenciamento do Banco
│   │   ├── __init__.py
│   │   ├── engine.py                    # SQLAlchemy engine, session factory
│   │   ├── session_manager.py           # Context manager para sessões
│   │   └── seed.py                      # Dados iniciais (tabelas, padrões)
│   │
│   ├── models/                          # 📊 Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py                      # Base class com id, created_at, updated_at
│   │   ├── empresa.py                   # Model: Empresa
│   │   ├── obra.py                      # Model: Obra
│   │   ├── lançamento_fiscal.py         # Model: LancamentoFiscal
│   │   ├── ajuste_fiscal.py             # Model: AjusteFiscal
│   │   ├── apuracao.py                  # Model: Apuracao
│   │   ├── apuracao_item.py             # Model: ApuracaoItem (memória)
│   │   ├── vencimento.py                # Model: Vencimento
│   │   ├── categoria_receita.py         # Model: CategoriaReceita (tabela)
│   │   ├── perfil_tributario.py         # Model: PerfilTributario (tabela)
│   │   ├── parametro_sistema.py         # Model: ParametroSistema (config)
│   │   └── auditoria.py                 # Model: AuditoriaEvento
│   │
│   ├── repositories/                    # 📚 Acesso a Dados
│   │   ├── __init__.py
│   │   ├── base_repository.py           # Base class (CRUD genérico)
│   │   ├── empresa_repository.py        # Repo: Empresa
│   │   ├── obra_repository.py           # Repo: Obra
│   │   ├── lancamento_repository.py     # Repo: Lançamento Fiscal
│   │   ├── ajuste_repository.py         # Repo: Ajuste Fiscal
│   │   ├── apuracao_repository.py       # Repo: Apuração
│   │   ├── vencimento_repository.py     # Repo: Vencimento
│   │   └── auditoria_repository.py      # Repo: Auditoria
│   │
│   ├── services/                        # 🔌 Lógica de Negócio
│   │   ├── __init__.py
│   │   ├── empresa_service.py           # Serviço: Empresa (CRUD + validações)
│   │   ├── obra_service.py              # Serviço: Obra
│   │   ├── lancamento_service.py        # Serviço: Lançamento Fiscal
│   │   ├── ajuste_service.py            # Serviço: Ajuste Fiscal
│   │   ├── apuracao_service.py          # Serviço: Orquestração de apuração
│   │   ├── vencimento_service.py        # Serviço: Vencimento
│   │   └── relatorio_service.py         # Serviço: Geração de relatórios
│   │
│   ├── fiscal/                          # 💰 Motor Fiscal (Cálculos)
│   │   ├── __init__.py
│   │   ├── calculators.py               # Base class para calculadores
│   │   ├── pis_cofins_calculator.py     # Calculador: PIS e COFINS
│   │   ├── irpj_csll_calculator.py      # Calculador: IRPJ e CSLL
│   │   ├── iss_calculator.py            # Calculador: ISS
│   │   ├── consolidation.py             # Consolidação: empresa inteira
│   │   └── memory_builder.py            # Construtor de memória de cálculo
│   │
│   ├── reports/                         # 📄 Geração de Relatórios
│   │   ├── __init__.py
│   │   ├── report_builder.py            # Base para relatórios
│   │   ├── memoria_calculo_report.py    # Relatório: Memória de cálculo
│   │   ├── composicao_report.py         # Relatório: Composição dos tributos
│   │   ├── evolucao_report.py           # Relatório: Evolução mensal
│   │   ├── vencimentos_report.py        # Relatório: Vencimentos
│   │   ├── pdf_exporter.py              # Exportador: PDF
│   │   └── xlsx_exporter.py             # Exportador: XLSX
│   │
│   ├── utils/                           # 🛠️  Utilitários
│   │   ├── __init__.py
│   │   ├── money.py                     # Classe Money, arredondamento, formatação
│   │   ├── date_utils.py                # Datas em padrão brasileiro
│   │   ├── cnpj.py                      # Validação de CNPJ
│   │   ├── decimal_utils.py             # Operações com Decimal
│   │   └── validators.py                # Validadores gerais
│   │
│   └── ui/                              # 🎨 Interface de Usuário
│       ├── __init__.py
│       ├── main_window.py               # Janela principal, gerenciador de pages
│       ├── navigation.py                # Lógica de navegação
│       │
│       ├── pages/                       # Páginas principais
│       │   ├── __init__.py
│       │   ├── dashboard_page.py        # Dashboard
│       │   ├── empresas_page.py         # Gestão de empresas
│       │   ├── apuracao_entrada_page.py # Lançamento de receitas
│       │   ├── apuracao_saida_page.py   # Visualização de apuração
│       │   ├── relatorios_page.py       # Geração de relatórios
│       │   ├── guias_page.py            # Gestão de vencimentos/guias
│       │   └── base_page.py             # Classe base para pages
│       │
│       ├── widgets/                     # Componentes Reutilizáveis
│       │   ├── __init__.py
│       │   ├── kpi_card.py              # Card de KPI
│       │   ├── chart_widget.py          # Widget de gráficos
│       │   ├── tabela_widget.py         # Widget de tabela genérica
│       │   ├── form_builder.py          # Constructor de formulários
│       │   ├── modal_dialog.py          # Dialog base
│       │   ├── toolbar_widget.py        # Barra de ferramentas
│       │   ├── sidebar_widget.py        # Barra lateral
│       │   ├── topbar_widget.py         # Barra superior
│       │   └── status_label.py          # Label com cores de status
│       │
│       ├── dialogs/                     # Diálogos de Confirmação/Edição
│       │   ├── __init__.py
│       │   ├── empresa_dialog.py        # Dialog: Editar empresa
│       │   ├── obra_dialog.py           # Dialog: Editar obra
│       │   ├── ajuste_dialog.py         # Dialog: Adicionar/editar ajuste
│       │   ├── confirmacao_dialog.py    # Dialog: Confirmação genérica
│       │   └── erro_dialog.py           # Dialog: Erro/aviso
│       │
│       ├── styles/                      # Temas e Estilos
│       │   ├── __init__.py
│       │   ├── dark_theme.py            # Paleta de cores dark
│       │   ├── stylesheet.py            # QSS stylesheets globais
│       │   └── fonts.py                 # Definição de fontes
│       │
│       └── assets/                      # Recursos Visuais
│           ├── __init__.py
│           ├── dashboard_referencia.png # Imagem de referência da dashboard
│           ├── icons/                   # Ícones SVG
│           │   ├── empresa.svg
│           │   ├── obra.svg
│           │   ├── relatorio.svg
│           │   └── ...
│           └── images/                  # Imagens gerais
│
├── banco_de_dados/                      # 🗄️  Banco SQLite (apenas .db aqui)
│   └── contabase_digital.db             # (criado em runtime)
│
├── docs/                                # 📚 Documentação
│   ├── CONTEXTO_OPERACIONAL.md
│   ├── ESPECIFICACAO_FUNCIONAL.md
│   ├── ARQUITETURA.md
│   ├── REGRAS_FISCAIS.md
│   ├── UI_DASHBOARD_REFERENCIA.md
│   └── ROADMAP_IMPLEMENTACAO.md
│
└── tests/                               # 🧪 Testes
    ├── __init__.py
    ├── test_models.py                   # Testes: Models
    ├── test_repositories.py             # Testes: Repositories
    ├── test_services.py                 # Testes: Services
    ├── test_fiscal_calculators.py       # Testes: Motor fiscal
    ├── test_integrations.py             # Testes: Integração E2E
    ├── fixtures.py                      # Fixtures de teste (dados)
    └── conftest.py                      # Configuração pytest
```

---

## 3. RESPONSABILIDADES POR CAMADA

### 3.1 Camada de Modelo (Models)

**Responsabilidade:** Definir estrutura de dados, constraints, relacionamentos

**Classes Principais:**

| Classe | Responsabilidade |
|--------|------------------|
| `Empresa` | Dados de empresa (CNPJ, razão social, status) + relacionamento com obras |
| `Obra` | Dados de obra (código, localização, alíquota ISS) + FK empresa |
| `LancamentoFiscal` | Lançamento de receita (bruta, tributável) + FK obra, competência |
| `AjusteFiscal` | Ajuste individual (adição/redução) + FK lançamento + tributo alvo |
| `Apuracao` | Resultado de cálculo (valores de impostos, data cálculo) |
| `ApuracaoItem` | Detalhe da apuração (memória de cálculo passo a passo) |
| `Vencimento` | Data e status de pagamento de tributo |
| `ParametroSistema` | Configurações globais (alíquotas, percentuais presunção) |
| `AuditoriaEvento` | Log de ações (create, update, delete) |

**Regras Implementadas no Model:**
- Constraints de integridade referencial
- Validação de tipos
- Valores padrão
- Timestamps (created_at, updated_at)

---

### 3.2 Camada de Repositório (Repositories)

**Responsabilidade:** Isolar acesso a dados, implementar queries reutilizáveis

**Padrão:** Repository Pattern com base class genérica

```python
class BaseRepository:
    def create(entity) → entity_id
    def read(id) → entity
    def update(id, data) → entity
    def delete(id) → bool
    def list(filters) → [entities]
    def exists(id) → bool
```

**Repositories Específicos:**

| Repository | Responsabilidade |
|------------|------------------|
| `EmpresaRepository` | CRUD empresa + busca por CNPJ + list com paginação |
| `ObraRepository` | CRUD obra + list por empresa + verificar exclusão |
| `LancamentoRepository` | CRUD lançamento + busca por obra/competência |
| `AjusteRepository` | CRUD ajuste + list por lançamento |
| `ApuracaoRepository` | Salvar/recuperar apuração + versioning |
| `VencimentoRepository` | List vencimentos + atualizar status |
| `AuditoriaRepository` | Registrar evento + list com filtros |

**Garantias:**
- Sem lógica de negócio (apenas queries)
- Transações gerenciadas em serviços
- Retorno typed (dataclass ou modelo)

---

### 3.3 Camada de Serviço (Services)

**Responsabilidade:** Orquestrar repositories, aplicar regras de negócio, gerenciar transações

**Exemplo: `EmpresaService`**

```python
class EmpresaService:
    def __init__(self, repo: EmpresaRepository, auditoria_repo):
        self.repo = repo
        self.auditoria = auditoria_repo
    
    def criar_empresa(data: EmpresaDTO) → Empresa:
        # 1. Validar CNPJ, campos obrigatórios
        # 2. Verificar CNPJ único
        # 3. Salvar empresa
        # 4. Carregar padrões (percentuais presunção)
        # 5. Registrar auditoria
        # 6. Retornar empresa
    
    def editar_empresa(id, data) → Empresa:
        # 1. Carregar empresa
        # 2. Validar mudanças
        # 3. Atualizar
        # 4. Registrar auditoria (antes/depois)
        # 5. Retornar
    
    def deletar_empresa(id) → bool:
        # 1. Verificar se tem dados fiscais (lançamentos)
        # 2. Se sim, lançar exceção "não pode deletar"
        # 3. Se não, deletar
        # 4. Registrar auditoria
        # 5. Retornar true
    
    def inativar_empresa(id) → Empresa:
        # 1. Marcar como inativa
        # 2. Registrar auditoria
        # 3. Retornar
```

**Todos os Services seguem esse padrão:**
- Validação de entrada
- Uso de repository
- Regras de negócio
- Transações (atômicas)
- Auditoria
- Type hints
- Exceções específicas (BusinessException, ValidationException)

---

### 3.4 Camada de Lógica Fiscal (Fiscal Calculators)

**Responsabilidade:** Implementar fórmulas de cálculo, gerar memória de cálculo

**Calculadores:**

| Calculador | Fórmula |
|------------|---------|
| `PISCOFINSCalculator` | `base = receita_tributavel + adicoes - reducoes`; `valor = base * aliquota` |
| `IRPJCSLLCalculator` | `base = suma(receita_por_categoria * presuncao%) + adicoes - reducoes`; `valor = base * aliquota` |
| `ISSCalculator` | `base = receita_bruta`; `iss = base * aliquota_obra` |
| `ConsolidationService` | Soma apurações de todas as obras |
| `MemoryBuilder` | Monta estrutura detalhada de cálculo |

**Garantias:**
- 100% `Decimal`, nunca float
- Arredondamento HALF_UP com 2 casas
- Resultados determinísticos (mesma entrada = mesma saída)
- Memória persistida para auditoria

---

### 3.5 Camada de Relatórios (Reports)

**Responsabilidade:** Compilar dados, formatar, exportar em PDF/XLSX

**Fluxo:**
```
ReportService
  → Busca dados via repositories
  → Monta estrutura de relatório
  → Passa para exporter (PDF / XLSX)
  → Retorna bytes ou salva em disco
```

**Relatórios:**
- Memória de Cálculo (por obra / consolidada)
- Composição de Tributos
- Evolução Mensal
- Vencimentos
- Guias de Recolhimento

---

### 3.6 Camada de Interface (UI)

**Responsabilidade:** Apresentar dados, capturar input, delegar para services

**Arquitetura de UI:**

```
MainWindow (janela principal)
  ├── Sidebar (navegação)
  ├── Topbar (filtros globais)
  └── CentralWidget (page dinâmica)
      ├── DashboardPage
      ├── EmpresasPage
      ├── ApuracaoEntradaPage
      ├── ApuracaoSaidaPage
      ├── RelatoriosPage
      └── GuiasPage
```

**Padrão MVC Leve:**
- Page = View (exibe dados)
- Service injetado = Controller (processa)
- User input → Service → atualiza UI

**Separação:**
- ✗ Services não importam PySide6
- ✗ UI não acessa banco diretamente
- ✓ Comunicação via DTOs (dataclasses)

---

## 4. FLUXO DE DADOS

### 4.1 Criar Empresa (End-to-End)

```
[UI: EmpresasPage]
  → usuário clica "Nova"
  → abre FormEmpresa (dialog)
  → usuário preenche CNPJ, razão social, etc
  → usuário clica "Salvar"
  ↓
[UI: valida campos locais]
  → checa campos obrigatórios
  → formata CNPJ
  ↓
[UI: chama EmpresaService.criar_empresa(data)]
  ↓
[Service: EmpresaService.criar_empresa]
  → monta EmpresaDTO a partir de data
  → valida CNPJ (utils.cnpj.valida)
  → verifica CNPJ único (repo.find_by_cnpj)
  → carrega percentuais padrão (parametro_repo)
  → cria entity Empresa
  → salva em DB (repo.create)
  → registra auditoria (auditoria_repo.registrar)
  → retorna EmpresaDTO
  ↓
[UI: recebe DTO]
  → exibe mensagem de sucesso
  → recarrega lista de empresas
  → limpa formulário
```

---

### 4.2 Calcular Apuração (End-to-End)

```
[Service: ApuracaoService.calcular]
  → busca lançamentos do período (lancamento_repo)
  → para cada lançamento:
    ↓
    [Calculador: PISCOFINSCalculator.calcular]
      → busca ajustes (ajuste_repo)
      → base = receita_tributavel + adições - reduções
      → valor = base * alíquota
      → retorna PISCOFINSResult
    ↓
    [Calculador: IRPJCSLLCalculator.calcular]
      → análogo ao PIS/COFINS
      → retorna IRPJCSLLResult
    ↓
    [Calculador: ISSCalculator.calcular]
      → base = receita_bruta
      → valor = base * alíquota_obra
      → retorna ISSResult
    
  → consolida resultados
  → monta memória (MemoryBuilder)
  → cria Apuracao entity
  → salva em DB (apuracao_repo.create)
  → cria ApuracaoItems (detalhes) (repo.create)
  → retorna ApuracaoDTO
```

---

## 5. MODELO DE DADOS (ER Simplificado)

```
Empresa (1) ----< (n) Obra
  ├─ id
  ├─ cnpj (unique)
  ├─ razao_social
  ├─ status (ativa/inativa)
  └─ created_at, updated_at

Obra (1) ----< (n) LancamentoFiscal
  ├─ id
  ├─ empresa_id (FK)
  ├─ codigo (unique per empresa)
  ├─ nome
  ├─ aliquota_iss
  ├─ status
  └─ created_at, updated_at

LancamentoFiscal (1) ----< (n) AjusteFiscal
  ├─ id
  ├─ obra_id (FK)
  ├─ competencia (MM/YYYY)
  ├─ receita_bruta (Decimal)
  ├─ receita_tributavel (Decimal)
  ├─ unique(obra_id, competencia)
  └─ created_at, updated_at

AjusteFiscal
  ├─ id
  ├─ lancamento_id (FK)
  ├─ tributo (enum: PIS, COFINS, CSLL, IRPJ, IRPJ_ADICIONAL)
  ├─ tipo (enum: ADICAO, REDUCAO)
  ├─ valor (Decimal)
  ├─ descricao
  └─ created_at, updated_at

Apuracao (1) ----< (n) ApuracaoItem
  ├─ id
  ├─ obra_id ou NULL (se consolidada)
  ├─ empresa_id (FK)
  ├─ competencia (MM/YYYY)
  ├─ pis_valor (Decimal)
  ├─ cofins_valor (Decimal)
  ├─ ... (outros tributos)
  ├─ data_calculo
  └─ versao (1, 2, 3... se recalculada)

ApuracaoItem
  ├─ id
  ├─ apuracao_id (FK)
  ├─ tributo (enum)
  ├─ receita_bruta (Decimal)
  ├─ base_antes (Decimal)
  ├─ adicoes (Decimal)
  ├─ reducoes (Decimal)
  ├─ base_depois (Decimal)
  ├─ aliquota (Decimal %)
  ├─ valor (Decimal)
  └─ passo (int: 1, 2, 3... para sequência)
```

---

## 6. PADRÕES E TECNOLOGIAS

### 6.1 Padrões de Design

| Padrão | Onde | Motivo |
|--------|------|--------|
| **Repository** | repositories/ | Abstrair acesso a dados |
| **Service Layer** | services/ | Orquestrar lógica complexa |
| **Data Transfer Object (DTO)** | services output | Desacoplamento entre camadas |
| **Factory** | db/seed.py | Criar padrões iniciais |
| **Builder** | fiscal/memory_builder.py | Construir memória de cálculo |
| **Strategy** | fiscal/calculators.py | Trocar estratégia de cálculo |
| **Template Method** | ui/pages/base_page.py | Estrutura comum de pages |

### 6.2 Dependências

| Lib | Versão | Uso |
|-----|--------|-----|
| PySide6 | 6.7.0 | Desktop UI |
| SQLAlchemy | 2.0.23 | ORM |
| python-dateutil | 2.8.2 | Manipulação de datas |
| pytest | 7.4.3 | Testes unitários |
| pytest-cov | 4.1.0 | Cobertura de testes |

### 6.3 Convenções de Código

- **Nomes:** snake_case para variáveis/funções, PascalCase para classes
- **Docstrings:** Google-style em toda função pública
- **Type hints:** 100% obrigatório
- **Validação:** Em service/repository, não em model
- **Exceções:** Criar classes específicas (BusinessException, ValidationException)

---

## 7. FLUXOS DE INICIALIZAÇÃO

### 7.1 Startup da Aplicação

```python
# main.py
1. Load config (paths, env vars)
2. Setup logging
3. Create SQLAlchemy engine
4. Run migrations (alembic ou SQL script)
5. Run seed (se tabelas vazias)
6. Create app (QApplication)
7. Create main window
8. Load inicial data (empresas, obras)
9. Exibir dashboard
10. Run event loop
```

### 7.2 Seed Idempotente

```python
# db/seed.py
1. Se tabela parametros_sistema vazia:
   → insert categorias de receita padrão
   → insert perfis tributários padrão
   → insert parâmetros (alíquotas, presunção)
   → insert regras de vencimento padrão
2. Se tabela não vazia:
   → skip (idempotente)
```

---

## 8. INTEGRAÇÃO COM ESPECIFICAÇÃO FUNCIONAL

Este documento descreve **como** implementar o que está em [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md):

- ✓ Cada "Funcionalidade" em Especificação = serviço (service) em Arquitetura
- ✓ Cada operação (CRUD) = método em service/repository
- ✓ Fluxo de dados (UI → Service → Repository → DB) implementado
- ✓ Modelo de dados suporta todas as entidades especificadas
- ✓ Sem camadas extras ou simplificações

---

## 9. DECISÕES ARQUITETURAIS E RISCOS

### 9.1 Decisão: 3 Camadas (UI → Service → Repository → DB)

**Alternativa:** Direto UI → DB (mais rápido, menos código)

**Justificativa:**
- ✓ Facilita testes (mockar services)
- ✓ Facilita trocar DB (todos usam repository)
- ✓ Lógica fiscal centralizada e reutilizável
- ✗ Um pouco mais verboso

**Risco:** Overhead de abstração

**Mitigação:** Templates/generators para boilerplate repetitivo

---

### 9.2 Decisão: Decimal para Tudo

**Alternativa:** Float (mais rápido, menos preciso)

**Justificativa:**
- ✓ Sem erros de arredondamento (crítico em impostos)
- ✓ Auditoria exata
- ✗ Mais lento (negligenciável em volumes normais)

**Risco:** Float se infiltrar por acidente

**Mitigação:** Tipo hints, testes, linter (mypy)

---

### 9.3 Decisão: Apuração Recalculada (não incremental)

**Alternativa:** Atualizar apuração anterior (mais rápido)

**Justificativa:**
- ✓ Idempotência garantida
- ✓ Sem Estado inconsistente
- ✓ Auditoria simples (recalcular = resultado final)
- ✗ Recalcula tudo mesmo se 1 ajuste mudou

**Risco:** Performance em muitos períodos

**Mitigação:** Índices no BD, cache de resultados intermediários

---

### 9.4 Decisão: Arquivo SQLite local

**Alternativa:** Cliente/Servidor (PostgreSQL)

**Justificativa:**
- ✓ Deployment simples (apenas 1 arquivo)
- ✓ Zero administração de BD
- ✓ Backup fácil (copiar .db)
- ✗ Sem suporte multi-usuário simultâneo

**Risco:** Contenção de arquivo

**Mitigação:** Aplicação single-user por design, documentar

---

## 10. COMPATIBILIDADE COM CONTEXTO OPERACIONAL

Este documento respeita:

- ✓ Stack: Python + PySide6 + SQLAlchemy + SQLite
- ✓ Sem web framework
- ✓ Arquitetura limpa (3 camadas)
- ✓ Type hints em 100%
- ✓ Decimal para moeda
- ✓ Sem circularidades de import
- ✓ Responsabilidades bem definidas

---

**Versão:** 1.0.0  
**Próxima Revisão:** Após implementação Etapa 3

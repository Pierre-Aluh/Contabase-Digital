# ROADMAP DE IMPLEMENTAÇÃO

**Data:** 24 de abril de 2026  
**Versão:** 1.0.0  
**Status:** Aprovado para Etapa 2

---

## 1. VISÃO GERAL DO ROADMAP

O projeto será implementado em **12 etapas sequenciais**, cada uma com:
- ✓ Pré-requisitos (dependências)
- ✓ Escopo bem definido
- ✓ Critério de conclusão (Definition of Done)
- ✓ Riscos identificados
- ✓ Estimativa de esforço (relativa)

**Duração Total Estimada:** 8-12 semanas (desenvolvimento contínuo)

**Equipe:** 1 desenvolvedor Python + design systems

---

## 2. MAPA DE DEPENDÊNCIAS

```
Etapa 1 (Contexto) ──→ Etapa 2 (Documentação)
                          ↓
Etapa 3 (Bootstrap) ←──────┘
                        ↓
Etapa 4 (Banco)
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    Etapa 5         Etapa 6         Etapa 7
    (CRUD)      (Lançamentos)   (Motor Fiscal)
    Empresas        Fiscais
                        ↓               ↓
                        └───────┬───────┘
                                ↓
                            Etapa 8
                          (Dashboard
                             Visual)
                                ↓
                            Etapa 9
                          (Dashboard
                         + Dados Reais)
                                ↓
        ┌───────────────────────┼───────────────────────┐
        ↓                       ↓                       ↓
    Etapa 10            Etapa 11 (Guias)         (em paralelo)
  (Relatórios)
                                ↓
                            Etapa 12
                       (Acabamento Final)
                                ↓
                            Pronto! 🎉
```

---

## 3. DETALHAMENTO DE CADA ETAPA

### ETAPA 1: Contexto Operacional ✅ CONCLUÍDA

**Data:** 24 abr 2026  
**Status:** ✅ Concluído

**Escopo:**
- Criar `docs/CONTEXTO_OPERACIONAL.md`
- Definir stack obrigatória
- Documentar regras de implementação
- Cláusula de revisão permanente

**Entrega:**
- 1 documento (CONTEXTO_OPERACIONAL.md)
- Estrutura de pastas criada
- Contexto permanente estabelecido

**Criterio de Conclusão:**
- [x] Documento criado e validado
- [x] Stack clara e vinculada
- [x] Riscos identificados
- [x] Checklist de revisão pronto

---

### ETAPA 2: Especificação Mestra 🔄 EM ANDAMENTO

**Data Esperada:** 24-26 abr 2026  
**Duração:** 2-3 dias  
**Esforço:** Médio

**Pré-requisitos:**
- [x] Etapa 1 concluída

**Escopo:**
- Criar 5 documentos mestres
- Especificação funcional detalhada
- Arquitetura e design patterns
- Regras fiscais completas
- Layout visual descritivo
- Roadmap de implementação

**Documentos a Criar:**
1. ESPECIFICACAO_FUNCIONAL.md ✅
2. ARQUITETURA.md ✅
3. REGRAS_FISCAIS.md ✅
4. UI_DASHBOARD_REFERENCIA.md ✅
5. ROADMAP_IMPLEMENTACAO.md 🔄 (este arquivo)

**Criterio de Conclusão:**
- [ ] 5 documentos criados
- [ ] Sem conflitos entre documentos
- [ ] Sem contradições periodicidade (mensal vs trimestral)
- [ ] Modelagem suporta empresa→obra→lançamento→apuração→relatório
- [ ] Todos requisitos com critério de aceite claro
- [ ] Riscos de alto risco registrados com mitigação

**Riscos Identificados:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Documentação vaga | Médio | Validar com checklist específico |
| Conflito entre docs | Alto | Revisão cruzada (fiscal vs arquitetura) |
| Escopo creeping | Médio | Revisar contra CONTEXTO_OPERACIONAL |
| Decisões não documentadas | Médio | Registrar decisões + justificativa |

---

### ETAPA 3: Bootstrap do Projeto

**Data Esperada:** 26-30 abr 2026  
**Duração:** 3-4 dias  
**Esforço:** Médio

**Pré-requisitos:**
- [x] Etapa 1 concluída
- [x] Etapa 2 concluída (documentação mestra)

**Scopo:**
- Estrutura inicial de pastas (já criada em etapa 1)
- `requirements.txt` com dependências
- `main.py` executável
- Configuração central (config.py, constants.py, logger.py)
- SQLAlchemy engine e session manager
- Inicialização do banco SQLite
- Tema dark base em QSS
- Janela principal com:
  - Sidebar navegação
  - Topbar com filtros
  - Área central para páginas
- Navigator simples entre páginas
- Logging e tratamento básico de erros
- Dashboard vazia (skeleton)

**Entrega:**
- `main.py` executável
- `app/core/*` (config, logger, constants)
- `app/db/*` (engine, session, seed)
- `app/ui/` estrutura base
- `banco_de_dados/contabase_digital.db` (criado)
- Temas QSS básicos

**Criterio de Conclusão:**
- [ ] `python main.py` sobe sem erro
- [ ] Banco SQLite criado em local correto
- [ ] Nenhum arquivo extra em `banco_de_dados/`
- [ ] Navbar/sidebar funcionam
- [ ] Tema dark aplicado globalmente
- [ ] Sem TODOs/FIXMEs no código
- [ ] Testes: verificar imports, integridade estrutura

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Imports circulares | Alto | Validar hierarquia (UI não conhece DB direto) |
| Banco em local errado | Médio | Testar criação em `banco_de_dados/` |
| Layout quebra com resize | Médio | Testar responsividade básica |
| Performance setup | Baixo | OK se startup < 3s |

---

### ETAPA 4: Modelo de Dados e Banco

**Data Esperada:** 30 abr - 7 mai 2026  
**Duração:** 5-7 dias  
**Esforço:** Alto

**Pré-requisitos:**
- [x] Etapa 3 concluída (bootstrap)

**Escopo:**
- Criar todos os models SQLAlchemy:
  - Empresa, Obra
  - LancamentoFiscal, AjusteFiscal
  - Apuracao, ApuracaoItem
  - Vencimento, ParametroSistema
  - CategoriaReceita, PerfilTributario
  - AuditoriaEvento
- Base class com id, created_at, updated_at
- Relacionamentos (FK, índices)
- Constraints integridade (unique, notnull)
- Session manager e transaction handling
- Repositories básicos para cada model
- Script seed automático (idempotente)
- Testes de integridade BD

**Entrega:**
- `app/models/*.py` (12 models)
- `app/repositories/*.py` (8 repositories)
- `app/db/session_manager.py`
- `app/db/seed.py`
- `tests/test_models.py`
- `tests/test_repositories.py`
- BD funcional com seed

**Criterio de Conclusão:**
- [ ] Todos os models criados
- [ ] Constraints integridade presentes
- [ ] Seed é idempotente (roda 2x = mesmo resultado)
- [ ] Repositórios implementam CRUD genérico
- [ ] Testes de modelo/repository passam
- [ ] Banco não tem arquivos extras
- [ ] Type hints em 100%
- [ ] Sem lógica de negócio em models (apenas constraints)

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Circular imports entre models | Alto | Revisar relacionamentos |
| Integridade referencial quebrada | Alto | Testes de constraint |
| Seed não idempotente | Médio | Testar rodar 2-3x |
| Performance queries | Baixo | Índices adicionados no design |

---

### ETAPA 5: CRUD Empresas e Obras

**Data Esperada:** 7-14 mai 2026  
**Duração:** 5-7 dias  
**Esforço:** Alto

**Pré-requisitos:**
- [x] Etapa 4 concluída (banco)

**Escopo:**
- EmpresaService (criar, editar, inativar, deletar, listar)
- ObraService (idem)
- Validações (CNPJ, campos obrigatórios)
- Auditoria (registrar ações)
- EmpresasPage (listagem, CRUD, nested obras)
- Dialogs (FormEmpresa, FormObra)
- UX intuitiva, sem placeholder
- Testes services + integração

**Entrega:**
- `app/services/empresa_service.py`
- `app/services/obra_service.py`
- `app/ui/pages/empresas_page.py`
- `app/ui/dialogs/empresa_dialog.py`
- `app/ui/dialogs/obra_dialog.py`
- `app/utils/cnpj.py` (validação)
- `tests/test_services.py`

**Criterio de Conclusão:**
- [ ] CRUD completo funcionando
- [ ] Validações ativas
- [ ] Auditoria registrando ações
- [ ] UI responsiva e intuitiva
- [ ] Sem exclusão física com dados vinculados
- [ ] Testes passam (CRUD, validação, bloqueio exclusão)
- [ ] Fluxo completo testável manualmente

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Validação falha CNPJ | Médio | Testes unitários validação |
| Exclusão deleta dados relacionados | Alto | Constraint BD + teste |
| UI não intuitiva | Médio | Feedback visual claro |
| Performance lista grande | Baixo | Paginação implementada |

---

### ETAPA 6: Lançamentos Fiscais por Obra e Competência

**Data Esperada:** 14-21 mai 2026  
**Duração:** 5-7 dias  
**Esforço:** Alto

**Pré-requisitos:**
- [x] Etapa 4 concluída (banco)
- [x] Etapa 5 concluída (empresas/obras)

**Escopo:**
- LancamentoService (criar, editar, duplicar, listar, deletar)
- AjusteService (adicionar/remover ajustes)
- ApuracaoEntradaPage (formulário de lançamento)
- Suporte a múltiplos ajustes por tributo
- Duplicação de mês anterior (copy receitas)
- Visualização base antes/depois ajustes
- Testes persistência normalizada

**Entrega:**
- `app/services/lancamento_service.py`
- `app/services/ajuste_service.py`
- `app/ui/pages/apuracao_entrada_page.py`
- `app/ui/dialogs/ajuste_dialog.py`
- `app/ui/widgets/ajuste_table_widget.py`
- `tests/test_lancamento_integration.py`

**Criterio de Conclusão:**
- [ ] Lançamento CRUD funcionando
- [ ] Múltiplos ajustes persistidos
- [ ] Duplicação não copia ajustes (apenas receitas)
- [ ] Base antes/depois visível
- [ ] Filtros (empresa, obra, competência) não se contradizem
- [ ] Testes passam
- [ ] Zero recálculos implícitos (tudo persistido)

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Duplicação copia ajustes (bug) | Alto | Testes duplicação |
| Base antes/depois confuso visualmente | Médio | UI clara (destacar diferenças) |
| Filtros contraditórios | Médio | Lógica de filtro clara |
| Competência invalida (futura) | Médio | Validação >= hoje |

---

### ETAPA 7: Motor Fiscal Completo

**Data Esperada:** 21-28 mai 2026  
**Duração:** 7 dias  
**Esforço:** Alto

**Pré-requisitos:**
- [x] Etapa 4 concluída (banco)
- [x] Etapa 6 concluída (lançamentos)

**Escopo:**
- FiscalCalculationService (orquestrador)
- PISCOFINSCalculator (fórmulas, Decimal)
- IRPJCSLLCalculator (mensal + trimestral)
- ISSCalculator (por obra)
- ConsolidationService (empresa inteira)
- MemoryBuilder (persistir passos cálculo)
- Parametrização (alíquotas no banco, não hardcoded)
- Testes unitários cobrindo:
  - Caso simples
  - Com ajustes
  - Adicional IRPJ
  - Consolidação
- Auditoria de cálculos

**Entrega:**
- `app/fiscal/calculators.py` (classes base)
- `app/fiscal/pis_cofins_calculator.py`
- `app/fiscal/irpj_csll_calculator.py`
- `app/fiscal/iss_calculator.py`
- `app/fiscal/consolidation.py`
- `app/fiscal/memory_builder.py`
- `app/services/apuracao_service.py`
- `tests/test_fiscal_calculators.py`

**Criterio de Conclusão:**
- [ ] Todos os tributos calculam corretamente
- [ ] Decimal usado em 100% dos cálculos
- [ ] Nenhuma alíquota hardcoded (parametrizado)
- [ ] Memória persistida == resultado exibido
- [ ] Testes unitários passam (casos de borda)
- [ ] Recálculo é idempotente (mesma entrada = mesma saída)
- [ ] Consolidação não duplica receitas
- [ ] Adicional IRPJ apenas se base > limite

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Float infiltra cálculo | Alto | Type hints + linter + testes |
| Arredondamento inconsistente | Alto | Classe Money centralizada |
| Memória incompleta/incorreta | Médio | Teste: memory == resultado |
| Consolidação duplica | Alto | Teste consolidação específico |
| Parametrização esquecida | Médio | Auditoria: todos params no BD |

---

### ETAPA 8: Dashboard Visual (Fidelidade Máxima)

**Data Esperada:** 28 mai - 4 jun 2026  
**Duração:** 5-7 dias  
**Esforço:** Alto (design + frontend)

**Pré-requisitos:**
- [x] Etapa 3 concluída (bootstrap UI base)

**Escopo:**
- Replicar layout visual da imagem de referência
- 4 KPI cards (receita, PIS+COFINS, IRPJ+CSLL, ISS)
- Gráfico evolução 12m (line chart)
- Resumo apuração (cards dos tributos)
- Tabela composição tributos
- Gráfico distribuição (donut)
- Card próximos vencimentos
- Barra de ações (Gerar Guia, Exportar, Compartilhar)
- Tema dark azul petróleo + acentos
- Widgets customizados (KPICard, ChartWidget, etc)
- Dados mockados (placeholder temporário)

**Entrega:**
- `app/ui/pages/dashboard_page.py`
- `app/ui/widgets/kpi_card.py`
- `app/ui/widgets/chart_widget.py`
- `app/ui/widgets/tabela_widget.py`
- `app/ui/styles/dark_theme.py`
- `app/ui/styles/stylesheet.qss`
- Screenshot para comparação

**Criterio de Conclusão:**
- [ ] Layout corresponde visualmente à referência
- [ ] Cores corretas (azul petróleo, acentos)
- [ ] Espaçamento/alinhamento fiel
- [ ] Cantos, sombras, beiras conforme referência
- [ ] Dados mockados (placeholder claro)
- [ ] Zero componentes genéricos feios (tudo customizado)
- [ ] Responsivo (re-size não quebra)
- [ ] Screenshot vs referência (manual comparison)

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Visual não fiel | Alto | Screenshot vs referência, iterativo |
| Performance gráficos | Médio | Otimizar matplotlib/plotly |
| Componentes duplicados | Médio | Reutilizar widgets base |
| Responsividade quebra | Médio | Testar breakpoints |

---

### ETAPA 9: Integrar Dashboard com Dados Reais

**Data Esperada:** 4-11 jun 2026  
**Duração:** 5-7 dias  
**Esforço:** Alto

**Pré-requisitos:**
- [x] Etapa 7 concluída (motor fiscal)
- [x] Etapa 8 concluída (dashboard visual)

**Escopo:**
- Conectar dashboard ao banco real
- Filtros funcionais (competência, empresa, obra)
- KPIs calculados com dados reais
- Gráfico com histórico 12m
- Resumo apuração com valores reais
- Tabela composição com dados reais
- Gráfico distribuição com % corretos
- Vencimentos lidos de BD
- Botões funcionais (Gerar Guia, Exportar, etc)
- Refresh automático de dados
- Diferenciar projeção mensal vs fechamento trimestral
- Zero dados fake remanescentes

**Entrega:**
- `app/ui/pages/dashboard_page.py` (atualizada)
- Serviços de dashboard (busca dados, calcula filtros)
- Testes integração dashboard

**Criterio de Conclusão:**
- [ ] Todos os dados vêm do banco (não hardcoded)
- [ ] Números dashboard == números banco
- [ ] Filtros funcionam sem conflito
- [ ] Projeção vs fechamento explicado ao usuário
- [ ] Zero dados fake
- [ ] Refresh carrega dados novos
- [ ] Performance < 1s para carregar
- [ ] Testes integração passam

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Números não batem | Alto | Comparar cálculos dashboard vs banco |
| Filtros conflitantes | Médio | Lógica clara de precedência |
| Performance slider | Médio | Índices BD, cache se necessário |
| Mocks esquecidos | Alto | Audit: grep "mock" / "TODO" |

---

### ETAPA 10: Relatórios e Memória de Cálculo

**Data Esperada:** 11-18 jun 2026  
**Duração:** 5-7 dias  
**Esforço:** Alto

**Pré-requisitos:**
- [x] Etapa 7 concluída (motor fiscal + memória)

**Escopo:**
- RelatoriosPage (seleção tipo, filtros)
- Relatório 1: Memória cálculo (por obra / consolidada)
- Relatório 2: Composição tributos
- Relatório 3: Evolução mensal
- Relatório 4: Vencimentos
- Exportadores PDF e XLSX
- Layout profissional
- Dados comparecem com persistido
- Botão dashboard "Exportar" integrado

**Entrega:**
- `app/ui/pages/relatorios_page.py`
- `app/reports/memoria_calculo_report.py`
- `app/reports/composicao_report.py`
- `app/reports/evolucao_report.py`
- `app/reports/vencimentos_report.py`
- `app/reports/pdf_exporter.py`
- `app/reports/xlsx_exporter.py`
- Testes relatórios

**Criterio de Conclusão:**
- [ ] 4 tipos de relatório implementados
- [ ] PDF e XLSX com conteúdo idêntico
- [ ] Layout PDF legível e profissional
- [ ] XLSX organizado por abas (consolidados)
- [ ] Relatório consolidado não duplica
- [ ] Números == banco + apuração
- [ ] Botão dashboard funciona
- [ ] Testes passam

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| PDF feio ou ilegível | Médio | Iteração design, validação manual |
| Consolidado duplica | Alto | Teste consolidação específico |
| Números divergem banco | Alto | Comparar fórmulas |
| Performance grande período | Médio | Paginação, otimização |

---

### ETAPA 11: Guias, Vencimentos e Status

**Data Esperada:** 18-25 jun 2026  
**Duração:** 5-7 dias  
**Esforço:** Médio-Alto

**Pré-requisitos:**
- [x] Etapa 7 concluída (apuração)

**Escopo:**
- GuiasPage (listagem com filtros)
- Cadastro parametrizável vencimentos
- Cadastro códigos de receita
- Geração PDF demonstrativo recolhimento
- Marcação manual de pagamento
- Status (aberto, pago, vencido, cancelado, N/A)
- Integração com card vencimentos dashboard
- Botão "Gerar Guia" funcional

**Entrega:**
- `app/ui/pages/guias_page.py`
- `app/services/vencimento_service.py`
- `app/reports/guia_report.py` (PDF demonstrativo)
- `app/ui/dialogs/pagamento_dialog.py`

**Criterio de Conclusão:**
- [ ] Vencimentos parametrizados (não hardcoded)
- [ ] Status sincronizado (página, dashboard, BD)
- [ ] PDF com base, alíquota, valor, vencimento, código
- [ ] Marcação pagamento atualiza status
- [ ] Próximos vencimentos widget funcional
- [ ] Botão "Gerar Guia" não é fake
- [ ] Testes passam

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Vencimento hardcoded | Médio | Audit: nenhuma data literal |
| Status inconsistente | Médio | Teste sincronização página/dashboard/BD |
| PDF incorreto | Médio | Validação manual conteúdo |

---

### ETAPA 12: Acabamento Final, Testes e Entrega

**Data Esperada:** 25 jun - 2 jul 2026  
**Duração:** 5-7 dias  
**Esforço:** Médio

**Pré-requisitos:**
- [x] Todas as etapas 1-11 concluídas

**Escopo:**
- Auditoria geral de duplicidade
- Revisão names (classes, variáveis)
- Revisão UX todas as páginas
- Revisão validações
- Revisão arredondamento monetário
- Consistência visual temas
- Seed demonstrativa (dados bonitos)
- README.md final
- Instruções backup banco
- Script reset BD (dev)
- Empacotamento PyInstaller
- Testes adicionais integração
- Sem TODOs/FIXMEs

**Entrega:**
- README.md atualizado
- Seed com dados bonitos
- Executável (.exe via PyInstaller)
- Testes integração E2E
- Documentação final
- Árvore arquivos final

**Criterio de Conclusão:**
- [ ] `python main.py` sobe limpo
- [ ] `pytest -q` passa 100%
- [ ] Dashboard fiel à referência
- [ ] Zero TODOs/FIXMEs
- [ ] Sem imports órfãos
- [ ] Sem duplicidade código
- [ ] Arredondamento consistente
- [ ] Seed demonstrativa completa
- [ ] README claro e completo
- [ ] Sem fluxo quebrado
- [ ] Limitações documentadas honestamente

**Riscos:**
| Risco | Nível | Mitigação |
|-------|-------|-----------|
| Fluxo quebrado não detectado | Médio | Testes E2E cobrindo fluxos |
| Regressão em integração | Alto | Bateria testes ampla |
| Dados seed incompletos | Médio | Seed inclui todos cenários |

---

## 4. ESTIMATIVAS DE ESFORÇO

### Por Etapa (horas de desenvolvimento)

| Etapa | Titulo | Horas | Dias | Dependências |
|-------|--------|-------|------|--------------|
| 1 | Contexto | 8 | 1 | Nenhuma |
| 2 | Documentação | 16 | 2 | Etapa 1 |
| 3 | Bootstrap | 24 | 3 | Etapa 2 |
| 4 | Banco | 40 | 5 | Etapa 3 |
| 5 | CRUD Empresas | 40 | 5 | Etapa 4 |
| 6 | Lançamentos | 40 | 5 | Etapa 4, 5 |
| 7 | Motor Fiscal | 48 | 6 | Etapa 4, 6 |
| 8 | Dashboard Visual | 40 | 5 | Etapa 3 |
| 9 | Dashboard Real | 40 | 5 | Etapa 7, 8 |
| 10 | Relatórios | 40 | 5 | Etapa 7 |
| 11 | Guias | 32 | 4 | Etapa 7 |
| 12 | Acabamento | 32 | 4 | Etapa 1-11 |
| **TOTAL** | | **400 h** | **50 dias** | |

**Nota:** 1 dia = 8 horas de desenvolvimento focado  
**Calendário:** 50 dias úteis ≈ 10 semanas (com pausas, code review, ajustes)

---

## 5. CRITÉRIOS GLOBAIS DE CONCLUSÃO

### Ao Final do Projeto (Etapa 12)

**Funcionalidade:**
- ✓ Todos os 5 módulos principais funcionando
- ✓ Fluxo completo empresa→obra→lançamento→apuração→relatório testado
- ✓ Zero dados fake (exceto seed demo)
- ✓ Auditoria registrando ações

**Código:**
- ✓ Type hints em 100%
- ✓ Decimal em 100% de cálculos monetários
- ✓ Zero circularidades de import
- ✓ Sem imports órfãos
- ✓ Zero TODOs/FIXMEs
- ✓ Nomes consistentes (snake_case, PascalCase)
- ✓ Docstrings Google-style

**Testes:**
- ✓ Unitários: >80% lógica fiscal
- ✓ Integração: fluxos completos
- ✓ E2E: casos de uso principais
- ✓ `pytest -q` passa 100%

**Documentação:**
- ✓ README.md completo
- ✓ Docstrings em funções públicas
- ✓ CONTEXTO_OPERACIONAL.md atualizado se necessário
- ✓ Limitações documentadas

**Visual:**
- ✓ Dashboard fiel à referência (screenshot comparado)
- ✓ Tema dark consistente
- ✓ Responsividade preservada
- ✓ Sem componentes genéricos feios

**Performance:**
- ✓ Startup < 3s
- ✓ Dashboard < 1s
- ✓ Relatório < 5s
- ✓ Sem freezes (UI responsiva)

---

## 6. INTEGRAÇÃO COM OUTROS DOCUMENTOS

Este roadmap é coerente com:

- ✓ [CONTEXTO_OPERACIONAL.md](CONTEXTO_OPERACIONAL.md) - regras permanentes
- ✓ [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md) - o que fazer
- ✓ [ARQUITETURA.md](ARQUITETURA.md) - como fazer
- ✓ [REGRAS_FISCAIS.md](REGRAS_FISCAIS.md) - regras do negócio
- ✓ [UI_DASHBOARD_REFERENCIA.md](UI_DASHBOARD_REFERENCIA.md) - visual esperado

---

## 7. COMO USAR ESTE ROADMAP

### Para Planejamento
- Cada etapa é um milestone
- Dependências claras (não começar antes do pré-requisito)
- Estimativas realistas (buffer incorporado)

### Para Execução
- Ao iniciar etapa X, revisar seção correspondente
- Seguir Criterio de Conclusão ponto a ponto
- Aplicar Checklist de Revisão Permanente (CONTEXTO_OPERACIONAL.md)

### Para Rastreamento
- [x] Etapa 1 concluída
- [x] Etapa 2 concluída
- [ ] Etapa 3-12 em andamento/não iniciadas

### Para Comunicação
- Relatar status por etapa
- Registrar bloqueadores (riscos realized)
- Documentar desvios do roadmap

---

## 8. PLANO B: Risco Critical Path

Se alguma etapa crítica travar:

### Se Etapa 4 (Banco) Travar
- **Impacto:** Bloqueia tudo
- **Plano B:** Usar BD in-memory (sqlite://) temporário
- **Ação:** Revisar constraints integridade

### Se Etapa 7 (Motor Fiscal) Travar
- **Impacto:** Bloqueia etapas 9, 10, 11
- **Plano B:** Implementar cálculo simplificado primeiro, iterar
- **Ação:** Quebrar em sub-etapas (PIS/COFINS primeiro, depois IRPJ/CSLL)

### Se Etapa 8 (Dashboard Visual) Travar
- **Impacto:** Afeta UX (bloqueador)
- **Plano B:** Usar framework de componentes (ex: Qt Designer)
- **Ação:** Iteração incremental, mockups rápidos

---

**Versão:** 1.0.0  
**Próxima Revisão:** Quinzenal durante execução

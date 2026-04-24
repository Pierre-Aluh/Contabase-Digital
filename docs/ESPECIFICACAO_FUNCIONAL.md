# ESPECIFICAÇÃO FUNCIONAL - Contabase Digital

**Data:** 24 de abril de 2026  
**Versão:** 1.0.0  
**Status:** Aprovado para Etapa 2

---

## 1. ESCOPO DO SISTEMA

### 1.1 Objetivo Geral

Sistema desktop para gestão integrada de cálculo de impostos sobre lucro presumido. Permite cadastro de empresas e obras, lançamento de receitas mensais, cálculo automático de tributos (PIS, COFINS, CSLL, IRPJ, IRPJ Adicional e ISS) com suporte a ajustes individuais, geração de relatórios e controle de vencimentos.

### 1.2 Públicos-Alvo

- **Contador/Gestor Fiscal:** Responsável por lançar receitas, efetuar ajustes e gerar relatórios
- **Gerente de Empresa:** Consulta apuração e status de tributos
- **Auditor Interno:** Valida cálculos e gera memória de cálculo detalhada

### 1.3 Premissas

- Sistema será usado por 1 a 5 usuários por empresa (não é multi-tenant, cada instalação = 1 cliente)
- Dados podem ser manipulados e exportados localmente (banco local)
- Cálculos devem ser auditáveis e reprodutíveis
- Interface deve ser intuitiva e responsiva

### 1.4 Restrições

- ✗ Não integrar com sistemas governamentais oficiais (e-CAC, RFB)
- ✗ Não é um software de emissão de NF-e
- ✗ Não gerencia fluxo de caixa ou contas a pagar/receber
- ✓ Foco exclusivo em cálculo de impostos e relatórios

---

## 2. FUNCIONALIDADES PRINCIPAIS

### 2.1 Módulo de Cadastros Mestres

#### 2.1.1 Gestão de Empresas

**Funcionalidade:** Cadastrar e manter empresas

**Dados Obrigatórios:**
- Razão Social
- CNPJ (validado)
- Inscrição Estadual (opcional, mas recomendado)
- Endereço (rua, número, bairro, cidade, UF, CEP)
- Contato (telefone, email)
- Regime de Apuração (Lucro Presumido - padrão)
- Percentual de Presunção de Lucro (por categoria - editável)
- Status (Ativa / Inativa)

**Operações:**
- ✓ Criar nova empresa
- ✓ Editar dados da empresa
- ✓ Visualizar empresa e suas obras
- ✓ Inativar empresa (soft delete se houver dados fiscais)
- ✓ Deletar empresa (apenas sem movimentação fiscal)
- ✓ Listar com filtro, busca e paginação

**Regras de Negócio:**
- CNPJ deve ser único
- Empresa só pode ser deletada se não tiver lançamentos ou apurações
- Se houver movimentação fiscal, apenas inativar (auditoria)
- Ao criar, carregar percentuais padrão de presunção do sistema

---

#### 2.1.2 Gestão de Obras

**Funcionalidade:** Cadastrar e manter obras vinculadas a empresas

**Dados Obrigatórios:**
- Código Interno (único por empresa)
- Nome da Obra
- Descrição (opcional)
- Localização (cidade, UF)
- Atividade Principal (seleção de tabela)
- Data de Início
- Data de Encerramento (opcional)
- Perfil Tributário (seleção de tabela)
- Alíquota de ISS (%) - customizável por obra
- Status (Ativa / Inativa)

**Operações:**
- ✓ Criar obra vinculada a empresa
- ✓ Editar dados da obra
- ✓ Visualizar lançamentos da obra
- ✓ Inativar obra
- ✓ Deletar obra (apenas sem movimentação)
- ✓ Listar com filtro por empresa

**Regras de Negócio:**
- Código interno único por empresa (pode repetir em empresas diferentes)
- Data de encerramento >= data de início (validação)
- Obra sem data de encerramento = obra em andamento
- Alíquota de ISS entre 2% e 5% (validação)

---

### 2.2 Módulo de Lançamentos Fiscais

#### 2.2.1 Registro de Lançamentos

**Funcionalidade:** Lançar receitas mensais por obra e competência

**Dados de Receita:**
- Receita Bruta (R$)
- Outras Receitas Operacionais (R$)
- Devoluções, Cancelamentos, Descontos Incondicionais (R$)
- **Receita Tributável para PIS/COFINS** = Bruta + Operacionais - Devoluções
- Observações (texto livre)

**Operações:**
- ✓ Criar lançamento para obra + competência
- ✓ Editar lançamento existente
- ✓ Visualizar lançamento
- ✓ Duplicar lançamento do mês anterior (copia receitas, não ajustes)
- ✓ Listar lançamentos com filtros (empresa, obra, competência)
- ✓ Deletar lançamento (apenas se sem apuração finalizada)

**Regras de Negócio:**
- Um lançamento por obra + competência (única combinação)
- Competência em formato MM/YYYY
- Receita Tributável calculada automaticamente
- Competência >= data de início da obra
- Competência <= hoje (não permite futuro)

---

#### 2.2.2 Ajustes Fiscais Individuais

**Funcionalidade:** Registrar adições e reduções de base de cálculo por tributo

**Dados de Ajuste:**
- Tributo Alvo: PIS | COFINS | CSLL | IRPJ | IRPJ_ADICIONAL
- Tipo: ADICAO | REDUCAO
- Valor (R$)
- Descrição (breve)
- Justificativa / Memória (texto longo)
- Documento de Suporte (caminho ou referência - opcional)
- Data do Ajuste

**Operações:**
- ✓ Adicionar múltiplos ajustes no mesmo período
- ✓ Editar ajuste
- ✓ Deletar ajuste (apenas se sem apuração)
- ✓ Visualizar ajuste com justificativa
- ✓ Listar ajustes do lançamento

**Regras de Negócio:**
- Múltiplos ajustes por tributo na mesma competência são permitidos (são somados)
- Valor do ajuste deve ser > 0
- Ajuste pertence a 1 lançamento (empresa + obra + competência)
- Ao deletar lançamento, todos os ajustes também são deletados

---

### 2.3 Módulo de Apuração (Motor Fiscal)

#### 2.3.1 Cálculo de Impostos

**Funcionalidade:** Calcular impostos automaticamente com base em lançamentos e ajustes

**Tributos Calculados:**
- PIS (mensal)
- COFINS (mensal)
- CSLL (trimestral, com projeção mensal)
- IRPJ (trimestral, com projeção mensal)
- IRPJ Adicional (trimestral)
- ISS (mensal, por obra)

**Operações:**
- ✓ Calcular apuração para competência/obra (sob demanda)
- ✓ Recalcular apuração (quando lançamento muda)
- ✓ Visualizar apuração com memória de cálculo
- ✓ Consolidar apuração (empresa inteira)
- ✓ Comparar períodos (mês vs mês anterior)

**Regras de Negócio:**
- Apuração é gerada automaticamente ao salvar lançamento
- Memória de cálculo é persistida (para auditoria)
- Consolidação soma todas as obras da empresa
- Não há limite de recálculos (é idempotente)

---

#### 2.3.2 Memória de Cálculo

**Funcionalidade:** Persistir e exibir passo a passo do cálculo

**Informações Armazenadas:**
- Receitas consideradas (bruta, tributável, etc)
- Base de cálculo (antes ajustes)
- Adições e reduções por tributo
- Base de cálculo (após ajustes)
- Alíquota aplicada
- Valor do imposto
- Data/hora de cálculo
- Versão do cálculo

**Operações:**
- ✓ Exportar memória em PDF (formatada, legível)
- ✓ Exibir memória na UI (expandível, detalhada)
- ✓ Comparar memória entre períodos

---

### 2.4 Módulo de Relatórios

#### 2.4.1 Relatórios Disponíveis

**Relatório 1: Memória de Cálculo por Obra**
- Escopo: Uma obra, um período
- Conteúdo: Receitas, bases, ajustes, impostos, vencimentos
- Formatos: PDF, XLSX

**Relatório 2: Memória de Cálculo Consolidada**
- Escopo: Uma empresa, um período (agregação de todas as obras)
- Conteúdo: Mesmo que acima, mas consolidado
- Formatos: PDF, XLSX (abas por obra)

**Relatório 3: Composição dos Tributos**
- Escopo: Período, visão por obra ou consolidada
- Conteúdo: Tabela com base, alíquota, valor para cada tributo
- Formatos: PDF, XLSX

**Relatório 4: Evolução Mensal**
- Escopo: 12 últimos meses
- Conteúdo: Série histórica de receitas, impostos e alíquotas efetivas
- Formatos: PDF, XLSX

**Relatório 5: Vencimentos**
- Escopo: Período (próximos 30/60/90 dias)
- Conteúdo: Tributo, valor, vencimento, status (pago/aberto/vencido)
- Formatos: PDF, XLSX

**Operações:**
- ✓ Filtrar por empresa, obra, competência, trimestre
- ✓ Gerar em PDF e XLSX
- ✓ Exportar para disco
- ✓ Imprimir diretamente

---

### 2.5 Módulo de Vencimentos e Guias

#### 2.5.1 Gestão de Vencimentos

**Funcionalidade:** Controlar datas de vencimento e status de pagamento de tributos

**Dados de Vencimento:**
- Tributo
- Competência
- Obra / Consolidada
- Valor
- Data de Vencimento (com base em regras parametrizáveis)
- Status: EM_ABERTO | PAGO | VENCIDO | CANCELADO | NAO_APLICAVEL
- Data de Pagamento (quando pago)
- Observações

**Operações:**
- ✓ Registrar pagamento de tributo
- ✓ Marcar como vencido (automático se data passou)
- ✓ Cancelar vencimento (se tributo não é devido)
- ✓ Listar vencimentos com filtros
- ✓ Dashboard com próximos vencimentos

**Regras de Negócio:**
- Vencimento é criado automaticamente ao finalizar apuração
- Status é atualizado automaticamente (se data vencimento passou = vencido)
- Cada tributo tem regra de vencimento parametrizável

---

#### 2.5.2 Guias de Recolhimento

**Funcionalidade:** Gerar demonstrativo de recolhimento (guia interna)

**Conteúdo da Guia:**
- Identificação (empresa, obra, competência)
- Tributo
- Base de cálculo
- Alíquota
- Valor a recolher
- Data de vencimento
- Código de receita (se parametrizado)
- Banco/Arrecadador (informativo)
- QR Code ou código de barras (opcional)

**Operações:**
- ✓ Gerar guia para tributo específico
- ✓ Gerar lote de guias (trimestre/mês)
- ✓ Exportar em PDF
- ✓ Imprimir
- ✓ Armazenar histórico

---

### 2.6 Módulo de Dashboard

#### 2.6.1 Painel Principal

**Funcionalidade:** Visualização consolidada da situação fiscal

**Componentes Principais:**
- **Filtros:** Competência, Empresa, Obra
- **KPIs:** 4 cards com métricas principais (receita, PIS+COFINS, IRPJ+CSLL, ISS)
- **Gráfico de Evolução:** Últimos 12 meses de receita e impostos
- **Resumo da Apuração:** Cards com valores de cada tributo (pago/pendente)
- **Tabela de Composição:** Base, alíquota, valor de cada tributo
- **Gráfico de Distribuição:** Pizza/Donut com % de cada tributo
- **Próximos Vencimentos:** Lista com status e dias para vencer
- **Ações Rápidas:** Botões (Gerar Guia, Exportar Relatório, Compartilhar)

**Operações:**
- ✓ Filtrar por competência e empresa
- ✓ Buscar por obra específica
- ✓ Refresh automático de dados
- ✓ Drill-down (clicar em KPI = detalhe)
- ✓ Exportar dashboard como PDF/PNG

---

## 3. FLUXOS PRINCIPAIS

### 3.1 Fluxo: Cadastro Completo de Empresa e Obras

```
Usuário
  → [Dashboard]
    → Clica "Novo" ou "Gestão de Empresas"
    → [EmpresasPage]
      → Clica "Nova Empresa"
      → [FormEmpresa]
        → Preenche dados (CNPJ, razão social, etc)
        → Clica "Salvar"
      → Empresa criada, carrega percentuais padrão
      → [EmpresasPage] lista empresa
      → Clica "Adicionar Obra"
      → [FormObra]
        → Preenche dados (código, nome, localização, etc)
        → Clica "Salvar"
      → Obra vinculada à empresa
→ Fim do fluxo
```

---

### 3.2 Fluxo: Lançamento e Apuração Mensal

```
Usuário
  → [Dashboard]
    → Seleciona Empresa e Competência
    → Clica "Novo Lançamento"
    → [ApuracaoEntradaPage]
      → Seleciona Obra
      → Preenche receitas (bruta, operacional, devoluções)
      → Opcional: Duplicar mês anterior
      → Adiciona ajustes fiscais (PIS, COFINS, etc)
      → Clica "Salvar"
    → Lançamento persistido
    → Sistema calcula automaticamente:
      * Base de cálculo (receita + ajustes)
      * PIS, COFINS, CSLL, IRPJ, ISS
      * Memória detalhada
    → [Dashboard] exibe apuração atualizada
→ Fim do fluxo
```

---

### 3.3 Fluxo: Geração de Relatório

```
Usuário
  → [Dashboard]
    → Clica "Exportar Relatório"
    → [RelatoriosPage]
      → Seleciona tipo (memória cálculo, composição, evolução)
      → Seleciona filtros (empresa, obra, período)
      → Clica "Gerar"
    → Sistema compila dados, formata em PDF/XLSX
    → Oferece download ou impressão
    → Relatório persistido no histórico
→ Fim do fluxo
```

---

### 3.4 Fluxo: Marcação de Pagamento

```
Usuário
  → [Dashboard]
    → Visualiza "Próximos Vencimentos"
    → Clica em vencimento específico
    → [DialogPagamento]
      → Preenche data e valor pago
      → Clica "Confirmar Pagamento"
    → Status muda de EM_ABERTO para PAGO
    → Dashboard atualiza (% pago aumenta)
→ Fim do fluxo
```

---

## 4. DEFINIÇÃO DE PRONTO (DoD - Definition of Done)

Uma funcionalidade está "pronta" quando:

- ✓ Código implementado e testado
- ✓ Testes unitários passam (>80% cobertura para fiscalidade)
- ✓ Testes de integração entre UI ↔ Service ↔ Repository ↔ DB
- ✓ Sem TODOs, FIXMEs ou placeholders no código
- ✓ Sem imports órfãos ou circularidades
- ✓ Documentação atualizada (docstrings, README)
- ✓ Validações funcionam (campos obrigatórios, tipos, ranges)
- ✓ Mensagens de erro claras ao usuário
- ✓ Dados persistem corretamente no banco
- ✓ Auditoria registra ações (criar, editar, deletar)
- ✓ Performance aceitável (<1s para operações comuns)
- ✓ UI é responsiva e segue padrão visual
- ✓ Fluxo de ponta a ponta (entrada → processamento → saída) funciona

---

## 5. MATRIZ DE CASOS DE USO

| Caso de Uso | Ator | Pré-Condição | Pós-Condição | Prioridade |
|-------------|------|--------------|--------------|-----------|
| Criar Empresa | Contador | Nenhuma | Empresa no banco, padrões carregados | Alta |
| Criar Obra | Contador | Empresa existe | Obra vinculada à empresa | Alta |
| Lançar Receita | Contador | Obra ativa existe | Lançamento no banco | Alta |
| Adicionar Ajuste | Contador | Lançamento existe | Ajuste persistido, apuração recalculada | Alta |
| Visualizar Apuração | Gestor | Lançamento existe | Tela exibe cálculos e memória | Alta |
| Gerar Relatório | Contador | Período com dados | Arquivo PDF/XLSX gerado | Alta |
| Marcar Pagamento | Contador | Vencimento existe | Status atualizado | Média |
| Gerar Guia | Contador | Apuração finalizada | PDF disponível para download | Média |
| Editar Empresa | Contador | Empresa existe | Dados atualizados | Média |
| Inativar Empresa | Contador | Empresa sem movimentação | Status = inativa | Baixa |

---

## 6. REQUISITOS NÃO FUNCIONAIS

### 6.1 Performance
- Listar empresas: < 500ms
- Calcular apuração: < 2s
- Gerar relatório: < 5s
- Dashboard carregar: < 1s

### 6.2 Segurança
- Validação de entrada em 100% dos formulários
- Sem SQL injection (usar ORM)
- Sem hard-coded secrets

### 6.3 Usabilidade
- Interface intuitiva em pt-BR
- Atalhos de teclado principais
- Mensagens de erro claras
- Help/tooltips em campos complexos

### 6.4 Confiabilidade
- Banco sempre consistente (constraints integridade)
- Transações atômicas para operações críticas
- Backup automático sugerido (fora do escopo da app)

### 6.5 Manutenibilidade
- Código limpo, nomes descritivos
- Documentação técnica (ARQUITETURA.md, docstrings)
- Testes cobrindo 80%+ da lógica crítica

---

## 7. COMPATIBILIDADE COM CONTEXTO OPERACIONAL

Este documento respeita todas as restrições do [CONTEXTO_OPERACIONAL.md](CONTEXTO_OPERACIONAL.md):

- ✓ Sem web framework (desktop apenas)
- ✓ Stack: Python + PySide6 + SQLAlchemy + SQLite
- ✓ Interface em pt-BR com moeda BRL e datas brasileiras
- ✓ Suporta empresa → obra → lançamento → apuração → relatório
- ✓ Ajustes individuais por tributo (PIS, COFINS, CSLL, IRPJ, IRPJ Adicional)
- ✓ Memória de cálculo detalhada e persistida
- ✓ Relatórios por obra e consolidados
- ✓ Dashboard com fidelidade visual à referência
- ✓ Arquitetura limpa: UI → Services → Repositories → Models → DB

---

**Versão:** 1.0.0  
**Próxima Revisão:** Após implementação Etapa 3

# CONTEXTO OPERACIONAL - Contabase Digital

**Projeto:** Contabase Digital - Lucro Presumido  
**Data de Criação:** 24 de abril de 2026  
**Versão:** 1.0.0

---

## 1. Stack Obrigatória

- **Linguagem:** Python 3.10+
- **Desktop Framework:** PySide6
- **ORM:** SQLAlchemy 2.x
- **Banco de Dados:** SQLite
- **Tipos:** typing, dataclasses ou pydantic conforme necessário
- **Moeda:** `Decimal` para dinheiro e percentuais
- **Idioma de Interface:** Português-Brasil (pt-BR)
- **Padrão de Data/Moeda:** Brasileiro (DD/MM/YYYY, R$ X.XXX,XX)

## 2. Estrutura de Banco de Dados

- **Localização:** `banco_de_dados/contabase_digital.db`
- **Restrição:** Dentro da pasta `banco_de_dados`, deve existir **apenas 1 arquivo**: o banco SQLite
- **Nenhum arquivo temporário, log ou cache deve ocupar essa pasta**

## 3. Regras Obrigatórias de Implementação

### 3.1 Stack e Arquitetura
- ✗ **Não trocar a stack** (Python + PySide6 + SQLAlchemy + SQLite)
- ✗ **Não usar web framework**
- ✓ **Usar arquitetura limpa e simples, mas prática**
- ✓ **Manter o sistema funcional a cada etapa**
- ✓ **Desacoplamento entre camadas:** UI → Services → Repositories → Models → DB

### 3.2 Código-Fonte
- ✗ **Não deixar TODO, FIXME ou "implementar depois"**
- ✗ **Não criar telas placeholder**
- ✓ **Usar type hints** em todas as funções
- ✓ **Arredondamento financeiro consistente** (sempre ROUND_HALF_UP com 2 casas)
- ✓ **Dataclasses ou Pydantic** para modelos de dados
- ✓ **Reutilizar componentes** ao máximo para evitar duplicidade

### 3.3 Compatibilidade
- ✓ **Preservar compatibilidade** ao alterar algo
- ✓ **Sem imports órfãos** ou arquivos mortos
- ✓ **Nomes consistentes** e sem circularidades
- ✓ **Integridade referencial** entre UI, services, repositories, models e banco

### 3.4 Qualidade e Testes
- ✓ **Cada etapa deve ser testável** com instruções objetivas
- ✓ **Testes unitários** para lógica fiscal e cálculos
- ✓ **Testes de integração** entre banco e services
- ✗ **Zero simulação** ou dados fake após a etapa ser "fechada"

## 4. Funcionalidades Obrigatórias do Sistema

### 4.1 Cadastros Mestres
- **Empresas:** CNPJ, razão social, endereço, contato, perfil fiscal
- **Obras:** Código interno, nome, localização, UF, atividade, período, perfil tributário
- Vinculação: Cada obra pertence a uma empresa
- Suporte a inativação lógica (não deletar se houver dados fiscais)

### 4.2 Lançamentos Fiscais
- **Competência:** Mês e ano (MM/YYYY)
- **Receitas:** Bruta, operacionais, devoluções/cancelamentos, tributável
- **Ajustes Individuais:** Adição ou redução de base por tributo
  - **Tributos:** PIS, COFINS, CSLL, IRPJ, IRPJ Adicional
- **Persistência Normalizada:** Cada ajuste é um registro separado
- **Memória de Cálculo:** Armazenar base antes/depois dos ajustes

### 4.3 Apuração dos Tributos
- **Periodicidade:**
  - PIS e COFINS: Mensal
  - IRPJ, CSLL: Trimestral (mas com projeção mensal)
  - ISS: Por obra, conforme alíquota configurada
- **Consolidação:** Por obra e consolidada (empresa inteira)
- **Memória Detalhada:** Persistir cálculos passo a passo

### 4.4 Relatórios
- **Visão por Obra:** Filtro por período, empresa e obra
- **Visão Consolidada:** Agregação de todas as obras da empresa
- **Formatos:** PDF e XLSX
- **Memória de Cálculo:** Exibição legível, profissional

### 4.5 Dashboard (Fidelidade Máxima à Referência)
- Layout conforme imagem: `app/ui/assets/dashboard_referencia.png`
- **Componentes Obrigatórios:**
  - Sidebar escura com navegação
  - Topbar com filtro de competência, empresa, busca, notificações
  - 4 cards KPI
  - Gráfico de evolução mensal
  - Resumo da apuração
  - Tabela de composição dos tributos
  - Gráfico de distribuição dos tributos
  - Card de próximos vencimentos
  - Faixa de ações (Gerar Guia, Exportar, Compartilhar)
- **Tema:** Dark azul petróleo, cards em azul marinho, destaques em azul vibrante/roxo/ciano
- **Responsividade:** Manter proporções mesmo com redimensionamento

## 5. Cláusula Permanente de Revisão Obrigatória

**Antes de encerrar qualquer resposta futura deste projeto, faça uma revisão crítica e confirme:**

- [ ] Não houve duplicidade de classes, serviços, models, migrations, seeds, rotas de navegação, widgets ou helpers
- [ ] Não ficaram imports quebrados, arquivos órfãos, nomes inconsistentes ou circularidades evitáveis
- [ ] Não ficaram regras rasas, incompletas, simuladas ou placeholders disfarçados de implementação final
- [ ] A integridade entre UI, services, repositories, models e banco foi preservada
- [ ] Os arquivos criados continuam compatíveis com o restante do projeto
- [ ] A etapa entregue está testável e com instruções objetivas de validação

## 6. Regras Fiscais - Lucro Presumido

### 6.1 Presunção de Lucro (Será detalhado na etapa 2)
- Por categoria de receita (alíquotas diferentes conforme atividade)
- Aplicação mensal com consolidação trimestral

### 6.2 Ajustes Individuais (Detalhado na etapa 4)
- Adição ou redução de base
- Suportados para: PIS, COFINS, CSLL, IRPJ, IRPJ Adicional
- Persistência individual com justificativa

### 6.3 Apuração de Impostos (Implementado na etapa 7)
- Cálculos com `Decimal`
- Parametrização via banco (não hardcoded)
- Versionamento simples da apuração

## 7. Roadmap em Etapas

| Etapa | Objetivo | Entrega Principal |
|-------|----------|-------------------|
| 1 | Contexto e Estrutura | Este documento + Estrutura de pastas |
| 2 | Documentação Mestra | Especificação, Arquitetura, Regras Fiscais, Dashboard Ref, Roadmap |
| 3 | Bootstrap do Projeto | main.py executável, estrutura, tema dark, navegação base |
| 4 | Banco de Dados | Models, repositories, seed, integridade referencial |
| 5 | CRUD Empresas/Obras | EmpresasPage funcional, validações, auditoria |
| 6 | Lançamentos Fiscais | ApuracaoEntradaPage, ajustes individuais, persistência |
| 7 | Motor Fiscal | Cálculos reais, memória de cálculo, testes unitários |
| 8 | Dashboard Visual | Fidelidade máxima à referência |
| 9 | Dashboard + Dados Reais | Integração com banco, filtros, KPIs |
| 10 | Relatórios | PDF e XLSX, memória de cálculo, exportação |
| 11 | Guias/Vencimentos | GuiasPage, demonstrativo de recolhimento, status |
| 12 | Acabamento Final | Testes, testes integração, empacotamento, README |
| 13 | Correção Emergencial (conforme necessário) | Correções cirúrgicas sem reescrever |

## 8. Comandos Esperados

```bash
# Ambiente
python -m venv .venv
.venv\Scripts\activate

# Dependências
pip install -r requirements.txt

# Execução
python main.py

# Testes
pytest -q
```

## 9. Como Reutilizar Este Contexto

Este arquivo **é um contrato permanente do projeto**. Nas próximas etapas:

1. **Leia este arquivo antes de começar a implementação**
2. **Use como checklist ao final de cada etapa**
3. **Qualquer conflito entre etapa e este documento: este documento prevalece**
4. **Se precisar ajustar alguma regra, faça aqui e documente o motivo**
5. **Mantenha este arquivo sincronizado com a realidade do projeto**

---

**Status:** Ativo desde 24 de abril de 2026

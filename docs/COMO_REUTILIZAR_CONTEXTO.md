# COMO REUTILIZAR ESTE CONTEXTO NAS PRÓXIMAS ETAPAS

## Propósito

Este documento orienta como o **CONTEXTO_OPERACIONAL.md** deve ser utilizado nas etapas 2 a 13 do projeto Contabase Digital.

---

## Para a Etapa 2 - Especificação Mestra

**O que fazer:**
1. Ler `docs/CONTEXTO_OPERACIONAL.md` completamente
2. Usar seção "Funcionalidades Obrigatórias" como checklist
3. Preparar 5 documentos mestres respeitando as regras:
   - `docs/ESPECIFICACAO_FUNCIONAL.md`
   - `docs/ARQUITETURA.md`
   - `docs/REGRAS_FISCAIS.md`
   - `docs/UI_DASHBOARD_REFERENCIA.md`
   - `docs/ROADMAP_IMPLEMENTACAO.md`

**Validação:**
- [ ] Nenhuma contradição entre os 5 documentos
- [ ] Regras de seção 3 estão respeitadas na especificação
- [ ] Stack (seção 1) não foi alterada
- [ ] Todos os requisitos fiscais (seção 6) estão cobertos

---

## Para a Etapa 3 - Bootstrap do Projeto

**O que fazer:**
1. Ler `docs/CONTEXTO_OPERACIONAL.md` novamente
2. Executar comandos da seção 8 (Comandos Esperados):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Criar `main.py` que executa sem erro
4. Estrutura deve bater com seção 2 (Estrutura de Banco de Dados) e README (Estrutura do Projeto)

**Validação:**
- [ ] `python main.py` sobe sem erro
- [ ] Banco é criado em `banco_de_dados/contabase_digital.db` (seção 2)
- [ ] Nenhum arquivo extra em `banco_de_dados/`
- [ ] Navbar/sidebar funcionam (preparação para etapa 8)

---

## Para a Etapa 4 - Modelo de Dados e Banco

**O que fazer:**
1. Ler seção 4.1 até 4.5 (Funcionalidades Obrigatórias)
2. Modelar banco respeitando:
   - Seção 3.3: Compatibilidade e integridade
   - Seção 4: Estrutura de dados esperada
   - Seção 6: Regras fiscais (ainda conceitualmente)
3. Criar models, repositories, session manager
4. Seed idempotente (sem duplicação)

**Validação:**
- [ ] Tabelas do seção 4.2 existem
- [ ] Integridade referencial (empresa → obra → lançamento → apuração)
- [ ] `Decimal` para valores monetários (seção 3.2)
- [ ] Seed roda duas vezes sem duplicar
- [ ] Testes básicos passam: `pytest -q`

---

## Para a Etapa 5 - CRUD Empresas/Obras

**O que fazer:**
1. Reler seção 4.1 (Cadastros Mestres)
2. Implementar `EmpresasPage` com:
   - CRUD: criar, editar, inativar, deletar
   - Validação de CNPJ (seção 4.1)
   - Bloqueio de exclusão se houver dados (integridade referencial)
   - Auditoria básica (seção 3.4)

**Validação:**
- [ ] Fluxo completo: criar empresa → adicionar obras → editar → inativar
- [ ] Não permite deletar empresa com lançamentos
- [ ] UI segue padrão dark da etapa 3
- [ ] Sem TODOs no código (seção 3.2)

---

## Para a Etapa 6 - Lançamentos Fiscais

**O que fazer:**
1. Reler seção 4.3 (Lançamentos Fiscais)
2. Criar `ApuracaoEntradaPage` com:
   - Filtro por empresa, obra, competência
   - Campos de receita (seção 4.3)
   - Múltiplos ajustes por tributo
   - Persistência normalizada (cada ajuste = registro)

**Validação:**
- [ ] Pode adicionar 5 ajustes no mesmo período
- [ ] Base original ≠ base ajustada (clareza visual)
- [ ] Duplicação de mês anterior funciona sem erros
- [ ] Dados persistem corretamente no banco

---

## Para a Etapa 7 - Motor Fiscal

**O que fazer:**
1. Reler seção 4.4 (Apuração dos Tributos) e seção 6 (Regras Fiscais)
2. Implementar calculadores para:
   - PIS/COFINS (mensal)
   - IRPJ/CSLL (trimestral com projeção mensal)
   - ISS (por obra)
3. Usar `Decimal` em todos os cálculos
4. Persistir memória de cálculo

**Validação:**
- [ ] Testes unitários para cada tributo
- [ ] Adicional de IRPJ calcula corretamente no trimestre
- [ ] Consolidação (várias obras) não duplica
- [ ] Memória persistida = resultado exibido

---

## Para a Etapa 8 - Dashboard Visual

**O que fazer:**
1. Ter imagem de referência em `app/ui/assets/dashboard_referencia.png`
2. Implementar layout com fidelidade máxima (seção 4.5)
3. Cards, gráficos, cores conforme referência
4. Usar dados mockados apenas nesta etapa

**Validação:**
- [ ] Screenshot vs imagem de referência (mesma estrutura)
- [ ] Cores, espaçamento, arredondamento = referência
- [ ] Zero componentes genéricos/feios
- [ ] Responsividade mantém proporções

---

## Para a Etapa 9 - Dashboard com Dados Reais

**O what fazer:**
1. Conectar dashboard à base de dados real
2. Remover todos os mocks (seção 3.2: "sem simulação")
3. Filtros funcionais (empresa, competência, obra)

**Validação:**
- [ ] Zero dados fake após etapa 9
- [ ] Números da dashboard = números do banco
- [ ] Filtros não se contradizem
- [ ] Projeção mensal vs fechamento trimestral explícito

---

## Para a Etapa 10 - Relatórios

**O que fazer:**
1. Criar `RelatoriosPage` e exportação PDF/XLSX
2. Conteúdo = memória de cálculo (seção 4.4)
3. Botão "Exportar" da dashboard chama isso

**Validação:**
- [ ] Relatório PDF legível e profissional
- [ ] PDF = XLSX (mesmos dados)
- [ ] Consolidado soma sem duplicar
- [ ] Números = banco

---

## Para a Etapa 11 - Guias/Vencimentos

**O que fazer:**
1. Criar `GuiasPage` parametrizável
2. Gerar demonstrativo de recolhimento (PDF)
3. Status: aberto, pago, vencido, não aplicável
4. Conectar ao card de vencimentos da dashboard

**Validação:**
- [ ] Regras de vencimento não são hardcoded
- [ ] Status sincronizado entre página, dashboard, banco
- [ ] PDF tem base, alíquota, valor, vencimento, código receita

---

## Para a Etapa 12 - Acabamento Final

**O que fazer:**
1. Revisar TUDO contra `CONTEXTO_OPERACIONAL.md`
2. Rodar checklist de duplicidade, imports, placeholders
3. Incluir dados seed bonitos
4. Preparar empacotamento PyInstaller
5. Testes de integração

**Validação:**
- [ ] `python main.py` funciona
- [ ] `pytest` passa
- [ ] Dashboard visual idêntica à referência
- [ ] Zero TODOs, FIXMEs, dados fake

---

## Para a Etapa 13 - Correção Emergencial (Se Necessário)

**Quando usar:**
- Se houver desvio real do que foi especificado
- Se algo quebrar entre etapas
- Se faltou cobertura de caso de borda

**O que fazer:**
1. Identificar exatamente qual regra de `CONTEXTO_OPERACIONAL.md` foi violada
2. Corrigir cirurgicamente
3. Não reescrever código inteiro
4. Documentar causa raiz

**Validação:**
- [ ] Causa raiz identificada
- [ ] Nenhuma regressão em módulos estáveis
- [ ] Teste valida correção

---

## Template de Prompt para Cada Etapa

Quando pedir ajuda (próximas etapas), use este template:

```
Etapa [N] - [Nome]

Contexto:
[Releia CONTEXTO_OPERACIONAL.md seção X.Y]

Tarefa:
[O que precisa fazer]

Validação esperada:
- [ ] Checklist item 1
- [ ] Checklist item 2
```

---

## Checklist Final de Cada Etapa

Ao final de QUALQUER etapa, valide:

**Arquitetura:**
- [ ] Stack não foi alterado (seção 1)
- [ ] Sem TODOs/FIXMEs (seção 3.2)
- [ ] Sem duplicidade (seção 5)
- [ ] Sem imports órfãos (seção 3.3)

**Dados:**
- [ ] `Decimal` usado para moeda (seção 3.2)
- [ ] Banco em `banco_de_dados/contabase_digital.db` (seção 2)
- [ ] Nada extra naquela pasta (seção 2)
- [ ] Integridade referencial (seção 3.3)

**Documentação:**
- [ ] README.md atualizado
- [ ] Passos de teste documentados
- [ ] Mudanças em CONTEXTO se necessário

**Funcionalidade:**
- [ ] Tudo funciona ponta a ponta
- [ ] Zero simulação/fake (seção 3.4)
- [ ] Pronto para próxima etapa

---

**Este documento foi criado em 24 de abril de 2026**  
**Use-o como referência permanente do projeto**

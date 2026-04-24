# VALIDAÇÃO DE COERÊNCIA - ETAPA 2

**Data:** 24 de abril de 2026  
**Revisão:** Etapa 2 Conclusão

---

## CHECKLIST DE REVISÃO OBRIGATÓRIA

### ✅ 1. Conflitos entre Documentação Funcional, Arquitetura, Regras Fiscais e Roadmap

**Validação:**

| Documento | Tema | Coerência | Status |
|-----------|------|-----------|--------|
| ESPECIFICACAO_FUNCIONAL | Fluxo empresa→obra→lançamento→apuração→relatório | Define o QUÊ | ✅ OK |
| ARQUITETURA | 3 camadas (UI → Service → Repo → DB) | Define o COMO | ✅ OK |
| REGRAS_FISCAIS | Fórmulas fiscais (PIS, COFINS, IRPJ, CSLL, ISS) | Define o NEGÓCIO | ✅ OK |
| UI_DASHBOARD | Layout visual com 4 KPIs, gráficos, etc | Define o VISUAL | ✅ OK |
| ROADMAP | 12 etapas sequenciais com dependências | Define a SEQUÊNCIA | ✅ OK |

**Conclusão:** ✅ Sem conflitos detectados. Documentos complementam-se.

---

### ✅ 2. Contradições entre Periodicidade Mensal e Trimestral

**Validação:**

**REGRAS_FISCAIS.md:**
```
PIS:         Mensal      (0,65%)
COFINS:      Mensal      (3,0%)
CSLL:        Trimestral  (9%)
IRPJ:        Trimestral  (15%) + projeção mensal
IRPJ Adic.:  Trimestral  (10% se base > R$ 20k)
ISS:         Mensal      (por obra, alíquota customizável)
```

**ESPECIFICACAO_FUNCIONAL.md seção 2.3:**
```
- PIS e COFINS: Mensalmente apurados
- IRPJ, CSLL: Trimestral (com projeção mensal)
- ISS: Mensalmente por obra
```

**ROADMAP_IMPLEMENTACAO.md etapa 7:**
```
"IRPJ e CSLL devem suportar apuração trimestral correta, 
 mas o sistema deve também mostrar projeção mensal"
```

**Conclusão:** ✅ Sem contradições. Todos documentos alinhados:
- Mensal: PIS, COFINS, ISS (sempre)
- Trimestral: IRPJ, CSLL (com projeção mensal visível)

---

### ✅ 3. Modelagem Suporta Fluxo Completo

**Validação:**

**Fluxo esperado:** Empresa → Obra → Lançamento → Apuração → Consolidação

**Modelos em ARQUITETURA.md seção 5 (ER):**

```
Empresa (1) ──────────< (n) Obra
Obra (1) ────────────< (n) LancamentoFiscal
LancamentoFiscal (1) ──< (n) AjusteFiscal
Apuracao (1) ────────< (n) ApuracaoItem (memória)
```

**Campos críticos:**

| Modelo | Campos | Suporta |
|--------|--------|---------|
| Empresa | id, cnpj, status | ✅ Filtrar empresas |
| Obra | id, empresa_id, aliquota_iss | ✅ Agrupar por obra |
| LancamentoFiscal | id, obra_id, competencia (MM/YYYY) | ✅ Agrupar por competência |
| AjusteFiscal | id, lancamento_id, tributo (enum), valor | ✅ Ajustes por tributo |
| Apuracao | id, obra_id (NULL se consolidada), empresa_id | ✅ Por obra OU consolidada |
| ApuracaoItem | id, apuracao_id, passo (seq) | ✅ Memória detalhada |

**Conclusão:** ✅ Modelagem suporta fluxo completo, incluindo consolidação.

---

### ✅ 4. Requisitos Sem Vaguidade (Critério de Aceite Claro)

**Validação:**

**Exemplo 1: ESPECIFICACAO_FUNCIONAL seção 2.1.1**

```
Dado: "Criar empresa"
Quando: Usuário preenche CNPJ, razão social, endereço, contato
Então: 
  ✓ Empresa salva no banco
  ✓ CNPJ é validado (formato)
  ✓ CNPJ é único
  ✓ Percentuais padrão carregados
  ✓ Auditoria registra ação
```

**Status:** ✅ Claro e testável.

---

**Exemplo 2: REGRAS_FISCAIS seção 3**

```
Dado: Receita bruta R$ 50.000
Quando: Empresa com presunção IRPJ 8%
Então:
  ✓ Base presumida = R$ 50.000 * 8% = R$ 4.000
  ✓ IRPJ = R$ 4.000 * 15% = R$ 600
  ✓ Se adicionar ajuste +R$ 1.000
  ✓ Nova base = R$ 5.000
  ✓ Novo IRPJ = R$ 750
```

**Status:** ✅ Numérico e verificável.

---

**Exemplo 3: ROADMAP seção 3, Etapa 5**

```
Criterio de Conclusão:
[ ] CRUD completo funcionando
[ ] Validações ativas
[ ] Auditoria registrando ações
[ ] UI responsiva e intuitiva
[ ] Sem exclusão física com dados vinculados
[ ] Testes passam (CRUD, validação, bloqueio exclusão)
[ ] Fluxo completo testável manualmente
```

**Status:** ✅ Todos são verificáveis/testáveis.

**Conclusão:** ✅ Sem vaguidades. Todos os requisitos têm critério de aceite claro.

---

### ✅ 5. Decisões de Alto Risco com Mitigação Registrada

**Validação:**

| Decisão | Documento | Risco | Mitigação |
|---------|-----------|-------|-----------|
| 3 Camadas (UI→Service→Repo→DB) | ARQUITETURA 9.1 | Overhead abstração | Templates/generators |
| Decimal (não Float) | ARQUITETURA 9.2 | Infiltração float | Type hints + testes |
| Apuração recalculada (não incremental) | ARQUITETURA 9.3 | Performance | Índices BD, cache |
| SQLite local (não servidor) | ARQUITETURA 9.4 | Contenção arquivo | Single-user design |
| Ajustes individuais por tributo | REGRAS_FISCAIS 7 | Complexidade | Normalização BD clara |
| Consolidação somando obras | REGRAS_FISCAIS 8 | Double counting | Testes específicos |
| Periodicidade mensal + trimestral | REGRAS_FISCAIS 2.3/2.4 | Confusão usuário | UI diferencia (projeção vs fechamento) |

**Conclusão:** ✅ Todas as decisões de risco estão documentadas com mitigação.

---

### ✅ 6. Compatibilidade com CONTEXTO_OPERACIONAL.md

**Validação:**

Todos os 5 documentos respeitam:

✅ Stack obrigatória (Python + PySide6 + SQLAlchemy + SQLite)  
✅ Banco em `banco_de_dados/` (apenas .db)  
✅ Sem web framework  
✅ Interface pt-BR  
✅ Decimal para moeda  
✅ Sem TODO/FIXME/placeholder  
✅ Arquitetura limpa (3 camadas)  
✅ Suporta empresa→obra→lançamento→apuração  
✅ Ajustes para 5 tributos (PIS, COFINS, CSLL, IRPJ, IRPJ_ADICIONAL)  
✅ Memória de cálculo detalhada  
✅ Relatórios por obra + consolidada  
✅ Dashboard fiel à referência  

**Conclusão:** ✅ 100% compatível.

---

## RESUMO DE VALIDAÇÃO

| Critério | Status | Observação |
|----------|--------|-----------|
| Sem conflitos entre documentos | ✅ PASS | Complementam-se bem |
| Sem contradições periodicidade | ✅ PASS | Mensal/Trimestral claro |
| Modelagem suporta fluxo | ✅ PASS | ER coerente com fluxo |
| Requisitos sem vaguidades | ✅ PASS | Todos com critério aceite |
| Riscos identificados/mitigados | ✅ PASS | 7 riscos altos documentados |
| Compatibilidade CONTEXTO | ✅ PASS | 100% alinhado |

---

## CONCLUSÃO

✅ **ETAPA 2 VALIDADA E APROVADA PARA IMPLEMENTAÇÃO**

Todos os 5 documentos:
1. ESPECIFICACAO_FUNCIONAL.md
2. ARQUITETURA.md
3. REGRAS_FISCAIS.md
4. UI_DASHBOARD_REFERENCIA.md
5. ROADMAP_IMPLEMENTACAO.md

...são **coerentes**, **sem contradições**, **bem documentados** e **prontos para servir como contrato de implementação nas etapas 3-12**.

Próxima etapa: **Etapa 3 - Bootstrap do Projeto**

---

**Validado em:** 24 de abril de 2026  
**Revisor:** Etapa 2 Checklist Automático

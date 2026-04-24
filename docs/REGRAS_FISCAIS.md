# REGRAS FISCAIS - Lucro Presumido

**Data:** 24 de abril de 2026  
**Versão:** 1.0.0  
**Status:** Aprovado para Etapa 2  
**Escopo:** Lucro Presumido (Decreto nº 3.000/99)

---

## 1. VISÃO GERAL

O **Lucro Presumido** é um sistema de apuração de IRPJ e CSLL onde:

- ✓ O lucro é **presumido** (fixo %) em cima da receita, conforme atividade
- ✓ PIS e COFINS são apurados **mensalmente** no regime cumulativo
- ✓ IRPJ e CSLL são apurados por **fechamento trimestral** (com projeção mensal gerencial)
- ✓ ISS é apurado **mensalmente** por obra (conforme alíquota local)
- ✓ Ajustes individuais permitidos (adição/redução de base)

---

## 2. PRESUNÇÃO DE LUCRO (IRPJ e CSLL)

### 2.1 Tabela de Percentuais de Presunção por Atividade

| Atividade | IRPJ % | CSLL % | Código | Obs |
|-----------|--------|--------|--------|-----|
| Comércio | 8% | 12% | COM | Padrão |
| Serviços | 16% | 12% | SRV | Inclui profissionais liberais |
| Construção Civil | 8% | 12% | CCL | Obras, incorporação |
| Agropecuária | 8% | 12% | AGR | Produção, criação |
| Transporte | 8% | 12% | TRP | Ônibus, caminhão, taxi |
| Intermediação | 8% | 12% | INT | Corretagem, representação |

**Regra:** O sistema deve permitir **editar percentuais** por empresa (alguns clientes têm cenários especiais).

---

### 2.2 Fórmula de Cálculo: IRPJ e CSLL Presumidos

#### Base Presumida (antes ajustes):

```
base_presumida_mensal = 
    receita_categoria_1 * percentual_presuncao_1 +
    receita_categoria_2 * percentual_presuncao_2 +
    ... +
    receita_categoria_n * percentual_presuncao_n
```

**Regra:** Cada receita recebe o percentual de presunção de sua categoria.

#### Ajustes à Base:

```
base_ajustada = base_presumida + adicoes_fiscais - reducoes_fiscais
```

**Condição:** `base_ajustada >= 0` (máximo zero, não negativo)

#### Projeção Mensal (gerencial):

```
irpj_mes = base_ajustada * aliquota_irpj_mensal (15%)
csll_mes = base_ajustada * aliquota_csll_mensal (9%)
```

**Regra:** A projeção mensal é informativa para acompanhamento; o recolhimento no Lucro Presumido segue o fechamento trimestral.

---

### 2.3 Cálculo Trimestral (IRPJ e CSLL)

No Lucro Presumido, considerar **apuração trimestral** para fechamento fiscal:

#### Trimestres (fixos no calendário):

| Trimestre | Meses | Vencimento |
|-----------|-------|-----------|
| 1º | Jan, Fev, Mar | 30 abr |
| 2º | Abr, Mai, Jun | 31 jul |
| 3º | Jul, Ago, Set | 31 out |
| 4º | Out, Nov, Dez | 31 dez |

#### Base Trimestral:

```
base_trimestre = 
    (base_mes_1 + base_mes_2 + base_mes_3) / 3 * 3
    = soma das 3 bases mensais
```

**Regra:** A base trimestral é a soma das 3 bases mensais (não média).

#### IRPJ Trimestral:

```
irpj_trimestre = base_trimestre * 15%
```

#### CSLL Trimestral:

```
csll_trimestre = base_trimestre * 9%
```

#### IRPJ Adicional (Trimestral):

```
Se base_trimestre > limite_adicional_trimestre (R$ 20.000):
    adicional = (base_trimestre - 20.000) * 10%
Senão:
    adicional = 0
```

**Regra:** IRPJ Adicional só incide quando base trimestral ultrapassa R$ 20.000.

---

## 3. PIS (Programa de Integração Social)

### 3.1 Periodicidade
- ✓ **Mensal** (obrigatório)
- Alíquota padrão no Lucro Presumido (regime cumulativo): **0,65%**

### 3.2 Base de Cálculo

```
receita_tributavel_pis = 
    receita_bruta + outras_receitas_operacionais 
    - devoluções - cancelamentos - descontos_incondicionais
```

**Regra:** Mesma base que COFINS, mas taxas diferentes.

### 3.3 Fórmula de Cálculo

```
base_pis_bruta = receita_tributavel_pis

base_pis = 
    max(0, base_pis_bruta + adicoes_pis - reducoes_pis)

pis_mensal = base_pis * 0.65%
```

**Condição:** Base não pode ser negativa.

### 3.4 Ajustes Permitidos

| Tipo | Exemplo | Impacto |
|------|---------|--------|
| Adição | Receita isenta não computada | Base ↑ |
| Redução | Despesa dedutível | Base ↓ |

---

## 4. COFINS (Contribuição para Financiamento da Seguridade Social)

### 4.1 Periodicidade
- ✓ **Mensal** (obrigatório)
- Alíquota padrão no Lucro Presumido (regime cumulativo): **3,0%**

### 4.2 Base de Cálculo

```
receita_tributavel_cofins = receita_tributavel_pis
(mesma base que PIS)
```

### 4.3 Fórmula de Cálculo

```
base_cofins_bruta = receita_tributavel_pis

base_cofins = 
    max(0, base_cofins_bruta + adicoes_cofins - reducoes_cofins)

cofins_mensal = base_cofins * 3.0%
```

### 4.4 Notas

- Como regra geral do Lucro Presumido, usar regime cumulativo (PIS 0,65% e COFINS 3,0%).
- Exceções legais (como regimes monofásicos, ST ou alíquota zero por produto) devem ser tratadas por parametrização específica em cadastro/regra fiscal, sem hardcode.

---

## 5. CSLL (Contribuição Social sobre Lucro Líquido)

### 5.1 Periodicidade

- ✓ **Trimestral** (regra de apuração no Lucro Presumido)
- ✓ **Mensal (projeção gerencial)** para acompanhamento interno

### 5.2 Base de Cálculo (Lucro Presumido)

```
base_csll = base_presumida_mensal + adicoes_csll - reducoes_csll
```

**Mesma base que IRPJ presumido.**

### 5.3 Alíquota

```
csll = base_csll * 9%
```

### 5.4 Apuração Trimestral

Mesma lógica do IRPJ trimestral (soma 3 meses).

---

## 6. ISS (Imposto Sobre Serviços)

### 6.1 Periodicidade

- ✓ **Mensal** (sempre, por obra)

### 6.2 Incidência

- ✓ Incide **apenas em receita de serviços** (não comércio)
- ✗ Não incide em devoluções/cancelamentos

### 6.3 Base de Cálculo

```
base_iss = receita_bruta_de_servicos
          (sem devoluções, sem cancelamentos)
```

### 6.4 Alíquota

```
aliquota_iss = aliquota_configurada_na_obra (2% a 5%)
               ou aliquota_parametrizada_por_tipo_servico
```

### 6.5 Fórmula de Cálculo

```
iss_mensal = base_iss * aliquota_iss
```

### 6.6 Particularidades

- ✓ ISS é **por obra** (cada obra pode ter alíquota diferente)
- ✓ ISS é **recolhido ao município** onde a obra está localizada
- ✓ No sistema: Consolidar ISS por municipio (se houver múltiplas obras em cidades diferentes)

---

## 7. AJUSTES FISCAIS INDIVIDUAIS

### 7.1 Definição

Ajustes são **adições ou reduções** de base de cálculo justificadas por situações específicas que não se enquadram na presunção padrão.

### 7.2 Tributos Ajustáveis

- ✓ PIS
- ✓ COFINS
- ✓ CSLL
- ✓ IRPJ
- ✓ IRPJ Adicional

**Nota:** ISS não possui ajuste neste sistema (alíquota é configurável na obra).

### 7.3 Tipos de Ajuste

| Tipo | Significado | Exemplo |
|------|-------------|---------|
| **ADICAO** | Soma à base | Receita esquecida, rendimento aplicação |
| **REDUCAO** | Subtrai da base | Despesa dedutível, incentivo fiscal |

### 7.4 Campos de Ajuste

```
{
  lançamento_id: int,
  tributo: enum [PIS, COFINS, CSLL, IRPJ, IRPJ_ADICIONAL],
  tipo: enum [ADICAO, REDUCAO],
  valor: Decimal,
  descricao: str (breve),
  justificativa: str (longa, memória),
  documento_ref: str (opcional, caminho ou nº)
}
```

### 7.5 Cálculo com Ajustes

```
base_ajustada = base_original 
              + soma(adicoes)
              - soma(reducoes)

imposto = max(0, base_ajustada) * aliquota
```

### 7.6 Exemplos de Ajustes Comuns

#### Adição:
- Bônus, comissões não inclusos na receita
- Rendimentos de aplicações
- Doações recebidas
- Indenizações

#### Redução:
- Deduções permitidas (combustível, seguros)
- Incentivos fiscais
- Crédito de impostos anteriores
- Compensação de prejuízos

---

## 8. CONSOLIDAÇÃO (Empresa Inteira)

### 8.1 Quando Consolidar

Quando empresa tem **múltiplas obras** e precisa visualizar apuração global:

```
imposto_empresa = imposto_obra_1 + imposto_obra_2 + ... + imposto_obra_n
```

### 8.2 Regra de Consolidação por Tributo

#### PIS, COFINS, CSLL:

```
Mensalmente consolidado:
valor_consolidado = soma(valor_mensal_de_cada_obra)
```

#### IRPJ Trimestral:

```
Trimestralmente consolidado:
base_trimestre_consolidada = soma(base_trimestre_de_cada_obra)
irpj_trimestre_consolidado = base_trimestre_consolidada * 15%
```

#### ISS:

```
iss_consolidado_por_municipio = soma(iss_de_cada_obra_no_municipio)

Se múltiplos municipios:
  → Gerar guia separada por município
```

### 8.3 Sem Double Counting

**Regra crítica:** Ao consolidar, não duplicar receitas.

```
❌ ERRADO: soma(receita_obra_1) + soma(receita_obra_2) = duplicata
✓ CERTO: receita_consolidada = soma(receita_por_obra)
         imposto = receita_consolidada * presunção
```

---

## 9. CRONOGRAMA DE APURAÇÃO E VENCIMENTO

### 9.1 Periodicidade por Tributo

| Tributo | Apuração | Vencimento | Órgão |
|---------|----------|-----------|-------|
| PIS | Mensal | 25º dia mês seguinte | RFB |
| COFINS | Mensal | 25º dia mês seguinte | RFB |
| IRPJ | Trimestral | 30º dia após trim | RFB |
| CSLL | Trimestral | 30º dia após trim | RFB |
| ISS | Mensal | 5º-25º (municipal) | Prefeitura |

### 9.2 Calendário de Vencimentos

#### PIS e COFINS:

```
Mês referência → Vencimento
Janeiro → 25 fevereiro
Fevereiro → 25 março
Março → 25 abril
... (padrão)
```

#### IRPJ e CSLL (Trimestral):

```
Trimestre → Vencimento
1º (jan-fev-mar) → 30 abril
2º (abr-mai-jun) → 31 julho
3º (jul-ago-set) → 31 outubro
4º (out-nov-dez) → 31 dezembro
```

#### ISS:

```
Conforme município (padrão Brasil: 5º dia útil)
Sistema permitirá configurar por município
```

---

## 10. PARAMETRIZAÇÃO OBRIGATÓRIA

O sistema **não deve hardcodar** nenhum desses valores:

| Parâmetro | Padrão | Tabela | Editável |
|-----------|--------|--------|----------|
| Alíquota PIS | 0.65% | parametros | Sim |
| Alíquota COFINS | 3.0% | parametros | Sim |
| Alíquota CSLL | 9% | parametros | Sim |
| Alíquota IRPJ | 15% | parametros | Sim |
| Alíquota Adicional IRPJ | 10% | parametros | Sim |
| Limite Adicional IRPJ | R$ 20.000 | parametros | Sim |
| Presunção por Atividade | Tabela | atividades | Sim |
| Alíquota ISS por Obra | Configurável | obra | Sim |
| Regra de Vencimento | Tabela | vencimentos | Sim |

---

## 11. ARREDONDAMENTO FINANCEIRO

### 11.1 Regra Global

```
Usar: Decimal, ROUND_HALF_UP, 2 casas decimais
```

### 11.2 Ponto de Aplicação

```
base_ajustada = (receita + adicoes - reducoes).quantize(
    Decimal('0.01'), ROUND_HALF_UP
)

imposto = (base_ajustada * aliquota).quantize(
    Decimal('0.01'), ROUND_HALF_UP
)
```

### 11.3 Tratamento de Frações

```
Exemplo:
  base = 1.234,567
  arredonda = 1.234,57 (ROUND_HALF_UP)
```

---

## 12. EXEMPLOS NUMÉRICOS

### Exemplo 1: Empresa Simples (1 obra, sem ajustes)

```
Empresa: Construção Beta
Obra: Reforma Prédio A (alíquota ISS 3%)
Competência: Janeiro/2026

Receita Bruta: R$ 50.000,00
Devoluções: R$ 0,00
Receita Tributável (PIS/COFINS): R$ 50.000,00

Cálculo:
  Base Presumida (CCL 8%): 50.000 * 8% = R$ 4.000,00
  
  PIS: 50.000 * 0,65% = R$ 325,00
  COFINS: 50.000 * 3,0% = R$ 1.500,00
  
  IRPJ (projeção mensal): 4.000 * 15% = R$ 600,00
  CSLL (projeção mensal): 4.000 * 9% = R$ 360,00
  
  ISS: 50.000 * 3% = R$ 1.500,00

Total tributário: R$ 325 + R$ 1.500 + R$ 600 + R$ 360 + R$ 1.500 = R$ 4.285,00
Alíquota efetiva: 4.285 / 50.000 = 8,57%
```

### Exemplo 2: Com Ajuste Fiscal

```
Mesmo cenário anterior, mas:
  → Receita esquecida encontrada: +R$ 5.000 (ADICAO IRPJ)

Cálculo:
  Base Presumida Original: R$ 4.000,00
  (+) Adição IRPJ: R$ 5.000,00
  (=) Base Ajustada IRPJ: R$ 9.000,00
  
  IRPJ (ajustado): 9.000 * 15% = R$ 1.350,00
  
  Diferença: R$ 1.350 - R$ 600 = +R$ 750,00 (novo débito)
```

### Exemplo 3: Consolidação (2 Obras)

```
Obra A (Jan/2026): PIS R$ 325, COFINS R$ 1.500
Obra B (Jan/2026): PIS R$ 195, COFINS R$ 900

Consolidado Janeiro/2026:
  PIS Total: R$ 325 + R$ 195 = R$ 520,00
  COFINS Total: R$ 1.500 + R$ 900 = R$ 2.400,00
```

---

## 13. VALIDAÇÕES E REGRAS DE NEGÓCIO

| Regra | Descrição | Implementação |
|-------|-----------|----------------|
| **Receita ≥ 0** | Não permitir receita negativa | Validação em UI + Service |
| **Competência válida** | Formato MM/YYYY, data <= hoje | Validação em Service |
| **Base ≥ 0** | Após ajustes, base não pode ser negativa | Cálculo fiscal |
| **Trimestre válido** | Apuração trimestral em períodos corretos | Lógica de apuração |
| **Imposto ≥ 0** | Resultado nunca negativo | Cálculo fiscal |
| **Consolidação sem dupla contagem** | Soma obras, não receitas duplicadas | Consolidation Service |
| **Ajuste com justificativa** | Não permitir ajuste vazio sem descrição | Validação em UI |
| **Alíquota plausível** | PIS 0-3%, COFINS 0-10%, etc | Validação em Service |

---

## 14. INTEGRAÇÃO COM ESPECIFICAÇÃO FUNCIONAL

Este documento detalha **como os tributos são calculados** referenciados em:

- ✓ [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md) seção 2.3 (Apuração)
- ✓ [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md) seção 2.4 (Memória)
- ✓ [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md) seção 3.2 (Fluxo de apuração)

---

## 15. COMPATIBILIDADE COM CONTEXTO OPERACIONAL

Este documento respeita:

- ✓ Regime: Lucro Presumido (conforme [CONTEXTO_OPERACIONAL.md](CONTEXTO_OPERACIONAL.md))
- ✓ Ajustes: PIS, COFINS, CSLL, IRPJ, IRPJ Adicional
- ✓ Periodicidade: Mensal (PIS/COFINS/ISS) e Trimestral (IRPJ/CSLL)
- ✓ Consolidação: Por obra e empresa inteira
- ✓ Memória: Persistência de cálculos detalhados
- ✓ Decimal: Todos os valores em Decimal (não float)

---

**Versão:** 1.0.0  
**Próxima Revisão:** Após implementação Etapa 7 (Motor Fiscal)

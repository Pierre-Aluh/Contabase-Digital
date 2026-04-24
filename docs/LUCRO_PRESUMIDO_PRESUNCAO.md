# Lucro Presumido - Aplicacao da Presuncao na Base de Calculo

## Objetivo
Aplicar corretamente a presuncao de lucro antes do calculo de IRPJ e CSLL nos lancamentos mensais.

## Base legal resumida
- Lei 9.249/1995, art. 15: define percentuais de presuncao para IRPJ sobre a receita bruta (ex.: 8%, 32%, 1.6%).
- Lei 9.249/1995, art. 20: define percentuais de base para CSLL (em regra 12% ou 32%, conforme atividade).
- Lei 9.430/1996, art. 25: lucro presumido resulta da aplicacao dos percentuais sobre receita bruta do periodo.
- Lei 9.249/1995, art. 3, par. 1: adicional de IRPJ (10%) incide sobre parcela da base que excede o limite legal.

## Regra implementada no sistema
1. A base de PIS/COFINS continua sendo calculada sobre receita tributavel de PIS/COFINS.
2. As bases de IRPJ e CSLL passam a usar presuncao conforme perfil tributario da obra.
3. O adicional de IRPJ usa a base de IRPJ presumida (apos ajustes), com incidencia apenas no excedente do limite.
4. Ajustes fiscais continuam sendo aplicados por tributo apos a formacao da base original presumida.

## Fluxo de calculo
1. Coletar receita bruta e receitas tributaveis de PIS/COFINS.
2. Buscar percentual de presuncao do perfil da obra:
   - percentual_presuncao_irpj
   - percentual_presuncao_csll
3. Calcular bases originais:
   - base_irpj_original = receita_bruta * percentual_presuncao_irpj
   - base_csll_original = receita_bruta * percentual_presuncao_csll
4. Aplicar adicoes/reducoes por tributo.
5. Calcular base final por tributo (sem negativo).
6. Calcular IRPJ adicional sobre excedente da base final de IRPJ em relacao ao limite legal.

## Situacao atual e proximo passo recomendado
Situacao atual:
- A presuncao ja e aplicada por perfil da obra no resumo de lancamentos.

Proximo passo recomendado:
- Permitir receitas mistas por natureza da receita no mesmo lancamento (ex.: parte 8%, parte 32%), para calcular base presumida ponderada.

Exemplo para receitas mistas:
- receita_comercio (8% IRPJ, 12% CSLL)
- receita_servicos_gerais (32% IRPJ, 32% CSLL)
- receita_transporte_cargas (8% IRPJ, 12% CSLL)

Base IRPJ total:
- soma(receita_categoria * percentual_irpj_categoria)

Base CSLL total:
- soma(receita_categoria * percentual_csll_categoria)

## Observacoes
- Percentuais podem ser mantidos por perfil para cenarios simples.
- Para cenarios avancados, mapear cada campo de receita a uma categoria fiscal permite maior aderencia legal.

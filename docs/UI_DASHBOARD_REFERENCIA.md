# UI - DASHBOARD REFERÊNCIA

**Data:** 24 de abril de 2026  
**Versão:** 1.0.0  
**Status:** Aprovado para Etapa 2

---

## 1. VISÃO GERAL

A dashboard é o **painel de controle principal** da aplicação. Centraliza visualização de dados, filtros rápidos e ações principais.

**Localização da Imagem de Referência:**
```
app/ui/assets/dashboard_referencia.png
```

**Resolução Recomendada:** 1920x1200 (16:10)  
**Responsivo:** Sim (se window redimensionar, mantém proporções)

---

## 2. LAYOUT GERAL (Wireframe ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TOPBAR                                                                      │
│ ┌─────────────────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ ┌──────────┐    │
│ │ Logo / Título       │ │Competência│ │ Empresa  │ │Busca │ │Sino|Usuário│
│ └─────────────────────┘ └──────────┘ └──────────┘ └──────┘ └──────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
┌─────────────┬─────────────────────────────────────────────────────────────────┐
│             │                                                                 │
│  SIDEBAR    │  CENTRAL AREA (ScrollArea)                                    │
│  (170px)    │                                                                 │
│             │  ┌─ KPI CARDS ──────────────────────────────────────────────┐  │
│ [Dashboard] │  │ [Card1] [Card2] [Card3] [Card4]                         │  │
│ [Empresas]  │  └───────────────────────────────────────────────────────────┘  │
│ [Lançamentos│                                                                 │
│ [Apuração]  │  ┌─ GRÁFICO + RESUMO ────────────────────────────────────┐  │
│ [Relatórios │  │ [Evolução 12m - Gráfico]  │ [Resumo Apuração]        │  │
│ [Guias]     │  │ (ocupar 60% esq)          │ (ocupar 40% dir)         │  │
│ [Config]    │  │                           │ - PIS, COFINS            │  │
│             │  │                           │ - CSLL, IRPJ             │  │
│ [Theme]     │  │                           │ - ISS                    │  │
│ [Logout]    │  │                           │ - Total                  │  │
│             │  └───────────────────────────────────────────────────────────┘  │
│             │                                                                 │
│             │  ┌─ TABELA + GRÁFICO ────────────────────────────────────┐  │
│             │  │ [Composição Tributos]     │ [Distribuição %]         │  │
│             │  │ Tabela (40% esq)          │ Donut (60% dir)          │  │
│             │  └───────────────────────────────────────────────────────────┘  │
│             │                                                                 │
│             │  ┌─ VENCIMENTOS + AÇÕES ────────────────────────────────┐  │
│             │  │ [Próximos 30 dias] [Gerar Guia] [Exportar] [Comp]   │  │
│             │  └───────────────────────────────────────────────────────────┘  │
│             │                                                                 │
│             │  ┌─ FOOTER ────────────────────────────────────────────┐  │
│             │  │ Atualizado: 24 abr 2026 14:30 [Refresh] [Menu]     │  │
│             │  └───────────────────────────────────────────────────────────┘  │
└─────────────┴─────────────────────────────────────────────────────────────────┘
```

---

## 3. COMPONENTES DETALHADOS

### 3.1 TOPBAR (Topo)

**Altura:** 60px  
**Fundo:** Azul marinho escuro (#1a2f4d)  
**Padding:** 12px horizontal

**Elementos:**

| Elemento | Tipo | Tamanho | Descrição |
|----------|------|--------|-----------|
| Logo/Título | Label | 24px bold | "Contabase Digital" |
| Competência | ComboBox | 120px | Mês/Ano (MM/YYYY) dropdown |
| Empresa | ComboBox | 200px | Razão social, permite buscar |
| Busca | LineEdit | 150px | Filtro rápido por obra |
| Sino (Notificação) | IconButton | 32px | Ícone de sino |
| Bloco Usuário | Widget | 150px | Avatar + "Usuário" + dropdown |

**Cores:**
- Fundo: #1a2f4d (azul marinho)
- Texto: Branco (#FFFFFF)
- Hover: #2a4a6d (mais claro)

---

### 3.2 SIDEBAR (Barra Lateral)

**Largura:** 170px  
**Fundo:** #0f1a2e (azul muito escuro, quase preto)  
**Padding:** 16px vertical

**Itens de Menu:**

```
┌─────────────────────────┐
│ 🏠 Dashboard            │ (selecionado = azul vibrante)
│ 🏢 Empresas             │
│ 📝 Lançamentos          │
│ 📊 Apuração             │
│ 📄 Relatórios           │
│ 📋 Guias/Vencimentos    │
│ ⚙️  Configurações        │
│ 🌙 Tema Escuro (toggle) │
│                         │
│ 🚪 Sair                 │
└─────────────────────────┘
```

**Estilos:**
- Item não selecionado: Cinza claro (#b0c4de)
- Item selecionado: Azul vibrante (#00a8ff) + fundo levemente mais claro
- Ícone: 20px
- Fonte: 12px

**Comportamento:**
- Clique em item = navega para página correspondente
- Sidebar fica fixa (não collapse, pelo menos nesta etapa)

---

### 3.3 AREA CENTRAL (Scrollable)

**Cor de Fundo:** #141d2a (azul muito escuro)  
**Padding:** 20px  
**Overflow:** ScrollArea (se houver muito conteúdo)

---

## 4. SEÇÃO 1: KPI CARDS (Topo)

**Layout:** 4 cards em linha (grid 1x4)  
**Altura card:** 120px  
**Largura card:** ~22% do viewport (com gap)

**Exemplo de Card:**

```
┌──────────────────────────────┐
│                              │
│  [Ícone colorido] ↗️  +5%    │
│                              │
│  Receita Bruta               │
│  R$ 250.000,00               │
│                              │
└──────────────────────────────┘
```

**Cards (da esquerda para direita):**

1. **Receita Bruta**
   - Ícone: Moeda/Dólar (cor: ciano #00d9ff)
   - Valor: Soma receita bruta período
   - Variação: vs período anterior (%)
   - Status: Verde se ↑, laranja se ↓

2. **PIS + COFINS**
   - Ícone: Gráfico (cor: roxo #9d4edd)
   - Valor: Soma PIS + COFINS
   - Variação: vs período anterior
   - Status: Vermelho se vencido

3. **IRPJ + CSLL**
   - Ícone: Calculadora (cor: azul vibrante #00a8ff)
   - Valor: Soma IRPJ + CSLL
   - Variação: vs período anterior
   - Status: Laranja se aproximando vencimento

4. **ISS**
   - Ícone: Prédio (cor: verde água #1ef886)
   - Valor: Soma ISS
   - Variação: vs período anterior
   - Status: Neutro (informativo)

**Estilos:**
- Cantos arredondados: 8px
- Sombra: Discreta, offset 2px
- Borda: 1px sutil (#2a4a6d)
- Fundo: #1a2f4d (azul marinho)
- Texto: Branco, labels em cinza (#9bb3ce)
- Hover: Borda mais clara, sombra maior

---

## 5. SEÇÃO 2: GRÁFICO + RESUMO (40% esquerda + 60% direita)

### 5.1 Gráfico: Evolução Mensal (40%)

**Tipo:** Line Chart (evolução temporal)  
**Eixo X:** Últimos 12 meses (labels: jan, fev, mar, ...)  
**Eixo Y:** Valores em R$

**Linhas no Gráfico:**
- Receita Bruta (cor: ciano #00d9ff, espessura: 2px)
- PIS+COFINS (cor: roxo #9d4edd, espessura: 2px)
- IRPJ+CSLL (cor: azul vibrante #00a8ff, espessura: 2px)
- ISS (cor: verde água #1ef886, espessura: 2px)

**Legenda:** Abaixo do gráfico, horizontal

**Grid:** Linhas verticais/horizontais muito sutis (#2a4a6d), apenas auxiliar

**Estilo:**
- Fundo gráfico: Transparente ou #1a2f4d muito subtil
- Pontos: 4px, cor da linha
- Hover: Tooltip mostrando valor exato

---

### 5.2 Card: Resumo da Apuração (60%)

**Estrutura:**

```
┌─────────────────────────────┐
│ RESUMO DA APURAÇÃO          │
│ Período: Jan/2026           │
│ Empresa: Beta Construção    │
│                             │
│ PIS          R$ 325,00      │
│ COFINS       R$ 1.500,00    │
│ CSLL         R$ 360,00      │
│ IRPJ         R$ 600,00      │
│ IRPJ Adic.   R$ 0,00        │
│ ISS          R$ 1.500,00    │
│ ──────────────────────────  │
│ TOTAL        R$ 4.285,00    │
│                             │
│ Alíquota Efetiva: 8,57%     │
│                             │
│ Status: EM ABERTO ⚠️        │
│ Próx. Vencimento: 25 fev   │
└─────────────────────────────┘
```

**Estilos:**
- Borde: 1px #2a4a6d
- Cantos: 8px
- Fundo: #1a2f4d
- Fonte: 12px (normal), 14px (valores), 16px (total)
- Cores valor: Branco (#FFF)
- Status: Verde (OK), laranja (alerta), vermelho (vencido)

---

## 6. SEÇÃO 3: TABELA + GRÁFICO DE DISTRIBUIÇÃO

### 6.1 Tabela: Composição dos Tributos (40%)

**Colunas:**

| Coluna | Tipo | Formato |
|--------|------|---------|
| Tributo | Text | "PIS", "COFINS", etc |
| Base | Decimal | R$ X.XXX,XX |
| Alíquota | Decimal | X,XX% |
| Valor | Decimal | R$ X.XXX,XX |
| Status | Badge | EM_ABERTO / PAGO / VENCIDO |

**Dados de Exemplo:**

```
Tributo      | Base          | Alíquota | Valor     | Status
─────────────────────────────────────────────────────────────
PIS          | R$ 50.000,00  | 0,65%    | R$ 325    | Aberto
COFINS       | R$ 50.000,00  | 3,00%    | R$ 1.500  | Aberto
CSLL         | R$ 4.000,00   | 9,00%    | R$ 360    | Aberto
IRPJ         | R$ 4.000,00   | 15,00%   | R$ 600    | Aberto
IRPJ Adic.   | R$ 0,00       | 10,00%   | R$ 0      | N/A
ISS          | R$ 50.000,00  | 3,00%    | R$ 1.500  | Aberto
```

**Estilos:**
- Cabeçalho: Fundo #0f1a2e, texto branco, bold
- Linhas: Alternadas (claro/um pouco mais escuro)
- Hover linha: Destaca levemente
- Status badges:
  - Aberto: Laranja (#FF9500)
  - Pago: Verde (#1ef886)
  - Vencido: Vermelho (#FF4444)
  - N/A: Cinza (#7a8fa0)

---

### 6.2 Gráfico: Distribuição dos Tributos (60%)

**Tipo:** Donut Chart (pizza em rosca)  
**Centro:** Valor total grande, texto "Total" pequeno

**Segmentos:**

```
         Total
          R$ 4.285

    (Donut visual)
    
  Segmentos:
   PIS        7,6%  (ciano)
   COFINS     35,0% (roxo)
   CSLL       8,4%  (azul)
   IRPJ       14,0% (azul vibrante)
   ISS        35,0% (verde água)
```

**Cores:**
- PIS: Ciano (#00d9ff)
- COFINS: Roxo (#9d4edd)
- CSLL: Azul (#4a7ce8)
- IRPJ: Azul vibrante (#00a8ff)
- ISS: Verde água (#1ef886)

**Legenda:** Abaixo ou à direita do gráfico

**Hover:** Tooltip mostrando "Tributo: X%" e valor absoluto

---

## 7. SEÇÃO 4: PRÓXIMOS VENCIMENTOS + AÇÕES

### 7.1 Card: Próximos Vencimentos (Esquerda)

**Altura:** 180px  
**Lista de até 5 próximos vencimentos:**

```
┌──────────────────────────────┐
│ PRÓXIMOS VENCIMENTOS         │
│                              │
│ PIS (jan)     25 fev 🔴 10d  │
│ COFINS (jan)  25 fev 🔴 10d  │
│ IRPJ (1º)     30 abr ⚠️  37d  │
│ CSLL (1º)     30 abr ⚠️  37d  │
│ ISS (jan)     05 fev ✅ -19d │
│ ...                          │
│                              │
│ [Ver Todos] [Atualizar]      │
└──────────────────────────────┘
```

**Cores:**
- 🔴 Vermelho: Vencimento <= 5 dias (crítico)
- ⚠️ Laranja: Vencimento 6-15 dias (atenção)
- 🟢 Verde: Vencimento > 15 dias (OK)
- ✅ Verde escuro: Já vencido (informativo)

---

### 7.2 Barra de Ações (Direita)

**Altura:** 60px  
**3 Botões Principais:**

```
┌────────────────────────────────────────────────────────┐
│  [Gerar Guia]  [Exportar Relatório]  [Compartilhar]   │
└────────────────────────────────────────────────────────┘
```

**Botões:**

1. **Gerar Guia** (Ícone: Documento)
   - Abre dialog para escolher tributo
   - Gera PDF de demonstrativo de recolhimento
   - Cor: Azul vibrante (#00a8ff)

2. **Exportar Relatório** (Ícone: Download)
   - Abre RelatoriosPage (nova aba)
   - Permite escolher tipo (memória, composição, evolução)
   - Cor: Verde água (#1ef886)

3. **Compartilhar** (Ícone: Compartilhamento)
   - Abre dialog para copiar link ou enviar email
   - Salva PDF em clipboard
   - Cor: Roxo (#9d4edd)

**Estilos Botão:**
- Altura: 40px
- Padding: 12px 20px
- Borda: 1px, cor suave
- Cantos: 6px
- Hover: Fundo + claro, sombra
- Click: Animação pressão

---

## 8. FOOTER (Rodapé)

**Altura:** 50px  
**Fundo:** #0f1a2e (azul muito escuro)  
**Borda superior:** 1px #2a4a6d

**Conteúdo:**

```
Atualizado: 24 abr 2026 14:30:45     [Atualizar Agora]     [≡ Menu]
```

**Elementos:**
- Timestamp de última atualização
- Botão "Atualizar Agora" (refresh dos dados)
- Menu dropdown (acessos rápidos, settings)

---

## 9. PALETA DE CORES

### Cores Principais (Dark Theme)

| Nome | Hex | RGB | Uso |
|------|-----|-----|-----|
| Background Muito Escuro | #0f1a2e | 15, 26, 46 | Sidebar, footer |
| Background Escuro | #141d2a | 20, 29, 42 | Área central |
| Background Claro | #1a2f4d | 26, 47, 77 | Cards, topbar |
| Border Sutil | #2a4a6d | 42, 74, 109 | Linhas, bordas |
| Texto Primário | #FFFFFF | 255, 255, 255 | Labels, títulos |
| Texto Secundário | #b0c4de | 176, 196, 222 | Hints, subtítulos |
| Texto Terciário | #7a8fa0 | 122, 143, 160 | Disabled, info |

### Cores Acentos

| Nom | Hex | Uso |
|-----|-----|-----|
| Ciano | #00d9ff | PIS, indicador positivo |
| Roxo | #9d4edd | COFINS, destaque secundário |
| Azul | #4a7ce8 | CSLL, informativo |
| Azul Vibrante | #00a8ff | IRPJ, ação primária |
| Verde Água | #1ef886 | ISS, sucesso, positivo |
| Laranja | #FF9500 | Alerta, atenção |
| Vermelho | #FF4444 | Crítico, erro, vencido |
| Verde Escuro | #0d8c3c | OK, pago, sucesso |

---

## 10. TIPOGRAFIA

### Fontes

| Elemento | Fonte | Tamanho | Weight |
|----------|-------|--------|--------|
| Título Dashboard | Inter / Roboto | 24px | Bold |
| Subtítulos | Inter / Roboto | 16px | SemiBold |
| Labels | Inter / Roboto | 12px | Normal |
| Valores (números) | IBM Plex Mono | 14px | Bold |
| Rodapé | Inter / Roboto | 10px | Normal |

### Hierarquia de Tamanho

```
Título Dashboard:        24px bold
Títulos de Seção:        16px semibold
Rótulos de Card:         12px normal (cinza)
Valores de Card:         14px bold (branco)
Texto de Tabela:         12px normal
Rodapé:                  10px normal (cinza)
Tooltips:                11px normal
```

---

## 11. ÍCONES

**Estilo:** Material Design Icons ou similar, 20-32px conforme contexto

**Ícones Principais:**

- 🏠 Dashboard
- 🏢 Empresas
- 📝 Lançamentos
- 📊 Apuração
- 📄 Relatórios
- 📋 Guias/Vencimentos
- ⚙️ Configurações
- 🌙 Tema Escuro
- 🚪 Logout
- 📥 Download / Exportar
- 🔄 Refresh / Atualizar
- 📎 Anexo / Compartilhar
- ℹ️ Informação / Help
- ❌ Fechar / Cancelar
- ✓ Confirmar / OK

---

## 12. RESPONSIVIDADE

### Breakpoints

| Tamanho | Viewport | Comportamento |
|---------|----------|---------------|
| Desktop | ≥ 1440px | Layout normal (4 colunas KPI) |
| Laptop | 1024-1439px | Layout normal (4 colunas KPI) |
| Tablet | 768-1023px | 2 colunas KPI, ajustes menores |
| Mobile | < 768px | 1 coluna, sidebar collapsa |

**Nota:** Sistema é desktop-first. Mobile é nice-to-have (etapa 12+).

### Regras de Responsividade

- Cards KPI: 4 em linha, se screen < 1024px → 2 em linha
- Gráfico + Resumo: 40/60 split, se screen < 1200px → 100% sequencial
- Tabela + Donut: 40/60 split, se screen < 1200px → 100% sequencial
- Sidebar: Mantém fixed em desktop, collapsa em mobile

---

## 13. ANIMAÇÕES E INTERAÇÕES

### Transições

- Hover em botão: 200ms fade + 2px elevação
- Clique em item menu: 300ms slide lateral
- Atualizar dados: 500ms fade in (suave)
- Erro/alerta: 100ms shake (sutil)

### Comportamentos

- Dashboard carrega dados ao abrir
- Filtro (competência, empresa) → Recalcula dashboard (< 2s)
- Botão "Atualizar" → Spinner + refetch dados
- Dropdown aberto → Click fora fecha
- Tooltip aparece ao hover (300ms delay)

---

## 14. DEFINIÇÃO VISUAL: Fidelidade Máxima

### Checklist de Validação Visual (Etapa 8)

Ao implementar a dashboard, **comparar com imagem de referência:**

- ✓ Cores: Azul petróleo fundo, azul marinho cards, acentos (ciano, roxo, verde)
- ✓ Espaçamento: Padding 20px externo, 12px interno, gaps 16px
- ✓ Cantos: 8px em cards, 6px em botões
- ✓ Tipografia: Sans-serif bold titles, monospace números
- ✓ Hierarquia: KPI > Gráfico/Resumo > Tabela/Donut > Vencimentos
- ✓ Ícones: Consistentes, 20-32px, cores de acentos
- ✓ Densidade: Não apinhado, respiração visual
- ✓ Contraste: Branco em azul, > 4.5:1 WCAG AA
- ✓ Alinhamento: Grid invisível 8px, tudo alinhado
- ✓ Sombras: Discreta, não dramática (offset 2-4px, blur 8px)
- ✓ Bordas: 1px sutil ou nenhuma (prefer fundo)
- ✓ Hover states: Claro, feedback visual
- ✓ Loading states: Spinner, skeletons para dados
- ✓ Error states: Mensagem vermelha, ícone ⚠️

---

## 15. COMPATIBILIDADE COM ESPECIFICAÇÃO FUNCIONAL

Esta documentação detalha **visualmente** a funcionalidade de Dashboard descrita em:

- ✓ [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md) seção 2.6 (Dashboard)
- ✓ [ESPECIFICACAO_FUNCIONAL.md](ESPECIFICACAO_FUNCIONAL.md) seção 3.1 (Fluxos)

---

**Versão:** 1.0.0  
**Próxima Revisão:** Após screenshot Etapa 8

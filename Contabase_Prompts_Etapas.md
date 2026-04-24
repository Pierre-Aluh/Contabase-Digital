# Contabase Digital - Lucro Presumido
Prompts em Etapas para VSCode/Copilot

Este material organiza os prompts em ordem crescente e já incorpora cláusulas estratégicas de revisão para reduzir riscos de implementação rasa, duplicidade, inconsistências, regressões e problemas de integridade.

Como usar:
1. Execute um prompt por vez.
2. Avance para a próxima etapa apenas quando a etapa atual estiver funcional.
3. Mantenha a imagem de referência da dashboard dentro do projeto em `app/ui/assets/dashboard_referencia.png`.
4. Sempre peça ao VSCode/Copilot para listar arquivos criados ou alterados e explicar como testar.
5. Quando algo sair do escopo, quebre em subtarefas sem trocar a stack definida.

Comandos esperados ao longo do projeto:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
pytest -q
```

## 1ª etapa - Bloco fixo

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá criar `docs/CONTEXTO_OPERACIONAL.md`, registrar as regras permanentes do projeto e assumir esse contexto como contrato de implementação para todas as próximas etapas.

**Cláusula estratégica de revisão:** Esta etapa já embute a cláusula permanente de revisão obrigatória, que deve ser carregada para todas as respostas seguintes.

**Conteúdo do prompt:**

```text
Projeto: Contabase Digital - Lucro Presumido.

Antes de qualquer implementação, crie um arquivo `docs/CONTEXTO_OPERACIONAL.md` com todas as regras abaixo e passe a obedecê-las como contrato do projeto.

Quero um sistema desktop em Python, com PySide6, SQLAlchemy e SQLite.

O banco deve ficar em uma pasta chamada `banco_de_dados` e dentro dela deve existir apenas 1 arquivo: o próprio banco SQLite.

Regras obrigatórias:
- Não trocar a stack.
- Não usar web framework.
- Não criar telas placeholder.
- Não deixar TODO, FIXME ou "implementar depois".
- Manter o sistema funcional a cada etapa.
- Usar arquitetura limpa e simples, mas prática.
- Usar typing, dataclasses ou pydantic quando fizer sentido, `Decimal` para dinheiro e percentuais, e arredondamento financeiro consistente.
- Interface em pt-BR.
- Datas e moeda em padrão brasileiro.
- O sistema deve permitir: cadastro de empresas, obras vinculadas a empresas, lançamentos por obra e competência, apuração dos tributos por obra e consolidada.
- Deve existir ajuste individual de adição e redução de base para PIS, COFINS, CSLL, IRPJ e IRPJ Adicional.
- O cálculo deve gerar memória de cálculo detalhada.
- Relatórios devem permitir visão por obra e visão consolidada por empresa.
- O layout da dashboard deve ser replicado com fidelidade máxima à imagem de referência em `app/ui/assets/dashboard_referencia.png`, especialmente estrutura, cores, espaçamentos, cards, gráficos e distribuição visual. Apenas o conteúdo textual da barra lateral pode variar.
- Sempre que alterar algo, preserve compatibilidade com o que já foi criado.

Cláusula permanente de revisão obrigatória:
Antes de encerrar qualquer resposta futura deste projeto, faça uma revisão crítica e confirme que:
- não houve duplicidade de classes, serviços, models, migrations, seeds, rotas de navegação, widgets ou helpers;
- não ficaram imports quebrados, arquivos órfãos, nomes inconsistentes ou circularidades evitáveis;
- não ficaram regras rasas, incompletas, simuladas ou placeholders disfarçados de implementação final;
- a integridade entre UI, services, repositories, models e banco foi preservada;
- os arquivos criados continuam compatíveis com o restante do projeto;
- a etapa entregue está testável e com instruções objetivas de validação.

Ao final desta etapa:
1. salve esse contexto em `docs/CONTEXTO_OPERACIONAL.md`;
2. mostre a árvore de arquivos criada;
3. liste os riscos iniciais do projeto e como pretende evitá-los nas próximas etapas;
4. informe como esse contexto deverá ser reutilizado nas respostas seguintes.
```

## 2ª etapa - Especificação mestra

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar os 5 documentos mestres do projeto em `docs/`, sem código de implementação nesta etapa, mas com escopo, arquitetura, regras fiscais e roadmap coerentes entre si.

**Cláusula estratégica de revisão:** Ponto estratégico: exigir revisão cruzada entre documentação funcional, arquitetura e regras fiscais para evitar contradições estruturais logo no início.

**Conteúdo do prompt:**

```text
Com base no contexto operacional já criado, antes de programar quero que você crie a documentação mestra do projeto, para servir de memória de longo prazo dentro do repositório.

Crie os arquivos:
- `docs/ESPECIFICACAO_FUNCIONAL.md`
- `docs/ARQUITETURA.md`
- `docs/REGRAS_FISCAIS.md`
- `docs/UI_DASHBOARD_REFERENCIA.md`
- `docs/ROADMAP_IMPLEMENTACAO.md`

Esses documentos devem conter:
1. escopo completo do sistema;
2. módulos e responsabilidades;
3. estrutura de pastas;
4. modelo de dados proposto;
5. regras fiscais do lucro presumido;
6. regras de apuração mensal e trimestral;
7. regra dos ajustes individuais de base por tributo;
8. fluxo de cadastro empresa > obra > lançamento > apuração > relatório;
9. definição de pronto;
10. checklist visual da dashboard com base na imagem de referência.

Nesta etapa não quero código de tela nem regra fiscal implementada ainda, apenas os documentos muito bem pensados e coerentes com o projeto real que será construído.

Revisão obrigatória antes de encerrar:
- verifique se não há conflito entre documentação funcional, arquitetura, regras fiscais e roadmap;
- elimine contradições entre periodicidade mensal e trimestral;
- garanta que a modelagem proposta suporta empresa, obra, competência, ajustes por tributo e consolidação;
- revise se algum requisito ficou vago, superficial ou sem critério de aceite;
- identifique decisões de alto risco e registre mitigação nos documentos.

Ao final, mostre a árvore de arquivos criada e resuma o que cada documento cobre.
```

## 3ª etapa - Bootstrap do projeto

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar o projeto inicial executável, com `main.py`, `requirements.txt`, estrutura de pastas, tema dark, janela principal e navegação base funcionando com o banco SQLite inicializado em `banco_de_dados/contabase_digital.db`.

**Cláusula estratégica de revisão:** Ponto estratégico: nesta fase é essencial pedir revisão de imports, boot da aplicação, localização correta do banco e remoção de estruturas duplicadas ou mortas.

**Conteúdo do prompt:**

```text
Agora implemente o bootstrap completo do projeto, respeitando a documentação criada.

Quero:
1. estrutura inicial de pastas;
2. `requirements.txt`;
3. `main.py`;
4. configuração da aplicação;
5. inicialização do banco SQLite;
6. tema dark base;
7. janela principal com sidebar, topbar e área central já funcionais;
8. navegação entre páginas vazias reais, sem quebrar o layout;
9. logging e tratamento básico de erros.

Estrutura desejada, podendo ajustar de forma coerente:
- `app/`
  - `core/`
  - `db/`
  - `models/`
  - `repositories/`
  - `services/`
  - `fiscal/`
  - `reports/`
  - `ui/`
    - `assets/`
    - `dialogs/`
    - `pages/`
    - `widgets/`
    - `styles/`
  - `utils/`
- `banco_de_dados/`
- `docs/`
- `tests/`

Requisitos técnicos:
- SQLite em `banco_de_dados/contabase_digital.db`
- usar SQLAlchemy 2.x
- usar PySide6
- usar um gerenciador simples de navegação entre páginas
- criar utilitários para moeda BRL, datas pt-BR e parsing de `Decimal`
- criar folha de estilo dark global inspirada na imagem
- a aplicação deve abrir com a `DashboardPage` como página inicial

Quero um projeto já executável.

Revisão obrigatória antes de encerrar:
- rode uma checagem de imports e garanta que `python main.py` sobe sem erro;
- verifique se a estrutura de pastas bate com a arquitetura documentada;
- elimine arquivos duplicados, componentes mortos e helpers sem uso;
- confirme que o banco é criado no diretório correto e que não há arquivos extras dentro de `banco_de_dados`;
- revise se a navegação está funcional e se o layout base não quebrou o tema dark.

No final, liste os arquivos criados ou alterados e o passo a passo para rodar.
```

## 4ª etapa - Modelo de dados e banco

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar os models SQLAlchemy, o gerenciamento de sessão, repositories básicos, criação automática do banco, seed idempotente e testes de integridade suficientes para validar a base de dados.

**Cláusula estratégica de revisão:** Ponto estratégico: aqui a revisão deve focar em integridade referencial, idempotência do seed, responsabilidades bem separadas e suporte real à consolidação por obra e empresa.

**Conteúdo do prompt:**

```text
Agora implemente o banco de dados de verdade, com models, repositories e seed inicial.

Quero as tabelas principais:
- `empresas`
- `obras`
- `perfis_tributarios`
- `categorias_receita`
- `competencias`
- `lancamentos_fiscais`
- `ajustes_fiscais`
- `apuracoes`
- `apuracao_itens`
- `obrigacoes_vencimento`
- `parametros_sistema`
- `auditoria_eventos`

Regras importantes:
- empresa pode ter várias obras;
- obra pertence a uma empresa;
- obra pode ser ativa ou inativa;
- empresa pode ser ativa ou inativa;
- cada lançamento fiscal deve estar ligado a empresa, obra e competência;
- `ajustes_fiscais` devem suportar tributo alvo: `PIS`, `COFINS`, `CSLL`, `IRPJ`, `IRPJ_ADICIONAL`;
- `ajustes_fiscais` devem suportar tipo: `ADICAO` ou `REDUCAO`;
- cada ajuste deve ter descrição, valor, documento opcional e observação;
- `apuracoes` devem permitir salvar resultado por obra e consolidado;
- `apuracao_itens` devem armazenar memória de cálculo detalhada.

Seed inicial obrigatório:
- categorias de receita padrão para lucro presumido;
- perfis tributários padrão com percentuais editáveis;
- parâmetros padrão para PIS, COFINS, CSLL, IRPJ e adicional de IRPJ;
- alguns códigos de receita e vencimentos padrão parametrizados.

Quero:
- models SQLAlchemy;
- session manager;
- repositories básicos;
- script de criação automática do banco;
- seed automático idempotente;
- testes simples de integridade do banco.

Não crie nada placeholder. Quero tudo consistente com o restante do projeto.

Revisão obrigatória antes de encerrar:
- verifique integridade referencial, `unique constraints`, `indexes` úteis e coerência entre chaves estrangeiras;
- revise se o seed é realmente idempotente e não duplica registros;
- confirme que o banco continua simples de localizar e identificar;
- garanta que os repositories não repetem responsabilidades dos services;
- cheque se a modelagem realmente suporta apuração por obra e consolidada sem gambiarra.

Ao final, liste os arquivos criados ou alterados, explique como recriar o banco e como validar o seed.
```

## 5ª etapa - CRUD de empresas e obras

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar a `EmpresasPage` funcional, com CRUD completo de empresas, cadastro interno de obras, validações, auditoria básica e regras corretas de exclusão e inativação.

**Cláusula estratégica de revisão:** Ponto estratégico: a revisão deve cobrir integridade entre empresa e obra, duplicidade de formulários, bloqueio de exclusão indevida e UX verdadeiramente utilizável.

**Conteúdo do prompt:**

```text
Agora implemente o módulo completo de cadastro de empresas e obras.

Quero uma `EmpresasPage` funcional com:
- listagem paginada ou com filtro local;
- busca por nome, CNPJ e status;
- botão novo;
- botão editar;
- botão excluir;
- botão inativar ou reativar;
- detalhes da empresa em painel ou diálogo;
- aba ou seção interna de obras vinculadas.

Quero uma experiência de cadastro parecida com "cadastro dentro de cadastro":
- dentro da empresa deve ser possível cadastrar obras;
- cada obra deve ter ao menos:
  - código interno
  - nome
  - descrição
  - cidade
  - UF
  - atividade principal
  - perfil tributário
  - alíquota de ISS
  - data início
  - data fim
  - status
  - observações

Também quero:
- validação de CNPJ;
- impedir exclusão física quando houver dados fiscais vinculados; nesse caso permitir apenas inativação;
- auditoria básica das ações de criar, editar, inativar e excluir;
- dialogs elegantes no mesmo padrão visual dark;
- repositories e services desacoplados da UI.

A página deve estar bonita e realmente utilizável.
Atualize a navegação para abrir esse módulo.

Revisão obrigatória antes de encerrar:
- valide os fluxos completos de criar, editar, inativar e excluir;
- confirme que não houve duplicidade de dialogs, formulários ou regras de validação;
- revise se a exclusão lógica e a exclusão física obedecem às dependências fiscais;
- garanta que empresa e obra continuam consistentes no banco após edição;
- cheque se a UX está utilizável de verdade, sem telas rasas e sem botões que não funcionam.

Ao final, informe os arquivos criados ou alterados e os passos de teste do CRUD.
```

## 6ª etapa - Lançamentos fiscais por obra e competência

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar a tela de lançamentos fiscais por obra e competência, com persistência normalizada, múltiplos ajustes por tributo, visualização da base antes e depois dos ajustes e recurso de duplicação do mês anterior.

**Cláusula estratégica de revisão:** Ponto estratégico: nesta etapa a revisão deve focar em persistência correta dos ajustes, clareza entre base original e base ajustada e segurança na duplicação de lançamentos.

**Conteúdo do prompt:**

```text
Agora implemente a página de lançamentos fiscais por obra e competência.

Quero uma `ApuracaoEntradaPage` ou `LancamentosPage` com:
- filtro por empresa;
- filtro por obra;
- filtro por competência;
- criação e edição de lançamento mensal por obra.

Campos do lançamento:
- receita bruta;
- outras receitas operacionais;
- devoluções, cancelamentos e descontos incondicionais;
- receita tributável para PIS e COFINS;
- observações;
- anexos ou documentos opcionais por caminho local, se viável.

Quero também uma grade ou bloco específico para AJUSTES FISCAIS INDIVIDUAIS:
- tributo alvo: PIS, COFINS, CSLL, IRPJ, IRPJ Adicional;
- tipo: adição ou redução;
- valor;
- descrição;
- justificativa ou memória;
- documento de suporte opcional.

Regras:
- um lançamento pertence a uma obra e competência;
- a tela deve permitir vários ajustes no mesmo período;
- o usuário deve conseguir ver o resumo da base antes e depois dos ajustes;
- salvar tudo no banco de forma normalizada;
- permitir duplicar lançamento do mês anterior para agilizar preenchimento.

Também crie uma visualização em tabela para listar lançamentos já registrados.
A UX precisa ser boa, rápida e sem poluição visual.

Revisão obrigatória antes de encerrar:
- confirme que vários ajustes no mesmo período são persistidos corretamente;
- revise se a tela diferencia claramente base original, adições, reduções e base final;
- verifique se a duplicação do mês anterior não replica dados incorretos ou chaves indevidas;
- elimine qualquer cálculo implícito raso que deveria ser persistido ou exibido com clareza;
- garanta que filtros de empresa, obra e competência não se contradizem.

Ao final, liste os arquivos alterados e explique como testar o fluxo completo de lançamento.
```

## 7ª etapa - Motor fiscal completo

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar o motor fiscal funcional do lucro presumido, com cálculos mensais e trimestrais, persistência da apuração, memória de cálculo detalhada, consolidação por empresa e cobertura de testes unitários para os principais cenários.

**Cláusula estratégica de revisão:** Ponto estratégico: exigir auditoria de `Decimal`, parametrização, coerência entre projeção e fechamento trimestral e comparação entre cálculo salvo e cálculo exibido.

**Conteúdo do prompt:**

```text
Agora implemente o motor fiscal real do lucro presumido, com persistência da apuração e memória de cálculo.

Regras centrais:
1. PIS e COFINS devem ser apurados mensalmente.
2. IRPJ, IRPJ Adicional e CSLL devem suportar apuração trimestral correta, mas o sistema deve também mostrar projeção mensal e fechamento do trimestre.
3. ISS deve ser calculado por obra, conforme alíquota configurada na obra ou no lançamento.
4. Todas as regras devem usar `Decimal`.
5. Nenhuma alíquota ou percentual importante deve ficar presa no código sem possibilidade de parametrização no banco.

Fórmulas esperadas:
- `base_pis = max(0, receita_tributavel_pis + adicoes_pis - reducoes_pis)`
- `pis = base_pis * aliquota_pis`

- `base_cofins = max(0, receita_tributavel_cofins + adicoes_cofins - reducoes_cofins)`
- `cofins = base_cofins * aliquota_cofins`

- `base_presumida_irpj = soma(receita_por_categoria * percentual_presuncao_irpj_da_categoria) + adicoes_irpj - reducoes_irpj`
- `irpj = base_presumida_irpj * aliquota_irpj`

- `base_presumida_csll = soma(receita_por_categoria * percentual_presuncao_csll_da_categoria) + adicoes_csll - reducoes_csll`
- `csll = base_presumida_csll * aliquota_csll`

- `adicional_irpj = max(0, base_presumida_irpj_trimestre - limite_adicional_trimestre) * aliquota_adicional_irpj`

- `iss = base_iss * aliquota_iss`

Quero suporte a:
- cálculo por obra;
- cálculo consolidado da empresa;
- memória de cálculo detalhada por tributo;
- memória consolidada somando todas as obras;
- salvar apuração no banco;
- reprocessar apuração quando o lançamento mudar;
- versionamento simples ou marcação de última apuração válida.

Também quero testes unitários cobrindo:
- caso simples de serviços;
- caso com ajustes individuais por tributo;
- caso com adicional de IRPJ em trimestre;
- caso consolidado de várias obras.

Crie serviços claros como, por exemplo:
- `FiscalCalculationService`
- `PISCOFINSCalculator`
- `IRPJCSLLCalculator`
- `ConsolidationService`
- `DueDateService`

Não simplifique as regras além do necessário.

Revisão obrigatória antes de encerrar:
- audite arredondamento financeiro, uso de `Decimal` e ausência de floats em cálculos críticos;
- revise se regras mensais e trimestrais estão coerentes entre projeção e fechamento;
- verifique se nenhum percentual relevante ficou hardcoded sem parametrização;
- compare memória de cálculo persistida com o resultado efetivamente exibido;
- confira se os testes cobrem cenários de borda e não apenas caminho feliz.

Ao final, informe arquivos alterados, testes criados e como validar os resultados fiscais.
```

## 8ª etapa - Dashboard visual idêntica à referência

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar a dashboard em PySide6 com fidelidade visual máxima à imagem de referência, incluindo widgets customizados, paleta, cards, gráficos, botões e estrutura geral do painel.

**Cláusula estratégica de revisão:** Ponto estratégico: aqui a revisão deve ser visual e arquitetural ao mesmo tempo, pedindo comparação direta com a referência e eliminação de componentes genéricos ou duplicados.

**Conteúdo do prompt:**

```text
Agora quero que você replique a dashboard da imagem de referência com fidelidade máxima no PySide6.

Objetivo:
- manter a estrutura visual praticamente idêntica à imagem;
- mesma organização dos blocos;
- mesmo clima visual;
- mesmos contrastes e densidade;
- mesmos tamanhos relativos;
- mesmos tipos de cards;
- mesmo padrão de borda, sombra, espaçamento e arredondamento;
- mesma lógica de cores;
- os textos do menu lateral podem variar, mas o restante deve seguir a referência ao máximo.

Elementos obrigatórios da dashboard:
- sidebar vertical escura;
- topbar com título, filtro de competência, seletor de empresa, busca, sino ou notificação e bloco do usuário;
- 4 cards KPI no topo;
- gráfico de evolução mensal ocupando a área central esquerda;
- card resumo da apuração à direita;
- tabela de composição dos tributos embaixo à esquerda;
- gráfico de distribuição dos tributos no centro inferior;
- card de próximos vencimentos à direita;
- faixa de ações inferior com botões `Gerar Guia`, `Exportar Relatório` e `Compartilhar`;
- rodapé do painel com atualização e ação de refresh;
- toggle de modo escuro no menu lateral.

Paleta aproximada a ser seguida:
- fundo principal muito escuro azul petróleo;
- cards em azul marinho escuro;
- bordas discretas azuladas;
- azul vibrante para destaques principais;
- roxo forte para tributos;
- ciano ou verde água em indicadores;
- verde para variação positiva;
- laranja para alertas;
- tipografia branca e cinza azulada.

Detalhes visuais:
- cantos arredondados generosos;
- ícones consistentes;
- cards com ícone grande colorido à esquerda;
- gráficos elegantes com grid suave;
- tabela escura refinada;
- donut chart central com valor total no meio;
- tudo com aparência premium, sem parecer sistema genérico de Qt.

Você pode criar widgets customizados e componentes reutilizáveis.
Nesta etapa, priorize o visual fiel à referência. Pode usar dados mockados coerentes temporariamente caso alguma integração real ainda não esteja pronta, mas sem quebrar a futura integração.

Revisão obrigatória antes de encerrar:
- compare a tela produzida com a imagem de referência e liste diferenças remanescentes;
- elimine widgets genéricos com aparência pobre ou desalinhada com o design;
- revise espaçamento, hierarquia visual, contraste, alinhamento e responsividade da janela;
- confirme que os mocks usados nesta etapa são facilmente substituíveis por dados reais;
- cheque se não criou componentes visuais duplicados que poderiam ser reutilizados.

Ao final, informe os arquivos alterados e como validar a fidelidade visual da dashboard.
```

## 9ª etapa - Integrar dashboard com dados reais

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar a dashboard conectada ao banco e ao motor fiscal, sem dados fake remanescentes, com filtros reais, KPIs, gráficos, vencimentos e atualização funcional.

**Cláusula estratégica de revisão:** Ponto estratégico: a revisão deve atacar mocks remanescentes, coerência entre UI e banco e clareza entre projeção mensal e fechamento trimestral.

**Conteúdo do prompt:**

```text
Agora integre a dashboard visual com os dados reais do banco e do motor fiscal.

Quero:
- filtro de competência funcionando;
- filtro de empresa funcionando;
- busca funcionando para empresa ou obra;
- cards KPI alimentados com dados reais;
- cálculo de variação vs competência anterior;
- gráfico de evolução mensal dos últimos 12 meses;
- resumo da apuração com dados reais;
- tabela de composição dos tributos com memória resumida;
- gráfico de distribuição dos tributos com percentuais corretos;
- card de próximos vencimentos com base nas regras de vencimento;
- status `em aberto`, `pago`, `vencido`, `não aplicável`;
- botão refresh recalculando a tela.

Importante:
- quando o mês não for de fechamento trimestral, a dashboard deve saber diferenciar projeção e fechamento de IRPJ, CSLL e adicional, sem confundir o usuário;
- quando houver várias obras, permitir visão consolidada;
- quando o usuário escolher uma obra específica, refletir na apuração e nos gráficos.

Quero zero dado fake após essa etapa, exceto dados seed para demonstração quando o banco estiver vazio.

Revisão obrigatória antes de encerrar:
- verifique se não restaram dados mockados escondidos na UI;
- compare os números da dashboard com a apuração persistida no banco;
- revise a lógica de filtros para evitar conflito entre empresa, obra e competência;
- garanta que a diferenciação entre projeção mensal e fechamento trimestral esteja explícita para o usuário;
- valide o refresh contra mudança real de dados e não apenas atualização visual.

Ao final, liste os arquivos alterados e explique como validar a dashboard com dados reais.
```

## 10ª etapa - Relatórios e memória de cálculo

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar a `RelatoriosPage`, a exportação em PDF e XLSX, os relatórios obrigatórios e a integração do botão `Exportar Relatório` da dashboard com o fluxo real.

**Cláusula estratégica de revisão:** Ponto estratégico: a revisão aqui precisa comparar o conteúdo exportado com a memória de cálculo persistida e evitar divergências ou dupla contagem em consolidados.

**Conteúdo do prompt:**

```text
Agora implemente o módulo de relatórios e exportação.

Quero uma `RelatoriosPage` funcional com filtros por:
- empresa;
- obra;
- competência;
- trimestre;
- tipo de visão: por obra ou consolidada.

Relatórios obrigatórios:
1. memória de cálculo por obra;
2. memória de cálculo consolidada da empresa;
3. composição dos tributos por período;
4. evolução mensal de faturamento e impostos;
5. relatório de vencimentos.

Formatos obrigatórios:
- PDF
- XLSX

Conteúdo mínimo da memória de cálculo:
- identificação da empresa;
- identificação da obra;
- competência ou período;
- receitas consideradas;
- percentuais de presunção usados;
- adições e reduções por tributo;
- bases antes e depois dos ajustes;
- alíquotas;
- valores calculados;
- total a recolher;
- observações;
- data e hora de geração.

Também quero:
- botão `Exportar Relatório` da dashboard chamando esse módulo;
- layout PDF bonito, profissional e legível;
- planilha XLSX organizada por abas quando for consolidado;
- possibilidade de gerar relatório consolidado de todas as obras da empresa.

Revisão obrigatória antes de encerrar:
- compare os relatórios gerados com a memória de cálculo persistida para evitar divergência;
- revise se PDF e XLSX cobrem os mesmos dados essenciais;
- elimine abas, colunas ou seções redundantes;
- confirme que o relatório consolidado soma corretamente as obras sem dupla contagem;
- cheque se o botão da dashboard abre o fluxo real e não um atalho incompleto.

Ao final, liste os arquivos alterados e explique como gerar cada relatório.
```

## 11ª etapa - Guias, vencimentos e status

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar a `GuiasPage`, o cadastro parametrizável de vencimentos e códigos de receita, o fluxo real de geração de demonstrativo de recolhimento em PDF e o controle de status das obrigações.

**Cláusula estratégica de revisão:** Ponto estratégico: a revisão deve garantir parametrização real das regras, consistência entre página, dashboard e banco, e ausência de fluxo simulado no botão `Gerar Guia`.

**Conteúdo do prompt:**

```text
Agora implemente o módulo Guias/Vencimentos de forma realmente funcional.

Quero:
- `GuiasPage`;
- cadastro parametrizável de códigos de receita e regras de vencimento;
- geração de guia interna ou demonstrativo de recolhimento por tributo;
- status da obrigação: `em aberto`, `pago`, `vencido`, `cancelado`, `não aplicável`;
- marcação manual de pagamento;
- listagem por empresa, obra, competência e status.

Botão `Gerar Guia` da dashboard:
- deve abrir um fluxo real;
- permitir escolher tributo, competência, empresa e visão consolidada ou por obra;
- gerar PDF de demonstrativo de recolhimento;
- mostrar valor, base, alíquota, vencimento, código de receita e observações.

Observação importante:
- não integrar com emissão oficial governamental;
- em vez disso, gerar um demonstrativo interno completo e utilizável, sem fake button.

Também quero que o card `Próximos Vencimentos` da dashboard leia esse módulo.

Revisão obrigatória antes de encerrar:
- garanta que as regras de vencimento estão parametrizadas e não hardcoded sem necessidade;
- revise coerência entre o status exibido na página, o status da dashboard e o que está salvo no banco;
- confirme que o botão `Gerar Guia` não abre fluxo vazio ou simulado;
- valide o PDF gerado com base, alíquota, valor, vencimento e código de receita corretos;
- elimine duplicidade entre regras de vencimento do motor fiscal e deste módulo.

Ao final, informe arquivos alterados e como testar o fluxo de geração e pagamento da guia.
```

## 12ª etapa - Acabamento final, testes e entrega

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá entregar o sistema revisado ponta a ponta, com README final, scripts auxiliares, seed demonstrativo, testes, instruções de execução e empacotamento com PyInstaller.

**Cláusula estratégica de revisão:** Ponto estratégico: esta é a etapa de auditoria geral. Aqui a revisão deve ser total, cobrindo integridade, duplicidades, limitações reais e confiabilidade dos fluxos de ponta a ponta.

**Conteúdo do prompt:**

```text
Agora faça o acabamento final do sistema inteiro e elimine qualquer ponta solta.

Quero:
- revisar arquitetura e remover duplicações;
- revisar nomes de classes e arquivos;
- revisar UX das telas;
- revisar validações;
- revisar arredondamentos monetários;
- revisar consistência visual entre todas as páginas;
- revisar seed inicial para demonstrar o sistema;
- incluir dados seed suficientes para a dashboard ficar bonita e completa já no primeiro uso;
- criar `README.md` final bem explicado;
- criar instruções de backup do banco SQLite;
- criar script opcional de reset do banco para ambiente de desenvolvimento;
- preparar empacotamento com PyInstaller;
- criar testes adicionais de integração onde fizer sentido;
- garantir que a aplicação sobe limpa;
- garantir que `pytest` rode sem erro;
- garantir que a dashboard continue fiel à referência visual.

Auditoria final obrigatória antes de encerrar:
- faça uma revisão geral de duplicidade, inconsistência, imports órfãos, arquivos mortos e nomes divergentes;
- revise integridade ponta a ponta entre banco, services, UI, relatórios, dashboard e guias;
- identifique tudo o que ainda estiver raso, incompleto ou excessivamente acoplado e corrija antes de encerrar;
- rode ou prepare os testes necessários para provar que a aplicação sobe e funciona;
- seja honesto sobre limitações reais restantes, sem esconder nada;
- não declare a etapa concluída se ainda houver fluxo quebrado.

Ao final:
1. mostre a árvore final do projeto;
2. liste os principais fluxos testáveis;
3. explique como rodar em desenvolvimento;
4. explique como gerar executável;
5. aponte qualquer limitação real restante.
```

## 13ª etapa - Prompt corretivo universal (usar somente se necessário)

**Após a execução deste prompt, o VSCode deverá:** O VSCode deverá corrigir de forma cirúrgica erros de execução, cálculo, persistência, UI ou arquitetura sem reescrever o que já estiver certo e sem simplificar o sistema.

**Cláusula estratégica de revisão:** Ponto estratégico: use esta etapa apenas quando houver desvio real. A revisão precisa focar em causa raiz, não em paliativos.

**Conteúdo do prompt:**

```text
Quero que você faça uma correção cirúrgica do projeto existente sem reescrever desnecessariamente o que já está certo.

Tarefas:
- identificar erros de execução, importação, tipagem, persistência, navegação, cálculo ou UI;
- corrigir mantendo a arquitetura atual;
- não simplificar o projeto;
- não remover funcionalidades já implementadas;
- não trocar stack;
- não criar placeholders;
- preservar a fidelidade visual da dashboard;
- garantir compatibilidade com o banco existente.

Revisão obrigatória antes de encerrar:
- liste a causa raiz de cada problema corrigido;
- confirme que a correção não gerou regressão em módulos já estabilizados;
- elimine correções duplicadas, paliativas ou contraditórias;
- informe exatamente o que foi alterado e o que permaneceu intacto;
- sugira testes objetivos para validar a correção.

Ao final, liste exatamente os arquivos alterados e os testes que devo rodar.
```

---

Observação estratégica final:
- A etapa 1 deve ser reutilizada como contexto permanente.
- As cláusulas de revisão foram distribuídas nos pontos de maior risco: documentação, bootstrap, banco, engine fiscal, dashboard, relatórios e fechamento.
- Se o VSCode começar a responder de forma rasa, genérica ou contraditória, volte para a 13ª etapa e force correção cirúrgica antes de seguir.

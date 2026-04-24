# RISCOS INICIAIS E MITIGAÇÃO

## Riscos Identificados na Etapa 1

### 1. Desvio de Stack (Alto Risco)
**Risco:** Pressão para usar web framework ou trocar biblioteca de UI durante desenvolvimento.

**Mitigação:**
- Contrato explícito em `CONTEXTO_OPERACIONAL.md`
- Checklist obrigatório ao final de cada etapa validando stack
- Qualquer tentativa de desvio exige revisão crítica documentada

---

### 2. Duplicidade de Código (Alto Risco)
**Risco:** Ao longo das 12 etapas, criar múltiplos widgets, formulários ou validações similares.

**Mitigação:**
- Estabelecer componentes reutilizáveis na etapa 3 (bootstrap)
- Biblioteca central de widgets e diálogos
- Checklist de duplicidade na cláusula de revisão permanente
- Code review antes de mergear cada etapa

---

### 3. Falta de Arredondamento Financeiro Consistente (Alto Risco)
**Risco:** Calcular impostos com floats, gerar divergências entre UI e relatórios.

**Mitigação:**
- Usar `Decimal` desde a etapa 4 (banco de dados)
- Criar classe `MoneyRounder` centralizada em `app/utils/`
- Testes unitários obrigatórios para cálculos fiscais
- Validação de consistência: UI vs banco vs relatório

---

### 4. Placeholder Disfarçado de Feature (Médio Risco)
**Risco:** Deixar tela "funcional" mas com lógica rasa ou data fake persistida.

**Mitigação:**
- Checklist "pronto para produção" em cada etapa
- Teste de ponta a ponta: criar → editar → deletar → relatorio
- Zero hardcoding de dados (tudo vem do banco ou parametrização)
- Code review exigindo "prove que funciona"

---

### 5. Dashboard Não Fiel à Referência (Médio Risco)
**Risco:** Criar dashboard "parecida" mas não idêntica à imagem de referência.

**Mitigação:**
- Manter imagem de referência em `app/ui/assets/dashboard_referencia.png`
- Revisão visual comparativa na etapa 8
- Componentes customizados PySide6 em `app/ui/widgets/` para manter fidelidade
- Screenshot vs referência como validação

---

### 6. Integridade Referencial Quebrada (Médio Risco)
**Risco:** Deletar empresa com obra vinculada, ou obra com lançamento.

**Mitigação:**
- Constraints explícitas no SQLAlchemy (ondelete='RESTRICT')
- Testes de integridade na etapa 4
- Validação em services antes de deletar
- Auditoria básica registrando quem deletou quando

---

### 7. Regras Fiscais Incompletas ou Contraditórias (Alto Risco)
**Risco:** Motor fiscal funcionando com presunção incorreta ou sem suportar todos ajustes.

**Mitigação:**
- Etapa 2: Documentação mestra de regras fiscais
- Etapa 7: Testes unitários cobrindo casos de borda
- Validação trimestral vs mensal explícita
- Comparação com planilha fiscal de referência (se existir)

---

### 8. Banco de Dados Contaminado (Médio Risco)
**Risco:** Misturar arquivo .db com arquivos temporários/logs em `banco_de_dados/`.

**Mitigação:**
- Documentar restrição claramente em `CONTEXTO_OPERACIONAL.md`
- Configurar logger para escrita em diretório diferente
- Script de inicialização verifica limpeza de `banco_de_dados/`
- CI/CD (futuro) rejeita commits com arquivos extras aí

---

### 9. Sem Documentação de Como Testar (Baixo Risco)
**Risco:** Ao final de cada etapa, não saber como validar o que foi feito.

**Mitigação:**
- Obrigatório informar "passos de teste" ao final de cada etapa
- Exemplos: "Digite empresa X > clique Editar > veja dados carregados > modifique > salve"
- Testes unitários e integração conforme aplicável
- README atualizado com instruções

---

### 10. Imports Órfãos / Circularidades (Médio Risco)
**Risco:** Ao longo das etapas, criar imports circulares ou deixar código morto.

**Mitigação:**
- Linter (pylint) na etapa 3
- Script de validação verifica imports antes de commit
- Documentação clara de hierarquia de dependências
- Revisão de imports em cada checklist de etapa

---

## Estratégia de Mitigação Geral

1. **Contrato Explícito:** Este arquivo (`CONTEXTO_OPERACIONAL.md`) é o contrato. Qualquer contradição = erro do desenvolvedor.

2. **Checklist Obrigatório:** Cláusula de revisão permanente será aplicada em toda etapa.

3. **Code Review:** Cada etapa será revida antes de marcar como "concluída".

4. **Testes Incrementais:** Não avançar para etapa X+1 se etapa X não estiver verde.

5. **Documentação Viva:** Manter docs sincronizadas com código, não como afterthought.

6. **Honestidade sobre Limitações:** Se algo não couber no escopo, documentar e registrar para etapa corretiva (13ª etapa).

---

## Como Este Contexto Será Reutilizado

### Para o Desenvolvedor (Você)

- **Antes de cada etapa:** Leia este documento completamente
- **Ao codificar:** Mantenha a aba com as regras obrigatórias visível
- **Ao terminar:** Rode a checklist de revisão permanente ponto por ponto
- **Se travar:** Consulte "Riscos Identificados" para estratégia de contorno

### Para Validação

- **Testes:** Use `pytest` para validar etapas 4, 6, 7, 10
- **Relatórios:** Compare PDF gerado com referência em relatórios.md (etapa 10)
- **Dashboard:** Screenshot da etapa 8 vs imagem de referência
- **Banco:** Valide integridade com queries SQL

### Para Iterações Futuras

- **Se novo requisito surgir:** Atualize este arquivo e marque com data
- **Se limitar escopo:** Documente aqui o motivo
- **Se houver bug:** Trace até a regra violada deste documento

---

**Documento criado:** 24 de abril de 2026  
**Revisão:** Aplicar a cada etapa

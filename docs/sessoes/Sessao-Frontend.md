# Sessão de Frontend

## Missão

Construir uma interface web limpa, leve e responsiva para o fluxo diário de priorização e acompanhamento das tarefas.

## Escopo da sessão

- Templates HTML.
- CSS ou Tailwind conforme a decisão de implementação.
- Formulários de criação e edição.
- Listagem, filtros e ordenações.
- Exibição do Score ICE e seus componentes.
- Destaque de deadlines atrasados.
- Ações de concluir, editar e excluir.
- Mensagens de validação, confirmação e estados vazios.
- Acessibilidade básica e uso em telas menores.

## Fora do escopo direto

- Recalcular o Score ICE como fonte de verdade.
- Decidir regras de atraso ou ordenação sem confirmação do backend.
- Alterar schema, rotas ou persistência.
- Esconder erros de resposta para fazer o fluxo parecer concluído.

## Pré-condições

- Receber do backend os nomes dos campos, rotas, métodos e respostas.
- Receber as regras confirmadas para filtros, ordenação e validação.
- Ter dados reais ou fixtures identificadas, sem mascarar respostas vazias ou inválidas.

## Retorno necessário

- **De:** Backend.
- **Retorno solicitado:** contrato confirmado de rotas, campos, validações e contexto dos templates.
- **De:** Testes.
- **Retorno solicitado:** seletores e fluxos de interface que precisam permanecer estáveis para validação.
- **Condição para continuar:** contrato da aplicação validado, superfície executável do `BE-003` disponível e Fase 4 autorizada.

## Participação na Fase 3

- Revisar `../CONTRATO-DOMINIO.md` e `../CONTRATO-APLICACAO.md` antes da implementação visual.
- Confirmar se os campos, filtros, mensagens e contexto fornecidos pelo Backend são suficientes para a Fase 4.
- Informar necessidades de contexto ou inconsistências de nomenclatura ao `BE-003`.
- Não implementar a identidade visual, templates finais ou interações da Fase 4 nesta sessão.
- Registrar o retorno para Administração no handoff `ADM-F3-001`.

## Ativação da Fase 4

- Usar `../IDENTIDADE-VISUAL.md` como referência oficial da interface.
- Implementar os templates finais, estilos, componentes, responsividade e acessibilidade do MVP.
- Preservar rotas, campos, seletores e contexto confirmados na Fase 3.
- Não mover regras de score, atraso, status ou tags para o frontend.
- Informar `QA-004` sobre fluxos, seletores e estados que precisam ser validados.
- Registrar o retorno de implementação para Administração no handoff `ADM-F4-001`.
- Apoiar a inspeção local registrada em `../VALIDACAO-VISUAL-F4.md` e corrigir falhas visuais encontradas.

### Retorno de implementação FE-001

- Templates finais aplicados em `app/templates/` e tokens responsivos registrados em `app/static/styles.css`.
- Preservados os campos, rotas, contexto e seletores `data-task-id`, `data-task-status`, `data-overdue`, `data-empty`, `data-error-field` e `data-message`; a selecao de tags respeita `casefold()`.
- Implementados painel de foco, filtros, cards ICE, deadlines, estados de atraso/conclusão, formulário, estado vazio e confirmação visual de exclusão.
- Erros de formulario foram associados aos campos com `aria-describedby`, mantendo os valores enviados em respostas `400`.
- A identidade visual usa fundo azul-petroleo, superficies brancas, destaque ciano e marca facetada de gelo.
- A suíte completa passou com 33 testes `OK`; a falha de contraste `QA-004-F01` foi corrigida e revalidada, permanecendo a validação visual dos demais cenários com o `QA-004`.

**Retorno necessário:**

- **De:** `QA-004`.
- **Retorno solicitado:** falhas de comportamento, acessibilidade, responsividade ou regressões visuais.
- **De:** Backend.
- **Retorno solicitado:** confirmação sobre qualquer divergência de contrato encontrada durante a implementação.
- **De:** Administração e `QA-004`.
- **Retorno solicitado:** evidências da inspeção visual local e falhas de layout, acessibilidade ou responsividade.
- **Condição para continuar:** interface principal implementada e fluxos de criação, edição, conclusão, reabertura, exclusão e filtragem disponíveis para QA.

## Atividades

### Frontend-01 - Estrutura visual

- Definir layout principal e navegação mínima.
- Criar hierarquia clara entre tarefas abertas, concluídas e filtros.
- Garantir leitura do score e dos valores ICE.
- Definir estados de carregamento, vazio e erro quando aplicável.

### Frontend-02 - Formulário

- Criar campos de título, ICE, deadline e tags conforme contrato.
- Exibir validações do servidor sem substituir regras do backend.
- Permitir edição dos dados existentes.
- Preservar valores digitados quando houver erro de validação.

### Frontend-03 - Lista e priorização

- Exibir tarefas abertas na ordenação padrão do backend.
- Mostrar score e dimensões ICE.
- Destacar tarefas atrasadas.
- Exibir deadline ausente de forma explícita.
- Implementar filtros e ordenações confirmados.

### Frontend-04 - Ações e segurança de uso

- Concluir tarefa com feedback claro.
- Excluir somente após confirmação.
- Exibir tarefas concluídas por filtro.
- Evitar cliques acidentais e controles ambíguos.

### Frontend-05 - Responsividade e acessibilidade

- Garantir uso em telas menores.
- Usar labels associados aos campos.
- Garantir contraste e foco visível.
- Não depender apenas de cor para indicar atraso ou status.

## Handoffs obrigatórios

- Qualquer campo, rota, método ou mensagem de validação divergente do backend: informar backend e testes com tipo `CONTRATO`.
- Mudança de seletor, estrutura de formulário ou fluxo de interação: informar testes com tipo `UI`.
- Mudança visual que altere significado de status, atraso ou score: informar backend e testes com tipo `REGRA` ou `UI`.
- Falha de persistência ou regra encontrada durante a implementação: informar backend, não contornar no template.

## Saída esperada

- Fluxos de criação, edição, conclusão, exclusão e filtragem funcionando com backend real.
- Interface consistente com as regras do `../Discovery.md`.
- Estados de erro e vazio tratados.
- Alterações de contrato e seletores comunicadas à sessão de testes.

## Checklist de encerramento

- [ ] Nenhuma regra de negócio crítica existe somente no frontend.
- [ ] O score exibido vem do backend ou segue contrato explícito.
- [ ] Deadlines atrasados e sem prazo são distinguíveis.
- [ ] Exclusão exige confirmação.
- [ ] Formulários têm labels e mensagens de erro.
- [ ] Mudanças relevantes foram encaminhadas para testes.
- [ ] Retornos necessários de Backend e Testes foram registrados.

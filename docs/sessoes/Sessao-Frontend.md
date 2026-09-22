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
- **Condição para continuar:** Fase 3 concluída e handoff `CONTRATO` recebido.

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

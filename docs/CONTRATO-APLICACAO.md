# Contrato da Aplicação

Este documento define as rotas HTTP, os formulários e o contexto dos templates da aplicação (Fases 3 e 9). A aplicação usa HTML renderizado pelo Flask; não há API JSON pública prevista para o MVP.

## Regras gerais

- Rotas de leitura respondem HTML com status `200`.
- Formulários válidos usam o padrão Post/Redirect/Get e respondem `303` para a página de destino.
- Mensagens de sucesso são flash messages de uso único, exibidas após o redirect e removidas no primeiro carregamento da página.
- Mensagens de sucesso desaparecem automaticamente após 4 segundos e podem ser fechadas manualmente; erros de validação permanecem visíveis.
- Erros de validação dos formulários de tarefa respondem `400` e renderizam novamente o formulário com os valores enviados e um mapa `errors` por campo.
- Erros de validação em ações de gestão de tags e grupos são comunicados por flash de erro e redirect `303`.
- Tarefa ou grupo inexistente nas rotas de recurso responde `404`.
- As regras de score, atraso, status e tags continuam pertencendo ao domínio; rotas e templates não as reimplementam.
- O endpoint `GET /health` da Fundação permanece disponível.

## Rotas

| Método | Rota | Responsabilidade | Resposta de sucesso |
|---|---|---|---|
| `GET` | `/` | Listar tarefas com filtros e ordenação | HTML `200` |
| `GET` | `/tasks/new` | Exibir formulário de criação | HTML `200` |
| `POST` | `/tasks` | Criar tarefa | Redirect `303` para `/` |
| `GET` | `/tasks/<int:task_id>/edit` | Exibir formulário de edição | HTML `200` |
| `POST` | `/tasks/<int:task_id>` | Atualizar tarefa | Redirect `303` para `/` |
| `POST` | `/tasks/<int:task_id>/complete` | Concluir tarefa | Redirect `303` para `/` |
| `POST` | `/tasks/<int:task_id>/reopen` | Reabrir tarefa | Redirect `303` para `/` |
| `POST` | `/tasks/<int:task_id>/delete` | Excluir tarefa permanentemente | Redirect `303` para `/` |
| `GET` | `/grupos` | Listar grupos com tipo, status e contagem de tarefas | HTML `200` |
| `POST` | `/grupos` | Criar grupo (`name`, `kind`) | Redirect `303` para `/grupos` |
| `POST` | `/grupos/<int:group_id>/rename` | Renomear grupo (`name`) | Redirect `303` para `/grupos` |
| `POST` | `/grupos/<int:group_id>/archive` | Arquivar grupo | Redirect `303` para `/grupos` |
| `POST` | `/grupos/<int:group_id>/delete` | Excluir grupo e soltar os cards | Redirect `303` para `/grupos` |
| `POST` | `/digest/send` | Enviar resumo das tarefas por email (SMTP_* + DIGEST_TO) | Redirect `303` para a tela de origem |
| `POST` | `/publish` | Publicar banco local no servidor Termux (DEPLOY_*; botao visivel apenas com configuracao) | Redirect `303` para a tela de origem |
| `GET` | `/health` | Verificar aplicação, banco e schema | JSON `200` |

Não criar rotas para autenticação, usuários, API JSON ou funcionalidades fora do MVP nesta fase.

## Listagem

`GET /` aceita os seguintes parâmetros de consulta:

| Parâmetro | Valores | Padrão | Regra |
|---|---|---|---|
| `status` | `open`, `completed`, `all` | `open` | Define o status consultado |
| `overdue` | `1` | ausente | Filtra tarefas abertas atrasadas |
| `tag` | repetido | ausente | Exige que a tarefa contenha todas as tags informadas |
| `group` | id inteiro ou `none` | ausente | Filtra por grupo; `none` mostra somente cards soltos |
| `order` | `score`, `deadline`, `created_at` | `score` | Usa a ordenação definida pelo domínio |

Exemplo:

```text
/?status=open&overdue=1&tag=Backend&tag=Estudo&group=2&order=deadline
```

Parâmetros inválidos devem gerar erro de validação controlado, sem exceção não tratada.

## Formulários

Os campos de criação e edição usam os nomes abaixo:

| Campo | Obrigatório | Formato |
|---|---:|---|
| `title` | sim | Texto, máximo de 120 caracteres |
| `impact` | sim | Inteiro de 1 a 10 |
| `confidence` | sim | Inteiro de 1 a 10 |
| `ease` | sim | Inteiro de 1 a 10 |
| `deadline` | não | `YYYY-MM-DD` ou vazio |
| `tags` | não | Texto separado por vírgulas |
| `grupo_id` | não | Id de grupo existente ou vazio para card solto |

O adaptador HTTP deve separar `tags` por vírgula, remover espaços externos e enviar a lista ao `TaskRepository`. Tags vazias ou inválidas devem ser rejeitadas pelo domínio e apresentadas no campo correspondente. Um `grupo_id` inexistente gera erro no campo `grupo_id`; campo ausente na edição preserva o vínculo atual.

## Ações de status e exclusão

- Concluir e reabrir são ações distintas e usam `POST`.
- Excluir é permanente e usa `POST`.
- A confirmação visual da exclusão pertence ao frontend; o backend continua validando o identificador.
- Após concluir, a tarefa deixa a lista padrão.
- Após reabrir, a tarefa volta a ser considerada na lista padrão e pode voltar a ficar atrasada.

## Contexto dos templates

O template da listagem deve receber:

- `tasks`: tarefas retornadas pelo domínio, incluindo `score`, indicador derivado de atraso, `grupo_id` e `group` (`id`, `name`, `kind`) quando houver vínculo.
- `available_tags`: tags existentes para os controles de filtro.
- `available_groups`: grupos existentes para o filtro e para os formulários.
- `filters`: valores ativos de `status`, `overdue`, `tag`, `group` e `order`.
- `errors`: erros de validação quando houver re-renderização do formulário.
- `messages`: mensagens de sucesso ou orientação para o usuário, consumidas uma única vez.

O template de criação/edição deve receber:

- `task`: tarefa existente na edição ou `None` na criação.
- `errors`: mapa de erros por campo.
- `form_values`: valores atuais do formulário, preservados quando houver erro, incluindo `grupo_id`.
- `groups`: grupos disponíveis para o campo `grupo_id`, incluindo arquivados para preservar vínculos existentes.

O template de `/grupos` recebe `groups` com `id`, `name`, `kind`, `status` e `task_count`, além de `messages`.

## Seletores de interface

- Cards: `data-task-id`, `data-task-status`, `data-overdue`.
- Grupo no card: `data-group-id`, `data-group-kind` (`projeto`/`area`).
- Tela de grupos: `data-group-id`, `data-group-kind`, `data-group-status` na linha; `groups-title` no heading.
- Filtro: `name="group"` com valores vazio, `none` ou id do grupo.

## Handoff entre setores

- Backend implementa rotas, adaptação de entrada, respostas e contexto.
- Frontend implementa templates, estilos, controles e confirmação visual.
- Testes valida métodos, status HTTP, redirecionamentos, mensagens, filtros e contexto.
- Qualquer alteração neste documento exige handoff `CONTRATO` para Backend, Frontend e Testes.

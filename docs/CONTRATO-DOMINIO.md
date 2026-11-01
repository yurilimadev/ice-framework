# Contrato do Domínio de Tarefas

Este documento descreve o domínio implementado e validado na Fase 2. As rotas
HTTP e o contexto dos templates são definidos separadamente em
`CONTRATO-APLICACAO.md` na Fase 3.

## Tarefa

Uma tarefa possui os campos:

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Identificador persistido, maior que zero |
| `title` | texto | Obrigatório, espaços externos removidos, máximo de 120 caracteres |
| `impact` | inteiro | Valor entre 1 e 10 |
| `confidence` | inteiro | Valor entre 1 e 10 |
| `ease` | inteiro | Valor entre 1 e 10; 10 representa uma tarefa muito fácil |
| `deadline` | data ou vazio | Data sem horário no formato `YYYY-MM-DD` |
| `status` | texto | `open` ou `completed` |
| `created_at` | timestamp | Instante de criação armazenado em UTC, em ISO 8601 |
| `tags` | lista de textos | Cada tag tem no máximo 30 caracteres |
| `grupo_id` | inteiro ou vazio | Referência opcional a um grupo; `vazio` representa card solto |

O score não é armazenado como fonte independente. Ele é derivado sempre por:

```text
impact x confidence x ease
```

O valor máximo é `1000`.

## Grupo

Um grupo organiza cards em um Projeto ou uma Área, sem alterar o score ou as tags da tarefa:

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Identificador persistido, maior que zero |
| `name` | texto | Obrigatório, espaços externos removidos, entre 1 e 30 caracteres |
| `kind` | texto | `projeto`, `area` ou `recurso` |
| `status` | texto | `active` ou `archived` |
| `created_at` | timestamp | Instante de criação armazenado em UTC, em ISO 8601 |

Regras do grupo:

- Um card pode pertencer a no máximo um grupo; `grupo_id` vazio mantém o card solto.
- Excluir um grupo solta seus cards (`ON DELETE SET NULL`), sem excluir tarefas ou tags.
- Arquivar um grupo apenas muda seu `status`; os vínculos das tarefas permanecem. A visão de grupos arquivados é o conceito de Arquivos.
- `Recursos` é um tipo de grupo (`recurso`) que também agrupa tarefas.
- Tags continuam transversais e não pertencem ao grupo.
- Não existe score agregado nem ordinal por grupo.

## Regras

- Uma tarefa está atrasada somente quando está `open` e seu deadline é anterior ao dia atual.
- Deadline igual ao dia atual não está atrasado.
- Uma tarefa `completed` nunca está atrasada.
- Tarefas concluídas podem ser reabertas.
- Tags têm espaços externos removidos e são deduplicadas por equivalência Unicode com `casefold()`; a primeira grafia é preservada.
- O filtro com várias tags exige que a tarefa contenha todas elas.
- A lista padrão consulta somente tarefas `open`.
- A ordenação padrão usa score decrescente, deadline crescente com tarefas sem deadline no fim, data de criação crescente e `id` como desempate final.
- A ordenação explícita por deadline é crescente; a ordenação por criação é decrescente.

## Persistência

O schema `4` usa as tabelas `tasks`, `tags`, `task_tags` e `grupos`. Tags podem
ser reutilizadas entre tarefas sem gerar linhas duplicadas. `tasks.grupo_id` é
nulo por padrão e referencia `grupos(id)` com `ON DELETE SET NULL`. A migração
`3 -> 4` recria `grupos` para ampliar `kind` e preserva ids, status e vínculos
das tarefas. A restauração do SQLite preserva os fatores ICE, as tags e os
vínculos de grupo; o score é reconstruído a partir dos fatores ICE.

O acesso do domínio nesta fase é feito por `TaskRepository` e
`GroupRepository`. As rotas de aplicação estão fora deste contrato e devem
seguir `CONTRATO-APLICACAO.md`.

## Operações disponíveis

O `TaskRepository` fornece as operações usadas pelo adaptador HTTP:

- `create`: cria uma tarefa aberta, opcionalmente vinculada a um grupo.
- `get`: recupera uma tarefa ou gera `TaskNotFoundError`.
- `list`: filtra por status, atraso, tags e grupo; `grupo_id` com id filtra o grupo, `None` filtra cards soltos e a ausência do parâmetro não filtra por grupo. Ordena por score, deadline ou criação.
- `update`: atualiza os campos editáveis, incluindo `grupo_id`, e recalcula o score derivado.
- `set_group`: vincula a tarefa a um grupo ou, com `None`, a deixa solta.
- `clear_group`: remove o vínculo da tarefa com qualquer grupo.
- `complete`: muda o status para `completed`.
- `reopen`: muda o status para `open`.
- `delete`: remove permanentemente a tarefa e seus vínculos de tags.

O `GroupRepository` fornece:

- `create`: cria um grupo ativo com `name` e `kind`.
- `get`: recupera um grupo ou gera `GroupNotFoundError`.
- `list`: lista grupos e pode filtrar por `status`.
- `rename`: altera o nome do grupo.
- `archive`: muda o status para `archived`.
- `delete`: remove o grupo e solta as tarefas vinculadas.

Entradas inválidas geram `ValidationError` com campo e mensagem controlados. O
adaptador HTTP é responsável por transformar essa exceção em erro de formulário.

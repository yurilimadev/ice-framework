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

O score não é armazenado como fonte independente. Ele é derivado sempre por:

```text
impact x confidence x ease
```

O valor máximo é `1000`.

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

O schema `2` usa as tabelas `tasks`, `tags` e `task_tags`. Tags podem ser
reutilizadas entre tarefas sem gerar linhas duplicadas. A restauração do
SQLite preserva os fatores ICE, e o score é reconstruído a partir deles.

O acesso do domínio nesta fase é feito por `TaskRepository`. As rotas de
aplicação estão fora deste contrato e devem seguir `CONTRATO-APLICACAO.md`.

## Operações disponíveis

O `TaskRepository` fornece as operações usadas pelo adaptador HTTP:

- `create`: cria uma tarefa aberta.
- `get`: recupera uma tarefa ou gera `TaskNotFoundError`.
- `list`: filtra por status, atraso e tags e ordena por score, deadline ou criação.
- `update`: atualiza os campos editáveis e recalcula o score derivado.
- `complete`: muda o status para `completed`.
- `reopen`: muda o status para `open`.
- `delete`: remove permanentemente a tarefa e seus vínculos de tags.

Entradas inválidas geram `ValidationError` com campo e mensagem controlados. O
adaptador HTTP é responsável por transformar essa exceção em erro de formulário.

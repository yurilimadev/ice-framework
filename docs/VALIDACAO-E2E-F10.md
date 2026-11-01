# Validacao E2E e publicacao dos grupos (Fase 10)

**Status:** concluída em 2026-10-31 — aceite do usuario registrado

Criterio de saida: fluxos de grupo aprovados nas duas instancias; backup/restauracao e publicacao preservam grupos e vinculos sem perda de dados.

## Drill local (aprovado)

- Banco de trabalho: copia do banco real (`data/app.sqlite3`), migrada de schema `2` para `3`.
- Estado inicial: `5` tarefas, `5` tags, schema `3`.
- Fluxos executados pela interface HTTP: criar grupos Projeto e Area, vincular tarefa existente, criar tarefa agrupada e tarefa solta, renomear grupo, arquivar grupo, filtrar por grupo e por `none`.
- Resultados: `/grupos`, `/?group=<id>` e `/?group=none` responderam `200` com os conteudos esperados.
- Reinicio: nova instancia da aplicacao manteve schema `3`, `2` grupos, `7` tarefas e os vinculos.
- Backup/restauracao: snapshot pela backup API do SQLite; restauracao em banco novo retornou `PRAGMA integrity_check = ok`, schema `3`, `2` grupos, `7` tarefas e o vinculo preservado.
- Exclusao de grupo: o card ficou solto (`grupo_id` nulo) e as tags foram preservadas.

## Drill do servidor Termux (aprovado)

- Codigo do servidor atualizado de `066008c` para `982e877` via `git pull --ff-only`.
- Publicacao de validacao: grupo `Verificacao F10` e tarefa `Card F10` criados no banco local e enviados com `python3 -m flask --app wsgi publish`.
- Verificacoes na instancia online: `/health` com `schema_version = 3`; `/grupos` com o grupo; `/` com o card e `data-group-kind="projeto"`; `/?group=1` com o card.
- Banco do servidor: schema `3`, grupo ativo e vinculo `Card F10 -> Verificacao F10`.
- Backup/restauracao no servidor: snapshot e copia restaurada com `PRAGMA integrity_check = ok`, schema `3`, o grupo e o vinculo preservados.
- Limpeza: grupo e tarefa de validacao removidos localmente e o banco republicado; o servidor voltou a `5` tarefas, `0` grupos, `/grupos` `200` e sem residuo de `Card F10`.

## Comandos reais utilizados

```bash
python3 -m flask --app wsgi publish
ssh ice-termux 'cd ~/ice-framework && git pull --ff-only'
```

As verificacoes usaram `curl` em `127.0.0.1:8000` no servidor e consultas `PRAGMA user_version`, `PRAGMA integrity_check` e contagens no SQLite.

## Conclusao

Criterio de saida da Fase 10 atendido nas duas instancias: os fluxos de grupo funcionam, a publicacao espelha grupos e vinculos, e backup/restauracao preservam os dados. Aceite do usuario pendente para encerrar o Ciclo 2.

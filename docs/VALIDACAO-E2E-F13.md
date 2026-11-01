# Validacao E2E e publicacao do Ciclo 3 (Fase 13)

**Status:** executada em 2026-10-31 — **aguardando aceite do usuario**

Criterio de saida: fluxos dos quatro conceitos aprovados nas duas instancias; backup/restauracao e publicacao preservam os dados.

## Drill local (aprovado)

- Banco de trabalho: copia do banco real, migrada de schema `3` para `4`.
- Estado inicial: `5` tarefas preservadas.
- Grupos criados: `Projeto F13`, `Area F13`, `Recurso F13` e `Arquivado F13` (arquivado).
- Cards: um por grupo ativo, um no grupo arquivado e um solto.
- Painel: secoes `projetos`, `areas`, `recursos`, `arquivos` e `sem-grupo` presentes; cards nas secoes corretas; filtro de grupo ausente.
- Formulario: opcoes dos tres tipos (`Projeto`, `Área`, `Recurso`) presentes.
- Filtro por tag: retornou os cards esperados.
- Reinicio: nova instancia manteve schema `4`, `4` grupos e `4` vinculos.
- Backup/restauracao: `PRAGMA integrity_check = ok`, schema `4`, `4` grupos e `4` vinculos preservados.
- Exclusao de grupo: card solto e tags preservadas.

## Drill do servidor Termux (aprovado)

- Codigo do servidor atualizado de `27aa558` para `33190be` via `git pull --ff-only`.
- Banco local migrado para schema `4`; grupos/cards de validacao criados e publicados com `python3 -m flask --app wsgi publish`.
- Verificacoes na instancia online: `/health` com `schema_version = 4`; painel com as cinco secoes; cards de Projeto, Area, Recurso, Arquivo e solto; `/grupos` `200`.
- Banco remoto: schema `4`, `4` grupos (`projeto` ativo, `area` ativo, `recurso` ativo, `projeto` arquivado), `10` tarefas e `4` vinculos.
- Backup/restauracao remota: `PRAGMA integrity_check = ok`, schema `4`, `4` grupos e `4` vinculos preservados.
- Limpeza: dados `Validacao F13` removidos localmente e o banco republicado. Estado final: schema `4`, `5` tarefas, `0` grupos; painel exibe apenas `Sem grupo`; `/grupos` `200`; nenhum residuo de validacao.

## Comandos reais utilizados

```bash
python3 -m flask --app wsgi publish
ssh ice-termux 'cd ~/ice-framework && git pull --ff-only'
```

As verificacoes usaram `curl` em `127.0.0.1:8000` no servidor e consultas `PRAGMA user_version`, `PRAGMA integrity_check` e contagens no SQLite.

## Conclusao

Criterio de saida da Fase 13 atendido nas duas instancias. A publicacao e o backup/restauracao preservam grupos, status e vinculos. Aceite do usuario pendente para encerrar o Ciclo 3.

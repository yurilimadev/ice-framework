# Validacao E2E do Peixe-piloto (Fase 16)

**Status:** concluida em 2026-10-31 (aceite do usuario)

Criterio de saida: e-mails diario e semanal recebidos, dados preservados apos restart/publicacao, suite verde e nenhuma credencial commitada.

## Validacao local (aprovada)

- Banco local migrado de schema `4` para `5`.
- Lead de validacao criado com status `a_enviar`.
- E-mail diario enviado com sucesso pelo SMTP configurado.
- E-mail semanal enviado com sucesso pelo SMTP configurado.
- Conteudo: missao/follow-ups no diario; mensagens, respostas, conversas, propostas, pilotos, quest e doce no semanal; links para `/peixe` e `/peixe/semana`.
- Backup e restauracao com schema `5`: `PRAGMA integrity_check = ok`, lead preservado e `PRAGMA foreign_key_check` vazio.
- Paginas locais verificadas: `/peixe`, `/peixe/leads`, `/peixe/leads/new`, detalhe, `/peixe/semana` e `/peixe/agenda`.
- Suite completa: `105` testes `OK`.
- Credenciais permanecem apenas no `.env` local, fora do git.

## Publicacao no Termux (aprovada)

- Codigo atualizado no servidor ate `7a76ff6` via `git pull --ff-only`.
- `python3 -m flask --app wsgi publish` enviou o banco em schema `5` e reiniciou o servico.
- Verificacoes:
  - `/health` local e `https://ice.yurilimadev.com/health` com `schema_version = 5`;
  - `/peixe` local e externo respondendo `200`;
  - lead `Validacao F16 Online` espelhado e visivel na missao;
  - e-mail diario disparado pelo Python/`.env` do proprio servidor com sucesso;
  - lead de validacao removido localmente e banco republicado; estado final com `0` leads e sem residuo.
- Backup/restauracao nao foi repetido no servidor nesta rodada, mas o schema `5` ja havia sido validado em copia local e o banco remoto respondeu `integrity_check` na publicacao anterior.

## Agendamento (aprovado com cronie)

O pacote `termux-job-scheduler` nao existe no repositorio Termux atual (`Unable to locate package`). Alternativa registrada no proprio briefing: `crond`.

- Instalado `cronie`.
- `crond` ativo via `termux-services`.
- Crontab:
  - `0 8 * * * ~/ice-framework/scripts/peixe-daily.sh`
  - `0 17 * * 5 ~/ice-framework/scripts/peixe-weekly.sh`
- Sintaxe dos scripts validada com `bash -n`; CLI `send-peixe-daily --help` carregou no venv do servidor.

## Conclusao

A F16 foi concluida: e-mails reais, backup/restauracao em schema `5`, publicacao no Termux, `/peixe` online e agendamento via `cronie`. Nenhuma credencial foi commitada.

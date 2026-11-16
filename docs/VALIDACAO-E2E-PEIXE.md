# Validacao E2E do Peixe-piloto (Fase 16)

**Status:** executada localmente em 2026-10-31 — publicacao no Termux pendente

Criterio de saida: e-mails diario e semanal recebidos, dados preservados apos restart/publicacao, suite verde e nenhuma credencial commitada.

## Validacao local (aprovada)

- Banco local migrado de schema `4` para `5`.
- Lead de validacao `Validacao F16` criado com status `a_enviar`.
- E-mail diario enviado com sucesso:
  - `python3 -m flask --app wsgi send-peixe-daily`
  - saida: `Resumo diario do Peixe enviado para ...`
- E-mail semanal enviado com sucesso:
  - `python3 -m flask --app wsgi send-peixe-weekly`
  - saida: `Fechamento semanal do Peixe enviado para ...`
- Conteudo dos e-mails: missao/follow-ups no diario; mensagens, respostas, conversas, propostas, pilotos, quest e doce no semanal; links para `/peixe` e `/peixe/semana`.
- Backup e restauracao com schema `5`: `PRAGMA integrity_check = ok`, lead preservado e `PRAGMA foreign_key_check` vazio.
- Paginas locais verificadas: `/peixe`, `/peixe/leads`, `/peixe/leads/new`, detalhe, `/peixe/semana` e `/peixe/agenda`.
- Suite completa: `105` testes `OK`.
- Credenciais permanecem apenas no `.env` local, fora do git.

## Publicacao no Termux (bloqueada)

- O app online respondeu `https://ice.yurilimadev.com/health` com schema `4`.
- A conexao SSH para `ice-termux:8022` foi recusada (`Connection refused`), embora o host responda a ping.
- Por isso, nesta sessao nao foi possivel:
  - rodar `git pull` no servidor;
  - executar `python3 -m flask --app wsgi publish`;
  - instalar/agendar `termux-job-scheduler`;
  - validar `/peixe` no online.

## Proximo passo

1. Abrir o Termux no Android e garantir que o `sshd` esteja ativo.
2. Rodar `git pull --ff-only` em `~/ice-framework`.
3. Executar `python3 -m flask --app wsgi publish` no PC local.
4. Confirmar `/health` com schema `5` e `/peixe` no online.
5. Instalar/agendar os scripts `scripts/peixe-daily.sh` e `scripts/peixe-weekly.sh` com `termux-job-scheduler`.

## Conclusao

A F16 esta validada localmente (e-mails reais, backup/restauracao e suite). A publicacao online e o agendamento permanecem pendentes por indisponibilidade do SSH do Termux.

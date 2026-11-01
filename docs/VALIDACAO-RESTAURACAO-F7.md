# Validacao de backup e restauracao da Fase 7

**Status:** executada em 2026-10-31 — **aguardando aceite do usuario**

Criterio de saida: uma copia do volume restaura a mesma instancia sem perda de dados. Ensaio executado nas DUAS instancias reais.

## Drill local (aprovado)

- Parada segura: SIGTERM ao processo do app; porta 5000 livre.
- Snapshot consistente (backup API): `backups/backup-f7-20261031-123709.sqlite3` — integridade `ok`, schema 2, 5 tarefas / 5 tags (3 abertas / 2 concluidas).
- Restauracao em instancia limpa (porta 5010, base zerada substituida pelo backup): `/health` 200 schema 2; os 5 titulos reais renderizados.

## Drill do servidor Termux (aprovado)

- Parada segura: `sv down ice-framework`.
- Snapshot: `~/backups-ice/backup-f7-20261031-224646.sqlite3` — integridade `ok`, schema 2, 5 tarefas / 5 tags.
- Restauracao em instancia limpa (gunicorn efemero na porta 8010, base em arquivo novo): `/health` 200; `status=open` = 3, `status=all` = 5; mesmos 5 titulos.
- Producao reposta: `sv up`, health 200, 5 cards na borda via `ice.yurilimadev.com`.
- Nota operacional do drill: primeira tentativa da instancia de restauracao subiu fora da pasta do app (`No module named 'wsgi'`) — erro do operador do ensaio (sem `cd`), corrigido; o gunicorn do servico de producao sempre faz `cd` no run script.

## Comandos reais documentados

Secao nova no `README.md` (raiz) com backup e restauracao para as duas instancias (backup API do SQLite, `sv down/up` no Termux, verificacao por `PRAGMA integrity_check`).

## Observacao de infraestrutura (registrada)

O Android/Termux passou por reinicios no dia (usuario reportou desligamentos periodicos). Mitigacoes orientadas: bateria do Termux em "Sem restricoes", reabrir o Termux apos reinicio (servicos `runsv` sobem sozinhos) e `termux-wake-lock`. Reserva de DHCP no roteador segue recomendada.

## Conclusao

Criterio de saida da Fase 7: atendido nas duas instancias (copia restaura a mesma instancia sem perda de dados). Aceite do usuario pendente para fechamento formal do Ciclo 1.

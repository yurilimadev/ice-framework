# Backlog e Próximos Passos

Este documento registra demandas futuras que ainda não fazem parte do escopo atual.

## 1. Gerenciamento de Tags

**Status:** implementado e reestruturado na Fase 4 (2026-09-27): `/tags` em largura única, excluir disponível para todas as tags (desvincula das tarefas após confirmação), renomear e mesclar. Pendente inspeção visual no roteiro da fase.

## 2. Otimização do Filtro de Tags

**Status:** pendente de discovery.

## 3. Notificações por Email

**Status:** implementado e testado com envio real via Gmail (2026-09-29): CLI `python3 -m flask --app wsgi send-digest` E botão "Enviar resumo" na barra superior (`POST /digest/send`, rota nova no contrato). Email redesenhado na identidade ICE (HTML inline + versão texto puro anexada). Credenciais em `.env` local (modelo em `.env.example`, fora do git). Pendente decisão de agendamento (cron/systemd timer).

## Registro

- Data: 2026-09-27
- Origem: solicitação do usuário durante sessão de validação da Fase 4.


## 5. Sincronizacao local <-> servidor Termux

**Status:** implementado (2026-10-10). Regra aprovada pelo usuario: local publica, servidor espelha (tarefa criada direto no servidor e sobrescrita na proxima publicacao). Gatilhos: CLI `python3 -m flask --app wsgi publish` e botao `Publicar` na barra superior (rota `POST /publish`, visivel apenas com DEPLOY_* no `.env` local). Snapshot consistente via backup API do SQLite; antivirus via restart do servico remoto. Cron ficou para decisao futura.


## 6. Agrupamento de tasks (grupos Projeto / Area - "PARA-lite")

**Status:** desenhado (2026-10-10), aguardando ciclo posterior as fases 5-7. Decisoes do usuario: (1) escopo = apenas agrupamento de tasks, sem PARA completo (sem Recursos, sem agregacao de score); (2) cards vivem dentro de grupos, card solto continua existindo (grupo_id funciona); (3) entra como Ciclo 2 apos as fases 5-7.

**Desenho registrado:**
- Schema 3: tabela `grupos` (id, name 1-30, kind 'projeto'|'area', status 'active'|'archived', created_at); `tasks.grupo_id` nulo referenciando grupos; excluir grupo solta os cards (ON DELETE SET NULL).
- Tags continuam transversais, sem mudancas.
- UI prevista: tela `/grupos` (criar/renomear/arquivar/excluir, padrao de `/tags`), filtro por grupo no painel, distintivo Projeto/Area no card e na intro do card.
- Sequencia do Ciclo 2: Fase 8 (dominio + migracao) -> Fase 9 (interface e filtros) -> Fase 10 (validacao + publicacao do banco no servidor via `publish`).
- Possiveis acrecismos futuros (fora do escopo): score agregado do grupo, ordinal por grupo, tela de Arquivo dedicada.

**Bloqueio:** iniciar apenas apos Fases 5, 6 e 7 concluidas (regra de uma fase por vez).

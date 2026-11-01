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

**Status:** concluido no Ciclo 2 (2026-10-31, aceite do usuario). Fases 8 a 10 entregues: schema `3`, `/grupos`, filtro e badges, E2E, backup/restauracao e publicacao no servidor. Possiveis acrescimos futuros (fora do escopo): score agregado do grupo, ordinal por grupo e tela de Arquivo dedicada. Decisoes do usuario: (1) escopo = apenas agrupamento de tasks, sem PARA completo (sem Recursos, sem agregacao de score); (2) cards vivem dentro de grupos, card solto continua existindo (grupo_id funciona); (3) entra como Ciclo 2 apos as fases 5-7.

**Desenho registrado:**
- Schema 3: tabela `grupos` (id, name 1-30, kind 'projeto'|'area', status 'active'|'archived', created_at); `tasks.grupo_id` nulo referenciando grupos; excluir grupo solta os cards (ON DELETE SET NULL).
- Tags continuam transversais, sem mudancas.
- UI prevista: tela `/grupos` (criar/renomear/arquivar/excluir, padrao de `/tags`), filtro por grupo no painel, distintivo Projeto/Area no card e na intro do card.
- Sequencia do Ciclo 2: Fase 8 (dominio + migracao) -> Fase 9 (interface e filtros) -> Fase 10 (validacao + publicacao do banco no servidor via `publish`).
- Possiveis acrecismos futuros (fora do escopo): score agregado do grupo, ordinal por grupo, tela de Arquivo dedicada.

**Bloqueio:** iniciar apenas apos Fases 5, 6 e 7 concluidas (regra de uma fase por vez).


## 7. PARA-lite completo: Recursos e painel em secoes

**Status:** em execucao no Ciclo 3 (2026-10-31); Fases 11 (schema `4` + `recurso`) e 12 (painel em secoes) concluidas, Fase 13 aguardando autorizacao.

**Origem:** o usuario esclareceu que precisa organizar as tasks em Projetos, Areas, Recursos e Arquivos. Isso amplia o item 6, que havia excluido Recursos.

**Decisoes do usuario:**
- `Recursos` sera um tipo de grupo que agrupa tasks (`kind='recurso'`).
- `Arquivos` nao e um novo tipo: e a visao dos grupos com `status='archived'`.
- O painel deve organizar os cards em secoes por grupo, em vez de lista unica com filtro por grupo.

**Desenho previsto:**
- Schema `4`: ampliar `kind` para `projeto`, `area` e `recurso`; `Arquivos` continua usando `status`.
- Painel com titulos de tipo (Projetos, Areas, Recursos, Arquivos, Sem grupo) e uma subsecao por grupo; grupos sem cards ficam em `/grupos`.
- Tela `/grupos` passa a aceitar `recurso`; o formulario de tarefa oferece os tres tipos.
- Ordem prevista do Ciclo 3: Fase 11 (schema `4` + dominio) -> Fase 12 (painel em secoes e gestao) -> Fase 13 (E2E + publicacao).

**Bloqueio:** Fase 13 depende de autorizacao explicita do usuario; respeitar uma fase por vez.

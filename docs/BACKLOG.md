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

**Status:** superado em 2026-11-21. O servidor Termux passou a ser a fonte de verdade; o PC baixa cópias com `flask pull` (validação + backup local) e o antigo `publish` virou exceção com `--force`. Botão da barra superior agora é **Baixar do servidor** (`POST /pull`). Backup diário no Termux via `scripts/ice-backup.sh`.


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

**Status:** em execucao no Ciclo 3 (2026-10-31); Fases 11 (schema `4` + `recurso`) e 12 (painel em secoes) concluidas e Fase 13 (E2E + backup/restauracao + publicacao) executada, aguardando aceite do usuario.

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

**Bloqueio:** nao ha bloqueio tecnico; Ciclo 3 aguarda aceite explicito do usuario.


## 8. Peixe-piloto

**Status:** concluido (2026-10-31, aceite do usuario). Fases 14 (schema `5` + dominio/testes), 15 (interface `/peixe`) e 16 (e-mails/scripts) entregues; publicado no Termux e agendado com `cronie` (diario 08:00, semanal sexta 17:00).

**Escopo:** modulo de prospeccao com leads, interacoes, missao diaria, XP, niveis, streak, quest e badges, no mesmo banco SQLite. Oceanos iniciais: odontologia em Natal. Briefing completo em `peixe-piloto/COMANDOS.md`; contrato do dominio em `CONTRATO-DOMINIO-PEIXE.md`.

**Ciclos previstos:** F14 (dominio + migracao 005) -> F15 (interface `/peixe`) -> F16 (email, agendamento e E2E).

**Bloqueio:** nenhum. Nota: `termux-job-scheduler` indisponivel; agendamento feito com `cronie`/`crond`.


## 9. Edicao de lead no Peixe-piloto

**Status:** implementado (2026-11-20). `PeixeRepository.update_lead` + rotas `GET/POST /peixe/leads/<int:lead_id>/editar`, formulário reaproveitado em modo edição, links **Editar** no detalhe e no pipeline. Status, próxima ação e data de criação preservados; duplicidade de canal/contato ignorando o próprio lead. Link de WhatsApp normaliza `0` inicial e `55` duplicado. Suíte com 110 testes.

**Fora do escopo:** excluir lead, editar status/próxima ação pela tela e histórico de alterações.

**Origem:** necessidade de corrigir telefones e observações dos 5 leads iniciais antes das primeiras abordagens.


## 10. Sincronizacao com o servidor como fonte de verdade

**Status:** implementado (2026-11-21). O banco do Termux passa a ser a fonte de verdade; o PC mantém uma copia para desenvolvimento e backup. `flask pull` cria snapshot consistente no servidor, valida `integrity_check` e `foreign_key_check`, salva backup local em `backups/` e substitui o banco. A rota `POST /pull` e o botao **Baixar do servidor** substituem o antigo **Publicar** (`POST /publish`). `flask publish --force` permanece apenas como recuperacao manual. Backup diario no Termux por `scripts/ice-backup.sh` (cronie 08:30, ultimos 7 arquivos).

**Decisao do usuario:** editar e prospectar de qualquer lugar pelo site; nao querer depender do PC de casa nem lidar com conflitos de sincronizacao.

**Fora do escopo:** sincronizacao bidirecional e resolucao de conflito por registro.

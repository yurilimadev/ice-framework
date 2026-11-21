# Contexto Atual

**Atualizado em:** 2026-11-20

Este arquivo é um snapshot operacional para iniciar uma nova sessão sem reler todo o histórico. Detalhes permanentes devem permanecer nos contratos, no discovery ou no registro de sessões.

## Fase ativa

- **Fases 11 e 12 do Ciclo 3**: concluídas em 2026-10-31.
- **Fase 13**: executada em 2026-10-31 — aguardando aceite do usuário para encerrar o Ciclo 3.
- **Peixe-piloto — Fases 14, 15 e 16**: concluídas em 2026-10-31; módulo publicado no Termux e agendado.
- **Melhoria pós-F16 (2026-11-20)**: edição de lead em `/peixe/leads/<id>/editar` (domínio, rota, formulário, links e testes); link de WhatsApp normaliza `0` inicial e `55` duplicado.
- **Sincronização (2026-11-21)**: o servidor Termux passa a ser a fonte de verdade; `pull`/botão **Baixar do servidor** substituem o fluxo local→servidor; `publish --force` fica como exceção; backup diário no Termux.
- **Abordagem (2026-11-21)**: mensagem gerada em duas linhas, com contato, observação, setor e cidade; sem a dor interna e sem "Estou estudando"; termina com "Posso te fazer 2 perguntas rápidas? Não é venda." O formulário orienta a observação a completar "Vi que...".
- Entregue na Fase 11: `kind='recurso'`, migração `3 -> 4` preservando grupos e vínculos; `Arquivos` segue como `status='archived'`.
- Entregue na Fase 12: painel em seções Projetos, Áreas, Recursos, Arquivos e Sem grupo; tipo Recurso na gestão e no formulário.
- Entregue/validado na Fase 13: E2E local e no Termux, backup/restauração e publicação em schema `4`; servidor espelhando 5 tarefas e 0 grupos.
- Entregue na F14: schema `5` com `leads`, `interactions` e `settings`; domínio Peixe-piloto com XP, níveis, streak, quest, missão diária, follow-ups e badges.
- Entregue na F15: interface `/peixe` (dashboard, pipeline, detalhe, semana e agenda), ações de lead, mensagem gerada, links por canal e sub-identidade coral/âmbar.
- Entregue na F16: e-mails diário/semanal texto+HTML, CLIs `send-peixe-daily`/`send-peixe-weekly`, botões manuais, scripts de agendamento e configuração `PEIXE_TO`.
- App local e online em schema `5`; `/peixe` ativo em `https://ice.yurilimadev.com/peixe`; agendamento via `cronie`/`crond` (diário 08:00, semanal sexta 17:00).
- Ciclo 1 fechado (2026-10-31): Fases 0 a 7 concluídas com aceites do usuário.
- Entregue na Fase 8: schema `3` com `grupos` e `tasks.grupo_id`; CRUD/arquivamento de grupo; vínculo e desvínculo de cards; exclusão preserva tarefas e tags.
- Entregue na Fase 9: tela `/grupos`, campo `grupo_id` no formulário, filtro `group` no painel e badge Projeto/Área nos cards.
- Entregue/validado na Fase 10: E2E local e no Termux, backup/restauração em schema `3`, publicação e espelho no servidor; dados de validação removidos.
- App: código e bancos local/online em schema `4`; servidor espelhando 5 tarefas e 0 grupos. Backups funcionais nas duas pontas.
- Suíte: 76 testes OK.


## Estado das sessões

| Sessão | Status | Próximo passo |
|---|---|---|
| `BE-006` | concluída | Suporte a regressões do domínio de grupos |
| `QA-006` | concluída | Schema `3` validado; Fase 8 encerrada |
| `BE-007` | concluída | Suporte a regressões das rotas de grupo |
| `FE-006` | concluída | Tela `/grupos` e filtros aplicados |
| `QA-007` | concluída | Fluxos de grupo validados; Fase 9 encerrada |
| `QA-008` | concluída | Drills F10 aprovados; Ciclo 2 encerrado |
| `BE-008` | concluída | Schema `4` e `GroupKind.RESOURCE` entregues |
| `QA-009` | concluída | Upgrade `3 -> 4` validado; Fase 11 encerrada |
| `BE-009` | concluída | Contexto de seções entregue |
| `FE-007` | concluída | Painel em seções e tipo Recurso aplicados |
| `QA-010` | concluída | Seções validadas; Fase 12 encerrada |
| `QA-011` | em validação | Drills F13 aprovados; aguardando aceite do usuário |
| `ADM-PEIXE-001` | em validação | F14 entregue; aguardando aceite antes da F15 |
| `ADM-PEIXE-002` | concluída | Edição de lead entregue em 2026-11-20 |
| `BE-010` | concluída | Schema `5` e domínio Peixe-piloto entregues |
| `QA-012` | em validação | 14 testes novos; suíte total com 89 testes OK |
| `BE-011` | concluída | Rotas e contexto `/peixe` entregues |
| `FE-008` | concluída | Interface Peixe-piloto aplicada |
| `QA-013` | concluída | Interface Peixe aprovada para a F16 |
| `QA-014` | concluída | E-mails, publicação e cronie validados; Peixe no ar |
| `BE-003` | concluída | Suporte somente para regressões ou mudanças de contrato |
| `FE-001` | concluída | Interface aprovada na inspeção visual de 2026-10-03 |
| `QA-004` | concluída | Inspeção visual aprovada; 53 testes OK |

## Concluído recentemente

- Fase 3 concluída com contrato HTTP validado.
- Interface visual aplicada em `app/templates/` e `app/static/styles.css`.
- Identidade visual ICE documentada e aplicada.
- Contraste de texto corrigido conforme WCAG AA.
- Fluxos reais, seletores, estados, labels, foco e breakpoints verificados pela sessão de Testes.
- Avisos de sucesso convertidos em flash messages efêmeros (4s, fechamento manual).
- Gerenciamento de tags implementado: `/tags` com renomear, excluir e mesclar; link na navegação; estilos completos.
- Comando CLI `flask --app wsgi send-digest` criado para envio de resumo por email via env vars SMTP.
- Respiros e espaçamentos ajustados em todo o app (tokens `--space-1..6`), sem mudar contrato ou seletores.
- Envio de resumo por email configurado e testado com Gmail real: `.env` local (fora do git), `.env.example`, `python-dotenv` e `env_file` no `compose.yaml`.
- Painel dinâmico na Fase 4: no desktop (`body.panel-mode`) o cabeçalho e os filtros ficam fixos e `.task-area` rola com scroll próprio; painel de filtros compactado (hero e respiros reduzidos; área de tags com limite de altura) para dispensar scroll no filtro; no mobile a rolagem de página é mantida.
- Filtro dinâmico sem recarregar: `app.js` busca a própria página e troca só as regiões `task-area`, `view-count` e `filter-feedback` (sem mudança de contrato HTTP); indicador de espera discreto (régua imediata, aviso 'Atualizando...' após 300ms), estado de erro com aviso; botão 'Aplicar filtros' removido para quem tem JS e mantido apenas via `<noscript>` como fallback; URL atualizada via `replaceState`.
- Botão "Enviar resumo" na barra superior: rota `POST /digest/send` (contrato atualizado), flash de sucesso/erro, botão desabilitado durante o envio e visível apenas com SMTP configurado; flashes de erro agora renderizam em todas as telas (correção: tela de tags nunca exibia flashes).
- Tela de tags no modo painel (desktop ≥801px): cabeçalho fixo e tabela rolando dentro do card; painel fixo agora limitado corretamente a desktop (mobile mantém rolagem normal).
- Email do resumo redesenhado na identidade ICE com versão texto puro anexada (multipart/alternative).
- Lançador local fora do repositório: comando `ice` (`~/.local/bin`) e ícone "ICE Framework" no GNOME (`app-framework.desktop`); sobe o servidor se necessário e abre `http://127.0.0.1:5000`.
- Sincronização local -> servidor (2026-10-10): CLI `publish` + botão `Publicar` (rota `POST /publish`); regra antiga: local publica, servidor espelha. **Superada em 2026-11-21.**
- Servidor como fonte de verdade (2026-11-21): CLI `pull` + botão **Baixar do servidor** (`POST /pull`) baixam snapshot consistente, validam integridade, salvam backup local e substituem o banco; `publish` virou exceção com `--force`. Backup diário no Termux por `scripts/ice-backup.sh` (cronie 08:30, últimos 7). 114 testes.
- Correção da Fase 5: `merge_tags` com tags compartilhadas na mesma tarefa (BE-F5-001) corrigido; suíte com regressão nova.
- Ciclo 2 ativado em 2026-10-31 a pedido do usuário; Fases 8/9/10 transpostas para `Fases-de-Desenvolvimento.md` e `ADM-F8-001` aberto para Backend e Testes.
- Fase 8 concluída: migração `003_grupos.sql` (schema `3`), `GroupRepository`, vínculo `tasks.grupo_id` e `tests/test_groups.py`; upgrade de cópia do banco local `2 -> 3` preservou 5 tarefas e 5 tags; excluir grupo solta cards sem excluir tags.
- Fase 9 concluída: rotas `/grupos` e filtro `group`, tela de gestão, campo `grupo_id` nos formulários e badge Projeto/Área nos cards; verificação HTTP local em `/`, `/grupos`, `/tasks/new`, `/?group=<id>` e `/?group=none` com `200`.
- Fase 10 concluída: E2E local e no Termux, reinício, backup/restauração com schema `3`, publicação e espelho no servidor; código remoto em `982e877`; grupo/card de validação removidos e servidor republicado com 5 tarefas e 0 grupos. Evidência em `docs/VALIDACAO-E2E-F10.md`.
- Ciclo 2 fechado com aceite do usuário (2026-10-31).
- Fase 11 concluída: migração `004_grupos_recurso.sql` (schema `4`), `GroupKind.RESOURCE` e preservação de grupos/vínculos; suíte com regressões de upgrade `3 -> 4`.
- Fase 12 concluída: painel em seções Projetos/Áreas/Recursos/Arquivos/Sem grupo, tipo Recurso em `/grupos` e no formulário, filtro de grupo removido; verificação HTTP local com as cinco seções.
- Fase 13 executada: E2E local e no Termux, backup/restauração e publicação em schema `4`; dados de validação removidos; evidência em `docs/VALIDACAO-E2E-F13.md`.
- Ajuste de interface pós-validação: blocos de grupo recolhíveis (`<details>`), fechados por padrão, com botão `Expandir grupos`/`Recolher grupos`.
- Fase 14 executada: migração `005_peixe.sql` (schema `5`), `PeixeRepository` e 14 testes de domínio; upgrade `4 -> 5` validado em cópia do banco real.
- Fase 15 executada: dashboard, pipeline, detalhe, semana e agenda em `/peixe`; mensagem/links por canal, ações de lead, cópia e sub-identidade visual; 10 testes de rotas.
- Fase 16 concluída: e-mails diário/semanal reais (local e servidor), publicação no Termux em schema `5`, `/peixe` online `200` e agendamento via `cronie` (diário 08:00, semanal sexta 17:00).
- Melhoria de 2026-11-20: `PeixeRepository.update_lead` + rotas `GET/POST /peixe/leads/<id>/editar`, formulário reaproveitado em modo edição, link **Editar** no detalhe e no pipeline; `status`, `next_action_at` e `created_at` preservados; duplicidade ignorando o próprio lead. Link de WhatsApp passou a normalizar `0` inicial e `55` duplicado. 5 testes novos.
- Suíte automatizada atual: `114` testes, resultado `OK`.

## Bloqueio atual

Nenhum bloqueio de projeto. Observação: `termux-job-scheduler` não existe no repositório Termux atual; o agendamento usa `cronie`/`crond` (diário às 08:00, semanal sexta às 17:00).

## Próxima decisão

Usar a edição para corrigir os 5 leads de odontologia em Natal (telefones e observações) e iniciar as primeiras abordagens **pelo site**, que agora é a fonte de verdade. O PC deve rodar `python3 -m flask --app wsgi pull` quando precisar de uma cópia atualizada; não usar `publish` sem `--force`. Refinar o tutorial do Peixe (`docs/peixe-piloto/TUTORIAL.md`) e definir melhorias futuras fora da v1. O aceite da Fase 13/Ciclo 3 também continua pendente. Handoffs de encerramento: `ADM-F16-CLOSE-001` e `ADM-PEIXE-CLOSE-001`.

## Backlog

- `BACKLOG.md` item 8: Peixe-piloto concluído (F14-F16) e publicado; agendamento via `cronie`.
- `BACKLOG.md` item 10: sincronização com o servidor como fonte de verdade (2026-11-21).
- `BACKLOG.md` item 7: Recursos e painel em seções (Ciclo 3); Fases 11 e 12 concluídas, Fase 13 executada e aguardando aceite.
- `BACKLOG.md` item 6: grupos Projeto/Área concluídos no Ciclo 2 (Fases 8 a 10).
- Demais demandas registradas: filtro de tags, agendamento de notificações por email, cron de publicação.

## Referências obrigatórias

- `Fases-de-Desenvolvimento.md`
- `sessoes/Administracao-de-Sessoes.md`
- `sessoes/Sessao-Frontend.md`
- `sessoes/Sessao-Testes.md`
- `IDENTIDADE-VISUAL.md`
- `CONTRATO-APLICACAO.md`

## Último versionamento

- Último commit de código publicado: `0a71404` (mensagem enxuta de abordagem), em `main` e implantado no Termux em 2026-11-21.
- Dados: leads 1 a 4 com contatos curtos e observações reescritas; SouSmile (5) mantido fora da primeira leva.
- Alterações locais pendentes: nenhuma.

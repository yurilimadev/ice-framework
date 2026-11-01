# Contexto Atual

**Atualizado em:** 2026-10-31

Este arquivo é um snapshot operacional para iniciar uma nova sessão sem reler todo o histórico. Detalhes permanentes devem permanecer nos contratos, no discovery ou no registro de sessões.

## Fase ativa

- **Fases 11 e 12 do Ciclo 3**: concluídas em 2026-10-31.
- **Fase 13**: executada em 2026-10-31 — aguardando aceite do usuário para encerrar o Ciclo 3.
- Entregue na Fase 11: `kind='recurso'`, migração `3 -> 4` preservando grupos e vínculos; `Arquivos` segue como `status='archived'`.
- Entregue na Fase 12: painel em seções Projetos, Áreas, Recursos, Arquivos e Sem grupo; tipo Recurso na gestão e no formulário.
- Entregue/validado na Fase 13: E2E local e no Termux, backup/restauração e publicação em schema `4`; servidor espelhando 5 tarefas e 0 grupos.
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
- Sincronização local -> servidor (2026-10-10): CLI `publish` + botão `Publicar` (rota `POST /publish`, contrato atualizado); snapshot consistente via backup API + scp + restart do serviço remoto; regra: local publica, servidor espelha; verificado ponta a ponta (tarefa-teste publicada e vista em `ice.yurilimadev.com`).
- Correção da Fase 5: `merge_tags` com tags compartilhadas na mesma tarefa (BE-F5-001) corrigido; suíte com regressão nova.
- Ciclo 2 ativado em 2026-10-31 a pedido do usuário; Fases 8/9/10 transpostas para `Fases-de-Desenvolvimento.md` e `ADM-F8-001` aberto para Backend e Testes.
- Fase 8 concluída: migração `003_grupos.sql` (schema `3`), `GroupRepository`, vínculo `tasks.grupo_id` e `tests/test_groups.py`; upgrade de cópia do banco local `2 -> 3` preservou 5 tarefas e 5 tags; excluir grupo solta cards sem excluir tags.
- Fase 9 concluída: rotas `/grupos` e filtro `group`, tela de gestão, campo `grupo_id` nos formulários e badge Projeto/Área nos cards; verificação HTTP local em `/`, `/grupos`, `/tasks/new`, `/?group=<id>` e `/?group=none` com `200`.
- Fase 10 concluída: E2E local e no Termux, reinício, backup/restauração com schema `3`, publicação e espelho no servidor; código remoto em `982e877`; grupo/card de validação removidos e servidor republicado com 5 tarefas e 0 grupos. Evidência em `docs/VALIDACAO-E2E-F10.md`.
- Ciclo 2 fechado com aceite do usuário (2026-10-31).
- Fase 11 concluída: migração `004_grupos_recurso.sql` (schema `4`), `GroupKind.RESOURCE` e preservação de grupos/vínculos; suíte com regressões de upgrade `3 -> 4`.
- Fase 12 concluída: painel em seções Projetos/Áreas/Recursos/Arquivos/Sem grupo, tipo Recurso em `/grupos` e no formulário, filtro de grupo removido; verificação HTTP local com as cinco seções.
- Fase 13 executada: E2E local e no Termux, backup/restauração e publicação em schema `4`; dados de validação removidos; evidência em `docs/VALIDACAO-E2E-F13.md`.
- Suíte automatizada atual: `75` testes, resultado `OK`.

## Bloqueio atual

Nenhum bloqueio de projeto. Nota de infra (2026-10-31): o Android descarregou e saiu do ar; recolocado pelo usuário — serviços voltaram sozinhos ao abrir o Termux, wake-lock reaplicado, `https://ice.yurilimadev.com` saudável de novo. Recomendo reserva de DHCP no roteador e a reabertura do Termux após qualquer reinício.

## Próxima decisão

Ouvir o usuário sobre o aceite da Fase 13; se aprovado, marcar a Fase 13 e o Ciclo 3 como concluídos. Depois, definir o próximo ciclo/backlog. Handoffs da Fase 13: `QA-F13-001`, `INFRA-F13-001` e `ADM-F13-HOLD-001`.

## Backlog

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

- Último commit publicado: `33190be` (Ciclo 3: Recursos e painel em seções com schema `4`).
- Alterações locais pendentes: documentação da Fase 13 (`VALIDACAO-E2E-F13.md` e snapshots); nenhuma alteração de código pendente.

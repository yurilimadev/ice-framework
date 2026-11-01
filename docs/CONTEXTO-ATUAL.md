# Contexto Atual

**Atualizado em:** 2026-10-31

Este arquivo é um snapshot operacional para iniciar uma nova sessão sem reler todo o histórico. Detalhes permanentes devem permanecer nos contratos, no discovery ou no registro de sessões.

## Fase ativa

- **Fases 8 e 9 do Ciclo 2**: concluídas em 2026-10-31.
- Entregue na Fase 8: schema `3` com `grupos` e `tasks.grupo_id`; CRUD/arquivamento de grupo; vínculo e desvínculo de cards; exclusão preserva tarefas e tags.
- Entregue na Fase 9: tela `/grupos`, campo `grupo_id` no formulário, filtro `group` no painel e badge Projeto/Área nos cards.
- Fase 10 (validação E2E e publicação no servidor) pronta para ativação, aguardando autorização do usuário.
- Ciclo 1 fechado (2026-10-31): Fases 0 a 7 concluídas com aceites do usuário.
- App: instância local íntegra + `https://ice.yurilimadev.com` no ar com Access; backups funcionais nas duas pontas (drills aprovados).
- Suíte: 74 testes OK (baseline da Fase 10).


## Estado das sessões

| Sessão | Status | Próximo passo |
|---|---|---|
| `BE-006` | concluída | Suporte a regressões do domínio de grupos |
| `QA-006` | concluída | Schema `3` validado; Fase 8 encerrada |
| `BE-007` | concluída | Suporte a regressões das rotas de grupo |
| `FE-006` | concluída | Tela `/grupos` e filtros aplicados |
| `QA-007` | concluída | Fluxos de grupo validados; Fase 9 encerrada |
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
- Suíte automatizada atual: `74` testes, resultado `OK`.

## Bloqueio atual

Nenhum bloqueio de projeto. A Fase 10 está pronta para ativação, mas não foi aberta. Nota de infra (2026-10-31): o Android descarregou e saiu do ar; recolocado pelo usuário — serviços voltaram sozinhos ao abrir o Termux, wake-lock reaplicado, `https://ice.yurilimadev.com` saudável de novo. Recomendo reserva de DHCP no roteador e a reabertura do Termux após qualquer reinício.

## Próxima decisão

Abrir a **Fase 10 — validação E2E e publicação dos grupos** quando o usuário autorizar: executar o roteiro dos grupos nas duas instâncias, validar backup/restauração com schema `3` e publicar no servidor via `publish`. Handoffs da Fase 9: `BE-F9-001`, `FE-F9-001`, `QA-F9-001` e `ADM-F9-CLOSE-001`.

## Backlog

- `BACKLOG.md` item 6: grupos Projeto/Área em execução (Ciclo 2, Fases 8 e 9 concluídas; Fase 10 pendente).
- Demais demandas registradas: filtro de tags, agendamento de notificações por email, cron de publicação.

## Referências obrigatórias

- `Fases-de-Desenvolvimento.md`
- `sessoes/Administracao-de-Sessoes.md`
- `sessoes/Sessao-Frontend.md`
- `sessoes/Sessao-Testes.md`
- `IDENTIDADE-VISUAL.md`
- `CONTRATO-APLICACAO.md`

## Último versionamento

- Último commit publicado: `47eb23e` (Ciclo 1 completo; semanas de 2026-10-07 a 10-31).
- Alterações locais pendentes: Fases 8 e 9 implementadas (`migrations/003_grupos.sql`, `app/tasks.py`, `app/routes.py`, templates, `styles.css`, testes e documentação do Ciclo 2); nada commitado.

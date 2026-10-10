# Contexto Atual

**Atualizado em:** 2026-09-27

Este arquivo é um snapshot operacional para iniciar uma nova sessão sem reler todo o histórico. Detalhes permanentes devem permanecer nos contratos, no discovery ou no registro de sessões.

## Fase ativa

- Fase concluída: **Fase 4 - Interface do frontend** (encerrada em 2026-10-03, inspeção visual aprovada pelo usuário).
- Próxima fase: **Fase 5 - Integração ponta a ponta** — pronta para ativação.
- Sessões previstas para a Fase 5: backend, frontend e testes.
- Critério de saída da Fase 5: fluxos ponta a ponta passam sem dados ou regras duplicadas de forma conflitante.

## Estado das sessões

| Sessão | Status | Próximo passo |
|---|---|---|
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
- Suíte automatizada atual: `53` testes, resultado `OK` (inclui `tests/test_digest.py`).

## Bloqueio atual

Nenhum bloqueio. Migração concluída (2026-10-09): app no ar em `https://ice.yurilimadev.com` com Cloudflare Access ativo e testes ponta a ponta aprovados pelo usuário.

## Próxima decisão

Sessão de 2026-10-10: desenhar e escolher o mecanismo de sincronização local <-> servidor Termux (CLI `publish`, botão na interface e/ou cron) — detalhes em `BACKLOG.md` item 5. Depois: ativar a Fase 5 - Integração ponta a ponta.

## Backlog

- `BACKLOG.md`: demandas futuras registradas (gerenciamento de tags, filtro dinâmico, notificações por email).

## Referências obrigatórias

- `Fases-de-Desenvolvimento.md`
- `sessoes/Administracao-de-Sessoes.md`
- `sessoes/Sessao-Frontend.md`
- `sessoes/Sessao-Testes.md`
- `IDENTIDADE-VISUAL.md`
- `CONTRATO-APLICACAO.md`

## Último versionamento

- Último commit publicado: `2e36d91` (Fases 3 e 4 completas no GitHub).
- Sem alterações locais pendentes de commit.

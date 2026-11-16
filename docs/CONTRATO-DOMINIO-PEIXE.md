# Contrato do Domínio Peixe-piloto

Este documento descreve o módulo Peixe-piloto, implementado na Fase 14. Ele usa o mesmo SQLite do ICE, mas mantém tabelas e regras separadas de `tasks` e `grupos`.

## Lead

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Identificador persistido, maior que zero |
| `company` | texto | Obrigatório, espaços externos removidos, 1 a 120 caracteres |
| `contact` | texto ou vazio | Nome do contato, opcional |
| `sector` | texto | Obrigatório, 1 a 60 caracteres |
| `city` | texto | Obrigatório, 1 a 60 caracteres |
| `channel` | texto | `whatsapp`, `linkedin`, `email`, `instagram` ou `presencial` |
| `handle` | texto | Obrigatório, 1 a 200 caracteres |
| `observation` | texto | Obrigatório, 1 a 200 caracteres |
| `status` | texto | Um dos status abaixo; começa em `novo` |
| `next_action_at` | data ou vazio | Data sem horário no formato `YYYY-MM-DD` |
| `created_at` | timestamp | Instante UTC em ISO 8601 |
| `updated_at` | timestamp | Instante UTC em ISO 8601 |

O par `(channel, handle)` é único.

## Status e transições

Cadeia principal:

```text
novo -> a_enviar -> enviado -> respondeu -> conversa -> proposta -> piloto -> ganho
```

- `pausado` pode ocorrer a partir de `enviado` ou de um status posterior da cadeia ativa.
- `pausado` pode voltar para `enviado`.
- `perdido` pode ocorrer a partir de qualquer status ativo, inclusive `pausado`.
- `ganho` e `perdido` são terminais.
- Transições fora dessas regras geram `ValidationError` no campo `status`.

## Interação

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Identificador persistido |
| `lead_id` | inteiro | Referência a `leads`; exclusão do lead remove as interações |
| `kind` | texto | `mensagem`, `resposta`, `conversa`, `proposta`, `piloto`, `nota` ou `pausa` |
| `channel` | texto | Canal do lead ou `sistema` |
| `notes` | texto ou vazio | Observação livre |
| `created_at` | timestamp | Instante UTC em ISO 8601 |

Regra especial: registrar uma `mensagem`:

- muda o status do lead para `enviado`, salvo lead `ganho`/`perdido`;
- define `next_action_at` para a data local do envio + 3 dias;
- atualiza `updated_at`.

## Gamificação

XP por interação:

| Tipo | XP |
|---|---:|
| `mensagem` | 10 |
| `resposta` | 15 |
| `conversa` | 30 |
| `proposta` | 50 |
| `piloto` | 150 |
| `nota` | 0 |
| `pausa` | 0 |

Níveis:

| XP | Nível |
|---|---|
| menos de 100 | Aprendiz |
| 100 a 299 | Piloto |
| 300 a 699 | Timoneiro |
| 700 ou mais | Capitão |

Regras:

- `streak`: dias locais consecutivos com pelo menos uma `mensagem`, contando a partir de hoje ou de ontem.
- `weekly_progress`: contagens da semana local (segunda a domingo) de mensagens, respostas e conversas.
- Meta semanal padrão: 5 mensagens, 2 respostas e 1 conversa.
- Badges: `primeira_mensagem`, `primeira_resposta`, `primeira_conversa`, `primeiro_piloto`, `streak_4_semanas`.

## Missão e follow-ups

- `daily_mission`: primeiro lead com status `a_enviar` ou `enviado` e `next_action_at` vazio ou anterior/igual a hoje. A ordenação prioriza follow-ups vencidos e depois usa `created_at` e `id`.
- `followups_due`: leads `enviado` com `next_action_at` anterior a hoje.
- `pipeline_counts`: contagem de leads por status, incluindo zeros.

## Persistência

O schema `5` adiciona as tabelas `leads`, `interactions` e `settings`. A migração é aditiva: `tasks`, `tags`, `task_tags` e `grupos` não são alterados. `settings` começa com `daily_target`, `weekly_messages`, `weekly_replies`, `weekly_conversations`, `current_ocean` e `current_city`.

## Operações

O `PeixeRepository` fornece:

- `create_lead`, `get_lead`, `list_leads`, `update_status`, `set_next_action`.
- `log_interaction`, `list_interactions`.
- `daily_mission`, `followups_due`, `pipeline_counts`.
- `xp_total`, `level`, `streak`, `weekly_progress`, `badges`.
- `get_setting`, `set_setting` para `settings` (metas, oceano, cidade, dor, aprendizado e bloqueio).

Entradas inválidas geram `ValidationError`; lead inexistente gera `LeadNotFoundError`.

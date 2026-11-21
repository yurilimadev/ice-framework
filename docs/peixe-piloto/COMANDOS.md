# Peixe-piloto — comandos de implementação no ICE

Briefing de execução para o agente que trabalha no repositório ICE. Execute **uma fase por vez**, pare ao fim de cada uma e aguarde aceite.

## 0. Ordem de execução

1. Ler `docs/README.md` e `docs/CONTEXTO-ATUAL.md`.
2. Ler `AGENTS.md`, `docs/CONTRATO-DOMINIO.md` e `docs/CONTRATO-APLICACAO.md`.
3. Registrar a sessão `ADM-PEIXE-001` em `docs/sessoes/Administracao-de-Sessoes.md`.
4. Executar F14. Não iniciar F15 antes do aceite da F14.
5. Ao fim de cada fase, atualizar `docs/CONTEXTO-ATUAL.md` com estado, verificação, pendências e próximo passo.

## 1. Contexto

Adicionar um módulo **Peixe-piloto** ao app ICE, com uma aba própria e o mesmo banco SQLite. O módulo é o cockpit diário de prospecção: um lead, uma mensagem, um registro, XP, streak e quest. O oceano inicial é **odontologia em Natal**.

Não criar app separado. Não alterar o comportamento de `tasks` ou `grupos`.

## 2. F14 — Domínio, migração 005 e testes

### 2.1 Criar `migrations/005_peixe.sql`

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    company TEXT NOT NULL CHECK (length(trim(company)) BETWEEN 1 AND 120),
    contact TEXT,
    sector TEXT NOT NULL CHECK (length(trim(sector)) BETWEEN 1 AND 60),
    city TEXT NOT NULL CHECK (length(trim(city)) BETWEEN 1 AND 60),
    channel TEXT NOT NULL CHECK (channel IN ('whatsapp', 'linkedin', 'email', 'instagram', 'presencial')),
    handle TEXT NOT NULL CHECK (length(trim(handle)) BETWEEN 1 AND 200),
    observation TEXT NOT NULL CHECK (length(trim(observation)) BETWEEN 1 AND 200),
    status TEXT NOT NULL DEFAULT 'novo' CHECK (status IN (
        'novo', 'a_enviar', 'enviado', 'respondeu', 'conversa',
        'proposta', 'piloto', 'ganho', 'perdido', 'pausado'
    )),
    next_action_at TEXT CHECK (next_action_at IS NULL OR length(next_action_at) = 10),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_leads_channel_handle ON leads (channel, handle);
CREATE INDEX idx_leads_status ON leads (status);
CREATE INDEX idx_leads_next_action ON leads (next_action_at);
CREATE INDEX idx_leads_created_at ON leads (created_at);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    lead_id INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN (
        'mensagem', 'resposta', 'conversa', 'proposta', 'piloto', 'nota', 'pausa'
    )),
    channel TEXT NOT NULL CHECK (channel IN ('whatsapp', 'linkedin', 'email', 'instagram', 'presencial', 'sistema')),
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_interactions_lead ON interactions (lead_id);
CREATE INDEX idx_interactions_kind_created ON interactions (kind, created_at);
CREATE INDEX idx_interactions_created ON interactions (created_at);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO settings (key, value) VALUES
    ('daily_target', '1'),
    ('weekly_messages', '5'),
    ('weekly_replies', '2'),
    ('weekly_conversations', '1'),
    ('current_ocean', 'odontologia'),
    ('current_city', 'Natal');

PRAGMA user_version = 5;
```

Regras da migração:
- Aditiva. Não tocar em `tasks`, `tags`, `task_tags` ou `grupos`.
- Testar banco novo (schema `5`) e upgrade `4 -> 5` com dados existentes.
- Rodar `PRAGMA foreign_key_check` no teste.

### 2.2 Criar `app/peixe.py`

Seguir o padrão de `app/tasks.py`: dataclasses, validações com `ValidationError`, repositório com `sqlite3.Connection`, timestamps UTC em ISO 8601 e datas no fuso `APP_TIMEZONE`.

Implementar:

- `Lead` e `Interaction` como dataclasses validadas.
- `PeixeRepository` com:
  - `create_lead`, `get_lead`, `list_leads`, `update_status`, `set_next_action`
  - `log_interaction`, `list_interactions`
  - `daily_mission`, `followups_due`, `pipeline_counts`
  - `xp_total`, `level`, `streak`, `weekly_progress`, `badges`
- `xp_for(kind)`:
  - `mensagem` 10, `resposta` 15, `conversa` 30, `proposta` 50, `piloto` 150, `nota` 0, `pausa` 0.
- `level_for(xp)`:
  - `< 100`: Aprendiz
  - `< 300`: Piloto
  - `< 700`: Timoneiro
  - `>= 700`: Capitão
- `streak`: dias locais consecutivos com pelo menos uma interação `mensagem`, contando a partir de hoje ou de ontem.
- `weekly_progress`: contagens da semana local (segunda a domingo) para mensagens, respostas e conversas.
- `daily_mission`: primeiro lead com status `a_enviar` ou `enviado` e `next_action_at` vazio ou `<= hoje`, ordenado por `next_action_at`, `created_at` e `id`.
- `badges`: primeira mensagem, primeira resposta, primeira conversa, primeiro piloto, streak de 4 semanas.

Transições permitidas:
- `novo -> a_enviar -> enviado -> respondeu -> conversa -> proposta -> piloto -> ganho`
- `pausado` pode ocorrer depois de `enviado`.
- `perdido` pode ocorrer depois de qualquer status ativo.
- Registrar cada ação em `interactions`.

Ao registrar `mensagem`:
- status passa para `enviado`;
- `next_action_at` recebe `hoje + 3 dias`;
- `updated_at` é atualizado.

### 2.3 Testes

Criar `tests/test_peixe_domain.py` com:

- migração em banco novo: `PRAGMA user_version = 5`;
- upgrade `4 -> 5` preservando `tasks`, `tags` e `grupos`;
- `PRAGMA foreign_key_check` limpo;
- XP por tipo de interação;
- limites de nível;
- streak com dias consecutivos;
- streak quebrado por um dia sem mensagem;
- progresso semanal de mensagens, respostas e conversas;
- transições de status válidas e inválidas;
- unicidade de `(channel, handle)`;
- `daily_mission` prioriza follow-up vencido;
- `followups_due` retorna apenas leads `enviado` com data vencida.

### 2.4 Documentação da F14

- Adicionar seção "Peixe-piloto" em `docs/CONTRATO-DOMINIO.md`, ou criar `docs/CONTRATO-DOMINIO-PEIXE.md` e linkar no roteador.
- Registrar a fase em `docs/Fases-de-Desenvolvimento.md`.
- Atualizar `docs/CONTEXTO-ATUAL.md`.

### 2.5 Comandos

```bash
cd "/home/limaydr/Ciclo de Estudos"
python3 -m unittest discover -s tests -v
python3 -c "import sqlite3; c=sqlite3.connect('data/app.sqlite3'); print(c.execute('PRAGMA user_version').fetchone())"
python3 -m flask --app wsgi run
curl http://127.0.0.1:5000/health
```

### 2.6 Aceite da F14

- Banco novo e banco `4` migram para `5` sem perda.
- Todas as regras acima cobertas por teste.
- Suíte completa verde.
- Nenhuma mudança de comportamento em `tasks` ou `grupos`.

Pare aqui e aguarde aceite antes da F15.

## 3. F15 — Interface `/peixe` e gamificação

### 3.1 Criar `app/peixe_routes.py`

Registrar o blueprint em `app/__init__.py`.

Rotas:

| Método | Rota | Ação |
|---|---|---|
| GET | `/peixe` | dashboard do dia |
| GET | `/peixe/leads` | pipeline com filtro por status |
| GET | `/peixe/leads/new` | formulário rápido |
| POST | `/peixe/leads` | criar lead e redirecionar `303` |
| GET | `/peixe/leads/<int:lead_id>` | detalhe e timeline |
| POST | `/peixe/leads/<int:lead_id>/send` | registrar mensagem enviada |
| POST | `/peixe/leads/<int:lead_id>/reply` | registrar resposta |
| POST | `/peixe/leads/<int:lead_id>/conversation` | registrar conversa |
| POST | `/peixe/leads/<int:lead_id>/proposal` | registrar proposta |
| POST | `/peixe/leads/<int:lead_id>/pilot` | registrar piloto |
| POST | `/peixe/leads/<int:lead_id>/pause` | pausar lead |
| POST | `/peixe/leads/<int:lead_id>/note` | adicionar nota |
| GET | `/peixe/semana` | fechamento semanal |
| GET | `/peixe/agenda` | próximos 7 dias |

Seguir o padrão do app: Post/Redirect/Get, flash messages, `404` para lead inexistente, `400` para validação.

### 3.2 Templates

Criar em `app/templates/peixe/`:

- `dashboard.html` — missão do dia, XP, nível, streak, quest, follow-ups, top 3 prioridades do ICE (somente leitura), botões de ação.
- `leads.html` — lista por status com contagem.
- `lead_form.html` — empresa, contato, setor, cidade, canal, handle, observação.
- `lead_detail.html` — dados, timeline e ações.
- `week.html` — números da semana, aprendizado, bloqueio, próximos 5 nomes.
- `agenda.html` — próximos 7 dias.
- `_macros.html` — barra de XP, chama de streak, anel da quest, badge de nível.

Adicionar link "Peixe" na navegação de `base.html`.

### 3.3 Script e links

Gerar a mensagem no servidor, no formato (revisado em 2026-11-21):

```text
Oi, {contato}, tudo bem? Vi que {observação}.
Estou pesquisando como {setor} de {cidade} organizam a agenda e conquistam pacientes novos.
São 2 perguntas rápidas, sem venda — pode ser por aqui?
```

`{setor}` vira "clínicas odontológicas" para odontologia e "clínicas de {setor}" nos demais. `settings.current_pain` não entra mais na mensagem.

Links por canal:
- WhatsApp: `https://wa.me/55{numero}?text={texto_urlencoded}`
- E-mail: `mailto:{email}?subject={assunto}&body={texto_urlencoded}`
- LinkedIn: abrir o perfil e copiar a mensagem.
- Instagram: abrir o perfil e copiar a mensagem.

Botão **Copiar mensagem** usa `navigator.clipboard` com fallback para seleção de texto.

### 3.4 Visual

- Reusar os tokens de `styles.css` (`--ink`, `--petrol`, `--cyan`, `--surface`).
- Sub-identidade peixe: fundo petróleo, destaque coral ou âmbar para XP/streak, ciano para ação primária.
- Manter contraste WCAG AA, foco visível, labels e responsividade.
- A tela `/peixe` deve funcionar em 320px de largura.

### 3.5 Testes

Criar `tests/test_peixe_routes.py` com:

- `GET /peixe` responde `200` e mostra a missão;
- criar lead redireciona `303` e aparece na lista;
- registrar envio altera status, cria interação, define follow-up e aumenta XP;
- registrar resposta, conversa, proposta e piloto;
- lead inexistente responde `404`;
- validação inválida responde `400` com erro no campo;
- `GET /peixe/semana` mostra os números corretos;
- `GET /peixe/agenda` mostra os próximos 7 dias.

### 3.6 Documentação da F15

- Atualizar `docs/CONTRATO-APLICACAO.md` com rotas, formulários e contexto.
- Atualizar `docs/IDENTIDADE-VISUAL.md` com a sub-identidade peixe.
- Atualizar `docs/CONTEXTO-ATUAL.md`.

### 3.7 Comandos

```bash
cd "/home/limaydr/Ciclo de Estudos"
python3 -m unittest discover -s tests -v
python3 -m flask --app wsgi run
curl -s http://127.0.0.1:5000/peixe | head
```

### 3.8 Aceite da F15

- Fluxo completo com backend real: criar lead, ver missão, enviar, registrar, ver XP/streak/quest.
- Inspeção visual aprovada em desktop e mobile.
- Nenhuma regressão em `/`, `/grupos` ou `/tags`.

Pare aqui e aguarde aceite antes da F16.

## 4. F16 — Email, agendamento e E2E

### 4.1 Criar `app/peixe_digest.py`

Seguir o padrão de `app/digest.py`:

- `render_daily_text`, `render_daily_html`
- `render_weekly_text`, `render_weekly_html`
- `send_peixe_daily(app, recipient=None)`
- `send_peixe_weekly(app, recipient=None)`

Configuração:
- `PEIXE_TO` com fallback para `DIGEST_TO`.
- Reusar `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`.

Conteúdo diário:
- assunto: `Peixe-piloto — missão de hoje`;
- empresa, contato, canal, observação, script;
- streak, XP e nível;
- follow-ups vencidos;
- link para `/peixe`.

Conteúdo semanal:
- assunto: `Peixe-piloto — fechamento da semana`;
- mensagens, respostas, conversas, propostas e pilotos;
- resultado da quest e status do doce;
- link para `/peixe/semana`.

Nunca incluir dado sensível de cliente. Só empresa, contato público e observação.

### 4.2 CLI

Adicionar em `app/__init__.py`:

```python
@app.cli.command("send-peixe-daily")
@click.option("--to", "to_address", default=None, help="Email de destino.")
def send_peixe_daily_command(to_address):
    from .peixe_digest import send_peixe_daily
    click.echo(send_peixe_daily(app, recipient=to_address))
```

Repetir para `send-peixe-weekly`.

Adicionar botões manuais na tela `/peixe`, visíveis apenas com SMTP configurado.

### 4.3 Variáveis

Atualizar `app/config.py` e `.env.example`:

```text
PEIXE_TO=seuemail@gmail.com
```

### 4.4 Agendamento no Termux

Criar `scripts/peixe-daily.sh` e `scripts/peixe-weekly.sh`:

```bash
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/ice-framework" || exit 1
set -a
. ./.env
set +a
./.venv/bin/python -m flask --app wsgi send-peixe-daily >> "$HOME/.local/state/ice-framework/peixe.log" 2>&1
```

```bash
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/ice-framework" || exit 1
set -a
. ./.env
set +a
./.venv/bin/python -m flask --app wsgi send-peixe-weekly >> "$HOME/.local/state/ice-framework/peixe.log" 2>&1
```

```bash
chmod +x scripts/peixe-daily.sh scripts/peixe-weekly.sh
```

Agendar com `termux-job-scheduler` (confirmar flags com `termux-job-scheduler --help`):

```bash
pkg install termux-job-scheduler
termux-job-scheduler --script "$HOME/ice-framework/scripts/peixe-daily.sh" --period-ms 86400000
termux-job-scheduler --script "$HOME/ice-framework/scripts/peixe-weekly.sh" --period-ms 604800000
```

Alternativa: `crond` ou serviço `sv` com loop; registrar a escolha no runbook.

### 4.5 Agendamento em VPS Linux (opcional)

Se migrar para VPS, usar systemd:

```ini
# /etc/systemd/system/peixe-daily.service
[Unit]
Description=Peixe-piloto daily email

[Service]
Type=oneshot
WorkingDirectory=/srv/ice
EnvironmentFile=/srv/ice/.env
ExecStart=/srv/ice/.venv/bin/python -m flask --app wsgi send-peixe-daily
```

```ini
# /etc/systemd/system/peixe-daily.timer
[Unit]
Description=Peixe-piloto daily email timer

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Repetir para `peixe-weekly` com `OnCalendar=Fri 17:00:00`.

```bash
systemctl daemon-reload
systemctl enable --now peixe-daily.timer peixe-weekly.timer
systemctl list-timers 'peixe-*'
```

### 4.6 E2E e publicação

```bash
cd "/home/limaydr/Ciclo de Estudos"
python3 -m unittest discover -s tests -v
python3 -m flask --app wsgi send-peixe-daily --to seuemail@gmail.com
python3 -m flask --app wsgi send-peixe-weekly --to seuemail@gmail.com
python3 -m flask --app wsgi publish
```

Validar:
- email real recebido nos dois formatos;
- dados preservados após reinício;
- backup/restauração com schema `5`;
- publicação no Termux e `/peixe` acessível em `https://ice.yurilimadev.com/peixe`;
- `GET /health` responde `schema_version: 5`.

### 4.7 Documentação da F16

- Atualizar `docs/CONTRATO-APLICACAO.md` com as rotas de email.
- Atualizar `AGENTS.md` com os comandos CLI.
- Criar `docs/VALIDACAO-E2E-PEIXE.md` com a evidência.
- Atualizar `docs/CONTEXTO-ATUAL.md` e `docs/BACKLOG.md`.

### 4.8 Aceite da F16

- Email diário e semanal recebidos.
- Dados preservados após restart e publicação.
- Suíte verde.
- Nenhuma credencial commitada.

## 5. Regras de gamificação

| Ação | XP |
|---|---:|
| mensagem enviada | 10 |
| resposta registrada | 15 |
| conversa realizada | 30 |
| proposta enviada | 50 |
| piloto fechado | 150 |

| Nível | XP |
|---|---:|
| Aprendiz | 0 |
| Piloto | 100 |
| Timoneiro | 300 |
| Capitão | 700 |

- Streak: dias consecutivos com pelo menos uma mensagem. Sem congelamento na v1.
- Quest semanal: 5 mensagens, 2 respostas, 1 conversa.
- Doce liberado quando 5/5 mensagens na semana.
- Badges: primeira mensagem, primeira resposta, primeira conversa, primeiro piloto, streak de 4 semanas.
- Recompensa sempre por **enviar**, nunca por receber resposta.

## 6. Guardrails

- Não alterar `tasks`, `tags`, `task_tags` ou `grupos`.
- Não adicionar autenticação, API JSON, scraping ou framework JavaScript.
- Não adicionar dependências além de Flask e python-dotenv.
- Não commitar `.env` nem credenciais.
- Não publicar no servidor antes da suíte local passar.
- Não avançar de fase sem aceite.
- Toda data de regra de negócio usa `APP_TIMEZONE`.
- Toda ação de escrita usa Post/Redirect/Get e flash message.
- Toda regra nova entra com teste.

## 7. Comandos úteis

```bash
cd "/home/limaydr/Ciclo de Estudos"

# suíte
python3 -m unittest discover -s tests -v

# app local
python3 -m flask --app wsgi run

# saúde
curl -s http://127.0.0.1:5000/health

# emails
python3 -m flask --app wsgi send-peixe-daily
python3 -m flask --app wsgi send-peixe-weekly

# publicar banco no Termux
python3 -m flask --app wsgi publish
```

## 8. Fora do escopo da v1

Drag-and-drop, IA gerando mensagem, Google Calendar, app mobile, scraping, push notification, leaderboard, avatar, loot.

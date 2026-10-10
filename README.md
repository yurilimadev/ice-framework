# ICE Framework

Aplicação web para organizar prioridades pelo framework **ICE** — **I**mpacto, **C**onfiança e **F**acilidade. Feita para responder, todos os dias, uma pergunta simples: *o que merece seu foco hoje?*

## Propósito

Listas de tarefas tradicionais ordenam por data de criação ou urgência, e isso não diz nada sobre o valor real de cada ação. O ICE Framework avalia cada tarefa em três dimensões, de 1 a 10:

- **Impacto** — quanto essa tarefa move algo importante quando concluída?
- **Confiança** — quão certo estou de que vai funcionar como esperado?
- **Facilidade** — quão simples é executar? (quanto menor o esforço, maior a nota)

O **score** é o produto das três dimensões — `I × C × F`, de 1 a 1000 — e a lista fica sempre ordenada pelas tarefas de maior score. Assim, o topo da lista é sempre a ação com melhor relação custo-benefício no momento, e não a mais recente.

## Como o app funciona

- **Painel de foco** — a tela principal lista as tarefas abertas com score, breakdown I·C·F, prazo, tags e status (aberta, concluída, atrasada).
- **Filtro dinâmico** — clicar em qualquer filtro (status, atrasadas, tags, ordenação) atualiza a lista na hora, sem recarregar a página; a URL acompanha o filtro, então dá para salvar/compartilhar uma vista já filtrada. O botão "Aplicar filtros" existe apenas como fallback para navegadores sem JavaScript.
- **Modo painel (desktop)** — cabeçalho e filtros ficam fixos e a lista rola dentro do próprio painel; em telas pequenas a página rola normalmente.
- **Tags** — cada tarefa pode ter várias tags; a tela "Gerenciar Tags" permite renomear, excluir (desvinculando das tarefas, com confirmação) e mesclar tags.
- **Ciclo de vida** — criar, editar, concluir, reabrir e excluir tarefas, com avisos efêmeros (4 segundos) de sucesso/erro e confirmação antes de exclusões.
- **Resumo por email** — envia um email com as tarefas abertas (por score), contagem de atrasadas e prazos, com destaque para as atrasadas. Disparável por botão na barra superior ou por comando no terminal (ver abaixo).
- **Saúde** — `GET /health` responde `status`, `database` e `schema_version` em JSON.

O backend é **Flask** com **SQLite** (migrações versionadas por `PRAGMA user_version`, schema atual `2`), renderização server-side e um pouco de JavaScript vanilla — sem frameworks no front, sem dependências além do Flask e do `python-dotenv`.

## Como executar

### Local

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app wsgi run
```

O app sobe em `http://127.0.0.1:5000`. Verificação:

```bash
curl http://127.0.0.1:5000/health
# {"status":"ok","database":"ok","schema_version":2}
```

### Docker Compose

```bash
docker compose up --build
curl http://127.0.0.1:8000/health
```

O banco (`./data`) fica montado em `/app/data` fora do filesystem efêmero do container; o sufixo `:Z` permite montagem em hosts com SELinux.

Variáveis suportadas: `APP_DATABASE_PATH`, `APP_TIMEZONE` (padrão `America/Sao_Paulo`), `TZ` e as de email (abaixo).

### Resumo por email

O envio exige credenciais SMTP em um arquivo **`.env`** na raiz (fora do git; copie `.env.example`):

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seuemail@gmail.com
SMTP_PASSWORD=senha_de_app_gerada_no_provedor
SMTP_FROM=seuemail@gmail.com
DIGEST_TO=destino@email.com
```

Com o `.env` preenchido, duas formas de enviar:

```bash
# Comando no terminal
python3 -m flask --app wsgi send-digest          # usa DIGEST_TO
python3 -m flask --app wsgi send-digest --to outro@email.com

# Ou botão "Enviar resumo" na barra superior do app
```

O botão só aparece quando o SMTP está configurado. Sem credenciais, o app funciona normalmente — só o envio de email fica indisponível.

### Lançador local (opcional, fora do repositório)

Em máquinas com GNOME, o app pode ser aberto como um aplicativo: script `~/.local/bin/ice` sobe o servidor se necessário e abre o navegador; o ícone "ICE Framework" aparece na grade de aplicativos. Instalação manual, específica de cada máquina — não faz parte do repositório.

### Publicação do banco no servidor

O PC local é a fonte de verdade; o servidor online (abaixo) é um espelho:

```bash
python3 -m flask --app wsgi publish
```

Gera um snapshot consistente do SQLite (backup API), envia por `scp` e reinicia o serviço remoto. Também dispara pelo botão **Publicar** da barra superior do app local (visível apenas com as variáveis `DEPLOY_*` no `.env`). Tarefas criadas diretamente no servidor são sobrescritas na próxima publicação.

### Execução no servidor (Termux/Android com Cloudflare Tunnel)

A instância online roda num Android com Termux, acessível pelo subdomínio protegido por Cloudflare Access:

- **Domínio**: `https://ice.yurilimadev.com` (protegido por email-OTP no Zero Trust).
- **Código**: `git clone https://github.com/yurilimadev/ice-framework.git ~/ice-framework` + venv com `requirements.txt` (inclui `gunicorn` e `tzdata` — o Termux não tem dados de fuso do sistema).
- **Serviços** (`termux-services`): `ice-framework` (gunicorn em `127.0.0.1:8000`) e `ice-tunnel` (`cloudflared tunnel run --url http://127.0.0.1:8000 ice`). Ambos em `$PREFIX/var/service/`.
- **Banco**: `~/ice-framework/data/app.sqlite3` — cópia do banco local, enviada via `scp` com o app parado; re-publicar = re-copiar o arquivo.
- **Secrets**: `.env` criado no servidor (nunca via git/chat), com `SMTP_*` (necessário para o botão "Enviar resumo") e `SECRET_KEY` fixo gerado no próprio servidor.
- **Depois de reiniciar o celular**: abrir o Termux (os serviços voltam automaticamente) e rodar `termux-wake-lock` para o Android não matar os processos com a tela apagada.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

A suíte cobre domínio (score, validações, tags), rotas HTTP (contrato, filtros, 404, 400, 303), interface (seletores, acessibilidade, contraste WCAG AA) e o resumo por email (HTML, texto puro, erros de SMTP).

## Estrutura

```
app/            # aplicação Flask: rotas, domínio, templates, estáticos
migrations/     # SQL versionado por PRAGMA user_version
tests/          # suíte unittest
data/           # app.sqlite3 (criado na primeira execução)
docs/           # governança do projeto: fases, contratos, sessões
```

A pasta `docs/` documenta como o projeto é desenvolvido (fases, sessões por papel e contratos vigentes) — comece por `docs/README.md`.

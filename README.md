# ICE Framework

Aplicacao Flask para organizar prioridades usando o framework ICE.

## Fase 1: fundacao

A aplicacao usa Python com `pip` e `requirements.txt`. O SQLite fica em
`data/app.sqlite3` por padrao. No Compose, `./data` e montada em `/app/data`,
fora do filesystem efemero do container. O sufixo `:Z` permite a montagem em
hosts com SELinux habilitado.

### Execucao local

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m flask --app wsgi run
```

Verificacao da aplicacao e do banco:

```bash
curl http://127.0.0.1:5000/health
```

A resposta esperada contem `"status":"ok"`, `"database":"ok"` e
`"schema_version":1`.

### Execucao com Docker Compose

```bash
docker compose up --build
curl http://127.0.0.1:8000/health
```

Variaveis suportadas:

- `APP_DATABASE_PATH`: caminho do arquivo SQLite.
- `APP_TIMEZONE`: fuso usado pela aplicacao; padrao `America/Sao_Paulo`.
- `TZ`: fuso do container; padrao `America/Sao_Paulo`.

### Schema SQLite

As mudancas estruturais serao aplicadas por arquivos SQL numerados em
`migrations/`. O numero aplicado e registrado em `PRAGMA user_version`.
Migracoes devem ser sequenciais, sem reutilizar ou pular versoes.

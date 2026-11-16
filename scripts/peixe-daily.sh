#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/ice-framework" || exit 1
set -a
. ./.env
set +a
./.venv/bin/python -m flask --app wsgi send-peixe-daily >> "$HOME/.local/state/ice-framework/peixe.log" 2>&1

#!/data/data/com.termux/files/usr/bin/bash
# Backup diario do banco do Peixe/ICE no Termux (mantem os ultimos 7 arquivos).
cd "$HOME/ice-framework" || exit 1
set -eu

mkdir -p backups
stamp="$(date +%Y%m%d-%H%M%S)"
python3 - data/app.sqlite3 "backups/backup-$stamp.sqlite3" <<'PY'
import sqlite3
import sys

source = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
target = sqlite3.connect(sys.argv[2])
source.backup(target)
target.close()
source.close()
PY

count=0
for file in $(ls -1t backups/backup-*.sqlite3 2>/dev/null); do
  count=$((count + 1))
  if [ "$count" -gt 7 ]; then
    rm -f "$file"
  fi
done

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  ./install.sh
fi
. .venv/bin/activate
[ -f .env ] || cp .env.example .env
python -m app.cli setup >/dev/null
( sleep 2; python -m webbrowser -t http://127.0.0.1:8000 >/dev/null 2>&1 || true ) &
echo "AltAlpha is starting at http://127.0.0.1:8000"
echo "On the first run, data synchronization starts automatically in the background."
exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

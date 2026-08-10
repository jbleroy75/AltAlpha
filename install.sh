#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=${PYTHON:-python3}
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3.11+ is required. Install Python, then rerun ./install.sh"
  exit 1
fi
"$PYTHON" - <<'PY'
import sys
if sys.version_info < (3,11):
    raise SystemExit("AltAlpha requires Python 3.11+")
PY
[ -d .venv ] || "$PYTHON" -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
[ -f .env ] || cp .env.example .env
python -m app.cli setup
printf '\nAltAlpha installed successfully. Run ./start.sh\n'

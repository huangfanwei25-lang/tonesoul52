#!/usr/bin/env bash
set -euo pipefail

# Antigravity VM smoke runner.
# Runs minimal gating checks by default, full test suite when --full is set.

FULL_MODE=0

for arg in "$@"; do
  case "$arg" in
    --full)
      FULL_MODE=1
      ;;
    *)
      echo "unknown argument: $arg"
      echo "usage: bash scripts/vm/run_antigravity_smoke.sh [--full]"
      exit 1
      ;;
  esac
done

if [ ! -f ".venv/bin/activate" ]; then
  echo "missing .venv. run: bash scripts/vm/bootstrap_antigravity_vm.sh"
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[1/3] Docs consistency gate..."
python -m pytest tests/test_verify_docs_consistency.py -q

echo "[2/3] Repo healthcheck gate..."
python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion

if [ "$FULL_MODE" = "1" ]; then
  echo "[3/3] Full test suite..."
  python -m pytest tests/ -q
else
  echo "[3/3] Skipped full suite (use --full to enable)."
fi

echo "smoke checks completed."

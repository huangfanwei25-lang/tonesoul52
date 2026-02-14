#!/usr/bin/env bash
set -euo pipefail

# Antigravity VM bootstrap (Ubuntu/Debian-oriented)
# Idempotent setup for ToneSoul development inside an isolated VM.

REPO_URL="${REPO_URL:-https://github.com/Fan1234-1/tonesoul52.git}"
REPO_DIR="${REPO_DIR:-tonesoul52}"
BRANCH="${BRANCH:-master}"
SKIP_WEB_INSTALL="${SKIP_WEB_INSTALL:-0}"

echo "[1/6] Checking base tools..."
for cmd in git python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "missing required command: $cmd"
    echo "install base deps first, e.g.: sudo apt update && sudo apt install -y git python3 python3-venv python3-pip"
    exit 1
  fi
done

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "[2/6] Cloning repository..."
  git clone "$REPO_URL" "$REPO_DIR"
else
  echo "[2/6] Repository already exists: $REPO_DIR"
fi

cd "$REPO_DIR"
echo "[3/6] Syncing branch: $BRANCH"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

echo "[4/6] Preparing Python virtual environment..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

if [ "$SKIP_WEB_INSTALL" = "1" ]; then
  echo "[5/6] Skipping web dependencies (SKIP_WEB_INSTALL=1)"
else
  if command -v npm >/dev/null 2>&1; then
    echo "[5/6] Installing web dependencies..."
    npm --prefix apps/web ci
  else
    echo "[5/6] npm not found; skipping web dependency install."
  fi
fi

echo "[6/6] Bootstrap complete."
echo "next: bash scripts/vm/run_antigravity_smoke.sh"

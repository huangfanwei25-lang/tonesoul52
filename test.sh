#!/usr/bin/env bash
# test.sh — canonical local-dev test entry for ToneSoul
#
# Purpose: a single command that mirrors what CI enforces, so a developer
# can run it before commit and trust that "if test.sh passes, CI will pass
# the same gates."
#
# Usage:
#   ./test.sh           full check (lint + format + tests; default)
#   ./test.sh lint      only lint + format
#   ./test.sh test      only tests
#   ./test.sh fast      lint + tests excluding @slow, parallelized with xdist
#
# Why this exists (per docs/status/calibration_sprint_2026-05-04_synthesis.md +
# reference_navigation_grammar_pattern memory): the "test entry" slot of
# ToneSoul's navigation grammar was previously empty. Developers had to
# remember to invoke ruff + black + pytest separately, in the right order,
# with the right flags. Easy to miss one. test.sh is the single answer to
# "how do I know I haven't broken anything".
#
# What this does NOT do:
#   - apps/web Next.js type check (handled by Web Quality Gate in CI)
#   - Repository Healthcheck (slow CI-only gate)
#   - Vercel deploy preview (CI/PaaS layer)
#   - The 14-day wave / calibration sprint runners (those are operator scripts)
#
# Mirrors CI gates: Lint and Format Check + Test Python 3.12.

set -e
set -o pipefail

MODE="${1:-full}"

# Color for terminal output (no color if not a tty)
if [ -t 1 ]; then
    YELLOW=$'\033[33m'
    GREEN=$'\033[32m'
    RED=$'\033[31m'
    RESET=$'\033[0m'
else
    YELLOW=''
    GREEN=''
    RED=''
    RESET=''
fi

step() {
    echo
    echo "${YELLOW}=== $1 ===${RESET}"
}

ok() {
    echo "${GREEN}✓ $1${RESET}"
}

fail() {
    echo "${RED}✗ $1${RESET}" >&2
    exit 1
}

# Ignored test files (slow, environment-specific, or known to need
# extra setup that CI provides but local dev typically doesn't).
PYTEST_IGNORES=(
    "--ignore=tests/test_demo_ui_modea_e2e.py"
)

run_lint() {
    # Mirrors CI workflow .github/workflows/ci.yml + pytest-ci.yml:
    #   - ruff check tonesoul tests (blocking, full scope)
    #   - python scripts/run_black_gate.py --strict (blocking, but bounded
    #     to changed Python files vs origin/master so pre-existing format
    #     debt in unrelated files does not gate unrelated work)
    #
    # The black gate is custom — raw "black --check tonesoul tests" would
    # fail on ~200 pre-existing format-debt files. The gate scopes to
    # what THIS branch / PR changed, exactly like CI.
    step "ruff check (tonesoul + tests)"
    python -m ruff check tonesoul tests || fail "ruff check failed"
    ok "ruff clean"

    step "black gate (changed-files-only, --strict)"
    python scripts/run_black_gate.py --strict || fail "black gate failed"
    ok "black gate clean"
}

run_tests() {
    step "pytest"
    python -m pytest tests/ -q "${PYTEST_IGNORES[@]}" || fail "pytest failed"
    ok "pytest passed"
}

run_tests_fast() {
    step "pytest fast (-m not slow, xdist auto)"
    python -m pytest tests/ -q "${PYTEST_IGNORES[@]}" -m "not slow" -n auto || fail "pytest failed"
    ok "pytest passed (fast mode)"
}

case "$MODE" in
    lint)
        run_lint
        ;;
    test)
        run_tests
        ;;
    fast)
        run_lint
        run_tests_fast
        ;;
    full)
        run_lint
        run_tests
        ;;
    *)
        echo "Usage: $0 [full|lint|test|fast]"
        echo ""
        echo "  full   lint + format + all tests (default)"
        echo "  lint   only lint + format"
        echo "  test   only tests"
        echo "  fast   lint + tests excluding @slow, parallelized with xdist"
        exit 2
        ;;
esac

echo
echo "${GREEN}✓ test.sh ${MODE} passed${RESET}"

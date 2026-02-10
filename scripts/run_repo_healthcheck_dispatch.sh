#!/usr/bin/env bash
set -euo pipefail

INCLUDE_SDH="${TS_INCLUDE_SDH:-false}"
WEB_BASE="${TS_WEB_BASE:-}"
API_BASE="${TS_API_BASE:-}"
SDH_TIMEOUT="${TS_SDH_TIMEOUT:-}"
CHECK_COUNCIL_MODES="${TS_CHECK_COUNCIL_MODES:-true}"

CMD=(python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion)

if [[ -n "${SDH_TIMEOUT}" ]]; then
  if ! [[ "${SDH_TIMEOUT}" =~ ^[0-9]+$ ]] || [[ "${SDH_TIMEOUT}" -lt 1 ]]; then
    echo "::error::sdh_timeout must be a positive integer. got='${SDH_TIMEOUT}'"
    exit 1
  fi
fi

if [[ "${INCLUDE_SDH}" == "true" ]]; then
  if [[ -n "${WEB_BASE}" && -z "${API_BASE}" ]]; then
    echo "::warning::include_sdh=true and web_base is set but api_base is empty; api_base will fallback to verify_7d default."
  fi
  if [[ -z "${WEB_BASE}" && -n "${API_BASE}" ]]; then
    echo "::warning::include_sdh=true and api_base is set but web_base is empty; web_base will fallback to verify_7d default."
  fi
  CMD+=(--include-sdh)

  if [[ "${CHECK_COUNCIL_MODES}" == "false" ]]; then
    CMD+=(--no-check-council-modes)
  else
    CMD+=(--check-council-modes)
  fi

  if [[ -n "${WEB_BASE}" ]]; then
    CMD+=(--web-base "${WEB_BASE}")
  fi
  if [[ -n "${API_BASE}" ]]; then
    CMD+=(--api-base "${API_BASE}")
  fi
  if [[ -n "${SDH_TIMEOUT}" ]]; then
    CMD+=(--sdh-timeout "${SDH_TIMEOUT}")
  fi
else
  if [[ -n "${WEB_BASE}" || -n "${API_BASE}" || -n "${SDH_TIMEOUT}" ]]; then
    echo "::warning::SDH inputs were provided but include_sdh=false; web/api/timeout inputs will be ignored."
  fi
fi

"${CMD[@]}"

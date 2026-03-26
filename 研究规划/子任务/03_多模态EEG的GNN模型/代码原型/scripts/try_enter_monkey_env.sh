#!/usr/bin/env bash
set -euo pipefail

echo "[check] HOME=$HOME"

if command -v senv >/dev/null 2>&1; then
  echo "[ok] found command: senv"
else
  echo "[miss] senv not found"
fi

if [[ -f "$HOME/senv_auto.sh" ]]; then
  echo "[ok] found file: $HOME/senv_auto.sh"
else
  echo "[miss] file not found: $HOME/senv_auto.sh"
fi

if [[ -n "${MONKEY_REPO:-}" ]]; then
  echo "[info] MONKEY_REPO=$MONKEY_REPO"
fi

if [[ -f "$HOME/senv_auto.sh" ]]; then
  echo "[try] source $HOME/senv_auto.sh"
  # shellcheck disable=SC1090
  source "$HOME/senv_auto.sh"
  echo "[ok] sourced senv_auto.sh"
elif command -v senv >/dev/null 2>&1; then
  echo "[try] run senv"
  senv
  echo "[ok] senv finished"
else
  echo "[fail] no container entrypoint found on this machine"
  exit 1
fi

#!/usr/bin/env bash
# Serve the example site with live reload: scripts/serve.sh [extra hugo flags]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec hugo server --source "$ROOT/exampleSite" \
  --themesDir "$(dirname "$ROOT")" --theme "$(basename "$ROOT")" "$@"

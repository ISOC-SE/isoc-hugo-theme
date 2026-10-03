#!/usr/bin/env bash
# Build exampleSite (strict: any warning fails), the same site again under a
# sub-path (as GitHub Pages serves it), and the edge-case fixture, then run the
# output assertions in scripts/checks/.
# Usage: scripts/check.sh [check-name-filter]
# Set CHECK_CLOCK=2030-01-01T12:00:00Z to build and check as if it were that time.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/.check"
THEMES_DIR="$(dirname "$ROOT")"
THEME="$(basename "$ROOT")"
MAIN_BASE="https://example.org/"
SUB_BASE="https://example.org/isoc-hugo-theme/"
EDGE_BASE="https://edge.example.org/sub/"
CLOCK_ARGS=()
NOW_ARGS=()
if [[ -n "${CHECK_CLOCK:-}" ]]; then
  CLOCK_ARGS=(--clock "$CHECK_CLOCK")
  NOW_ARGS=(--now "$CHECK_CLOCK")
fi

rm -rf "$OUT"
mkdir -p "$OUT"

echo "==> exampleSite (strict)"
hugo --source "$ROOT/exampleSite" --themesDir "$THEMES_DIR" --theme "$THEME" \
  --destination "$OUT/main" --baseURL "$MAIN_BASE" ${CLOCK_ARGS[@]+"${CLOCK_ARGS[@]}"} \
  --panicOnWarning --printI18nWarnings --printPathWarnings --logLevel warn

echo "==> exampleSite under a sub-path (strict)"
hugo --source "$ROOT/exampleSite" --themesDir "$THEMES_DIR" --theme "$THEME" \
  --destination "$OUT/main-sub" --baseURL "$SUB_BASE" ${CLOCK_ARGS[@]+"${CLOCK_ARGS[@]}"} \
  --panicOnWarning --printI18nWarnings --printPathWarnings --logLevel warn

echo "==> tests/edge (warnings expected, captured in .check/edge.log)"
if ! hugo --source "$ROOT/tests/edge" --themesDir "$THEMES_DIR" --theme "$THEME" \
  --destination "$OUT/edge" --baseURL "$EDGE_BASE" ${CLOCK_ARGS[@]+"${CLOCK_ARGS[@]}"} \
  --printI18nWarnings --logLevel warn >"$OUT/edge.log" 2>&1; then
  cat "$OUT/edge.log"
  echo "edge build failed" >&2
  exit 1
fi

echo "==> tests/crowded (header-fit fixture)"
hugo --source "$ROOT/tests/crowded" --themesDir "$THEMES_DIR" --theme "$THEME" \
  --destination "$OUT/crowded" --baseURL "https://crowded.example.org/" \
  --printI18nWarnings --logLevel error >/dev/null

echo "==> assertions"
status=0
if [[ $# -eq 0 || "$1" != "browser" ]]; then
python3 "$ROOT/scripts/check_site.py" \
  --main "$OUT/main" --main-base "$MAIN_BASE" \
  --main-sub "$OUT/main-sub" --main-sub-base "$SUB_BASE" \
  --edge "$OUT/edge" --edge-base "$EDGE_BASE" --edge-log "$OUT/edge.log" \
  ${NOW_ARGS[@]+"${NOW_ARGS[@]}"} "$@" || status=1
fi

# Browser checks (headless Chrome) run on full runs and with a "browser" filter.
if [[ $# -eq 0 || "$1" == *browser* ]]; then
  echo "==> browser checks"
  python3 "$ROOT/scripts/check_browser.py" --site "$OUT/main" --crowded "$OUT/crowded" || status=1
fi
exit $status

#!/usr/bin/env bash
# Visual review helper (needs Google Chrome; override with CHROME=/path/to/chrome).
#   scripts/screenshots.sh              exampleSite pages -> .check/screenshots/
#   scripts/screenshots.sh --reference  chapter-template.isoc.org -> .check/reference/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PORT="${PORT:-1414}"

shoot() { # out width url [extra chrome flags...]
  local out=$1 width=$2 url=$3
  shift 3
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 \
    --window-size="$width,2400" --screenshot="$out" "$@" "$url" >/dev/null 2>&1
}

# Headless Chrome never makes the viewport narrower than 500px, so phone-width
# shots load the page in a 390px iframe on a small wrapper page instead.
shoot_mobile() { # out path [extra chrome flags...]
  local out=$1 path=$2 wrapper
  shift 2
  wrapper="_m-$(basename "$out" .png).html"
  printf '<!doctype html><body style="margin:0"><iframe src="%s" style="border:0;width:390px;height:2400px"></iframe></body>\n' \
    "$path" > "$SITE/$wrapper"
  shoot "$out" 500 "http://localhost:$PORT/$wrapper" "$@"
}

if [[ "${1:-}" == "--reference" ]]; then
  OUT="$ROOT/.check/reference"
  mkdir -p "$OUT"
  for entry in "home:https://chapter-template.isoc.org/" \
               "post:https://chapter-template.isoc.org/2023/06/test-post/" \
               "category:https://chapter-template.isoc.org/category/news/"; do
    name=${entry%%:*}
    url=${entry#*:}
    shoot "$OUT/$name.png" 1440 "$url" --virtual-time-budget=15000
  done
  cp "$ROOT/genesis-child-chapters-main/screenshot.png" "$OUT/theme-screenshot.png"
  cp "$ROOT/genesis-child-chapters-main/config/import/images/thumbnails/home-color.jpg" "$OUT/theme-home.jpg"
  ls "$OUT"
  exit 0
fi

SITE="$ROOT/.check/shots-site"
OUT="$ROOT/.check/screenshots"
rm -rf "$SITE" "$OUT"
mkdir -p "$OUT"
hugo --quiet --source "$ROOT/exampleSite" --themesDir "$(dirname "$ROOT")" --theme "$(basename "$ROOT")" \
  --destination "$SITE" --baseURL "http://localhost:$PORT/"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$SITE" >/dev/null 2>&1 &
SERVER=$!
trap 'kill "$SERVER"' EXIT
sleep 1

pages=(
  "home:/" "home-sv:/sv/" "about:/about/" "board:/about/board/" "membership:/membership/"
  "news:/posts/" "post:/posts/annual-general-meeting-2026/" "archive:/archive/"
  "events:/events/" "event:/events/samnet-5/" "search:/search/?q=encryption"
  "shortcodes:/shortcodes/" "404:/404.html"
)
for entry in "${pages[@]}"; do
  name=${entry%%:*}
  path=${entry#*:}
  shoot "$OUT/$name-desktop.png" 1440 "http://localhost:$PORT$path"
  shoot_mobile "$OUT/$name-mobile.png" "$path"
done
# Headless Chrome cannot screenshot with scripting disabled, so shoot a copy of
# the homepage with every <script> removed (html keeps its "no-js" class).
python3 - "$SITE/index.html" "$SITE/_nojs-home.html" <<'PY'
import re, sys
html = open(sys.argv[1], encoding="utf-8").read()
open(sys.argv[2], "w", encoding="utf-8").write(re.sub(r"<script\b.*?</script>", "", html, flags=re.S))
PY
shoot "$OUT/home-nojs-desktop.png" 1440 "http://localhost:$PORT/_nojs-home.html"
shoot_mobile "$OUT/home-nojs-mobile.png" "/_nojs-home.html"
ls "$OUT"

# ISOC Chapters Hugo Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable Hugo theme that recreates the Internet Society chapter WordPress theme ("Internet Chapters", Genesis child theme) plus a bilingual exampleSite, buildable with only the `hugo` binary.

**Architecture:** The repo root is the theme. Layouts use Hugo's ≥0.146 template system (`layouts/_partials`, `layouts/_shortcodes`, `layouts/_markup`). Styling is plain CSS split per component and bundled by Hugo Pipes. Behaviour is two small vanilla JS files (menu, search) plus vendored Fuse.js. Templates key on content **type** (`posts`, `events`), never directory names. Generated artefacts (search index, `.ics` files) are published with `resources.FromString`, so sites need no output-format config. Verification is a strict Hugo build of `exampleSite/` and an edge-case fixture `tests/edge/`, followed by Python (stdlib only) assertions over the generated HTML.

**Tech Stack:** Hugo 0.167 (≥0.158 required, standard edition), HTML templates, CSS custom properties, vanilla ES2017 JS, Fuse.js 7.1.0 (UMD basic build), Hind font (self-hosted woff2), Python 3 stdlib for checks, headless Chrome for screenshots.

**Spec:** `docs/superpowers/specs/2026-10-02-isoc-hugo-theme-design.md`

## Global Constraints

- Hugo **≥ 0.158.0**; develop and verify on 0.167.0; standard (non-extended) edition must suffice. Theme `hugo.toml` declares `[module.hugoVersion] min = "0.158.0"`.
- **Never use deprecated APIs** (deprecation warnings fail the strict build): not `site.Languages`, `.Sites`, `site.Sites`, `.Language.LanguageName`, `.Language.LanguageCode`, `.Language.LanguageDirection`, `.Site.LanguageCode`, nor the `languageCode`/`languageName` config keys. Use `hugo.Sites`, `.Language.Label`, `.Language.Locale`, `.Language.Direction`, `locale`, `label`.
- No build dependencies beyond `hugo`. No runtime CDN requests: Fuse.js and fonts are vendored. Python 3 (stdlib only) is used **only** by dev/test scripts.
- Theme config supplies only `[params]` and `[module]`; Hugo does not merge `outputs`, `pagination` or `markup` from a theme (verified). Do not rely on them.
- Templates select content by `.Type` (`"posts"`, `"events"`), never by section directory name.
- Every user-facing string in templates goes through `T` with the key present in **both** `i18n/en.toml` and `i18n/sv.toml` (missing keys fail the build via `--printI18nWarnings --panicOnWarning`).
- Brand colours (exact): navy `#0c1c2c`, blue `#2b72d6`, bright blue `#1d69d3`, light blue `#3a82e4`, depth blue `#24366e`, blue bg `#27376a`, teal `#40b2a4`, depth green `#085856`, depth teal `#143e50`, purple `#7e245c`, orange `#d25238`, yellow `#eeca4a`, neutral white `#eff2ec`, neutral green `#d0e6da`, putty `#dedad0`. Body text `#0c1c2c`. Font Hind 18px/28px.
- Content must be visible and the menu reachable with JavaScript disabled; only search needs JS. WCAG 2.1 AA target.
- License GPL-2.0-or-later (theme), SIL OFL 1.1 (Hind), Apache-2.0 (Fuse.js); license files shipped.
- `genesis/` and `genesis-child-chapters-main/` are read-only reference material: never modify them.
- **Never run `git commit`** (user instruction: "Do not commit anything at any stage"). There are no commit steps; leave all changes in the working tree.

## Review Focus

1. **Site served from a sub-path** (GitHub Pages project URL such as `/isoc-hugo-theme/`): every stylesheet, script, image, link, `.ics` and search-index URL must include the base path. → `tests/edge` is built with `--baseURL https://edge.example.org/sub/` and the link checker (Task 1) plus the `.ics`/index URL checks (Tasks 7, 9) run against it.
2. **Event `start` written without a UTC offset**: must be read in the site's `timeZone`, and the `.ics` must carry the correct UTC instant. → edge event `2099-05-01T18:00:00` with `timeZone = "Europe/Stockholm"` must give `DTSTART:20990501T160000Z` (Task 7).
3. **A page that exists in only one language**: the language switcher must link to the other language's homepage, not a 404. → exampleSite `/shortcodes/` exists only in English; its Swedish switcher link must be `/sv/` (Task 3 creates the page and the check).
4. **Invalid front-matter values** (unknown homepage block `type`, unknown `banner`): the build continues, logs a warning naming the page, and renders a fallback. → edge site uses `type: nonsense` and `banner: purple`; checks assert the warnings in the edge log and the fallback markup (Tasks 5, 8).
5. **Single-language site with search disabled and no menus**: header and footer render without empty containers or dead controls (no language switcher, no search button, no empty `<nav>`). → edge site checks (Tasks 3, 4, 9).

---

## File Map

| Path | Responsibility | Task |
|---|---|---|
| `.gitignore`, `hugo.toml`, `theme.toml`, `go.mod`, `LICENSE` | Theme metadata & defaults | 1 |
| `scripts/check.sh` | Build exampleSite (strict) + edge fixture, run assertions | 1 |
| `scripts/check_site.py`, `scripts/checklib.py` | Assertion runner + HTML tree/link helpers | 1 |
| `scripts/checks/*.py` | One assertion module per feature area | 1–10 |
| `scripts/serve.sh` | Local dev server for exampleSite | 1 |
| `exampleSite/hugo.toml`, `exampleSite/content/{en,sv}/…`, `exampleSite/assets/images/…` | Demo site | 1–9 |
| `tests/edge/…` | Edge-case fixture site (single language, sub-path, invalid values) | 1–9 |
| `scripts/fetch-fonts.py`, `static/fonts/hind/*`, `assets/css/fonts.css` | Self-hosted Hind | 2 |
| `assets/css/tokens.css`, `base.css`, `layout.css` | Tokens, base typography, containers, buttons | 2 |
| `i18n/en.toml`, `i18n/sv.toml` | All theme strings | 2 |
| `layouts/baseof.html`, `_partials/head.html`, `_partials/head/css.html`, `_partials/head/meta.html`, `_partials/func/description.html`, `_partials/func/body-class.html`, `_partials/func/resource.html` | Document shell & head; resource resolver | 2 |
| `static/favicon.ico` | Default favicon | 2 |
| `assets/images/logo-isoc-chapters.svg`, `assets/images/icons/*.svg` | Logo, UI icons | 3 |
| `_partials/header.html`, `nav-menu.html`, `lang-switch.html`, `icon.html`, `func/logo.html`, `scripts.html` | Header & navigation | 3 |
| `assets/css/header.css`, `nav.css`, `assets/js/menu.js` | Header styles + behaviour | 3 |
| `_partials/footer.html`, `social-links.html`, `func/copyright.html`, `assets/images/social/*.svg`, `assets/css/footer.css` | Footer | 4 |
| `_partials/banner.html`, `func/banner-image.html`, `img.html`, `func/url.html`, `button.html`, `card.html`, `page-content.html` | Shared building blocks | 5 |
| `layouts/single.html`, `list.html`, `404.html`, `_markup/render-image.html`, `_markup/render-link.html` | Pages | 5 |
| `assets/images/patterns/*.jpg`, `assets/css/hero.css`, `content.css`, `cards.css` | Banners, prose, cards | 5 |
| `layouts/posts/single.html`, `posts/list.html`, `taxonomy.html`, `term.html`, `archive.html` | News | 6 |
| `_partials/post-meta.html`, `post-categories.html`, `featured-image.html`, `related-posts.html`, `category-nav.html`, `pagination.html`, `latest-posts-grid.html` | News partials | 6 |
| `layouts/events/single.html`, `events/list.html`, `_partials/card-event.html`, `event-details.html`, `upcoming-events-grid.html`, `func/event-dates.html`, `func/event-when.html`, `func/events.html`, `func/event-ics.html`, `func/ics-escape.html`, `assets/css/events.css` | Events | 7 |
| `layouts/home.html`, `_partials/blocks/*.html`, `image-text.html`, `quote.html`, `stats.html`, `cta.html`, `gallery.html`, `_shortcodes/*.html`, `assets/css/blocks.css` | Homepage blocks & shortcodes | 8 |
| `layouts/search.html`, `_partials/search-toggle.html`, `search-panel.html`, `search-config.html`, `func/search-index.html`, `assets/js/search.js`, `assets/js/vendor/fuse.basic.min.js`, `assets/css/search.css` | Search | 9 |
| `assets/css/motion.css`, `scripts/screenshots.sh` | Motion, visual verification | 10 |
| `archetypes/*.md`, `README.md`, `.github/workflows/demo.yml` | Docs & CI | 11 |

**How to run checks (every task):** `scripts/check.sh` builds both sites and runs all assertions; `scripts/check.sh <filter>` runs only checks whose name contains `<filter>` (both sites are still rebuilt). A check "fails" when the script prints `FAIL <name>` and exits non-zero. A Hugo build error also counts as a failure.

---

### Task 1: Theme skeleton and test harness

**Files:**
- Create: `.gitignore`, `hugo.toml`, `theme.toml`, `go.mod`, `LICENSE`
- Create: `layouts/baseof.html`, `layouts/home.html`, `layouts/single.html`, `layouts/list.html` (minimal; replaced in Tasks 2, 5, 8)
- Create: `exampleSite/hugo.toml`, `exampleSite/content/en/_index.md`, `exampleSite/content/sv/_index.md`
- Create: `tests/edge/hugo.toml`, `tests/edge/content/_index.md`
- Create: `scripts/check.sh`, `scripts/serve.sh`, `scripts/check_site.py`, `scripts/checklib.py`, `scripts/checks/core.py`

**Interfaces:**
- Produces (used by every later task):
  - `scripts/checklib.py`: `check` (decorator registering a check function `fn(ctx)`), `expect(cond: bool, msg: str)`, `Site` with `.exists(rel) -> bool`, `.read(rel) -> str`, `.html(rel) -> El`, `.json(rel)`, `.html_files() -> list[str]`, `.resolve(url, page_rel) -> str | None` (local file path, or `None` for external), `.broken_links() -> list[str]`, `.log: str`, `.base_path: str`; `El` with `.select(css) -> list[El]`, `.find(css) -> El | None`, `.kids(tag=None) -> list[El]` (direct children), `.text() -> str`, `.attrs: dict`, `.classes: list[str]`, `.parent: El`.
  - Check context `ctx` with `ctx.main` (exampleSite `Site`, base `https://example.org/`) and `ctx.edge` (edge `Site`, base `https://edge.example.org/sub/`, `.log` = edge build output).
  - Selector syntax supported by `El.select`: descendant combinator (space) between compound selectors made of optional tag, `.class`, `#id`, `[attr]`, `[attr=value]`, `[attr="value"]`.

- [ ] **Step 1: Create the theme metadata files**

`.gitignore`:
```gitignore
.DS_Store
.check/
.hugo_build.lock
exampleSite/public/
exampleSite/resources/
tests/edge/public/
tests/edge/resources/
```

`hugo.toml`:
```toml
# Theme defaults. Hugo merges [params] (and menus) from a theme's config,
# but NOT outputs, pagination or markup, so the theme depends on none of them.
[module]
  [module.hugoVersion]
    extended = false
    min = "0.158.0"

[params]
  logoWidth = 233
  joinURL = "https://community.internetsociety.org/s/new-registration"
  showSearch = true
  pagerSize = 9
  dateFormat = ":date_long"
  defaultBanner = "blue"
  copyright = "© {year} {chapterName}"
```

`theme.toml`:
```toml
name = "ISOC Chapters"
license = "GPL-2.0-or-later"
licenselink = "https://github.com/ISOC-SE/isoc-hugo-theme/blob/main/LICENSE"
description = "Hugo port of the Internet Society chapter WordPress theme (Genesis child theme \"Internet Chapters\"), with news, events, search and English/Swedish translations."
homepage = "https://github.com/ISOC-SE/isoc-hugo-theme"
demosite = "https://isoc-se.github.io/isoc-hugo-theme/"
tags = ["multilingual", "blog", "events", "nonprofit", "responsive"]
features = ["multilingual", "search", "events", "responsive", "no-build-tools"]
min_version = "0.158.0"

[author]
  name = "ISOC-SE (Internet Society Swedish Chapter)"
  homepage = "https://isoc.se"

[original]
  name = "Internet Chapters (Genesis child theme)"
  homepage = "https://chapter-template.isoc.org/"
  repo = "https://github.com/InternetSociety/genesis-child-chapters"
```

`go.mod` (lets the theme be imported as a Hugo Module; module path assumes the final GitHub location):
```
module github.com/ISOC-SE/isoc-hugo-theme

go 1.22
```

Download the license:
```bash
curl -fsSL https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt -o LICENSE
head -3 LICENSE
```
Expected: first lines contain `GNU GENERAL PUBLIC LICENSE` and `Version 2, June 1991`.

- [ ] **Step 2: Write the check library**

`scripts/checklib.py`:
```python
"""Small, dependency-free helpers for asserting on Hugo output.

Checks live in scripts/checks/*.py and register themselves with @check.
"""
import json
import os
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

CHECKS = []
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}


def check(fn):
    """Register a check. The function receives the check context."""
    CHECKS.append(fn)
    return fn


class CheckFailed(AssertionError):
    pass


def expect(cond, msg):
    if not cond:
        raise CheckFailed(msg)


class El:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = {k: (v if v is not None else "") for k, v in attrs}
        self.parent = parent
        self.children = []  # El or str, in document order

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    def text(self):
        parts = []
        for child in self.children:
            parts.append(child if isinstance(child, str) else child.text())
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def kids(self, tag=None):
        """Direct child elements, optionally filtered by tag name."""
        return [c for c in self.children if isinstance(c, El) and (tag is None or c.tag == tag)]

    def descendants(self):
        for child in self.children:
            if isinstance(child, El):
                yield child
                yield from child.descendants()

    def select(self, selector):
        current = [self]
        for part in selector.split():
            comp = _parse_compound(part)
            found, seen = [], set()
            for base in current:
                for el in base.descendants():
                    if id(el) not in seen and _matches(el, comp):
                        seen.add(id(el))
                        found.append(el)
            current = found
        return current

    def find(self, selector):
        found = self.select(selector)
        return found[0] if found else None

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"


_ATTR_RE = re.compile(r'\[([\w:-]+)(?:=("?)([^\]"]*)\2)?\]')


def _parse_compound(part):
    tag_match = re.match(r"^[a-zA-Z][\w-]*", part)
    return {
        "tag": tag_match.group(0).lower() if tag_match else None,
        "classes": re.findall(r"\.([\w-]+)", _ATTR_RE.sub("", part)),
        "ids": re.findall(r"#([\w-]+)", _ATTR_RE.sub("", part)),
        "attrs": [(name, value if eq or value else None)
                  for name, eq, value in _ATTR_RE.findall(part)],
    }


def _matches(el, comp):
    if comp["tag"] and el.tag != comp["tag"]:
        return False
    if any(c not in el.classes for c in comp["classes"]):
        return False
    if any(el.attrs.get("id") != i for i in comp["ids"]):
        return False
    for name, value in comp["attrs"]:
        if name not in el.attrs:
            return False
        if value is not None and el.attrs[name] != value:
            return False
    return True


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = El("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        el = El(tag, attrs, self.cur)
        self.cur.children.append(el)
        if tag not in VOID:
            self.cur = el

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(El(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse_html(text):
    builder = _TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


class Site:
    """A built Hugo site: its publish directory and base URL."""

    def __init__(self, public, base_url, log=""):
        self.public = public
        parsed = urlparse(base_url)
        self.host = parsed.netloc
        self.base_path = parsed.path if parsed.path.endswith("/") else parsed.path + "/"
        self.log = log
        self._cache = {}

    def _local(self, rel):
        rel = rel.lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel += "index.html"
        return os.path.join(self.public, rel)

    def exists(self, rel):
        return os.path.isfile(self._local(rel))

    def read(self, rel):
        path = self._local(rel)
        expect(os.path.isfile(path), f"missing output file: {rel}")
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def html(self, rel):
        if rel not in self._cache:
            self._cache[rel] = parse_html(self.read(rel))
        return self._cache[rel]

    def json(self, rel):
        return json.loads(self.read(rel))

    def html_files(self):
        out = []
        for dirpath, _, files in os.walk(self.public):
            for name in files:
                if name.endswith(".html"):
                    out.append(os.path.relpath(os.path.join(dirpath, name), self.public))
        return sorted(out)

    def url_to_rel(self, url):
        """Turn a site URL (absolute or root-relative) into a publish-dir path, or None if external."""
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            return None
        if parsed.netloc and parsed.netloc != self.host:
            return None
        path = unquote(parsed.path)
        if not path.startswith(self.base_path):
            return "!outside-base:" + path
        return path[len(self.base_path):]

    def resolve(self, url, page_rel):
        """Local file for a URL found on page `page_rel`; None if external or same-page anchor."""
        parsed = urlparse(url)
        if parsed.scheme in ("mailto", "tel", "data", "javascript"):
            return None
        if not parsed.scheme and not parsed.netloc and not parsed.path:
            return None  # "#fragment" or "?query" on the same page
        if not parsed.scheme and not parsed.path.startswith("/"):
            page_dir = os.path.dirname(page_rel)
            rel = os.path.normpath(os.path.join(page_dir, unquote(parsed.path)))
            return self._local(rel + ("/" if parsed.path.endswith("/") else ""))
        rel = self.url_to_rel(url)
        if rel is None:
            return None
        if rel.startswith("!outside-base:"):
            return rel
        local = self._local(rel)
        if not os.path.isfile(local) and os.path.isfile(os.path.join(local, "index.html")):
            local = os.path.join(local, "index.html")
        return local

    def broken_links(self):
        broken = []
        for page_rel in self.html_files():
            root = self.html(page_rel)
            for el in root.descendants():
                urls = [el.attrs[a] for a in ("href", "src") if a in el.attrs]
                if "srcset" in el.attrs:
                    urls += [p.strip().split()[0] for p in el.attrs["srcset"].split(",") if p.strip()]
                for url in urls:
                    if el.tag == "link" and el.attrs.get("rel") in ("canonical", "alternate"):
                        continue  # absolute permalinks, checked separately
                    if url in ("", "#"):
                        broken.append(f"{page_rel}: placeholder link {url!r} on <{el.tag}>")
                        continue
                    local = self.resolve(url, page_rel)
                    if local is None:
                        continue
                    if local.startswith("!outside-base:") or not os.path.isfile(local):
                        broken.append(f"{page_rel}: {url}")
        return broken
```

- [ ] **Step 3: Write the runner**

`scripts/check_site.py`:
```python
#!/usr/bin/env python3
"""Run output assertions against the built example and edge sites.

Usage: check_site.py --main DIR --main-base URL --edge DIR --edge-base URL --edge-log FILE [filter]
"""
import argparse
import importlib.util
import pathlib
import sys
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from checklib import CHECKS, CheckFailed, Site  # noqa: E402


class Ctx:
    def __init__(self, main, edge):
        self.main = main
        self.edge = edge


def load_checks():
    for path in sorted((HERE / "checks").glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"checks.{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--main-base", required=True)
    ap.add_argument("--edge", required=True)
    ap.add_argument("--edge-base", required=True)
    ap.add_argument("--edge-log", required=True)
    ap.add_argument("filter", nargs="?", default="")
    args = ap.parse_args()

    with open(args.edge_log, encoding="utf-8") as fh:
        edge_log = fh.read()
    ctx = Ctx(Site(args.main, args.main_base), Site(args.edge, args.edge_base, edge_log))

    load_checks()
    selected = [fn for fn in CHECKS if args.filter in fn.__name__]
    failures = 0
    for fn in selected:
        try:
            fn(ctx)
            print(f"PASS {fn.__name__}")
        except CheckFailed as exc:
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
        except Exception:  # a crashing check is a failure too
            failures += 1
            print(f"FAIL {fn.__name__}: crashed\n{traceback.format_exc()}")
    print(f"\n{len(selected) - failures} passed, {failures} failed")
    if not selected:
        print(f"no checks match {args.filter!r}")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write the build-and-check script and dev server script**

`scripts/check.sh`:
```bash
#!/usr/bin/env bash
# Build exampleSite (strict: any warning fails) and the edge-case fixture,
# then run the output assertions in scripts/checks/.
# Usage: scripts/check.sh [check-name-filter]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/.check"
THEMES_DIR="$(dirname "$ROOT")"
THEME="$(basename "$ROOT")"
MAIN_BASE="https://example.org/"
EDGE_BASE="https://edge.example.org/sub/"

rm -rf "$OUT"
mkdir -p "$OUT"

echo "==> exampleSite (strict)"
hugo --source "$ROOT/exampleSite" --themesDir "$THEMES_DIR" --theme "$THEME" \
  --destination "$OUT/main" --baseURL "$MAIN_BASE" \
  --panicOnWarning --printI18nWarnings --printPathWarnings --logLevel warn

echo "==> tests/edge (warnings expected, captured in .check/edge.log)"
if ! hugo --source "$ROOT/tests/edge" --themesDir "$THEMES_DIR" --theme "$THEME" \
  --destination "$OUT/edge" --baseURL "$EDGE_BASE" \
  --printI18nWarnings --logLevel warn >"$OUT/edge.log" 2>&1; then
  cat "$OUT/edge.log"
  echo "edge build failed" >&2
  exit 1
fi

echo "==> assertions"
python3 "$ROOT/scripts/check_site.py" \
  --main "$OUT/main" --main-base "$MAIN_BASE" \
  --edge "$OUT/edge" --edge-base "$EDGE_BASE" --edge-log "$OUT/edge.log" "$@"
```

`scripts/serve.sh`:
```bash
#!/usr/bin/env bash
# Serve the example site with live reload: scripts/serve.sh [extra hugo flags]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec hugo server --source "$ROOT/exampleSite" \
  --themesDir "$(dirname "$ROOT")" --theme "$(basename "$ROOT")" "$@"
```

Run: `chmod +x scripts/check.sh scripts/serve.sh scripts/check_site.py`

- [ ] **Step 5: Write the failing core checks**

`scripts/checks/core.py`:
```python
from checklib import check, expect


@check
def core_homepages_exist(ctx):
    for rel in ("index.html", "sv/index.html"):
        expect(ctx.main.exists(rel), f"exampleSite did not build {rel}")
    expect(ctx.edge.exists("index.html"), "edge site did not build index.html")


@check
def core_html_lang_uses_locale(ctx):
    cases = [(ctx.main, "/", "en-GB"), (ctx.main, "/sv/", "sv-SE"), (ctx.edge, "/", "sv-SE")]
    for site, rel, lang in cases:
        html = site.html(rel).find("html")
        expect(html is not None and html.attrs.get("lang") == lang,
               f"{rel}: expected <html lang={lang!r}>, got {html and html.attrs.get('lang')!r}")


@check
def core_internal_links_resolve(ctx):
    for name, site in (("exampleSite", ctx.main), ("edge", ctx.edge)):
        broken = site.broken_links()
        expect(not broken, f"{name} has broken links:\n  " + "\n  ".join(broken[:40]))
```

- [ ] **Step 6: Run the checks to verify they fail**

Run: `scripts/check.sh`
Expected: FAIL. Hugo exits with an error because `exampleSite/hugo.toml` does not exist yet (`Unable to locate config file` or similar).

- [ ] **Step 7: Create the minimal layouts**

`layouts/baseof.html` (replaced in Task 2):
```html
<!doctype html>
<html lang="{{ site.Language.Locale | default site.Language.Name }}" class="no-js">
<head>
<meta charset="utf-8">
<title>{{ .Title }}</title>
</head>
<body>
{{ block "main" . }}{{ end }}
</body>
</html>
```

`layouts/home.html` (replaced in Task 8):
```html
{{ define "main" }}<h1>{{ site.Title }}</h1>{{ .Content }}{{ end }}
```

`layouts/single.html` (replaced in Task 5):
```html
{{ define "main" }}<h1>{{ .Title }}</h1>{{ .Content }}{{ end }}
```

`layouts/list.html` (replaced in Task 5):
```html
{{ define "main" }}<h1>{{ .Title }}</h1>{{ .Content }}{{ end }}
```

- [ ] **Step 8: Create the exampleSite and edge fixture configs and homepages**

`exampleSite/hugo.toml`:
```toml
baseURL = "https://example.org/"
theme = "isoc-hugo-theme"
defaultContentLanguage = "en"
timeZone = "Europe/Stockholm"
enableRobotsTXT = true

[languages]
  [languages.en]
    contentDir = "content/en"
    locale = "en-GB"
    label = "English"
    title = "Internet Society Chapter"
    weight = 1
    [languages.en.params]
      description = "Demo site for the ISOC Chapters Hugo theme: an Internet Society chapter working for an open, globally connected, secure and trustworthy Internet."
  [languages.sv]
    contentDir = "content/sv"
    locale = "sv-SE"
    label = "Svenska"
    title = "Internet Society Sverige"
    weight = 2
    [languages.sv.params]
      description = "Demosajt för temat ISOC Chapters: en chapter inom Internet Society som arbetar för ett öppet, globalt sammankopplat, säkert och pålitligt internet."

[params]
  pagerSize = 4
```

`exampleSite/content/en/_index.md`:
```markdown
---
title: Home
---
```

`exampleSite/content/sv/_index.md`:
```markdown
---
title: Hem
---
```

`tests/edge/hugo.toml` (single language, served from a sub-path):
```toml
# Edge-case fixture: one language, sub-path base URL, deliberately odd settings.
baseURL = "https://edge.example.org/sub/"
theme = "isoc-hugo-theme"
defaultContentLanguage = "sv"
timeZone = "Europe/Stockholm"

[languages]
  [languages.sv]
    locale = "sv-SE"
    label = "Svenska"
    title = "Edge Chapter"
    weight = 1
```

`tests/edge/content/_index.md`:
```markdown
---
title: Edge
---
```

- [ ] **Step 9: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: both builds succeed; output ends with `3 passed, 0 failed`, including `PASS core_internal_links_resolve`. (The 404 page arrives with its template in Task 5.)

---

### Task 2: Head, fonts, design tokens and base styles

**Files:**
- Create: `scripts/fetch-fonts.py`, `static/fonts/hind/*.woff2`, `static/fonts/hind/OFL.txt`, `assets/css/fonts.css` (generated)
- Create: `assets/css/tokens.css`, `assets/css/base.css`, `assets/css/layout.css`
- Create: `i18n/en.toml`, `i18n/sv.toml`
- Create: `layouts/_partials/head.html`, `layouts/_partials/head/css.html`, `layouts/_partials/head/meta.html`, `layouts/_partials/func/description.html`, `layouts/_partials/func/body-class.html`
- Create: `static/favicon.ico` (copied from the WP theme)
- Modify (overwrite): `layouts/baseof.html`
- Modify: `tests/edge/hugo.toml` (add colour override)
- Test: `scripts/checks/head.py`

**Interfaces:**
- Consumes: Task 1 harness.
- Produces:
  - `partial "func/description.html" PAGE` → plain-text meta description (string).
  - `partial "func/body-class.html" PAGE` → space-separated body classes (string).
  - CSS bundle: `head/css.html` concatenates, in order, every file that exists among `fonts tokens base layout header nav hero content cards news blocks events search footer motion` under `assets/css/`, plus an optional site-level `assets/css/custom.css`, then minifies and fingerprints it. Later tasks just create their CSS file; no edit to `head/css.html` is needed.
  - CSS custom properties defined in `tokens.css` (names used by all later CSS): `--isoc-*` palette, `--color-text`, `--color-heading`, `--color-link`, `--color-accent`, `--color-header`, `--color-footer`, `--color-button`, `--color-bg`, `--color-band-light`, `--color-band-green`, `--color-border`, `--font-sans`, `--wrap`, `--wrap-1180`, `--wrap-960`, `--wrap-800`, `--wrap-max`, `--header-height`, `--section-space`, `--radius`, `--radius-pill`, `--shadow-card`, `--shadow-card-hover`, `--shadow-panel`, `--transition`.
  - Utility classes from `base.css`/`layout.css`: `.sr-only`, `.skip-link`, `.btn`, `.btn--secondary`, `.btn--white`, `.btn-row`, `.wrap`, `.wrap--1180`, `.wrap--960`, `.wrap--800`, `.section`, `.band`, `.band--white|light|green|navy|blue`, `.notice`, `.notice--warning`, `.columns`, `.column`.
  - Site param `params.colors.{link,accent,header,footer,button}` → inline `<style>` overriding the matching `--color-*` variables.
  - All i18n keys (full list in Step 4); later tasks use them without editing i18n files.

- [ ] **Step 1: Write the failing head checks**

`scripts/checks/head.py`:
```python
import os
import re

from checklib import check, expect


def _stylesheet(site, rel="/"):
    links = [l for l in site.html(rel).select("link[rel=stylesheet]")]
    expect(len(links) == 1, f"{rel}: expected exactly one stylesheet link, found {len(links)}")
    return links[0]


@check
def head_css_bundle_is_fingerprinted_with_sri(ctx):
    for site in (ctx.main, ctx.edge):
        link = _stylesheet(site)
        href = link.attrs["href"]
        expect(re.search(r"/css/main\.min\.[0-9a-f]{64}\.css$", href), f"unexpected css href {href}")
        expect(link.attrs.get("integrity", "").startswith("sha256-"), "stylesheet lacks SRI integrity")
        expect(href.startswith(site.base_path), f"css href {href} ignores base path {site.base_path}")


@check
def head_css_contains_tokens_and_fonts(ctx):
    css = open(ctx.main.resolve(_stylesheet(ctx.main).attrs["href"], "index.html"), encoding="utf-8").read()
    for needle in ("--isoc-navy:#0c1c2c", "--color-text:var(--isoc-navy)", "@font-face",
                   "font-family:hind", ".skip-link", ".btn--white", ".wrap--1180"):
        expect(needle.lower() in css.lower().replace('"', "").replace(" ", ""), f"css bundle lacks {needle!r}")
    fonts = re.findall(r"url\(\"?(\.\./fonts/[^\")]+)\"?\)", css)
    expect(len(fonts) == 10, f"expected 10 font urls (5 weights x 2 subsets), found {len(fonts)}")
    for url in fonts:
        path = os.path.join(ctx.main.public, url.replace("../", "", 1))
        expect(os.path.isfile(path), f"font file missing: {url}")


@check
def head_preloads_fonts_and_favicon(ctx):
    root = ctx.main.html("/")
    preloads = [l.attrs["href"] for l in root.select("link[rel=preload][as=font]")]
    expect(any(h.endswith("/fonts/hind/hind-400-latin.woff2") for h in preloads), f"no hind 400 preload: {preloads}")
    expect(root.find('link[rel=icon]') is not None, "no favicon link")
    edge_icon = ctx.edge.html("/").find("link[rel=icon]").attrs["href"]
    expect(edge_icon == "/sub/favicon.ico", f"edge favicon should respect base path, got {edge_icon}")


@check
def head_meta_description_canonical_og(ctx):
    root = ctx.main.html("/")
    desc = root.find("meta[name=description]")
    expect(desc is not None and desc.attrs["content"].startswith("Demo site for the ISOC Chapters"), "home meta description missing")
    expect(root.find("link[rel=canonical]").attrs["href"] == "https://example.org/", "wrong canonical")
    for prop in ("og:title", "og:description", "og:url", "og:type", "og:site_name", "og:locale"):
        expect(root.find(f"meta[property={prop}]") is not None, f"missing {prop}")
    expect(root.find("meta[property=og:locale]").attrs["content"] == "en_GB", "og:locale should be en_GB")
    expect(root.find("meta[name=twitter:card]") is not None, "missing twitter:card")
    sv_desc = ctx.main.html("/sv/").find("meta[name=description]").attrs["content"]
    expect(sv_desc.startswith("Demosajt"), f"sv description not localised: {sv_desc!r}")


@check
def head_hreflang_alternates(ctx):
    alts = {l.attrs["hreflang"]: l.attrs["href"] for l in ctx.main.html("/").select("link[rel=alternate][hreflang]")}
    expect(alts == {"en-GB": "https://example.org/", "sv-SE": "https://example.org/sv/"}, f"hreflang: {alts}")
    expect(not ctx.edge.html("/").select("link[hreflang]"), "single-language site must not emit hreflang")


@check
def head_skip_link_and_main_landmark(ctx):
    root = ctx.main.html("/")
    skip = root.find("a.skip-link")
    expect(skip is not None and skip.attrs["href"] == "#main", "skip link missing")
    expect(skip.text() == "Skip to main content", f"skip link text {skip.text()!r}")
    expect(ctx.main.html("/sv/").find("a.skip-link").text() == "Hoppa till huvudinnehållet", "sv skip link")
    expect(root.find("main#main") is not None, "main#main missing")


@check
def head_color_overrides(ctx):
    edge_styles = " ".join(s.text() for s in ctx.edge.html("/").select("style"))
    expect("--color-link:#7e245c" in edge_styles.replace(" ", ""), f"edge colour override missing: {edge_styles!r}")
    main_styles = " ".join(s.text() for s in ctx.main.html("/").select("style"))
    expect("--color-link" not in main_styles, "exampleSite sets no colours, so no override style expected")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh head`
Expected: FAIL. Every `head_*` check fails (no stylesheet link: `expected exactly one stylesheet link, found 0`).

- [ ] **Step 3: Fetch the Hind font**

`scripts/fetch-fonts.py`:
```python
#!/usr/bin/env python3
"""Download Hind (SIL OFL 1.1) from Google Fonts and write self-hosted @font-face rules.

Run from anywhere: python3 scripts/fetch-fonts.py
Writes static/fonts/hind/*.woff2, static/fonts/hind/OFL.txt and assets/css/fonts.css.
"""
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_URL = "https://fonts.googleapis.com/css2?family=Hind:wght@300;400;500;600;700&display=swap"
OFL_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/hind/OFL.txt"
# A modern browser UA makes Google Fonts serve woff2 with unicode-range subsets.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
SUBSETS = ("latin", "latin-ext")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main():
    css = get(CSS_URL).decode()
    font_dir = os.path.join(ROOT, "static", "fonts", "hind")
    os.makedirs(font_dir, exist_ok=True)
    rules = []
    for subset, block in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S):
        if subset not in SUBSETS:
            continue
        weight = re.search(r"font-weight: (\d+);", block).group(1)
        url = re.search(r"src: url\((.*?)\)", block).group(1)
        unicode_range = re.search(r"unicode-range: (.*?);", block).group(1)
        name = f"hind-{weight}-{subset}.woff2"
        with open(os.path.join(font_dir, name), "wb") as fh:
            fh.write(get(url))
        rules.append(
            "@font-face {\n"
            '  font-family: "Hind";\n'
            "  font-style: normal;\n"
            f"  font-weight: {weight};\n"
            "  font-display: swap;\n"
            f'  src: url("../fonts/hind/{name}") format("woff2");\n'
            f"  unicode-range: {unicode_range};\n"
            "}\n"
        )
    if len(rules) != 10:
        raise SystemExit(f"expected 10 font files (5 weights x 2 subsets), got {len(rules)}")
    with open(os.path.join(font_dir, "OFL.txt"), "wb") as fh:
        fh.write(get(OFL_URL))
    header = ("/* Hind by Indian Type Foundry, SIL Open Font License 1.1 (static/fonts/hind/OFL.txt).\n"
              "   Generated by scripts/fetch-fonts.py; do not edit by hand. */\n")
    os.makedirs(os.path.join(ROOT, "assets", "css"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "css", "fonts.css"), "w", encoding="utf-8") as fh:
        fh.write(header + "\n".join(rules))
    print(f"wrote {len(rules)} font files to {font_dir}")


if __name__ == "__main__":
    main()
```

Run:
```bash
chmod +x scripts/fetch-fonts.py && python3 scripts/fetch-fonts.py && ls static/fonts/hind
```
Expected: `wrote 10 font files …`; listing shows `hind-300-latin.woff2 … hind-700-latin-ext.woff2` and `OFL.txt`.

Copy the favicon from the reference theme:
```bash
cp genesis-child-chapters-main/favicon.ico static/favicon.ico
```

- [ ] **Step 4: Create the translation files**

`i18n/en.toml`:
```toml
skipToContent = "Skip to main content"
mainMenu = "Main menu"
footerMenu = "Footer menu"
openMenu = "Open menu"
closeMenu = "Close menu"
toggleSubmenu = "Show submenu for {{ .Name }}"
language = "Language"
join = "Join"
search = "Search"
searchSite = "Search this website"
searchPlaceholder = "Search…"
searchNoResults = "No results for “{query}”."
searchResultsCount = "{count} results"
searchSeeAll = "See all results"
searchError = "Search is not available right now."
searchJsRequired = "Search requires JavaScript to be enabled in your browser."
moreNews = "More news"
relatedPosts = "Related posts"
by = "by"
imageCopyright = "Image copyright: {{ .Credit }}"
categories = "Categories"
noPosts = "There are no posts yet."
pagination = "Pagination"
pageN = "Page {{ .Number }}"
newerPosts = "Newer"
olderPosts = "Older"
upcomingEvents = "Upcoming events"
pastEvents = "Past events"
allEvents = "All events"
noUpcomingEvents = "There are no upcoming events right now."
eventDate = "Date"
location = "Location"
online = "Online"
joinOnline = "Join online"
organizer = "Organizer"
register = "Register"
registrationClosed = "Registration closed"
addToCalendar = "Add to calendar"
eventPassed = "This event has already taken place."
notFoundTitle = "Page not found"
notFoundText = "Sorry, we couldn't find the page you were looking for. It may have moved, or the address may be mistyped."
backHome = "Go to the homepage"
tableOfContents = "Contents"
```

`i18n/sv.toml`:
```toml
skipToContent = "Hoppa till huvudinnehållet"
mainMenu = "Huvudmeny"
footerMenu = "Sidfotsmeny"
openMenu = "Öppna menyn"
closeMenu = "Stäng menyn"
toggleSubmenu = "Visa undermeny för {{ .Name }}"
language = "Språk"
join = "Bli medlem"
search = "Sök"
searchSite = "Sök på webbplatsen"
searchPlaceholder = "Sökord…"
searchNoResults = "Inga träffar för ”{query}”."
searchResultsCount = "{count} träffar"
searchSeeAll = "Visa alla träffar"
searchError = "Sökningen är inte tillgänglig just nu."
searchJsRequired = "Sökningen kräver att JavaScript är aktiverat i din webbläsare."
moreNews = "Fler nyheter"
relatedPosts = "Relaterade inlägg"
by = "av"
imageCopyright = "Bild: {{ .Credit }}"
categories = "Kategorier"
noPosts = "Det finns inga inlägg ännu."
pagination = "Sidnavigering"
pageN = "Sida {{ .Number }}"
newerPosts = "Nyare"
olderPosts = "Äldre"
upcomingEvents = "Kommande evenemang"
pastEvents = "Tidigare evenemang"
allEvents = "Alla evenemang"
noUpcomingEvents = "Det finns inga kommande evenemang just nu."
eventDate = "Datum"
location = "Plats"
online = "Online"
joinOnline = "Anslut online"
organizer = "Arrangör"
register = "Anmäl dig"
registrationClosed = "Anmälan stängd"
addToCalendar = "Lägg till i kalendern"
eventPassed = "Det här evenemanget har redan ägt rum."
notFoundTitle = "Sidan hittades inte"
notFoundText = "Tyvärr kunde vi inte hitta sidan du letade efter. Den kan ha flyttats, eller så är adressen felstavad."
backHome = "Gå till startsidan"
tableOfContents = "Innehåll"
```

- [ ] **Step 5: Create the design tokens, base and layout CSS**

`assets/css/tokens.css`:
```css
/* Design tokens. Values come from the Genesis "Internet Chapters" theme
   (genesis-child-chapters-main/scss/_variables.scss). Sites override the
   --color-* roles through params.colors in hugo.toml. */
:root {
  /* Brand palette */
  --isoc-navy: #0c1c2c;
  --isoc-blue: #2b72d6;
  --isoc-bright-blue: #1d69d3;
  --isoc-light-blue: #3a82e4;
  --isoc-depth-blue: #24366e;
  --isoc-blue-bg: #27376a;
  --isoc-teal: #40b2a4;
  --isoc-depth-green: #085856;
  --isoc-depth-teal: #143e50;
  --isoc-purple: #7e245c;
  --isoc-orange: #d25238;
  --isoc-yellow: #eeca4a;
  --isoc-neutral-white: #eff2ec;
  --isoc-neutral-green: #d0e6da;
  --isoc-putty: #dedad0;
  --isoc-light-gray: #f1f1f1;
  --isoc-gray: #6b6b6b;

  /* Roles */
  --color-text: var(--isoc-navy);
  --color-heading: var(--isoc-depth-blue);
  --color-link: var(--isoc-blue);
  --color-accent: var(--isoc-teal);
  --color-header: var(--isoc-navy);
  --color-footer: var(--isoc-navy);
  --color-button: var(--isoc-depth-blue);
  --color-bg: #fff;
  --color-band-light: var(--isoc-neutral-white);
  --color-band-green: var(--isoc-neutral-green);
  --color-border: #d9dde3;

  /* Typography */
  --font-sans: "Hind", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;

  /* Layout */
  --wrap: 1280px;
  --wrap-1180: 1180px;
  --wrap-960: 960px;
  --wrap-800: 800px;
  --wrap-max: 90%;
  --header-height: 126px;
  --section-space: 60px;

  /* Shape and effects */
  --radius: 4px;
  --radius-pill: 24px;
  --shadow-card: 0 0 22px 0 rgba(201, 205, 208, 0.6);
  --shadow-card-hover: 0 0 22px 0 rgba(201, 205, 208, 1);
  --shadow-panel: 0 3px 30px rgba(0, 0, 0, 0.2);
  --transition: all 0.3s ease;
}

@media (max-width: 1179px) {
  :root {
    --header-height: 80px;
    --section-space: 48px;
  }
}
```

`assets/css/base.css`:
```css
/* Base elements, typography, buttons. Sizes follow scss/style/_common.scss. */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  scroll-padding-top: calc(var(--header-height) + 16px);
}

body {
  margin: 0;
  padding-top: var(--header-height);
  background: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-sans);
  font-size: 18px;
  font-weight: 400;
  line-height: 28px;
  overflow-x: hidden;
}

body.menu-open {
  overflow: hidden;
}

img,
svg,
video {
  max-width: 100%;
  height: auto;
}

.icon {
  width: 1em;
  height: 1em;
  flex-shrink: 0;
  vertical-align: -0.125em;
}

a {
  color: var(--color-link);
  text-underline-offset: 0.15em;
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}

a:hover,
a:focus {
  color: var(--color-text);
  text-decoration: none;
}

:focus-visible {
  outline: 3px solid var(--color-link);
  outline-offset: 2px;
}

main:focus {
  outline: none;
}

p {
  margin: 0 0 30px;
}

p:last-child {
  margin-bottom: 0;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  margin: 0 0 20px;
  font-family: inherit;
  font-weight: 400;
  line-height: 1.2;
  color: inherit;
}

h1 { font-size: 30px; }
h2 { font-size: 36px; line-height: 1.53; color: var(--isoc-blue); }
h3 { font-size: 30px; line-height: 1.33; }
h4 { font-size: 25px; line-height: 1.28; }
h5 { font-size: 18px; }
h6 { font-size: 16px; }

ul,
ol {
  margin: 0 0 30px;
  padding-left: 1.5em;
}

li {
  margin-bottom: 0.25em;
}

b,
strong {
  font-weight: 700;
}

hr {
  width: 70%;
  margin: 50px auto;
  border: 0;
  border-top: 1px solid var(--color-border);
}

table {
  width: 100%;
  margin: 0 0 30px;
  border-collapse: collapse;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
  vertical-align: top;
}

th {
  font-weight: 600;
}

input,
button,
select,
textarea {
  font: inherit;
  color: inherit;
}

@media (max-width: 1023px) {
  h2 { font-size: 32px; line-height: 1.44; }
  h3 { font-size: 28px; }
}

@media (max-width: 767px) {
  h2 { font-size: 30px; line-height: 1.45; }
  h3 { font-size: 25px; }
  h4 { font-size: 22px; }
}

/* Accessibility helpers */
.sr-only {
  position: absolute !important;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.skip-link {
  position: absolute;
  top: -100px;
  left: 16px;
  z-index: 1000;
  padding: 12px 20px;
  background: #fff;
  color: var(--isoc-navy);
  font-weight: 600;
  border-radius: var(--radius);
}

.skip-link:focus {
  top: 16px;
}

/* Buttons: pill-shaped, depth blue; hover inverts (as .blue-button in the WP theme). */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5em;
  min-width: 173px;
  padding: 10px 30px 8px;
  border: 1.5px solid var(--color-button);
  border-radius: var(--radius-pill);
  background: var(--color-button);
  color: #fff;
  font-size: 18px;
  font-weight: 400;
  line-height: 28px;
  text-decoration: none;
  cursor: pointer;
  transition: var(--transition);
}

.btn:hover,
.btn:focus-visible {
  background: #fff;
  color: var(--color-button);
}

.btn--secondary {
  background: transparent;
  color: var(--color-button);
}

.btn--secondary:hover,
.btn--secondary:focus-visible {
  background: var(--color-button);
  color: #fff;
}

.btn--white {
  border-color: #fff;
  background: #fff;
  color: var(--isoc-navy);
}

.btn--white:hover,
.btn--white:focus-visible {
  background: transparent;
  color: #fff;
}

.btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 30px;
}
```

`assets/css/layout.css`:
```css
/* Containers and full-width bands. Widths follow the WP theme's
   $fixed-body (1280), $fixed-1180, $fixed-96 (960) with $max-fixed (90%). */
.wrap {
  width: var(--wrap);
  max-width: var(--wrap-max);
  margin-inline: auto;
}

.wrap--1180 { width: var(--wrap-1180); }
.wrap--960 { width: var(--wrap-960); }
.wrap--800 { width: var(--wrap-800); }

.section {
  padding-block: var(--section-space);
}

.band {
  padding-block: var(--section-space);
}

.band--white { background: #fff; }
.band--light { background: var(--color-band-light); }
.band--green { background: var(--color-band-green); }

.band--navy,
.band--blue {
  color: #fff;
}

.band--navy { background: var(--isoc-navy); }
.band--blue { background: var(--isoc-depth-blue); }

.band--navy h2,
.band--blue h2,
.band--navy a:not(.btn),
.band--blue a:not(.btn) {
  color: #fff;
}

.band--navy :focus-visible,
.band--blue :focus-visible {
  outline-color: var(--color-accent);
}

.notice {
  margin: 0 0 30px;
  padding: 16px 20px;
  border-left: 4px solid var(--color-link);
  background: var(--color-band-light);
}

.notice--warning {
  border-left-color: var(--isoc-orange);
  background: #fbeee9;
}

.columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 40px;
  margin: 0 0 30px;
}
```

- [ ] **Step 6: Create the head partials and the document shell**

`layouts/_partials/func/description.html`:
```html
{{- /* Returns a plain-text meta description for a page. */ -}}
{{- $d := .Description -}}
{{- if and (not $d) .IsPage -}}
  {{- $d = .Summary | plainify | htmlUnescape | strings.TrimSpace | truncate 160 -}}
{{- end -}}
{{- if not $d -}}
  {{- $d = .Params.lead | default site.Params.description -}}
{{- end -}}
{{- return ($d | plainify | htmlUnescape | strings.TrimSpace) -}}
```

`layouts/_partials/func/body-class.html`:
```html
{{- $c := slice (printf "kind-%s" .Kind) (printf "type-%s" .Type) -}}
{{- if .IsHome }}{{ $c = $c | append "is-home" }}{{ end -}}
{{- return (delimit $c " ") -}}
```

`layouts/_partials/head/css.html`:
```html
{{- /* Bundle every component stylesheet that exists, in cascade order. */ -}}
{{- $names := slice "fonts" "tokens" "base" "layout" "header" "nav" "hero" "content" "cards" "news" "blocks" "events" "search" "footer" "motion" "custom" -}}
{{- $files := slice -}}
{{- range $names -}}
  {{- with resources.Get (printf "css/%s.css" .) -}}
    {{- $files = $files | append . -}}
  {{- end -}}
{{- end -}}
{{- $css := $files | resources.Concat "css/main.css" | minify | fingerprint -}}
<link rel="stylesheet" href="{{ $css.RelPermalink }}" integrity="{{ $css.Data.Integrity }}">
{{- with site.Params.colors }}
{{- $colors := . -}}
{{- $vars := slice -}}
{{- range $key := slice "link" "accent" "header" "footer" "button" -}}
  {{- with index $colors $key -}}
    {{- $vars = $vars | append (printf "--color-%s:%s" $key .) -}}
  {{- end -}}
{{- end -}}
{{- with $vars }}
<style>:root{ {{- delimit . ";" | safeCSS -}} }</style>
{{- end }}
{{- end }}
```

`layouts/_partials/head/meta.html`:
```html
{{- $desc := partial "func/description.html" . -}}
{{- $image := "" -}}
{{- with .Params.image -}}
  {{- with partial "func/resource.html" (dict "page" $ "src" .) }}{{ $image = .Permalink }}{{ end -}}
{{- end -}}
{{- if not $image -}}
  {{- with site.Params.ogImage }}{{ with resources.Get . }}{{ $image = .Permalink }}{{ end }}{{ end -}}
{{- end }}
<meta property="og:site_name" content="{{ site.Title }}">
<meta property="og:title" content="{{ if .IsHome }}{{ site.Title }}{{ else }}{{ .Title }}{{ end }}">
<meta property="og:description" content="{{ $desc }}">
<meta property="og:url" content="{{ .Permalink }}">
<meta property="og:type" content="{{ if .IsPage }}article{{ else }}website{{ end }}">
<meta property="og:locale" content="{{ replace (site.Language.Locale | default site.Language.Name) "-" "_" }}">
{{- with $image }}
<meta property="og:image" content="{{ . }}">
<meta name="twitter:card" content="summary_large_image">
{{- else }}
<meta name="twitter:card" content="summary">
{{- end }}
{{- if and .IsPage (eq .Type "posts") }}
<meta property="article:published_time" content="{{ .Date.Format "2006-01-02T15:04:05Z07:00" }}">
{{- end }}
```

`head/meta.html` calls `func/resource.html`, which Task 5 creates. Create it now so the head works, with this exact content. Task 5 reuses it unchanged.

`layouts/_partials/func/resource.html`:
```html
{{- /* Resolve an image/file reference: page resource first, then global assets/.
       Context: dict "page" PAGE (may be nil) "src" STRING. Returns a resource or "". */ -}}
{{- $r := "" -}}
{{- $src := .src -}}
{{- if and $src (not (urls.Parse $src).IsAbs) -}}
  {{- with .page -}}
    {{- with .Resources.Get $src }}{{ $r = . }}{{ end -}}
  {{- end -}}
  {{- if not $r -}}
    {{- with resources.Get (strings.TrimPrefix "/" $src) }}{{ $r = . }}{{ end -}}
  {{- end -}}
{{- end -}}
{{- return $r -}}
```

`layouts/_partials/head.html`:
```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ if .IsHome }}{{ site.Title }}{{ else }}{{ .Title }} – {{ site.Title }}{{ end }}</title>
<meta name="description" content="{{ partial "func/description.html" . }}">
<link rel="canonical" href="{{ .Permalink }}">
{{- if .IsTranslated }}
{{- range .AllTranslations }}
<link rel="alternate" hreflang="{{ .Language.Locale | default .Language.Name }}" href="{{ .Permalink }}">
{{- end }}
{{- end }}
{{- with .OutputFormats.Get "rss" }}
<link rel="alternate" type="application/rss+xml" href="{{ .Permalink }}" title="{{ site.Title }}">
{{- end }}
<script>document.documentElement.classList.replace("no-js", "js");</script>
<link rel="preload" href="{{ "fonts/hind/hind-400-latin.woff2" | relURL }}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{{ "fonts/hind/hind-700-latin.woff2" | relURL }}" as="font" type="font/woff2" crossorigin>
{{ partial "head/css.html" . }}
{{ partial "head/meta.html" . }}
<link rel="icon" href="{{ "favicon.ico" | relURL }}" sizes="any">
```

Overwrite `layouts/baseof.html`:
```html
<!doctype html>
<html lang="{{ site.Language.Locale | default site.Language.Name }}" dir="{{ site.Language.Direction | default "ltr" }}" class="no-js">
<head>
{{ partial "head.html" . }}
</head>
<body class="{{ partial "func/body-class.html" . }}">
<a class="skip-link" href="#main">{{ T "skipToContent" }}</a>
<main id="main" tabindex="-1">
{{ block "main" . }}{{ end }}
</main>
</body>
</html>
```

Add the colour override to the edge fixture. Append to `tests/edge/hugo.toml`:
```toml

[params]
  [params.colors]
    link = "#7e245c"
```

- [ ] **Step 7: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: `PASS` for all `core_*` and `head_*` checks.

---

### Task 3: Header, navigation, language switcher

**Files:**
- Create: `assets/images/logo-isoc-chapters.svg` (downloaded), `assets/images/icons/{search,globe,chevron-down,calendar,map-pin,video,user}.svg`
- Create: `layouts/_partials/icon.html`, `layouts/_partials/func/logo.html`, `layouts/_partials/header.html`, `layouts/_partials/nav-menu.html`, `layouts/_partials/lang-switch.html`, `layouts/_partials/scripts.html`
- Create: `assets/css/header.css`, `assets/css/nav.css`, `assets/js/menu.js`
- Modify: `layouts/baseof.html` (include header and scripts)
- Modify: `exampleSite/hugo.toml` (menus)
- Create exampleSite pages (en): `about/_index.md`, `about/board/index.md`, `about/statutes.md`, `posts/_index.md`, `events/_index.md`, `membership.md`, `contact.md`, `shortcodes/index.md`
- Create exampleSite pages (sv): `om/_index.md`, `om/styrelse/index.md`, `om/stadgar.md`, `nyheter/_index.md`, `evenemang/_index.md`, `medlemskap.md`, `kontakt.md`
- Test: `scripts/checks/header.py`

**Interfaces:**
- Consumes: `T` keys `mainMenu`, `openMenu`, `closeMenu`, `toggleSubmenu`, `language`, `join` (Task 2); `.btn`, `.btn--white`, `.sr-only` (Task 2).
- Produces:
  - `partial "icon.html" (dict "name" NAME ["set" "icons"|"social"] ["class" EXTRA])` → inline `<svg class="icon icon--NAME" aria-hidden="true" …>` read from `assets/images/<set>/<name>.svg`; warns if missing.
  - `partial "func/logo.html" PAGE` → `dict "src" STRING "width" INT "height" INT` (height 0 if unknown).
  - Header DOM contract used by `menu.js`, Task 9 and CSS: `header.site-header[data-header]` > `.site-header__inner` > `a.site-logo`, `div#site-nav.site-nav[data-site-nav]` (contains `nav.nav-primary`, `.lang-switch`, `a.btn--join`), `button.menu-toggle[data-menu-toggle]`. Task 9 inserts the search toggle before the menu toggle and the search panel before `</header>`.
  - Dropdown contract: any `button[data-submenu-toggle]` or `button[data-dropdown-toggle]` toggles `aria-expanded`; CSS shows the next sibling list when `aria-expanded="true"`.
  - `layouts/_partials/scripts.html` is the single place for page-end scripts (Task 9 appends to it).
  - exampleSite translation keys: `about`, `board`, `statutes`, `news`, `events`, `membership`, `contact` link the en and sv pages. The sv news and events sections set `type` + `cascade.type` so templates treat them as `posts`/`events`.

- [ ] **Step 1: Write the failing header checks**

`scripts/checks/header.py`:
```python
import re

from checklib import check, expect


def _top_items(root):
    ul = root.find("nav.nav-primary ul.menu")
    expect(ul is not None, "no main menu <ul>")
    return ul.kids("li")


@check
def header_logo_and_join(ctx):
    root = ctx.main.html("/")
    logo = root.find("header.site-header a.site-logo img")
    expect(logo is not None, "no logo image in header")
    expect(logo.attrs.get("alt") == "Internet Society Chapter", f"logo alt {logo.attrs.get('alt')!r}")
    expect(logo.attrs.get("width") == "233" and logo.attrs.get("height") == "47", "default logo needs width/height")
    expect(root.find("a.site-logo").attrs["href"] == "/", "logo should link to the homepage")
    expect(ctx.main.html("/sv/").find("a.site-logo").attrs["href"] == "/sv/", "sv logo should link to /sv/")
    join = root.find("header.site-header a.btn--join")
    expect(join is not None, "no Join button")
    expect(join.attrs["href"] == "https://community.internetsociety.org/s/new-registration", f"join href {join.attrs['href']}")
    expect(join.text() == "Join", f"join label {join.text()!r}")
    expect(ctx.main.html("/sv/").find("a.btn--join").text() == "Bli medlem", "sv join label")


@check
def header_main_menu_top_level(ctx):
    expected = {
        "/": ["About", "News", "Events", "Membership", "Contact"],
        "/sv/": ["Om ISOC-SE", "Nyheter", "Evenemang", "Medlemskap", "Kontakt"],
    }
    for rel, names in expected.items():
        got = [li.kids("a")[0].text() for li in _top_items(ctx.main.html(rel))]
        expect(got == names, f"{rel}: menu {got}")
    hrefs = [li.kids("a")[0].attrs["href"] for li in _top_items(ctx.main.html("/sv/"))]
    expect(hrefs == ["/sv/om/", "/sv/nyheter/", "/sv/evenemang/", "/sv/medlemskap/", "/sv/kontakt/"], f"sv hrefs {hrefs}")


@check
def header_submenu_structure(ctx):
    about = _top_items(ctx.main.html("/"))[0]
    expect("has-children" in about.classes, "About item lacks has-children")
    btn = about.find("button.submenu-toggle")
    expect(btn is not None and btn.attrs.get("aria-expanded") == "false", "submenu toggle missing")
    expect(btn.find(".sr-only").text() == "Show submenu for About", f"toggle label {btn.find('.sr-only').text()!r}")
    expect(btn.find("svg.icon") is not None, "toggle needs a chevron icon")
    links = about.select("ul.menu--sub a")
    expect([a.text() for a in links] == ["Board", "Statutes"], f"submenu {[a.text() for a in links]}")
    expect([a.attrs["href"] for a in links] == ["/about/board/", "/about/statutes/"], "submenu hrefs")
    sv = [a.attrs["href"] for a in ctx.main.html("/sv/").select("nav.nav-primary ul.menu--sub a")]
    expect(sv == ["/sv/om/styrelse/", "/sv/om/stadgar/"], f"sv submenu hrefs {sv}")


@check
def header_marks_current_page(ctx):
    root = ctx.main.html("/about/board/")
    current = [a.text() for a in root.select("nav.nav-primary a[aria-current=page]")]
    expect(current == ["Board"], f"aria-current on {current}")
    expect("is-active" in _top_items(root)[0].classes, "parent of the current page should be is-active")


@check
def header_language_switcher(ctx):
    sw = ctx.main.html("/about/").find(".lang-switch")
    expect(sw is not None, "no language switcher")
    links = {a.attrs["lang"]: a.attrs["href"] for a in sw.select("a")}
    expect(links == {"en-GB": "/about/", "sv-SE": "/sv/om/"}, f"switcher links {links}")
    expect([a.text() for a in sw.select("a")] == ["English", "Svenska"], "switcher labels")
    current = sw.select("a[aria-current]")
    expect(len(current) == 1 and current[0].attrs["lang"] == "en-GB", "current language not marked")
    toggle = sw.find("button.lang-switch__toggle")
    expect(toggle.attrs.get("aria-expanded") == "false", "language toggle needs aria-expanded")
    expect(toggle.find(".lang-switch__current").text() == "EN", "toggle should show EN")


@check
def header_language_switcher_untranslated_page(ctx):
    links = {a.attrs["lang"]: a.attrs["href"] for a in ctx.main.html("/shortcodes/").select(".lang-switch a")}
    expect(links.get("sv-SE") == "/sv/", f"untranslated page should link to /sv/, got {links}")


@check
def header_menu_toggle_and_script(ctx):
    root = ctx.main.html("/")
    toggle = root.find("button.menu-toggle")
    expect(toggle is not None and toggle.attrs.get("aria-controls") == "site-nav"
           and toggle.attrs.get("aria-expanded") == "false", "menu toggle attributes")
    expect(toggle.find(".sr-only").text() == "Open menu", "menu toggle label")
    expect(root.find("#site-nav") is not None, "menu target #site-nav missing")
    menu = [s for s in root.select("script[src]") if re.search(r"/js/menu\.min\.[0-9a-f]{64}\.js$", s.attrs["src"])]
    expect(menu, "menu.js not loaded")
    expect("defer" in menu[0].attrs and menu[0].attrs.get("integrity", "").startswith("sha256-"), "menu.js needs defer + SRI")


@check
def header_edge_single_language_no_menu(ctx):
    root = ctx.edge.html("/")
    expect(root.find("header.site-header") is not None, "edge header missing")
    expect(root.find(".lang-switch") is None, "single-language site must not show a language switcher")
    expect(root.find("nav.nav-primary") is None, "no menu configured: <nav> must be omitted")
    expect(root.find("a.site-logo").attrs["href"] == "/sub/", "edge logo should link to /sub/")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh header`
Expected: FAIL. Every `header_*` check fails (`no logo image in header`, `no main menu <ul>`, and `missing output file: shortcodes/index.html` for the untranslated-page check).

- [ ] **Step 3: Add the logo and UI icons**

```bash
mkdir -p assets/images/icons
curl -fsSL https://chapter-template.isoc.org/wp-content/uploads/2024/01/internet-society-logo-header-233px-47.svg -o assets/images/logo-isoc-chapters.svg
grep -c 'viewBox="0 0 233.14 47.07"' assets/images/logo-isoc-chapters.svg
```
Expected: `1` (the white "Internet Society Chapters" logo, 233×47).

Create each icon file with exactly this content (one line each):

`assets/images/icons/search.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="10.5" cy="10.5" r="7"/><path d="m20.5 20.5-5-5"/></svg>
```

`assets/images/icons/globe.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.8 3.9 6 3.9 9.5s-1.3 6.7-3.9 9.5c-2.6-2.8-3.9-6-3.9-9.5s1.3-6.7 3.9-9.5z"/></svg>
```

`assets/images/icons/chevron-down.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
```

`assets/images/icons/calendar.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>
```

`assets/images/icons/map-pin.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>
```

`assets/images/icons/video.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="6" width="13" height="12" rx="2"/><path d="m15.5 10.5 6-3.5v10l-6-3.5"/></svg>
```

`assets/images/icons/user.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>
```

- [ ] **Step 4: Create the header partials**

`layouts/_partials/icon.html`:
```html
{{- /* Inline an SVG icon from assets/images/<set>/<name>.svg.
       Context: dict "name" NAME ["set" "icons"|"social"] ["class" EXTRA]. */ -}}
{{- $set := .set | default "icons" -}}
{{- $path := printf "images/%s/%s.svg" $set .name -}}
{{- with resources.Get $path -}}
  {{- $class := printf "icon icon--%s" $.name -}}
  {{- with $.class }}{{ $class = printf "%s %s" $class . }}{{ end -}}
  {{- replaceRE `^\s*<svg\b` (printf `<svg class="%s" aria-hidden="true" focusable="false"` $class) .Content 1 | safeHTML -}}
{{- else -}}
  {{- warnf "icon %q not found at assets/%s" $.name $path -}}
{{- end -}}
```

`layouts/_partials/func/logo.html`:
```html
{{- /* Header logo. Returns dict "src" "width" "height" (height 0 when unknown). */ -}}
{{- $width := int (site.Params.logoWidth | default 233) -}}
{{- $src := "" -}}
{{- $height := 0 -}}
{{- $res := "" -}}
{{- with site.Params.logo -}}
  {{- with resources.Get (strings.TrimPrefix "/" .) -}}
    {{- $res = . -}}
  {{- else -}}
    {{- $src = . | relURL -}}
  {{- end -}}
{{- else -}}
  {{- $res = resources.Get "images/logo-isoc-chapters.svg" -}}
  {{- $height = int (math.Round (div (mul 47.0 $width) 233.0)) -}}
{{- end -}}
{{- with $res -}}
  {{- $src = .RelPermalink -}}
  {{- if in (slice "jpeg" "png" "webp" "gif") .MediaType.SubType -}}
    {{- $height = int (math.Round (div (mul (float .Height) $width) .Width)) -}}
  {{- end -}}
{{- end -}}
{{- return dict "src" $src "width" $width "height" $height -}}
```

`layouts/_partials/nav-menu.html`:
```html
{{- /* Recursive menu. Context: dict "page" PAGE "entries" MENU ["sub" true]. */ -}}
{{- $page := .page -}}
<ul class="menu{{ if .sub }} menu--sub{{ end }}">
  {{- range .entries }}
  {{- $current := $page.IsMenuCurrent .Menu . -}}
  {{- $active := or $current ($page.HasMenuCurrent .Menu .) -}}
  {{- with .Page }}{{ if and (not .IsHome) ($page.IsDescendant .) }}{{ $active = true }}{{ end }}{{ end }}
  <li class="menu-item{{ if .HasChildren }} has-children{{ end }}{{ if $active }} is-active{{ end }}">
    <a href="{{ .URL }}"{{ if $current }} aria-current="page"{{ end }}>{{ .Name }}</a>
    {{- if .HasChildren }}
    <button class="submenu-toggle" type="button" aria-expanded="false" data-submenu-toggle>
      {{- partial "icon.html" (dict "name" "chevron-down") -}}
      <span class="sr-only">{{ T "toggleSubmenu" (dict "Name" .Name) }}</span>
    </button>
    {{- partial "nav-menu.html" (dict "page" $page "entries" .Children "sub" true) }}
    {{- end }}
  </li>
  {{- end }}
</ul>
```

`layouts/_partials/lang-switch.html`:
```html
{{- /* Language switcher; rendered only for multilingual sites. Links to the
       translation of the current page, or to that language's homepage. */ -}}
{{- if gt (len hugo.Sites) 1 -}}
{{- $page := . -}}
<div class="lang-switch" data-dropdown>
  <button class="lang-switch__toggle" type="button" aria-expanded="false" aria-controls="lang-switch-menu" data-dropdown-toggle>
    {{- partial "icon.html" (dict "name" "globe") -}}
    <span class="lang-switch__current" aria-hidden="true">{{ upper site.Language.Name }}</span>
    <span class="sr-only">{{ T "language" }}: {{ site.Language.Label | default site.Language.Name }}</span>
    {{- partial "icon.html" (dict "name" "chevron-down") -}}
  </button>
  <ul class="lang-switch__menu" id="lang-switch-menu">
    {{- range hugo.Sites }}
    {{- $lang := .Language.Name -}}
    {{- $code := .Language.Locale | default $lang -}}
    {{- $href := .Home.RelPermalink -}}
    {{- range $page.AllTranslations }}{{ if eq .Language.Name $lang }}{{ $href = .RelPermalink }}{{ end }}{{ end }}
    <li><a href="{{ $href }}" lang="{{ $code }}" hreflang="{{ $code }}"{{ if eq $lang site.Language.Name }} aria-current="true"{{ end }}>{{ .Language.Label | default (upper $lang) }}</a></li>
    {{- end }}
  </ul>
</div>
{{- end -}}
```

`layouts/_partials/header.html`:
```html
{{- $logo := partial "func/logo.html" . -}}
<header class="site-header" data-header>
  <div class="wrap site-header__inner">
    <a class="site-logo" href="{{ site.Home.RelPermalink }}" rel="home" style="max-width: {{ $logo.width }}px">
      <img src="{{ $logo.src }}" alt="{{ site.Params.logoAlt | default site.Title }}" width="{{ $logo.width }}"{{ with $logo.height }} height="{{ . }}"{{ end }}>
    </a>
    <div class="site-nav" id="site-nav" data-site-nav>
      {{- with site.Menus.main }}
      <nav class="nav-primary" aria-label="{{ T "mainMenu" }}">
        {{ partial "nav-menu.html" (dict "page" $ "entries" .) }}
      </nav>
      {{- end }}
      {{ partial "lang-switch.html" . }}
      {{- with site.Params.joinURL }}
      <a class="btn btn--white btn--join" href="{{ . }}">{{ site.Params.joinLabel | default (T "join") }}</a>
      {{- end }}
    </div>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" data-menu-toggle>
      <span class="menu-toggle__bars" aria-hidden="true"><span></span><span></span><span></span></span>
      <span class="sr-only" data-label-open="{{ T "openMenu" }}" data-label-close="{{ T "closeMenu" }}">{{ T "openMenu" }}</span>
    </button>
  </div>
</header>
```

`layouts/_partials/scripts.html`:
```html
{{- $menu := resources.Get "js/menu.js" | minify | fingerprint -}}
<script src="{{ $menu.RelPermalink }}" integrity="{{ $menu.Data.Integrity }}" defer></script>
```

In `layouts/baseof.html`, replace:
```html
<a class="skip-link" href="#main">{{ T "skipToContent" }}</a>
<main id="main" tabindex="-1">
{{ block "main" . }}{{ end }}
</main>
</body>
```
with:
```html
<a class="skip-link" href="#main">{{ T "skipToContent" }}</a>
{{ partial "header.html" . }}
<main id="main" tabindex="-1">
{{ block "main" . }}{{ end }}
</main>
{{ partial "scripts.html" . }}
</body>
```

- [ ] **Step 5: Create menu.js**

`assets/js/menu.js`:
```js
/* Header behaviour: mobile menu, dropdowns, scrolled state.
   Progressive enhancement only; the page works without it. */
(function () {
  'use strict';

  var body = document.body;
  var OPEN = '[data-submenu-toggle][aria-expanded="true"], [data-dropdown-toggle][aria-expanded="true"]';

  // Mobile menu
  var menuToggle = document.querySelector('[data-menu-toggle]');
  if (menuToggle) {
    var label = menuToggle.querySelector('.sr-only');
    var setMenu = function (open) {
      menuToggle.setAttribute('aria-expanded', String(open));
      body.classList.toggle('menu-open', open);
      if (label) {
        label.textContent = label.getAttribute(open ? 'data-label-close' : 'data-label-open');
      }
    };
    menuToggle.addEventListener('click', function () {
      setMenu(menuToggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && body.classList.contains('menu-open')) {
        setMenu(false);
        menuToggle.focus();
      }
    });
    window.matchMedia('(min-width: 1180px)').addEventListener('change', function (e) {
      if (e.matches) setMenu(false);
    });
  }

  // Sub-menus and the language dropdown
  function closeOthers(keep) {
    document.querySelectorAll(OPEN).forEach(function (btn) {
      if (btn === keep) return;
      if (keep && btn.parentElement.contains(keep)) return; // keep ancestors of a nested toggle open
      btn.setAttribute('aria-expanded', 'false');
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-submenu-toggle], [data-dropdown-toggle]');
    if (btn) {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      closeOthers(btn);
      btn.setAttribute('aria-expanded', String(open));
      return;
    }
    if (!e.target.closest('.menu-item.has-children, [data-dropdown]')) closeOthers(null);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelector(OPEN);
    if (open) {
      closeOthers(null);
      open.focus();
    }
  });

  // Header shadow once the page scrolls
  var header = document.querySelector('[data-header]');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-scrolled', window.scrollY > 10);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
```

- [ ] **Step 6: Create the header and navigation CSS**

`assets/css/header.css`:
```css
/* Fixed navy header (scss/style/_header.scss): logo, main menu, tools, Join. */
.site-header {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 100;
  background: var(--color-header);
  color: #fff;
  transition: box-shadow 0.3s ease;
}

.site-header.is-scrolled {
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.25);
}

.site-header :focus-visible {
  outline-color: var(--color-accent);
}

.site-header__inner {
  display: flex;
  align-items: center;
  height: var(--header-height);
}

.site-logo {
  display: block;
  flex: 0 1 auto;
  order: 1;
  width: 100%;
  line-height: 0;
}

.site-logo img {
  display: block;
  width: 100%;
  height: auto;
}

/* Desktop: the nav wrapper dissolves so its children line up in the header row. */
.site-nav {
  display: contents;
}

.nav-primary {
  order: 2;
  margin: 0 auto 0 40px;
}

.lang-switch {
  order: 3;
  margin-right: 28px;
}

.search-toggle {
  order: 4;
  margin-right: 28px;
}

.btn--join {
  order: 5;
  min-width: 104px;
  padding: 8px 32px 6px;
  font-weight: 600;
}

.search-toggle,
.menu-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: 0;
  background: none;
  color: #fff;
  cursor: pointer;
}

.search-toggle .icon {
  width: 22px;
  height: 22px;
}

.search-toggle:hover,
.search-toggle[aria-expanded="true"] {
  color: var(--color-accent);
}

.menu-toggle {
  display: none;
  order: 6;
}

.menu-toggle__bars {
  position: relative;
  display: block;
  width: 26px;
  height: 18px;
}

.menu-toggle__bars span {
  position: absolute;
  left: 0;
  width: 100%;
  height: 2px;
  border-radius: 2px;
  background: currentColor;
  transition: transform 0.25s ease, opacity 0.2s ease, top 0.25s ease;
}

.menu-toggle__bars span:nth-child(1) { top: 0; }
.menu-toggle__bars span:nth-child(2) { top: 8px; }
.menu-toggle__bars span:nth-child(3) { top: 16px; }

.menu-open .menu-toggle__bars span:nth-child(1) { top: 8px; transform: rotate(45deg); }
.menu-open .menu-toggle__bars span:nth-child(2) { opacity: 0; }
.menu-open .menu-toggle__bars span:nth-child(3) { top: 8px; transform: rotate(-45deg); }

@media (max-width: 1179px) {
  .site-logo {
    max-width: 170px !important;
  }

  .menu-toggle {
    display: inline-flex;
    margin-left: 4px;
  }

  .search-toggle {
    order: 5;
    margin: 0 0 0 auto;
  }

  .site-nav {
    position: fixed;
    top: var(--header-height);
    right: 0;
    bottom: 0;
    left: 0;
    display: none;
    flex-direction: column;
    align-items: flex-start;
    gap: 24px;
    padding: 16px 5% 48px;
    overflow-y: auto;
    background: var(--color-header);
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }

  .menu-open .site-nav {
    display: flex;
  }

  .nav-primary {
    width: 100%;
    margin: 0;
  }

  .lang-switch {
    margin: 0;
  }

  /* Without JavaScript the toggle cannot work: show the menu in the page flow. */
  .no-js body {
    padding-top: 0;
  }

  .no-js .site-header {
    position: static;
  }

  .no-js .site-header__inner {
    flex-wrap: wrap;
    height: auto;
    min-height: var(--header-height);
  }

  .no-js .site-nav {
    position: static;
    display: flex;
    width: 100%;
  }

  .no-js .menu-toggle {
    display: none;
  }
}
```

`assets/css/nav.css`:
```css
/* Main menu, dropdowns and the language switcher (scss/style/_menu.scss). */
.menu {
  margin: 0;
  padding: 0;
  list-style: none;
}

.menu-item {
  position: relative;
  margin: 0;
}

.nav-primary > .menu {
  display: flex;
  align-items: center;
}

.nav-primary > .menu > .menu-item {
  display: flex;
  align-items: center;
  padding: 0 30px;
}

.nav-primary a {
  display: block;
  padding: 8px 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  line-height: 28px;
  text-decoration: none;
}

.nav-primary a:hover,
.nav-primary a:focus-visible,
.nav-primary .is-active > a,
.nav-primary a[aria-current="page"] {
  color: var(--color-accent);
}

.submenu-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 4px;
  padding: 4px;
  border: 0;
  background: none;
  color: #fff;
  cursor: pointer;
}

.submenu-toggle .icon {
  width: 14px;
  height: 14px;
  transition: transform 0.2s ease;
}

.submenu-toggle[aria-expanded="true"] .icon {
  transform: rotate(180deg);
}

.menu--sub {
  position: absolute;
  top: 100%;
  left: 14px;
  z-index: 10;
  display: none;
  min-width: 240px;
  padding: 12px 0;
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-panel);
}

.submenu-toggle[aria-expanded="true"] + .menu--sub {
  display: block;
}

@media (hover: hover) and (min-width: 1180px) {
  .menu-item.has-children:hover > .menu--sub,
  .menu-item.has-children:focus-within > .menu--sub {
    display: block;
  }
}

.nav-primary .menu--sub a {
  padding: 8px 24px;
  color: var(--isoc-navy);
  font-size: 17px;
  font-weight: 400;
}

.nav-primary .menu--sub a:hover,
.nav-primary .menu--sub a:focus-visible,
.nav-primary .menu--sub a[aria-current="page"] {
  background: var(--color-band-light);
  color: var(--color-link);
}

.menu--sub .menu--sub {
  position: static;
  display: block;
  padding: 0 0 0 16px;
  box-shadow: none;
}

/* Language switcher */
.lang-switch {
  position: relative;
}

.lang-switch__toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 4px;
  border: 0;
  background: none;
  color: #fff;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
}

.lang-switch__toggle:hover,
.lang-switch__toggle[aria-expanded="true"] {
  color: var(--color-accent);
}

.lang-switch__toggle .icon--globe {
  width: 18px;
  height: 18px;
}

.lang-switch__toggle .icon--chevron-down {
  width: 14px;
  height: 14px;
}

.lang-switch__menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 10;
  display: none;
  min-width: 160px;
  margin: 8px 0 0;
  padding: 8px 0;
  list-style: none;
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow-panel);
}

.lang-switch__toggle[aria-expanded="true"] + .lang-switch__menu {
  display: block;
}

.lang-switch__menu li {
  margin: 0;
}

.lang-switch__menu a {
  display: block;
  padding: 8px 20px;
  color: var(--isoc-navy);
  text-decoration: none;
}

.lang-switch__menu a[aria-current] {
  font-weight: 600;
}

.lang-switch__menu a:hover,
.lang-switch__menu a:focus-visible {
  background: var(--color-band-light);
  color: var(--color-link);
}

.no-js .lang-switch__toggle {
  display: none;
}

.no-js .lang-switch__menu {
  position: static;
  display: flex;
  gap: 4px;
  margin: 0;
  padding: 0;
  background: none;
  box-shadow: none;
}

.no-js .lang-switch__menu a {
  padding: 4px 8px;
  color: #fff;
}

@media (max-width: 1179px) {
  .nav-primary > .menu {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-primary > .menu > .menu-item {
    flex-wrap: wrap;
    padding: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  }

  .nav-primary > .menu > .menu-item > a {
    flex: 1;
    padding: 14px 0;
    font-size: 20px;
  }

  .submenu-toggle {
    width: 44px;
    height: 44px;
  }

  .menu--sub {
    position: static;
    width: 100%;
    min-width: 0;
    padding: 0 0 12px 16px;
    background: transparent;
    box-shadow: none;
  }

  .nav-primary .menu--sub a {
    padding: 10px 0;
    color: #fff;
    font-size: 18px;
  }

  .nav-primary .menu--sub a:hover,
  .nav-primary .menu--sub a:focus-visible,
  .nav-primary .menu--sub a[aria-current="page"] {
    background: transparent;
    color: var(--color-accent);
  }

  .no-js .menu--sub {
    display: block;
  }

  .lang-switch__menu {
    right: auto;
    left: 0;
  }
}
```

- [ ] **Step 7: Add exampleSite menus and pages**

Append to `exampleSite/hugo.toml`:
```toml

# Header menus (pageRef resolves per language, so each language links to its own pages).
[[languages.en.menus.main]]
  identifier = "about"
  name = "About"
  pageRef = "/about"
  weight = 10
[[languages.en.menus.main]]
  parent = "about"
  name = "Board"
  pageRef = "/about/board"
  weight = 11
[[languages.en.menus.main]]
  parent = "about"
  name = "Statutes"
  pageRef = "/about/statutes"
  weight = 12
[[languages.en.menus.main]]
  name = "News"
  pageRef = "/posts"
  weight = 20
[[languages.en.menus.main]]
  name = "Events"
  pageRef = "/events"
  weight = 30
[[languages.en.menus.main]]
  name = "Membership"
  pageRef = "/membership"
  weight = 40
[[languages.en.menus.main]]
  name = "Contact"
  pageRef = "/contact"
  weight = 50

[[languages.sv.menus.main]]
  identifier = "om"
  name = "Om ISOC-SE"
  pageRef = "/om"
  weight = 10
[[languages.sv.menus.main]]
  parent = "om"
  name = "Styrelse"
  pageRef = "/om/styrelse"
  weight = 11
[[languages.sv.menus.main]]
  parent = "om"
  name = "Stadgar"
  pageRef = "/om/stadgar"
  weight = 12
[[languages.sv.menus.main]]
  name = "Nyheter"
  pageRef = "/nyheter"
  weight = 20
[[languages.sv.menus.main]]
  name = "Evenemang"
  pageRef = "/evenemang"
  weight = 30
[[languages.sv.menus.main]]
  name = "Medlemskap"
  pageRef = "/medlemskap"
  weight = 40
[[languages.sv.menus.main]]
  name = "Kontakt"
  pageRef = "/kontakt"
  weight = 50
```

English pages (paths under `exampleSite/content/en/`):

`about/_index.md` (completed in Task 5):
```markdown
---
title: About us
translationKey: about
---
```

`about/board/index.md` (completed in Task 5):
```markdown
---
title: Board
translationKey: board
---
```

`about/statutes.md`:
```markdown
---
title: Statutes
translationKey: statutes
lead: The statutes adopted at the annual general meeting govern how the chapter works.
---
## § 1 Name

The name of the association is Internet Society Chapter (in this demo).

## § 2 Purpose

The chapter works to ensure that the Internet continues to develop as an open platform for economic and social development for people everywhere.

## § 3 Membership

Membership is open to anyone who supports the purpose of the chapter and is a member of the Internet Society.
```

`posts/_index.md`:
```markdown
---
title: News
translationKey: news
lead: News and statements from the chapter.
---
```

`events/_index.md`:
```markdown
---
title: Events
translationKey: events
lead: Meetings, talks and conferences organised by the chapter and our friends.
---
```

`membership.md`:
```markdown
---
title: Membership
translationKey: membership
banner: teal
lead: Join a global community working for an open, secure and trustworthy Internet.
---
Membership of the chapter is free. As a member of the chapter you are also a member of the Internet Society, which has more than 100,000 members around the world.

## How to join

1. Create a free account with the Internet Society.
2. Choose this chapter when you register.
3. You will receive a welcome email with information about upcoming events.

## Organisational membership

Organisations that share our goals are welcome to join as organisational members. Contact the board to learn more.
```

`contact.md`:
```markdown
---
title: Contact
translationKey: contact
lead: Get in touch with the board.
---
The easiest way to reach us is by email: [board@example.org](mailto:board@example.org).

**Postal address**\
Internet Society Chapter\
Box 3025\
211 65 Malmö\
Sweden
```

`shortcodes/index.md` (a page bundle, English only on purpose; completed in Task 8):
```markdown
---
title: Shortcodes
lead: Every shortcode the theme provides, in one place.
---
This page exists only in English, so the language switcher sends Swedish readers to the Swedish homepage.
```

Swedish pages (paths under `exampleSite/content/sv/`):

`om/_index.md` (completed in Task 5):
```markdown
---
title: Om ISOC-SE
translationKey: about
---
```

`om/styrelse/index.md` (completed in Task 5):
```markdown
---
title: Styrelse
translationKey: board
---
```

`om/stadgar.md`:
```markdown
---
title: Stadgar
translationKey: statutes
lead: Stadgarna antas av årsstämman och styr hur föreningen arbetar.
---
## § 1 Namn

Föreningens namn är Internet Society Sverige (i denna demo).

## § 2 Ändamål

Föreningen arbetar för att internet ska fortsätta utvecklas som en öppen plattform för ekonomisk och social utveckling för människor på alla håll i världen.

## § 3 Medlemskap

Medlemskap är öppet för alla som stöder föreningens ändamål och är medlemmar i Internet Society.
```

`nyheter/_index.md`:
```markdown
---
title: Nyheter
translationKey: news
type: posts
cascade:
  type: posts
lead: Nyheter och uttalanden från föreningen.
---
```

`evenemang/_index.md`:
```markdown
---
title: Evenemang
translationKey: events
type: events
cascade:
  type: events
lead: Möten, föredrag och konferenser som föreningen och våra vänner arrangerar.
---
```

`medlemskap.md`:
```markdown
---
title: Medlemskap
translationKey: membership
banner: teal
lead: Bli en del av en global gemenskap som arbetar för ett öppet, säkert och pålitligt internet.
---
Medlemskap i föreningen är gratis. Som medlem i föreningen är du också medlem i Internet Society, som har över 100 000 medlemmar över hela världen.

## Så blir du medlem

1. Skapa ett kostnadsfritt konto hos Internet Society.
2. Välj den svenska föreningen när du registrerar dig.
3. Du får ett välkomstmejl med information om kommande evenemang.

## Organisationsmedlemskap

Organisationer som delar våra mål är välkomna som organisationsmedlemmar. Kontakta styrelsen för mer information.
```

`kontakt.md`:
```markdown
---
title: Kontakt
translationKey: contact
lead: Kontakta styrelsen.
---
Enklast når du oss via e-post: [styrelsen@example.org](mailto:styrelsen@example.org).

**Postadress**\
Internet Society Sverige\
Box 3025\
211 65 Malmö
```

- [ ] **Step 8: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: all `core_*`, `head_*` and `header_*` checks PASS.

Then open the site to eyeball the header: `scripts/serve.sh`, visit http://localhost:1313/ at desktop width and below 1180px, toggle the hamburger and the About dropdown, then stop the server.

---

### Task 4: Footer

**Files:**
- Create: `assets/images/social/{facebook,instagram,linkedin,rss,x,youtube,mastodon,bluesky,github,email}.svg`
- Create: `layouts/_partials/footer.html`, `layouts/_partials/social-links.html`, `layouts/_partials/func/copyright.html`
- Create: `assets/css/footer.css`
- Modify: `layouts/baseof.html` (include footer)
- Modify: `exampleSite/hugo.toml` (footer menus, social links, footer text)
- Create: `exampleSite/content/en/privacy.md`, `exampleSite/content/sv/integritetspolicy.md`
- Test: `scripts/checks/footer.py`

**Interfaces:**
- Consumes: `partial "icon.html"` with `"set" "social"` (Task 3); `T "footerMenu"`.
- Produces: site params `social` (list of `{name, url, label}`), `footerText` (Markdown), `footerLogo` (assets path), `footerLogoAlt`, `copyright` (`{year}`, `{chapterName}` placeholders), `chapterName` (defaults to site title). `partial "func/copyright.html" PAGE` → HTML.

- [ ] **Step 1: Write the failing footer checks**

`scripts/checks/footer.py`:
```python
import datetime

from checklib import check, expect


@check
def footer_menu_per_language(ctx):
    cases = {"/": ["About", "Contact", "Privacy policy"], "/sv/": ["Om ISOC-SE", "Kontakt", "Integritetspolicy"]}
    for rel, names in cases.items():
        nav = ctx.main.html(rel).find("footer.site-footer nav.footer-nav")
        expect(nav is not None and nav.attrs.get("aria-label"), f"{rel}: footer nav missing or unlabeled")
        got = [a.text() for a in nav.select("a")]
        expect(got == names, f"{rel}: footer menu {got}")


@check
def footer_social_links(ctx):
    links = ctx.main.html("/").select("footer.site-footer ul.social-links a")
    expect(len(links) == 3, f"expected 3 social links, got {len(links)}")
    labels = [a.find(".sr-only").text() for a in links]
    expect(labels == ["LinkedIn", "Mastodon", "RSS"], f"social labels {labels}")
    for a in links:
        expect(a.find("svg.icon") is not None, f"social link {a.attrs['href']} has no icon")
    expect(links[2].attrs["href"] == "/posts/index.xml", f"rss link {links[2].attrs['href']}")


@check
def footer_copyright_and_text(ctx):
    year = datetime.date.today().year
    text = ctx.main.html("/").find("footer.site-footer .site-footer__copyright").text()
    expect(text == f"© {year} Internet Society Chapter", f"copyright {text!r}")
    sv = ctx.main.html("/sv/").find(".site-footer__copyright").text()
    expect(sv == f"© {year} Internet Society Sverige", f"sv copyright {sv!r}")
    blurb = ctx.main.html("/").find(".site-footer__text")
    expect(blurb is not None and blurb.find("a") is not None, "footerText (Markdown with a link) not rendered")


@check
def footer_edge_minimal(ctx):
    footer = ctx.edge.html("/").find("footer.site-footer")
    expect(footer is not None, "edge footer missing")
    expect(footer.find("nav") is None, "edge has no footer menu: <nav> must be omitted")
    expect(footer.find("ul.social-links") is None, "edge has no social links: list must be omitted")
    expect(footer.find(".site-footer__copyright").text().endswith("Edge Chapter"), "edge copyright")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh footer`
Expected: FAIL. Every `footer_*` check fails (`footer nav missing`).

- [ ] **Step 3: Add the social icons**

Convert the WP theme's white icons to `currentColor` and fetch three CC0 icons from Simple Icons:
```bash
mkdir -p assets/images/social
for n in facebook instagram linkedin rss youtube; do
  sed -e 's/<?xml[^>]*?>//' -e 's/ width="1792" height="1792"//' -e 's/fill="#fff"/fill="currentColor"/g' \
    "genesis-child-chapters-main/config/import/images/social/white/$n.svg" | tr -d '\n' > "assets/images/social/$n.svg"
done
sed -e 's/fill="#fff"/fill="currentColor"/g' genesis-child-chapters-main/config/import/images/social/white/X.svg \
  | tr -d '\n' > assets/images/social/x.svg
for n in mastodon bluesky github; do
  curl -fsSL "https://cdn.jsdelivr.net/npm/simple-icons@13/icons/$n.svg" \
    | sed -e 's/ role="img"//' -e 's/<title>[^<]*<\/title>//' -e 's/<svg /<svg fill="currentColor" /' > "assets/images/social/$n.svg"
done
grep -L 'currentColor' assets/images/social/*.svg; head -c 60 assets/images/social/facebook.svg; echo
```
Expected: `grep -L` prints nothing (every file uses `currentColor`); `facebook.svg` starts with `<svg viewBox="0 0 1792 1792"`.

`assets/images/social/email.svg`:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="m3 6 9 7 9-7"/></svg>
```

- [ ] **Step 4: Create the footer partials and CSS**

`layouts/_partials/func/copyright.html`:
```html
{{- $name := site.Params.chapterName | default site.Title -}}
{{- $text := site.Params.copyright | default "© {year} {chapterName}" -}}
{{- $text = replace $text "{year}" (string now.Year) -}}
{{- $text = replace $text "{chapterName}" $name -}}
{{- return ($text | markdownify) -}}
```

`layouts/_partials/social-links.html`:
```html
{{- with site.Params.social -}}
<ul class="social-links">
  {{- range . }}
  <li><a href="{{ .url }}" rel="me noopener">{{ partial "icon.html" (dict "name" .name "set" "social") }}<span class="sr-only">{{ .label | default (title .name) }}</span></a></li>
  {{- end }}
</ul>
{{- end -}}
```

`layouts/_partials/footer.html`:
```html
<footer class="site-footer">
  <div class="wrap site-footer__inner">
    {{- with site.Menus.footer }}
    <nav class="footer-nav" aria-label="{{ T "footerMenu" }}">
      <ul class="footer-menu">
        {{- range . }}
        <li><a href="{{ .URL }}"{{ if $.IsMenuCurrent .Menu . }} aria-current="page"{{ end }}>{{ .Name }}</a></li>
        {{- end }}
      </ul>
    </nav>
    {{- end }}
    {{ partial "social-links.html" . }}
    {{- with site.Params.footerText }}
    <div class="site-footer__text">{{ $.RenderString . }}</div>
    {{- end }}
    {{- with site.Params.footerLogo }}
    {{- with resources.Get (strings.TrimPrefix "/" .) }}
    <div class="site-footer__logo"><img src="{{ .RelPermalink }}" alt="{{ site.Params.footerLogoAlt | default "" }}" width="180"></div>
    {{- end }}
    {{- end }}
    <p class="site-footer__copyright">{{ partial "func/copyright.html" . }}</p>
  </div>
</footer>
```

In `layouts/baseof.html`, replace:
```html
</main>
{{ partial "scripts.html" . }}
```
with:
```html
</main>
{{ partial "footer.html" . }}
{{ partial "scripts.html" . }}
```

`assets/css/footer.css`:
```css
/* Footer (scss/style/_footer.scss): navy band, centred menu, social icons, copyright. */
.site-footer {
  padding: 50px 0 30px;
  background: var(--color-footer);
  color: #fff;
  text-align: center;
}

.site-footer a {
  color: #fff;
  text-decoration: none;
}

.site-footer a:hover,
.site-footer a:focus-visible,
.site-footer a[aria-current="page"] {
  color: var(--color-accent);
}

.site-footer :focus-visible {
  outline-color: var(--color-accent);
}

.footer-menu {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin: 0 0 20px;
  padding: 0;
  list-style: none;
}

.footer-menu li {
  margin: 0;
}

.footer-menu a {
  display: inline-block;
  padding: 10px 25px;
  font-size: 18px;
}

.social-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px;
  margin: 0 0 24px;
  padding: 0;
  list-style: none;
}

.social-links li {
  margin: 0;
}

.social-links a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
}

.social-links .icon {
  width: 28px;
  height: 28px;
}

.site-footer__text {
  max-width: 700px;
  margin: 0 auto 24px;
  font-size: 16px;
  line-height: 1.6;
}

.site-footer__text a {
  text-decoration: underline;
}

.site-footer__logo {
  margin: 0 auto 30px;
}

.site-footer__logo img {
  display: inline-block;
  width: 180px;
}

.site-footer__copyright {
  margin: 0;
  font-size: 16px;
}

@media (max-width: 767px) {
  .footer-menu {
    flex-direction: column;
  }
}
```

- [ ] **Step 5: Configure the exampleSite footer and add the privacy pages**

In `exampleSite/hugo.toml`, add to the existing `[languages.en.params]` table (below `description`):
```toml
      footerText = "Demo site for the [ISOC Chapters Hugo theme](https://github.com/ISOC-SE/isoc-hugo-theme). The Internet Society chapter template, without WordPress."
```
and to `[languages.sv.params]`:
```toml
      footerText = "Demosajt för [Hugo-temat ISOC Chapters](https://github.com/ISOC-SE/isoc-hugo-theme): Internet Societys chaptermall, utan WordPress."
```

Append to `exampleSite/hugo.toml`:
```toml

[[languages.en.menus.footer]]
  name = "About"
  pageRef = "/about"
  weight = 10
[[languages.en.menus.footer]]
  name = "Contact"
  pageRef = "/contact"
  weight = 20
[[languages.en.menus.footer]]
  name = "Privacy policy"
  pageRef = "/privacy"
  weight = 30

[[languages.sv.menus.footer]]
  name = "Om ISOC-SE"
  pageRef = "/om"
  weight = 10
[[languages.sv.menus.footer]]
  name = "Kontakt"
  pageRef = "/kontakt"
  weight = 20
[[languages.sv.menus.footer]]
  name = "Integritetspolicy"
  pageRef = "/integritetspolicy"
  weight = 30

[[params.social]]
  name = "linkedin"
  url = "https://www.linkedin.com/company/internet-society/"
  label = "LinkedIn"
[[params.social]]
  name = "mastodon"
  url = "https://mastodon.social/@internetsociety"
  label = "Mastodon"
[[params.social]]
  name = "rss"
  url = "/posts/index.xml"
  label = "RSS"
```

`[[params.social]]` must come after the existing `[params]` table (`pagerSize = 4`), because TOML attaches it to the most recently opened `params` table. Appending at the end of the file guarantees that.

`exampleSite/content/en/privacy.md`:
```markdown
---
title: Privacy policy
translationKey: privacy
lead: How this website handles personal data.
---
This website does not use cookies, analytics or any third-party services. Fonts and scripts are served from this website itself.

When you email us, we use your address only to answer you. We keep member records according to our statutes and delete them when a membership ends.
```

`exampleSite/content/sv/integritetspolicy.md`:
```markdown
---
title: Integritetspolicy
translationKey: privacy
lead: Så hanterar webbplatsen personuppgifter.
---
Den här webbplatsen använder inga kakor, ingen analys och inga tredjepartstjänster. Typsnitt och skript levereras från webbplatsen själv.

När du mejlar oss använder vi din adress enbart för att svara dig. Vi för medlemsregister enligt stadgarna och raderar uppgifterna när medlemskapet upphör.
```

- [ ] **Step 6: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: all `core_*`, `head_*`, `header_*`, `footer_*` checks PASS.

Note: the RSS social link `/posts/index.xml` is root-relative and does not get a language prefix; it is the same feed on Swedish pages. That is intended for the demo.

---

### Task 5: Banners, pages, images, links and cards

**Files:**
- Create: `assets/images/patterns/green-header.jpg`, `blue-header.jpg`, `green-hero.jpg` (copied from the WP theme)
- Create: `layouts/_partials/banner.html`, `func/banner-image.html`, `img.html`, `func/url.html`, `button.html`, `card.html`, `page-content.html`
- Overwrite: `layouts/single.html`, `layouts/list.html`; create `layouts/404.html`
- Create: `layouts/_markup/render-image.html`, `layouts/_markup/render-link.html`
- Create: `assets/css/hero.css`, `assets/css/content.css`, `assets/css/cards.css`
- Overwrite exampleSite pages: `content/en/about/_index.md`, `content/en/about/board/index.md`, `content/sv/om/_index.md`, `content/sv/om/styrelse/index.md`; add `board.jpg` / `styrelse.jpg` to those bundles
- Create edge pages: `tests/edge/content/about.md`, `plain.md`, `odd.md`; modify `tests/edge/hugo.toml`
- Test: `scripts/checks/pages.py`

**Interfaces:**
- Consumes: `func/resource.html` (Task 2), `icon.html` (Task 3), `T` keys `notFoundTitle`, `notFoundText`, `backHome`, `tableOfContents`.
- Produces:
  - `partial "banner.html" (dict "page" PAGE ["title" STR] ["lead" STR] ["variant" STR] ["above" HTML] ["below" HTML] ["image" SRC])` renders `header.banner.banner--<variant>` (or `header.page-header` for `none`) with `h1.banner__title`, optional `.banner__above`, `p.banner__lead`, and the `below` HTML. Unknown variants warn `"<url>: unknown banner \"x\"; using \"blue\" …"` and fall back to blue.
  - `partial "func/banner-image.html" (dict "page" "variant" "src" ["hero" true])` → resource or `""`.
  - `partial "img.html" (dict "page" PAGE "src" SRC | "res" RESOURCE ["alt"] ["sizes"] ["class"] ["title"] ["eager" bool] ["fill" "WxH"])` → `<img>` with `srcset` (480/800/1200/1600 widths smaller than the original, plus the original), `width`/`height`, `loading`. Remote URLs and root-relative paths (`/…`, static files) render as plain `<img>`. Missing relative paths warn `Image "x" not found (referenced from …)`.
  - `partial "func/url.html" (dict "url" STR)` → content paths (`/about`) become the current language's permalink; others pass through (`relURL` for unknown root-relative paths).
  - `partial "button.html" (dict "label" "url" ["style" "primary"|"secondary"|"white"])` → `a.btn`.
  - `partial "card.html" PAGE` → `article.card` (thumbnail when `image` is a raster image; date and category labels for `posts`).
  - `partial "page-content.html" PAGE` → optional `nav.toc` (when `toc: true`) + `div.entry-content`.

- [ ] **Step 1: Write the failing page checks**

`scripts/checks/pages.py`:
```python
import os
import re

from checklib import check, expect


def _bg_url(el):
    m = re.search(r"url\('?([^')]+)'?\)", el.attrs.get("style", ""))
    return m.group(1) if m else None


@check
def pages_banner_variants(ctx):
    about = ctx.main.html("/about/").find("header.banner")
    expect(about is not None and "banner--green" in about.classes, "about should use the green banner")
    expect(about.find("h1.banner__title").text() == "About us", "about banner title")
    expect(about.find("p.banner__lead") is not None, "about banner lead missing")
    url = _bg_url(about)
    expect(url and url.endswith(".jpg"), f"green banner should have a pattern image, got {url}")
    expect(os.path.isfile(ctx.main.resolve(url, "about/index.html")), f"banner image {url} not published")
    contact = ctx.main.html("/contact/").find("header.banner")
    expect("banner--blue" in contact.classes, "pages without banner: use params.defaultBanner (blue)")
    membership = ctx.main.html("/membership/").find("header.banner")
    expect("banner--teal" in membership.classes and _bg_url(membership) is None, "teal banner is CSS-only")
    expect(len(ctx.main.html("/about/").select("h1")) == 1, "exactly one h1 per page")


@check
def pages_content_image_is_responsive(ctx):
    img = ctx.main.html("/about/board/").find(".entry-content img")
    expect(img is not None, "board image missing")
    expect(img.attrs.get("alt") == "The board at the annual general meeting", f"alt {img.attrs.get('alt')!r}")
    srcset = [p.strip().split()[0] for p in img.attrs.get("srcset", "").split(",") if p.strip()]
    expect(len(srcset) >= 2, f"expected srcset with >= 2 candidates, got {srcset}")
    expect(img.attrs.get("width") and img.attrs.get("height"), "content image needs width and height")
    expect(img.attrs.get("loading") == "lazy", "content images should lazy-load")


@check
def pages_links_resolve_per_language(ctx):
    en = {a.text(): a.attrs for a in ctx.main.html("/about/").select(".entry-content a")}
    expect(en["contact us"]["href"] == "/contact/", f"contact link {en['contact us']}")
    expect(en["statutes"]["href"] == "/about/statutes/", f"statutes link {en['statutes']}")
    expect(en["Internet Society"].get("rel") == "noopener", "external links get rel=noopener")
    sv = {a.text(): a.attrs for a in ctx.main.html("/sv/om/").select(".entry-content a")}
    expect(sv["kontakta oss"]["href"] == "/sv/kontakt/", f"sv contact link {sv['kontakta oss']}")


@check
def pages_table_of_contents(ctx):
    toc = ctx.main.html("/about/").find("nav.toc")
    expect(toc is not None and toc.attrs.get("aria-label") == "Contents", "toc missing or unlabeled")
    expect(len(toc.select("a")) == 3, f"toc should list 3 headings, got {len(toc.select('a'))}")
    expect(toc.find("nav") is None, "toc must not contain a nested <nav>")


@check
def pages_section_lists_children(ctx):
    links = [a.attrs["href"] for a in ctx.main.html("/about/").select(".card .card__title a")]
    expect(links == ["/about/board/", "/about/statutes/"], f"child page cards {links}")


@check
def pages_not_found(ctx):
    for rel, title, home in (("404.html", "Page not found", "/"), ("sv/404.html", "Sidan hittades inte", "/sv/")):
        root = ctx.main.html(rel)
        expect(root.find(".banner__title").text() == title, f"{rel}: title {root.find('.banner__title').text()!r}")
        btn = root.find(".entry-content a.btn")
        expect(btn is not None and btn.attrs["href"] == home, f"{rel}: home button")


@check
def pages_edge_banner_fallbacks(ctx):
    plain = ctx.edge.html("/plain/")
    expect(plain.find("header.page-header h1") is not None and plain.find(".banner") is None,
           "banner: none should render a plain page header")
    odd = ctx.edge.html("/odd/").find("header.banner")
    expect(odd is not None and "banner--blue" in odd.classes, "unknown banner should fall back to blue")
    expect('odd/: unknown banner "purple"' in ctx.edge.log, "edge log should name the page with banner: purple")
    default = ctx.edge.html("/about/").find("header.banner")
    expect("banner--green" in default.classes, "params.defaultBanner should apply to pages without banner")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh pages`
Expected: FAIL. Every `pages_*` check fails (`about should use the green banner`, `missing output file: plain/index.html`, …).

- [ ] **Step 3: Copy the pattern images**

```bash
mkdir -p assets/images/patterns
cp genesis-child-chapters-main/config/import/images/about/Green-pattern-header.jpg assets/images/patterns/green-header.jpg
cp genesis-child-chapters-main/images/blue-pattern-header.jpg assets/images/patterns/blue-header.jpg
cp genesis-child-chapters-main/config/import/images/home/Header-Pattern-Green-1.jpg assets/images/patterns/green-hero.jpg
ls -la assets/images/patterns
```
Expected: three JPEGs (about 34 KB, 37 KB, 59 KB).

- [ ] **Step 4: Create the shared partials**

`layouts/_partials/func/url.html`:
```html
{{- /* Resolve a link from front matter or config. Content paths such as "/about"
       become the current language's permalink; anything else passes through. */ -}}
{{- $u := .url | default "" -}}
{{- if and (hasPrefix $u "/") (not (hasPrefix $u "//")) -}}
  {{- $path := strings.TrimSuffix "/" $u | default "/" -}}
  {{- with site.GetPage $path -}}
    {{- $u = .RelPermalink -}}
  {{- else -}}
    {{- $u = $u | relURL -}}
  {{- end -}}
{{- end -}}
{{- return $u -}}
```

`layouts/_partials/button.html`:
```html
{{- /* Context: dict "label" "url" ["style" "primary"|"secondary"|"white"]. */ -}}
<a class="btn{{ with .style }}{{ if ne . "primary" }} btn--{{ . }}{{ end }}{{ end }}" href="{{ partial "func/url.html" (dict "url" .url) }}">{{ .label }}</a>
{{- /**/ -}}
```

`layouts/_partials/img.html`:
```html
{{- /* Responsive image.
       Context: dict "page" PAGE, "src" STRING or "res" RESOURCE,
       optional "alt" "sizes" "class" "title" "eager" (bool) "fill" ("600x600"). */ -}}
{{- $res := .res -}}
{{- $src := .src | default "" -}}
{{- if and (not $res) $src -}}
  {{- $res = partial "func/resource.html" (dict "page" .page "src" $src) -}}
{{- end -}}
{{- $alt := .alt | default "" -}}
{{- $loading := "lazy" -}}
{{- if .eager }}{{ $loading = "eager" }}{{ end -}}
{{- $class := .class | default "" -}}
{{- $title := .title | default "" -}}
{{- if $res -}}
  {{- $raster := in (slice "jpeg" "png" "webp") $res.MediaType.SubType -}}
  {{- if and $raster .fill -}}
    {{- $res = $res.Fill (printf "%s Center" .fill) -}}
  {{- end -}}
  {{- if $raster -}}
    {{- $set := slice -}}
    {{- range slice 480 800 1200 1600 -}}
      {{- if lt . $res.Width -}}
        {{- $set = $set | append (printf "%s %dw" ($res.Resize (printf "%dx" .)).RelPermalink .) -}}
      {{- end -}}
    {{- end -}}
    {{- $set = $set | append (printf "%s %dw" $res.RelPermalink $res.Width) -}}
    {{- $fallback := $res -}}
    {{- if gt $res.Width 1200 }}{{ $fallback = $res.Resize "1200x" }}{{ end -}}
<img src="{{ $fallback.RelPermalink }}" srcset="{{ delimit $set ", " }}" sizes="{{ .sizes | default "100vw" }}" width="{{ $fallback.Width }}" height="{{ $fallback.Height }}" alt="{{ $alt }}" loading="{{ $loading }}" decoding="async"{{ with $class }} class="{{ . }}"{{ end }}{{ with $title }} title="{{ . }}"{{ end }}>
  {{- else -}}
<img src="{{ $res.RelPermalink }}" alt="{{ $alt }}" loading="{{ $loading }}" decoding="async"{{ with $class }} class="{{ . }}"{{ end }}{{ with $title }} title="{{ . }}"{{ end }}>
  {{- end -}}
{{- else if $src -}}
  {{- if or (urls.Parse $src).IsAbs (hasPrefix $src "/") -}}
    {{- $url := $src -}}
    {{- if not (urls.Parse $src).IsAbs }}{{ $url = $src | relURL }}{{ end -}}
<img src="{{ $url }}" alt="{{ $alt }}" loading="{{ $loading }}" decoding="async"{{ with $class }} class="{{ . }}"{{ end }}{{ with $title }} title="{{ . }}"{{ end }}>
  {{- else -}}
    {{- $from := "site configuration" -}}
    {{- with .page }}{{ $from = .RelPermalink }}{{ end -}}
    {{- warnf "Image %q not found (referenced from %s)" $src $from -}}
  {{- end -}}
{{- end -}}
```

`layouts/_partials/func/banner-image.html`:
```html
{{- /* Background image for a banner or hero.
       Context: dict "page" PAGE "variant" STRING "src" STRING ["hero" bool].
       Returns a resource, or "" for CSS-only variants (navy, teal). */ -}}
{{- $res := "" -}}
{{- with .src -}}
  {{- $res = partial "func/resource.html" (dict "page" $.page "src" .) -}}
  {{- if not $res }}{{ warnf "%s: banner image %q not found" $.page.RelPermalink . }}{{ end -}}
{{- else -}}
  {{- $patterns := dict "green" "images/patterns/green-header.jpg" "blue" "images/patterns/blue-header.jpg" -}}
  {{- if .hero }}{{ $patterns = merge $patterns (dict "green" "images/patterns/green-hero.jpg") }}{{ end -}}
  {{- with index $patterns .variant }}{{ $res = resources.Get . }}{{ end -}}
{{- end -}}
{{- if and $res (in (slice "jpeg" "png" "webp") $res.MediaType.SubType) (gt $res.Width 2400) -}}
  {{- $res = $res.Resize "2400x" -}}
{{- end -}}
{{- return $res -}}
```

`layouts/_partials/banner.html`:
```html
{{- /* Page banner (WP .inner-page-header). See the Interfaces list in the plan for the context keys. */ -}}
{{- $p := .page -}}
{{- $variant := .variant | default $p.Params.banner | default site.Params.defaultBanner | default "blue" -}}
{{- if not (in (slice "green" "blue" "navy" "teal" "none") $variant) -}}
  {{- warnf "%s: unknown banner %q; using \"blue\" (valid: green, blue, navy, teal, none)" $p.RelPermalink $variant -}}
  {{- $variant = "blue" -}}
{{- end -}}
{{- $title := .title | default $p.Title -}}
{{- $lead := .lead | default $p.Params.lead -}}
{{- if eq $variant "none" }}
<header class="page-header">
  <div class="wrap wrap--1180">
{{- else }}
{{- $img := partial "func/banner-image.html" (dict "page" $p "variant" $variant "src" (.image | default $p.Params.banner_image)) }}
<header class="banner banner--{{ $variant }}"{{ with $img }} style="{{ printf "background-image:url('%s')" .RelPermalink | safeCSS }}"{{ end }}>
  <div class="wrap wrap--1180 banner__inner">
{{- end }}
    {{- with .above }}
    <div class="banner__above">{{ . }}</div>
    {{- end }}
    <h1 class="banner__title">{{ $title }}</h1>
    {{- with $lead }}
    <p class="banner__lead">{{ . | markdownify }}</p>
    {{- end }}
    {{- with .below }}
    {{ . }}
    {{- end }}
  </div>
</header>
```

`layouts/_partials/page-content.html`:
```html
{{- if .Params.toc }}
<nav class="toc" aria-label="{{ T "tableOfContents" }}">{{ .TableOfContents | replaceRE `</?nav[^>]*>` "" | safeHTML }}</nav>
{{- end }}
<div class="entry-content">{{ .Content }}</div>
```

`layouts/_partials/card.html`:
```html
{{- /* Card for a post or page (WP .latest-blog-post). Context: PAGE. */ -}}
{{- $isPost := eq .Type "posts" -}}
{{- $summary := .Params.lead | default .Summary | plainify | htmlUnescape | strings.TrimSpace -}}
<article class="card">
  {{- with .Params.image }}
  {{- with partial "func/resource.html" (dict "page" $ "src" .) }}
  {{- if in (slice "jpeg" "png" "webp") .MediaType.SubType }}
  <div class="card__image">{{ partial "img.html" (dict "res" (.Fill "640x360 Center") "sizes" "(min-width: 1180px) 300px, (min-width: 600px) 45vw, 90vw") }}</div>
  {{- end }}
  {{- end }}
  {{- end }}
  <div class="card__body">
    {{- if $isPost }}
    <p class="card__date"><time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date | time.Format site.Params.dateFormat }}</time></p>
    {{- end }}
    <h3 class="card__title"><a href="{{ .RelPermalink }}">{{ .LinkTitle }}</a></h3>
    {{- with $summary }}
    <p class="card__summary">{{ . | truncate 140 }}</p>
    {{- end }}
    {{- if $isPost }}
    {{- with .GetTerms "categories" }}
    <ul class="card__tags">{{ range . }}<li>{{ .LinkTitle }}</li>{{ end }}</ul>
    {{- end }}
    {{- end }}
  </div>
</article>
```

- [ ] **Step 5: Create the page layouts and render hooks**

Overwrite `layouts/single.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="wrap wrap--1180 section">
  {{ partial "page-content.html" . }}
</div>
{{ end }}
```

Overwrite `layouts/list.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="wrap wrap--1180 section">
  {{- if .Content }}
  <div class="list-intro">{{ partial "page-content.html" . }}</div>
  {{- end }}
  {{- with .Pages }}
  <div class="card-grid">
    {{- range . }}{{ partial "card.html" . }}{{ end }}
  </div>
  {{- end }}
</div>
{{ end }}
```

`layouts/404.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" . "title" (T "notFoundTitle") "variant" "blue" "above" "404") }}
<div class="wrap wrap--1180 section">
  <div class="entry-content">
    <p>{{ T "notFoundText" }}</p>
    <p><a class="btn" href="{{ site.Home.RelPermalink }}">{{ T "backHome" }}</a></p>
  </div>
</div>
{{ end }}
```

`layouts/_markup/render-image.html`:
```html
{{- partial "img.html" (dict "page" .PageInner "src" .Destination "alt" .PlainText "title" .Title "sizes" "(min-width: 1180px) 1180px, 90vw" "class" "content-image") -}}
```

`layouts/_markup/render-link.html`:
```html
{{- /* Content paths ("/about", "board") resolve to the current language's page;
       external http(s) links get rel="noopener". */ -}}
{{- $u := urls.Parse .Destination -}}
{{- $href := .Destination -}}
{{- if and (not $u.IsAbs) $u.Path -}}
  {{- with or (.PageInner.GetPage $u.Path) (.PageInner.Resources.Get $u.Path) -}}
    {{- $href = .RelPermalink -}}
    {{- with $u.RawQuery }}{{ $href = printf "%s?%s" $href . }}{{ end -}}
    {{- with $u.Fragment }}{{ $href = printf "%s#%s" $href . }}{{ end -}}
  {{- end -}}
{{- end -}}
<a href="{{ $href }}"{{ with .Title }} title="{{ . }}"{{ end }}{{ if and $u.IsAbs (in (slice "http" "https") $u.Scheme) }} rel="noopener"{{ end }}>{{ .Text }}</a>
{{- /**/ -}}
```

- [ ] **Step 6: Create the banner, content and card CSS**

`assets/css/hero.css`:
```css
/* Page banners and the homepage hero (WP .inner-page-header, .wp-block-cover, .header-no-video). */
:root {
  /* Translucent rounded-bar motif for the CSS-only navy/teal banners. */
  --pattern-light: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1440' height='400' viewBox='0 0 1440 400'%3E%3Cg fill='%23fff' fill-opacity='.06'%3E%3Crect x='-120' y='150' width='760' height='120' rx='30' transform='rotate(24 260 210)'/%3E%3Crect x='520' y='-120' width='150' height='560' rx='30' transform='rotate(24 595 160)'/%3E%3Crect x='860' y='40' width='700' height='140' rx='30' transform='rotate(24 1210 110)'/%3E%3Crect x='1180' y='160' width='130' height='420' rx='30' transform='rotate(24 1245 370)'/%3E%3C/g%3E%3C/svg%3E");
}

.banner {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 300px;
  padding: 64px 0;
  overflow: hidden;
  background-color: var(--isoc-blue-bg);
  background-position: center;
  background-size: cover;
  color: #fff;
}

.banner__inner {
  position: relative;
  z-index: 1;
}

.banner__title {
  margin: 0;
  color: inherit;
  font-size: 52px;
  font-weight: 700;
  line-height: 1.1;
}

.banner__lead {
  max-width: 800px;
  margin: 24px 0 0;
  font-size: 25px;
  line-height: 32px;
}

.banner__above {
  margin-bottom: 20px;
  font-size: 18px;
}

.banner__meta {
  margin: 24px 0 0;
  font-size: 16px;
  line-height: 24px;
}

.banner a {
  color: inherit;
}

.banner a:hover,
.banner a:focus-visible {
  color: inherit;
  text-decoration: none;
}

.banner--blue :focus-visible,
.banner--navy :focus-visible,
.banner--teal :focus-visible {
  outline-color: #fff;
}

/* Light green pattern under a white overlay (WP .white-overlay), dark blue text. */
.banner--green {
  background-color: var(--isoc-neutral-green);
  color: var(--isoc-depth-blue);
}

.banner--green::after {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.45);
}

.banner--navy {
  background-color: var(--isoc-navy);
  background-image: var(--pattern-light);
}

.banner--teal {
  background-color: var(--isoc-depth-teal);
  background-image: var(--pattern-light);
}

/* banner: none */
.page-header {
  padding-top: var(--section-space);
  color: var(--color-heading);
}

.page-header + .section {
  padding-top: 30px;
}

/* Homepage hero */
.hero {
  min-height: 500px;
  padding: 80px 0;
}

.hero__title {
  margin: 0;
  color: inherit;
  font-size: 56px;
  font-weight: 700;
  line-height: 1.1;
}

.hero__tagline {
  max-width: 590px;
  margin: 30px 0 0;
  font-size: 25px;
  line-height: 1.4;
}

.hero .btn-row {
  margin-top: 36px;
}

@media (max-width: 1023px) {
  .banner__title { font-size: 46px; }
  .hero__title { font-size: 48px; }
}

@media (max-width: 767px) {
  .banner {
    min-height: 200px;
    padding: 44px 0;
  }

  .banner__title { font-size: 36px; }
  .banner__lead { font-size: 21px; line-height: 1.4; }

  .hero {
    min-height: 380px;
    padding: 56px 0;
  }

  .hero__title { font-size: 40px; }
  .hero__tagline { font-size: 21px; }
}
```

`assets/css/content.css`:
```css
/* Long-form Markdown content. */
.entry-content > :first-child {
  margin-top: 0;
}

.entry-content h2 { margin-top: 50px; }
.entry-content h3,
.entry-content h4 { margin-top: 40px; }

.entry-content h2:first-child,
.entry-content h3:first-child,
.entry-content h4:first-child {
  margin-top: 0;
}

.entry-content ul { list-style: disc; }
.entry-content ol { list-style: decimal; }

.entry-content li > ul,
.entry-content li > ol {
  margin: 0.25em 0 0;
}

.entry-content blockquote {
  margin: 40px 0;
  padding: 4px 0 4px 30px;
  border-left: 4px solid var(--color-accent);
  color: var(--isoc-depth-blue);
  font-size: 22px;
  line-height: 1.5;
}

.entry-content img {
  display: block;
  height: auto;
}

.entry-content code {
  padding: 0.1em 0.35em;
  border-radius: 3px;
  background: var(--isoc-light-gray);
  font-size: 0.9em;
}

.entry-content pre {
  margin: 0 0 30px;
  padding: 20px;
  overflow-x: auto;
  border-radius: var(--radius);
  background: var(--isoc-navy);
  color: #fff;
  font-size: 15px;
  line-height: 1.6;
}

.entry-content pre code {
  padding: 0;
  background: none;
  font-size: inherit;
}

.toc {
  margin: 0 0 40px;
  padding: 24px 30px;
  border-left: 4px solid var(--color-accent);
  background: var(--color-band-light);
}

.toc ul {
  margin: 0;
  padding-left: 1.2em;
  list-style: none;
}

.toc > ul {
  padding-left: 0;
}

.toc li {
  margin: 0.2em 0;
}

.toc a {
  text-decoration: none;
}

.list-intro {
  margin-bottom: 40px;
}

/* Large blue lead text (the template's intro heading: 36px, #2b72d6, weight 400). */
.lead {
  color: var(--isoc-blue);
  font-size: 36px;
  line-height: 1.53;
}

.lead p {
  margin-bottom: 20px;
}

.lead p:last-child {
  margin-bottom: 0;
}

.featured-image {
  margin: 0 0 40px;
}

.featured-image img {
  display: block;
  width: 100%;
}

.image-credit {
  margin-top: 12px;
  color: var(--isoc-gray);
  font-size: 14px;
  line-height: 1.4;
}

@media (max-width: 767px) {
  .lead {
    font-size: 26px;
    line-height: 1.45;
  }

  .entry-content table {
    display: block;
    overflow-x: auto;
  }
}
```

`assets/css/cards.css`:
```css
/* Cards for posts and pages (WP .latest-blog-post, .rel-posts-box). */
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px 20px;
}

.card-grid--4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 285px;
  background: #fff;
  color: var(--isoc-navy);
  box-shadow: var(--shadow-card);
  transition: box-shadow 0.3s ease;
}

.card:hover,
.card:focus-within {
  box-shadow: var(--shadow-card-hover);
}

.card__image {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--color-band-green);
}

.card__image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.card:hover .card__image img {
  transform: scale(1.03);
}

.card__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 25px 22px;
}

.card__date {
  margin: 0 0 12px;
  font-size: 16px;
  line-height: 1.4;
}

.card__title {
  margin: 0 0 16px;
  font-size: 25px;
  font-weight: 400;
  line-height: 32px;
}

.card__title a {
  color: var(--color-link);
  text-decoration: none;
}

/* The whole card is clickable through the title link. */
.card__title a::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
}

.card__title a:hover,
.card__title a:focus-visible {
  color: var(--isoc-navy);
}

.card__summary {
  margin: 0 0 16px;
  font-size: 17px;
  line-height: 1.5;
}

.card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: auto 0 0;
  padding: 0;
  list-style: none;
}

.card__tags li {
  margin: 0;
  padding: 6px 12px 4px;
  border-radius: var(--radius-pill);
  background: var(--color-band-light);
  color: var(--isoc-depth-blue);
  font-size: 14px;
  line-height: 1;
}

@media (max-width: 1023px) {
  .card-grid,
  .card-grid--4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 599px) {
  .card-grid,
  .card-grid--4 {
    grid-template-columns: minmax(0, 1fr);
  }

  .card {
    min-height: 0;
  }
}
```

- [ ] **Step 7: Fill in the exampleSite About pages and add the edge pages**

Copy the board photos (demo images from the WP theme):
```bash
cp genesis-child-chapters-main/config/import/images/home/gallery-image.jpg exampleSite/content/en/about/board/board.jpg
cp genesis-child-chapters-main/config/import/images/home/gallery-image.jpg exampleSite/content/sv/om/styrelse/styrelse.jpg
```

Overwrite `exampleSite/content/en/about/_index.md`:
```markdown
---
title: About us
translationKey: about
banner: green
lead: We are the local chapter of the Internet Society, a global non-profit working for an Internet that is open, globally connected, secure and trustworthy.
toc: true
---
## What we do

We bring together people who care about the Internet: engineers, researchers, students, policymakers and everyday users. We organise talks and conferences, respond to public consultations, and help people get online safely.

## How we work

The chapter is run by volunteers. An elected board handles day-to-day work between the annual general meetings. Read our [statutes](/about/statutes) or [contact us](/contact) if you want to get involved.

## The Internet Society

The [Internet Society](https://www.internetsociety.org/) was founded in 1992 by Internet pioneers. Today it has more than 120 chapters around the world.
```

Overwrite `exampleSite/content/en/about/board/index.md`:
```markdown
---
title: Board
translationKey: board
lead: The board is elected by the annual general meeting for one year at a time.
---
![The board at the annual general meeting](board.jpg "The board, 2026")

| Role | Name |
|---|---|
| Chair | Alex Example |
| Treasurer | Kim Example |
| Secretary | Sam Example |
| Member | Robin Example |
```

Overwrite `exampleSite/content/sv/om/_index.md`:
```markdown
---
title: Om ISOC-SE
translationKey: about
banner: green
lead: Vi är den svenska föreningen inom Internet Society, en global ideell organisation som arbetar för ett internet som är öppet, globalt sammankopplat, säkert och pålitligt.
toc: true
---
## Vad vi gör

Vi samlar människor som bryr sig om internet: ingenjörer, forskare, studenter, beslutsfattare och vanliga användare. Vi arrangerar föredrag och konferenser, svarar på remisser och hjälper människor att använda internet säkert.

## Hur vi arbetar

Föreningen drivs av ideella krafter. En vald styrelse sköter det löpande arbetet mellan årsstämmorna. Läs våra [stadgar](/om/stadgar) eller [kontakta oss](/kontakt) om du vill engagera dig.

## Internet Society

[Internet Society](https://www.internetsociety.org/) grundades 1992 av internets pionjärer. I dag finns över 120 chapters runt om i världen.
```

Overwrite `exampleSite/content/sv/om/styrelse/index.md`:
```markdown
---
title: Styrelse
translationKey: board
lead: Styrelsen väljs av årsstämman för ett år i taget.
---
![Styrelsen på årsstämman](styrelse.jpg "Styrelsen 2026")

| Roll | Namn |
|---|---|
| Ordförande | Alex Exempel |
| Kassör | Kim Exempel |
| Sekreterare | Sam Exempel |
| Ledamot | Robin Exempel |
```

In `tests/edge/hugo.toml`, replace:
```toml
[params]
  [params.colors]
```
with:
```toml
[params]
  defaultBanner = "green"
  [params.colors]
```

`tests/edge/content/about.md`:
```markdown
---
title: About
---
A page without a banner setting uses params.defaultBanner.
```

`tests/edge/content/plain.md`:
```markdown
---
title: Plain page
banner: none
---
A page with banner: none.
```

`tests/edge/content/odd.md`:
```markdown
---
title: Odd banner
banner: purple
---
An invalid banner value must warn and fall back to blue.
```

- [ ] **Step 8: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: every check so far PASSES, including all `pages_*`.

---

### Task 6: News: posts, lists, categories, archive

**Files:**
- Create: `layouts/posts/single.html`, `layouts/posts/list.html`, `layouts/taxonomy.html`, `layouts/term.html`, `layouts/archive.html`
- Create: `layouts/_partials/post-meta.html`, `post-categories.html`, `featured-image.html`, `related-posts.html`, `category-nav.html`, `pagination.html`
- Create: `assets/css/news.css`
- Create exampleSite posts (6 en + 6 sv), `content/en/archive.md`, `content/sv/arkiv.md`
- Create: `tests/edge/content/posts/plain-post.md`
- Test: `scripts/checks/posts.py`

**Interfaces:**
- Consumes: `banner.html`, `card.html`, `img.html`, `page-content.html` (Task 5); `T` keys `by`, `imageCopyright`, `relatedPosts`, `categories`, `noPosts`, `pagination`, `pageN`, `newerPosts`, `olderPosts`.
- Produces:
  - Post front matter: `title`, `date`, `categories`, `tags`, `authors` (list), `image` (page resource or assets path), `image_alt`, `image_credit`, `summary`, `lead`, `banner`.
  - `partial "pagination.html" PAGER` → `nav.pagination` (only when more than one page).
  - `partial "category-nav.html" PAGE` → `nav > ul.category-nav` listing all categories with counts, marking the current term.
  - CSS classes `.cards-band`, `.block__title`, `.band__title`, `.archive__*`, `.term-list` (reused by Task 8).

- [ ] **Step 1: Write the failing news checks**

`scripts/checks/posts.py`:
```python
from checklib import check, expect


def _card_titles(root):
    return [a.text() for a in root.select(".card-grid .card .card__title a")]


@check
def posts_list_paginates(ctx):
    root = ctx.main.html("/posts/")
    titles = _card_titles(root)
    expect(titles == ["Annual general meeting 2026", "Call for nominations to the board",
                      "New postal address", "Save the date: national Internet governance forum"],
           f"page 1 cards {titles}")
    nav = root.find("nav.pagination")
    expect(nav is not None and nav.find("a[href=/posts/page/2/]") is not None, "pagination link to page 2 missing")
    expect(nav.find("span[aria-current=page]").text() == "1", "current page marker")
    page2 = _card_titles(ctx.main.html("/posts/page/2/"))
    expect(page2 == ["Why end-to-end encryption matters", "Our response to the EU consultation on data retention"],
           f"page 2 cards {page2}")
    sv = ctx.main.html("/sv/nyheter/")
    expect(len(_card_titles(sv)) == 4 and sv.find("a[href=/sv/nyheter/page/2/]") is not None, "sv news pagination")


@check
def posts_cards_have_date_thumbnail_and_tags(ctx):
    cards = ctx.main.html("/posts/").select(".card-grid .card")
    first = cards[0]
    expect(first.find("time").attrs.get("datetime") == "2026-02-11", "card date datetime")
    expect(first.find("time").text() == "11 February 2026", f"card date text {first.find('time').text()!r}")
    expect(first.find(".card__image img") is not None, "post with an image should have a thumbnail")
    expect(cards[1].find(".card__image") is None, "post without an image must not render a thumbnail")
    expect([li.text() for li in first.select(".card__tags li")] == ["Community"], "card category labels")
    sv_time = ctx.main.html("/sv/nyheter/").find(".card time").text()
    expect(sv_time == "11 februari 2026", f"sv card date {sv_time!r}")


@check
def posts_category_nav(ctx):
    items = [a.text() for a in ctx.main.html("/posts/").select("ul.category-nav a")]
    expect(items == ["Community (3)", "Internet governance (2)", "Privacy (2)"], f"category nav {items}")
    term = ctx.main.html("/categories/community/")
    current = term.find("ul.category-nav a[aria-current=page]")
    expect(current is not None and current.text() == "Community (3)", "current category not marked")
    expect(len(_card_titles(term)) == 3, f"community term should list 3 posts, got {_card_titles(term)}")
    expect(len(ctx.main.html("/categories/").select(".term-list a")) == 3, "taxonomy page should list 3 terms")


@check
def posts_single_banner_meta_and_image(ctx):
    root = ctx.main.html("/posts/annual-general-meeting-2026/")
    banner = root.find("header.banner")
    expect("banner--blue" in banner.classes, "posts use the blue banner by default")
    expect([a.text() for a in banner.select(".banner__above a")] == ["Community"], "categories above the title")
    expect(banner.find("h1").text() == "Annual general meeting 2026", "post title")
    meta = banner.find(".banner__meta")
    expect(meta.find("time").text() == "11 February 2026", f"post date {meta.find('time').text()!r}")
    expect("by The Board" in meta.text(), f"authors line {meta.text()!r}")
    fig = root.find("figure.featured-image")
    expect(fig is not None and fig.find("img[srcset]") is not None, "featured image missing")
    expect(fig.find("img").attrs.get("loading") == "eager", "featured image should load eagerly")
    expect(fig.find("figcaption").text() == "Image copyright: ISOC Chapter, CC BY 4.0", "image credit caption")
    sv = ctx.main.html("/sv/nyheter/kallelse-arsstamma-2026/")
    expect(sv.find(".banner__meta time").text() == "11 februari 2026", "sv post date")
    expect(sv.find("figcaption").text() == "Bild: ISOC-SE, CC BY 4.0", "sv image credit")


@check
def posts_related(ctx):
    rel = ctx.main.html("/posts/annual-general-meeting-2026/").find("section.related")
    expect(rel is not None and rel.find("h2").text() == "Related posts", "related posts section missing")
    hrefs = [a.attrs["href"] for a in rel.select(".card__title a")]
    expect(len(hrefs) == 4, f"expected 4 related posts, got {hrefs}")
    expect("/posts/annual-general-meeting-2026/" not in hrefs, "a post must not be related to itself")
    expect(all(h.startswith("/posts/") for h in hrefs), f"related posts must be posts: {hrefs}")


@check
def posts_archive(ctx):
    root = ctx.main.html("/archive/")
    years = [h.text() for h in root.select(".archive__year h2")]
    expect(years == ["2026", "2025"], f"archive years {years}")
    months = [h.text() for h in root.select(".archive__year")[0].select(".archive__month")]
    expect(months == ["February", "January"], f"2026 months {months}")
    expect(len(root.select(".archive__list li")) == 6, "archive should list all 6 posts")
    sv_months = [h.text() for h in ctx.main.html("/sv/arkiv/").select(".archive__month")][:2]
    expect(sv_months == ["Februari", "Januari"], f"sv months {sv_months}")


@check
def posts_rss(ctx):
    rss = ctx.main.read("posts/index.xml")
    expect(rss.count("<item>") == 6, "news RSS should contain 6 items")


@check
def posts_edge_minimal_post(ctx):
    card = ctx.edge.html("/posts/").find(".card")
    expect(card is not None, "edge posts list missing")
    expect(card.find(".card__image") is None and card.find(".card__tags") is None, "no empty thumbnail/tags")
    post = ctx.edge.html("/posts/plain-post/")
    expect(post.find(".banner__above") is None and post.find("figure") is None, "no empty categories/figure")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh posts`
Expected: FAIL. Every `posts_*` check fails (no posts yet: `missing output file: posts/annual-general-meeting-2026/index.html`; the list shows no cards).

- [ ] **Step 3: Create the news partials**

`layouts/_partials/post-categories.html`:
```html
{{- with .GetTerms "categories" -}}
{{- range $i, $t := . }}{{ if $i }} | {{ end }}<a href="{{ $t.RelPermalink }}">{{ $t.LinkTitle }}</a>{{ end -}}
{{- end -}}
```

`layouts/_partials/post-meta.html`:
```html
<p class="banner__meta post-meta">
  <time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date | time.Format site.Params.dateFormat }}</time>
  {{- with .Params.authors }}<br><span class="post-meta__authors">{{ T "by" }} {{ delimit . ", " }}</span>{{ end }}
</p>
```

`layouts/_partials/featured-image.html`:
```html
{{- with .Params.image -}}
<figure class="featured-image">
  {{ partial "img.html" (dict "page" $ "src" . "alt" ($.Params.image_alt | default "") "sizes" "(min-width: 1180px) 1180px, 90vw" "eager" true) }}
  {{- with $.Params.image_credit }}
  <figcaption class="image-credit">{{ T "imageCopyright" (dict "Credit" .) }}</figcaption>
  {{- end }}
</figure>
{{- end -}}
```

`layouts/_partials/related-posts.html`:
```html
{{- /* Up to four related posts; topped up with the newest other posts. */ -}}
{{- $posts := where site.RegularPages "Type" "posts" -}}
{{- $related := where (site.RegularPages.Related .) "Type" "posts" -}}
{{- $others := complement (slice .) $related $posts -}}
{{- $list := first 4 ($related | append $others) -}}
{{- with $list -}}
<section class="related band band--light" aria-labelledby="related-title">
  <div class="wrap wrap--1180">
    <h2 class="band__title" id="related-title">{{ T "relatedPosts" }}</h2>
    <div class="card-grid card-grid--4">
      {{- range . }}{{ partial "card.html" . }}{{ end }}
    </div>
  </div>
</section>
{{- end -}}
```

`layouts/_partials/category-nav.html`:
```html
{{- $current := . -}}
{{- with site.Taxonomies.categories -}}
<nav aria-label="{{ T "categories" }}">
  <ul class="category-nav">
    {{- range .Alphabetical }}
    <li><a href="{{ .Page.RelPermalink }}"{{ if eq .Page $current }} aria-current="page"{{ end }}>{{ .Page.LinkTitle }} ({{ .Count }})</a></li>
    {{- end }}
  </ul>
</nav>
{{- end -}}
```

`layouts/_partials/pagination.html`:
```html
{{- $pag := . -}}
{{- if gt $pag.TotalPages 1 -}}
<nav class="pagination" aria-label="{{ T "pagination" }}">
  {{- with $pag.Prev }}
  <a class="pagination__prev" href="{{ .URL }}" rel="prev">{{ T "newerPosts" }}</a>
  {{- end }}
  <ul class="pagination__pages">
    {{- range $pag.Pagers }}
    <li>
      {{- if eq .PageNumber $pag.PageNumber }}
      <span aria-current="page">{{ .PageNumber }}</span>
      {{- else }}
      <a href="{{ .URL }}" aria-label="{{ T "pageN" (dict "Number" .PageNumber) }}">{{ .PageNumber }}</a>
      {{- end }}
    </li>
    {{- end }}
  </ul>
  {{- with $pag.Next }}
  <a class="pagination__next" href="{{ .URL }}" rel="next">{{ T "olderPosts" }}</a>
  {{- end }}
</nav>
{{- end -}}
```

- [ ] **Step 4: Create the news layouts**

`layouts/posts/single.html`:
```html
{{ define "main" }}
{{- $above := partial "post-categories.html" . -}}
{{- $below := partial "post-meta.html" . -}}
{{ partial "banner.html" (dict "page" . "above" $above "below" $below) }}
<article class="wrap wrap--1180 section post">
  {{ partial "featured-image.html" . }}
  {{ partial "page-content.html" . }}
</article>
{{ partial "related-posts.html" . }}
{{ end }}
```

`layouts/posts/list.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="cards-band section">
  <div class="wrap wrap--1180">
    {{- if .Content }}
    <div class="list-intro">{{ partial "page-content.html" . }}</div>
    {{- end }}
    {{ partial "category-nav.html" . }}
    {{- $pag := .Paginate (where .RegularPagesRecursive "Type" "posts") (site.Params.pagerSize | default 9) }}
    {{- with $pag.Pages }}
    <div class="card-grid">
      {{- range . }}{{ partial "card.html" . }}{{ end }}
    </div>
    {{- else }}
    <p>{{ T "noPosts" }}</p>
    {{- end }}
    {{ partial "pagination.html" $pag }}
  </div>
</div>
{{ end }}
```

`layouts/term.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="cards-band section">
  <div class="wrap wrap--1180">
    {{- if eq .Data.Plural "categories" }}{{ partial "category-nav.html" . }}{{ end }}
    {{- $pag := .Paginate .Pages (site.Params.pagerSize | default 9) }}
    <div class="card-grid">
      {{- range $pag.Pages }}
      {{- if eq .Type "events" }}{{ partial "card-event.html" . }}{{ else }}{{ partial "card.html" . }}{{ end }}
      {{- end }}
    </div>
    {{ partial "pagination.html" $pag }}
  </div>
</div>
{{ end }}
```

`term.html` refers to `card-event.html`, which Task 7 creates. Create a temporary version now so `term.html` never refers to a missing partial; Task 7 overwrites it.

`layouts/_partials/card-event.html` (temporary, replaced in Task 7):
```html
{{ partial "card.html" . }}
```

`layouts/taxonomy.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="wrap wrap--1180 section">
  <ul class="term-list">
    {{- range .Data.Terms.Alphabetical }}
    <li><a href="{{ .Page.RelPermalink }}">{{ .Page.LinkTitle }}</a> ({{ .Count }})</li>
    {{- end }}
  </ul>
</div>
{{ end }}
```

`layouts/archive.html` (used by pages with `layout: archive`):
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="wrap wrap--960 section archive">
  {{- if .Content }}
  <div class="list-intro">{{ partial "page-content.html" . }}</div>
  {{- end }}
  {{- $posts := where site.RegularPages "Type" "posts" }}
  {{- range $posts.GroupByDate "2006" }}
  <section class="archive__year">
    <h2>{{ .Key }}</h2>
    {{- range .Pages.GroupByDate "2006-01" }}
    <h3 class="archive__month">{{ (index .Pages 0).Date | time.Format "January" | strings.FirstUpper }}</h3>
    <ul class="archive__list">
      {{- range .Pages }}
      <li><time datetime="{{ .Date.Format "2006-01-02" }}">{{ .Date | time.Format ":date_medium" }}</time> <a href="{{ .RelPermalink }}">{{ .LinkTitle }}</a></li>
      {{- end }}
    </ul>
    {{- end }}
  </section>
  {{- end }}
</div>
{{ end }}
```

`assets/css/news.css`:
```css
/* News lists, category filter, pagination, related posts, archive. */
.cards-band {
  background: var(--color-band-light);
}

.block__title,
.band__title {
  margin: 0 0 30px;
  color: var(--isoc-blue);
  font-size: 36px;
  line-height: 1.53;
}

.band--navy .block__title,
.band--blue .block__title {
  color: #fff;
}

.category-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 0 0 40px;
  padding: 0;
  list-style: none;
}

.category-nav li {
  margin: 0;
}

.category-nav a {
  display: inline-block;
  padding: 8px 20px 6px;
  border: 1.5px solid var(--color-link);
  border-radius: var(--radius-pill);
  background: #fff;
  font-size: 16px;
  text-decoration: none;
}

.category-nav a:hover,
.category-nav a:focus-visible,
.category-nav a[aria-current="page"] {
  background: var(--color-link);
  color: #fff;
}

.pagination {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 50px;
}

.pagination__pages {
  display: flex;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.pagination__pages li {
  margin: 0;
}

.pagination a,
.pagination span[aria-current] {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
  padding: 2px 16px 0;
  border: 1.5px solid var(--color-button);
  border-radius: var(--radius-pill);
  background: #fff;
  color: var(--color-button);
  text-decoration: none;
}

.pagination span[aria-current],
.pagination a:hover,
.pagination a:focus-visible {
  background: var(--color-button);
  color: #fff;
}

.term-list {
  margin: 0;
  padding: 0;
  list-style: none;
  columns: 2 260px;
}

.term-list li {
  margin: 0 0 8px;
}

.archive__year + .archive__year {
  margin-top: 50px;
}

.archive__month {
  margin: 30px 0 12px;
  color: var(--color-heading);
  font-size: 22px;
  font-weight: 600;
}

.archive__list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.archive__list li {
  display: flex;
  gap: 16px;
  margin: 0;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}

.archive__list time {
  flex: 0 0 130px;
  color: var(--isoc-gray);
  font-size: 16px;
}

@media (max-width: 599px) {
  .archive__list li {
    flex-direction: column;
    gap: 2px;
  }

  .archive__list time {
    flex-basis: auto;
  }
}
```

- [ ] **Step 5: Add the exampleSite posts and archive pages**

Copy the featured images:
```bash
mkdir -p exampleSite/content/en/posts/annual-general-meeting-2026 exampleSite/content/sv/nyheter/kallelse-arsstamma-2026
cp genesis-child-chapters-main/config/import/images/projects/Green-pattern-blog-page.jpg exampleSite/content/en/posts/annual-general-meeting-2026/cover.jpg
cp genesis-child-chapters-main/config/import/images/projects/Green-pattern-blog-page.jpg exampleSite/content/sv/nyheter/kallelse-arsstamma-2026/cover.jpg
```

English posts (`exampleSite/content/en/posts/`):

`annual-general-meeting-2026/index.md`:
```markdown
---
title: Annual general meeting 2026
date: 2026-02-11T10:00:00+01:00
translationKey: post-agm-2026
categories: [Community]
tags: [meetings]
authors: [The Board]
image: cover.jpg
image_alt: ""
image_credit: ISOC Chapter, CC BY 4.0
summary: Members are invited to the annual general meeting on 25 March, online.
---
Members are invited to the annual general meeting of the chapter.

**When:** Wednesday 25 March 2026, 18:00–20:30\
**Where:** Online. A link is sent the day before to the email address you registered with.

## Agenda

1. Opening of the meeting
2. Annual report and accounts
3. Election of the board
4. Any other business

Before the formal meeting we host a short talk about vulnerabilities that stay undiscovered for years.
```

`call-for-board-nominations.md`:
```markdown
---
title: Call for nominations to the board
date: 2026-01-20T09:00:00+01:00
translationKey: post-nominations-2026
categories: [Community]
tags: [meetings, board]
summary: The nomination committee is looking for candidates for the 2026 board.
---
The nomination committee is now accepting nominations for the board that will be elected at the annual general meeting. Any member can nominate themselves or someone else.

Send your nomination, with a few lines about the candidate, to the nomination committee before 1 March.
```

`new-postal-address.md`:
```markdown
---
title: New postal address
date: 2025-12-08T09:00:00+01:00
translationKey: post-postal-address
categories: [Community]
summary: The chapter has a new postal address in Malmö.
---
We have a new postal address. From now on you can reach us at:

Internet Society Chapter\
Box 3025\
211 65 Malmö
```

`internet-governance-forum.md`:
```markdown
---
title: "Save the date: national Internet governance forum"
date: 2025-11-03T09:00:00+01:00
translationKey: post-igf-2026
categories: [Internet governance]
tags: [conferences]
summary: A full day about technology, the Internet, privacy and decentralisation.
---
The national Internet governance forum returns in January. It is a full-day meeting about technology, the Internet, privacy and decentralisation, for everyone who wants to help shape our digital future.

More details will follow in the events calendar.
```

`why-encryption-matters.md`:
```markdown
---
title: Why end-to-end encryption matters
date: 2025-09-15T09:00:00+02:00
translationKey: post-encryption
categories: [Privacy]
tags: [encryption]
authors: [The Board]
summary: End-to-end encryption protects everyone. Weakening it for some weakens it for all.
---
End-to-end encryption means that only the people communicating can read their messages. It protects journalists, businesses, governments and ordinary users alike.

Proposals to give third parties access to encrypted messages would create weaknesses that criminals and hostile states could also exploit.
```

`eu-data-retention-response.md`:
```markdown
---
title: Our response to the EU consultation on data retention
date: 2025-06-16T09:00:00+02:00
translationKey: post-data-retention
categories: [Privacy, Internet governance]
tags: [encryption]
authors: [The Board]
summary: We told the European Commission that end-to-end encryption must never be broken.
---
The European Commission invited us to comment on its call for evidence about metadata retention for criminal proceedings. We thank the Commission for the opportunity and summarise our position here.

We want to be very clear: end-to-end encryption must never be broken. The security consequences of weakening it would be severe and long-lasting.
```

Swedish posts (`exampleSite/content/sv/nyheter/`):

`kallelse-arsstamma-2026/index.md`:
```markdown
---
title: Kallelse årsstämma 2026
date: 2026-02-11T10:00:00+01:00
translationKey: post-agm-2026
categories: [Föreningen]
tags: [möten]
authors: [Styrelsen]
image: cover.jpg
image_alt: ""
image_credit: ISOC-SE, CC BY 4.0
summary: Medlemmar kallas till årsstämma den 25 mars, online.
---
Medlemmar kallas härmed till föreningens årsstämma.

**Tid:** Onsdag 25 mars 2026, 18.00–20.30\
**Plats:** Online. Länk skickas dagen innan till den e-postadress du registrerade dig med.

## Dagordning

1. Mötets öppnande
2. Verksamhetsberättelse och bokslut
3. Val av styrelse
4. Övriga frågor

Före stämman bjuder vi på ett kort föredrag om sårbarheter som förblir oupptäckta i åratal.
```

`nominera-till-styrelsen.md`:
```markdown
---
title: Nominera till styrelsen
date: 2026-01-20T09:00:00+01:00
translationKey: post-nominations-2026
categories: [Föreningen]
tags: [möten, styrelse]
summary: Valberedningen söker kandidater till styrelsen 2026.
---
Valberedningen tar nu emot nomineringar till den styrelse som väljs på årsstämman. Alla medlemmar kan nominera sig själva eller någon annan.

Skicka din nominering, med några rader om kandidaten, till valberedningen före den 1 mars.
```

`ny-postadress.md`:
```markdown
---
title: Ny postadress
date: 2025-12-08T09:00:00+01:00
translationKey: post-postal-address
categories: [Föreningen]
summary: Föreningen har fått en ny postadress i Malmö.
---
Vi har fått ny postadress. Från och med nu når du oss på:

Internet Society Sverige\
Box 3025\
211 65 Malmö
```

`internetforum.md`:
```markdown
---
title: "Save the date: nationellt internetforum"
date: 2025-11-03T09:00:00+01:00
translationKey: post-igf-2026
categories: [Internetstyrning]
tags: [konferenser]
summary: En heldag om teknik, internet, integritet och decentralisering.
---
Det nationella internetforumet återkommer i januari. Det är en heldag om teknik, internet, integritet och decentralisering för alla som vill vara med och forma digitaliseringens framtid.

Mer information kommer i evenemangskalendern.
```

`darfor-ar-kryptering-viktigt.md`:
```markdown
---
title: Därför är end-to-end-kryptering viktigt
date: 2025-09-15T09:00:00+02:00
translationKey: post-encryption
categories: [Integritet]
tags: [kryptering]
authors: [Styrelsen]
summary: End-to-end-kryptering skyddar alla. Att försvaga den för några försvagar den för alla.
---
End-to-end-kryptering innebär att bara de som kommunicerar kan läsa meddelandena. Den skyddar journalister, företag, myndigheter och vanliga användare.

Förslag om att ge tredje part tillgång till krypterade meddelanden skulle skapa svagheter som även kriminella och fientliga stater kan utnyttja.
```

`yttrande-datalagring.md`:
```markdown
---
title: Vårt yttrande till EU-kommissionen om datalagring och kryptering
date: 2025-06-16T09:00:00+02:00
translationKey: post-data-retention
categories: [Integritet, Internetstyrning]
tags: [kryptering]
authors: [Styrelsen]
summary: Vi har meddelat EU-kommissionen att end-to-end-kryptering aldrig får brytas.
---
EU-kommissionen bjöd in oss att lämna synpunkter på deras underlag om lagring av metadata för brottsutredningar. Vi tackar för möjligheten och sammanfattar här våra ståndpunkter.

Vi vill vara mycket tydliga: end-to-end-kryptering får aldrig brytas. De säkerhetsmässiga konsekvenserna skulle bli allvarliga och långvariga.
```

`exampleSite/content/en/archive.md`:
```markdown
---
title: News archive
translationKey: archive
layout: archive
lead: Every post we have published, by month.
---
```

`exampleSite/content/sv/arkiv.md`:
```markdown
---
title: Nyhetsarkiv
translationKey: archive
layout: archive
lead: Alla inlägg vi har publicerat, månad för månad.
---
```

`tests/edge/content/posts/plain-post.md`:
```markdown
---
title: Plain post
date: 2026-01-01T09:00:00+01:00
---
A post with no image, categories or authors.
```

- [ ] **Step 6: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: every check so far PASSES, including all `posts_*`.

If `posts_related` fails because Hugo's default related config returns nothing, the top-up from `$others` still yields 4 cards, so a failure there means `complement`/`append` misbehaved. Print `{{ len $related }} {{ len $others }}` into the page temporarily to debug, then remove it.

---

### Task 7: Events with upcoming/past lists and .ics files

**Files:**
- Create: `layouts/events/list.html`, `layouts/events/single.html`
- Create: `layouts/_partials/func/event-dates.html`, `func/event-when.html`, `func/events.html`, `func/event-ics.html`, `func/ics-escape.html`
- Overwrite: `layouts/_partials/card-event.html`; create `layouts/_partials/event-details.html`, `layouts/_partials/upcoming-events-grid.html`
- Create: `assets/css/events.css`
- Create exampleSite events (4 en + 4 sv)
- Create edge events: `tests/edge/content/events/{no-offset,all-day,no-end,past}.md`
- Test: `scripts/checks/events.py`

**Interfaces:**
- Consumes: `banner.html`, `featured-image.html`, `page-content.html`, `icon.html` (icons `calendar`, `map-pin`, `video`, `user`); `T` keys `upcomingEvents`, `pastEvents`, `noUpcomingEvents`, `eventDate`, `location`, `online`, `joinOnline`, `organizer`, `register`, `registrationClosed`, `addToCalendar`, `eventPassed`.
- Produces:
  - Event front matter: `start` (**required**; datetime, offset optional; without an offset it is read in the site `timeZone`), `end`, `all_day`, `location`, `online`, `online_url`, `registration_url`, `registration_closed`, `organizer`, plus the post keys `summary`, `image`, `image_alt`, `image_credit`, `banner`. `date` is only the publish date.
  - `partial "func/event-dates.html" PAGE` → `dict "start" TIME "end" TIME "hasEnd" BOOL "past" BOOL "sameDay" BOOL`. Fails the build (`errorf`) when `start` is missing.
  - `partial "func/event-when.html" (dict "page" PAGE "d" DATES)` → human-readable, localised date/time range (string).
  - `partialCached "func/events.html" PAGE site.Language.Name` → `dict "upcoming" (list of dict "page" "ts") "past" (…)`, upcoming ascending, past descending.
  - `partial "func/event-ics.html" PAGE` → published `.ics` resource at `<event URL>event.ics`.
  - `partial "card-event.html" PAGE` → `article.event-card`.
  - `partial "upcoming-events-grid.html" (dict "count" N)` → `div.event-list.event-list--grid` of upcoming event cards, or nothing (used by Task 8).

- [ ] **Step 1: Write the failing event checks**

`scripts/checks/events.py`:
```python
from checklib import check, expect


def _ics(site, rel):
    raw = site.read(rel)
    expect("\n" not in raw.replace("\r\n", ""), f"{rel}: lines must end with CRLF")
    lines = raw.split("\r\n")
    expect(lines[0] == "BEGIN:VCALENDAR" and lines[-2] == "END:VCALENDAR" and lines[-1] == "",
           f"{rel}: not a complete VCALENDAR")
    return lines


def _group_titles(root, group):
    return [a.text() for a in root.select(f".events-group--{group} .event-card__title a")]


@check
def events_list_splits_upcoming_and_past(ctx):
    root = ctx.main.html("/events/")
    expect(_group_titles(root, "upcoming") == ["SamNet 5 conference", "Annual general meeting 2027, online"],
           f"upcoming {_group_titles(root, 'upcoming')}")
    expect(_group_titles(root, "past") == ["Annual general meeting 2026", "SamNet 4 conference"],
           f"past {_group_titles(root, 'past')}")
    first = root.find(".events-group--upcoming .event-card")
    expect(first.find(".event-card__day").text() == "21" and first.find(".event-card__month").text() == "Jan",
           "date badge")
    expect("event-card--past" in root.find(".events-group--past .event-card").classes, "past cards are marked")
    sv = ctx.main.html("/sv/evenemang/")
    expect(len(sv.select(".events-group--upcoming .event-card")) == 2, "sv upcoming events")
    expect(sv.find(".events-group--upcoming h2").text() == "Kommande evenemang", "sv heading")


@check
def events_single_details(ctx):
    root = ctx.main.html("/events/samnet-5/")
    details = root.find(".event__details")
    expect(details is not None, "event details box missing")
    text = details.text()
    expect("21 January 2027, 09:00–17:00" in text, f"date range missing: {text!r}")
    expect("Internetstiftelsen, Hammarby kaj 10D, Stockholm" in text, "location missing")
    register = details.find("a.btn[href=https://example.com/register]")
    expect(register is not None and register.text() == "Register", "register button missing")
    ics = details.find("a[download]")
    expect(ics is not None and ics.attrs["href"] == "/events/samnet-5/event.ics", f"ics link {ics and ics.attrs}")
    expect(root.find(".notice") is None, "upcoming events must not show the past-event notice")


@check
def events_registration_closed_and_online(ctx):
    details = ctx.main.html("/events/agm-2027/").find(".event__details")
    expect("Registration closed" in details.text(), "closed registration not shown")
    expect(details.find("a.btn[href=https://example.com/register]") is None, "no register button when closed")
    online = details.find("a[href=https://meet.example.org/agm-2027]")
    expect(online is not None and online.text() == "Join online", "online link missing")


@check
def events_past_notice(ctx):
    root = ctx.main.html("/events/agm-2026/")
    notice = root.find(".notice")
    expect(notice is not None and notice.text() == "This event has already taken place.", "past notice")
    buttons = [a.text() for a in root.select(".event__details a.btn")]
    expect(buttons == ["Add to calendar"], f"past event should only offer the calendar file, got {buttons}")


@check
def events_ics_content(ctx):
    lines = _ics(ctx.main, "events/samnet-5/event.ics")
    for expected in ("VERSION:2.0", "BEGIN:VEVENT", "END:VEVENT", "DTSTART:20270121T080000Z",
                     "DTEND:20270121T160000Z", "SUMMARY:SamNet 5 conference",
                     "LOCATION:Internetstiftelsen\\, Hammarby kaj 10D\\, Stockholm",
                     "URL:https://example.org/events/samnet-5/"):
        expect(expected in lines, f"samnet-5 ics lacks {expected!r}")
    expect(any(l.startswith("UID:") and l.endswith("@example.org") for l in lines), "UID missing")
    expect(any(l.startswith("DTSTAMP:") and l.endswith("Z") for l in lines), "DTSTAMP missing")
    agm = _ics(ctx.main, "events/agm-2027/event.ics")
    expect("SUMMARY:Annual general meeting 2027\\, online" in agm, "commas in SUMMARY must be escaped")
    expect("LOCATION:Online" in agm and "DTSTART:20270324T170000Z" in agm, "online event location/start")
    expect(ctx.main.exists("sv/evenemang/samnet-5/event.ics"), "sv events need .ics files too")


@check
def events_edge_timezones_and_all_day(ctx):
    no_offset = _ics(ctx.edge, "events/no-offset/event.ics")
    expect("DTSTART:20990501T160000Z" in no_offset and "DTEND:20990501T180000Z" in no_offset,
           "a start without offset must be read in the site timeZone (Europe/Stockholm, CEST)")
    all_day = _ics(ctx.edge, "events/all-day/event.ics")
    expect("DTSTART;VALUE=DATE:20990601" in all_day and "DTEND;VALUE=DATE:20990603" in all_day,
           "all-day events use DATE values with an exclusive end")
    no_end = _ics(ctx.edge, "events/no-end/event.ics")
    expect("DTSTART:20990701T080000Z" in no_end and "DTEND:20990701T090000Z" in no_end,
           "events without end default to one hour")
    link = ctx.edge.html("/events/no-offset/").find("a[download]")
    expect(link.attrs["href"] == "/sub/events/no-offset/event.ics", f"ics link must include base path, got {link.attrs['href']}")
    titles = _group_titles(ctx.edge.html("/events/"), "upcoming")
    expect(titles == ["No offset", "All day", "No end"], f"edge upcoming order {titles}")
    expect(_group_titles(ctx.edge.html("/events/"), "past") == ["Past event"], "edge past events")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh events`
Expected: FAIL. Every `events_*` check fails (`missing output file: events/samnet-5/index.html`, `events-group` not found).

- [ ] **Step 3: Create the event helper partials**

`layouts/_partials/func/event-dates.html`:
```html
{{- /* Parsed dates for an event page. Returns dict start end hasEnd past sameDay. */ -}}
{{- if not .Params.start -}}
  {{- errorf "%s: events need a \"start\" date in front matter (e.g. start: 2027-03-25T18:00:00+01:00)" .File.Path -}}
{{- end -}}
{{- $start := time.AsTime .Params.start -}}
{{- $end := $start -}}
{{- $hasEnd := false -}}
{{- with .Params.end }}{{ $end = time.AsTime . }}{{ $hasEnd = true }}{{ end -}}
{{- $past := $end.Before now -}}
{{- if and .Params.all_day (not $past) -}}
  {{- /* An all-day event is over only after its last day ends. */ -}}
  {{- $past = ($end.AddDate 0 0 1).Before now -}}
{{- end -}}
{{- return dict
    "start" $start
    "end" $end
    "hasEnd" $hasEnd
    "past" $past
    "sameDay" (eq ($start.Format "2006-01-02") ($end.Format "2006-01-02"))
-}}
```

`layouts/_partials/func/event-when.html`:
```html
{{- /* Localised date/time range. Context: dict "page" PAGE "d" (event-dates result). */ -}}
{{- $d := .d -}}
{{- $fmt := site.Params.dateFormat | default ":date_long" -}}
{{- $s := $d.start | time.Format $fmt -}}
{{- if .page.Params.all_day -}}
  {{- if not $d.sameDay }}{{ $s = printf "%s – %s" $s ($d.end | time.Format $fmt) }}{{ end -}}
{{- else -}}
  {{- $s = printf "%s, %s" $s ($d.start | time.Format ":time_short") -}}
  {{- if $d.hasEnd -}}
    {{- if $d.sameDay -}}
      {{- $s = printf "%s–%s" $s ($d.end | time.Format ":time_short") -}}
    {{- else -}}
      {{- $s = printf "%s – %s, %s" $s ($d.end | time.Format $fmt) ($d.end | time.Format ":time_short") -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
{{- return $s -}}
```

`layouts/_partials/func/events.html`:
```html
{{- /* Upcoming (ascending) and past (descending) events for the current language.
       Call with partialCached "func/events.html" . site.Language.Name */ -}}
{{- $up := slice -}}
{{- $past := slice -}}
{{- range where site.RegularPages "Type" "events" -}}
  {{- $d := partial "func/event-dates.html" . -}}
  {{- $entry := dict "page" . "ts" $d.start.Unix -}}
  {{- if $d.past }}{{ $past = $past | append $entry }}{{ else }}{{ $up = $up | append $entry }}{{ end -}}
{{- end -}}
{{- return dict "upcoming" (sort $up "ts" "asc") "past" (sort $past "ts" "desc") -}}
```

`layouts/_partials/func/ics-escape.html`:
```html
{{- /* Escape TEXT values for iCalendar (RFC 5545 §3.3.11). */ -}}
{{- $s := replace . "\\" "\\\\" -}}
{{- $s = replace $s ";" "\\;" -}}
{{- $s = replace $s "," "\\," -}}
{{- $s = replace $s "\r\n" "\\n" -}}
{{- $s = replace $s "\n" "\\n" -}}
{{- return $s -}}
```

`layouts/_partials/func/event-ics.html`:
```html
{{- /* Publish <event URL>event.ics and return the resource. Context: event PAGE. */ -}}
{{- $p := . -}}
{{- $d := partial "func/event-dates.html" $p -}}
{{- $utc := "20060102T150405Z" -}}
{{- $host := (urls.Parse site.BaseURL).Host -}}
{{- $lines := slice "BEGIN:VCALENDAR" "VERSION:2.0" (printf "PRODID:-//%s//ISOC Chapters Hugo theme//%s" site.Title (upper site.Language.Name)) "CALSCALE:GREGORIAN" "METHOD:PUBLISH" "BEGIN:VEVENT" -}}
{{- $lines = $lines | append (printf "UID:%s@%s" (md5 $p.Permalink) $host) -}}
{{- $lines = $lines | append (printf "DTSTAMP:%s" ($p.Lastmod.UTC.Format $utc)) -}}
{{- if $p.Params.all_day -}}
  {{- $lines = $lines | append (printf "DTSTART;VALUE=DATE:%s" ($d.start.Format "20060102")) -}}
  {{- $lines = $lines | append (printf "DTEND;VALUE=DATE:%s" (($d.end.AddDate 0 0 1).Format "20060102")) -}}
{{- else -}}
  {{- $end := $d.end -}}
  {{- if not $d.hasEnd }}{{ $end = $d.start.Add (time.ParseDuration "1h") }}{{ end -}}
  {{- $lines = $lines | append (printf "DTSTART:%s" ($d.start.UTC.Format $utc)) -}}
  {{- $lines = $lines | append (printf "DTEND:%s" ($end.UTC.Format $utc)) -}}
{{- end -}}
{{- $lines = $lines | append (printf "SUMMARY:%s" (partial "func/ics-escape.html" $p.Title)) -}}
{{- with $p.Params.location -}}
  {{- $lines = $lines | append (printf "LOCATION:%s" (partial "func/ics-escape.html" .)) -}}
{{- else -}}
  {{- if $p.Params.online }}{{ $lines = $lines | append (printf "LOCATION:%s" (T "online")) }}{{ end -}}
{{- end -}}
{{- $lines = $lines | append (printf "URL:%s" $p.Permalink) -}}
{{- with $p.Summary | plainify | htmlUnescape | strings.TrimSpace -}}
  {{- $lines = $lines | append (printf "DESCRIPTION:%s" (partial "func/ics-escape.html" (truncate 300 .))) -}}
{{- end -}}
{{- $lines = $lines | append "END:VEVENT" "END:VCALENDAR" -}}
{{- $body := printf "%s\r\n" (delimit $lines "\r\n") -}}
{{- /* FromString paths are relative to the publish root and get the base path added back. */ -}}
{{- $base := (urls.Parse site.BaseURL).Path -}}
{{- $path := printf "%sevent.ics" (strings.TrimPrefix $base $p.RelPermalink) -}}
{{- return resources.FromString $path $body -}}
```

- [ ] **Step 4: Create the event templates**

Overwrite `layouts/_partials/card-event.html`:
```html
{{- $d := partial "func/event-dates.html" . -}}
<article class="event-card{{ if $d.past }} event-card--past{{ end }}">
  <div class="event-card__date" aria-hidden="true">
    <span class="event-card__day">{{ $d.start.Day }}</span>
    <span class="event-card__month">{{ $d.start | time.Format "Jan" }}</span>
  </div>
  <div class="event-card__body">
    <h3 class="event-card__title"><a href="{{ .RelPermalink }}">{{ .LinkTitle }}</a></h3>
    <p class="event-card__meta">{{ partial "icon.html" (dict "name" "calendar") }}<time datetime="{{ $d.start.Format "2006-01-02T15:04:05-07:00" }}">{{ partial "func/event-when.html" (dict "page" . "d" $d) }}</time></p>
    {{- with .Params.location }}
    <p class="event-card__meta">{{ partial "icon.html" (dict "name" "map-pin") }}<span>{{ . }}</span></p>
    {{- end }}
    {{- if .Params.online }}
    <p class="event-card__meta">{{ partial "icon.html" (dict "name" "video") }}<span>{{ T "online" }}</span></p>
    {{- end }}
  </div>
</article>
```

`layouts/_partials/event-details.html`:
```html
{{- /* Details box. Context: dict "page" PAGE "d" (event-dates result). */ -}}
{{- $p := .page -}}
{{- $d := .d -}}
{{- $ics := partial "func/event-ics.html" $p -}}
<dl class="event-details">
  <dt>{{ partial "icon.html" (dict "name" "calendar") }}{{ T "eventDate" }}</dt>
  <dd><time datetime="{{ $d.start.Format "2006-01-02T15:04:05-07:00" }}">{{ partial "func/event-when.html" (dict "page" $p "d" $d) }}</time></dd>
  {{- with $p.Params.location }}
  <dt>{{ partial "icon.html" (dict "name" "map-pin") }}{{ T "location" }}</dt>
  <dd>{{ . }}</dd>
  {{- end }}
  {{- if $p.Params.online }}
  <dt>{{ partial "icon.html" (dict "name" "video") }}{{ T "online" }}</dt>
  <dd>{{ with $p.Params.online_url }}<a href="{{ . }}">{{ T "joinOnline" }}</a>{{ else }}{{ T "online" }}{{ end }}</dd>
  {{- end }}
  {{- with $p.Params.organizer }}
  <dt>{{ partial "icon.html" (dict "name" "user") }}{{ T "organizer" }}</dt>
  <dd>{{ . }}</dd>
  {{- end }}
</dl>
<div class="event-details__actions">
  {{- if not $d.past }}
  {{- if $p.Params.registration_closed }}
  <p class="event-details__closed">{{ T "registrationClosed" }}</p>
  {{- else }}
  {{- with $p.Params.registration_url }}
  <a class="btn" href="{{ . }}">{{ T "register" }}</a>
  {{- end }}
  {{- end }}
  {{- end }}
  <a class="btn btn--secondary" href="{{ $ics.RelPermalink }}" download>{{ T "addToCalendar" }}</a>
</div>
```

`layouts/_partials/upcoming-events-grid.html`:
```html
{{- /* Context: dict "count" N. Renders nothing when there are no upcoming events. */ -}}
{{- $ev := partialCached "func/events.html" site.Home site.Language.Name -}}
{{- with first (int (.count | default 3)) $ev.upcoming -}}
<div class="event-list event-list--grid">
  {{- range . }}{{ partial "card-event.html" .page }}{{ end }}
</div>
{{- end -}}
```

`layouts/events/list.html`:
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
{{- $ev := partialCached "func/events.html" site.Home site.Language.Name }}
<div class="wrap wrap--1180 section">
  {{- if .Content }}
  <div class="list-intro">{{ partial "page-content.html" . }}</div>
  {{- end }}
  <section class="events-group events-group--upcoming" aria-labelledby="events-upcoming">
    <h2 id="events-upcoming">{{ T "upcomingEvents" }}</h2>
    {{- with $ev.upcoming }}
    <div class="event-list">{{ range . }}{{ partial "card-event.html" .page }}{{ end }}</div>
    {{- else }}
    <p class="events-empty">{{ T "noUpcomingEvents" }}</p>
    {{- end }}
  </section>
  {{- with $ev.past }}
  <section class="events-group events-group--past" aria-labelledby="events-past">
    <h2 id="events-past">{{ T "pastEvents" }}</h2>
    <div class="event-list">{{ range . }}{{ partial "card-event.html" .page }}{{ end }}</div>
  </section>
  {{- end }}
</div>
{{ end }}
```

`layouts/events/single.html`:
```html
{{ define "main" }}
{{- $d := partial "func/event-dates.html" . -}}
{{- $below := printf `<p class="banner__meta">%s</p>` (partial "func/event-when.html" (dict "page" . "d" $d) | htmlEscape) | safeHTML -}}
{{ partial "banner.html" (dict "page" . "below" $below) }}
<div class="wrap wrap--1180 section event">
  {{- if $d.past }}
  <p class="notice">{{ T "eventPassed" }}</p>
  {{- end }}
  <div class="event__layout">
    <div class="event__content">
      {{ partial "featured-image.html" . }}
      {{ partial "page-content.html" . }}
    </div>
    <aside class="event__details">{{ partial "event-details.html" (dict "page" . "d" $d) }}</aside>
  </div>
</div>
{{ end }}
```

`assets/css/events.css`:
```css
/* Events: cards with a date badge, upcoming/past groups, details box. */
.events-group + .events-group {
  margin-top: 60px;
}

.event-list {
  display: grid;
  gap: 20px;
}

.event-list--grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.event-card {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 24px;
  padding: 24px;
  background: #fff;
  box-shadow: var(--shadow-card);
  transition: box-shadow 0.3s ease;
}

.event-card:hover,
.event-card:focus-within {
  box-shadow: var(--shadow-card-hover);
}

.event-card__date {
  display: flex;
  flex: 0 0 76px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 84px;
  border-radius: var(--radius);
  background: var(--isoc-depth-blue);
  color: #fff;
  line-height: 1;
  text-align: center;
}

.event-card--past .event-card__date {
  background: var(--isoc-gray);
}

.event-card__day {
  font-size: 36px;
  font-weight: 700;
}

.event-card__month {
  margin-top: 6px;
  font-size: 15px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.event-card__body {
  min-width: 0;
}

.event-card__title {
  margin: 0 0 8px;
  font-size: 25px;
  line-height: 32px;
}

.event-card__title a {
  color: var(--color-link);
  text-decoration: none;
}

.event-card__title a::after {
  content: "";
  position: absolute;
  inset: 0;
}

.event-card__title a:hover,
.event-card__title a:focus-visible {
  color: var(--isoc-navy);
}

.event-card__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 17px;
  line-height: 1.6;
}

.event-card__meta .icon {
  color: var(--isoc-depth-blue);
}

.events-empty {
  font-size: 20px;
}

/* Single event */
.event__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  align-items: start;
  gap: 60px;
}

.event__details {
  position: sticky;
  top: calc(var(--header-height) + 24px);
  padding: 30px;
  border-radius: var(--radius);
  background: var(--color-band-light);
}

.event-details {
  margin: 0 0 24px;
}

.event-details dt {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  font-weight: 600;
}

.event-details dt:first-child {
  margin-top: 0;
}

.event-details dd {
  margin: 4px 0 0 26px;
}

.event-details__actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-details__closed {
  margin: 0;
  padding: 10px 16px;
  border: 1.5px dashed var(--isoc-depth-blue);
  border-radius: var(--radius-pill);
  text-align: center;
}

@media (max-width: 1023px) {
  .event-list--grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .event__layout {
    grid-template-columns: minmax(0, 1fr);
    gap: 30px;
  }

  .event__details {
    position: static;
    order: -1;
  }
}

@media (max-width: 599px) {
  .event-card {
    gap: 16px;
    padding: 18px;
  }

  .event-card__date {
    flex-basis: 60px;
    height: 70px;
  }

  .event-card__day {
    font-size: 28px;
  }
}
```

- [ ] **Step 5: Add the exampleSite and edge events**

English events (`exampleSite/content/en/events/`):

`samnet-5.md`:
```markdown
---
title: SamNet 5 conference
date: 2026-09-01T09:00:00+02:00
translationKey: event-samnet-5
start: 2027-01-21T09:00:00+01:00
end: 2027-01-21T17:00:00+01:00
location: Internetstiftelsen, Hammarby kaj 10D, Stockholm
organizer: SamNet
registration_url: https://example.com/register
summary: A full day about technology, the Internet, privacy and decentralisation.
---
SamNet is a full-day conference about technology, the Internet, privacy and decentralisation. It is for everyone who wants to help shape our digital future and discuss its challenges and opportunities.
```

`agm-2027.md`:
```markdown
---
title: Annual general meeting 2027, online
date: 2026-09-01T09:00:00+02:00
translationKey: event-agm-2027
start: 2027-03-24T18:00:00+01:00
end: 2027-03-24T20:30:00+01:00
online: true
online_url: https://meet.example.org/agm-2027
registration_closed: true
summary: The annual general meeting for members, held online.
---
The annual general meeting is open to members only. The meeting link is sent the day before to the email address you registered with.
```

`agm-2026.md`:
```markdown
---
title: Annual general meeting 2026
date: 2026-02-11T10:00:00+01:00
translationKey: event-agm-2026
start: 2026-03-25T18:00:00+01:00
end: 2026-03-25T20:30:00+01:00
online: true
summary: The 2026 annual general meeting, held online.
---
Minutes from the meeting are available from the board on request.
```

`samnet-4.md`:
```markdown
---
title: SamNet 4 conference
date: 2025-12-11T09:00:00+01:00
translationKey: event-samnet-4
start: 2026-01-22T09:00:00+01:00
end: 2026-01-22T17:00:00+01:00
location: Internetstiftelsen, Hammarby kaj 10D, Stockholm
organizer: SamNet
summary: The fourth SamNet conference.
---
Thank you to everyone who joined us for the fourth SamNet conference.
```

Swedish events (`exampleSite/content/sv/evenemang/`):

`samnet-5.md`:
```markdown
---
title: SamNet 5-konferensen
date: 2026-09-01T09:00:00+02:00
translationKey: event-samnet-5
start: 2027-01-21T09:00:00+01:00
end: 2027-01-21T17:00:00+01:00
location: Internetstiftelsen, Hammarby kaj 10D, Stockholm
organizer: SamNet
registration_url: https://example.com/register
summary: En heldag om teknik, internet, integritet och decentralisering.
---
SamNet är en heldagskonferens om teknik, internet, integritet och decentralisering, för dig som vill vara med och forma digitaliseringens framtid.
```

`arsstamma-2027.md`:
```markdown
---
title: Årsstämma 2027, online
date: 2026-09-01T09:00:00+02:00
translationKey: event-agm-2027
start: 2027-03-24T18:00:00+01:00
end: 2027-03-24T20:30:00+01:00
online: true
online_url: https://meet.example.org/agm-2027
registration_closed: true
summary: Föreningens årsstämma för medlemmar, online.
---
Årsstämman är enbart för medlemmar. Länken skickas dagen innan till den e-postadress du registrerade dig med.
```

`arsstamma-2026.md`:
```markdown
---
title: Årsstämma 2026
date: 2026-02-11T10:00:00+01:00
translationKey: event-agm-2026
start: 2026-03-25T18:00:00+01:00
end: 2026-03-25T20:30:00+01:00
online: true
summary: Årsstämman 2026, online.
---
Protokollet kan begäras från styrelsen.
```

`samnet-4.md`:
```markdown
---
title: SamNet 4-konferensen
date: 2025-12-11T09:00:00+01:00
translationKey: event-samnet-4
start: 2026-01-22T09:00:00+01:00
end: 2026-01-22T17:00:00+01:00
location: Internetstiftelsen, Hammarby kaj 10D, Stockholm
organizer: SamNet
summary: Den fjärde SamNet-konferensen.
---
Tack till alla som var med på den fjärde SamNet-konferensen.
```

Edge events (`tests/edge/content/events/`):

`no-offset.md`:
```markdown
---
title: No offset
date: 2026-01-01
start: 2099-05-01T18:00:00
end: 2099-05-01T20:00:00
---
Times without a UTC offset are read in the site's timeZone.
```

`all-day.md`:
```markdown
---
title: All day
date: 2026-01-01
start: 2099-06-01
end: 2099-06-02
all_day: true
---
A two-day event without times.
```

`no-end.md`:
```markdown
---
title: No end
date: 2026-01-01
start: 2099-07-01T10:00:00+02:00
end: ""
---
An event with an empty end time (as left by the archetype): treated as no end.
```

`past.md`:
```markdown
---
title: Past event
date: 2020-01-01
start: 2020-02-01T10:00:00+01:00
end: 2020-02-01T12:00:00+01:00
---
An event that is over.
```

- [ ] **Step 6: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: every check so far PASSES, including all `events_*`.

Note for maintainers (also documented in the README in Task 11): "upcoming" is decided at build time, so the site must be rebuilt regularly (the demo workflow rebuilds daily).

---

### Task 8: Homepage blocks and shortcodes

**Files:**
- Overwrite: `layouts/home.html`
- Create: `layouts/_partials/blocks/{hero,intro,image_text,stats,latest_posts,upcoming_events,quote,cta,gallery,markdown}.html`
- Create: `layouts/_partials/image-text.html`, `quote.html`, `stats.html`, `cta.html`, `gallery.html`, `latest-posts-grid.html`
- Create: `layouts/_shortcodes/{button,cta,image-text,quote,stats,stat,columns,column,gallery,latest-posts,upcoming-events,notice}.html`
- Create: `assets/css/blocks.css`
- Create: `exampleSite/assets/images/home/{section,gallery-1,gallery-2,gallery-3}.jpg`, `exampleSite/content/en/shortcodes/photo-{1,2}.jpg`
- Overwrite: `exampleSite/content/en/_index.md`, `exampleSite/content/sv/_index.md`, `exampleSite/content/en/shortcodes/index.md`, `tests/edge/content/_index.md`
- Test: `scripts/checks/home.py`

**Interfaces:**
- Consumes: `banner-image.html`, `img.html`, `button.html`, `func/url.html`, `card.html` (Task 5); `upcoming-events-grid.html`, `card-event.html` (Task 7); `.block__title`, `.cards-band` (Task 6); `T` keys `moreNews`, `upcomingEvents`, `allEvents`.
- Produces:
  - Homepage front matter `blocks:`, a list of maps with a `type` key. Each type renders `layouts/_partials/blocks/<type>.html` with context `dict "page" PAGE "block" MAP "index" INT`. Unknown types warn `Homepage block N has unknown type "x" (<file>)` and are skipped. If `blocks` is empty, the homepage shows a default hero and the latest posts.
  - Block keys as in the spec §6.4; `background` ∈ `white|light|green|navy|blue`.
  - Inner partials shared by blocks and shortcodes: `image-text.html` (dict page src alt side ratio content buttons), `quote.html` (dict text author role), `stats.html` (list of dict value label), `cta.html` (dict title text button background), `gallery.html` (dict page images: list of dict res|src alt caption), `latest-posts-grid.html` (dict count section).
  - Every block's inner wrapper carries the class `reveal`. Task 10 styles it.

- [ ] **Step 1: Write the failing homepage and shortcode checks**

`scripts/checks/home.py`:
```python
from checklib import check, expect

ORDER = ["hero", "block-image-text", "block-intro", "block-stats", "block-latest-posts",
         "block-upcoming-events", "block-quote", "block-cta", "block-gallery", "block-markdown"]


def _blocks(root):
    main = root.find("main")
    return [k for k in main.kids() if k.tag in ("section", "header")]


@check
def home_blocks_render_in_order(ctx):
    for rel in ("/", "/sv/"):
        found = []
        for el in _blocks(ctx.main.html(rel)):
            found += [c for c in el.classes if c in ORDER]
        expect(found == ORDER, f"{rel}: block order {found}")


@check
def home_hero(ctx):
    hero = ctx.main.html("/").find("section.hero")
    expect("banner--green" in hero.classes, "hero defaults to the green pattern")
    expect(hero.find("h1.hero__title").text() == "Internet Society Chapter", "hero title")
    expect(hero.find(".hero__tagline") is not None, "hero tagline")
    expect([a.attrs["href"] for a in hero.select("a.btn")] == ["/membership/"], "hero button href")
    sv = ctx.main.html("/sv/").find("section.hero a.btn")
    expect(sv.attrs["href"] == "/sv/medlemskap/", f"sv hero button {sv.attrs['href']}")
    expect(len(ctx.main.html("/").select("h1")) == 1, "homepage needs exactly one h1")


@check
def home_latest_posts_and_events(ctx):
    root = ctx.main.html("/")
    latest = root.find("section.block-latest-posts")
    expect(len(latest.select(".card")) == 4, "latest posts should show 4 cards")
    expect(latest.find(".block__more a").attrs["href"] == "/posts/", "more news link")
    sv_more = ctx.main.html("/sv/").find("section.block-latest-posts .block__more a")
    expect(sv_more.attrs["href"] == "/sv/nyheter/" and sv_more.text() == "Fler nyheter", "sv more news link")
    events = root.find("section.block-upcoming-events")
    titles = [a.text() for a in events.select(".event-card__title a")]
    expect(titles == ["SamNet 5 conference", "Annual general meeting 2027, online"], f"upcoming block {titles}")
    expect(events.find(".block__more a").attrs["href"] == "/events/", "all events link")


@check
def home_content_blocks(ctx):
    root = ctx.main.html("/")
    expect(root.find("section.block-image-text .image-text img") is not None, "image_text image")
    expect(root.find("section.block-intro .lead") is not None, "intro lead")
    stats = root.select("section.block-stats li.stat")
    expect([s.find(".stat__value").text() for s in stats] == ["120+", "1992", "100 000+"], "stats values")
    expect("band--navy" in root.find("section.block-stats").classes, "stats background")
    quote = root.find("section.block-quote figure.quote")
    expect(quote.find("blockquote").text() == "The Internet is for everyone.", "quote text")
    expect(quote.find(".quote__author").text() == "Internet Society", "quote author")
    cta = root.find("section.block-cta")
    expect(cta.find("h2").text() == "Become a member" and cta.find("a.btn--white") is not None, "cta block")
    gallery = root.select("section.block-gallery ul.gallery img")
    expect(len(gallery) == 3, "gallery should show 3 images")
    expect(all(g.attrs.get("width") == "600" and g.attrs.get("height") == "600" for g in gallery), "gallery fill 600x600")
    expect(root.find("section.block-markdown .entry-content p") is not None, "markdown block")


@check
def home_shortcodes_page(ctx):
    raw = ctx.main.read("shortcodes/index.html")
    for bad in ("{{<", "HAHAHUGO", "<p><div", "<p><figure", "<p><ul"):
        expect(bad not in raw, f"shortcodes page contains {bad!r}")
    root = ctx.main.html("/shortcodes/")
    content = root.find(".entry-content")
    expect(len(content.select("a.btn")) >= 3, "buttons")
    expect(len(content.select(".notice")) == 2 and content.find(".notice--warning") is not None, "notices")
    expect(content.find(".image-text.image-text--right img") is not None, "image-text shortcode")
    expect(content.find("figure.quote blockquote").text() == "The Internet is for everyone.", "quote shortcode")
    expect(len(content.select("ul.stats li.stat")) == 3, "stats shortcode")
    expect(len(content.select(".columns .column h3")) == 2, "columns shortcode")
    expect(len(content.select("ul.gallery img")) == 2, "gallery shortcode uses the bundle's images")
    expect(len(content.select(".card-grid .card")) == 4, "latest-posts shortcode")
    expect(len(content.select(".event-list .event-card")) == 2, "upcoming-events shortcode")
    expect(content.find(".cta--box h2").text() == "Join the chapter", "cta shortcode")


@check
def home_edge_unknown_block(ctx):
    root = ctx.edge.html("/")
    expect(root.find("section.hero h1").text() == "Edge Chapter", "edge hero defaults its title to the site title")
    expect('unknown type "nonsense"' in ctx.edge.log, "edge log should warn about the unknown block type")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh home`
Expected: FAIL. Every `home_*` check fails (`/: block order []`, missing `section.hero`, …).

- [ ] **Step 3: Create the shared inner partials**

`layouts/_partials/image-text.html`:
```html
{{- /* Context: dict "page" "src" "alt" "side" (left|right) "ratio" (50-50|30-70|70-30) "content" HTML ["buttons"]. */ -}}
{{- $side := .side | default "left" -}}
{{- $ratio := .ratio | default "50-50" -}}
{{- if not (in (slice "left" "right") $side) }}{{ warnf "image-text: unknown side %q; using \"left\"" $side }}{{ $side = "left" }}{{ end -}}
{{- if not (in (slice "50-50" "30-70" "70-30") $ratio) }}{{ warnf "image-text: unknown ratio %q; using \"50-50\"" $ratio }}{{ $ratio = "50-50" }}{{ end -}}
<div class="image-text image-text--{{ $side }} image-text--{{ $ratio }}">
  <div class="image-text__media">{{ partial "img.html" (dict "page" .page "src" .src "alt" .alt "sizes" "(min-width: 768px) 50vw, 90vw") }}</div>
  <div class="image-text__body">
    {{ .content }}
    {{- with .buttons }}
    <div class="btn-row">{{ range . }}{{ partial "button.html" . }}{{ end }}</div>
    {{- end }}
  </div>
</div>
```

`layouts/_partials/quote.html`:
```html
{{- /* Context: dict "text" HTML "author" "role". */ -}}
<figure class="quote">
  <img class="quote__icon" src="{{ (resources.Get "images/quote.svg").RelPermalink }}" alt="" width="104" height="84">
  <blockquote class="quote__text">{{ .text }}</blockquote>
  {{- with .author }}
  <figcaption class="quote__cite"><span class="quote__author">{{ . }}</span>{{ with $.role }}<span class="quote__role">{{ . }}</span>{{ end }}</figcaption>
  {{- end }}
</figure>
```

Copy the quote mark from the reference theme:
```bash
cp genesis-child-chapters-main/images/Parenthesis-Homepage-quote-blue-207px-153px.svg assets/images/quote.svg
```

`layouts/_partials/stats.html`:
```html
{{- /* Context: list of dict "value" "label". */ -}}
<ul class="stats">
  {{- range . }}
  <li class="stat"><span class="stat__value">{{ .value }}</span><span class="stat__label">{{ .label }}</span></li>
  {{- end }}
</ul>
```

`layouts/_partials/cta.html`:
```html
{{- /* Context: dict "title" "text" HTML "button" (dict label url [style]) "background". */ -}}
{{- $dark := in (slice "navy" "blue") (.background | default "navy") -}}
<div class="cta">
  {{- with .title }}
  <h2 class="cta__title">{{ . }}</h2>
  {{- end }}
  {{- with .text }}
  <div class="cta__text">{{ . }}</div>
  {{- end }}
  {{- with .button }}{{ if .url }}
  <p class="cta__action">{{ partial "button.html" (dict "label" .label "url" .url "style" (.style | default (cond $dark "white" "primary"))) }}</p>
  {{- end }}{{ end }}
</div>
```

`layouts/_partials/gallery.html`:
```html
{{- /* Context: dict "page" PAGE "images" (list of dict "res" or "src", "alt", "caption"). */ -}}
<ul class="gallery">
  {{- range .images }}
  <li class="gallery__item">
    <figure>
      {{ partial "img.html" (dict "page" $.page "res" .res "src" .src "alt" .alt "fill" "600x600" "sizes" "(min-width: 768px) 33vw, 50vw") }}
      {{- with .caption }}<figcaption>{{ . }}</figcaption>{{ end }}
    </figure>
  </li>
  {{- end }}
</ul>
```

`layouts/_partials/latest-posts-grid.html`:
```html
{{- /* Context: dict "count" N ["section" NAME]. */ -}}
{{- $posts := where site.RegularPages "Type" "posts" -}}
{{- with .section }}{{ $posts = where $posts "Section" . }}{{ end -}}
{{- with first (int (.count | default 4)) $posts.ByDate.Reverse -}}
<div class="card-grid card-grid--4">
  {{- range . }}{{ partial "card.html" . }}{{ end }}
</div>
{{- end -}}
```

- [ ] **Step 4: Create the block partials**

`layouts/_partials/blocks/hero.html`:
```html
{{- $b := .block -}}
{{- $variant := $b.banner | default "green" -}}
{{- $img := partial "func/banner-image.html" (dict "page" .page "variant" $variant "src" $b.image "hero" true) -}}
<section class="hero banner banner--{{ $variant }}"{{ with $img }} style="{{ printf "background-image:url('%s')" .RelPermalink | safeCSS }}"{{ end }}>
  <div class="wrap wrap--1180 banner__inner">
    <h1 class="hero__title">{{ $b.title | default site.Title }}</h1>
    {{- with $b.tagline }}
    <p class="hero__tagline">{{ . | markdownify }}</p>
    {{- end }}
    {{- with $b.buttons }}
    <div class="btn-row">{{ range . }}{{ partial "button.html" . }}{{ end }}</div>
    {{- end }}
  </div>
</section>
```

`layouts/_partials/blocks/intro.html`:
```html
{{- $b := .block -}}
<section class="block block-intro{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--1180 reveal">
    <div class="lead">{{ .page.RenderString (dict "display" "block") ($b.text | default "") }}</div>
  </div>
</section>
```

`layouts/_partials/blocks/image_text.html`:
```html
{{- $b := .block -}}
{{- $text := "" -}}
{{- with $b.text }}{{ $text = $.page.RenderString (dict "display" "block") . }}{{ end -}}
<section class="block block-image-text{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--1180 reveal">
    {{ partial "image-text.html" (dict "page" .page "src" $b.image "alt" $b.image_alt "side" $b.image_side "ratio" $b.ratio "content" $text "buttons" $b.buttons) }}
  </div>
</section>
```

`layouts/_partials/blocks/stats.html`:
```html
{{- $b := .block -}}
<section class="block block-stats{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--1180 reveal">
    {{- with $b.title }}
    <h2 class="block__title">{{ . }}</h2>
    {{- end }}
    {{ partial "stats.html" ($b.items | default slice) }}
  </div>
</section>
```

`layouts/_partials/blocks/latest_posts.html`:
```html
{{- $b := .block -}}
{{- if where site.RegularPages "Type" "posts" -}}
{{- $more := "" -}}
{{- with $b.more_url -}}
  {{- $more = partial "func/url.html" (dict "url" .) -}}
{{- else -}}
  {{- range first 1 (where site.Sections "Type" "posts") }}{{ $more = .RelPermalink }}{{ end -}}
{{- end -}}
<section class="block block-latest-posts band band--{{ $b.background | default "light" }}">
  <div class="wrap wrap--1180 reveal">
    {{- with $b.title }}
    <h2 class="block__title">{{ . }}</h2>
    {{- end }}
    {{ partial "latest-posts-grid.html" (dict "count" ($b.count | default 4) "section" $b.section) }}
    {{- with $more }}
    <p class="block__more"><a class="btn" href="{{ . }}">{{ $b.more_label | default (T "moreNews") }}</a></p>
    {{- end }}
  </div>
</section>
{{- end -}}
```

`layouts/_partials/blocks/upcoming_events.html`:
```html
{{- $b := .block -}}
{{- $grid := partial "upcoming-events-grid.html" (dict "count" ($b.count | default 3)) -}}
{{- if or $grid $b.empty_text -}}
<section class="block block-upcoming-events{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--1180 reveal">
    <h2 class="block__title">{{ $b.title | default (T "upcomingEvents") }}</h2>
    {{- with $grid }}
    {{ . }}
    {{- else }}
    <p class="events-empty">{{ $b.empty_text }}</p>
    {{- end }}
    {{- range first 1 (where site.Sections "Type" "events") }}
    <p class="block__more"><a class="btn btn--secondary" href="{{ .RelPermalink }}">{{ T "allEvents" }}</a></p>
    {{- end }}
  </div>
</section>
{{- end -}}
```

`layouts/_partials/blocks/quote.html`:
```html
{{- $b := .block -}}
<section class="block block-quote{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--960 reveal">
    {{ partial "quote.html" (dict "text" (.page.RenderString (dict "display" "block") ($b.text | default "")) "author" $b.author "role" $b.role) }}
  </div>
</section>
```

`layouts/_partials/blocks/cta.html`:
```html
{{- $b := .block -}}
{{- $bg := $b.background | default "navy" -}}
{{- $text := "" -}}
{{- with $b.text }}{{ $text = $.page.RenderString (dict "display" "block") . }}{{ end -}}
<section class="block block-cta band band--{{ $bg }}">
  <div class="wrap wrap--960 reveal">
    {{ partial "cta.html" (dict "title" $b.title "text" $text "button" $b.button "background" $bg) }}
  </div>
</section>
```

`layouts/_partials/blocks/gallery.html`:
```html
{{- $b := .block -}}
<section class="block block-gallery{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--1180 reveal">
    {{- with $b.title }}
    <h2 class="block__title">{{ . }}</h2>
    {{- end }}
    {{ partial "gallery.html" (dict "page" .page "images" ($b.images | default slice)) }}
  </div>
</section>
```

`layouts/_partials/blocks/markdown.html`:
```html
{{- $b := .block -}}
{{- with .page.Content -}}
<section class="block block-markdown{{ with $b.background }} band band--{{ . }}{{ end }}">
  <div class="wrap wrap--1180 reveal">
    <div class="entry-content">{{ . }}</div>
  </div>
</section>
{{- end -}}
```

Overwrite `layouts/home.html`:
```html
{{ define "main" }}
{{- $blocks := .Params.blocks -}}
{{- if not $blocks -}}
  {{- $blocks = slice (dict "type" "hero" "tagline" site.Params.description) (dict "type" "latest_posts") (dict "type" "markdown") -}}
{{- end -}}
{{- $hasMarkdown := false -}}
{{- range $blocks }}{{ if eq .type "markdown" }}{{ $hasMarkdown = true }}{{ end }}{{ end -}}
{{- range $i, $b := $blocks -}}
  {{- $tpl := printf "blocks/%s.html" (string $b.type) -}}
  {{- if templates.Exists (printf "_partials/%s" $tpl) -}}
    {{ partial $tpl (dict "page" $ "block" $b "index" $i) }}
  {{- else -}}
    {{- warnf "Homepage block %d has unknown type %q (%s)" $i (string $b.type) $.File.Path -}}
  {{- end -}}
{{- end -}}
{{- if and .Content (not $hasMarkdown) }}
{{ partial "blocks/markdown.html" (dict "page" . "block" dict) }}
{{- end }}
{{ end }}
```

- [ ] **Step 5: Create the shortcodes**

`layouts/_shortcodes/button.html`:
```html
{{- partial "button.html" (dict "label" (.Inner | strings.TrimSpace) "url" (.Get "url") "style" (.Get "style")) -}}
```

`layouts/_shortcodes/notice.html`:
```html
<div class="notice{{ with .Get "type" }}{{ if ne . "info" }} notice--{{ . }}{{ end }}{{ end }}">{{ .Page.RenderString (dict "display" "block") (.Inner | strings.TrimSpace) }}</div>
```

`layouts/_shortcodes/image-text.html`:
```html
{{- partial "image-text.html" (dict "page" .Page "src" (.Get "image") "alt" (.Get "alt") "side" (.Get "side") "ratio" (.Get "ratio") "content" (.Page.RenderString (dict "display" "block") (.Inner | strings.TrimSpace))) -}}
```

`layouts/_shortcodes/quote.html`:
```html
{{- partial "quote.html" (dict "text" (.Page.RenderString (dict "display" "block") (.Inner | strings.TrimSpace)) "author" (.Get "author") "role" (.Get "role")) -}}
```

`layouts/_shortcodes/stats.html`:
```html
<ul class="stats">{{ .Inner }}</ul>
```

`layouts/_shortcodes/stat.html`:
```html
<li class="stat"><span class="stat__value">{{ .Get "value" }}</span><span class="stat__label">{{ .Get "label" }}</span></li>
```

`layouts/_shortcodes/columns.html`:
```html
<div class="columns">{{ .Inner }}</div>
```

`layouts/_shortcodes/column.html`:
```html
<div class="column">{{ .Page.RenderString (dict "display" "block") (.Inner | strings.TrimSpace) }}</div>
```

`layouts/_shortcodes/gallery.html`:
```html
{{- /* Images from this page bundle; optional match="glob" narrows them. alt/caption come from resource params. */ -}}
{{- $imgs := .Page.Resources.ByType "image" -}}
{{- with .Get "match" }}{{ $imgs = $.Page.Resources.Match . }}{{ end -}}
{{- $items := slice -}}
{{- range $imgs }}{{ $items = $items | append (dict "res" . "alt" (.Params.alt | default "") "caption" (.Params.caption | default "")) }}{{ end -}}
{{- partial "gallery.html" (dict "page" .Page "images" $items) -}}
```

`layouts/_shortcodes/latest-posts.html`:
```html
{{- partial "latest-posts-grid.html" (dict "count" (.Get "count" | default 4) "section" (.Get "section")) -}}
```

`layouts/_shortcodes/upcoming-events.html`:
```html
{{- partial "upcoming-events-grid.html" (dict "count" (.Get "count" | default 3)) -}}
```

`layouts/_shortcodes/cta.html`:
```html
{{- $bg := .Get "background" | default "navy" -}}
<div class="cta--box band band--{{ $bg }}">
  {{ partial "cta.html" (dict "title" (.Get "title") "text" (.Page.RenderString (dict "display" "block") (.Inner | strings.TrimSpace)) "button" (dict "label" (.Get "label") "url" (.Get "url")) "background" $bg) }}
</div>
```

- [ ] **Step 6: Create the blocks CSS**

`assets/css/blocks.css`:
```css
/* Homepage blocks and their shortcode counterparts. */
.block {
  padding-block: var(--section-space);
}

.block__more {
  margin: 40px 0 0;
  text-align: center;
}

/* Image + text (WP .col-with-left-img, .section-30-70, .section-70-30) */
.image-text {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  align-items: center;
  gap: 60px;
  margin: 0 0 30px;
}

.block .image-text {
  margin: 0;
}

.image-text--30-70 { grid-template-columns: minmax(0, 3fr) minmax(0, 7fr); }
.image-text--70-30 { grid-template-columns: minmax(0, 7fr) minmax(0, 3fr); }
.image-text--right.image-text--30-70 { grid-template-columns: minmax(0, 7fr) minmax(0, 3fr); }
.image-text--right.image-text--70-30 { grid-template-columns: minmax(0, 3fr) minmax(0, 7fr); }

.image-text--right .image-text__media {
  order: 2;
}

.image-text__media img {
  display: block;
  width: 100%;
  height: auto;
}

.image-text__body > :last-child {
  margin-bottom: 0;
}

/* Stats */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
  margin: 0 0 30px;
  padding: 0;
  list-style: none;
  text-align: center;
}

.block .stats {
  margin: 0;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
}

.stat__value {
  color: var(--isoc-depth-blue);
  font-size: 56px;
  font-weight: 700;
  line-height: 1;
}

.stat__label {
  font-size: 20px;
  line-height: 1.3;
}

.band--navy .stat__value,
.band--blue .stat__value {
  color: var(--color-accent);
}

/* Quote with the ISOC parenthesis mark */
.quote {
  display: grid;
  grid-template-columns: 104px minmax(0, 1fr);
  gap: 0 40px;
  align-items: start;
  margin: 0 0 30px;
}

.block .quote {
  margin: 0;
}

.quote__icon {
  grid-row: span 2;
  width: 104px;
  height: auto;
}

.quote__text {
  margin: 0;
  color: var(--isoc-depth-blue);
  font-size: 30px;
  font-style: normal;
  line-height: 1.4;
}

.quote__text p {
  margin-bottom: 16px;
}

.quote__cite {
  display: flex;
  flex-direction: column;
  grid-column: 2;
  margin-top: 24px;
  font-size: 18px;
}

.quote__author {
  font-weight: 600;
}

.quote__role {
  color: var(--isoc-gray);
}

.band--navy .quote__text,
.band--blue .quote__text,
.band--navy .quote__role,
.band--blue .quote__role {
  color: #fff;
}

/* Call to action band */
.cta {
  text-align: center;
}

.cta__title {
  margin: 0 0 20px;
  color: inherit;
  font-size: 40px;
  font-weight: 700;
  line-height: 1.25;
}

.band--white .cta__title,
.band--light .cta__title,
.band--green .cta__title {
  color: var(--color-heading);
}

.cta__text {
  max-width: 700px;
  margin: 0 auto 30px;
  font-size: 21px;
}

.cta__action {
  margin: 0;
}

.cta--box {
  margin: 0 0 30px;
  padding: 50px 30px;
  border-radius: var(--radius);
}

/* Gallery (static grid instead of the slick slider) */
.gallery {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  margin: 0 0 30px;
  padding: 0;
  list-style: none;
}

.block .gallery {
  margin: 0;
}

.gallery__item,
.gallery figure {
  margin: 0;
}

.gallery img {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 1;
  object-fit: cover;
}

.gallery figcaption {
  margin-top: 8px;
  font-size: 15px;
  line-height: 1.4;
}

@media (max-width: 767px) {
  .image-text,
  .image-text--30-70,
  .image-text--70-30,
  .image-text--right.image-text--30-70,
  .image-text--right.image-text--70-30 {
    grid-template-columns: minmax(0, 1fr);
    gap: 30px;
  }

  .image-text--right .image-text__media {
    order: 0;
  }

  .stat__value { font-size: 44px; }

  .quote {
    grid-template-columns: minmax(0, 1fr);
  }

  .quote__icon {
    grid-row: auto;
    width: 64px;
    margin-bottom: 16px;
  }

  .quote__text { font-size: 24px; }

  .quote__cite {
    grid-column: 1;
  }

  .cta__title { font-size: 30px; }

  .gallery {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
```

- [ ] **Step 7: Add the homepage content and images**

```bash
mkdir -p exampleSite/assets/images/home
cp genesis-child-chapters-main/config/import/images/home/Green-pattern-medium-projects-page-1.jpg exampleSite/assets/images/home/section.jpg
cp genesis-child-chapters-main/config/import/images/home/gallery-image.jpg exampleSite/assets/images/home/gallery-1.jpg
cp genesis-child-chapters-main/config/import/images/home/Section-Pattern-medium.jpg exampleSite/assets/images/home/gallery-2.jpg
cp genesis-child-chapters-main/config/import/images/projects/Green-pattern-blog-page.jpg exampleSite/assets/images/home/gallery-3.jpg
cp genesis-child-chapters-main/config/import/images/home/Green-pattern-medium-projects-page-1.jpg exampleSite/content/en/shortcodes/photo-1.jpg
cp genesis-child-chapters-main/config/import/images/home/Section-Pattern-medium.jpg exampleSite/content/en/shortcodes/photo-2.jpg
```

Overwrite `exampleSite/content/en/_index.md`:
```markdown
---
title: Home
blocks:
  - type: hero
    title: Internet Society Chapter
    tagline: Working for an Internet that is open, globally connected, secure and trustworthy, for everyone.
    buttons:
      - label: Get involved
        url: /membership
  - type: image_text
    image: images/home/section.jpg
    image_alt: ""
    text: |
      We are a group of volunteers who care about the Internet. We organise talks and conferences, respond to public consultations, and help people get online safely.
    buttons:
      - label: About us
        url: /about
  - type: intro
    text: The Internet is one of the most important tools of our time. We want it to stay open, so that everyone can use it to learn, create and connect.
  - type: stats
    background: navy
    items:
      - value: "120+"
        label: Chapters worldwide
      - value: "1992"
        label: Year the Internet Society was founded
      - value: "100 000+"
        label: Members globally
  - type: latest_posts
    title: Latest news
  - type: upcoming_events
    title: Upcoming events
  - type: quote
    text: The Internet is for everyone.
    author: Internet Society
    role: Mission statement
  - type: cta
    title: Become a member
    text: Membership is free and open to everyone who shares our goals.
    button:
      label: Join us
      url: https://community.internetsociety.org/s/new-registration
  - type: gallery
    title: From our events
    images:
      - src: images/home/gallery-1.jpg
        alt: ""
      - src: images/home/gallery-2.jpg
        alt: ""
      - src: images/home/gallery-3.jpg
        alt: ""
  - type: markdown
---
This text comes from the Markdown body of `content/en/_index.md`. The `markdown` block decides where it appears on the page.
```

Overwrite `exampleSite/content/sv/_index.md`:
```markdown
---
title: Hem
blocks:
  - type: hero
    title: Internet Society Sverige
    tagline: Vi arbetar för ett internet som är öppet, globalt sammankopplat, säkert och pålitligt, för alla.
    buttons:
      - label: Engagera dig
        url: /medlemskap
  - type: image_text
    image: images/home/section.jpg
    image_alt: ""
    text: |
      Vi är en grupp ideella krafter som bryr sig om internet. Vi arrangerar föredrag och konferenser, svarar på remisser och hjälper människor att använda internet säkert.
    buttons:
      - label: Om oss
        url: /om
  - type: intro
    text: Internet är ett av vår tids viktigaste verktyg. Vi vill att det förblir öppet, så att alla kan använda det för att lära sig, skapa och mötas.
  - type: stats
    background: navy
    items:
      - value: "120+"
        label: Chapters i världen
      - value: "1992"
        label: Året Internet Society grundades
      - value: "100 000+"
        label: Medlemmar globalt
  - type: latest_posts
    title: Senaste nytt
  - type: upcoming_events
    title: Kommande evenemang
  - type: quote
    text: Internet är till för alla.
    author: Internet Society
    role: Vision
  - type: cta
    title: Bli medlem
    text: Medlemskap är gratis och öppet för alla som delar våra mål.
    button:
      label: Gå med
      url: https://community.internetsociety.org/s/new-registration
  - type: gallery
    title: Från våra evenemang
    images:
      - src: images/home/gallery-1.jpg
        alt: ""
      - src: images/home/gallery-2.jpg
        alt: ""
      - src: images/home/gallery-3.jpg
        alt: ""
  - type: markdown
---
Den här texten kommer från Markdown-delen av `content/sv/_index.md`. Blocket `markdown` bestämmer var den visas.
```

Overwrite `exampleSite/content/en/shortcodes/index.md`:
```markdown
---
title: Shortcodes
lead: Every shortcode the theme provides, in one place.
resources:
  - src: "photo-*.jpg"
    params:
      alt: Abstract green pattern
---
This page exists only in English, so the language switcher sends Swedish readers to the Swedish homepage.

## Button

{{< button url="/membership" >}}Become a member{{< /button >}}
{{< button url="/contact" style="secondary" >}}Contact us{{< /button >}}

## Notice

{{< notice >}}
The annual general meeting is on **25 March**.
{{< /notice >}}

{{< notice type="warning" >}}
Registration closes on Friday.
{{< /notice >}}

## Image and text

{{< image-text image="photo-1.jpg" alt="Abstract green pattern" side="right" >}}
Pair a picture with a short text. The image can sit on either side, at 50/50, 30/70 or 70/30.
{{< /image-text >}}

## Quote

{{< quote author="Internet Society" role="Mission statement" >}}
The Internet is for everyone.
{{< /quote >}}

## Stats

{{< stats >}}
{{< stat value="120+" label="Chapters worldwide" >}}
{{< stat value="1992" label="Year the Internet Society was founded" >}}
{{< stat value="100 000+" label="Members globally" >}}
{{< /stats >}}

## Columns

{{< columns >}}
{{< column >}}
### Open
The Internet should be available to everyone.
{{< /column >}}
{{< column >}}
### Secure
People should be able to trust the Internet.
{{< /column >}}
{{< /columns >}}

## Gallery

{{< gallery >}}

## Latest posts

{{< latest-posts count="4" >}}

## Upcoming events

{{< upcoming-events count="2" >}}

## Call to action

{{< cta title="Join the chapter" url="/membership" label="Become a member" >}}
Membership is free and open to everyone.
{{< /cta >}}
```

Overwrite `tests/edge/content/_index.md`:
```markdown
---
title: Edge
blocks:
  - type: hero
  - type: nonsense
---
```

- [ ] **Step 8: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: every check so far PASSES, including all `home_*`.

Hugo 0.167 does not wrap a shortcode in `<p>` when it sits alone on its own line, with blank lines around it (verified). Consecutive inline shortcodes, like the two buttons, share one `<p>`, which is valid. If `home_shortcodes_page` reports `<p><div`, a blank line is missing around a block shortcode in `index.md`.

---

### Task 9: Search (Fuse.js)

**Files:**
- Create: `assets/js/vendor/fuse.basic.min.js`, `assets/js/vendor/fuse.LICENSE.txt` (downloaded)
- Create: `layouts/_partials/func/search-index.html`, `search-config.html`, `search-toggle.html`, `search-panel.html`
- Create: `layouts/search.html`, `assets/js/search.js`, `assets/css/search.css`
- Modify: `layouts/_partials/header.html`, `layouts/_partials/scripts.html`
- Create: `exampleSite/content/en/search.md`, `exampleSite/content/sv/search.md`
- Modify: `tests/edge/hugo.toml` (`showSearch = false`)
- Test: `scripts/checks/search.py`

**Interfaces:**
- Consumes: `icon.html` (`search`), `banner.html`; `T` keys `search`, `searchSite`, `searchPlaceholder`, `searchNoResults`, `searchResultsCount`, `searchSeeAll`, `searchError`, `searchJsRequired`.
- Produces:
  - `partialCached "func/search-index.html" PAGE site.Language.Name` → JSON resource at `/search-index/<lang>.json`: list of `{title, url, section, date, tags, categories, summary, content}` for every regular page and section page without `search_exclude: true`; `content` ≤ 1500 characters plus an ellipsis.
  - `<script type="application/json" id="search-config">` with `index`, `fuse`, `fuseIntegrity`, `page` (search page URL or `""`), `i18n.{noResults,results,seeAll,error}` (`{query}`/`{count}` placeholders).
  - Search page: any page with `layout: search`, found by `site.GetPage "/search"` (so it must live at `content/<lang>/search.md`).
  - DOM hooks for `search.js`: `[data-search-toggle]`, `#search-panel`, `[data-search-input]`, `[data-search-results]`, `form[data-search-page]`, `[data-search-page-results]`.

- [ ] **Step 1: Write the failing search checks**

`scripts/checks/search.py`:
```python
import json
import re

from checklib import check, expect


def _cfg(site, rel):
    el = site.html(rel).find("script#search-config")
    expect(el is not None, f"{rel}: search config missing")
    return json.loads(el.text())


@check
def search_config_per_language(ctx):
    en = _cfg(ctx.main, "/")
    expect(en["page"] == "/search/", f"en search page {en['page']}")
    expect(en["index"] == "/search-index/en.json" and ctx.main.exists(en["index"]), f"en index {en['index']}")
    expect(re.search(r"/js/vendor/fuse\.basic\.min\.[0-9a-f]{64}\.js$", en["fuse"]) and ctx.main.exists(en["fuse"]),
           f"fuse url {en['fuse']}")
    expect(en["fuseIntegrity"].startswith("sha256-"), "fuse integrity missing")
    sv = _cfg(ctx.main, "/sv/")
    expect(sv["page"] == "/sv/sok/" and sv["index"] == "/search-index/sv.json", f"sv config {sv}")
    expect(sv["i18n"]["noResults"] == "Inga träffar för ”{query}”.", f"sv strings {sv['i18n']}")


@check
def search_index_content(ctx):
    items = ctx.main.json("search-index/en.json")
    urls = {i["url"] for i in items}
    for url in ("/posts/annual-general-meeting-2026/", "/events/samnet-5/", "/about/", "/contact/"):
        expect(url in urls, f"index lacks {url}")
    expect("/search/" not in urls, "the search page must be excluded")
    for item in items:
        for key in ("title", "url", "section", "date", "tags", "categories", "summary", "content"):
            expect(key in item, f"{item.get('url')}: missing {key}")
        expect(len(item["content"]) <= 1501, f"{item['url']}: content not truncated ({len(item['content'])})")
        expect(ctx.main.exists(item["url"]), f"index url {item['url']} does not resolve")
    agm = next(i for i in items if i["url"] == "/posts/annual-general-meeting-2026/")
    expect(agm["date"] == "11 February 2026" and agm["categories"] == ["Community"], f"post entry {agm}")
    event = next(i for i in items if i["url"] == "/events/samnet-5/")
    expect(event["date"] == "21 January 2027", f"event entry date {event['date']!r}")
    sv = ctx.main.json("search-index/sv.json")
    expect(sv and all(i["url"].startswith("/sv/") for i in sv), "sv index must only hold Swedish pages")


@check
def search_header_controls(ctx):
    root = ctx.main.html("/")
    toggle = root.find("button.search-toggle")
    expect(toggle is not None and toggle.attrs.get("aria-controls") == "search-panel"
           and toggle.attrs.get("aria-expanded") == "false", "search toggle attributes")
    panel = root.find("#search-panel")
    expect(panel is not None and "hidden" in panel.attrs, "search panel should start hidden")
    form = panel.find("form[role=search]")
    expect(form is not None and form.attrs.get("action") == "/search/", "panel form should submit to /search/")
    field = form.find("input[name=q]")
    expect(form.find(f"label[for={field.attrs['id']}]") is not None, "search input needs a label")
    scripts = [s.attrs["src"] for s in root.select("script[src]")]
    expect(any(re.search(r"/js/search\.min\.[0-9a-f]{64}\.js$", s) for s in scripts), "search.js not loaded")
    expect(not any("fuse" in s for s in scripts), "Fuse.js must be loaded lazily, not with a script tag")


@check
def search_page(ctx):
    root = ctx.main.html("/search/")
    expect(root.find("form[data-search-page]") is not None, "search page form missing")
    expect(root.find("[data-search-page-results]") is not None, "search page results container missing")
    expect("JavaScript" in root.find("noscript").text(), "no-JS message missing")
    expect(ctx.main.html("/sv/sok/").find("h1").text() == "Sök", "sv search page")


@check
def search_edge_disabled(ctx):
    root = ctx.edge.html("/")
    expect(root.find(".search-toggle") is None and root.find("#search-panel") is None, "search UI must be hidden")
    expect(root.find("script#search-config") is None, "no search config when search is disabled")
    expect(not any("search" in s.attrs["src"] for s in root.select("script[src]")), "no search.js when disabled")
    expect(not ctx.edge.exists("search-index/sv.json"), "no index when search is disabled")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh search`
Expected: FAIL. `search_config_per_language`, `search_index_content`, `search_header_controls` and `search_page` fail (`search config missing`, missing output files). `search_edge_disabled` already passes (nothing renders yet); it guards the `showSearch = false` path once the UI exists.

- [ ] **Step 3: Vendor Fuse.js**

Fuse.js 7.1.0 is the newest release with a UMD "basic" build that sets `window.Fuse` (7.5 ships ES modules only).
```bash
mkdir -p assets/js/vendor
curl -fsSL https://cdn.jsdelivr.net/npm/fuse.js@7.1.0/dist/fuse.basic.min.js -o assets/js/vendor/fuse.basic.min.js
curl -fsSL https://cdn.jsdelivr.net/npm/fuse.js@7.1.0/LICENSE -o assets/js/vendor/fuse.LICENSE.txt
head -c 120 assets/js/vendor/fuse.basic.min.js; echo; grep -c "Apache License" assets/js/vendor/fuse.LICENSE.txt
```
Expected: the file starts with `/**` and ` * Fuse.js v7.1.0`; the license grep prints a number ≥ 1.

- [ ] **Step 4: Create the search partials and layout**

`layouts/_partials/func/search-index.html`:
```html
{{- /* Per-language search index, published as /search-index/<lang>.json.
       Call with partialCached "func/search-index.html" . site.Language.Name */ -}}
{{- $fmt := site.Params.dateFormat | default ":date_long" -}}
{{- $items := slice -}}
{{- range where site.Pages "Kind" "in" (slice "page" "section") -}}
  {{- if not .Params.search_exclude -}}
    {{- $date := "" -}}
    {{- if eq .Type "posts" }}{{ if .IsPage }}{{ $date = .Date | time.Format $fmt }}{{ end }}{{ end -}}
    {{- if and (eq .Type "events") .Params.start }}{{ $date = time.AsTime .Params.start | time.Format $fmt }}{{ end -}}
    {{- $tags := slice -}}
    {{- range .GetTerms "tags" }}{{ $tags = $tags | append .LinkTitle }}{{ end -}}
    {{- $cats := slice -}}
    {{- range .GetTerms "categories" }}{{ $cats = $cats | append .LinkTitle }}{{ end -}}
    {{- $items = $items | append (dict
        "title" .Title
        "url" .RelPermalink
        "section" .Section
        "date" $date
        "tags" $tags
        "categories" $cats
        "summary" (.Params.lead | default .Summary | plainify | htmlUnescape | strings.TrimSpace | truncate 200)
        "content" (.Plain | htmlUnescape | strings.TrimSpace | truncate 1500)
    ) -}}
  {{- end -}}
{{- end -}}
{{- return resources.FromString (printf "search-index/%s.json" site.Language.Name) ($items | jsonify) -}}
```

`layouts/_partials/search-config.html`:
```html
{{- $idx := partialCached "func/search-index.html" . site.Language.Name -}}
{{- $fuse := resources.Get "js/vendor/fuse.basic.min.js" | fingerprint -}}
{{- $page := "" -}}
{{- with site.GetPage "/search" }}{{ $page = .RelPermalink }}{{ end -}}
{{- $cfg := dict
    "index" $idx.RelPermalink
    "fuse" $fuse.RelPermalink
    "fuseIntegrity" $fuse.Data.Integrity
    "page" $page
    "i18n" (dict
      "noResults" (T "searchNoResults")
      "results" (T "searchResultsCount")
      "seeAll" (T "searchSeeAll")
      "error" (T "searchError"))
-}}
<script type="application/json" id="search-config">{{ $cfg | jsonify | safeJS }}</script>
```

`layouts/_partials/search-toggle.html`:
```html
<button class="search-toggle" type="button" aria-expanded="false" aria-controls="search-panel" data-search-toggle>
  {{- partial "icon.html" (dict "name" "search") -}}
  <span class="sr-only">{{ T "search" }}</span>
</button>
```

`layouts/_partials/search-panel.html`:
```html
{{- $action := "" -}}
{{- with site.GetPage "/search" }}{{ $action = .RelPermalink }}{{ end -}}
<div class="search-panel" id="search-panel" hidden>
  <div class="wrap wrap--960">
    <form class="search-form" role="search" method="get"{{ with $action }} action="{{ . }}"{{ end }}>
      <label class="sr-only" for="search-panel-input">{{ T "searchSite" }}</label>
      <input class="search-form__input" id="search-panel-input" type="search" name="q" placeholder="{{ T "searchPlaceholder" }}" autocomplete="off" data-search-input>
      <button class="search-form__submit" type="submit">{{ partial "icon.html" (dict "name" "search") }}<span class="sr-only">{{ T "search" }}</span></button>
    </form>
    <div class="search-results" data-search-results aria-live="polite"></div>
  </div>
</div>
```

`layouts/search.html` (used by pages with `layout: search`):
```html
{{ define "main" }}
{{ partial "banner.html" (dict "page" .) }}
<div class="wrap wrap--960 section">
  <form class="search-form search-form--page" role="search" method="get" action="{{ .RelPermalink }}" data-search-page>
    <label class="sr-only" for="search-page-input">{{ T "searchSite" }}</label>
    <input class="search-form__input" id="search-page-input" type="search" name="q" placeholder="{{ T "searchPlaceholder" }}" autocomplete="off">
    <button class="btn" type="submit">{{ T "search" }}</button>
  </form>
  <noscript><p class="notice notice--warning">{{ T "searchJsRequired" }}</p></noscript>
  <div class="search-results search-results--page" data-search-page-results aria-live="polite"></div>
</div>
{{ end }}
```

In `layouts/_partials/header.html`, replace:
```html
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" data-menu-toggle>
```
with:
```html
    {{- if site.Params.showSearch }}
    {{ partial "search-toggle.html" . }}
    {{- end }}
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" data-menu-toggle>
```
and replace the final:
```html
  </div>
</header>
```
with:
```html
  </div>
  {{- if site.Params.showSearch }}
  {{ partial "search-panel.html" . }}
  {{- end }}
</header>
```

Append to `layouts/_partials/scripts.html`:
```html
{{- if site.Params.showSearch }}
{{ partial "search-config.html" . }}
{{- $search := resources.Get "js/search.js" | minify | fingerprint }}
<script src="{{ $search.RelPermalink }}" integrity="{{ $search.Data.Integrity }}" defer></script>
{{- end }}
```

- [ ] **Step 5: Create search.js and search.css**

`assets/js/search.js`:
```js
/* Client-side search with Fuse.js over the index Hugo builds per language.
   Fuse.js and the index are downloaded on first use only. */
(function () {
  'use strict';

  var cfgEl = document.getElementById('search-config');
  if (!cfgEl) return;
  var cfg = JSON.parse(cfgEl.textContent);
  var fusePromise = null;

  function loadScript(src, integrity) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src;
      if (integrity) s.integrity = integrity;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  function getFuse() {
    if (!fusePromise) {
      fusePromise = Promise.all([
        window.Fuse ? Promise.resolve() : loadScript(cfg.fuse, cfg.fuseIntegrity),
        fetch(cfg.index).then(function (r) {
          if (!r.ok) throw new Error('search index: HTTP ' + r.status);
          return r.json();
        })
      ]).then(function (res) {
        return new window.Fuse(res[1], {
          keys: [
            { name: 'title', weight: 3 },
            { name: 'tags', weight: 2 },
            { name: 'categories', weight: 2 },
            { name: 'summary', weight: 1.5 },
            { name: 'content', weight: 1 }
          ],
          threshold: 0.35,
          ignoreLocation: true,
          minMatchCharLength: 2
        });
      });
      fusePromise.catch(function () { fusePromise = null; }); // allow a retry later
    }
    return fusePromise;
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function render(container, query, results, limit) {
    container.textContent = '';
    if (!query) return;
    if (!results.length) {
      container.appendChild(el('p', 'search-results__empty', cfg.i18n.noResults.replace('{query}', query)));
      return;
    }
    container.appendChild(el('p', 'search-results__count', cfg.i18n.results.replace('{count}', String(results.length))));
    var list = el('ul', 'search-results__list');
    results.slice(0, limit || results.length).forEach(function (r) {
      var item = r.item;
      var li = el('li', 'search-result');
      var a = el('a', 'search-result__title', item.title);
      a.href = item.url;
      li.appendChild(a);
      if (item.date) li.appendChild(el('span', 'search-result__meta', item.date));
      if (item.summary) li.appendChild(el('p', 'search-result__summary', item.summary));
      list.appendChild(li);
    });
    container.appendChild(list);
    if (limit && results.length > limit && cfg.page) {
      var all = el('a', 'search-results__all', cfg.i18n.seeAll);
      all.href = cfg.page + '?q=' + encodeURIComponent(query);
      container.appendChild(all);
    }
  }

  function search(container, query, limit) {
    if (query.length < 2) {
      render(container, '', [], limit);
      return;
    }
    getFuse().then(function (fuse) {
      render(container, query, fuse.search(query), limit);
    }).catch(function () {
      container.textContent = '';
      container.appendChild(el('p', 'search-results__empty', cfg.i18n.error));
    });
  }

  function bindInput(input, container, limit) {
    var timer;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { search(container, input.value.trim(), limit); }, 150);
    });
  }

  // Header search panel
  var toggle = document.querySelector('[data-search-toggle]');
  var panel = document.getElementById('search-panel');
  if (toggle && panel) {
    var input = panel.querySelector('[data-search-input]');
    var results = panel.querySelector('[data-search-results]');
    var setOpen = function (open) {
      toggle.setAttribute('aria-expanded', String(open));
      panel.hidden = !open;
      if (open) {
        input.focus();
        getFuse().catch(function () {});
      }
    };
    toggle.addEventListener('click', function () { setOpen(panel.hidden); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hidden) {
        setOpen(false);
        toggle.focus();
      }
    });
    bindInput(input, results, 8);
    panel.querySelector('form').addEventListener('submit', function (e) {
      if (!cfg.page) e.preventDefault(); // no search page: keep results in the panel
    });
  }

  // Search page
  var pageForm = document.querySelector('[data-search-page]');
  if (pageForm) {
    var pageInput = pageForm.querySelector('input[name="q"]');
    var pageResults = document.querySelector('[data-search-page-results]');
    var initial = (new URLSearchParams(window.location.search).get('q') || '').trim();
    pageInput.value = initial;
    bindInput(pageInput, pageResults, 0);
    pageForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var query = pageInput.value.trim();
      history.replaceState(null, '', '?q=' + encodeURIComponent(query));
      search(pageResults, query, 0);
    });
    if (initial) search(pageResults, initial, 0);
  }
})();
```

`assets/css/search.css`:
```css
/* Header search panel (WP .search-block) and the search page. */
.no-js .search-toggle {
  display: none;
}

.search-panel {
  position: absolute;
  top: 100%;
  right: 0;
  left: 0;
  max-height: calc(100vh - var(--header-height));
  padding: 24px 0 28px;
  overflow-y: auto;
  background: #fff;
  color: var(--isoc-navy);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.search-panel[hidden] {
  display: none;
}

.search-panel :focus-visible {
  outline-color: var(--color-link);
}

.search-form {
  display: flex;
  align-items: center;
  border-bottom: 2px solid var(--isoc-navy);
}

.search-form:focus-within {
  border-bottom-color: var(--color-link);
}

.search-form__input {
  flex: 1;
  min-width: 0;
  padding: 10px 0 6px;
  border: 0;
  background: transparent;
  font-size: 24px;
}

.search-form__input:focus {
  outline: none;
}

.search-form__submit {
  padding: 8px;
  border: 0;
  background: none;
  color: var(--isoc-navy);
  cursor: pointer;
}

.search-form__submit .icon {
  width: 24px;
  height: 24px;
}

.search-results {
  margin-top: 16px;
}

.search-results__count,
.search-result__meta {
  color: var(--isoc-gray);
  font-size: 15px;
}

.search-results__count {
  margin: 0 0 8px;
}

.search-results__list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.search-result {
  margin: 0;
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border);
}

.search-result__title {
  color: var(--color-link);
  font-size: 21px;
  font-weight: 600;
  text-decoration: none;
}

.search-result__meta {
  display: block;
}

.search-result__summary {
  margin: 6px 0 0;
  font-size: 17px;
  line-height: 1.5;
}

.search-results__all {
  display: inline-block;
  margin-top: 16px;
  font-weight: 600;
}

.search-results__empty {
  margin: 0;
}

/* Search page */
.search-form--page {
  gap: 16px;
  margin-bottom: 30px;
  border: 0;
}

.search-form--page .search-form__input {
  padding: 10px 24px 8px;
  border: 1.5px solid var(--isoc-navy);
  border-radius: var(--radius-pill);
  font-size: 20px;
}

.search-form--page .search-form__input:focus {
  border-color: var(--color-link);
  outline: 2px solid var(--color-link);
}

@media (max-width: 599px) {
  .search-form--page {
    flex-direction: column;
    align-items: stretch;
  }
}
```

- [ ] **Step 6: Add the search pages and disable search in the edge fixture**

`exampleSite/content/en/search.md`:
```markdown
---
title: Search
translationKey: search
layout: search
search_exclude: true
---
```

`exampleSite/content/sv/search.md`:
```markdown
---
title: Sök
translationKey: search
layout: search
slug: sok
search_exclude: true
---
```

In `tests/edge/hugo.toml`, replace:
```toml
[params]
  defaultBanner = "green"
```
with:
```toml
[params]
  defaultBanner = "green"
  showSearch = false
```

- [ ] **Step 7: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: every check PASSES, including all `search_*`.

Then try it by hand: `scripts/serve.sh`, open http://localhost:1313/, click the search icon, type `encryption`. Expect live results ("Why end-to-end encryption matters" and the EU response). Press Enter and expect the `/search/?q=encryption` page with full results. Repeat on `/sv/` with `kryptering`. Stop the server.

---

### Task 10: Motion, visual verification and polish

**Files:**
- Create: `assets/css/motion.css`, `scripts/screenshots.sh`
- Modify: `assets/js/menu.js` (reveal-on-scroll)
- Modify (as found during review): any `assets/css/*.css`
- Test: `scripts/checks/motion.py`

**Interfaces:**
- Consumes: `.reveal` class on block wrappers (Task 8), `menu.js` (Task 3).
- Produces: `html.can-reveal` (set by JS only when IntersectionObserver exists and reduced motion is off), `.reveal.is-visible`. `scripts/screenshots.sh [--reference]` writes `.check/screenshots/*.png` (or `.check/reference/*.png`).

- [ ] **Step 1: Write the failing motion checks**

`scripts/checks/motion.py`:
```python
import re

from checklib import check, expect


def _asset(site, pattern):
    root = site.html("/")
    for el in root.select("link[rel=stylesheet]") + root.select("script[src]"):
        url = el.attrs.get("href") or el.attrs.get("src")
        if re.search(pattern, url):
            return open(site.resolve(url, "index.html"), encoding="utf-8").read()
    raise AssertionError(f"no asset matching {pattern}")


@check
def motion_reveal_is_progressive(ctx):
    css = _asset(ctx.main, r"/css/main\.min\.").replace(" ", "")
    expect(".can-reveal.reveal{opacity:0" in css, "reveal styles must be scoped to html.can-reveal")
    expect(not re.search(r"(?<!can-reveal)\.reveal\{opacity:0", css), "unscoped .reveal hiding would blank pages without JS")
    expect("prefers-reduced-motion" in css, "reduced-motion override missing")
    js = _asset(ctx.main, r"/js/menu\.min\.")
    expect("IntersectionObserver" in js and "can-reveal" in js, "menu.js should add the reveal behaviour")
    expect('class="no-js"' in ctx.main.read("index.html"), "html must start with class=no-js")
```

Note on the selector: the minified CSS is `.can-reveal .reveal{…}`. With spaces removed it becomes `.can-reveal.reveal{`, which is what the check looks for.

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh motion`
Expected: FAIL with `reveal styles must be scoped to html.can-reveal`.

- [ ] **Step 3: Add the motion styles and script**

`assets/css/motion.css`:
```css
/* Gentle reveal on scroll, replacing the WP theme's GSAP animations.
   Blocks are hidden only after JS has added html.can-reveal, and never when
   the visitor prefers reduced motion. */
.can-reveal .reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.can-reveal .reveal.is-visible {
  opacity: 1;
  transform: none;
}

@media print {
  .can-reveal .reveal {
    opacity: 1;
    transform: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

In `assets/js/menu.js`, replace the final line:
```js
})();
```
with:
```js

  // Reveal blocks as they scroll into view
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var revealEls = document.querySelectorAll('.reveal');
    if (revealEls.length) {
      document.documentElement.classList.add('can-reveal');
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -10% 0px' });
      revealEls.forEach(function (node) { observer.observe(node); });
    }
  }
})();
```

- [ ] **Step 4: Run the checks to verify they pass**

Run: `scripts/check.sh`
Expected: every check PASSES, including `motion_reveal_is_progressive`.

- [ ] **Step 5: Create the screenshot script**

`scripts/screenshots.sh`:
```bash
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
  shoot "$OUT/$name-mobile.png" 390 "http://localhost:$PORT$path"
done
shoot "$OUT/home-nojs-desktop.png" 1440 "http://localhost:$PORT/" --blink-settings=scriptEnabled=false
shoot "$OUT/home-nojs-mobile.png" 390 "http://localhost:$PORT/" --blink-settings=scriptEnabled=false
ls "$OUT"
```

Run:
```bash
chmod +x scripts/screenshots.sh
scripts/screenshots.sh --reference
scripts/screenshots.sh
```
Expected: `.check/reference/` holds 5 images and `.check/screenshots/` holds 28 PNGs.

- [ ] **Step 6: Review the screenshots against the reference and fix differences**

Open each screenshot next to the matching reference (`theme-screenshot.png` and `theme-home.jpg` for the homepage, `home.png` for pages, `post.png` for posts, `category.png` for lists). Check each item; for each failure, adjust the named CSS file and re-run `scripts/screenshots.sh`:

| # | Area (file) | Acceptance criterion at 1440 px unless noted |
|---|---|---|
| 1 | Header (`header.css`, `nav.css`) | Navy bar ≈126 px tall. Logo's left edge at 80 px (5 % gutter). First menu item ≈70 px right of the logo, items ≈60 px apart, white 18 px semibold. On the right: globe + "EN" + chevron, search icon, white pill "Join" ≈104×44 px with navy text. |
| 2 | Page banner (`hero.css`) | Green: mint pattern, bold dark-blue title ≈52 px whose left edge lines up with the content (130 px). Blue: blue pattern, white title. Lead text 25 px, max ≈800 px wide. |
| 3 | Homepage hero (`hero.css`) | Like `theme-screenshot.png`: ≈500 px tall green pattern, title ≈56 px bold dark blue, tagline 25 px, depth-blue pill button below. |
| 4 | Image + text (`blocks.css`) | Image left, text right, vertically centred, ≈60 px gap, both inside the 1180 px container. |
| 5 | Cards (`cards.css`, `news.css`) | White cards with a soft grey shadow on the `#eff2ec` band. 25 px padding, 16 px date, 25 px blue title. 4 per row in "Latest news" and "Related posts", 3 per row on news lists. |
| 6 | Events (`events.css`) | Date badge: depth blue, white day number ≈36 px. Single event: details box on the right in a light band. |
| 7 | Footer (`footer.css`) | Navy band: centred menu (18 px), white icons, small text, copyright. Hover turns teal. |
| 8 | Mobile, 390 px (all) | Hamburger visible, nothing overflows horizontally, banner title ≈36 px, cards in one column, footer menu stacked. |
| 9 | No JS (`*-nojs-*`) | Every block visible (none blank). On mobile the menu shows in the page flow under the logo. No search icon. |

Then check by hand in `scripts/serve.sh` at about 1000 px width:
- the hamburger opens a full-height navy panel;
- Esc closes it, and focus returns to the button;
- sub-menu chevrons expand in place;
- the language menu opens and closes on click;
- Tab moves through header → content → footer with a visible focus ring everywhere.

- [ ] **Step 7: Re-run the checks after any CSS changes**

Run: `scripts/check.sh`
Expected: every check PASSES.

---

### Task 11: Archetypes, README and demo deployment

**Files:**
- Create: `archetypes/default.md`, `archetypes/posts.md`, `archetypes/events.md`
- Create: `README.md`, `.github/workflows/demo.yml`
- Test: `scripts/checks/docs.py`

**Interfaces:**
- Consumes: everything above (the README documents it).
- Produces: user-facing documentation and CI.

- [ ] **Step 1: Write the failing documentation checks**

`scripts/checks/docs.py`:
```python
import os
import re

from checklib import check, expect

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    path = os.path.join(ROOT, rel)
    expect(os.path.isfile(path), f"{rel} missing")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


@check
def docs_readme_covers_configuration(ctx):
    readme = _read("README.md")
    for needle in ("hugo.toml", "joinURL", "defaultBanner", "params.colors", "blocks:", "registration_url",
                   "translationKey", "layout: search", "scripts/check.sh", "0.158", "timeZone",
                   "{{< image-text", "{{< cta", "custom.css"):
        expect(needle in readme, f"README does not mention {needle!r}")


@check
def docs_archetypes_and_workflow(ctx):
    for name in ("default", "posts", "events"):
        _read(f"archetypes/{name}.md")
    expect("start:" in _read("archetypes/events.md"), "events archetype needs start")
    wf = _read(".github/workflows/demo.yml")
    for needle in ("schedule:", "scripts/check.sh", "actions/deploy-pages", "HUGO_VERSION"):
        expect(needle in wf, f"workflow lacks {needle!r}")


@check
def docs_i18n_files_have_same_keys(ctx):
    en = set(re.findall(r"^(\w+) = ", _read("i18n/en.toml"), re.M))
    sv = set(re.findall(r"^(\w+) = ", _read("i18n/sv.toml"), re.M))
    expect(en == sv, f"i18n key mismatch: only en {sorted(en - sv)}, only sv {sorted(sv - en)}")
```

- [ ] **Step 2: Run the checks to verify they fail**

Run: `scripts/check.sh docs`
Expected: FAIL. `docs_readme_covers_configuration` and `docs_archetypes_and_workflow` fail (`README.md missing`); `docs_i18n_files_have_same_keys` passes.

- [ ] **Step 3: Create the archetypes**

`archetypes/default.md`:
```markdown
---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
# lead: One sentence shown in the banner.
# banner: green   # green | blue | navy | teal | none
draft: true
---
```

`archetypes/posts.md`:
```markdown
---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
categories: []
tags: []
authors: []
# image: cover.jpg          # put the image next to index.md (page bundle) or in assets/
# image_alt: ""
# image_credit: ""
summary: ""
draft: true
---
```

`archetypes/events.md`:
```markdown
---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
# When the event happens. Include the UTC offset, or the site's timeZone is used.
start: {{ .Date }}
# end: 2027-01-21T17:00:00+01:00
# all_day: false
# location: ""
# online: false
# online_url: ""
# registration_url: ""
# registration_closed: false
# organizer: ""
summary: ""
draft: true
---
```

Verify the archetypes render. Hugo is run from a scratch copy so the exampleSite stays untouched:
```bash
tmp="$(mktemp -d)" && cp -R exampleSite "$tmp/site" \
  && hugo new content --source "$tmp/site" --themesDir "$(dirname "$PWD")" --theme "$(basename "$PWD")" events/test-event.md \
  && cat "$tmp/site/content/en/events/test-event.md"; rm -rf "$tmp"
```
Expected: a front matter block with `title: "Test Event"`, a `date:` and `start:` set to now, and the commented keys.

- [ ] **Step 4: Write the README**

`README.md`:
````markdown
# ISOC Chapters: Hugo theme

A [Hugo](https://gohugo.io/) port of the Internet Society's WordPress theme for
chapters ("Internet Chapters", the Genesis child theme shown at
[chapter-template.isoc.org](https://chapter-template.isoc.org/)). It keeps the
ISOC look and drops the server: no WordPress, PHP, database or plugins.

Maintained by [ISOC-SE](https://isoc.se), the Swedish chapter. Other chapters are very welcome to use it.

**Features**

- The chapter look: navy header with Join button, pattern banners, Hind type, ISOC colours.
- Homepage built from blocks (hero, intro, image + text, stats, latest news,
  upcoming events, quote, call to action, gallery), plus the same pieces as shortcodes.
- News with categories, related posts, pagination, a monthly archive and RSS.
- Events with upcoming/past lists and an "Add to calendar" `.ics` file per event.
- Search in the browser (Fuse.js) over an index built with the site.
- English and Swedish built in; any number of languages with a language switcher.
- Nothing to install but Hugo. No Node, npm, Sass or CDN; fonts and scripts are self-hosted.
- Works without JavaScript (except search), keyboard friendly, WCAG 2.1 AA target.

Not included, because a static site can't do it: contact/membership forms,
comments, newsletter sign-up. Link to external services for those, for example
the ISOC registration page used by the Join button.

## Requirements

Hugo **0.158.0 or newer**. The standard edition is enough; "extended" is not needed.

## Quick start

```bash
hugo new site my-chapter && cd my-chapter
git init
git submodule add https://github.com/ISOC-SE/isoc-hugo-theme.git themes/isoc-hugo-theme
cp themes/isoc-hugo-theme/exampleSite/hugo.toml hugo.toml
cp -R themes/isoc-hugo-theme/exampleSite/content .
hugo server
```

Then edit `hugo.toml` and the Markdown files in `content/`.

As a Hugo Module instead (needs Go):

```toml
[module]
  [[module.imports]]
    path = "github.com/ISOC-SE/isoc-hugo-theme"
```

## Configuration

All settings live in your site's `hugo.toml`. Theme defaults are shown.

```toml
baseURL = "https://example.org/"
theme = "isoc-hugo-theme"
timeZone = "Europe/Stockholm"   # used for event times written without an offset

[params]
  chapterName   = ""            # defaults to the site title; used in the copyright line
  description   = ""            # default meta description and homepage hero tagline
  logo          = ""            # path in assets/ (e.g. "images/logo.svg"); default: ISOC Chapters logo
  logoAlt       = ""            # defaults to the site title
  logoWidth     = 233
  joinURL       = "https://community.internetsociety.org/s/new-registration"
  joinLabel     = ""            # defaults to "Join" / "Bli medlem"
  showSearch    = true
  pagerSize     = 9             # cards per news page
  dateFormat    = ":date_long"  # Hugo date format, localised per language
  defaultBanner = "blue"        # green | blue | navy | teal | none
  footerText    = ""            # Markdown shown in the footer
  footerLogo    = ""            # path in assets/
  footerLogoAlt = ""
  copyright     = "© {year} {chapterName}"
  ogImage       = ""            # default social sharing image (path in assets/)

  [params.colors]               # optional overrides of the ISOC defaults
    link   = "#2b72d6"
    accent = "#40b2a4"
    header = "#0c1c2c"
    footer = "#0c1c2c"
    button = "#24366e"

  [[params.social]]             # icons: facebook instagram linkedin x youtube mastodon bluesky github rss email
    name  = "linkedin"
    url   = "https://www.linkedin.com/company/your-chapter/"
    label = "LinkedIn"
```

**Logo.** Use your official chapter logo from the
[ISOC brand guidelines](https://assets.internetsociety.org/guidelines/) (white
version, for the navy header). The bundled "Internet Society Chapters" logo is
only a placeholder.

### Languages

```toml
defaultContentLanguage = "en"

[languages.en]
  contentDir = "content/en"
  locale = "en-GB"
  label = "English"
  title = "Internet Society Chapter"
  weight = 1
[languages.sv]
  contentDir = "content/sv"
  locale = "sv-SE"
  label = "Svenska"
  title = "Internet Society Sverige"
  weight = 2
```

- Pages with the same path in each language are linked as translations
  automatically. If the paths differ (`content/sv/om/` vs `content/en/about/`),
  give both the same `translationKey`.
- Templates find news and events by **type**, not by folder name. Keep the
  folders `posts/` and `events/`, or, for translated folder names, set the type
  in the section's `_index.md`:

  ```yaml
  ---
  title: Nyheter
  type: posts
  cascade:
    type: posts
  ---
  ```

- The theme ships English and Swedish texts. To add a language, copy
  `themes/isoc-hugo-theme/i18n/en.toml` to `i18n/<code>.toml` in your site and
  translate it. To change a text, override just that key in your site's i18n file.
- The language switcher appears automatically when there is more than one language.
- The category taxonomy must keep the name `categories` in every language.

### Menus

```toml
[[languages.en.menus.main]]
  identifier = "about"
  name = "About"
  pageRef = "/about"
  weight = 10
[[languages.en.menus.main]]
  parent = "about"            # dropdown item
  name = "Board"
  pageRef = "/about/board"
  weight = 11

[[languages.en.menus.footer]]
  name = "Privacy policy"
  pageRef = "/privacy"
  weight = 30
```

## Content

### Pages

```yaml
---
title: About us
lead: One sentence shown under the title in the banner.
banner: green          # green | blue | navy | teal | none
banner_image: hero.jpg # optional: your own banner background
toc: true              # optional table of contents
description: Meta description (defaults to the summary).
---
```

Links in Markdown may use content paths, `[contact us](/contact)`. They are
turned into the right URL for the page's language.

### News posts (`content/<lang>/posts/`)

```yaml
---
title: Annual general meeting 2026
date: 2026-02-11T10:00:00+01:00
categories: [Community]
tags: [meetings]
authors: [The Board]
image: cover.jpg            # page bundle file or assets/ path
image_alt: ""
image_credit: ISOC Chapter, CC BY 4.0
summary: Shown on cards, in search results and in social previews.
---
```

For a monthly archive, add a page with `layout: archive`.

### Events (`content/<lang>/events/`)

```yaml
---
title: SamNet 5 conference
date: 2026-09-01             # publish date
start: 2027-01-21T09:00:00+01:00
end: 2027-01-21T17:00:00+01:00
all_day: false
location: Internetstiftelsen, Hammarby kaj 10D, Stockholm
online: false
online_url: ""
registration_url: https://example.com/register
registration_closed: false
organizer: SamNet
summary: A full day about technology and the Internet.
---
```

- `start` is required. Without a UTC offset, times are read in the site's `timeZone`.
- Each event gets an `event.ics` file for calendars.
- "Upcoming" and "past" are decided **when the site is built**. Rebuild the
  site at least daily (the included GitHub workflow does) so finished events move to "past".

### Homepage blocks (`content/<lang>/_index.md`)

```yaml
---
title: Home
blocks:
  - type: hero
    title: Internet Society Chapter
    tagline: A short sentence about who you are.
    banner: green                 # green | blue | navy | teal
    buttons:
      - label: Get involved
        url: /membership          # content paths work in every language
        style: primary            # primary | secondary | white
  - type: intro
    text: Large blue introduction text (Markdown).
  - type: image_text
    image: images/home/section.jpg
    image_alt: ""
    image_side: left              # left | right
    ratio: 50-50                  # 50-50 | 30-70 | 70-30
    text: Markdown text.
    buttons: [{label: About us, url: /about}]
  - type: stats
    background: navy              # white | light | green | navy | blue
    items: [{value: "120+", label: Chapters worldwide}]
  - type: latest_posts
    title: Latest news
    count: 4
  - type: upcoming_events
    title: Upcoming events
    count: 3
    empty_text: Nothing planned right now.   # omit to hide the block when empty
  - type: quote
    text: The Internet is for everyone.
    author: Internet Society
  - type: cta
    title: Become a member
    text: Membership is free.
    button: {label: Join us, url: "https://community.internetsociety.org/s/new-registration"}
  - type: gallery
    images: [{src: images/home/gallery-1.jpg, alt: ""}]
  - type: markdown                # where the Markdown body of _index.md appears
---
```

Unknown block types are skipped with a build warning.

### Shortcodes

```markdown
{{< button url="/membership" style="secondary" >}}Become a member{{< /button >}}

{{< notice type="warning" >}}Registration closes on **Friday**.{{< /notice >}}

{{< image-text image="photo.jpg" alt="…" side="right" ratio="30-70" >}}
Markdown text next to the image.
{{< /image-text >}}

{{< quote author="Internet Society" role="Mission statement" >}}The Internet is for everyone.{{< /quote >}}

{{< stats >}}
{{< stat value="120+" label="Chapters worldwide" >}}
{{< /stats >}}

{{< columns >}}
{{< column >}}First column (Markdown){{< /column >}}
{{< column >}}Second column{{< /column >}}
{{< /columns >}}

{{< gallery >}}                  <!-- images in this page bundle; match="photos/*" to filter -->
{{< latest-posts count="4" >}}
{{< upcoming-events count="3" >}}

{{< cta title="Join the chapter" url="/membership" label="Become a member" background="navy" >}}
Membership is free.
{{< /cta >}}
```

Put block shortcodes on their own line with blank lines around them, and don't
indent the content inside them.

### Search

Search needs a page with `layout: search` at `content/<lang>/search.md`:

```yaml
---
title: Search
layout: search
search_exclude: true
---
```

To keep any page out of search results, add `search_exclude: true`. To remove
search entirely, set `showSearch = false`.

## Customising

- **Colours:** `[params.colors]` (above).
- **Extra CSS:** create `assets/css/custom.css` in your site; it is loaded last.
- **Templates:** copy any file from `themes/isoc-hugo-theme/layouts/` to the same
  path under your site's `layouts/` and edit it. For example,
  `layouts/_partials/footer.html` overrides the footer.
- **Icons:** add `assets/images/social/<name>.svg` (using `fill="currentColor"`)
  and use that name in `[[params.social]]`.

## Deployment

`hugo --minify` writes the site to `public/`; upload it anywhere that serves static files.

**GitHub Pages:** see `.github/workflows/demo.yml` in this repository. It
builds the demo site on every push and every night (`schedule:`), so event
lists stay current. Copy it and replace the `exampleSite` paths with your site.

## Development

```bash
scripts/serve.sh          # live-reloading demo site at http://localhost:1313/
scripts/check.sh          # strict builds + output assertions (needs python3)
scripts/check.sh events   # only checks whose name contains "events"
scripts/screenshots.sh    # screenshots for visual review (needs Google Chrome)
python3 scripts/fetch-fonts.py   # re-download the Hind font files
```

`scripts/check.sh` builds `exampleSite/` with `--panicOnWarning` (any warning,
missing translation or deprecated API fails) and the edge-case fixture
`tests/edge/` (single language, served from a sub-path, deliberately invalid
values). It then runs the assertions in `scripts/checks/`.

| Path | What it is |
|---|---|
| `layouts/` | Templates (`_partials/blocks/` = homepage blocks, `_shortcodes/`, `_markup/` render hooks) |
| `assets/css/` | One stylesheet per component, bundled in order by `_partials/head/css.html` |
| `assets/js/` | `menu.js`, `search.js`, vendored Fuse.js |
| `i18n/` | Theme texts (en, sv) |
| `exampleSite/` | Demo content in English and Swedish |
| `tests/edge/` | Edge-case fixture site |

## Credits and licences

- Design: the Internet Society's
  [chapter WordPress theme](https://github.com/InternetSociety/genesis-child-chapters)
  (Genesis child theme by StudioPress, GPL-2.0-or-later). Pattern images and the
  quote mark come from that theme.
- This theme: GPL-2.0-or-later (see `LICENSE`).
- Hind font: Indian Type Foundry, SIL Open Font License 1.1 (`static/fonts/hind/OFL.txt`).
- Fuse.js: Kiro Risk, Apache-2.0 (`assets/js/vendor/fuse.LICENSE.txt`).
- Social icons: Font Awesome 4 shapes from the original theme; Mastodon, Bluesky
  and GitHub from [Simple Icons](https://simpleicons.org/) (CC0).
- "Internet Society" and the ISOC logos are trademarks of the Internet Society.
````

- [ ] **Step 5: Create the demo workflow**

`.github/workflows/demo.yml`:
```yaml
name: Demo site

on:
  push:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: "15 3 * * *" # nightly rebuild keeps "upcoming events" correct

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

env:
  HUGO_VERSION: "0.167.0"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Hugo
        run: |
          curl -fsSL -o "$RUNNER_TEMP/hugo.deb" \
            "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.deb"
          sudo dpkg -i "$RUNNER_TEMP/hugo.deb"
          hugo version

      - name: Check theme
        run: scripts/check.sh

      - name: Configure Pages
        id: pages
        uses: actions/configure-pages@v5

      - name: Build demo
        run: |
          hugo --source exampleSite --minify \
            --themesDir "$(dirname "$GITHUB_WORKSPACE")" --theme "$(basename "$GITHUB_WORKSPACE")" \
            --baseURL "${{ steps.pages.outputs.base_url }}/"

      - uses: actions/upload-pages-artifact@v3
        with:
          path: exampleSite/public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 6: Run the full verification**

Run: `scripts/check.sh`
Expected: every check in `core, head, header, footer, pages, posts, events, home, search, motion, docs` PASSES; the summary line reads `N passed, 0 failed`.

Run: `git status --short`
Expected: the new theme files show as untracked or modified. Nothing has been committed (user instruction).


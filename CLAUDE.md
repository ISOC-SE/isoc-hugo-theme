# CLAUDE.md

Hugo theme that ports the Internet Society chapter WordPress theme ("Internet
Chapters", Genesis child theme) to a static site. Maintained by ISOC-SE. The
**repo root is the theme root**; `exampleSite/` is the bilingual (en/sv) demo
and doubles as the main test fixture. License GPL-2.0-or-later.

`README.md` is the user-facing reference (config keys, front matter, blocks,
shortcodes). The design spec and implementation plan in `docs/superpowers/`
explain the *why*, but are partly stale (e.g. the spec's "index.ics" is
`event.ics` in the code); trust code + README over them.

## Commands

```bash
scripts/serve.sh                 # hugo server for exampleSite at http://localhost:1313/
scripts/check.sh                 # full verification (run before calling anything done)
scripts/check.sh events          # only checks whose function name contains "events"
scripts/check.sh browser         # only the headless-Chrome checks
CHECK_CLOCK=2030-01-01T00:00:00Z scripts/check.sh   # build + check "as of" another time
scripts/screenshots.sh           # PNGs to .check/screenshots/ for visual review
```

Requirements: `hugo` ≥ 0.158 (standard edition; CI pins 0.167.0, see
`.github/workflows/demo.yml`), Python 3 (stdlib only, used only by scripts),
Google Chrome/Chromium for browser checks and screenshots (skipped if absent).
There is no Node/npm/Sass, and none may be added.

The scripts use `--themesDir <parent of repo> --theme <repo dir name>`, so the
checkout's parent directory acts as the themes dir. All build output goes to
`.check/` (gitignored).

## What `scripts/check.sh` does

1. Builds `exampleSite/` **strictly** (`--panicOnWarning --printI18nWarnings
   --printPathWarnings`): any `warnf`, missing i18n key or deprecated Hugo API
   fails the build. Then builds it again under `/isoc-hugo-theme/` (GitHub
   Pages sub-path).
2. Builds `tests/edge/` (single language `sv`, sub-path base URL, search off,
   no menus, deliberately invalid values like unknown block type / banner).
   Warnings are *expected* here and captured in `.check/edge.log`; checks
   assert on them.
3. Builds `tests/crowded/` (ISOC-SE's real six-item Swedish menu) for
   header-fit browser checks.
4. Runs `scripts/check_site.py`, which loads every `scripts/checks/*.py`.
   Each `@check`-decorated function gets `ctx` with `ctx.main`, `ctx.main_sub`,
   `ctx.edge` (`checklib.Site` objects: `.html(rel)` → tiny DOM with
   `.select()/.find()` supporting tag/.class/#id/[attr=val] and descendant
   selectors, `.json()`, `.read()`, `.broken_links()`, `.log`) and `ctx.now`.
5. Runs `scripts/check_browser.py` (iframe harness in headless Chrome:
   header layout at several widths, menus, dropdowns, search).

When adding a feature: add assertions to the matching `scripts/checks/<area>.py`
(name the function `<area>_...` so the filter works), add demo content in
**both** `exampleSite/content/en` and `content/sv`, and an edge case in
`tests/edge/` if relevant.

Hidden coupling: `checks/docs.py` asserts that README mentions specific
strings (`joinURL`, `defaultBanner`, `{{< image-text`, `custom.css`, ...) and
that the workflow contains `schedule:`, `scripts/check.sh`, `HUGO_VERSION`.
Keep those when editing docs/CI.

## Architecture

- **Hugo ≥0.146 template layout**: `layouts/_partials/`, `layouts/_shortcodes/`,
  `layouts/_markup/` (render hooks), top-level `baseof/home/single/list/
  taxonomy/term/404/search/archive.html`, plus `posts/` and `events/` overrides.
- **Content is selected by `.Type`** (`"posts"`, `"events"`), never by
  directory name. Translated section folders (`sv/nyheter`, `sv/evenemang`)
  set `type` + `cascade: {type: ...}` in their `_index.md`.
- **Theme config only supplies `[params]` and `[module]`** (Hugo does not
  merge `outputs`/`pagination`/`markup` from a theme). Hence:
  - search index (`search-index/<lang>.json`) and per-event `event.ics` are
    generated with `resources.FromString`, not output formats;
  - pagination uses `.Paginate ... (site.Params.pagerSize | default 9)`.
- **"Returning" partials** live in `_partials/func/` and end in `return`
  (e.g. `func/url.html`, `func/resource.html`, `func/events.html`,
  `func/event-dates.html`, `func/banner-variant.html`). Expensive per-language
  ones are called via `partialCached ... site.Language.Name`.
- **Homepage** (`home.html`) renders `.Params.blocks` in order via
  `_partials/blocks/<type>.html` (`templates.Exists` check; unknown type →
  `warnf` and skip). Blocks and shortcodes share partials (`image-text.html`,
  `quote.html`, `stats.html`, `cta.html`, `gallery.html`,
  `latest-posts-grid.html`, `upcoming-events-grid.html`) so they look identical.
  New block = new `_partials/blocks/<type>.html` + README + example + check.
- **URLs must survive a sub-path base URL.** Front-matter/config links go
  through `func/url.html` (content path → current language's page; other
  root-relative paths → `relURL` after trimming the leading `/`). Markdown
  links go through `_markup/render-link.html`. Images through `img.html` /
  `func/resource.html` (page resource first, then `assets/`). Never emit a raw
  `"/..."` path.
- **Events**: `start` is required (`errorf` otherwise). Times without offset
  are read in the site's `timeZone`. Upcoming/past is computed at **build
  time** (`now`), which is why CI rebuilds nightly and checks follow
  `CHECK_CLOCK`. All-day events are past only after their last day.
- **Invalid values** (banner, image-text side/ratio, missing image/icon) log a
  `warnf` naming the page and fall back; they must not fail the build.
- **CSS**: plain CSS, one file per component in `assets/css/`, concatenated in
  the fixed order listed in `_partials/head/css.html`, then minified +
  fingerprinted with SRI. A new stylesheet must be added to that list.
  `compact.css` (hamburger layout) is written with `.nav-compact ` selectors
  and is emitted twice: wrapped in `@media (max-width: 1179px)` with the prefix
  stripped, and as-is for wide screens where `menu.js` adds `html.nav-compact`
  because the menu doesn't fit. Tokens in `tokens.css`; `params.colors`
  overrides become inline `--color-*` vars. A site's `assets/css/custom.css`
  is loaded last.
- **JS**: vanilla ES5-ish IIFEs, progressive enhancement only. `menu.js`
  (mobile menu, compact detection, dropdowns, scrolled header, reveal
  animation). `search.js` reads `<script id="search-config">` JSON and lazily
  loads the vendored `vendor/fuse.basic.min.js` (Fuse 7.1.0) + index on first
  use. `<html>` starts as `no-js`, swapped to `js` inline in `head.html`.
- **i18n**: every user-visible template string goes through `T` and must
  exist in both `i18n/en.toml` and `i18n/sv.toml` (a check compares key sets).
- **Fonts**: Hind self-hosted in `static/fonts/hind/` (refetch with
  `scripts/fetch-fonts.py`). No CDN requests at runtime (GDPR).

## Rules and gotchas

- Never use deprecated Hugo APIs; deprecation warnings fail the strict build.
  Use `hugo.Sites`, `.Language.Label`, `.Language.Locale`,
  `.Language.Direction`, config keys `locale`/`label`. Not `site.Languages`,
  `.Sites`, `.Language.LanguageName`, `.Language.LanguageCode`,
  `languageCode`, `languageName`.
- The site must work without JavaScript (except search) and target WCAG 2.1
  AA. Teal `#40b2a4` is never a background behind white text.
- Brand colours/values come from the original theme's SCSS; see
  `assets/css/tokens.css` and the plan's "Global Constraints".
- The language switcher links to a page's translation, else that language's
  homepage (exampleSite `/shortcodes/` is English-only to test this).
- `genesis/` and `genesis-child-chapters-main/` (the original WordPress
  themes) may exist locally as read-only reference; they are gitignored and
  must not be modified or committed.
- The plan's "never run git commit" was an instruction for the initial build;
  follow the user's current instructions on committing.

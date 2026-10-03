# ISOC Chapters Hugo Theme — Design Spec

- **Date:** 2026-10-02
- **Status:** Approved in conversation, awaiting written-spec review
- **Owner:** ISOC-SE (Swedish Chapter of the Internet Society)

## 1. Goal

Port the Internet Society chapter WordPress theme (Genesis child theme
"Internet Chapters", reference copy in `genesis-child-chapters-main/`) to a
reusable **Hugo theme** that looks like the original but needs no WordPress,
no PHP and no server-side runtime.

Success means:

1. A chapter can create a Hugo site, add this theme, edit a config file and
   Markdown, and get a site that is visually recognisable as the ISOC chapter
   theme (compare `genesis-child-chapters-main/screenshot.png` and
   chapter-template.isoc.org).
2. Building requires **only the `hugo` binary** (no Node, npm, Sass or
   PostCSS).
3. The theme is multilingual-ready (English + Swedish shipped).
4. An `exampleSite/` demonstrates every layout, block and shortcode in both
   languages and builds without warnings.

### What the user said vs. what is assumed

| Said by user | Assumed / decided in brainstorming |
|---|---|
| Port the ISOC chapter Genesis theme to Hugo, look similar | Visual fidelity target is the theme screenshot + chapter-template.isoc.org, not pixel-perfect |
| Use isoc.se for inspiration | isoc.se runs an older, different theme; we borrow its *structure* (news-first, Swedish, sub-menus, monthly archive, sidebar blurbs) not its look |
| Skip interactive things that cannot work statically (forms) | Comments, forms, share widgets, sliders, video header, WooCommerce, Events Calendar plugin are dropped |
| Theme + demo site; migration later | Migrating isoc.se content is a separate future project in the site repo |
| Multilingual-ready | en + sv i18n; language switcher only when >1 language |
| Fuse.js search | Client-side search over a Hugo-generated JSON index |
| Static events | `events` content type; upcoming/past computed at build time |
| Plain CSS, Hugo only | Rewrite styling with the original's tokens; vanilla JS |
| Do not commit anything at any stage | All files are left uncommitted for the user to review |

## 2. Non-goals

- Migrating content from isoc.se (separate project).
- Any server-side or third-party interactive feature: contact/membership
  forms, comments, newsletter signup, share buttons, analytics.
- Carousels/sliders (replaced by a static gallery grid), video hero.
- Pixel-perfect reproduction of WordPress block markup or Genesis class names.
- A CMS/admin UI. (Decap/Sveltia CMS could be added later; out of scope.)

## 3. Constraints

- **Hugo ≥ 0.158.0**: new template system (`layouts/_partials`,
  `layouts/_shortcodes`, `layouts/_markup`, top-level `home.html`,
  `single.html`, `list.html`) plus the 0.156–0.158 APIs `hugo.Sites`,
  `.Language.Label`, `.Language.Locale` and the `locale`/`label` language
  config keys. Their predecessors (`site.Languages`, `.Sites`,
  `.Language.LanguageName`, `.Language.LanguageCode`, `languageCode`) are
  deprecated and must not be used, because deprecation warnings fail the
  strict build. Developed and verified on Hugo 0.167.0. Standard
  (non-extended) Hugo is sufficient.
- No build dependencies beyond Hugo. Third-party JS (Fuse.js) is vendored
  into `assets/js/vendor/`; fonts are self-hosted. No CDN requests at
  runtime (GDPR-friendly for EU chapters).
- Works with JavaScript disabled, except search (graceful message).
- WCAG 2.1 AA as the accessibility target.
- **License:** GPL-2.0-or-later, matching the original theme from which
  images and design values are derived. Hind font: SIL OFL 1.1. Fuse.js:
  Apache-2.0. License files included.
- The reference directories `genesis/` and `genesis-child-chapters-main/`
  stay in place, untouched; they are not part of the theme.

## 4. Repository layout

```
isoc-hugo-theme/                 (repo root = theme root)
├── hugo.toml                    # theme defaults: module.hugoVersion, outputs, params defaults
├── theme.toml                   # name, description, license, min_version, demosite
├── LICENSE, README.md
├── archetypes/
│   ├── default.md, posts.md, events.md
├── assets/
│   ├── css/
│   │   ├── tokens.css           # colours, type scale, spacing, widths, radii, shadows
│   │   ├── base.css             # reset/normalize, typography, links, buttons, forms, tables
│   │   ├── layout.css           # containers (wrap/inner/narrow), grid helpers, skip link
│   │   ├── header.css           # fixed navy header, logo, right-hand tools, Join button
│   │   ├── nav.css              # desktop menu + dropdowns, mobile off-canvas menu
│   │   ├── hero.css             # page banners & homepage hero, pattern variants
│   │   ├── content.css          # prose (.entry-content), figures, captions, quotes
│   │   ├── cards.css            # post cards, event cards, related posts, pagination
│   │   ├── blocks.css           # homepage blocks + shortcodes
│   │   ├── events.css           # event details box, upcoming/past lists
│   │   ├── search.css           # header search panel, search page results
│   │   ├── footer.css           # footer menu, social icons, copyright
│   │   └── motion.css           # fade-in (respects prefers-reduced-motion)
│   ├── js/
│   │   ├── menu.js              # mobile toggle, dropdown keyboard/tap support
│   │   ├── search.js            # search panel + Fuse.js querying + results rendering
│   │   └── vendor/fuse.min.js   # Fuse.js 7.x (basic build), vendored
│   └── images/
│       ├── patterns/            # green-header.jpg, blue-header.jpg, green-hero.jpg,
│       │                        # green-section.jpg, green-medium.jpg (from WP theme)
│       ├── logo-isoc-chapters.svg   # default header logo (white)
│       ├── quote.svg, arrow.svg, search.svg, globe.svg, chevron.svg
│       └── social/              # facebook, instagram, linkedin, x, youtube, rss,
│                                # mastodon, bluesky, github, email (SVG, currentColor)
├── static/fonts/hind/           # Hind 300/400/500/600/700 woff2 + OFL.txt
├── i18n/en.toml, sv.toml
├── layouts/
│   ├── baseof.html
│   ├── home.html                # renders front-matter blocks
│   ├── single.html              # generic page
│   ├── list.html                # generic section list (cards)
│   ├── taxonomy.html, term.html # categories/tags
│   ├── 404.html
│   ├── search.html              # layout for the /search/ page
│   ├── archive.html             # layout for the monthly archive page
│   ├── posts/single.html, posts/list.html
│   ├── events/single.html, events/list.html
│   ├── _partials/
│   │   ├── head.html, head/css.html, head/js.html, head/meta.html
│   │   ├── header.html, nav-menu.html, lang-switch.html, search-panel.html
│   │   ├── banner.html          # page/section banner (pattern or image)
│   │   ├── footer.html, social-links.html
│   │   ├── card-post.html, card-event.html, pagination.html
│   │   ├── related-posts.html, post-meta.html, event-details.html
│   │   ├── icon.html            # inline SVG helper
│   │   ├── func/                # returning partials: search-index (JSON resource),
│   │   │                        # event-ics (ICS resource), upcoming/past event lists,
│   │   │                        # banner-image, image resolver
│   │   └── blocks/              # hero, intro, latest_posts, upcoming_events,
│   │                            # image_text, stats, quote, cta, gallery, markdown
│   ├── _shortcodes/
│   │   ├── button.html, cta.html, image-text.html, quote.html, stats.html,
│   │   ├── stat.html, columns.html, column.html, gallery.html,
│   │   ├── latest-posts.html, upcoming-events.html, notice.html
│   └── _markup/
│       ├── render-image.html    # responsive images (page resources), lazy loading
│       └── render-link.html     # content-path links per language; rel="noopener" on external
├── exampleSite/
│   ├── hugo.toml                # full demo config (en + sv, menus, params)
│   ├── content/en/…, content/sv/…
│   └── assets/images/…          # demo images
├── .github/workflows/demo.yml   # build exampleSite, deploy to GitHub Pages
└── docs/superpowers/…           # this spec + implementation plan
```

## 5. Configuration (site `hugo.toml`)

The theme ships defaults in its own `hugo.toml`; sites override them.

```toml
[params]
  chapterName   = "Internet Society Sweden Chapter"   # used in titles, footer, alt text
  description   = "…"                                  # default meta description
  logo          = "images/logo.svg"     # assets/ path; default = ISOC Chapters white logo
  logoAlt       = ""                    # default: chapterName
  logoWidth     = 233                   # px, matches WP theme custom-logo default
  joinURL       = "https://community.internetsociety.org/s/new-registration"
  joinLabel     = ""                    # default: i18n "join"
  showSearch    = true
  pagerSize     = 9                     # cards per list page
  dateFormat    = ":date_long"          # localised via language `locale`
  defaultBanner = "blue"                # banner pattern when page sets none
  footerText    = ""                    # optional Markdown under footer menu
  copyright     = "© {year} {chapterName}"  # {year} replaced at build time
  footerLogo    = ""                    # optional (e.g. ISOC logo) above copyright

  [params.colors]                       # optional overrides → CSS custom properties
    link   = "#2B72D6"
    accent = "#40B2A4"
    header = "#0c1c2c"

  [[params.social]]
    name = "linkedin"                   # selects icon from assets/images/social
    url  = "https://www.linkedin.com/company/isoc-se/"
    label = "LinkedIn"                  # accessible name

[menus]
  [[menus.main]]    # header menu; nested via `parent`/`identifier`
  [[menus.footer]]  # footer menu, flat
```

Verified on Hugo 0.167: a theme's `hugo.toml` **does** supply `params`
(and menus) defaults, but **not** `outputs`, `pagination` or `markup`.
The theme is therefore designed to need no site-level config beyond
`params`, menus and languages:

- the search index and `.ics` files are generated with
  `resources.FromString` (no custom output formats);
- list pagination size comes from `params.pagerSize` (default 9) passed to
  `.Paginate`;
- Hugo's defaults already provide `categories`/`tags` taxonomies, RSS,
  related-content config, and `unsafe = false`.

The theme's `hugo.toml` contains `[module.hugoVersion] min = "0.158.0"` and
`[params]` defaults only.

## 6. Content model

### 6.1 Pages (any section without a specific type)

Front matter:

| Key | Type | Purpose |
|---|---|---|
| `title` | string | Banner heading, `<title>` |
| `lead` | string | Large intro line shown in banner |
| `banner` | `green` \| `blue` \| `navy` \| `teal` \| `none` | Pattern variant; default `params.defaultBanner` |
| `banner_image` | string | Page resource or `assets/` path; overrides pattern |
| `toc` | bool | Optional table of contents |
| `description` | string | Meta description |

`green` uses the light green pattern with dark-blue (`#24366E`) heading
text (as on the template site's homepage); `blue` uses the blue pattern with
white text (as on the template's post and category pages). `navy` and `teal`
are solid brand colours with a translucent inline-SVG rounded-rectangle
motif imitating the pattern, white text. Banner min-height 400px desktop,
reduced on mobile.

### 6.2 Posts (type `posts`)

Section directory is `content/<lang>/posts/` by default. Sites may use any
directory name (e.g. `nyheter`) by setting `cascade: {type: posts}` in that
section's `_index.md`. Templates key on **type**, not directory name.

Front matter: `title`, `date`, `categories`, `tags`, `authors` (list of
strings), `image` (featured image, page resource), `image_alt`,
`image_credit` (rendered as "Image copyright: …" caption, as in WP theme),
`summary`, `lead`, `banner`.

- **Single post:** blue banner containing category links, title, date and
  authors; featured image + credit; Markdown body; "Related posts" row of up
  to 4 cards (Hugo `.Related`) on a light green (`#eff2ec`) band.
- **Post list / category / tag pages:** banner + grid of post cards (3 per
  row desktop, 2 tablet, 1 mobile), paginated. Card = optional thumbnail,
  date, title (whole card clickable), category labels, white background,
  soft shadow (`0 0 22px rgba(201,205,208,.6)`, stronger on hover).
- **Monthly archive:** a page with `layout: archive` lists all posts grouped
  by year → month (replaces isoc.se's archive dropdown).
- RSS feed per section and per taxonomy term.

### 6.3 Events (type `events`)

Hugo excludes future-dated content by default, so an event's *publish*
date (`date`) is separate from when it happens:

| Key | Type | Purpose |
|---|---|---|
| `title` | string | |
| `date` | datetime | Publish date (normally ≤ today) |
| `start` | datetime (with TZ offset) | **Required.** Event start |
| `end` | datetime | Optional end |
| `all_day` | bool | Hide times |
| `location` | string | Venue name/address |
| `online` | bool | Shows "Online" label |
| `online_url` | string | Optional meeting link |
| `registration_url` | string | "Register" button |
| `registration_closed` | bool | Shows "Registration closed" instead |
| `organizer` | string | Optional |
| `summary`, `image`, `banner`, `categories` | | As posts |

- **Event list page:** "Upcoming" (not yet ended at build time, ascending) and
  "Past" (descending, all listed). Event card shows
  a date badge (day + abbreviated month), title, time range, location/online.
- **Single event:** banner with title + date; details box (date/time range,
  location, online link, organizer, register button or "registration closed",
  "Add to calendar" `.ics` link); body; if the event has passed, a notice
  "This event has already taken place."
- **.ics:** each event page publishes `<event-url>/event.ics`, built from a
  template string with `resources.FromString`, so sites need no
  output-format config (verified on 0.167, both languages). Valid RFC 5545 (`VCALENDAR`/`VEVENT`, `UID`, `DTSTAMP`,
  `DTSTART`, `DTEND`, `SUMMARY`, `LOCATION`, `URL`, `DESCRIPTION`), CRLF line
  endings, UTC timestamps.
- README documents that "upcoming" is evaluated at build time and recommends
  a scheduled daily rebuild (example cron in the GitHub workflow).

### 6.4 Homepage (`content/<lang>/_index.md`)

The homepage body is assembled from a `blocks:` list in front matter. Each
block has a `type` and type-specific keys; unknown types emit a build warning
(`warnf`) and are skipped. Blocks render in order. An optional Markdown body is
rendered where a `{type: markdown}` block appears, or at the end if none.

| Block `type` | Keys | Renders |
|---|---|---|
| `hero` | `title`, `tagline`, `buttons[] {label,url,style}`, `banner`, `image` | Large pattern hero, ~500px tall (WP `.header-no-video`), heading max-width 880px. Matches `screenshot.png` |
| `intro` | `text` (Markdown) | Large blue lead paragraph in narrow container |
| `latest_posts` | `title`, `count` (default 4), `section`, `more_label`, `more_url` | Row of post cards on light-green band + "More news" button |
| `upcoming_events` | `title`, `count` (default 3), `empty_text` | Event cards; hidden or `empty_text` when none |
| `image_text` | `image`, `image_alt`, `text` (Markdown), `buttons[]`, `image_side` (`left`/`right`), `ratio` (`50-50`/`30-70`/`70-30`), `background` | Two-column split (WP `.col-with-left-img`, `.section-30-70`) |
| `stats` | `title`, `items[] {value,label}`, `background` | Impact numbers row |
| `quote` | `text`, `author`, `role` | Quote with ISOC parenthesis quote icon |
| `cta` | `title`, `text`, `button {label,url}`, `background` | Full-width coloured band |
| `gallery` | `title`, `images[] {src,alt,caption}` | Static responsive grid (replaces slick slider) |
| `markdown` | — | Page body content |

`background` accepts `white`, `light` (`#eff2ec`), `green` (`#D0E6DA`),
`navy`, `blue`.

### 6.5 Shortcodes (for any Markdown page)

Same visual vocabulary as blocks:

- `{{< button url="…" style="primary|secondary|white" >}}Label{{< /button >}}`
- `{{< cta title="…" url="…" label="…" >}}text{{< /cta >}}`
- `{{< image-text image="…" alt="…" side="left" ratio="50-50" >}}Markdown{{< /image-text >}}`
- `{{< quote author="…" role="…" >}}text{{< /quote >}}`
- `{{< stats >}}{{< stat value="100 000+" label="Members" >}}…{{< /stats >}}`
- `{{< columns >}}{{< column >}}…{{< /column >}}{{< /columns >}}`
- `{{< gallery >}}` renders the page bundle's images (optionally `match="glob"`) as a grid
- `{{< latest-posts count="4" >}}`, `{{< upcoming-events count="3" >}}`
- `{{< notice type="info|warning" >}}…{{< /notice >}}`

Shortcodes and blocks share partials, so they look the same.

## 7. Visual system

All values come from `genesis-child-chapters-main/scss/_variables.scss` and
the SCSS partials.

### 7.1 Tokens (`tokens.css`)

```css
:root {
  --isoc-navy: #0c1c2c;        /* $ground-navy / $dark-blue — header, footer */
  --isoc-blue: #2B72D6;        /* $link / $blue-titles */
  --isoc-bright-blue: #1D69D3; /* $isoc-blue */
  --isoc-light-blue: #3A82E4;
  --isoc-depth-blue: #24366E;  /* buttons, dark headings */
  --isoc-teal: #40B2A4;        /* accent, hover */
  --isoc-depth-green: #085856;
  --isoc-depth-teal: #143E50;
  --isoc-purple: #7E245C;
  --isoc-orange: #D25238;
  --isoc-yellow: #EECA4A;
  --isoc-neutral-white: #eff2ec;
  --isoc-neutral-green: #D0E6DA;
  --isoc-putty: #DEDAD0;

  --color-text: var(--isoc-navy); /* body text per original (_common.scss) */
  --color-link: var(--isoc-blue);
  --color-accent: var(--isoc-teal);
  --color-header: var(--isoc-navy);
  --color-button: var(--isoc-depth-blue);

  --font-sans: "Hind", system-ui, sans-serif;
  --radius-pill: 24px;
  --shadow-card: 0 0 22px 0 rgba(201,205,208,.6);
  --shadow-card-hover: 0 0 22px 0 rgba(201,205,208,1);
  --wrap: 1280px; --wrap-1180: 1180px; --wrap-960: 960px; --wrap-800: 800px;
  --wrap-max: 90%;
  --transition: all .3s ease;
  --bp-menu: 1180px;           /* reference only; media queries use literal */
}
```

Colour overrides from `params.colors` are emitted as an inline `<style>`
block redefining `--color-link`, `--color-accent`, `--color-header`.

### 7.2 Typography

Hind, self-hosted woff2, `font-display: swap`, weights 300/400/500/600/700.
Body 18px/1.55. Headings bold, H1 in banners ~56px desktop (scales down with
`clamp()`), dark-blue on light banners, white on dark. Lead/intro text
~32px, blue, weight 400 (as on template homepage).

### 7.3 Components

- **Header:** navy, fixed at top (original `position: fixed`), wrap 1280px /
  90%. Left: logo (max 233×47 default). Middle: main menu, 18px weight 600
  white, teal on hover/focus/current. Right: language switcher (globe icon +
  code + chevron, dropdown), search icon button, white pill **Join** button
  (navy text). Height ~126px desktop; gains a shadow once the page scrolls
  (`is-scrolled` class).
- **Dropdown menus:** white panel, navy text, appear on hover and
  `:focus-within`; toggle buttons for touch/keyboard (`aria-expanded`).
- **Mobile (< 1180px):** hamburger (three bars, from WP responsive-menus
  config) opens a full-height navy panel with the menu, expandable sub-menus,
  language links, search field, Join button. On wider screens the same compact
  layout switches on automatically (JS adds `html.nav-compact`) when the menu
  does not fit on one row; without JS the menu wraps instead. Body scroll locked while open,
  Esc closes, focus returns to toggle.
- **Search panel:** clicking the search icon opens a panel under the header
  with a single input (as in WP `.search-block`); results list appears as you
  type (debounced). Enter navigates to `/search/?q=…` with full results.
- **Buttons:** pill (24px radius), depth-blue background, white text; hover
  inverts to white background with depth-blue text, as the original's
  `.blue-button`. Teal is never used behind white text (2.6:1 fails AA).
  Variants: `secondary` (outline), `white` (white bg, navy text — Join).
- **Footer:** navy background, white text. Centred footer menu (18px, teal
  hover), centred social icons row (white SVG, teal hover), optional footer
  text, optional footer logo (180px wide), copyright line with auto year.
  On mobile the menu stacks vertically.
- **Cards, banners, blocks:** as described in §6.
- **Motion:** sections fade/slide in once (IntersectionObserver adds
  `.is-visible`); disabled under `prefers-reduced-motion: reduce` and when JS
  is off (content visible by default; animation class added only by JS).

## 8. JavaScript

Two small files loaded with `defer`, bundled + minified + fingerprinted via
Hugo Pipes (`resources.Concat` → `minify` → `fingerprint`, with SRI).

- `menu.js` (~2 KB): mobile toggle, dropdown toggles, language switcher
  dropdown, Esc/outside-click close, header `scrolled` class, fade-in
  observer.
- `search.js` (~2 KB + Fuse.js ~25 KB): lazy-loads `index.json` for the
  current language on first focus of the search input; Fuse options
  `keys: [{name:'title',weight:3},{name:'tags',weight:2},'summary','content']`,
  `threshold: 0.35`, `ignoreLocation: true`; renders up to 8 results in the
  panel and all results on `/search/`. `search.js` is small and loaded
  (deferred) on every page; it injects the fingerprinted `fuse.min.js` and
  fetches `index.json` only on the first open of the search panel or on the
  `/search/` page, so visitors who never search download neither.

### Search index (`_partials/func/search-index.html`)

Published with `resources.FromString` at `/search-index/<lang>.json`, called via
`partialCached … site.Language.Name` so it is built once per language. The
header exposes the URL in a `data-index` attribute for `search.js`. Per
language, array of `{title, url, section, date, summary, tags,
categories, content}` for regular and section pages, where `content` is
`.Plain` truncated to ~1500 characters to keep the index small. Excludes pages with
`search_exclude: true` in front matter and the search page itself.

## 9. Internationalisation

- All theme strings via `i18n` keys in `i18n/en.toml` and `i18n/sv.toml`
  (e.g. `readMore`, `join`, `search`, `searchPlaceholder`, `noResults`,
  `relatedPosts`, `upcomingEvents`, `pastEvents`, `addToCalendar`,
  `register`, `registrationClosed`, `eventPassed`, `online`, `location`,
  `skipToContent`, `menu`, `close`, `language`, `page`, `olderPosts`,
  `newerPosts`, `by`, `imageCopyright`, `notFoundTitle`, `notFoundText`,
  `jsRequiredForSearch`, `archive`, `categories`, `tags`, `moreNews`).
- Dates use `time.Format` with `:date_long` / `:date_medium` /
  `:time_short`, localised by each language's `locale`
  (verified: `sv-SE` → "2 oktober 2026" / "18:00", `en-US` →
  "October 2, 2026" / "6:00 pm").
- Language switcher: iterates `hugo.Sites`, showing each
  `.Language.Label`; links to the translation of the current page if it
  exists (`.AllTranslations`), otherwise to that site's `.Home`.
  Hidden when only one language. `hreflang` alternate links in `<head>`.
- exampleSite uses `defaultContentLanguage = "en"`, content directories
  per language (`contentDir`).

## 10. Head, SEO, accessibility

- `<head>`: charset, viewport, title pattern "Page – Chapter", meta
  description, canonical, Hugo's embedded OpenGraph and Twitter-card
  templates, RSS
  `<link rel="alternate">`, `hreflang` alternates, favicon (from WP theme
  favicon.ico, overridable via `static/favicon.ico`), preload of Hind 400 and
  700.
- Skip link "Skip to main content" (WP `genesis-skip-link`), visible on focus.
- Landmarks: `header`, `nav[aria-label]`, `main#main`, `footer`.
- Focus-visible outlines in teal on dark, blue on light.
- Images: `render-image` hook uses page resources when available, emits
  `width`/`height`, `loading="lazy"`, `decoding="async"`, `srcset` (480/800/
  1200/1600) for raster images; falls back to plain `<img>` for remote URLs.
- Contrast: white on navy/depth-blue and navy on light-green banners meet AA.
  Link/lead blue `#2B72D6` on white is 4.7:1 (passes AA). Teal `#40B2A4`
  is used only as a hover/accent colour on navy or as a background behind
  navy text, never for white text.

## 11. exampleSite

Two languages (en, sv) with parallel content:

- Homepage using every block type (hero, intro, image_text, stats,
  latest_posts, upcoming_events, quote, cta, gallery).
- Pages: About (with sub-pages Board, Statutes), Membership, Contact
  (address and email only, no form), Shortcodes reference page showing every
  shortcode, Archive (monthly), Search.
- 6–8 posts across 3 categories with and without featured images.
- 4 events: 2 upcoming (dates computed far enough in the future, e.g.
  2027), 2 past; one online, one with registration closed.
- Menus: main (with dropdown under About and Membership), footer.
- Social links, footer text, copyright.
- Demo images: pattern images from the WP theme + `gallery-image.jpg`; no
  copyrighted photos.

The exampleSite content is modelled on isoc.se's structure (Om ISOC-SE,
Nyheter, Medlemskap, Publikationer, Föreningsarkiv, Kontakt) in the Swedish
version and generic chapter wording in English.

## 12. Build & deployment

- Local: `hugo server --source exampleSite --themesDir ../..` (README also
  documents `theme = "isoc-hugo-theme"` with git submodule, and Hugo Module
  import `github.com/ISOC-SE/isoc-hugo-theme`).
- `go.mod` is **not** required for submodule use; a `go.mod` with module
  path `github.com/ISOC-SE/isoc-hugo-theme` (assumed final GitHub location;
  trivially changed) is added so the theme can also be imported as a Hugo
  Module (needs Go only for that path).
- `.github/workflows/demo.yml`: on push to `main`, manual dispatch, and a
  daily schedule (so upcoming events stay correct), install Hugo (pinned
  version), build exampleSite with `--minify --baseURL` from Pages, deploy
  with `actions/deploy-pages`.

## 13. Verification

There is no unit-test framework for Hugo templates; verification is:

1. **Clean build:** `hugo --source exampleSite --themesDir ../.. --panicOnWarning --printPathWarnings --printI18nWarnings`
   exits 0 with no warnings (missing i18n keys count as failures).
2. **Output assertions:** a small shell script (`scripts/check.sh`) asserts
   on the built `public/`:
   - both languages' homepages exist and contain each block's root class;
   - `index.json` exists per language and is valid JSON (`python3 -m json.tool`);
   - each event has an `index.ics` containing `BEGIN:VEVENT` and `DTSTART`;
   - upcoming/past split puts 2027 events under upcoming and past events
     under past;
   - no `href="#"`/empty `src` left in output; all internal links resolve
     (link checker in the script).
3. **Visual check:** headless Chrome screenshots of home, page, post, post
   list, events list, single event, search, 404 at 1440px and 390px; compared
   by eye against `genesis-child-chapters-main/screenshot.png`, the
   starter-pack thumbnail, and chapter-template.isoc.org screenshots.
4. **No-JS check:** screenshot with JS disabled. Content is visible and the
   menu is reachable.
5. **Accessibility spot check:** keyboard-only navigation through header,
   dropdowns, mobile menu; contrast of key colour pairs.

## 14. Risks and open points

- **Theme-config merging:** checked. Only `params`/menus merge, and the
  design no longer depends on anything else (§5).
- **Logo/trademark:** the ISOC chapters logo is shipped as a default because
  the original theme ships it. README states chapters must use their official
  chapter logo per ISOC brand guidelines.
- **Build-time "upcoming":** events change state only on rebuild. Mitigated
  by the daily scheduled build and documented.
- **Fuse.js index size** grows with content; capping `content` at ~1500
  chars keeps a site of ~500 pages under ~1 MB (gzips to ~200 KB) and loads
  only on first search use.

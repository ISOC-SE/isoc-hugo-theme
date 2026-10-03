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
- News with categories, related posts, pagination, a monthly archive and RSS, plus consultation responses with a facts box and an overview table.
- Events with upcoming/past lists and an "Add to calendar" `.ics` file per event.
- Search in the browser (Fuse.js) over an index built with the site.
- English and Swedish built in; any number of languages with a language switcher.
- Nothing to install but Hugo. No Node, npm, Sass or CDN; fonts and scripts are self-hosted.
- Works without JavaScript (except search), keyboard friendly, WCAG 2.2 AA target
  (the level the Internet Society aims for).

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

Pin the version you have reviewed, for example with
`hugo mod get github.com/ISOC-SE/isoc-hugo-theme@<tag or commit>`, and commit
`go.mod`/`go.sum`. (A git submodule is pinned to a commit already.)

## Configuration

All settings live in your site's `hugo.toml`. Theme defaults are shown.

```toml
baseURL = "https://example.org/"
theme = "isoc-hugo-theme"
timeZone = "Europe/Stockholm"   # used for event times written without an offset
titleCaseStyle = "firstupper"   # generated titles (category pages) in sentence case, right for Swedish

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

  [params.colors]               # optional overrides: #hex, rgb()/hsl() or a colour name
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

**Logo.** ISOC asks chapters to use the official chapter branding. Download your
chapter logo from the
[ISOC Digital Asset Manager](https://assets.internetsociety.org/guidelines/guide/84cb806a-1844-46a2-aa00-1459bd1f0e70/page/99bbdc24-9e64-493a-8125-bd8459f16d7c)
(login required; white version, for the navy header). The bundled "Internet Society Chapters" logo is
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

Below 1180 px the header shows a hamburger menu. On wider screens the same
happens automatically when the menu, language switcher and Join button do not
fit on one row (many items or long labels). Without JavaScript the menu wraps
onto a second line instead.

## Content

### Pages

```yaml
---
title: About us
lead: One sentence shown under the title in the banner.
banner: green          # green | blue | navy | teal | none
banner_image: hero.jpg # optional: your own banner background
toc: true              # optional table of contents
description: Meta description (defaults to the summary; aim for 120–158 characters).
---
```

The page title is the page's only `<h1>`, so start headings in Markdown at
`##` and don't skip levels (ISOC's accessibility and SEO advice).

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

#### Consultation responses

A post about a response to a public consultation (a *remissvar*, a submission
to a regulator, a call for evidence) can carry the facts about it:

```yaml
consultation:
  topic: EU metadata retention       # short name for the overview table (defaults to the title)
  recipient: European Commission
  reference: Ares(2025)4081079
  document: response.pdf             # page bundle file, assets/ path, /static path or URL
  url: https://ec.europa.eu/…        # the consultation itself
  joint_with: [Another chapter]      # a list or one name
```

The post then ends with a box showing the recipient, reference and partners,
with buttons to the document and the consultation. A `document` that can't be
found logs a warning. List every such post in the current language, newest
first, with the `consultations` shortcode (see below), for example on a policy page.

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
- Events can be grouped in subfolders, for example one per year
  (`content/<lang>/events/2025/`). Give each folder an `_index.md` with
  `title: Events 2025` and `linkTitle: "2025"`, and it gets its own list page
  with only its events. The events page and the folders link to each other,
  newest first. The events page itself still lists every event.

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
{{< consultations order="desc" >}}  <!-- table of posts with consultation front matter; order="asc" for oldest first -->
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

### Security headers

The theme loads nothing from other hosts and sends a
`strict-origin-when-cross-origin` referrer policy. If your host lets you set
HTTP headers, this Content-Security-Policy works with every page of the theme,
search included:

```text
Content-Security-Policy: default-src 'self'; script-src 'self' 'sha256-tlTtfpdsMQSdcfX3DLM1fgx/y++BLw+48vFj+5cTJa0='; style-src 'self' 'unsafe-inline'; img-src 'self'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'
```

- The `sha256-…` value allows the one inline script (it swaps the `no-js`
  class); it changes only if `layouts/_partials/head.html` does.
- `'unsafe-inline'` in `style-src` is needed for banner images, the logo width
  and `[params.colors]`, which are inline styles. Inline *scripts* stay blocked.
- Add hosts to `img-src`/`frame-src` if your content embeds remote images or videos.

GitHub Pages cannot set headers; there a `<meta http-equiv>` CSP would be the
only option, and `frame-ancestors` does not work in a meta tag.

Security problems in the theme: see [SECURITY.md](SECURITY.md).

## Development

```bash
scripts/serve.sh          # live-reloading demo site at http://localhost:1313/
scripts/check.sh          # strict builds + output assertions + browser checks
scripts/check.sh events   # only checks whose name contains "events"
scripts/check.sh browser  # only the headless-Chrome checks
CHECK_CLOCK=2030-01-01T00:00:00Z scripts/check.sh   # build and check as of another date
scripts/screenshots.sh    # screenshots for visual review (needs Google Chrome)
python3 scripts/fetch-fonts.py   # re-download the Hind font files
```

`scripts/check.sh` builds `exampleSite/` twice with `--panicOnWarning` (any
warning, missing translation or deprecated API fails), once at the site root and
once under `/isoc-hugo-theme/` as GitHub Pages serves it. It also builds the
edge-case fixture `tests/edge/` (single language, served from a sub-path,
deliberately invalid values) and `tests/crowded/` (ISOC-SE's six-item Swedish
menu). Then it runs the assertions in `scripts/checks/` and, when Chrome or
Chromium is installed, `scripts/check_browser.py`. Those browser checks
measure the header at several widths and click through the menus and search.
Event checks follow the build time, so they stay valid as demo events pass.
The same checks run on every pull request (`.github/workflows/checks.yml`);
that workflow only builds and checks, it never deploys.

| Path | What it is |
|---|---|
| `layouts/` | Templates (`_partials/blocks/` = homepage blocks, `_shortcodes/`, `_markup/` render hooks) |
| `assets/css/` | One stylesheet per component, bundled in order by `_partials/head/css.html` |
| `assets/js/` | `menu.js`, `search.js`, vendored Fuse.js |
| `i18n/` | Theme texts (en, sv) |
| `exampleSite/` | Demo content in English and Swedish |
| `tests/edge/` | Edge-case fixture site |
| `tests/crowded/` | Header-fit fixture (long Swedish menu) for the browser checks |

## License

Copyright © 2026 ISOC-SE (Internet Society Swedish Chapter) and contributors.

This theme is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either **version 2 of the License, or (at your option) any later
version** (SPDX: `GPL-2.0-or-later`). It is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See [`LICENSE`](LICENSE)
for the full text.

The theme is a port of the Internet Society's
[chapter WordPress theme](https://github.com/InternetSociety/genesis-child-chapters)
("Internet Chapters", by the Internet Society, built on StudioPress's Genesis
Framework). Both are licensed GPL-2.0-or-later, so this port is too. The
pattern images, the quote mark and the social icons for Facebook, Instagram,
LinkedIn, RSS, X and YouTube come from that theme.

### Third-party components

| Component | Author | License | Notice |
|---|---|---|---|
| Hind font | Indian Type Foundry | SIL Open Font License 1.1 | `static/fonts/hind/OFL.txt` |
| Fuse.js 7.1.0 | Kiro Risk | Apache-2.0 | `assets/js/vendor/fuse.LICENSE.txt` |
| Social icon shapes (from the original theme) | Font Awesome 4, Dave Gandy | SIL Open Font License 1.1 | — |
| Mastodon, Bluesky, GitHub icons | [Simple Icons](https://simpleicons.org/) | CC0 1.0 | — |

Apache-2.0 code can be combined with GPL code under GPL version 3, which the
"or any later version" terms allow.

### Trademarks

"Internet Society", "ISOC" and the Internet Society logos are trademarks of
the Internet Society. The GPL covers copyright only; it grants no trademark
rights. The bundled "Internet Society Chapters" logo is a placeholder: use your
chapter's official logo as described in the ISOC brand guidelines.

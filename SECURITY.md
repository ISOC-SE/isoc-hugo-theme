# Security policy

## Reporting a vulnerability

Please report security problems in this theme **privately** via GitHub:
open the repository's **Security** tab and choose **Report a vulnerability**.
Don't open a public issue for it.

Include what you found, how to reproduce it (a minimal site or front matter is
ideal) and the theme commit or version you tested. We aim to answer within two
weeks. This is a volunteer project maintained by ISOC-SE.

## Scope

The theme's templates, CSS, JavaScript, vendored files, the scripts in
`scripts/` and the GitHub workflows. A chapter site built with the theme is
static; issues in your hosting, your own content or your Hugo version are out
of scope, but tell us if the theme makes them worse.

## Supported versions

Only the latest commit on `main`. Pin a version in your site (git submodule or
`hugo mod get ...@<version>`) and update after reviewing the changes.

## What the theme does to stay safe

- Content and config go through Go's context-aware HTML escaping; raw HTML in
  Markdown is not rendered (Hugo's default `unsafe = false`; keep it).
- Colour overrides are validated before they are written into a `<style>` element.
- No requests to other hosts at runtime; scripts and styles carry SRI hashes.
- Fuse.js is vendored unmodified (see `assets/js/vendor/`); the Hind fonts are
  self-hosted and their checksums are recorded in `static/fonts/hind/SHA256SUMS`.
- See "Security headers" in the README for a Content-Security-Policy that fits.

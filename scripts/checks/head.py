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
    expect("<script>alert" not in ctx.edge.read("/") and "--color-accent" not in edge_styles,
           "an invalid colour value must not be written into the page")
    expect("params.colors.accent" in ctx.edge.log and "is not a colour value" in ctx.edge.log,
           "an invalid colour value must log a warning")
    main_styles = " ".join(s.text() for s in ctx.main.html("/").select("style"))
    expect("--color-link" not in main_styles, "exampleSite sets no colours, so no override style expected")


@check
def head_referrer_policy_and_noopener(ctx):
    head = ctx.main.html("/").find("head")
    expect(head.find("meta[name=referrer][content=strict-origin-when-cross-origin]") is not None,
           "referrer policy meta missing")
    missing = []
    for rel in ctx.main.html_files():
        if os.path.basename(rel).startswith("_"):
            continue
        for a in ctx.main.html(rel).select("a[href]"):
            href = a.attrs["href"]
            if href.startswith(("http://", "https://", "//")) and "//example.org/" not in href \
                    and "noopener" not in a.attrs.get("rel", "").split():
                missing.append(f"{rel}: {href}")
    expect(not missing, "external links without rel=noopener:\n  " + "\n  ".join(missing[:20]))

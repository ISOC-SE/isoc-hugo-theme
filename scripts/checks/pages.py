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


@check
def pages_edge_subpath_urls(ctx):
    # Root-relative paths to static files and fragment links must keep the /sub/ base path.
    home = ctx.edge.html("/")
    hrefs = [a.attrs["href"] for a in home.select("section.hero a.btn")]
    expect(hrefs == ["/sub/files/x.pdf", "/sub/about/#team"], f"hero button hrefs {hrefs}")
    logo = home.find("a.site-logo img").attrs["src"]
    expect(logo == "/sub/images/logo.svg", f"static logo src {logo}")
    plain = ctx.edge.html("/plain/")
    img = plain.find(".entry-content img").attrs["src"]
    expect(img == "/sub/images/photo.jpg", f"static content image src {img}")
    expect(plain.find(".entry-content a[href=/sub/files/x.pdf]") is not None, "static file link in Markdown")


@check
def pages_edge_invalid_urls(ctx):
    # An invalid URL in content is logged and must not stop the build. The link
    # is still rendered; Go's escaping turns its href into "#ZgotmplZ".
    body = ctx.edge.html("/bad-urls/").find(".entry-content")
    link = body and body.find("a")
    expect(link is not None and link.text() == "opening hours", "the page with invalid URLs should still render its link")
    for value in ('"09:00-17:00" is not a valid URL', '"1a:b" is not a valid URL'):
        expect(value in ctx.edge.log, f"edge log should warn: {value}")


@check
def pages_heading_levels(ctx):
    # One h1 per page and no skipped levels (ISOC chapter-template guidance, WCAG 1.3.1).
    for name, site in (("exampleSite", ctx.main), ("edge", ctx.edge)):
        problems = []
        for rel in site.html_files():
            if os.path.basename(rel).startswith("_"):
                continue  # harness pages written by the browser checks
            root = site.html(rel)
            if root.find("meta[http-equiv=refresh]"):
                continue  # alias redirects
            levels = [int(el.tag[1]) for el in root.descendants() if re.fullmatch(r"h[1-6]", el.tag)]
            if levels.count(1) != 1:
                problems.append(f"{rel}: {levels.count(1)} h1")
            skips = [f"h{a}->h{b}" for a, b in zip(levels, levels[1:]) if b > a + 1]
            if skips:
                problems.append(f"{rel}: {', '.join(skips)}")
        expect(not problems, f"{name} heading problems:\n  " + "\n  ".join(problems[:30]))


@check
def pages_provenance(ctx):
    box = ctx.main.html("/about/statutes/").find(".entry-content")
    note = ctx.main.html("/about/statutes/").find("aside.provenance")
    expect(note is not None and "provenance--imported" in note.classes, "imported provenance notice missing")
    text = note.text()
    expect(text.startswith("Imported text. It is copied unchanged from the previous website."), f"imported text {text!r}")
    expect("Originally published 24 March 2014." in text and "The signatures are left out." in text, f"date and note {text!r}")
    link = note.find("a")
    expect(link.attrs.get("href") == "https://old.example.net/statutes/" and link.text() == "old.example.net/statutes",
           "source link without scheme or trailing slash")
    expect(box is not None and box.find("aside.provenance") is None, "the notice comes before the content, not inside it")
    sv = ctx.main.html("/sv/om/stadgar/").find("aside.provenance")
    expect(sv.text().startswith("Importerad text. Texten kommer oförändrad"), f"sv imported {sv.text()!r}")
    gen = ctx.main.html("/posts/new-postal-address/").find("aside.provenance")
    expect("provenance--generated" in gen.classes and gen.text().startswith("Generated text."), "generated notice on a post")
    expect(len(gen.select("a")) == 2, "a list of sources gives one link each")
    expect(ctx.main.html("/about/").find("aside.provenance") is None, "no notice without provenance")
    expect(ctx.edge.html("/provenance/").find("aside.provenance") is None, "unknown kind shows no notice")
    expect('provenance/: provenance.kind "copied" is not imported, generated or mixed' in ctx.edge.log,
           "edge log should warn about the unknown kind")
    mixed = ctx.edge.html("/provenance-mixed/").find("aside.provenance")
    expect(mixed is not None and mixed.find("a") is None and "/old-path/" in mixed.text(), "relative source as text")

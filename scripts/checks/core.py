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


@check
def core_subpath_build_links_resolve(ctx):
    # The demo workflow deploys exampleSite under /isoc-hugo-theme/ (GitHub Pages).
    broken = ctx.main_sub.broken_links()
    expect(not broken, f"exampleSite under a sub-path has {len(broken)} broken links:\n  " + "\n  ".join(broken[:20]))

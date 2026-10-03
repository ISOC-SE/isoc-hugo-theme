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


@check
def core_no_template_escaping_residue(ctx):
    # "ZgotmplZ" is what Go's html/template prints when it refuses a value in a
    # context (e.g. an action in attribute-name position). It must never reach the
    # output, except the edge fixture's deliberately invalid link on /bad-urls/.
    for name, site in (("exampleSite", ctx.main), ("exampleSite (sub-path)", ctx.main_sub), ("edge", ctx.edge)):
        bad = [rel for rel in site.html_files()
               if "ZgotmplZ" in site.read(rel) and not rel.startswith("bad-urls/")]
        expect(not bad, f"{name}: ZgotmplZ in {len(bad)} pages, e.g. {bad[:5]}")

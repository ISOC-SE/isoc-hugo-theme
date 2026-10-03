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

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

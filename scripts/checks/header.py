import re

from checklib import check, expect


def _top_items(root):
    ul = root.find("nav.nav-primary ul.menu")
    expect(ul is not None, "no main menu <ul>")
    return ul.kids("li")


@check
def header_logo_and_join(ctx):
    root = ctx.main.html("/")
    logo = root.find("header.site-header a.site-logo img")
    expect(logo is not None, "no logo image in header")
    expect(logo.attrs.get("alt") == "Internet Society Chapter", f"logo alt {logo.attrs.get('alt')!r}")
    expect(logo.attrs.get("width") == "233" and logo.attrs.get("height") == "47", "default logo needs width/height")
    expect(root.find("a.site-logo").attrs["href"] == "/", "logo should link to the homepage")
    expect(ctx.main.html("/sv/").find("a.site-logo").attrs["href"] == "/sv/", "sv logo should link to /sv/")
    join = root.find("header.site-header a.btn--join")
    expect(join is not None, "no Join button")
    expect(join.attrs["href"] == "https://community.internetsociety.org/s/new-registration", f"join href {join.attrs['href']}")
    expect(join.text() == "Join", f"join label {join.text()!r}")
    expect(ctx.main.html("/sv/").find("a.btn--join").text() == "Bli medlem", "sv join label")


@check
def header_main_menu_top_level(ctx):
    expected = {
        "/": ["About", "News", "Events", "Membership", "Contact"],
        "/sv/": ["Om ISOC-SE", "Nyheter", "Evenemang", "Medlemskap", "Kontakt"],
    }
    for rel, names in expected.items():
        got = [li.kids("a")[0].text() for li in _top_items(ctx.main.html(rel))]
        expect(got == names, f"{rel}: menu {got}")
    hrefs = [li.kids("a")[0].attrs["href"] for li in _top_items(ctx.main.html("/sv/"))]
    expect(hrefs == ["/sv/om/", "/sv/nyheter/", "/sv/evenemang/", "/sv/medlemskap/", "/sv/kontakt/"], f"sv hrefs {hrefs}")


@check
def header_submenu_structure(ctx):
    about = _top_items(ctx.main.html("/"))[0]
    expect("has-children" in about.classes, "About item lacks has-children")
    btn = about.find("button.submenu-toggle")
    expect(btn is not None and btn.attrs.get("aria-expanded") == "false", "submenu toggle missing")
    expect(btn.find(".sr-only").text() == "Show submenu for About", f"toggle label {btn.find('.sr-only').text()!r}")
    expect(btn.find("svg.icon") is not None, "toggle needs a chevron icon")
    links = about.select("ul.menu--sub a")
    expect([a.text() for a in links] == ["Board", "Statutes"], f"submenu {[a.text() for a in links]}")
    expect([a.attrs["href"] for a in links] == ["/about/board/", "/about/statutes/"], "submenu hrefs")
    sv = [a.attrs["href"] for a in ctx.main.html("/sv/").select("nav.nav-primary ul.menu--sub a")]
    expect(sv == ["/sv/om/styrelse/", "/sv/om/stadgar/"], f"sv submenu hrefs {sv}")


@check
def header_marks_current_page(ctx):
    root = ctx.main.html("/about/board/")
    current = [a.text() for a in root.select("nav.nav-primary a[aria-current=page]")]
    expect(current == ["Board"], f"aria-current on {current}")
    expect("is-active" in _top_items(root)[0].classes, "parent of the current page should be is-active")


@check
def header_language_switcher(ctx):
    sw = ctx.main.html("/about/").find(".lang-switch")
    expect(sw is not None, "no language switcher")
    links = {a.attrs["lang"]: a.attrs["href"] for a in sw.select("a")}
    expect(links == {"en-GB": "/about/", "sv-SE": "/sv/om/"}, f"switcher links {links}")
    expect([a.text() for a in sw.select("a")] == ["English", "Svenska"], "switcher labels")
    current = sw.select("a[aria-current]")
    expect(len(current) == 1 and current[0].attrs["lang"] == "en-GB", "current language not marked")
    toggle = sw.find("button.lang-switch__toggle")
    expect(toggle.attrs.get("aria-expanded") == "false", "language toggle needs aria-expanded")
    expect(toggle.find(".lang-switch__current").text() == "EN", "toggle should show EN")


@check
def header_language_switcher_untranslated_page(ctx):
    links = {a.attrs["lang"]: a.attrs["href"] for a in ctx.main.html("/shortcodes/").select(".lang-switch a")}
    expect(links.get("sv-SE") == "/sv/", f"untranslated page should link to /sv/, got {links}")


@check
def header_menu_toggle_and_script(ctx):
    root = ctx.main.html("/")
    toggle = root.find("button.menu-toggle")
    expect(toggle is not None and toggle.attrs.get("aria-controls") == "site-nav"
           and toggle.attrs.get("aria-expanded") == "false", "menu toggle attributes")
    expect(toggle.find(".sr-only").text() == "Open menu", "menu toggle label")
    expect(root.find("#site-nav") is not None, "menu target #site-nav missing")
    menu = [s for s in root.select("script[src]") if re.search(r"/js/menu\.min\.[0-9a-f]{64}\.js$", s.attrs["src"])]
    expect(menu, "menu.js not loaded")
    expect("defer" in menu[0].attrs and menu[0].attrs.get("integrity", "").startswith("sha256-"), "menu.js needs defer + SRI")


@check
def header_edge_single_language_no_menu(ctx):
    root = ctx.edge.html("/")
    expect(root.find("header.site-header") is not None, "edge header missing")
    expect(root.find(".lang-switch") is None, "single-language site must not show a language switcher")
    expect(root.find("nav.nav-primary") is None, "no menu configured: <nav> must be omitted")
    expect(root.find("a.site-logo").attrs["href"] == "/sub/", "edge logo should link to /sub/")

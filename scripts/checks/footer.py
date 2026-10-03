from checklib import check, expect


@check
def footer_menu_per_language(ctx):
    cases = {"/": ["About", "Contact", "Privacy policy"], "/sv/": ["Om ISOC-SE", "Kontakt", "Integritetspolicy"]}
    for rel, names in cases.items():
        nav = ctx.main.html(rel).find("footer.site-footer nav.footer-nav")
        expect(nav is not None and nav.attrs.get("aria-label"), f"{rel}: footer nav missing or unlabeled")
        got = [a.text() for a in nav.select("a")]
        expect(got == names, f"{rel}: footer menu {got}")


@check
def footer_social_links(ctx):
    links = ctx.main.html("/").select("footer.site-footer ul.social-links a")
    expect(len(links) == 3, f"expected 3 social links, got {len(links)}")
    labels = [a.find(".sr-only").text() for a in links]
    expect(labels == ["LinkedIn", "Mastodon", "RSS"], f"social labels {labels}")
    for a in links:
        expect(a.find("svg.icon") is not None, f"social link {a.attrs['href']} has no icon")
    expect(links[2].attrs["href"] == "/posts/index.xml", f"rss link {links[2].attrs['href']}")


@check
def footer_copyright_and_text(ctx):
    year = ctx.now.year
    text = ctx.main.html("/").find("footer.site-footer .site-footer__copyright").text()
    expect(text == f"© {year} Internet Society Chapter", f"copyright {text!r}")
    sv = ctx.main.html("/sv/").find(".site-footer__copyright").text()
    expect(sv == f"© {year} Internet Society Sverige", f"sv copyright {sv!r}")
    blurb = ctx.main.html("/").find(".site-footer__text")
    expect(blurb is not None and blurb.find("a") is not None, "footerText (Markdown with a link) not rendered")


@check
def footer_edge_minimal(ctx):
    footer = ctx.edge.html("/").find("footer.site-footer")
    expect(footer is not None, "edge footer missing")
    expect(footer.find("nav") is None, "edge has no footer menu: <nav> must be omitted")
    expect(footer.find("ul.social-links") is None, "edge has no social links: list must be omitted")
    expect(footer.find(".site-footer__copyright").text().endswith("Edge Chapter"), "edge copyright")

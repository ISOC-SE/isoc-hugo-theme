from checklib import check, expect, ics_events, split_events

ORDER = ["hero", "block-image-text", "block-intro", "block-stats", "block-latest-posts",
         "block-upcoming-events", "block-quote", "block-cta", "block-gallery", "block-markdown"]


def _blocks(root):
    main = root.find("main")
    return [k for k in main.kids() if k.tag in ("section", "header")]


@check
def home_blocks_render_in_order(ctx):
    for rel in ("/", "/sv/"):
        found = []
        for el in _blocks(ctx.main.html(rel)):
            found += [c for c in el.classes if c in ORDER]
        expect(found == ORDER, f"{rel}: block order {found}")


@check
def home_hero(ctx):
    hero = ctx.main.html("/").find("section.hero")
    expect("banner--green" in hero.classes, "hero defaults to the green pattern")
    expect(hero.find("h1.hero__title").text() == "Internet Society Chapter", "hero title")
    expect(hero.find(".hero__tagline") is not None, "hero tagline")
    expect([a.attrs["href"] for a in hero.select("a.btn")] == ["/membership/"], "hero button href")
    sv = ctx.main.html("/sv/").find("section.hero a.btn")
    expect(sv.attrs["href"] == "/sv/medlemskap/", f"sv hero button {sv.attrs['href']}")
    expect(len(ctx.main.html("/").select("h1")) == 1, "homepage needs exactly one h1")


@check
def home_latest_posts_and_events(ctx):
    root = ctx.main.html("/")
    latest = root.find("section.block-latest-posts")
    expect(len(latest.select(".card")) == 4, "latest posts should show 4 cards")
    expect(latest.find(".block__more a").attrs["href"] == "/posts/", "more news link")
    sv_more = ctx.main.html("/sv/").find("section.block-latest-posts .block__more a")
    expect(sv_more.attrs["href"] == "/sv/nyheter/" and sv_more.text() == "Fler nyheter", "sv more news link")
    events = root.find("section.block-upcoming-events")
    upcoming, _ = split_events(ics_events(ctx.main, "events"), ctx.now)
    titles = [a.text() for a in events.select(".event-card__title a")]
    expect(titles == [e["title"] for e in upcoming][:3], f"upcoming block {titles}")
    if not upcoming:
        expect(events.find(".events-empty") is not None, "empty_text should show when nothing is upcoming")
    expect(events.find(".block__more a").attrs["href"] == "/events/", "all events link")


@check
def home_content_blocks(ctx):
    root = ctx.main.html("/")
    expect(root.find("section.block-image-text .image-text img") is not None, "image_text image")
    expect(root.find("section.block-intro .lead") is not None, "intro lead")
    stats = root.select("section.block-stats li.stat")
    expect([s.find(".stat__value").text() for s in stats] == ["120+", "1992", "100 000+"], "stats values")
    expect("band--navy" in root.find("section.block-stats").classes, "stats background")
    quote = root.find("section.block-quote figure.quote")
    expect(quote.find("blockquote").text() == "The Internet is for everyone.", "quote text")
    expect(quote.find(".quote__author").text() == "Internet Society", "quote author")
    cta = root.find("section.block-cta")
    expect(cta.find("h2").text() == "Become a member" and cta.find("a.btn--white") is not None, "cta block")
    gallery = root.select("section.block-gallery ul.gallery img")
    expect(len(gallery) == 3, "gallery should show 3 images")
    expect(all(g.attrs.get("width") == "600" and g.attrs.get("height") == "600" for g in gallery), "gallery fill 600x600")
    expect(root.find("section.block-markdown .entry-content p") is not None, "markdown block")


@check
def home_shortcodes_page(ctx):
    raw = ctx.main.read("shortcodes/index.html")
    for bad in ("{{<", "HAHAHUGO", "<p><div", "<p><figure", "<p><ul"):
        expect(bad not in raw, f"shortcodes page contains {bad!r}")
    root = ctx.main.html("/shortcodes/")
    content = root.find(".entry-content")
    expect(len(content.select("a.btn")) >= 3, "buttons")
    expect(len(content.select(".notice")) == 2 and content.find(".notice--warning") is not None, "notices")
    expect(content.find(".image-text.image-text--right img") is not None, "image-text shortcode")
    expect(content.find("figure.quote blockquote").text() == "The Internet is for everyone.", "quote shortcode")
    expect(len(content.select("ul.stats li.stat")) == 3, "stats shortcode")
    expect(len(content.select(".columns .column h3")) == 2, "columns shortcode")
    expect(len(content.select("ul.gallery img")) == 2, "gallery shortcode uses the bundle's images")
    expect(len(content.select(".card-grid .card")) == 4, "latest-posts shortcode")
    upcoming, _ = split_events(ics_events(ctx.main, "events"), ctx.now)
    expect(len(content.select(".event-card")) == min(2, len(upcoming)), "upcoming-events shortcode")
    expect(content.find(".cta--box h2").text() == "Join the chapter", "cta shortcode")


@check
def home_edge_unknown_block(ctx):
    root = ctx.edge.html("/")
    expect(root.find("section.hero h1").text() == "Edge Chapter", "edge hero defaults its title to the site title")
    expect('unknown type "nonsense"' in ctx.edge.log, "edge log should warn about the unknown block type")


@check
def home_edge_invalid_hero_banner(ctx):
    hero = ctx.edge.html("/").find("section.hero")
    expect("banner--violet" not in hero.classes and "banner--green" in hero.classes,
           f"unknown hero banner should fall back to green, got {hero.classes}")
    expect('unknown banner "violet"' in ctx.edge.log, "edge log should warn about the hero's banner: violet")

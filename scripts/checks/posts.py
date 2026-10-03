from checklib import check, expect


def _card_titles(root):
    return [a.text() for a in root.select(".card-grid .card .card__title a")]


@check
def posts_list_paginates(ctx):
    root = ctx.main.html("/posts/")
    titles = _card_titles(root)
    expect(titles == ["Annual general meeting 2026", "Call for nominations to the board",
                      "New postal address", "Save the date: national Internet governance forum"],
           f"page 1 cards {titles}")
    nav = root.find("nav.pagination")
    expect(nav is not None and nav.find("a[href=/posts/page/2/]") is not None, "pagination link to page 2 missing")
    expect(nav.find("span[aria-current=page]").text() == "1", "current page marker")
    page2 = _card_titles(ctx.main.html("/posts/page/2/"))
    expect(page2 == ["Why end-to-end encryption matters", "Our response to the EU consultation on data retention"],
           f"page 2 cards {page2}")
    sv = ctx.main.html("/sv/nyheter/")
    expect(len(_card_titles(sv)) == 4 and sv.find("a[href=/sv/nyheter/page/2/]") is not None, "sv news pagination")


@check
def posts_cards_have_date_thumbnail_and_tags(ctx):
    cards = ctx.main.html("/posts/").select(".card-grid .card")
    first = cards[0]
    expect(first.find("time").attrs.get("datetime") == "2026-02-11", "card date datetime")
    expect(first.find("time").text() == "11 February 2026", f"card date text {first.find('time').text()!r}")
    expect(first.find(".card__image img") is not None, "post with an image should have a thumbnail")
    expect(cards[1].find(".card__image") is None, "post without an image must not render a thumbnail")
    expect([li.text() for li in first.select(".card__tags li")] == ["Community"], "card category labels")
    sv_time = ctx.main.html("/sv/nyheter/").find(".card time").text()
    expect(sv_time == "11 februari 2026", f"sv card date {sv_time!r}")


@check
def posts_category_nav(ctx):
    items = [a.text() for a in ctx.main.html("/posts/").select("ul.category-nav a")]
    expect(items == ["Community (3)", "Internet governance (2)", "Privacy (2)"], f"category nav {items}")
    term = ctx.main.html("/categories/community/")
    current = term.find("ul.category-nav a[aria-current=page]")
    expect(current is not None and current.text() == "Community (3)", "current category not marked")
    expect(len(_card_titles(term)) == 3, f"community term should list 3 posts, got {_card_titles(term)}")
    expect(len(ctx.main.html("/categories/").select(".term-list a")) == 3, "taxonomy page should list 3 terms")


@check
def posts_single_banner_meta_and_image(ctx):
    root = ctx.main.html("/posts/annual-general-meeting-2026/")
    banner = root.find("header.banner")
    expect("banner--blue" in banner.classes, "posts use the blue banner by default")
    expect([a.text() for a in banner.select(".banner__above a")] == ["Community"], "categories above the title")
    expect(banner.find("h1").text() == "Annual general meeting 2026", "post title")
    meta = banner.find(".banner__meta")
    expect(meta.find("time").text() == "11 February 2026", f"post date {meta.find('time').text()!r}")
    expect("by The Board" in meta.text(), f"authors line {meta.text()!r}")
    fig = root.find("figure.featured-image")
    expect(fig is not None and fig.find("img[srcset]") is not None, "featured image missing")
    expect(fig.find("img").attrs.get("loading") == "eager", "featured image should load eagerly")
    expect(fig.find("figcaption").text() == "Image copyright: ISOC Chapter, CC BY 4.0", "image credit caption")
    sv = ctx.main.html("/sv/nyheter/kallelse-arsstamma-2026/")
    expect(sv.find(".banner__meta time").text() == "11 februari 2026", "sv post date")
    expect(sv.find("figcaption").text() == "Bild: ISOC-SE, CC BY 4.0", "sv image credit")


@check
def posts_related(ctx):
    rel = ctx.main.html("/posts/annual-general-meeting-2026/").find("section.related")
    expect(rel is not None and rel.find("h2").text() == "Related posts", "related posts section missing")
    hrefs = [a.attrs["href"] for a in rel.select(".card__title a")]
    expect(len(hrefs) == 4, f"expected 4 related posts, got {hrefs}")
    expect("/posts/annual-general-meeting-2026/" not in hrefs, "a post must not be related to itself")
    expect(all(h.startswith("/posts/") for h in hrefs), f"related posts must be posts: {hrefs}")


@check
def posts_archive(ctx):
    root = ctx.main.html("/archive/")
    years = [h.text() for h in root.select(".archive__year h2")]
    expect(years == ["2026", "2025"], f"archive years {years}")
    months = [h.text() for h in root.select(".archive__year")[0].select(".archive__month")]
    expect(months == ["February", "January"], f"2026 months {months}")
    expect(len(root.select(".archive__list li")) == 6, "archive should list all 6 posts")
    sv_months = [h.text() for h in ctx.main.html("/sv/arkiv/").select(".archive__month")][:2]
    expect(sv_months == ["Februari", "Januari"], f"sv months {sv_months}")


@check
def posts_rss(ctx):
    rss = ctx.main.read("posts/index.xml")
    expect(rss.count("<item>") == 6, "news RSS should contain 6 items")


@check
def posts_edge_minimal_post(ctx):
    card = ctx.edge.html("/posts/").find(".card")
    expect(card is not None, "edge posts list missing")
    expect(card.find(".card__image") is None and card.find(".card__tags") is None, "no empty thumbnail/tags")
    post = ctx.edge.html("/posts/plain-post/")
    expect(post.find(".banner__above") is None and post.find("figure") is None, "no empty categories/figure")


def _consultation_rows(root):
    return [[td.text() for td in tr.select("td")] for tr in root.select("table.consultations tbody tr")]


@check
def posts_consultation_details(ctx):
    box = ctx.main.html("/posts/eu-data-retention-response/").find("article aside.consultation-details")
    expect(box is not None, "a post with consultation front matter needs the details box")
    expect(box.find("h2").text() == "About the response", "details box heading")
    expect([d.text() for d in box.select("dt")] == ["Submitted to", "Reference", "Together with"], "details box labels")
    expect([d.text() for d in box.select("dd")] == ["European Commission", "Ares(2025)4081079",
                                                    "Another chapter, A digital rights group"], "details box values")
    links = box.select(".consultation-details__actions a")
    expect(links[0].attrs.get("href") == "/posts/eu-data-retention-response/response.pdf"
           and links[0].text() == "Read our response" and "rel" not in links[0].attrs, "document button from the page bundle")
    expect(links[1].attrs.get("href", "").startswith("https://ec.europa.eu/") and links[1].attrs.get("rel") == "noopener",
           "consultation link button")
    expect(ctx.main.exists("posts/eu-data-retention-response/response.pdf"), "the bundled document must be published")
    sv = ctx.main.html("/sv/nyheter/yttrande-datalagring/").find("aside.consultation-details")
    expect(sv.find("h2").text() == "Om svaret" and sv.find("dt").text() == "Mottagare", "sv details box")
    expect(ctx.main.html("/posts/why-encryption-matters/").find("aside.consultation-details") is None,
           "posts without consultation front matter have no details box")
    old = ctx.edge.html("/posts/consultation-old/").find("aside.consultation-details")
    expect(old.select("dd")[-1].text() == "One partner", "joint_with may be a plain string")
    expect(old.find(".consultation-details__actions a").attrs.get("href") == "/sub/files/x.pdf", "static-path document keeps the base path")
    missing = ctx.edge.html("/posts/consultation-missing-doc/").find("aside.consultation-details")
    expect(missing.find(".consultation-details__actions") is None, "no buttons when the document is missing and there is no url")
    expect('consultation-missing-doc/: consultation.document "nowhere.pdf" not found' in ctx.edge.log,
           "edge log should warn about the missing document")


@check
def posts_consultations_table(ctx):
    table = ctx.main.html("/shortcodes/").find("table.consultations")
    expect(table is not None, "consultations shortcode table missing")
    expect([th.text() for th in table.select("th")] == ["Year", "Consultation", "Submitted to", "Reference"], "table headers")
    expect(_consultation_rows(ctx.main.html("/shortcodes/")) == [["2025", "EU metadata retention", "European Commission", "Ares(2025)4081079"]],
           "only the current language's consultation posts, topic before title")
    expect(table.find("a").attrs.get("href") == "/posts/eu-data-retention-response/", "row links to the post")
    edge = ctx.edge.html("/consultations/")
    tables = edge.select("table.consultations")
    expect(len(tables) == 2, "edge page has two consultation tables")
    asc = [[td.text() for td in tr.select("td")] for tr in tables[0].select("tbody tr")]
    expect([r[1] for r in asc] == ["Old consultation response", "Missing document"], f"order=asc, title as fallback: {asc}")
    desc = [[td.text() for td in tr.select("td")] for tr in tables[1].select("tbody tr")]
    expect([r[0] for r in desc] == ["2020", "2019"], f"invalid order falls back to newest first: {desc}")
    expect('consultations order="sideways" is not asc or desc' in ctx.edge.log, "edge log should warn about the invalid order")

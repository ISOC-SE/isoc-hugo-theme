from checklib import check, expect, ics_events, split_events


def _ics(site, rel):
    raw = site.read(rel)
    expect("\n" not in raw.replace("\r\n", "") and "\r" not in raw.replace("\r\n", ""),
           f"{rel}: lines must end with CRLF and contain no other line breaks")
    lines = raw.split("\r\n")
    expect(lines[0] == "BEGIN:VCALENDAR" and lines[-2] == "END:VCALENDAR" and lines[-1] == "",
           f"{rel}: not a complete VCALENDAR")
    return lines


def _group_titles(root, group):
    return [a.text() for a in root.select(f".events-group--{group} .event-card__title a")]


def _is_upcoming(ctx, site, section, rel):
    upcoming, _ = split_events(ics_events(site, section), ctx.now)
    return any(e["rel"] == rel for e in upcoming)


@check
def events_list_splits_upcoming_and_past(ctx):
    # Expectations follow the build time, so the nightly CI stays valid as events pass.
    for site_rel, section in (("/events/", "events"), ("/sv/evenemang/", "sv/evenemang")):
        upcoming, past = split_events(ics_events(ctx.main, section), ctx.now)
        root = ctx.main.html(site_rel)
        expect(_group_titles(root, "upcoming") == [e["title"] for e in upcoming],
               f"{site_rel} upcoming {_group_titles(root, 'upcoming')} != {[e['title'] for e in upcoming]}")
        expect(_group_titles(root, "past") == [e["title"] for e in past],
               f"{site_rel} past {_group_titles(root, 'past')} != {[e['title'] for e in past]}")
        if not upcoming:
            expect(root.find(".events-group--upcoming .events-empty") is not None, f"{site_rel}: empty-state text missing")
        expect(all("event-card--past" in c.classes for c in root.select(".events-group--past .event-card")),
               f"{site_rel}: past cards must be marked")
    card = next(c for c in ctx.main.html("/events/").select(".event-card")
                if c.find(".event-card__title a").text() == "SamNet 5 conference")
    expect(card.find(".event-card__day").text() == "21" and card.find(".event-card__month").text() == "Jan", "date badge")
    expect(ctx.main.html("/sv/evenemang/").find(".events-group--upcoming h2").text() == "Kommande evenemang", "sv heading")


@check
def events_single_details(ctx):
    root = ctx.main.html("/events/samnet-5/")
    details = root.find(".event__details")
    expect(details is not None, "event details box missing")
    text = details.text()
    expect("21 January 2027, 09:00–17:00" in text, f"date range missing: {text!r}")
    expect("Internetstiftelsen, Hammarby kaj 10D, Stockholm" in text, "location missing")
    ics = details.find("a[download]")
    expect(ics is not None and ics.attrs["href"] == "/events/samnet-5/event.ics", f"ics link {ics and ics.attrs}")
    register = details.find("a.btn[href=https://example.com/register]")
    if _is_upcoming(ctx, ctx.main, "events", "events/samnet-5/"):
        expect(register is not None and register.text() == "Register", "register button missing")
        expect(root.find(".notice") is None, "upcoming events must not show the past-event notice")
    else:
        expect(register is None, "a past event must not offer registration")
        expect(root.find(".notice") is not None, "a past event needs the past-event notice")


@check
def events_registration_closed_and_online(ctx):
    details = ctx.main.html("/events/agm-2027/").find(".event__details")
    online = details.find("a[href=https://meet.example.org/agm-2027]")
    expect(online is not None and online.text() == "Join online", "online link missing")
    expect(details.find("a.btn[href=https://example.com/register]") is None, "no register button when closed")
    closed = "Registration closed" in details.text()
    if _is_upcoming(ctx, ctx.main, "events", "events/agm-2027/"):
        expect(closed, "closed registration not shown")
    else:
        expect(not closed, "a past event does not need the registration-closed note")


@check
def events_past_notice(ctx):
    root = ctx.main.html("/events/agm-2026/")
    notice = root.find(".notice")
    expect(notice is not None and notice.text() == "This event has already taken place.", "past notice")
    buttons = [a.text() for a in root.select(".event__details a.btn")]
    expect(buttons == ["Add to calendar"], f"past event should only offer the calendar file, got {buttons}")


@check
def events_ics_content(ctx):
    lines = _ics(ctx.main, "events/samnet-5/event.ics")
    for expected in ("VERSION:2.0", "BEGIN:VEVENT", "END:VEVENT", "DTSTART:20270121T080000Z",
                     "DTEND:20270121T160000Z", "SUMMARY:SamNet 5 conference",
                     "LOCATION:Internetstiftelsen\\, Hammarby kaj 10D\\, Stockholm",
                     "URL:https://example.org/events/samnet-5/"):
        expect(expected in lines, f"samnet-5 ics lacks {expected!r}")
    expect(any(l.startswith("UID:") and l.endswith("@example.org") for l in lines), "UID missing")
    expect(any(l.startswith("DTSTAMP:") and l.endswith("Z") for l in lines), "DTSTAMP missing")
    agm = _ics(ctx.main, "events/agm-2027/event.ics")
    expect("SUMMARY:Annual general meeting 2027\\, online" in agm, "commas in SUMMARY must be escaped")
    expect("LOCATION:Online" in agm and "DTSTART:20270324T170000Z" in agm, "online event location/start")
    expect(ctx.main.exists("sv/evenemang/samnet-5/event.ics"), "sv events need .ics files too")


@check
def events_edge_timezones_and_all_day(ctx):
    no_offset = _ics(ctx.edge, "events/no-offset/event.ics")
    expect("DTSTART:20990501T160000Z" in no_offset and "DTEND:20990501T180000Z" in no_offset,
           "a start without offset must be read in the site timeZone (Europe/Stockholm, CEST)")
    all_day = _ics(ctx.edge, "events/all-day/event.ics")
    expect("DTSTART;VALUE=DATE:20990601" in all_day and "DTEND;VALUE=DATE:20990603" in all_day,
           "all-day events use DATE values with an exclusive end")
    no_end = _ics(ctx.edge, "events/no-end/event.ics")
    expect("DTSTART:20990701T080000Z" in no_end and "DTEND:20990701T090000Z" in no_end,
           "events without end default to one hour")
    expect("LOCATION:Room 1\\nORGANIZER:mailto:x@example.com" in no_end
           and not any(l.startswith("ORGANIZER") for l in no_end),
           "a carriage return in a text value must be escaped, not start a new property")
    link = ctx.edge.html("/events/no-offset/").find("a[download]")
    expect(link.attrs["href"] == "/sub/events/no-offset/event.ics", f"ics link must include base path, got {link.attrs['href']}")
    titles = _group_titles(ctx.edge.html("/events/"), "upcoming")
    expect(titles == ["No offset", "All day", "No end"], f"edge upcoming order {titles}")
    expect(_group_titles(ctx.edge.html("/events/"), "past") == ["Past event"], "edge past events")

"""Small, dependency-free helpers for asserting on Hugo output.

Checks live in scripts/checks/*.py and register themselves with @check.
"""
import json
import os
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

CHECKS = []
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}


def check(fn):
    """Register a check. The function receives the check context."""
    CHECKS.append(fn)
    return fn


class CheckFailed(AssertionError):
    pass


def expect(cond, msg):
    if not cond:
        raise CheckFailed(msg)


class El:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = {k: (v if v is not None else "") for k, v in attrs}
        self.parent = parent
        self.children = []  # El or str, in document order

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    def text(self):
        parts = []
        for child in self.children:
            parts.append(child if isinstance(child, str) else child.text())
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def kids(self, tag=None):
        """Direct child elements, optionally filtered by tag name."""
        return [c for c in self.children if isinstance(c, El) and (tag is None or c.tag == tag)]

    def descendants(self):
        for child in self.children:
            if isinstance(child, El):
                yield child
                yield from child.descendants()

    def select(self, selector):
        current = [self]
        for part in selector.split():
            comp = _parse_compound(part)
            found, seen = [], set()
            for base in current:
                for el in base.descendants():
                    if id(el) not in seen and _matches(el, comp):
                        seen.add(id(el))
                        found.append(el)
            current = found
        return current

    def find(self, selector):
        found = self.select(selector)
        return found[0] if found else None

    def __repr__(self):
        return f"<{self.tag} {self.attrs}>"


_ATTR_RE = re.compile(r'\[([\w:-]+)(?:=("?)([^\]"]*)\2)?\]')


def _parse_compound(part):
    tag_match = re.match(r"^[a-zA-Z][\w-]*", part)
    return {
        "tag": tag_match.group(0).lower() if tag_match else None,
        "classes": re.findall(r"\.([\w-]+)", _ATTR_RE.sub("", part)),
        "ids": re.findall(r"#([\w-]+)", _ATTR_RE.sub("", part)),
        "attrs": [(name, value if eq or value else None)
                  for name, eq, value in _ATTR_RE.findall(part)],
    }


def _matches(el, comp):
    if comp["tag"] and el.tag != comp["tag"]:
        return False
    if any(c not in el.classes for c in comp["classes"]):
        return False
    if any(el.attrs.get("id") != i for i in comp["ids"]):
        return False
    for name, value in comp["attrs"]:
        if name not in el.attrs:
            return False
        if value is not None and el.attrs[name] != value:
            return False
    return True


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = El("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        el = El(tag, attrs, self.cur)
        self.cur.children.append(el)
        if tag not in VOID:
            self.cur = el

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(El(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def parse_html(text):
    builder = _TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


class Site:
    """A built Hugo site: its publish directory and base URL."""

    def __init__(self, public, base_url, log=""):
        self.public = public
        parsed = urlparse(base_url)
        self.host = parsed.netloc
        self.base_path = parsed.path if parsed.path.endswith("/") else parsed.path + "/"
        self.log = log
        self._cache = {}

    def _local(self, rel):
        rel = rel.lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel += "index.html"
        return os.path.join(self.public, rel)

    def exists(self, rel):
        return os.path.isfile(self._local(rel))

    def read(self, rel):
        path = self._local(rel)
        expect(os.path.isfile(path), f"missing output file: {rel}")
        with open(path, encoding="utf-8", newline="") as fh:  # keep CRLF intact
            return fh.read()

    def html(self, rel):
        if rel not in self._cache:
            self._cache[rel] = parse_html(self.read(rel))
        return self._cache[rel]

    def json(self, rel):
        return json.loads(self.read(rel))

    def html_files(self):
        out = []
        for dirpath, _, files in os.walk(self.public):
            for name in files:
                if name.endswith(".html"):
                    out.append(os.path.relpath(os.path.join(dirpath, name), self.public))
        return sorted(out)

    def url_to_rel(self, url):
        """Turn a site URL (absolute or root-relative) into a publish-dir path, or None if external."""
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            return None
        if parsed.netloc and parsed.netloc != self.host:
            return None
        path = unquote(parsed.path)
        if not path.startswith(self.base_path):
            return "!outside-base:" + path
        return path[len(self.base_path):]

    def resolve(self, url, page_rel):
        """Local file for a URL found on page `page_rel`; None if external or same-page anchor."""
        parsed = urlparse(url)
        if parsed.scheme in ("mailto", "tel", "data", "javascript"):
            return None
        if not parsed.scheme and not parsed.netloc and not parsed.path:
            return None  # "#fragment" or "?query" on the same page
        if not parsed.scheme and not parsed.path.startswith("/"):
            page_dir = os.path.dirname(page_rel)
            rel = os.path.normpath(os.path.join(page_dir, unquote(parsed.path)))
            return self._local(rel + ("/" if parsed.path.endswith("/") else ""))
        rel = self.url_to_rel(url)
        if rel is None:
            return None
        if rel.startswith("!outside-base:"):
            return rel
        local = self._local(rel)
        if not os.path.isfile(local) and os.path.isfile(os.path.join(local, "index.html")):
            local = os.path.join(local, "index.html")
        return local

    def broken_links(self):
        broken = []
        for page_rel in self.html_files():
            root = self.html(page_rel)
            for el in root.descendants():
                urls = [el.attrs[a] for a in ("href", "src") if a in el.attrs]
                if "srcset" in el.attrs:
                    urls += [p.strip().split()[0] for p in el.attrs["srcset"].split(",") if p.strip()]
                for url in urls:
                    if el.tag == "link" and el.attrs.get("rel") in ("canonical", "alternate"):
                        continue  # absolute permalinks, checked separately
                    if url in ("", "#"):
                        broken.append(f"{page_rel}: placeholder link {url!r} on <{el.tag}>")
                        continue
                    local = self.resolve(url, page_rel)
                    if local is None:
                        continue
                    if local.startswith("!outside-base:") or not os.path.isfile(local):
                        broken.append(f"{page_rel}: {url}")
        return broken


def ics_events(site, section):
    """Events of one built section, read from their generated event.ics files.

    Returns dicts {title, rel, start, end, past?} sorted by start; start/end are
    aware UTC datetimes (all-day events: midnight UTC of the DATE values).
    """
    import datetime as dt
    root = os.path.join(site.public, section.strip("/"))
    events = []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        ics = os.path.join(root, name, "event.ics")
        if not os.path.isfile(ics):
            continue
        fields = {}
        with open(ics, encoding="utf-8", newline="") as fh:
            for line in fh.read().split("\r\n"):
                key, _, value = line.partition(":")
                fields[key.split(";")[0]] = value
        def parse(v):
            if len(v) == 8:
                return dt.datetime.strptime(v, "%Y%m%d").replace(tzinfo=dt.timezone.utc)
            return dt.datetime.strptime(v, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
        title = re.sub(r"\\([,;\\])", r"\1", fields["SUMMARY"]).replace("\\n", "\n")
        events.append({"title": title, "rel": f"{section.strip('/')}/{name}/",
                       "start": parse(fields["DTSTART"]), "end": parse(fields["DTEND"])})
    return sorted(events, key=lambda e: e["start"])


def split_events(events, now):
    """(upcoming ascending, past descending) as the theme should compute them at `now`."""
    upcoming = [e for e in events if e["end"] >= now]
    past = [e for e in events if e["end"] < now]
    return upcoming, list(reversed(past))

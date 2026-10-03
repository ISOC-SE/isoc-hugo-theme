import base64
import hashlib
import os
import re

from checklib import check, expect

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(rel):
    path = os.path.join(ROOT, rel)
    expect(os.path.isfile(path), f"{rel} missing")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


@check
def docs_readme_covers_configuration(ctx):
    readme = _read("README.md")
    for needle in ("hugo.toml", "joinURL", "defaultBanner", "params.colors", "blocks:", "registration_url",
                   "translationKey", "layout: search", "scripts/check.sh", "0.158", "timeZone",
                   "{{< image-text", "{{< cta", "custom.css"):
        expect(needle in readme, f"README does not mention {needle!r}")


@check
def docs_archetypes_and_workflow(ctx):
    for name in ("default", "posts", "events"):
        _read(f"archetypes/{name}.md")
    expect("start:" in _read("archetypes/events.md"), "events archetype needs start")
    wf = _read(".github/workflows/demo.yml")
    for needle in ("schedule:", "scripts/check.sh", "actions/deploy-pages", "HUGO_VERSION"):
        expect(needle in wf, f"workflow lacks {needle!r}")


@check
def docs_i18n_files_have_same_keys(ctx):
    en = set(re.findall(r"^(\w+) = ", _read("i18n/en.toml"), re.M))
    sv = set(re.findall(r"^(\w+) = ", _read("i18n/sv.toml"), re.M))
    expect(en == sv, f"i18n key mismatch: only en {sorted(en - sv)}, only sv {sorted(sv - en)}")


@check
def docs_font_checksums(ctx):
    # static/fonts/hind/SHA256SUMS (written by scripts/fetch-fonts.py) must match the committed fonts.
    font_dir = os.path.join(ROOT, "static", "fonts", "hind")
    listed = {}
    for line in _read("static/fonts/hind/SHA256SUMS").splitlines():
        digest, _, name = line.partition("  ")
        listed[name] = digest
    present = sorted(n for n in os.listdir(font_dir) if n.endswith(".woff2"))
    expect(sorted(listed) == present, f"SHA256SUMS lists {sorted(listed)}, directory has {present}")
    for name in present:
        with open(os.path.join(font_dir, name), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        expect(digest == listed[name], f"{name} does not match SHA256SUMS")


@check
def docs_csp_hash_matches_inline_script(ctx):
    # The CSP in README allows the inline script by hash; keep the two in sync.
    scripts = [s.text() for s in ctx.main.html("/").select("head script") if "src" not in s.attrs
               and s.attrs.get("type") != "application/json"]
    expect(len(scripts) == 1, f"expected one inline script in <head>, found {len(scripts)}")
    raw = re.search(r"<head>.*?<script>(.*?)</script>", ctx.main.read("/"), re.S).group(1)
    digest = "sha256-" + base64.b64encode(hashlib.sha256(raw.encode()).digest()).decode()
    expect(digest in _read("README.md"), f"README CSP must allow the inline script with '{digest}'")
    expect(os.path.isfile(os.path.join(ROOT, "SECURITY.md")), "SECURITY.md missing")

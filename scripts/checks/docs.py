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

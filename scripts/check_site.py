#!/usr/bin/env python3
"""Run output assertions against the built example and edge sites.

Usage: check_site.py --main DIR --main-base URL --edge DIR --edge-base URL --edge-log FILE [filter]
"""
import argparse
import datetime
import importlib.util
import pathlib
import sys
import traceback

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from checklib import CHECKS, CheckFailed, Site  # noqa: E402


class Ctx:
    def __init__(self, main, main_sub, edge, now):
        self.main = main
        self.main_sub = main_sub  # exampleSite built under a sub-path
        self.edge = edge
        self.now = now  # build time (UTC); CHECK_CLOCK overrides it


def load_checks():
    for path in sorted((HERE / "checks").glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"checks.{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--main-base", required=True)
    ap.add_argument("--main-sub", required=True)
    ap.add_argument("--main-sub-base", required=True)
    ap.add_argument("--edge", required=True)
    ap.add_argument("--edge-base", required=True)
    ap.add_argument("--edge-log", required=True)
    ap.add_argument("--now", default="", help="ISO time the sites were built as (hugo --clock)")
    ap.add_argument("filter", nargs="?", default="")
    args = ap.parse_args()

    with open(args.edge_log, encoding="utf-8") as fh:
        edge_log = fh.read()
    now = (datetime.datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now
           else datetime.datetime.now(datetime.timezone.utc))
    ctx = Ctx(Site(args.main, args.main_base), Site(args.main_sub, args.main_sub_base),
              Site(args.edge, args.edge_base, edge_log), now)

    load_checks()
    selected = [fn for fn in CHECKS if args.filter in fn.__name__]
    failures = 0
    for fn in selected:
        try:
            fn(ctx)
            print(f"PASS {fn.__name__}")
        except CheckFailed as exc:
            failures += 1
            print(f"FAIL {fn.__name__}: {exc}")
        except Exception:  # a crashing check is a failure too
            failures += 1
            print(f"FAIL {fn.__name__}: crashed\n{traceback.format_exc()}")
    print(f"\n{len(selected) - failures} passed, {failures} failed")
    if not selected:
        print(f"no checks match {args.filter!r}")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

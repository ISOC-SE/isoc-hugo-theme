#!/usr/bin/env python3
"""Browser checks in headless Chrome: header layout at several widths and the
interactive behaviour of the menu, dropdowns and search panel.

Usage: check_browser.py --site DIR --crowded DIR
  --site     exampleSite built with a root base URL
  --crowded  tests/crowded built with a root base URL

Each check runs inside a same-origin harness page that loads the site in an
iframe (whose width is the viewport the site sees), drives it with JavaScript
and writes PASS/FAIL lines that are read back with --dump-dom.
Skips with a notice (exit 0) when no Chrome/Chromium is installed.
"""
import argparse
import functools
import html
import os
import re
import shutil
import subprocess
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
]

HARNESS = """<!doctype html><meta charset="utf-8"><body style="margin:0">
<pre id="out">pending</pre>
<script>
var out = [];
function ok(name, cond, info) { out.push((cond ? 'PASS ' : 'FAIL ') + name + (!cond && info ? ' (' + info + ')' : '')); }
function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
function frame(src, width) {
  return new Promise(function (resolve) {
    var f = document.createElement('iframe');
    f.style.cssText = 'border:0;display:block;width:' + width + 'px;height:900px';
    f.onload = function () { setTimeout(function () { resolve(f); }, 500); };
    f.src = src;
    document.body.appendChild(f);
  });
}
function rect(el) { return el.getBoundingClientRect(); }
function visible(w, el) { return !!el && w.getComputedStyle(el).display !== 'none' && rect(el).width > 0; }
// Problems with the header row at the iframe's width ([] when everything fits).
function headerProblems(f) {
  var w = f.contentWindow, d = w.document, vw = w.innerWidth, p = [];
  var join = d.querySelector('.btn--join'), search = d.querySelector('.search-toggle');
  var toggle = d.querySelector('.menu-toggle'), nav = d.querySelector('.nav-primary'), lang = d.querySelector('.lang-switch');
  if (search && visible(w, search) && rect(search).right > vw + 0.5) p.push('search icon off-screen');
  if (visible(w, toggle)) {
    if (rect(toggle).right > vw + 0.5) p.push('hamburger off-screen');
  } else {
    if (join && rect(join).right > vw + 0.5) p.push('Join off-screen at ' + Math.round(rect(join).right) + 'px');
    if (nav && lang && rect(nav).right > rect(lang).left + 0.5) p.push('menu overlaps the language switcher');
    if (nav && search && visible(w, search) && rect(nav).right > rect(search).left + 0.5) p.push('menu overlaps search');
  }
  return p;
}
async function main() {
%(body)s
}
main().catch(function (e) { out.push('FAIL harness crashed: ' + e); }).then(function () {
  document.getElementById('out').textContent = out.join('\\n');
});
</script>
"""

# Header fits (with JS) for ISOC-SE's six-item Swedish menu and for the demo.
FIT_BODY = """
  var cases = [['/', 1180], ['/', 1280], ['/', 1440], ['/', 1600], ['/', 1000]];
  for (var i = 0; i < cases.length; i++) {
    var f = await frame(cases[i][0], cases[i][1]);
    var p = headerProblems(f);
    ok('crowded header fits at ' + cases[i][1] + 'px', p.length === 0, p.join('; '));
    f.remove();
  }
  var g = await frame('/_nojs.html', 1440);
  var q = headerProblems(g);
  ok('crowded header fits at 1440px without JavaScript', q.length === 0, q.join('; '));
  g.remove();
"""

DEMO_BODY = """
  // Desktop: English and Swedish menus fit without collapsing to the hamburger.
  var widths = [1180, 1440];
  for (var i = 0; i < widths.length; i++) {
    var pages = ['/', '/sv/'];
    for (var j = 0; j < pages.length; j++) {
      var f = await frame(pages[j], widths[i]);
      var w = f.contentWindow, d = w.document;
      ok('demo ' + pages[j] + ' header fits at ' + widths[i] + 'px', headerProblems(f).length === 0, headerProblems(f).join('; '));
      ok('demo ' + pages[j] + ' keeps the desktop menu at ' + widths[i] + 'px',
         !visible(w, d.querySelector('.menu-toggle')) && visible(w, d.querySelector('.nav-primary')));
      f.remove();
    }
  }

  // Desktop dropdown opened by keyboard focus can be dismissed with Escape (WCAG 1.4.13).
  var f = await frame('/', 1440), w = f.contentWindow, d = w.document;
  var item = d.querySelector('.nav-primary .menu-item.has-children');
  var top = item.querySelector('a'), sub = item.querySelector('.menu--sub');
  top.focus();  // keyboard users Tab to the parent link first
  ok('focus opens the desktop dropdown', w.getComputedStyle(sub).display === 'block');
  sub.querySelector('a').focus();
  ok('Tab can move into the open dropdown', d.activeElement === sub.querySelector('a'));
  d.activeElement.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  ok('Escape hides a focus-opened dropdown', w.getComputedStyle(sub).display === 'none');
  ok('Escape returns focus to the parent menu link', d.activeElement === top);
  d.querySelector('.site-logo').focus();
  top.focus();
  ok('the dropdown opens again on the next focus', w.getComputedStyle(sub).display === 'block');
  f.remove();

  // Mobile menu, sub-menu, language dropdown and search panel (1000px viewport).
  f = await frame('/', 1000); w = f.contentWindow; d = w.document;
  var cs = function (el) { return w.getComputedStyle(el); };
  var mt = d.querySelector('[data-menu-toggle]'), nav = d.getElementById('site-nav');
  ok('mobile nav hidden before the toggle', cs(nav).display === 'none');
  mt.click();
  ok('menu toggle opens the menu', mt.getAttribute('aria-expanded') === 'true' && d.body.classList.contains('menu-open') && cs(nav).display === 'flex');
  ok('menu toggle label switches to close', mt.querySelector('.sr-only').textContent === 'Close menu');
  var st = d.querySelector('[data-submenu-toggle]'), sm = st.nextElementSibling;
  st.click();
  ok('submenu toggle opens the submenu', st.getAttribute('aria-expanded') === 'true' && cs(sm).display === 'block');
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  ok('Escape closes menu and submenu', mt.getAttribute('aria-expanded') === 'false' && st.getAttribute('aria-expanded') === 'false' && cs(nav).display === 'none');
  ok('focus returns to the menu toggle', d.activeElement === mt);
  mt.click();
  var lt = d.querySelector('[data-dropdown-toggle]');
  lt.click();
  ok('language menu opens', lt.getAttribute('aria-expanded') === 'true' && cs(lt.nextElementSibling).display === 'block');
  d.querySelector('main').click();
  ok('outside click closes the language menu', lt.getAttribute('aria-expanded') === 'false');
  mt.click();
  var stg = d.querySelector('[data-search-toggle]'), panel = d.getElementById('search-panel');
  stg.click();
  ok('search panel opens and focuses its input', !panel.hidden && d.activeElement === panel.querySelector('input'));
  var inp = panel.querySelector('input');
  inp.value = 'encryption';
  inp.dispatchEvent(new w.Event('input', { bubbles: true }));
  await wait(1500);
  ok('search shows live results', panel.querySelectorAll('.search-result').length === 2);
  d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  ok('Escape closes the search panel', panel.hidden && stg.getAttribute('aria-expanded') === 'false');
  f.remove();
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if not candidate:
            continue
        path = candidate if os.path.isabs(candidate) else shutil.which(candidate)
        if path and os.path.exists(path):
            return path
    return None


def run_chrome(chrome, url, *flags):
    """Dump the DOM of `url` after scripts ran. --no-sandbox is only a fallback
    for Linux CI runners that do not allow Chrome's sandbox (it changes rendering
    on macOS). Note: headless --dump-dom renders frames irregularly, so
    IntersectionObserver (reveal-on-scroll) is not asserted here; the static
    check motion_reveal_is_progressive and the screenshots cover it."""
    base = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", *flags, "--dump-dom", url]
    out = subprocess.run(base, capture_output=True, text=True, timeout=180).stdout
    if not out.strip() and sys.platform.startswith("linux"):
        out = subprocess.run(base[:2] + ["--no-sandbox"] + base[2:], capture_output=True, text=True, timeout=180).stdout
    return out


def serve(directory):
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=directory))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def run_harness(chrome, directory, name, body):
    with open(os.path.join(directory, name), "w", encoding="utf-8") as fh:
        fh.write(HARNESS % {"body": body})
    server, base = serve(directory)
    try:
        dom = run_chrome(chrome, f"{base}/{name}", "--window-size=1700,1100", "--virtual-time-budget=30000")
    finally:
        server.shutdown()
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    return html.unescape(m.group(1)).strip().splitlines() if m else [f"FAIL {name}: no harness output"]


def strip_scripts(directory, src, dest):
    with open(os.path.join(directory, src), encoding="utf-8") as fh:
        page = fh.read()
    with open(os.path.join(directory, dest), "w", encoding="utf-8") as fh:
        fh.write(re.sub(r"<script\b.*?</script>", "", page, flags=re.S))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--crowded", required=True)
    args = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        print("SKIP browser checks: no Chrome/Chromium found (set CHROME=/path/to/chrome)")
        return 0
    strip_scripts(args.crowded, "index.html", "_nojs.html")
    lines = run_harness(chrome, args.site, "_harness.html", DEMO_BODY)
    lines += run_harness(chrome, args.crowded, "_harness.html", FIT_BODY)
    for line in lines:
        print(line)
    failures = sum(1 for line in lines if not line.startswith("PASS"))
    print(f"\n{len(lines) - failures} passed, {failures} failed (browser)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

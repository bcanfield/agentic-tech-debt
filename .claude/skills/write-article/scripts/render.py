#!/usr/bin/env python3
"""Render a meme via memegen.link (no API key, ~350 templates) into articles/.

The agent picks the template and writes the lines — that's judgment. This just
handles the deterministic part: the memegen escaping rules and the download.

  --list                     print every template (id | lines | name | keywords)
                             so the agent can pick the format that fits the beat.
  <id> <slug> <l1> [l2 ...]  render and save to articles/<slug>.meme.png

memegen escaping (from api.memegen.link): spaces become underscores, so literal
underscores/dashes double up, and reserved chars get a ~ alias. We do it here so
the agent never hand-escapes a URL.

Usage:
  python3 render.py --list
  python3 render.py drake invisible-debt-is-the-problem "ship it" "wrote it down"
"""
import json
import sys
import urllib.parse
import urllib.request

API = "https://api.memegen.link"
TIMEOUT = 20
# memegen 403s the default urllib UA, so send a plain browser-ish one.
UA = {"User-Agent": "Mozilla/5.0 (debt-ops write-article meme renderer)"}

# Order matters: double the literals first, alias reserved chars, spaces last.
_RESERVED = {"?": "~q", "&": "~a", "%": "~p", "#": "~h", "/": "~s",
             "\\": "~b", "<": "~l", ">": "~g", '"': "''", "\n": "~n"}


def esc(line):
    line = line.replace("_", "__").replace("-", "--")
    for ch, alias in _RESERVED.items():
        line = line.replace(ch, alias)
    return line.replace(" ", "_") or "_"  # empty line -> blank


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT)


def get_json(path):
    with fetch(API + path) as r:
        return json.load(r)


def list_templates():
    rows = get_json("/templates")
    rows.sort(key=lambda t: t["id"])
    for t in rows:
        kw = ", ".join(t.get("keywords") or [])[:50]
        print(f"{t['id']:24} {t.get('lines', '?')}L  {t['name']:32} {kw}")
    print(f"\n{len(rows)} templates. Pick by what the FORMAT means, not the topic.")


def render(template, slug, lines):
    # validate the template + its line count before spending a download
    try:
        meta = get_json(f"/templates/{template}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f"unknown template '{template}' — run `render.py --list`")
        raise
    want = meta.get("lines")
    if want and len(lines) != want:
        print(f"  note: '{template}' expects {want} lines, got {len(lines)} "
              f"(memegen will pad/truncate)", file=sys.stderr)

    url = f"{API}/images/{template}/" + "/".join(esc(l) for l in lines) + ".png"
    out = f"articles/{slug}.meme.png"
    with fetch(url) as r, open(out, "wb") as f:
        f.write(r.read())
    print(out)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        list_templates()
    elif len(sys.argv) >= 4:
        render(sys.argv[1], sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)

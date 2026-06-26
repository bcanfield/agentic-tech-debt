#!/usr/bin/env python3
"""Stage an articles/<slug>.md file into the portfolio-2 repo for deploy.

The portfolio (Next.js + content-collections, deployed on Vercel at
brandincanfield.com) is the canonical home for every article and the host for its
images. Publishing there is just a file copy: the body is already MDX-safe
markdown, and image paths like `/foo.png` already map 1:1 onto the portfolio's
`public/` folder (so `public/foo.png` serves at `brandincanfield.com/foo.png`).

This copies the article to `content/<slug>.mdx` and every local image to
`public/`. It does NOT touch git — the SKILL drives commit/push/deploy-wait so
those steps stay visible. Re-running overwrites an existing copy, so don't run it
over a portfolio article you've since hand-edited (it would clobber your edits).

Outputs: copies files, prints the canonical URL and what it staged.

Usage:
  python3 stage.py articles/<slug>.md [--slug <portfolio-slug>] [--portfolio <dir>]
"""
import argparse
import os
import re
import shutil
import sys

DEFAULT_PORTFOLIO = "/Users/bcanfield/Documents/Git/portfolio-2"
SITE_URL = "https://brandincanfield.com"


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def split_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    header = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    fm = {}
    for line in header.splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm, body


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        return s[1:-1]
    return s


def local_images(fm, body, article_dir):
    """Every local (non-http) image referenced by the article: cover + inline."""
    refs = []
    cover = unquote(fm.get("image", "")) if "image" in fm else ""
    if cover and not cover.startswith("http"):
        refs.append(cover)
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", body):
        src = m.group(1).strip()
        if src and not src.startswith("http"):
            refs.append(src)
    # de-dupe, preserve order
    seen, out = set(), []
    for r in refs:
        key = r.lstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "ref": r,
            "abspath": os.path.abspath(os.path.join(article_dir, key)),
            "filename": os.path.basename(key),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("article")
    ap.add_argument("--slug", help="portfolio slug (default: the article's filename)")
    ap.add_argument("--portfolio", default=DEFAULT_PORTFOLIO)
    args = ap.parse_args()

    article = os.path.abspath(args.article)
    if not os.path.exists(article):
        die(f"no such file: {article}")
    portfolio = os.path.abspath(args.portfolio)
    content_dir = os.path.join(portfolio, "content")
    public_dir = os.path.join(portfolio, "public")
    if not os.path.isdir(content_dir) or not os.path.isdir(public_dir):
        die(f"portfolio repo not found (need content/ and public/ under {portfolio})")

    slug = args.slug or os.path.splitext(os.path.basename(article))[0]
    article_dir = os.path.dirname(article)

    with open(article, encoding="utf-8") as f:
        text = f.read()
    fm, body = split_frontmatter(text)
    images = local_images(fm, body, article_dir)

    missing = [im for im in images if not os.path.exists(im["abspath"])]
    if missing:
        for im in missing:
            print(f"  MISSING image: {im['abspath']}", file=sys.stderr)
        die(f"{len(missing)} referenced image(s) not found — fix before staging")

    # Copy the article verbatim as .mdx (body is already MDX-safe markdown).
    mdx_path = os.path.join(content_dir, f"{slug}.mdx")
    overwrote_mdx = os.path.exists(mdx_path)
    shutil.copyfile(article, mdx_path)

    # Copy each local image into public/ (filename preserved → URL matches the ref).
    copied = []
    for im in images:
        dest = os.path.join(public_dir, im["filename"])
        shutil.copyfile(im["abspath"], dest)
        copied.append((im["filename"], os.path.exists(dest)))

    canonical = f"{SITE_URL}/blog/{slug}"
    print(f"staged: {slug}")
    print(f"  mdx:       content/{slug}.mdx" + ("  [OVERWROTE existing]" if overwrote_mdx else ""))
    print(f"  images:    {len(copied)} → public/")
    for name, _ in copied:
        print(f"             - {name}  →  {SITE_URL}/{name}")
    print(f"  canonical: {canonical}")
    print(f"  portfolio: {portfolio}")
    print(f"  deploy-check URL: {canonical}")


if __name__ == "__main__":
    main()

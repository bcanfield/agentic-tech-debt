#!/usr/bin/env python3
"""Turn an articles/<slug>.md file into a ready-to-POST dev.to API payload.

dev.to (Forem) has a real write API — POST https://dev.to/api/articles with an
`api-key` header and a JSON body whose `body_markdown` takes raw markdown. No
browser, no pandoc. The one gap: dev.to has NO image upload, so cover + inline
images must be public URLs. We host them on the portfolio (brandincanfield.com),
so this rewrites every local image path to its brandincanfield.com URL and sets the
cover as `main_image`. canonical_url points back to the portfolio post.

Outputs (under <tmp>/devto-publish/<slug>/):
  article.json   the full {"article": {...}} payload for the API
  (prints the image URLs so the SKILL can HEAD-check them before posting)

Usage:
  python3 prepare.py articles/<slug>.md --canonical https://brandincanfield.com/blog/<slug> [--publish]
"""
import argparse
import json
import os
import re
import sys
import tempfile

DEVTO_MAX_TAGS = 4  # dev.to caps articles at 4 tags
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


def parse_tags(raw):
    inner = raw.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    tags = []
    for t in inner.split(","):
        t = unquote(t).strip().lower()
        t = re.sub(r"[^a-z0-9]", "", t)  # dev.to tags are alphanumeric only
        if t:
            tags.append(t)
    return tags[:DEVTO_MAX_TAGS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("article")
    ap.add_argument("--canonical", required=True,
                    help="canonical URL (the portfolio post: brandincanfield.com/blog/<slug>)")
    ap.add_argument("--image-base", default=SITE_URL,
                    help="base URL local images are hosted at (default brandincanfield.com)")
    ap.add_argument("--publish", action="store_true",
                    help="publish live (default: create as a draft)")
    args = ap.parse_args()

    article = os.path.abspath(args.article)
    if not os.path.exists(article):
        die(f"no such file: {article}")
    slug = os.path.splitext(os.path.basename(article))[0]
    base = args.image_base.rstrip("/")

    with open(article, encoding="utf-8") as f:
        fm, body = split_frontmatter(f.read())

    title = unquote(fm.get("title", "")) or slug
    description = unquote(fm.get("summary", ""))
    series = unquote(fm.get("series", "")) if "series" in fm else ""
    tags = parse_tags(fm.get("tags", "")) if "tags" in fm else []

    # Track every image URL we reference, so the SKILL can verify they're live.
    image_urls = []

    def to_url(src):
        src = src.strip()
        if src.startswith("http://") or src.startswith("https://"):
            return src  # already remote — leave it
        url = f"{base}/{src.lstrip('/')}"
        image_urls.append(url)
        return url

    # Cover → main_image (frontmatter `image`).
    cover_local = unquote(fm.get("image", "")) if "image" in fm else ""
    main_image = to_url(cover_local) if cover_local else None

    # Inline images → rewrite each ![alt](local) to the hosted URL.
    def repl(m):
        return f"![{m.group(1)}]({to_url(m.group(2))})"

    body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, body)

    article_obj = {
        "title": title,
        "body_markdown": body,
        "published": bool(args.publish),
        # dev.to wants tags as a JSON array — a comma-separated string is silently
        # ignored on POST (post publishes with zero tags).
        "tags": tags,
        "canonical_url": args.canonical,
    }
    if description:
        article_obj["description"] = description
    if series:
        article_obj["series"] = series
    if main_image:
        article_obj["main_image"] = main_image

    out_dir = os.path.join(tempfile.gettempdir(), "devto-publish", slug)
    os.makedirs(out_dir, exist_ok=True)
    payload_path = os.path.join(out_dir, "article.json")
    with open(payload_path, "w", encoding="utf-8") as f:
        json.dump({"article": article_obj}, f, indent=2)

    print(f"prepared: {slug}")
    print(f"  title:     {title}")
    print(f"  tags:      {', '.join(tags) or '(none)'}")
    print(f"  series:    {series or '(none)'}")
    print(f"  canonical: {args.canonical}")
    print(f"  cover:     {main_image or '(none)'}")
    print(f"  published: {bool(args.publish)}  ({'LIVE' if args.publish else 'draft'})")
    print(f"  image URLs to verify ({len(image_urls)}):")
    for u in image_urls:
        print(f"    {u}")
    print(f"  payload:   {payload_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Turn an articles/<slug>.md file into what the Hashnode publish playbook needs.

Hashnode's editor is markdown-native (paste raw markdown, it renders) AND it
rehosts pasted image Files to its own CDN — so we keep the body as markdown and
inject every local image as a File (no GitHub raw-URL hot-linking, no branch
dependency; published posts are self-contained). Mirrors the publish-to-medium
prepare.py, minus the HTML step.

Outputs (under <tmp>/hashnode-publish/<slug>/):
  manifest.json   title, tags, cover_abspath, inline image list (with inject_js)
  body.md         markdown body; local inline images replaced with ⟦IMAGE:img-N⟧ markers
  img-N.js        a File-paste injector per local inline image

Usage:
  python3 prepare.py articles/my-slug.md
"""
import base64
import json
import os
import re
import sys
import tempfile

HASHNODE_MAX_TAGS = 5


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
    tags = [unquote(t) for t in inner.split(",") if t.strip()]
    return [t for t in tags if t][:HASHNODE_MAX_TAGS]


def placeholder_for(idx):
    return f"⟦IMAGE:img-{idx}⟧"


def build_image_js(abspath):
    """agent-browser `eval` payload: inject one local image as a File.

    Hashnode's body editor accepts a synthetic paste carrying a File and uploads it
    to cdn.hashnode.com. The agent empties the marker line first, then runs this.
    """
    with open(abspath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    name = os.path.basename(abspath)
    mime = "image/png" if abspath.lower().endswith(".png") else "image/jpeg"
    return (
        "(()=>{"
        f'const B64="{b64}";const name="{name}";const mime="{mime}";'
        "const bytes=Uint8Array.from(atob(B64),c=>c.charCodeAt(0));"
        "const file=new File([bytes],name,{type:mime});"
        "const ed=document.querySelector('[contenteditable=\"true\"]');"
        "if(!ed)return 'NO_EDITOR';ed.focus();"
        "const dt=new DataTransfer();dt.items.add(file);"
        "ed.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));"
        "return 'IMG dispatched '+file.size+'B (wait for a cdn.hashnode img)';"
        "})()"
    )


def main():
    args = list(sys.argv[1:])
    if len(args) != 1:
        die("usage: prepare.py articles/<slug>.md")
    article = os.path.abspath(args[0])
    if not os.path.exists(article):
        die(f"no such file: {article}")
    slug = os.path.splitext(os.path.basename(article))[0]
    article_dir = os.path.dirname(article)

    with open(article, encoding="utf-8") as f:
        text = f.read()
    fm, body = split_frontmatter(text)

    title = unquote(fm.get("title", "")) or slug
    tags = parse_tags(fm.get("tags", "")) if "tags" in fm else []
    cover_local = unquote(fm.get("image", "")) if "image" in fm else ""
    cover_abspath = (
        os.path.abspath(os.path.join(article_dir, cover_local.lstrip("/")))
        if cover_local else ""
    )

    # Replace each local inline image with a marker; collect for File injection.
    images = []

    def repl(m):
        alt, src = m.group(1), m.group(2).strip()
        if src.startswith("http://") or src.startswith("https://"):
            return m.group(0)  # already hosted — leave it in the markdown
        idx = len(images)
        abspath = os.path.abspath(os.path.join(article_dir, src.lstrip("/")))
        ph = placeholder_for(idx)
        images.append({
            "alt": alt, "abspath": abspath,
            "exists": os.path.exists(abspath), "placeholder": ph,
        })
        return ph

    body = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, body)

    out_dir = os.path.join(tempfile.gettempdir(), "hashnode-publish", slug)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "body.md"), "w", encoding="utf-8") as f:
        f.write(body)
    for idx, im in enumerate(images):
        if im["exists"]:
            js_path = os.path.join(out_dir, f"img-{idx}.js")
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(build_image_js(im["abspath"]))
            im["inject_js"] = js_path

    manifest = {
        "slug": slug, "title": title, "tags": tags,
        "cover_abspath": cover_abspath, "images": images, "out_dir": out_dir,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"prepared: {slug}")
    print(f"  title:    {title}")
    print(f"  tags:     {', '.join(tags) or '(none)'}")
    cov = "(none)"
    if cover_abspath:
        cov = os.path.basename(cover_abspath) + ("" if os.path.exists(cover_abspath) else "  [MISSING]")
    print(f"  cover:    {cov}  (uploaded as a file)")
    print(f"  inline images: {len(images)} (injected as Files → cdn.hashnode)")
    for im in images:
        flag = "" if im["exists"] else "  [MISSING]"
        print(f"            - {os.path.basename(im['abspath'])}  (@ {im['placeholder']}){flag}")
    print(f"  body.md:  {os.path.join(out_dir, 'body.md')}")
    print(f"  out_dir:  {out_dir}")


if __name__ == "__main__":
    main()

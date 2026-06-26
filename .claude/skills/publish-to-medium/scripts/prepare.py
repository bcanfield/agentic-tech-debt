#!/usr/bin/env python3
"""Turn an articles/<slug>.md file into everything the publish playbook needs.

The agent drives the browser; this just handles the deterministic parts that are
easy to get subtly wrong by hand: frontmatter parsing, markdown->clean-HTML via
pandoc, image discovery, and emitting a ready-to-run paste injector.

Outputs (under <tmp>/medium-publish/<slug>/):
  manifest.json   title, subtitle, tags (<=5), and the image list (local vs remote)
  body.html       clean HTML for the post body (no frontmatter, no title)
  paste.js        an agent-browser `eval` payload that injects body.html into the
                  focused Medium editor via a synthetic paste event

Usage:
  python3 prepare.py articles/my-slug.md
  python3 prepare.py articles/my-slug.md --out /some/dir
"""
import base64
import json
import os
import re
import subprocess
import sys
import tempfile

PANDOC_TIMEOUT = 30
MEDIUM_MAX_TAGS = 5


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def split_frontmatter(text):
    """Return (frontmatter_dict, body) for a `---`-delimited YAML header.

    We only need title/summary/tags/image, so we parse those by hand rather than
    take a pyyaml dependency — the fields are simple scalars and one flat list.
    """
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
        if not m:
            continue
        key, raw = m.group(1), m.group(2).strip()
        fm[key] = raw
    return fm, body


def unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] in "\"'" and s[-1] == s[0]:
        return s[1:-1]
    return s


def parse_tags(raw):
    # tags: ["ai", "technicaldebt", ...]  ->  list of strings, capped for Medium
    inner = raw.strip()
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1]
    tags = [unquote(t) for t in inner.split(",") if t.strip()]
    return [t for t in tags if t][:MEDIUM_MAX_TAGS]


def find_images(body, frontmatter, article_dir):
    """Collect cover image + inline body images, flagged local vs remote.

    Medium re-hosts remote https images on paste, but local files have to be
    uploaded through the editor — so the agent needs the absolute paths.
    """
    images = []
    seen = set()

    def add(src, alt):
        src = src.strip()
        if not src or src in seen:
            return
        seen.add(src)
        remote = src.startswith("http://") or src.startswith("https://")
        abspath = None
        if not remote:
            # frontmatter image is "/slug.cover.jpg" (leading slash = articles dir)
            rel = src[1:] if src.startswith("/") else src
            abspath = os.path.abspath(os.path.join(article_dir, rel))
        images.append({
            "src": src,
            "alt": alt,
            "kind": "remote" if remote else "local",
            "abspath": abspath,
            "exists": bool(abspath and os.path.exists(abspath)),
        })

    cover = frontmatter.get("image")
    if cover:
        add(unquote(cover), "cover")
    for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body):
        add(src, alt)
    return images


def render_html(body, workdir):
    src = os.path.join(workdir, "body.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write(body)
    try:
        out = subprocess.run(
            ["pandoc", "-f", "gfm", "-t", "html", "--syntax-highlighting=none", src],
            capture_output=True, text=True, timeout=PANDOC_TIMEOUT,
        )
    except FileNotFoundError:
        die("pandoc not found — install it (brew install pandoc)")
    except subprocess.TimeoutExpired:
        die("pandoc timed out")
    if out.returncode != 0:
        die(f"pandoc failed: {out.stderr.strip()}")
    return out.stdout.strip()


def placeholder_for(idx):
    # A findable marker the agent locates after pasting, then swaps for the image.
    return f"⟦IMAGE:img-{idx}⟧"


def swap_local_imgs(html, images):
    """Replace each local <img> in the body with a placeholder paragraph.

    Medium can't load a local `src`, so an inline `![](/x.png)` would publish as a
    broken empty image. We pull it out and leave a marker; the agent injects the
    real file at that spot (Step 5). Remote images are left alone — Medium loads them.
    Mutates `images` to tag which ones are inline (carry a placeholder).
    """
    src_to_idx = {im["src"]: i for i, im in enumerate(images)}

    def repl(m):
        src = m.group(1)
        idx = src_to_idx.get(src)
        if idx is not None and images[idx]["kind"] == "local":
            ph = placeholder_for(idx)
            images[idx]["placeholder"] = ph
            return f"<p>{ph}</p>"
        return m.group(0)  # remote or unknown — keep as-is

    return re.sub(r'<img[^>]*\bsrc="([^"]+)"[^>]*>', repl, html)


def build_paste_js(html):
    """A self-contained agent-browser `eval` payload.

    Dispatches a synthetic paste event carrying text/html at the focused editor —
    Medium's own paste handler reads clipboardData.getData('text/html'). Returns a
    string the agent inspects to confirm the content actually landed.
    """
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return (
        "(()=>{"
        f'const B64="{b64}";'
        "const bytes=Uint8Array.from(atob(B64),c=>c.charCodeAt(0));"
        "const html=new TextDecoder().decode(bytes);"
        "const tmp=document.createElement('div');tmp.innerHTML=html;"
        "const plain=tmp.innerText;"
        "let t=document.activeElement;"
        "t=(t&&t.closest&&t.closest('[contenteditable=\"true\"]'))||document.querySelector('[contenteditable=\"true\"]');"
        "if(!t)return 'NO_EDITOR: click into the story body first';"
        "t.focus();"
        "const dt=new DataTransfer();dt.setData('text/html',html);dt.setData('text/plain',plain);"
        "const ev=new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true});"
        "t.dispatchEvent(ev);"
        "const n=t.querySelectorAll('h1,h2,h3,p,pre,blockquote,li,img').length;"
        "return 'RESULT blocks='+n;"
        "})()"
    )


# JPEG/PNG magic — enough to set the right MIME on the pasted File.
def _mime_for(path):
    return "image/png" if path.lower().endswith(".png") else "image/jpeg"


def build_image_js(abspath):
    """An agent-browser `eval` payload that injects one local image.

    Same trick as the body: dispatch a synthetic paste carrying the image as a
    File. Medium's paste handler uploads it to its CDN — no OS file dialog. The
    agent places the caret on an empty line first; this pastes there.
    """
    with open(abspath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    name = os.path.basename(abspath)
    mime = _mime_for(abspath)
    return (
        "(()=>{"
        f'const B64="{b64}";'
        f'const name="{name}";const mime="{mime}";'
        "const bytes=Uint8Array.from(atob(B64),c=>c.charCodeAt(0));"
        "const file=new File([bytes],name,{type:mime});"
        "let t=document.activeElement;"
        "t=(t&&t.closest&&t.closest('[contenteditable=\"true\"]'))||document.querySelector('[contenteditable=\"true\"]');"
        "if(!t)return 'NO_EDITOR';"
        "t.focus();"
        "const dt=new DataTransfer();dt.items.add(file);"
        "const ev=new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true});"
        "t.dispatchEvent(ev);"
        "return 'IMG dispatched '+file.size+'B (wait, then check for a new cdn-images img)';"
        "})()"
    )


def main():
    args = [a for a in sys.argv[1:]]
    out_dir = None
    if "--out" in args:
        i = args.index("--out")
        out_dir = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        die("usage: prepare.py articles/<slug>.md [--out DIR]")

    article = os.path.abspath(args[0])
    if not os.path.exists(article):
        die(f"no such file: {article}")
    slug = os.path.splitext(os.path.basename(article))[0]
    article_dir = os.path.dirname(article)

    with open(article, encoding="utf-8") as f:
        text = f.read()
    fm, body = split_frontmatter(text)

    title = unquote(fm.get("title", "")) or slug
    subtitle = unquote(fm.get("summary", ""))
    tags = parse_tags(fm.get("tags", "")) if "tags" in fm else []
    images = find_images(body, fm, article_dir)

    if out_dir is None:
        out_dir = os.path.join(tempfile.gettempdir(), "medium-publish", slug)
    os.makedirs(out_dir, exist_ok=True)

    html = render_html(body, out_dir)
    # Pull local inline images out of the body — they'd publish broken otherwise.
    html = swap_local_imgs(html, images)
    with open(os.path.join(out_dir, "body.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(out_dir, "paste.js"), "w", encoding="utf-8") as f:
        f.write(build_paste_js(html))

    # One image-paste injector per existing local image; record its path on the image.
    for idx, im in enumerate(images):
        if im["kind"] == "local" and im["exists"]:
            js_path = os.path.join(out_dir, f"img-{idx}.js")
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(build_image_js(im["abspath"]))
            im["inject_js"] = js_path

    manifest = {
        "slug": slug,
        "title": title,
        "subtitle": subtitle,
        "tags": tags,
        "images": images,
        "out_dir": out_dir,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Human summary
    local_imgs = [i for i in images if i["kind"] == "local"]
    print(f"prepared: {slug}")
    print(f"  title:    {title}")
    print(f"  subtitle: {subtitle or '(none)'}")
    print(f"  tags:     {', '.join(tags) or '(none)'}")
    print(f"  images:   {len(images)} ({len(local_imgs)} local to upload, "
          f"{len(images) - len(local_imgs)} remote)")
    for im in local_imgs:
        flag = "" if im["exists"] else "  [MISSING]"
        # inline images carry a placeholder; the cover (frontmatter) goes at top
        where = f"@ {im['placeholder']}" if im.get("placeholder") else "cover → top"
        print(f"            - {os.path.basename(im['abspath'])}  ({where}){flag}")
    print(f"  out_dir:  {out_dir}")


if __name__ == "__main__":
    main()

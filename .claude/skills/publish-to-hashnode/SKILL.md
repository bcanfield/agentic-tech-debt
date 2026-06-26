---
name: publish-to-hashnode
description: Publish an article from articles/<slug>.md to Hashnode as a live post, driving a logged-in browser via agent-browser. Use when the user asks to "post to Hashnode", "publish on Hashnode", or to wire Hashnode publishing into a routine. Hashnode's editor is markdown-native; images are uploaded as files and rehosted on Hashnode's CDN. Not for Medium/dev.to.
---

# Publish to Hashnode

Hashnode's GraphQL publish API is a paid feature, so we drive the editor in a
logged-in browser with **agent-browser**. The editor is **markdown-native** (paste
raw markdown, it renders) — no HTML conversion. Images (cover + inline) are uploaded
as **Files** so Hashnode rehosts them on `cdn.hashnode.com`; published posts are
self-contained (no external URL or git-branch dependency). This file is
self-sufficient; the sibling `publish-to-medium` skill follows the same shape.

**Inputs:** an `articles/<slug>.md` file. **Output:** a live Hashnode post; you return its URL.

## Prerequisites (check first)

1. **Tools:** `agent-browser` on PATH. (No pandoc — markdown goes in raw. No git/repo
   dependency — images are uploaded as Files, not linked.)
2. **A logged-in Hashnode session.** Persistent session named `hashnode`; for the
   one-time login launch it **headed + de-automated** (same Cloudflare/visibility
   reasons as Medium):

   ```bash
   agent-browser --session-name hashnode --headed \
     --args "--disable-blink-features=AutomationControlled" open https://hashnode.com
   ```

   User signs in by hand once. Confirm logged-in via snapshot before proceeding.

> **Two environment gotchas (both bit during development):**
> - **Daemon reuse.** `agent-browser` runs one shared background daemon. If a daemon
>   is already up (e.g. a session for another site like `medium`), `--headed`/`--args`
>   on a new `open` are **silently ignored** — you get the existing, often headless,
>   browser (symptom: no visible window for login). Fix: `agent-browser close --all`,
>   then relaunch with the headed login command above.
> - **Sandbox (Claude Code).** agent-browser needs its socket dir `~/.agent-browser`;
>   the Bash sandbox blocks it (`Socket directory '/…/.agent-browser' is not writable
>   … os error 1`). Run agent-browser commands with the sandbox disabled.

> **First run supervised.** Selectors below are confirmed by live exploration on
> first use; watch the snapshots and confirm before Publish.

## Step 1 — Prep

```bash
python3 .claude/skills/publish-to-hashnode/scripts/prepare.py articles/<slug>.md
```

Writes `body.md` (markdown; local inline images replaced with `⟦IMAGE:img-N⟧`
markers) + per-image `img-N.js` File injectors + `manifest.json` (`title`, `tags`,
`cover_abspath`, `images[]`) to `<tmp>/hashnode-publish/<slug>/`. Read the manifest.

## Step 2 — Open a fresh draft, confirm login

```bash
agent-browser --session-name hashnode open https://hashnode.com 2>&1 | head -1
agent-browser --session-name hashnode snapshot -i      # logged in? (Feed/Write/Dashboard, not "Sign in")
```

If a sign-in page shows, **stop** and have the user run the login command. Then click
**Write** (opens `hashnode.com/draft/<id>`). The Write button reopens the *last*
draft — if it has content, click **New** to get a blank one. Verified editor fields:
`textbox "Article Title..."`, a body `[contenteditable="true"]`, a `"Cover"` button,
and `"Publish"` (upper-right). Refs change per load — snapshot for current ones.

## Step 3 — Title

The title is a `textarea[placeholder="Article Title..."]` — `find role textbox`
misses it. Focus it by that CSS selector, then `keyboard type` the title:

```bash
agent-browser --session-name hashnode eval '(()=>{const t=document.querySelector("[placeholder=\"Article Title...\"]");t.focus();return t.tagName;})()'
agent-browser --session-name hashnode keyboard type "<title from manifest>"
```

## Step 4 — Body (paste raw markdown)

Hashnode converts pasted markdown to rich text — headings, code, and links all
render. Local images aren't here yet (they're `⟦IMAGE:img-N⟧` markers, injected as
Files in Step 4b). Click into the body contenteditable, then paste `body.md` as
**text/plain** via a synthetic paste:

```bash
OUT="<out_dir from manifest>"
B64=$(base64 < "$OUT/body.md" | tr -d '\n')
agent-browser --session-name hashnode eval "(()=>{const md=new TextDecoder().decode(Uint8Array.from(atob('$B64'),c=>c.charCodeAt(0)));const t=document.querySelector('[contenteditable=\"true\"]');if(!t)return 'NO_EDITOR';t.focus();const dt=new DataTransfer();dt.setData('text/plain',md);t.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));return 'pasted '+md.length+' chars';})()"
```

**Verify** via snapshot/eval: paragraphs and code (`pre`) appear, and the body
contains the `⟦IMAGE:img-N⟧` markers (those become images in the next step). Any
already-remote `https` images render directly.

## Step 4b — Inline images (inject as Files at their markers)

Each local inline image has an `inject_js` in the manifest. Hashnode rehosts a
pasted image File to `cdn.hashnode.com`. Like Medium, image-paste *inserts* rather
than replacing, so empty the marker line first, then inject:

```bash
# select the marker paragraph, Backspace to empty it (caret stays), then inject
agent-browser --session-name hashnode eval '(()=>{const ed=document.querySelector("[contenteditable=\"true\"]");const p=[...ed.querySelectorAll("p")].find(p=>p.textContent.includes("⟦IMAGE:img-0⟧"));if(!p)return "marker not found";const r=document.createRange();r.selectNodeContents(p);const s=getSelection();s.removeAllRanges();s.addRange(r);ed.focus();return "selected";})()'
agent-browser --session-name hashnode press "Backspace"
agent-browser --session-name hashnode eval "$(cat "$OUT/img-0.js")"
sleep 5   # Hashnode uploads to its CDN
```

**Verify:** a new `img` with a `cdn.hashnode.com` src appears and no `⟦IMAGE:…⟧`
markers remain (`get text` on the editor).

## Step 5 — Cover image (upload the local file)

Hashnode's cover widget is Upload/Unsplash only (no URL field), but it has a hidden
`input[type=file]` — set it directly with the manifest's `cover_abspath` (no OS
dialog). Open the cover widget first so the input exists:

```bash
agent-browser --session-name hashnode find role button click --name "Cover"
agent-browser --session-name hashnode upload 'input[type=file]' "<cover_abspath from manifest>"
sleep 4   # uploads; then "Change cover"/"Delete cover" appear = success
```

## Step 6 — Tags (in the Publish panel)

Click **Publish** (upper-right) → "Draft settings" dialog opens → **Discovery** tab →
`textbox "Tags"`. Hashnode tags are a fixed taxonomy with autocomplete: for each tag
in the manifest, focus the Tags box, `keyboard type` it, wait ~1.5s, then **click the
matching suggestion** to commit it.

> **Two gotchas that bite hard (verified June 2026):**
> - **You MUST click the suggestion — typing + Enter does nothing.** The box does not
>   clear on its own; if you just type each tag, they **concatenate** into one garbage
>   string (`aiopensourcetechnicaldebt…`). Clicking the suggestion is what adds the
>   chip and clears the box. (If it accumulated, select-all + Backspace to clear.)
> - **Suggestion text has NO space between tag and count** — it's `#ai38,235 posts`,
>   not `#ai 38,235 posts`. So a `startsWith("#ai ")` match fails. Match the tag token
>   with a regex that stops at the first digit:
>   ```bash
>   # after typing one tag, click its exact suggestion:
>   agent-browser --session-name hashnode eval '(()=>{const want="ai";const b=[...document.querySelectorAll("button")].filter(x=>/posts/.test(x.textContent)).find(x=>{const m=x.textContent.trim().match(/^#([a-zA-Z0-9-]+?)\d/);return m&&m[1].toLowerCase()===want;});if(!b)return "NO_MATCH";b.setAttribute("data-ab","tg");return "ok";})()'
>   agent-browser --session-name hashnode click '[data-ab="tg"]'
>   ```
> - **Re-focus the Tags box before each tag** (`[...document.querySelectorAll("input,textarea")].find(e=>/tag/i.test(e.placeholder||"")).focus()`).

NOTE: some canonical tags have a cuid-suffixed slug (e.g. `#programming-ciovqvfcb008…`)
— that's the *real* tag (displays as "#programming" to readers), not a malformed custom
one, so don't "fix" it; the regex above won't match it (the cuid has letters after the
digits), so click that suggestion by its `startsWith("#programming-")` prefix instead.
Added tags show as chip buttons; click a chip to remove it.

**Canonical URL (cross-posting).** Same tab, find the SEO / "canonical URL" field
(it may be behind a "This article is originally published elsewhere" / canonical
checkbox). Set it to the **portfolio** post — `https://brandincanfield.com/blog/<slug>`
— so Hashnode doesn't compete with your site for SEO. Publish the portfolio first
(`publish-to-portfolio`) to have that URL; Medium and dev.to point at the same one.
(Same tab also has slug + other SEO fields — optional.)

## Step 7 — Publish

> Public and hard to undo — only when the user asked to publish (else stop at draft).

Confirm the **Attribution** tab shows the right publication, then click the **dialog's**
Publish button — *not* via `find role button --name "Publish"` (that hits the header
button and just toggles the dialog). Mark and click it directly, e.g.:

```bash
agent-browser --session-name hashnode eval '(()=>{const d=document.querySelector("[role=dialog]");const b=[...d.querySelectorAll("button")].find(x=>x.textContent.trim()==="Publish");b.setAttribute("data-ab","pub");return "ok";})()'
agent-browser --session-name hashnode click '[data-ab="pub"]'
```

On success the URL goes `/draft/…` → `/edit/…` and the header button flips
"Publish" → "Update". The `/edit` page has no canonical link, so get the public URL
from the publication dashboard (a `*.hashnode.dev` link) — it's `<blog>/<slug>` (the
slug is on the Discovery tab). Return that URL.

## Notes

- **Scheduling:** Hashnode has a native **Scheduling** tab in the publish dialog, but
  per project convention scheduling stays separate — a routine calls this skill.
- **Drafts** autosave — for a draft, do Steps 1–6 and stop.
- **Self-contained images:** both cover and inline images are uploaded as Files and
  rehosted on `cdn.hashnode.com`, so there's no GitHub/branch dependency — a published
  post keeps its images even if the source branch is deleted.

---
name: publish-to-medium
description: Publish an article from articles/<slug>.md to Medium as a live post, driving a logged-in browser via agent-browser. Use when the user asks to "post to Medium", "publish on Medium", "push this article to Medium", or to wire Medium publishing into a scheduled routine. Handles markdown→Medium formatting, tags, and image upload. Not for dev.to/blog targets.
---

# Publish to Medium

Medium closed its API to new integrations (Jan 2025) — no token path. So we drive
the real editor in a logged-in browser with **agent-browser**, the same way a human
would paste a formatted draft and hit Publish. This skill is agent-driven: a Python
helper does the deterministic prep, then you steer the browser off live snapshots.

**Inputs:** an `articles/<slug>.md` file (frontmatter + markdown body).
**Output:** a live Medium post; you return its URL.

## Prerequisites (check first, once)

1. **Tools:** `agent-browser` and `pandoc` on PATH. (`agent-browser --version`, `which pandoc`.)
2. **A logged-in Medium session.** Everything uses a persistent session named
   `medium` so the login survives between runs (and future scheduled runs). For the
   **one-time login**, launch it **headed** (visible) and de-automated — Medium sits
   behind Cloudflare, which blocks the default headless automation browser with a
   "Just a moment…" wall and, being headless, shows no window to log in through:

   ```bash
   agent-browser --session-name medium --headed \
     --args "--disable-blink-features=AutomationControlled" open https://medium.com
   ```

   In that window the user signs in **once, by hand** (Google/email — captchas and
   2FA mean you can't script it). Confirm with a snapshot: a logged-out page shows
   "Sign in"/"Get started"; logged-in shows the avatar and a working "Write". After
   login the session cookies persist, so later publish runs can reuse `--session-name
   medium`. Keep `--headed --args "--disable-blink-features=AutomationControlled"` on
   the publish runs too, or Cloudflare may re-challenge. Don't try to automate login.

> **Two environment gotchas (both bit during development):**
> - **Daemon reuse.** `agent-browser` runs one shared background daemon. If a daemon
>   is already up (e.g. a session for another site), `--headed`/`--args` on a new
>   `open` are **silently ignored** — you get the existing, often headless, browser
>   (symptom: no visible window for login, or a stale page). Fix: `agent-browser
>   close --all`, then relaunch with the headed login command above.
> - **Sandbox (Claude Code).** agent-browser needs its socket dir `~/.agent-browser`;
>   the Bash sandbox blocks it (`Socket directory '/…/.agent-browser' is not writable
>   … os error 1`). Run agent-browser commands with the sandbox disabled.

> **First run is supervised.** The text-injection primitive and the prep are tested,
> but Medium's exact editor/publish-dialog selectors can shift. On the first real
> publish, watch the snapshots and confirm each step before clicking Publish. Once
> it's confirmed working, later runs (and a routine) can trust the flow.

## Step 1 — Prep the article

```bash
python3 .claude/skills/publish-to-medium/scripts/prepare.py articles/<slug>.md
```

This prints the title/subtitle/tags/images and writes to `<tmpdir>/medium-publish/<slug>/`:

- `manifest.json` — title, subtitle, tags (capped at Medium's 5), image list
- `body.html` — clean HTML for the body
- `paste.js` — a ready-to-run injector (see Step 4)

Read the manifest. Note the **local images** — those must be uploaded by hand
through the editor (Medium only auto-imports remote `https` images on paste).

## Step 2 — Open the editor, confirm you're logged in

```bash
agent-browser --session-name medium open https://medium.com/new-story
agent-browser --session-name medium snapshot -i
```

If the snapshot shows a sign-in / "Get started" page instead of an editor, the
session isn't logged in — **stop** and tell the user to run the login command
above. Don't proceed.

## Step 3 — Inject the body (do this BEFORE the title)

Order matters: **paste the body first, set the title last.** Pasting rebuilds the
editor's first block, so any title typed beforehand gets wiped. (Verified on the
live editor.)

Medium's editor is one contenteditable; the title is `h3.graf` and the body starts
at `p.graf`. The element `id`s are dynamic — don't target them; use those classes.
`click`-by-selector is unreliable here, so place the caret with `eval`, then paste.

```bash
OUT="<out_dir from the manifest>"
# caret into the body paragraph (first p.graf), so the paste lands in the body
agent-browser --session-name medium eval '(()=>{const ed=document.querySelector("[contenteditable=\"true\"]");const p=ed.querySelector("p.graf");const r=document.createRange();r.selectNodeContents(p);r.collapse(true);const s=getSelection();s.removeAllRanges();s.addRange(r);return "caret in body";})()'
# inject the body HTML via synthetic paste — Medium's own handler ingests it
agent-browser --session-name medium eval "$(cat "$OUT/paste.js")"
```

The injector returns `RESULT blocks=N`. **Verify:** snapshot and confirm the
paragraphs/headings/code/blockquotes are in the editor (inline code, bold, links
and code fences all convert correctly).

If it returns `NO_EDITOR` or the editor stays empty, escalate through these
fallbacks, re-checking after each:

1. **Real paste.** Put the HTML on the system clipboard and send a real paste:
   ```bash
   hex=$(python3 -c "import sys;print(open('$OUT/body.html','rb').read().hex())")
   osascript -e "set the clipboard to «data HTML${hex}»"
   ```
   then bring Chrome to the front and send a genuine Cmd+V (macOS):
   ```bash
   osascript -e 'tell application "Google Chrome" to activate' \
             -e 'tell application "System Events" to keystroke "v" using command down'
   ```
   (Needs Accessibility permission for the terminal; truest to a human paste.)
2. **insertHTML.** As a last resort, in the focused editor:
   `agent-browser --session-name medium eval "document.execCommand('insertHTML',false,<body html>)"`
   — verify it sticks (Medium's editor may re-normalize it).

## Step 4 — Title (last, after the body is in)

The paste left an empty `h3.graf` as the first block. Put the caret in it and type
the title from the manifest with real keystrokes (it commits to Medium's model and
survives because nothing pastes after it):

```bash
agent-browser --session-name medium eval '(()=>{const ed=document.querySelector("[contenteditable=\"true\"]");const t=ed.querySelector("h3.graf");ed.focus();const r=document.createRange();r.selectNodeContents(t);r.collapse(true);const s=getSelection();s.removeAllRanges();s.addRange(r);return "caret in title";})()'
agent-browser --session-name medium keyboard type "<title from manifest>"
```

Verify: `eval` the title text reads back clean (no `Title` placeholder appended).
For a subtitle, Medium derives the preview from an early line; if you want it
explicit, the manifest's `subtitle` can go in as the first body paragraph before
the paste — optional, skip if the body already opens strong.

## Step 5 — Images

Every **local** image in the manifest has an `inject_js` file — an image-paste
injector (same synthetic-paste trick, carrying the file as a `File`; Medium uploads
it to its CDN, no OS file dialog). Don't use `agent-browser upload` — Medium has no
persistent file input, and the add-image button opens an OS picker automation can't
drive. Local images left as `<img>` in the pasted body would publish **broken**
(empty `src`), which is why `prepare.py` pulls them out. Verified working.

Two kinds, both in the manifest's `images`:

**Cover** (the frontmatter `image`, no `placeholder`) → goes at the very top, since
Medium uses the first image as the post preview. Make an empty first line, inject:

```bash
agent-browser --session-name medium eval '(()=>{const ed=document.querySelector("[contenteditable=\"true\"]");const t=ed.querySelector("h3.graf");const r=document.createRange();r.selectNodeContents(t);r.collapse(false);const s=getSelection();s.removeAllRanges();s.addRange(r);return "ok";})()'
agent-browser --session-name medium press "Enter"
agent-browser --session-name medium eval "$(cat "$OUT/img-0.js")"   # cover is usually img-0
sleep 5
```

**Inline images** (diagram, meme — each has a `placeholder` like `⟦IMAGE:img-2⟧`)
→ `prepare.py` left that marker text where the image belongs in the body. Image-paste
*inserts* (it doesn't replace a selection), so **delete the marker first**, then
inject into the emptied line:

```bash
# select the marker paragraph by its text, then Backspace to empty it (caret stays)
agent-browser --session-name medium eval '(()=>{const ed=document.querySelector("[contenteditable=\"true\"]");const p=[...ed.querySelectorAll("p")].find(p=>p.textContent.includes("⟦IMAGE:img-2⟧"));if(!p)return "marker not found";const r=document.createRange();r.selectNodeContents(p);const s=getSelection();s.removeAllRanges();s.addRange(r);ed.focus();return "selected";})()'
agent-browser --session-name medium press "Backspace"
agent-browser --session-name medium eval "$(cat "$OUT/img-2.js")"   # injects at the now-empty line
sleep 5
```

**Verify** after each: a new `img` with a `cdn-images-1.medium.com`/`miro.medium.com`
src appears and no `⟦IMAGE:…⟧` markers remain (`get text` on the editor). Skip
remote `https` images — they came in with the body paste.

## Step 6 — Publish

> Publishing is public and hard to undo. Only do it when the user asked to publish
> (vs. leaving a draft). For drafts, stop after Step 5.

1. Click **Publish** (top-right): `agent-browser --session-name medium find role button click --name "Publish"`.
2. A **Topics** dialog opens with an "Add a topic…" combobox. Click it, then for each
   tag in the manifest: `keyboard type "<tag>"`, `sleep 0.4`, `press "Enter"`. Confirm
   each became a "Remove <tag>" chip via snapshot (Medium caps at 5; manifest is capped).
3. Click the dialog's **Publish** button (labelled just "Publish", not "Publish now"):
   `agent-browser --session-name medium find role button click --name "Publish"`.
4. Wait, then read the canonical URL — that's the deliverable:
   ```bash
   agent-browser --session-name medium eval 'document.querySelector("link[rel=canonical]")?.href || location.href'
   ```
   It looks like `https://medium.com/@<user>/<slug>-<id>`.

## Notes

- **One article at a time.** Re-running on the same slug makes a *new* post; it
  doesn't update the old one.
- **Drafts.** If the user wants a draft instead of live, do Steps 1–5 and stop —
  Medium autosaves the draft; skip Publish.
- **Scheduling.** This skill is the unit a routine calls; the schedule itself lives
  outside it. A scheduled run only works where the `medium` session's cookies live
  (i.e. this machine), and will fail loudly at Step 2 if Medium has expired the login.

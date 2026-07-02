---
name: publish-to-devto
description: Publish an article from articles/<slug>.md to dev.to as a post via the Forem write API (no browser). Use when the user asks to "post to dev.to", "publish on dev.to", or to wire dev.to into a cross-post routine. Requires the article already live on the portfolio (brandincanfield.com hosts the images and is the canonical URL). Not for Medium/Hashnode.
---

# Publish to dev.to

Unlike Medium and Hashnode, dev.to (Forem) has a real **write API**, so there's no
browser — a Python helper builds the JSON payload and you POST it. The one catch:
dev.to has **no image upload**, so cover + inline images must be public URLs. We host
them on the portfolio (brandincanfield.com) and set the canonical URL there too.

**Run `publish-to-portfolio` first.** This skill depends on the portfolio being live:
images load from brandincanfield.com and `canonical_url` points at the portfolio post.

**Inputs:** `articles/<slug>.md` + the portfolio canonical URL (from `publish-to-portfolio`).
**Output:** a dev.to post (draft by default); you return its URL.

## Prerequisites

1. **`DEVTO_API_KEY`** — a dev.to API key (Settings → Extensions → "DEV Community API
   Keys" / Settings → Account). **It lives in the repo-root `./.env`
   (`DEVTO_API_KEY=…`), NOT the shell profile** — so it won't be in `$DEVTO_API_KEY`
   until you source it. Load it (sandbox disabled — the Bash sandbox blocks reading
   `.env`), then confirm:

   ```bash
   set -a; . ./.env; set +a
   [ -n "$DEVTO_API_KEY" ] && echo "key present" || echo "MISSING — check ./.env, else ask the user"
   ```

   Source it again in the same command as the Step 3 POST (env doesn't persist between
   Bash calls). Only ask the user if `./.env` truly lacks it.

2. **The article is live on the portfolio** (so its images resolve). Have the
   canonical URL ready: `https://brandincanfield.com/blog/<slug>`.

## Step 1 — Build the payload

```bash
python3 .claude/skills/publish-to-devto/scripts/prepare.py articles/<slug>.md \
  --canonical https://brandincanfield.com/blog/<slug>
```

Writes `article.json` (the `{"article": {...}}` body) and prints the image URLs it
references. It rewrites every local image to its brandincanfield.com URL, sets the
cover as `main_image`, maps `summary`→`description`, `series`→`series`, caps tags at
dev.to's **4** (lowercase alphanumeric), and defaults to **draft** (`published:
false`). Add `--publish` to go live immediately.

## Step 2 — Verify the images are live

dev.to fetches `main_image` server-side and renders inline images from their URLs — if
any 404s the post looks broken. HEAD-check each URL printed in Step 1:

```bash
for u in <the image URLs from step 1>; do
  curl -s -o /dev/null -w "%{http_code}  $u\n" "$u"
done
```

All `200` → good. Any 404 → the portfolio isn't deployed yet (run/finish
`publish-to-portfolio`) — **stop**, don't post a broken article.

## Step 3 — POST to dev.to

> Publishing is public. With `--publish` the post goes live immediately; without it
> you get a draft you can review at dev.to/dashboard before publishing. Default to a
> draft unless the user asked to publish.

```bash
OUT="<out_dir — the dir holding article.json from step 1>"
curl -s -X POST https://dev.to/api/articles \
  -H "api-key: $DEVTO_API_KEY" \
  -H "Content-Type: application/json" \
  -d @"$OUT/article.json" | tee "$OUT/response.json" | python3 -c "import json,sys; r=json.load(sys.stdin); print(r.get('url') or r.get('current_state_path') or r)"
```

A success returns the article JSON including its `url`. An error returns
`{"error": "...", "status": ...}` — common causes: bad/missing api-key (401),
duplicate title (422 — dev.to rejects re-posting the same title), or a malformed
canonical_url already used by another post. Surface the error; don't retry blindly.

## Step 4 — Return the URL

Report the `url` from the response. For a draft, also mention it's a draft awaiting
publish at `https://dev.to/dashboard`.

## Notes

- **Sandbox:** the POST hits `dev.to` (not whitelisted) — run the curl with the Bash
  sandbox disabled.
- **Updating vs. re-posting:** re-running creates a *new* post (and dev.to 422s on a
  duplicate title). To update an existing post use `PUT /api/articles/{id}` with the
  id from the create response — not in scope here.
- **Tags:** dev.to allows 4, lowercase alphanumeric; the article's 5th tag (and any
  punctuation) is dropped. Edit the article frontmatter if you want different ones.
- **Canonical:** set to the portfolio URL so dev.to doesn't compete with it for SEO —
  matches Medium and Hashnode, which point canonical at the same portfolio post.

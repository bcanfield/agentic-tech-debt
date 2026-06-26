---
name: publish-to-portfolio
description: Publish an article from articles/<slug>.md to the personal portfolio (brandincanfield.com) — copy it into the portfolio-2 Next.js repo, push, and wait for Vercel to deploy. Use when the user asks to "publish to my portfolio/blog/site", or as the FIRST step of cross-posting (the portfolio is the canonical home + image host for Medium/Hashnode/dev.to). Returns the live canonical URL.
---

# Publish to Portfolio (brandincanfield.com)

The portfolio is the **canonical home** for every article and the **host for its
images**. It's a Next.js site (`content-collections` + MDX) at
`/Users/bcanfield/Documents/Git/portfolio-2`, auto-deployed by Vercel on every push
to `main`. Publishing is a plain file copy — the article body is already MDX-safe
markdown, and image paths like `/foo.png` map 1:1 onto the repo's `public/` folder
(`public/foo.png` serves at `https://brandincanfield.com/foo.png`).

**Run this FIRST when cross-posting.** Medium, Hashnode, and dev.to all set their
canonical URL to the portfolio post and (for dev.to) pull images from
brandincanfield.com — so the portfolio has to be live before those run.

**Inputs:** an `articles/<slug>.md` file (+ its companion images in `articles/`).
**Output:** a live post at `https://brandincanfield.com/blog/<slug>`; you return that URL.

## Step 1 — Stage the files into the portfolio repo

```bash
python3 .claude/skills/publish-to-portfolio/scripts/stage.py articles/<slug>.md
```

Copies the article to `content/<slug>.mdx` and every local image to `public/`,
then prints the canonical URL and what it staged. The portfolio slug defaults to the
article's filename; pass `--slug <name>` if you want a different URL slug (the mdx
filename *is* the slug — `content/x.mdx` → `/blog/x`). Image filenames are preserved,
so the markdown's `/name.png` refs resolve against `public/` unchanged.

> **Don't clobber edits.** If this article already lives in the portfolio and you've
> hand-edited it there, staging overwrites it (the script warns `[OVERWROTE existing]`).
> For a brand-new article that's fine; otherwise reconcile first.

## Step 2 — Commit and push (triggers the Vercel deploy)

Vercel deploys on push to `main`. Review what changed, then commit + push *from the
portfolio repo*:

```bash
git -C /Users/bcanfield/Documents/Git/portfolio-2 add content public
git -C /Users/bcanfield/Documents/Git/portfolio-2 status -s          # sanity-check the staged files
git -C /Users/bcanfield/Documents/Git/portfolio-2 commit -m "Add <slug>"
git -C /Users/bcanfield/Documents/Git/portfolio-2 push origin main
```

If `main` isn't checked out in the portfolio repo, stop and ask — don't publish from
a feature branch (Vercel production builds from `main`).

## Step 3 — Wait for the deploy to go live

Poll the canonical URL until it returns `200` (Vercel builds take ~1–3 min). The URL
404s until the new article is built and live:

```bash
URL="https://brandincanfield.com/blog/<slug>"
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "$URL")
  echo "$code  $URL"
  [ "$code" = "200" ] && break
  sleep 15
done
```

Also confirm an image is live (the cross-posters depend on it):

```bash
curl -s -o /dev/null -w '%{http_code}\n' "https://brandincanfield.com/<cover-filename>.jpg"
```

Both `200` → the article and its images are deployed.

## Step 4 — Return the canonical URL

Report `https://brandincanfield.com/blog/<slug>` — that's the deliverable and the
canonical URL the other publish skills consume. Hand it to:

- `publish-to-devto` — `--canonical "<url>"` (also pulls images from brandincanfield.com)
- `publish-to-medium` — set the story's canonical link to it
- `publish-to-hashnode` — set the post's canonical URL to it

## Notes

- **Sandbox:** `curl` to brandincanfield.com may need the Bash sandbox disabled
  (host isn't whitelisted).
- **Body drift:** the cross-posters read `articles/<slug>.md`, not the portfolio copy.
  If you later edit the portfolio version, the cross-posts won't reflect those edits
  unless you re-sync the source article. Keep `articles/<slug>.md` the source of truth.
- **Scheduling:** this skill is the unit a routine calls; the schedule lives outside it.

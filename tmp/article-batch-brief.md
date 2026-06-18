# Batch brief — Days 3–12 of the Agentic Tech Debt series

You are writing ONE article for the debt-ops content pipeline. This brief is shared
across the batch so the 10 pieces stay consistent and DON'T converge on one shape.

## Non-negotiable process

1. **Read and follow `/Users/bcanfield/Documents/debt/.claude/skills/write-article/SKILL.md` in full.**
   It is the authority. Everything below is supplementary.
2. **Facts come only from `docs/ai-tech-debt-stories.md`.** No invented numbers, no
   rounded stats, no paraphrased quotes. Carry the Caveats section inline (vendor
   studies labeled as vendor research; Amazon 6.3M always "a Business Insider estimate
   Amazon disputes"; METR always n=16, early-2025 models).
3. **Date discipline:** write relative to YOUR publish slot date, not today. GitClear's
   8x duplication rise was *during 2024* — never "last year." curl's bounty reopened
   March 2026, so the shutdown is not the headline event (lead with the June 2026
   ~18-hour volume datapoint).
4. **One link in the whole piece** and it's `github.com/bcanfield/agentic-tech-debt`.
   Name siblings/sources/studies in prose, never link them.

## Required artifacts (all committed, none hotlinked)

- `articles/<slug>.md` — frontmatter block per SKILL.md Step 3, then body. No body H1.
- `articles/<slug>.cover.jpg` — 1000×420, concrete-concept Unsplash/Pexels photo,
  downloaded via curl. NOT AI-generated.
- `articles/diagrams/<slug>.html` + `articles/<slug>.diagram.png` — one custom diagram,
  matched to the pillar, carrying content the prose doesn't. Render via Playwright MCP
  (see below).
- `articles/<slug>.meme.png` — one meme via `scripts/render.py`, landing a specific beat.

## Tooling notes (save yourself the trouble)

- **Playwright + cover + meme all need network to non-allowlisted hosts**
  (localhost http.server is fine; unsplash CDN and memegen.link are NOT in the sandbox
  allowlist). Those Bash calls will fail in the sandbox — rerun them with
  `dangerouslyDisableSandbox: true`. (localhost rendering needs the server running.)
- **Diagram render dance** (from `articles/diagrams/README.md`):
  1. `cd articles/diagrams && python3 -m http.server <PORT>` in the background
     (use the unique PORT given in your assignment to avoid any collision).
  2. Load Playwright tool schemas via ToolSearch:
     `select:mcp__plugin_playwright_playwright__browser_navigate,mcp__plugin_playwright_playwright__browser_take_screenshot`
  3. `browser_navigate` → `http://localhost:<PORT>/<slug>.html?scale=2`
  4. `browser_take_screenshot` `target: "#card"` → `articles/<slug>.diagram.png`
  5. `Read` the PNG to confirm the layout holds; kill the http.server when done.
- **Meme:** `python3 scripts/render.py --list` to browse, then
  `python3 scripts/render.py <id> <slug> "line 1" "line 2"` (sandbox-disabled).
- **Cover:** WebSearch `site:unsplash.com <concept>`, WebFetch the photo page for the
  `og:image` id, then
  `curl -fsSL -o articles/<slug>.cover.jpg "https://images.unsplash.com/photo-<id>?w=1000&h=420&fit=crop&q=80&auto=format&fm=jpg"`
  (sandbox-disabled), `file` + `Read` to confirm the crop works as a header.

## Audit before you deliver (SKILL.md Step 3)

Run all three and fix every hit:
- `python3 .claude/skills/ai-smell-review/scripts/phrase_lint.py articles/<slug>.md`
- `python3 .claude/skills/ai-smell-review/scripts/fingerprint.py --vs-corpus articles/<slug>.md`
- `python3 .claude/skills/write-article/scripts/meme_check.py articles/<slug>.md`

Then **spawn a FRESH agent** (Agent tool, subagent_type general-purpose) pointed at the
`ai-smell-review` skill (`.claude/skills/ai-smell-review/SKILL.md`) with your draft path.
You are blind to your own tells — this pass is mandatory, not optional. Apply its ranked
edits; if it flags >5 real findings, send the revised draft back once more. Have it judge
the meme too (Read the PNG). Then stop.

## Anti-signature rules for THIS batch (the series must not get a fingerprint)

The two already-published pieces (`anatomy-of-the-replit-database-deletion.md`,
`invisible-debt-is-the-problem.md`) BOTH:
- open on a bare quote / the agent's confession,
- close with the same "that gap is why I built debt-ops" CTA bridge + install block,
- drop in a registry-frontmatter code block from the author's own repo,
- use "the detail/part I keep chewing on / can't get past" asides.

**Read both before you draft.** Then:
- Do NOT open on a bare quote (both existing ones do). Find a different cold open for
  your shape.
- Vary the CTA bridge wording — "stories like this are why I built…" is spent; write a
  different bridge.
- Avoid reused phrases: "I keep coming back to," "the part nobody read," "quietly,"
  "the detail I can't get past," "chewing on."
- Use the author's-real-repo trick (a real `docs/debt/` entry, real `git log`, a real
  ADR, fresh tool output) — but a DIFFERENT artifact than the existing pieces used, and
  not in every piece a registry-frontmatter block (it's becoming the signature).
- You are assigned a specific human exemplar to calibrate on (WebFetch one of their
  essays first if possible). Borrow its structural range, not its voice.

SERIES-WIDE CONVERGENCE BANS (caught by the Day 6 review — these now fingerprint the run):
- Do NOT write any variant of "outside the agent's own account of the session / itself /
  how the session went." That CTA-bridge phrasing is already in 4 articles. Describe where
  the decision lands using THIS piece's own concrete artifact instead.
- Do NOT use the "it would not have saved/stopped X... it does something smaller/duller"
  closing formula. It's in 3+ articles. Be candid about the tool's limits in a fresh shape,
  once, and don't mirror Replit's "it would not have saved Lemkin's database" sentence.
- Watch the closing register: "the one nobody put on a curve" / "tell me who's being served"
  / "13,000 people... paid for it" are all cost-tally/rhetorical-question closes. Let yours
  be plainer.
- "a clean line that compiles" is in 3 articles — don't reuse it.

Author identity: Brandin Canfield, solo dev building debt-ops in public. Plain-spoken,
concise, a little dry. Voice reference: this repo's README and CLAUDE.md.

Deliver: a one-paragraph summary of the article + the slug + confirmation all four
artifacts are committed and all audits pass. Do not paste the whole article back.

# Cross-tool packaging plan: reaching the non-Claude/Codex market

## Why this document exists

debt-ops reaches Claude Code and Codex. The rest of the agentic-coding market —
Copilot, Gemini CLI, Cursor, Continue, Windsurf, and ~35 more — runs other tools.
This plan names how we reach them without watering down the product. The
architectural decision behind it is [ADR 0013](./adr/0013-portable-agent-skills-layer.md);
this is the build sequence.

## The one insight that drives everything

debt-ops is **two mechanisms**, and they package differently:

| Surface | Examples | How it ships cross-tool |
|---|---|---|
| **Model-invoked** | `add`, `review`, `metrics`, `init` | Agent Skills open standard — one `SKILL.md` folder, ~40 tools |
| **Hook-driven** (the differentiator) | write-time `feedback.py`, SessionStart inject, `drop`, Stop | per-runtime **hook adapter** — only on tools that expose hooks |

The Agent Skills standard has **no hook/event mechanism** — skills run when the
model decides, not on every edit. So the write-time enforcement *cannot* be a
skill. The good news (verified June 2026): hooks themselves went cross-tool.
**GitHub Copilot CLI** and **Gemini CLI** both ship a `postToolUse` /
`sessionStart` contract nearly identical to Claude Code's, including
`additionalContext` injection. So the differentiator ports — as a hook adapter,
not as a skill.

### Per-tool reality (June 2026)

| Tool | Agent Skills | Hooks | Best we can ship |
|---|---|---|---|
| Claude Code | ✅ | ✅ | full (have it) |
| Codex | ✅ | ✅ | full (have it) |
| GitHub Copilot CLI | ✅ | ✅ `postToolUse` (no matcher; self-filter to edits) | full — adapter is the prize |
| Gemini CLI | ✅ | ✅ (on by default) | full |
| Cursor / Windsurf / Continue | ✅ | weak/none or non-portable | **skills + AGENTS.md degraded mode** |
| VS Code Copilot (extension) | ✅ | cloud-agent hooks only | skills + degraded mode |

Sources are cited in the session research; key ones: the Agent Skills standard
(agentskills.io, ~40 client tools), GitHub Copilot hooks reference
(`sessionStart`/`postToolUse` with `additionalContext`), Gemini CLI skills + hooks
docs.

## Honest limitation we lead with, not bury

On a skills-only tool (no hook adapter) there is **no deterministic write-time
feedback and no auto-capture on every edit**. The agent self-applies the
disciplines from the charter (`AGENTS.md`). That's "vibes," not a tripwire — it
violates Pillar 7 if we pretend otherwise. We ship it as the *degraded mode* and
say so in the README. The full experience needs a hook adapter.

## Phases

### Phase A — decision + plan ✅ (this doc + ADR 0013)

### Phase B — portable skills prototype  ← in progress

Add a runtime-agnostic `skills/` set at the repo root, strict to the open
standard, so it drops into any compatible tool. Scope:

- `debt-ops-add` + bundled `scripts/register.py`
- `debt-ops-review` + bundled `scripts/review.py`
- `debt-ops-metrics` (markdown; portable cache lookup via `python3 -c`, not `shasum`)
- `debt-ops-init` → writes the charter to `AGENTS.md` (the cross-tool charter file)
- `skills/README.md` — per-tool install paths + the degraded-mode disclaimer

Frontmatter is `name` + `description` only. Names are `debt-ops-*` prefixed to
avoid collision. Scripts use relative `scripts/…` paths. This is additive — it
touches neither released adapter.

**Validation:** install the folder into at least one non-Claude tool (Gemini CLI
or Copilot CLI) and confirm `debt-ops-add` writes an entry and `debt-ops-review`
prints its report. The prototype proves the *helper scripts travel and run*,
which is the only non-obvious part.

### Phase C — Copilot CLI hook adapter (the real test)

A `copilot/` sibling adapter wiring the hook-driven layer to Copilot's hook
contract. This is where the differentiator either survives the port or doesn't.
Key adapter deltas vs Claude Code:

- Copilot's `postToolUse` has **no matcher** — it fires after every tool, so
  `feedback.py` must self-filter to file-edit tools by reading `toolName` from the
  hook stdin (Copilot's JSON shape: `toolName`, `toolArgs`, `toolResult`).
- Output contract: return `{ "additionalContext": "…" }`; Copilot appends it to
  `textResultForLlm`. Close to our existing envelope; needs a thin shim.
- Charter file is `AGENTS.md` / Copilot instructions, not `CLAUDE.md`.

### Phase D — Gemini CLI hook adapter

Same shape against Gemini's hook contract; Gemini ships skills + hooks natively,
so it's the second full-experience target.

### Phase E — ~~extract `_common.py`~~ dropped: keep duplication, sync by AI

**Reversed.** The original plan was to extract a vendored `_common.py` once a
third adapter landed. We're not doing that ([ADR 0014](./adr/0014-keep-adapters-duplicated.md)):
the helper scripts and skills stay duplicated across all four implementations, and
parity is maintained by hand/AI per-change. The policy, the full duplicate map, and
the per-adapter deltas live in CLAUDE.md under "Adapter parity — duplicated on
purpose." Revisit the extraction only if AI-sync drift actually ships a bug.

## Sequencing rationale

- B first: lowest risk, mostly mechanical, immediately widens reach to every
  skills tool, and proves the portable-script pattern with zero impact on shipped
  plugins.
- C before D: Copilot is the larger audience and its hook contract is the closest
  to ours — best return on the first hook port, and it de-risks D.
- E dropped: rather than extract a shared module, we keep the duplication and
  sync by AI (ADR 0014). Self-containment was the point of the adapter design;
  hand/AI sync is the lighter mitigation we're trying before any extraction tooling.

## Out of scope (named, not forgotten)

- Refactoring the released `claude-code/` adapter to consume a shared module —
  ruled out (ADR 0014); adapters stay self-contained and duplicated.
- A marketplace/registry listing for the portable skills (submitting to
  agentskills.io or per-tool catalogs) — distribution, not engineering; revisit
  after B validates.
- Cursor/Continue-specific hook shims — only if those tools grow a portable hook
  surface; until then they get skills + degraded mode.

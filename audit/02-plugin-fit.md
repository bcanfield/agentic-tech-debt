# Plugin-fit audit (Pass 2)

Date: 2026-05-05
CC docs version checked: `code.claude.com/docs/en/*` (live, no version banner; references to v2.1.59, v2.1.105, v2.1.121 indicate this audit covers behavior as of v2.1.121+). `docs.claude.com/en/docs/claude-code/*` 301-redirects to `code.claude.com/docs/en/*` — the plan's preferred URL is no longer canonical. Findings are derived from the official docs above; the team's own `claude-code-plugins.md` was used only as a starting cross-check.

---

## A. Primitive correctness

| Plan claim | Verdict | Notes / source |
|---|---|---|
| `plugin.json` has fields `name`, `version`, `description`, `userConfig: {}`, `dependencies: []` | **Mostly correct, one error** | `name` is the only required field. `version`, `description`, `userConfig`, `dependencies` are all optional. The plan's example `"userConfig": {}` and `"dependencies": []` are **legal but pointless** — both fields can simply be omitted. https://code.claude.com/docs/en/plugins-reference#required-fields |
| `name` becomes the slash-command namespace prefix | Correct | `skills/add/SKILL.md` in plugin `debt-ops` becomes `/debt-ops:add`. https://code.claude.com/docs/en/plugins#step-add-a-skill |
| Hook event `SessionStart` exists | Correct | Fires on session begin/resume; matchers include `startup`, `resume`, `clear`, `compact`. https://code.claude.com/docs/en/hooks-reference |
| Hook event `PostToolUse` exists | Correct | Fires after tool call succeeds; tool-name matcher. Same source. |
| `PostToolUse` matcher `Write\|Edit\|MultiEdit` | **Correct as a tool-name list** | Per the matcher syntax table: "Only letters, digits, `_`, and `\|` → Exact string, or `\|`-separated list of exact strings. `Edit\|Write` matches either tool exactly." `Write\|Edit\|MultiEdit` is therefore an exact-list match, **not** a regex. https://code.claude.com/docs/en/hooks-reference (Matcher Syntax) |
| `${CLAUDE_PLUGIN_DATA}` exists, persistent across updates | Correct | Resolves to `~/.claude/plugins/data/{id}/` where `{id}` is plugin-id (e.g. `debt-ops-my-marketplace`), survives updates, deleted on uninstall (unless `--keep-data`). **Per-plugin × per-user, NOT per-repo.** https://code.claude.com/docs/en/plugins-reference#persistent-data-directory |
| Writing `feedback.list` to `${CLAUDE_PLUGIN_DATA}` is supported | Correct mechanically, **wrong semantically** | Variable is per-user-per-plugin, not per-repo. Writing one `feedback.list` there means **the cache is shared across every repo the user opens with this plugin.** Plan reads as if each repo has its own cache. Fix: namespace by `cwd` hash, e.g. `${CLAUDE_PLUGIN_DATA}/cache/$(echo "$CWD" \| shasum)/feedback.list`. Same source as above. |
| `${CLAUDE_PLUGIN_ROOT}` for bundled scripts | Correct, plan uses it implicitly via `hooks.json` `command` paths. https://code.claude.com/docs/en/plugins-reference#environment-variables |
| `SessionStart` hook injects context via "heredoc to stdout" | **Partially correct, sloppy** | "Plain text stdout is added as context for Claude" — so a heredoc echo does work. But the **documented preferred contract** is JSON with `hookSpecificOutput.additionalContext`, which is wrapped in a system reminder and explicitly cap-managed. Plain stdout and `additionalContext` are both capped at **10,000 characters**; the four disciplines easily fit, but the plan should commit to the structured form for forward compatibility. https://code.claude.com/docs/en/hooks-reference (additionalContext Field) |
| Hook script return contract is "structured JSON" | **Correct but underspecified** | Universal fields: `continue`, `stopReason`, `suppressOutput`, `systemMessage`, `hookSpecificOutput`. `PostToolUse` does not directly accept the agent JSON the plan describes — the agent sees the hook's stdout/`additionalContext` as feedback, not a custom-shape object. The plan's `{<command>: pass\|fail, ...}` is fine **as a serialized payload inside `additionalContext`**, but it isn't a first-class CC contract. https://code.claude.com/docs/en/hooks-reference (JSON Output Format) |
| Skill `skills/add/SKILL.md` in plugin `debt-ops` → `/debt-ops:add` | Correct | Confirmed by quickstart; namespace prefix is the manifest `name`. https://code.claude.com/docs/en/plugins |
| Plugin-shipped agents cannot define `hooks`, `mcpServers`, `permissionMode` | Correct | Quoted: "For security reasons, `hooks`, `mcpServers`, and `permissionMode` are not supported for plugin-shipped agents." https://code.claude.com/docs/en/plugins-reference#agents |
| 3-second budget on `feedback.sh` is enforceable by CC | **Incorrect** | CC default `command` hook timeout is **600 seconds**. There is no aggregate or per-plugin budget. Per-hook timeout is configurable via `timeout` field in `hooks.json` (in seconds). The 3 s budget is something `feedback.sh` must self-enforce (e.g., `timeout 3 …`). https://code.claude.com/docs/en/hooks-reference (Timeouts) |
| `disciplines.md` lives inline in `session-start.sh` | Mechanically fine. Just keep stdout < 10,000 chars (cap). |
| `hooks.json` location at `hooks/hooks.json` | Correct default. https://code.claude.com/docs/en/plugins-reference#file-locations-reference |

---

## B. Native overlap

| Plan behavior | Native CC equivalent | Recommendation |
|---|---|---|
| "Rely on Claude Code's native `AGENTS.md` / `CLAUDE.md` loading" (Pillar 6, line 226–227, 151) | **HALF-FALSE.** CC reads `CLAUDE.md`, **not** `AGENTS.md`. Quoted: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it…" https://code.claude.com/docs/en/memory#agents-md | **Major rewrite.** Throughout the plan, every "AGENTS.md or CLAUDE.md" assertion is wrong. CC only auto-loads `CLAUDE.md` (and `CLAUDE.local.md`, `.claude/rules/*.md`, managed-policy CLAUDE.md). For `AGENTS.md` to be loaded, the user must put `@AGENTS.md` inside their `CLAUDE.md`. The plan should standardise on **CLAUDE.md as the inject target** and treat AGENTS.md as a community convention the plugin can `@import` if present. |
| `/debt:init` writes a `## Tech debt operations` section into AGENTS.md | Same problem. Writing into a file CC doesn't auto-load defeats the purpose. | Have `/debt:init` write into `./CLAUDE.md` (or `./.claude/CLAUDE.md`), creating the file if absent. If the team also wants `AGENTS.md` parity, write to AGENTS.md and add `@AGENTS.md` to CLAUDE.md. |
| SessionStart inject defers to charter section if present | Reasonable defer pattern, but **CC has no marker-based hook contract** between plugins | No native marker spec exists; the plan's `<!-- debt-ops:feedback -->` is purely a self-imposed convention. Document it as such; don't suggest other plugins will respect it. |
| Built-in `/init` "scaffolds AGENTS.md" (line 233, line 352) | **WRONG.** `/init` produces `CLAUDE.md`. Quoted from the commands reference: "/init — Initialize project with a `CLAUDE.md` guide. Set `CLAUDE_CODE_NEW_INIT=1` for an interactive flow…" https://code.claude.com/docs/en/commands and https://code.claude.com/docs/en/memory#set-up-a-project-claude-md | Replace every "AGENTS.md" reference around `/init` with "CLAUDE.md". |
| Native bash auto-detection vs. SessionStart inject | No native "detect quality commands" feature exists; the plan's approach is correct on this point. | Keep. |
| Bundling executables on PATH | CC has `bin/` for this. Plan doesn't use it (correct — nothing to ship); just be aware. https://code.claude.com/docs/en/plugins-reference#file-locations-reference |
| The plan's "lazy creation of `debt/registry/` and `doc/adr/`" | No native "managed include" mechanism for plugins to write into user repos under a sandbox. The plan's lazy creation pattern is correct. | Keep. |
| Per-skill tool restrictions | Native: `allowed-tools` in SKILL.md frontmatter. Plan doesn't lock down `/debt:add`'s tool surface — minor v1 concern but worth a single line: `allowed-tools: Write Edit Read`. https://code.claude.com/docs/en/skills#frontmatter-reference |
| Skill `disable-model-invocation` for `/debt:init` | Native, missing from plan. Without it, Claude can auto-invoke `/debt:init` (writes to CLAUDE.md without the user asking). | **Set `disable-model-invocation: true` on `/debt:init`** to keep it user-only — matches the plan's "opt-in" intent. |

---

## C. Coexistence

The plan's "How we coexist with other plugins" claims hooks are commutative and the 3 s budget is fine. Stress-test:

1. **SessionStart ordering across plugins.** Docs say: "All matching hooks run in parallel, and identical handlers are deduplicated automatically." There is **no documented per-source ordering** beyond the resolution hierarchy (user → project → local → managed → plugin → component). Multiple plugins' SessionStart hooks **run in parallel**; their stdout/`additionalContext` outputs are all injected. The plan's defer-to-charter logic still works because the `session-start.sh` script reads the charter file at run time, so it doesn't matter if another plugin's inject fired first or in parallel. **Coexistence claim holds.**

2. **PostToolUse with `Write|Edit|MultiEdit` from two plugins.** All matching hooks run in parallel. Deduplication is by command string, so two plugins running different scripts do not dedupe. Both run; both inject feedback. The plan's "structured JSON" return doesn't conflict because each plugin's output is appended separately. **Coexistence claim holds, with caveat:** there is no defined order for which plugin's feedback the model sees first; it's racy. Don't rely on order.

3. **Per-hook timeout, NOT aggregate.** Default `command` hook timeout is **600 s**, configurable per-hook via `timeout`. There is no aggregate budget across plugins or a per-plugin budget. The plan's "3 s aggregate budget" is **a self-imposed limit inside `feedback.sh`**, not a CC enforcement. The plan should:
   - Set `timeout: 4` (or 5) in `hooks.json` so CC kills a stuck script.
   - Inside `feedback.sh`, run each command under `timeout 3 …`.
   - State explicitly that other plugins' PostToolUse hooks are not bounded by this budget. https://code.claude.com/docs/en/hooks-reference (Timeouts)

4. **Namespace collisions on `/debt:*`.** Plugin-skill namespacing uses the manifest `name` field. Another plugin literally named `debt-ops` would collide; another plugin named `debt-something` would not (it'd own `/debt-something:*`). The plan documents the working name as `debt-ops`; that is the right level of specificity. **No collision risk** for typical neighbors.

5. **`settings.json` `agent` override.** Confirmed: `settings.json` at plugin root is honored, but only the `agent` and `subagentStatusLine` keys. Setting `agent` swaps the main thread's system prompt, model, and tools — exactly the "hostile to other plugins" outcome the plan calls out. The plan's commitment not to set this is correct and documentable. https://code.claude.com/docs/en/plugins#ship-default-settings-with-your-plugin

6. **Hook merging hierarchy.** When the plugin is enabled, its hooks merge with user/project hooks. There's no override; both fire. The plan's commutative assumption is correct **for parallel execution** but the plan should not assume any particular ordering. Re-word "hooks are commutative" as "hooks run in parallel; we don't depend on ordering."

---

## D. CC-version anchor

This plan implicitly targets **Claude Code v2.1.121 or later** (post-`claude plugin prune`, post-monitors-v2.1.105, post-auto-memory-v2.1.59). Concretely:

- `${CLAUDE_PLUGIN_DATA}` and `${CLAUDE_PLUGIN_ROOT}`: standard, available since plugins shipped.
- `hookSpecificOutput.additionalContext` for SessionStart: documented; the plain-stdout variant is the legacy fallback.
- 10,000-char cap on injected context: documented.
- Skill progressive disclosure (`SKILL.md` + supporting files): documented.
- Plugin-shipped agent restrictions (`hooks`/`mcpServers`/`permissionMode` blocked): documented.
- `disable-model-invocation` on skills: documented.

**Risky / undocumented features the plan depends on:** none. Every primitive the plan touches is officially documented. The two genuinely risky bets are conventions, not features:
1. The `<!-- debt-ops:feedback -->` marker block — purely the plugin's own convention; no other tool will respect it.
2. The "AGENTS.md is auto-loaded" assumption — this is **not** a CC behavior. (See B above.)

**Forward compatibility note:** the plan should not pin `version` in `plugin.json` while iterating ("If you set `version` in `plugin.json`, you must bump it every time you want users to receive changes" — bumping omissions silently no-op updates). For pre-1.0 development, omit `version` and let the git SHA be the cache key. https://code.claude.com/docs/en/plugins-reference#version-management

---

## E. Required corrections to v1 plan

All file paths refer to `/Users/bcanfield/Documents/debt/tech-debt-plugin-plan.md`.

1. **Replace AGENTS.md with CLAUDE.md throughout.** Sections affected: line 17 ("required AGENTS.md edits"), line 86 (`AGENTS.md` or `CLAUDE.md` defer), line 151 (Pillar 6 row), line 226–235 (Pillar 6 v1 commitment), line 252–254 (Pillar 7 charter marker), line 285 (skill comment "writes section to AGENTS.md"), line 352 ("Charter bootstrap"), line 364 ("`AGENTS.md` and `CLAUDE.md` belong to the project"), line 433–438 (day-in-the-life), line 552 ("zero required AGENTS.md modifications"). The corrected fact: **CC auto-loads `CLAUDE.md`, not `AGENTS.md`.** `/debt:init` should write to `./CLAUDE.md` (or `./.claude/CLAUDE.md`); if the team wants AGENTS.md parity, the same content can be appended there with `@AGENTS.md` added to CLAUDE.md. Source: https://code.claude.com/docs/en/memory#agents-md

2. **Fix the `/init` claim.** Lines 233 and 352: "Claude Code's built-in `/init` already does that" — `/init` produces `CLAUDE.md`, not AGENTS.md. Reword: "Claude Code's built-in `/init` already scaffolds CLAUDE.md." Source: https://code.claude.com/docs/en/commands

3. **Fix the 3-second budget framing.** Lines 258, 320, 530–531: "3 s wall-clock budget" / "3 s aggregate budget for `feedback.sh`". CC does not enforce this; default `command` hook timeout is **600 s**. Required edit: state the budget is enforced **inside `feedback.sh`** (e.g., `timeout 3 …` per command) AND set `timeout: 5` in `hooks.json` as a CC-level guard. Add a sentence: "The 3 s budget is plugin-self-imposed; Claude Code's default hook timeout is 600 s." Source: https://code.claude.com/docs/en/hooks-reference

4. **Empty `userConfig` and `dependencies` arrays should be omitted.** Lines 301–308 (the `plugin.json` example). The plan ships `"userConfig": {}` and `"dependencies": []` — both are legal but cargo-cult. The manifest schema treats both as optional; just delete the keys. The minimal manifest is `{ "name", "description" }`. Source: https://code.claude.com/docs/en/plugins-reference#required-fields

5. **`${CLAUDE_PLUGIN_DATA}/feedback.list` is per-user-per-plugin, not per-repo.** Lines 65, 320, 398: the plan reads as if each repo has its own cache. The variable resolves to a **single directory shared across every repo the user opens with this plugin enabled**. Required edit: namespace cache by repo (e.g., `${CLAUDE_PLUGIN_DATA}/cache/$(git rev-parse --show-toplevel | shasum | cut -c1-12)/feedback.list`) and document the scope. Source: https://code.claude.com/docs/en/plugins-reference#persistent-data-directory

6. **Commit to `additionalContext` over plain stdout.** Lines 84–85, 319: "live inside `session-start.sh` as a heredoc". Both work, but the canonical contract is JSON output `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "<text>"}}`. Plain stdout is documented as "added as context" but is the legacy form. Required edit: switch `session-start.sh` to emit a JSON envelope; note the 10,000-character cap on injected context. Source: https://code.claude.com/docs/en/hooks-reference (additionalContext Field)

7. **Add `disable-model-invocation: true` to `/debt:init`.** Plan section "Plugin layout (v1)" lists the skill but doesn't gate it. Without this flag, Claude may auto-invoke `/debt:init` based on conversation context, silently writing to the user's CLAUDE.md. The plan's whole "opt-in" framing requires this flag. Source: https://code.claude.com/docs/en/skills#frontmatter-reference

8. **Re-word the "hooks are commutative" claim.** Line 384: "Hook ordering across plugins. We assume hooks are commutative." Replace with: "Multiple plugins' SessionStart and PostToolUse hooks run in parallel; we depend on no ordering and our outputs are independently consumable." Source: https://code.claude.com/docs/en/hooks-reference (Hook Merging & Ordering)

9. **Drop or qualify the `<!-- debt-ops:feedback -->` marker contract.** Lines 252–254, 273. Document this as a self-imposed convention; CC does not standardize cross-plugin marker blocks. No other plugin will know to respect (or avoid clobbering) this marker. Recommend renaming to a longer, more unique form like `<!-- debt-ops:feedback v1 -->` and explicitly note that interoperability with other plugins that touch CLAUDE.md is undefined.

10. **Pin a CC version, omit `version` from `plugin.json` until v1.0.** Add a "Requires Claude Code v2.1.121 or later" line near the top. In `plugin.json` (line 301–308), drop `"version": "0.1.0"` so the git SHA acts as the cache key during pre-1.0 iteration; otherwise users will silently miss updates if the maintainer forgets to bump. Source: https://code.claude.com/docs/en/plugins-reference#version-management

11. **Update the Pillar 7 cache-source-of-truth chain.** Lines 252–256 say cache is overridden by charter marker block when present. Given correction (1), this should read "CLAUDE.md marker block when present; otherwise per-repo cache under `${CLAUDE_PLUGIN_DATA}`." Same edit; cited here separately because it touches the architectural "trust boundary" prose at line 261–263.

12. **The `${CLAUDE_PLUGIN_ROOT}` reference is missing from the layout discussion.** The plan's `hooks.json` table at line 317–321 doesn't show how `session-start.sh` and `feedback.sh` are addressed. Required: in `hooks.json`, the `command` field must be `"${CLAUDE_PLUGIN_ROOT}/scripts/session-start.sh"` etc. Currently implied but not written out. Source: https://code.claude.com/docs/en/plugins-reference#environment-variables

---

## Summary

The plan's architectural shape — two skills, two hooks, two scripts, no userConfig, lazy file creation — is sound and uses CC primitives appropriately. The single biggest correction is that **Claude Code does not auto-load `AGENTS.md`**; every `AGENTS.md` reference must become `CLAUDE.md`, and `/init` produces CLAUDE.md. The second-biggest is that the 3-second budget is self-imposed, not CC-enforced. The third is that `${CLAUDE_PLUGIN_DATA}` is per-plugin-per-user, not per-repo, so the feedback cache needs repo-namespacing. Once those three are fixed, the design is well-aligned with CC's plugin model and does not duplicate native behavior, with the minor exceptions called out in B (don't reinvent `disable-model-invocation`, do use `additionalContext`, do reference scripts via `${CLAUDE_PLUGIN_ROOT}`).

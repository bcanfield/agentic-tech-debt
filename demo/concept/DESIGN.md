# debt-ops: conceptual hero animation (design spec)

A professionally-designed, conceptual animated GIF that introduces newcomers to
debt-ops. **Not a terminal recording**. A motion-design piece. The single hook
is **auto-capture**: debt gets logged the instant the AI agent writes it,
hands-free, and the noise prunes away in a word.

Every value below is chosen from research, not taste. The "why" lives in
[§1](#1-research-foundation); the rest of the doc is decision-locked so it can be
built without re-litigating.

---

## 0. Non-negotiables

1. **Auto-capture is the hook.** The hero beat is the *catch*: a deferral
   detaching from code and filing itself into the registry with **no human
   input on screen**. It gets the most screen time and the most polished motion.
2. **Graceful, not punitive.** Debt capture reads as *reassuring* ("nothing
   slipped through"), never as an error. **No red, no alarm, no strobing.**
   Grounds in the project's design tenet *graceful over punitive*
   (`docs/tech-debt-pillars.md`) and WCAG 2.3.1.
3. **Truthful.** Cards render the *real* CLI output (`+1 entry: <slug> (A)` and
   the real plain-language tags from `review.py`), never invented UI.
4. **GIF-native.** Flat fills, limited palette, static background. The aesthetic
   that looks modern *and* compresses well is the same one. Design for the
   format, don't fight it.
5. **Deterministic.** All motion is a pure function of normalized time
   `seek(t), t∈[0,1]`. Frame `i` = `seek(i/(N-1))`. Reproducible like the VHS
   tape, frame-exact.

---

## 1. Research foundation

| Decision driven | Source | What it tells us |
|---|---|---|
| Front-load the hook; total ≤ ~13s | README-as-landing-page consensus | A GIF must show value in seconds; busy viewers leave. |
| UI moves 200–500ms; hero move ≤ ~700ms; nothing ≥1s | [NN/g, *Animation Duration*](https://www.nngroup.com/articles/animation-duration/) | 100ms=instant, ~230ms=perception, 500ms starts to drag, 1s=limit of flow. |
| Duration scales with travel; desktop faster | [Material. Duration & Easing](https://m1.material.io/motion/duration-easing.html) | Big arc gets a longer duration than a micro-fade; desktop 150–200ms baseline. |
| Exact easing curves | [Material 3 motion tokens](https://github.com/material-components/material-components-android/blob/master/docs/theming/Motion.md) | standard, decelerate, accelerate, emphasized cubic-beziers (see §6). |
| Cut clutter; cue the essential; caption with its action; discrete beats | [Mayer, Multimedia Learning principles](https://www.nngroup.com/articles/) → coherence, signaling, contiguity, segmenting ([summary](https://www.digitallearninginstitute.com/blog/mayers-principles-multimedia-learning)) | Minimal scene, one focal action, synced captions, beat structure. |
| Caption hold ≥ 0.3s/word | [BBC subtitle guidelines](https://www.clevercast.com/bbc-subtitling-guidelines/) | A 5-word caption needs ≥1.5s on screen. |
| No flash >3/s, no red flash, small luminance swing | [WCAG 2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) | Single slow pulses only; reinforces "no alarm." |
| Two-pass palette, lanczos, diff modes, dithering | [ubitux, *High-quality GIF with FFmpeg*](https://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html) | The encode recipe in §11. |
| Disney principles: staging, anticipation, slow-in/out, follow-through, secondary action | classical animation canon | Applied per beat in §7. |

---

## 2. Format & canvas

| Property | Value | Rationale |
|---|---|---|
| Design canvas | **1280×720** (16:9) | Matches the existing hero slot; README renders at `width=720`. |
| Master render | **2560×1440 @ 50fps** PNG frames | 2× for a crisp optional MP4/WebP twin. |
| GIF deliverable | **960×540, 25fps, loop forever** | 25fps keeps eased motion smooth (15 stutters); 960w gives HiDPI headroom over the 720 display width. |
| Total runtime | **≈12.6s** | Hook lands by ~4–7s; under the attention ceiling. |
| Safe area | content within central **90%** (64px margin) | Survives social/README cropping. |
| Loop seam | end state ≈ start state (dark canvas) | Invisible loop; no jarring cut. |

---

## 3. Color system

Base palette is **Catppuccin Mocha** (the demo theme already in use), accent is
the **Claude orange** from the README badge. Red is deliberately absent.

| Role | Token | Hex | Notes / contrast on bg |
|---|---|---|---|
| Canvas | Mantle | `#181825` | near-flat; faint radial glow behind ledger only |
| Panel surface | Base / Surface0 | `#1e1e2e` / `#313244` | code panel + cards |
| Panel border | Surface1 | `#45475a` | 1px hairline |
| Primary text / captions | Text | `#cdd6f4` | ~11:1 on Mantle ✓ |
| Secondary text / tags | Subtext0 | `#a6adc8` | ~6:1 ✓ |
| Comments (code) | Overlay0 | `#6c7086` | dim, intentionally low |
| Keyword (code) | Mauve | `#cba6f7` | |
| String (code) | Green | `#a6e3a1` | also the "logged ✓" confirm |
| Function/slug | Blue | `#89b4fa` | slug color matches real CLI output (~7:1) |
| **Deferral highlight + flying chip + trail** | Peach | `#fab387` | warm "noticed", *not* alarm-red (~9:1) |
| **Brand accent** (wordmark, ledger mark) | Claude orange | `#d97757` | distinctive; ties to README badge (~5:1, large text only) |
| Drop action word `drop B` | Mauve | `#cba6f7` | matches the Claude prompt chevron in `scene.bash` |

Rule: **never encode meaning by color alone**. The catch is conveyed by motion +
a ✓ + text, not hue (color-blind safe, Mayer-redundant).

---

## 4. Typography

Both fonts bundled locally as **woff2** (offline → deterministic render).

| Use | Font | Size (1280 canvas) | Weight | Hold / notes |
|---|---|---|---|---|
| Code | **JetBrains Mono** | 26px / lh 1.5 | 400–500 | already a project font |
| Card system line (`+1 entry: …`) | JetBrains Mono | 24px | 500 | the literal, truthful output |
| Card plain tag | **Inter** | 16px | 500 | e.g. "loosened type · checkout" |
| Caption (lower third) | Inter | 32px | 600, ls −0.01em | `#cdd6f4`; per-beat hold ≥0.3s/word |
| Wordmark "debt-ops" | Inter | 72px | 800 | `#cdd6f4`, the "-ops" in `#d97757` |
| Tagline | Inter | 28px | 500 | `#bac2de` |

Dual-coding (Mayer): each card pairs the *literal* mono output with a one-line
*plain* tag, so the system fact and its meaning reinforce each other.

---

## 5. Layout & composition

12-column grid, 64px outer margin. One horizontal band, vertically centered.

```
┌──────────────────────────────────────────────────────────────┐
│  64px margin                                                   │
│   ┌─ code surface ───────────────┐      ┌─ debt registry ──┐  │
│   │ function checkout(session) { │      │ registry · ⬤1    │  │   ⬤ = orange mark + count
│   │   const payload = …          │      │ ┌──────────────┐ │  │
│   │   if (session.user) {        │ ⟿arc⟿ │ │ + entry (A)  │ │  │
│   │     …session.user as any     │      │ │ as-any-… ✓   │ │  │
│   │                              │      │ └──────────────┘ │  │
│   └──────────────────────────────┘      └──────────────────┘  │
│                                                                │
│            «  caption, lower third, one line  »               │
└──────────────────────────────────────────────────────────────┘
```

- **Code surface** (left, ~52% width): rounded card `#1e1e2e`, 1px `#45475a`,
  radius 16px, soft shadow. No terminal chrome; just a small filename chip
  (`api/checkout.ts`) above 6 lines of real TypeScript.
- **Debt registry** (right, ~40%): header `registry · ⬤N` (orange mark + live
  count), then cards stack downward. A faint radial glow sits behind it so the
  eye lands here on the catch (signaling).
- **Caption**: lower-third, single line, centered. Staging: only one beat's
  caption is ever visible.

---

## 6. Motion system (named eases + durations)

Eases (exact, from Material). Implemented via a cubic-bezier evaluator so they
match precisely:

| Name | cubic-bezier | Use |
|---|---|---|
| `STANDARD` | `0.4, 0, 0.2, 1` | moves that start and end on screen |
| `ENTER` (decelerate) | `0, 0, 0.2, 1` | elements arriving |
| `EXIT` (accelerate) | `0.4, 0, 1, 1` | elements leaving |
| `EMPHASIZED` | `0.05, 0.7, 0.1, 1` | the hero catch (MD3 emphasized-decelerate) |
| `LINEAR` | `0, 0, 1, 1` | the background code marquee only |

Durations (Material tokens; all UI ≤500ms, hero arc 700ms as a deliberate
content move, still <1s flow limit):

| Motion | ms | Ease |
|---|---|---|
| Underline draw | 200 | STANDARD |
| Deferral pulse (one cycle) | 400 | STANDARD |
| Anticipation lift | 120 | STANDARD |
| **Hero arc travel** | **700** | EMPHASIZED |
| Snap / morph to card | 300 | EMPHASIZED |
| "logged" ✓ fade-in | 150 | ENTER |
| Count tick (number flip) | 200 | STANDARD |
| Caption in / out | 250 / 200 | ENTER / EXIT |
| Second (fast) catch arc | 450 | EMPHASIZED |
| Drop card exit | 300 | EXIT |
| Wordmark / tagline reveal | 500 / 300 | ENTER |

---

## 7. Beat-by-beat choreography

Total ≈12.6s. One focal action per beat (staging + coherence).

| # | Beat | Window | Action | Caption |
|---|---|---|---|---|
| 0 | Setup | 0.0–1.8s | Fade in. Code lines reveal into the left panel, top-down (LINEAR marquee feel). Registry empty, count `0`. | "Your AI agent writes fast." |
| 1 | Shortcut born | 1.8–3.8s | Last line completes: `    payload.userId = session.user as any`. A peach underline draws under the `as any` cast (signaling). | "A shortcut slips in." |
| **2** | **The catch** ⭐ | **3.8–7.0s** | The hero. See frame-level breakdown below. Card **A** files itself; count ticks `0→1`; ✓ confirms. Left panel dims to 70% (staging). | "debt-ops logs it. Automatically." |
| 3 | Continuous | 7.0–8.8s | A second deferral appears (`// TODO: tidy log format`) and is caught *faster* (450ms arc, minimal anticipation) → card **B** `log-format-nit` drops below A; count `1→2`. Shows it's automatic & ongoing. | "Every shortcut. As it happens." |
| 4 | Out of your way | 8.8–10.6s | The word `drop B` types in (mauve), card **B** accelerates out and dissolves; count `2→1`; card A settles. Low-friction prune. | "Prune the noise in a word." |
| 5 | Resolve / brand | 10.6–12.6s | Panels recede & dim; registry holds the one real entry. Wordmark **debt-ops** + tagline reveal centered. Fade toward the start frame for a clean loop. | **debt-ops** · "Catches AI-introduced tech debt at write-time." |

### The hero catch: frame-level (beat 2, @25fps)

| Sub-beat | t (within beat) | Detail |
|---|---|---|
| a. Underline settles | 0–120ms | peach underline from beat 1 brightens to full. |
| b. Pulse (signal) | 120–520ms | one gentle peach background pulse on the deferral fragment, low amplitude (WCAG-safe, single cycle). |
| c. Anticipation | 520–640ms | fragment lifts `translateY:-4px`, `scale:1.05`, shadow grows, +10% brightness. Telegraphs the move (Disney anticipation). |
| d. Detach + arc | 640–1340ms | fragment becomes a peach pill ("chip"), travels an **arc** (up-and-over, EMPHASIZED) to the empty ledger slot; a short peach trail follows and fades; left panel dims to 70%. (Arc not straight line = Material emphasized "expressive" path.) |
| e. Morph + snap | 1340–1640ms | chip expands into the full card at the slot (EMPHASIZED-DECELERATE → slight overshoot then settle, Disney follow-through); peach border → card style; slug text settles to blue. |
| f. Confirm (secondary) | 1640–1840ms | green ✓ fades in at card's right; registry count flips `0→1` (Disney secondary action). |
| g. Hold | 1840–3200ms | rest. Card legible: `+1 entry: as-any-checkout-payload (A)` + tag "loosened type · checkout". Caption holds. |

---

## 8. Copy (exact, reading-time validated)

Captions ≤6 words; hold ≥ 0.3s/word (BBC), padded for competing motion.

| Beat | Caption | Words | Min hold | Actual |
|---|---|---|---|---|
| 0 | "Your AI agent writes fast." | 5 | 1.5s | 1.8s ✓ |
| 1 | "A shortcut slips in." | 4 | 1.2s | 1.8s ✓ |
| 2 | "debt-ops logs it. Automatically." | 4 | 1.2s | 2.5s ✓ |
| 3 | "Every shortcut. As it happens." | 5 | 1.5s | 1.8s ✓ |
| 4 | "Prune the noise in a word." | 6 | 1.8s | 2.0s ✓ |
| 5 | "Catches AI-introduced tech debt at write-time." | 7 | 2.1s | 2.5s ✓ |

**Code sample** (left panel. A real, recognizable debt smell, kept consistent
with the VHS demo's `as any` catch):

```typescript
function checkout(session) {
  const payload = buildCart(session)
  payload.total = price(payload.items)
  // TODO: tidy log format
  if (session.user) {
    payload.email = session.email
    payload.userId = session.user as any
```

Cards:
- **A** (kept): `+1 entry: as-any-checkout-payload (A)` · tag "loosened type · checkout"
- **B** (the nit, dropped): `+1 entry: log-format-nit (B)` · tag "code quality"

---

## 9. Accessibility

- **Flash safety (WCAG 2.3.1):** only single, slow pulses (≥400ms cycle, well
  under 3/s); arcs and snaps are smooth, never strobing; no full-frame luminance
  jumps. The one pulse covers <25% of the frame at low amplitude.
- **No red:** debt never uses red, both semantically (not an error) and to
  stay clear of the red-flash threshold.
- **Contrast:** captions ~11:1, slug ~7:1, all body text ≥4.5:1; wordmark large
  (≥3:1). Verify with a checker before ship.
- **Not color-alone:** the catch = motion + ✓ + text.
- **GIFs ignore `prefers-reduced-motion`** → ship a **static poster**
  (`poster.png`, the beat-2 settled frame) for reduced-motion / social-card /
  no-autoplay contexts, and write descriptive `alt` text (mirror the existing
  hero's detailed alt).

---

## 10. Determinism & build pipeline

**Shipped stack:** [Motion Canvas](https://motioncanvas.io/) (MIT TypeScript,
purpose-built for "informative vector animations") → image-sequence exporter →
two-pass ffmpeg. MIT-clean throughout. Pivot rationale and the trade-off vs.
Remotion / hand-rolled HTML+Playwright is in the conversation thread that
produced this spec; in short, Motion Canvas was the only option with a
real timeline scrubber, OSS license, and exact `cubic-bezier` easing.

1. **`src/theme.ts`**: the design tokens from §3–§6 expressed as code, with
   a Newton/​bisection cubic-bezier solver so MC tweens match the exact
   Material curves to 1e-6.
2. **`src/scenes/main.tsx`**: the whole animation as a single generator
   scene. Frame = pure function of time, so output is deterministic.
3. **Render**: the editor's RENDER button writes a 1280×720 PNG sequence
   to `output/project/`. Headless automation via the Vite dev server +
   Playwright is wired into the agent loop but kept out of the human
   workflow (one extra click is cheaper than a puppeteer dep).
4. **`tools/encode.sh`** (`npm run encode`): two-pass ffmpeg → GIF + poster.

### Field-tested gotchas (don't re-discover these)

- **Children of a Rect use LOCAL coordinates** (relative to the rect's center),
  not view-absolute. The whole panel-positioning math chains off this.
- **`offset` doesn't behave as expected on `<Txt>`** the way `<Rect>` does;
  setting `width` on a Txt turns its child spans into flex items that get
  *distributed* across the width. Use neither for code lines. Anchor with
  `offset={[-1,0]}` at a known left-edge x.
- **MC collapses leading whitespace in the first span of an inline run.** So
  indentation can't be string-based; we express indent as a per-line column
  shift (`x={charX(indent)}`) and use NBSP between inline tokens to keep
  intra-line spacing exact.

---

## 11. Encoding & file-size budget

Two-pass palette with a static background (ubitux recipe). The shipped form
lives in [`tools/encode.sh`](./tools/encode.sh) (`npm run encode`):

```sh
# pass 1: palettegen: note ffmpeg ≥8 requires -update 1 for single-image out
ffmpeg -y -framerate 25 -i output/project/%06d.png -frames:v 1 -update 1 \
  -vf "scale=960:-1:flags=lanczos,palettegen=max_colors=192:stats_mode=diff" \
  /tmp/pal.png

# pass 2: paletteuse: filter_complex with explicit [0:v] input label
ffmpeg -y -framerate 25 -i output/project/%06d.png -i /tmp/pal.png \
  -filter_complex "[0:v]scale=960:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
  -loop 0 debt-ops-concept.gif
```

| Budget | Target | Shipped | If over |
|---|---|---|---|
| File size | ≤3 MB | **~1.1 MB** ✓ | drop fps→20, then width→800, then `max_colors`→128 |

- `stats_mode=diff` + `diff_mode=rectangle` + a **static background** keep bytes
  on the moving foreground only.
- Optional lighter twin: animated **WebP** (~30–50% smaller, same quality) via
  `<picture>`. GIF stays the default since GIF was the brief.

---

## 12. Deliverables (as shipped)

```
demo/concept/
├── DESIGN.md                 # this spec
├── README.md                 # short user-facing doc (render + encode)
├── package.json              # Motion Canvas + Vite + fontsource deps
├── vite.config.ts            # MC plugin wiring (with CJS interop note)
├── tsconfig.json             # extends @motion-canvas/2d
├── src/
│   ├── project.ts            # loads scene + bundled woff2 fonts
│   ├── project.meta          # 1280×720, 25 fps, image-sequence exporter
│   ├── theme.ts              # color/type/easing/duration tokens
│   └── scenes/main.tsx       # the whole animation
├── tools/encode.sh           # two-pass ffmpeg → GIF + poster
├── poster.png                # static fallback (hero-hold frame)
└── debt-ops-concept.gif      # the deliverable
```

The existing `demo/debt-ops.gif` (VHS terminal hero) stays untouched: different
asset, different audience.

---

## 14. What changed during build (notes for future maintainers)

1. **Captions cut.** The lower-third beat captions in §7/§8 were removed late
   in the build. The visuals carry the whole story (deferral underlined →
   chip flies → ledger → completion + drop → empty registry → brand). The
   tagline stays as part of the brand resolve. Captions were redundant signal
   in a piece this short; cutting them tightened the runtime by ~3 s.
2. **Beat 4 reworked from prune-with-word to visual completion + drop.** The
   `❯ drop B` typed command was dropped along with the captions. Card B
   slides off as noise; card A gets paid down (green border + ✓ stamp pulse
   + strikethrough on the slug + recede) and the registry count returns to
   zero. Same "stays out of your way" message, told entirely by motion.
3. **Code panel is honest.** The `// TODO: tidy log format` nit is now an
   actual line in the rendered snippet (between `payload.total` and the `if`), so
   the second chip really originates from code the viewer can see. Not a chip
   conjured from offscreen.
4. **Runtime ~12.8 s** (down from the spec's 12.6 s target after pacing
   tuning; not a meaningful drift).

---

## 13. Open knobs (decide in review, everything else is locked)

1. **Placement** *(decided)*: README "Why it exists" section, below the VHS
   hero GIF. Not the hero slot.
2. **Second deferral** *(decided)*: the hero catch is the `as any` loosened type
   (matches the VHS demo); `log-format-nit` stays as the pruned nit (card B).
3. **Wordmark lockup**: two-tone "debt-**ops**" vs. an orange dot mark.
4. **Twin format**: ship the WebP twin now or later.
</content>
</invoke>

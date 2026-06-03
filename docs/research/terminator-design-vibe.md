# Terminator — Design Vibe Brief (for the Designer)

> The *feel* we're after, as vocabulary — not layout. Plus how to use shadcn/ui without
> looking like default shadcn. Hand this to the designer as a north star + word bank.

## North star (one line)

**Quiet, engineered, mission-control-calm: the map recedes and the data advances. Dense
but breathable, near-black with surface-based depth, one accent, hairline structure,
tabular numerals — restraint that reads as confidence.**

---

## Word bank (lead with the **bold** ones)

**Overall tone**
- **Restrained** — say less; absence of decoration is the statement.
- **Considered** — everything looks chosen, nothing defaulted.
- **Quiet / calm** — the UI recedes so the data is the loudest thing on screen.
- **Precise / engineered** — tight tolerances, built-by-engineers feel.
- Matte, not flashy · disciplined · purpose-built · crafted microstates.

**Color**
- **Low-chroma / desaturated** — accents toned down, nothing screams.
- **Monochrome + single accent** — neutral foundation, one color used sparingly.
- **Context color only** — color = meaning (status, deltas, alerts), never decoration.
- Tinted neutrals (grays with a faint hue, not dead gray) · high-contrast, nothing muddy.

**Density & space** (the tension you care about)
- **High-density but breathable** — packed yet has room to breathe.
- **Tight, consistent rhythm** — 4/8/12px spacing applied uniformly so tightness reads
  as *order*, not crowding. Structured density ≠ cramped.
- **Data-ink disciplined** — strip borders/fills/gridlines that carry no information.
- Interaction density over visual density · progressive disclosure · scannable rows over cards.

**Typography**
- **Engineered typeface** — Inter / Geist / IBM Plex / Söhne (geometric, screen-tuned).
- **Tabular / monospaced numerals** — fixed-width digits so numbers align and compare.
- **Tight tracking** — slightly negative letter-spacing for a crisp, intentional feel.
- Small-caps micro-labels · one type family as the brand anchor · systemic scale.

**Surface & depth** (dark mode)
- **Near-black, not true-black** — deep charcoal/navy; pure #000 reads cheap and flat.
- **Elevation via surface, not shadow** — layers separated by subtle lightness shifts
  (base → raised → overlay).
- **Hairline / 1px borders** do the structural work quietly.
- Subtle glow over neon · layered surfaces · designed (brand-tinted) focus ring · optional whisper of grain.

**Motion**
- **Snappy / instant** — sub-300ms, ease-out; speed is a feature.
- **Purposeful, not decorative** — motion signals state change, never shows off.
- Interruptible · authored easing curves · microinteractions as the signature of craft.

---

## Map-specific vocabulary

**Basemap / cartography**
- **"The map recedes, data advances"** — desaturated, compressed lightness range so
  overlays own the foreground. ≤2 hues, hairline geography, lowered label density.
- Quiet / understated basemap · figure-ground discipline · night-mode-legible (not just inverted).

**Controls & overlays**
- **Floating panels — flat matte OR tasteful frosted glass** (12–32px backdrop-blur,
  10–40% opacity), used *structurally* to signal hierarchy (panel < modal < tooltip),
  never as ornament. Restrained, not "everything is frosted."
- **Scrim** — semi-opaque gradient that quiets imagery so overlaid text stays readable.
- Hairline semi-transparent borders · faint rim-light · monochrome single-weight icons · thin low-ink legends.

**Data on the map**
- **Perceptually-uniform, colorblind-safe ramp** (viridis/cividis) — equal steps look equal.
- **Data pops off a muted ground** — high-chroma overlays earn their saturation against the desaturated base.
- **Glow for "live/active"** markers (restrained luminance), not garish fills · density
  encodings (hexbin/heat) over pin clutter · elegant animated flow (wind/particle), purposeful not busy.

**Tone**
- **Mission-control / situational-awareness / telemetry / instrument / HUD** — but
  **tactical-but-calm**: cockpit legibility without sci-fi neon theatrics. Calibrated, precise, instant feedback.

---

## shadcn/ui: leverage it, don't look like it

**What to leverage**
- **MapCN** (`mapcn.dev`) — MapLibre-based shadcn map components (markers, controls,
  fly-to, routes, live overlays), no API key, full code ownership. Best fit; note it
  publishes no a11y guarantees, so we own that.
- **shadcn charts** (official, Recharts) over **Tremor** for the dashboard — lighter,
  matches our tokens exactly (Tremor is fast but ~200kB and has a recognizable "Tremor look").
- **Origin UI / ReUI** for richer data tables/timelines where stock shadcn is thin.

**The tell — what makes a site read as "default shadcn":** the zinc/neutral palette +
Geist font + Lucide icons + `rounded-md` (0.5rem) radius + thin `ring-ring/50` focus ring
+ comfortable (Vega) spacing. Break all of these:

1. **Start from a dense base, not Vega.** `npx shadcn create` ships named styles —
   use **Mira (dense, product-focused)** or **Lyra (sharp/mono)**; it rewrites component
   code, not just colors. Vega = the generic look to avoid.
2. **Change `--radius`** off the 0.5rem default (sharper ~0.25rem suits an ops/data feel).
3. **Abandon zinc/neutral** — the gray *is* the tell. Set a real brand primary and
   retheme the neutrals in OKLCH (use **tweakcn** as the single source of truth for
   radius/spacing/shadow/color tokens; exports Tailwind v4 vars).
4. **Swap the font** off Geist/Inter defaults (distinct display + body pairing).
5. **Tighten density** globally (h-8 rows, py-1 cells); optional Compact/Comfortable toggle.
6. **Custom focus ring** (deliberate + brand-tinted) and **swap the icon set** off Lucide.
7. **Bespoke data-viz, empty/loading/skeleton states** — stock ones are recognizable.
8. **Restrained motion** — one or two intentional micro-interactions, not a Magic-UI
   confetti. Over-animation just trades "generic shadcn" for "generic Aceternity."

---

## Accessibility guardrails (part of the considered vibe — keep while customizing)

- **Fix the focus-ring contrast** — the default `ring-ring/50` commonly **fails WCAG 3:1**;
  our custom ring must clear it.
- **Never color alone** (status, map markers, KPI deltas) — pair with icon/text/shape.
- **Text contrast 4.5:1, large/non-text 3:1**; scrim-back text over imagery.
- **Don't break Radix a11y** when restyling (`asChild` needs a focusable child; forward
  refs + spread props; icon-only controls need `aria-label`).
- **Density ≠ tiny hit areas** — keep touch targets usable. Test keyboard-only + screen
  reader + axe.

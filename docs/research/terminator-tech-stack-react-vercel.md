# Terminator — React + Vercel Variant (Cost-Conscious)

> Companion to `terminator-tech-stack.md` (the Svelte/all-Cloudflare baseline). This
> documents the stack if we use **React/Next.js on Vercel** instead, optimized to stay
> cheap by leaning on Vercel's caching — and on Cloudflare R2 where Vercel is expensive.

## TL;DR

React is a fine choice here **because the hottest updates are routed *around* React's
render path** (canvas via refs, charts via imperative Canvas APIs, streams via rAF) —
so the VDOM tax rarely sits on the critical path. On hosting, the cost-smart move is a
**split**: Vercel for the Next.js app + cached feed routes, **Cloudflare R2 for the
PMTiles** (zero egress), and the firehose fan-out **off Vercel**. Expect **~$20/seat/mo**
(Vercel Pro) vs **$0–5** for the all-Cloudflare baseline.

---

## Part A — React done well for this app

The principle (from the deck.gl and react-three-fiber teams): **keep high-frequency
data out of React's render tree.** React renders *structure*; refs + an external store +
requestAnimationFrame drive everything that ticks at 1–30 Hz.

| Concern | Do this | Not this |
|---|---|---|
| Firehose / 30Hz metrics | Buffer messages into a `useRef`, flush once per frame via **rAF**; commit to a **Zustand** store | `setState` per message |
| Live values on screen | Read the store **transiently** (`store.subscribe` / refs) so the node updates without re-rendering | Context (re-renders the whole subtree) |
| Structural state (selected layer, panel open, scrubber commit) | `useSyncExternalStore` selectors — low frequency, genuine re-render | Putting fast values here |
| deck.gl | `MapboxOverlay` + `useControl` on **`@vis.gl/react-maplibre`** (v8.x); feed it imperatively with `setProps` — the deck instance lives outside the component tree | `<DeckGL>` re-rendered every frame |
| Hover tooltips | Write to the DOM directly from `onHover` using `PickingInfo.x/y` | `setState` in `onHover` (fires every frame — the #1 deck.gl-in-React bug) |
| Camera | Hold `viewState` in the store, update via the controller imperatively | Round-trip every `onMove` through React state |
| Live charts | **uPlot via `uplot-react`** (Canvas-2D, fed imperatively from the rAF flush; it doesn't recreate the instance on prop change) | visx/SVG charts for 30Hz (DOM churn) |

Notes:
- **React Compiler (1.0, prod-ready) helps but isn't the savior.** It auto-memoizes to
  cut prop-churn re-renders, but it operates *inside* the VDOM model — it does not make
  30Hz `setState` cheap, and it can **fail silently on exactly the hot components**. Let
  it clean up component boundaries; don't depend on it for the hot loop. Architect the
  hot paths so they don't need it.
- **Recreating deck.gl layers every render is cheap** — deck diffs props and only
  touches GPU buffers when they change. The cost is the *surrounding React re-render*,
  not layer creation.
- **Next.js SSR:** deck.gl/MapLibre need a WebGL context — isolate them to a client
  component, exclude from server rendering.
- **Bundle:** React's runtime (~45KB) vs Svelte (~5KB) is real on hello-world but a
  rounding error here — **maplibre-gl + deck.gl + luma.gl dominate the bundle** by
  hundreds of KB. Bundle size is not a credible reason to reject React for this product.

**Honest residual cost vs signals:** React stays ~50–60% behind Svelte 5/Solid on raw
DOM-mutation benchmarks, and carries the conceptual overhead (render boundaries,
dependency arrays) signals eliminate. But with the architecture above, React's diffing
is bounded by the GPU/canvas layer, not by React — you get React's ecosystem + DX with
performance effectively capped by the hardware, not the framework.

**React-side stack:** Next.js (App Router) + **Zustand** (single source of truth) +
`@vis.gl/react-maplibre` + deck.gl `MapboxOverlay` + `uplot-react`. Optional
`@preact/signals-react` only for a metric grid if store+rAF isn't granular enough.

---

## Part B — Cost-conscious Vercel deployment

### What actually costs money (2025/2026 model)
Vercel moved to **credit-based usage billing** (Sept 2025). For a mostly-static map app
the spend is **bandwidth + edge requests**, not compute:
- **Fast Data Transfer (bandwidth)** — Hobby 100 GB/mo (then paused); Pro 1 TB included,
  then **$0.15/GB**. The #1 trap for a tile/asset-heavy app.
- **Edge Requests** — Hobby 1M/mo; Pro 10M included, then **$2/1M**. *Every* fetch counts
  **even on a cache HIT** — a polling dashboard can rack these up.
- **Functions (Fluid compute)** — Active CPU **~$0.128/hr** (cheap US regions) + memory +
  invocations (first 1M free). **CPU pauses during I/O**, so cached feed proxies cost
  almost nothing; **memory bills for the whole in-flight duration** (matters for streams).
- **ISR / Data Cache** — billed as reads ($0.40/1M) / writes ($4/1M); **CDN cache reads
  are free**. Design so the common path is a free CDN hit.
- ⚠️ **Hobby is non-commercial only.** Any commercial angle → **Pro ($20/seat/mo, includes
  $20 credits)**.

### The caching plan (make visitors hit cache, not upstream)
Proxy each periodic feed through a Next **route handler** with edge cache headers:
- **NOAA aurora (~5 min):** `Cache-Control: public, s-maxage=300, stale-while-revalidate=600`
  (or `fetch(url, { next: { revalidate: 300 } })`).
- **Weather / AQ (hourly):** `s-maxage=3600, stale-while-revalidate=1800`.
- Result: thousands of visitor polls collapse into ~12 upstream fetches/hr, served from
  the **free CDN cache**; the function runs only on revalidation.
- Use **`use cache` + `cacheLife`** (Next 15/16) — `unstable_cache` is **deprecated in
  Next 16**; match the installed version (project rule).
- **Edge Config** for tiny hot config (map style URL, active-layer flags) — sub-ms reads.
  Don't put feeds there. KV/Blob aren't needed if you cache at the edge.

### Tiles: keep them on Cloudflare R2 (decisive)
- **Vercel Blob bills egress (~$0.05/GB) + an Edge Request per tile access** even on cache
  hits. Serving ~1 TB/mo of tiles ≈ **~$50/mo on Blob** plus edge-request and bandwidth
  meter hits.
- **Cloudflare R2 = $0 egress** (storage $0.015/GB-mo; 10 GB + 10M reads free). Same 1 TB
  ≈ **~$0**.
- **→ Serve the `.pmtiles` archive directly from R2** (public/custom domain, browser
  range-requests it), fronted by Cloudflare's cache, with CORS + `Accept-Ranges` set.
  This also keeps tile bytes **entirely off Vercel's bandwidth meter**.

### Firehose: not on Vercel
- Vercel functions cap at **300s default / 800s max**, **don't host raw WebSockets**, and
  **memory bills for the entire streaming duration** — a persistent fan-out is a poor,
  expensive fit.
- **→ Keep the Wikimedia firehose fan-out on a Cloudflare Durable Object** (hibernatable
  WebSockets, ~$5/mo floor) or a small always-on box. The **$0 alternative** still
  applies: cron-write an aggregated snapshot to KV and poll it.

### Avoid the traps
- Don't let the client re-poll feeds on window-focus (React Query/SWR refocus refetch
  inflates Edge Requests) — cache at the edge and lengthen client intervals.
- Don't proxy tiles through Vercel functions (doubles cost: Fast Origin + Fast Data
  Transfer). Serve from R2 directly.
- Keep `ETag`/`If-Modified-Since` on (Next default) for cheap 304s.
- Pin functions to cheap regions (iad1/pdx1/cle1) for lowest Active CPU.

---

## Part C — Cost & tradeoff vs the all-Cloudflare baseline

| | All-Cloudflare (Svelte) | React + Vercel (this doc) |
|---|---|---|
| App host | Pages (unmetered bandwidth, free) | Vercel Pro (**$20/seat/mo**, commercial requires it) |
| Tiles | R2 ($0 egress) | **R2 ($0 egress)** — same; don't use Blob |
| Cached feeds | Workers + KV + SWR (free tier) | Next route handlers + CDN/ISR cache (mostly free CDN hits) |
| Firehose | Durable Object ($5 or $0 poll) | **Same — Durable Object off Vercel** ($5 or $0 poll) |
| Framework perf | Signals, ~50–60% faster on DOM churn | VDOM, hot paths routed around it → effectively GPU-bound |
| **Typical monthly** | **$0–5** | **~$20–28** (Pro + R2 + optional DO) |

**The honest read:** going Vercel costs ~$20/seat/mo more and *still* pulls in Cloudflare
for the two things Vercel does expensively (zero-egress tile storage, persistent
streaming). You're paying for React/Next DX + Vercel's deploy polish and previews. If the
team is React-first and values that workflow, the plan above keeps Vercel's bill flat and
predictable. If minimizing cost is the top priority, the all-Cloudflare baseline wins —
and you can *still write it in React* (Next `adapter`/SPA or Vite + React on Pages) to get
the framework without Vercel's pricing. The framework choice and the host choice are
independent.

# Terminator — Tech Stack (Speed + Cost Optimized)

> Research-backed stack for a real-time map + dashboard that is hyper-efficient on
> **render speed** (many live geo layers on a globe) and **run cost** (near-$0 at
> portfolio scale, scales cheaply). Companion to `map-dashboard-plan.md` and
> `terminator-data-blueprint.md`.

## TL;DR

**All-Cloudflare hosting + a signals-based static frontend + GPU map rendering.**
Runs at **$0/month** until you opt into server-pushed real-time, then a **$5/month**
floor. Nothing else has an always-on server, tile bill, or egress fee.

| Layer | Pick | Why (speed + cost) |
|---|---|---|
| Framework | **SvelteKit (Svelte 5 runes)** or SolidStart | Signals = surgical DOM updates, no re-render cascade next to the GPU canvas; ~5–7KB runtime, near-vanilla benchmark. |
| Output | **`adapter-static` SPA** (or Astro islands) | Fully static, CDN-hostable, no SSR server to pay for; fast first paint. |
| Build | **Vite 8 + Rolldown**, **Bun** as pkg mgr / script runner | 10–30× faster prod builds vs Rollup; Bun speeds installs/scripts. |
| Map | **MapLibre GL JS + PMTiles + deck.gl** | BSD/MIT, GPU layers, no tile-server, no map-load billing. |
| Charts | **uPlot** | ~20KB, streams 3,600 pts @60fps ~10% CPU; built for live time-series. |
| Static host | **Cloudflare Pages** | **Unlimited free bandwidth**, global edge, no cold start. |
| Tile/raster storage | **Cloudflare R2** | **$0 egress**; 10GB + 10M reads free → realistically $0–3/mo. |
| Feed proxy + cache | **Cloudflare Workers** (Cache API / KV + Cron) | Free 100k req/day; CPU billed only on compute, not on `fetch()` waits. |
| Real-time fan-out (optional) | **Durable Object + WebSocket Hibernation** | Cheapest server-push; ~$5/mo floor, $0 duration while idle. |

## Frontend

- **Why signals, not React:** the dashboard pushes 1–30 Hz updates (time-scrubber,
  live metric cards, firehose pulse) right next to a WebGL canvas. Svelte 5 / Solid
  update only the exact bound node; VDOM frameworks re-run components every tick — the
  classic deck.gl trap is `onHover`/`onViewStateChange` firing every frame and
  triggering React tree re-renders. React would only win on ecosystem/hiring, at a
  measurable bundle + re-render cost.
- **The map pixels don't care about the framework** — deck.gl renders on the GPU
  outside DOM diffing (its React wrapper "does not add significant overhead"). Framework
  choice matters for the *chrome and high-frequency state plumbing*, which is exactly
  where signals win. deck.gl is framework-agnostic via the standalone `Deck` class;
  `svelte-maplibre-gl` is a maintained Svelte 5 MapLibre wrapper.
- **Charts:** uPlot for everything live; add visx only for bespoke non-streaming
  widgets. Avoid ECharts (~1MB) unless you need 100k+ points.

## Hosting & storage (all Cloudflare)

- **Pages** for the static app — uniquely **unmetered bandwidth** on the free tier
  (Vercel/Netlify cap at 100 GB/mo and bill overage; a popular map app blows past that).
- **R2** for PMTiles basemap + baked rasters (night-lights, light-pollution). **Zero
  egress** is decisive: 10M tile reads ≈ **$11 on R2 vs ~$120 on S3 vs ~$3,600 on
  Google Maps**; a real ~120 GB global tileset reported at **$1.67/mo**. PMTiles serves
  via HTTP range requests, so cost is per-request (Class B), not per-byte.
- Avoid **S3+CloudFront** ($0.09/GB egress) for globally-served tiles. **Bunny.net**
  ($0.005/GB) or **B2+Cloudflare** (free egress via Bandwidth Alliance) only if you ever
  leave Cloudflare. **Deno Deploy** (1M req + 100GB free) is the no-lock-in edge
  fallback for proxies. Avoid **Render/Fly** for anything latency-sensitive (cold
  starts / no permanent free tier).

## Data / real-time architecture

The rule: **stream only the firehose; poll everything else from an edge cache;
compute what you can on the client.**

- **Periodic JSON (aurora ~5 min, weather/AQ hourly):** a **Workers Cron Trigger**
  fetches each on its cadence → **KV**; every visitor reads the cached copy with
  **`stale-while-revalidate`**. Collapses N visitor hits into 1 upstream call per
  interval — respects rate limits, stays on the free tier, no streaming needed.
- **Client-computed layers (terminator, % awake, births/deaths):** pure functions of
  time — compute in a **Web Worker** on a timer, zero network.
- **Wikimedia firehose:** **one** Durable Object subscribes once (SSE with
  `Last-Event-ID` resume), **aggregates/throttles**, and fans out to browsers over
  **hibernatable WebSockets**. Never let each visitor open their own upstream
  connection — the public endpoint is capped (~450 total) and forwarding raw multiplies
  bandwidth by N.
- **Client rendering:** buffer stream events into state; render once per frame via an
  **rAF-throttled loop** (decouple data ticks from render ticks); push heavy work to a
  **Web Worker (OffscreenCanvas)** so firehose parsing never stalls the map. Keep JSON
  deltas small; reach for Protobuf/FlatBuffers only if payloads get large.

## Cost ladder

| Stage | Monthly cost |
|---|---|
| Static app + R2 tiles + cron-cached feeds (poll-only) | **$0** (within free tiers) |
| Heavier tile traffic | **$0–3** (R2 reads) |
| Add server-pushed real-time (Durable Object fan-out) | **$5 floor** |

**$0 option for real-time:** instead of a Durable Object, have the cron Worker also
write an aggregated snapshot (e.g. "edits in the last 10s") to KV and **poll** it. You
lose true push (a few seconds of latency) but stay fully free. Add the DO only if
live-push smoothness is worth the $5.

## Stated tradeoffs

- Svelte/Solid have smaller ecosystems than React (fewer prebuilt dashboard
  components; you may wrap deck.gl yourself — `svelte-maplibre-gl` helps).
- All-Cloudflare means some lock-in; the listed fallbacks (Bunny, B2, Deno Deploy)
  exist precisely to de-risk that.
- SSE on plain serverless hits the ~300s function timeout and must reconnect — which is
  exactly why the firehose lives in a Durable Object, not a Worker.

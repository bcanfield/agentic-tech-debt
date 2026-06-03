# Terminator — React + Vercel Build Guide (Concrete)

> Deep-dive on the React/Next.js-on-Vercel approach: concrete App Router architecture,
> the Vercel↔Cloudflare boundary, deployment specifics, and grounded cost reality.
> Builds on `terminator-tech-stack-react-vercel.md` (the comparison) with
> implementation-level detail. Match exact API names to the installed Next.js version.

## Architecture at a glance

```
Browser ──HTTPS──▶ Cloudflare (proxy + Cache Rules, WAF)
                      ├─▶ Vercel  (Next.js app shell, SSR/ISR, cached feed routes, token minting)
                      └─▶ R2      (basemap.pmtiles, baked rasters — zero egress)
Browser ──WSS────▶ Cloudflare Durable Object  (Wikimedia firehose fan-out — never via Vercel)
```

Three hosts, one repo. Vercel serves the app; **R2 serves tiles**; a **Durable Object**
serves the live stream. Cloudflare sits in front of all of it.

## 1. Next.js App Router layout

```
app/
  layout.tsx                 # server; global CSS
  page.tsx                   # SERVER component → renders <MapClient/> + <Dashboard/>
  api/
    feed/[source]/route.ts   # Node runtime cached proxy for aurora/weather/AQ
    ws-token/route.ts        # mints a short-lived signed token for the DO WebSocket
    revalidate/route.ts      # webhook → revalidateTag() for push freshness
components/
  MapClient.tsx              # "use client"; dynamic(() => import('./Map'), { ssr:false })
  Map.tsx                    # "use client"; maplibre + deck.gl + pmtiles protocol
  Dashboard.tsx              # client; Zustand store, uPlot charts, WS connection
lib/
  store.ts                   # Zustand single source of truth
  ws.ts                      # DO WebSocket client (backoff + jitter)
```

**Client/server boundary (the one gotcha):** `dynamic(..., { ssr:false })` is **not
allowed in a Server Component** in App Router. Use the two-file pattern — a `"use client"`
`MapClient.tsx` does the dynamic import; the server `page.tsx` renders `<MapClient/>`.
Everything touching `window`/WebGL/`maplibre-gl` lives in `Map.tsx`. deck.gl needs a WebGL
context, so SSR buys nothing — exclude it.

**Reference repo (closest real match):** [Pharos AI](https://github.com/Juliusolsson05/pharos-ai)
— Next 16 + React 19 + deck.gl + MapLibre on Vercel, feature-modular layout.

## 2. deck.gl + MapLibre wiring

- Import from the MapLibre entry: `import { Map, useControl } from 'react-map-gl/maplibre'`
  (or `@vis.gl/react-maplibre` v8) and `import { MapboxOverlay } from '@deck.gl/mapbox'`.
- Integrate deck.gl as a **`MapboxOverlay` via `useControl`** (a `null`-rendering
  component), **interleaved** mode for correct z-mixing with basemap labels (needs
  maplibre-gl ≥3). Push new props imperatively with `overlay.setProps(...)` — the deck
  instance lives **outside** React's tree.
- `import 'maplibre-gl/dist/maplibre-gl.css'` in the client map component.
- **Perf rule:** never `setState` in `onHover`/`onViewStateChange` (they fire every
  frame). Write hover tooltips to the DOM from `PickingInfo.x/y`; keep `viewState` in the
  Zustand store. Recreating layers each render is fine — deck diffs props and only touches
  GPU buffers on change.
- Turbopack dev caveat: an open bug drops MapLibre's inline worker under `next dev
  --turbo` (blank tiles); use webpack dev if hit.

## 3. PMTiles from R2

- Register once, client-side, with cleanup:
  ```ts
  import { Protocol } from 'pmtiles';
  const protocol = new Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile);   // in useEffect
  return () => maplibregl.removeProtocol('pmtiles');   // cleanup
  ```
- Style source URL: `"url": "pmtiles://https://<r2-domain>/basemap.pmtiles"` (the
  `pmtiles://` scheme auto-derives min/max zoom).
- **R2 CORS must allow Range requests:** `methods: ["GET","HEAD"]`, `headers:
  ["range","if-match"]`, `exposeHeaders: ["etag"]`. Front the R2 bucket with Cloudflare's
  cache so repeated range reads are cache hits (Class-B-free).

## 4. Caching the periodic feeds (Vercel side)

Proxy each upstream feed through a **Node-runtime** Route Handler so one fetch is shared
by all visitors. Two equivalent models — **pick one per route, don't mix:**

- **Header model:** return `Cache-Control: public, s-maxage=300, stale-while-revalidate=600`
  (aurora ~5min) / `s-maxage=3600, stale-while-revalidate=1800` (weather/AQ hourly).
  Vercel's edge honors `s-maxage` + SWR. Note: GET handlers are **dynamic by default since
  Next 15** — you must opt into caching. `export const revalidate = 300` is the simplest knob.
- **Cache Components model (Next 15/16):** `'use cache'` + `cacheLife('minutes')` +
  `cacheTag('aurora')`; invalidate on push via a webhook calling `revalidateTag('aurora')`
  (or `updateTag` in Next 16). `unstable_cache` is legacy — prefer `use cache` for new code.
- **Edge vs Node:** framework `revalidate` isn't available under `runtime='edge'`; use Node
  + `revalidate`/`use cache` for cached proxies, or Edge + explicit `Cache-Control` headers
  for raw low-latency. Truly live data should bypass the cache (Suspense-streamed or
  client-polled), not `use cache`.

## 5. The WebSocket boundary (firehose)

**Confirmed: Vercel functions cannot hold WebSockets, even with Fluid compute** — each
invocation ends when it returns. So:

- **Browser connects directly to the Cloudflare Durable Object** (WSS). The stream never
  touches Vercel — which also keeps firehose bytes **off Vercel's bandwidth meter**.
- **Auth:** cookies don't work cross-origin; mint a **short-lived signed token** from a
  normal Vercel route (`/api/ws-token`) and pass it as a URL query param; the Worker
  verifies it + checks `Origin` against an allowlist before the upgrade. Keep expirations
  to minutes.
- **Client reconnect:** exponential backoff **with jitter** (base ~500ms, ×2, cap ~30s),
  reset on open, plus an app-level heartbeat. Jitter is mandatory to avoid reconnection
  storms when the DO restarts.
- **DO implementation:** accept via `ctx.acceptWebSocket(ws)` (Hibernation API); broadcast
  with `ctx.getWebSockets().forEach(ws => ws.send(...))`; use
  `setWebSocketAutoResponse(...)` for pings so keepalives don't wake the DO. One DO holds a
  **single upstream `EventSource`** subscriber to Wikimedia and fans every parsed event
  out. Caveat: **outgoing connections don't hibernate** (workerd#4864), so the upstream
  subscriber keeps this DO warm — factor that into cost (it won't fully idle-hibernate).
- **Vercel SSE is fine for *short* streams** (token mint, a bounded query): 300s default /
  800s Pro max, Edge must emit first byte within 25s. A permanent firehose is unsuitable —
  it'd burn a 5–13 min function continuously and hit the cap. Keep it on the DO.

## 6. Bundle & deploy hygiene (controls Fast Data Transfer)

- Map behind `dynamic({ ssr:false })` → its own chunk, out of the entry/server bundle.
- Tree-shake deck.gl: import layers individually (`import { ScatterplotLayer } from
  '@deck.gl/layers'`); install only the submodules you use. maplibre-gl + deck.gl +
  luma.gl dominate the bundle, so this is where the bytes are.
- `@next/bundle-analyzer` gated behind `ANALYZE=true` to verify the split.
- `images: { unoptimized: true }` — map imagery is tiles, not `next/image`; the
  optimization pipeline is metered dead weight.
- Don't over-split (`next/dynamic` everywhere) — each chunk is a separate fetch (waterfall).
- Immutable hashed chunks + strong cache headers so returning visitors serve from CDN.

## 7. Monorepo / previews (Turborepo)

- App deploys on Vercel (set its Root Directory); the Worker/DO deploys **separately** via
  Cloudflare CI (`wrangler`). Co-located in one repo, two deploy targets.
- Declare env vars in `turbo.json` (they're hashed into the build cache). `NEXT_PUBLIC_*`
  (e.g. the DO WSS URL) is **inlined at build time** — set per-environment values for
  preview vs prod.
- **Preview wrinkle:** each preview URL won't match a fixed Origin allowlist/token audience
  on the Worker — add a preview-origin rule or relax auth in preview. Preview builds
  consume the same quotas; scope them and use Ignored Build Step to skip when only the
  Worker changed.

## 8. Cost reality (grounded in real invoices)

**Pro = $20/seat/mo with a $20 flexible usage credit** (Sept 2025 credit model). Included:
**~1 TB Fast Data Transfer, 10M Edge Requests, 10M invocations, 40 CPU-hrs/mo.** Overage:
FDT **$0.15/GB**, Edge Requests **$2/1M**, invocations **$0.40/1M**, CPU **$5/hr**.

**What actually blows up bills — and our mitigations already cover them:**
- **Bandwidth + Edge Requests dominate, not compute.** A *static* site (Jmail) hit a
  **$46,485.99** bill at 450M views by blowing past 1 TB egress. Tiles are our biggest
  bandwidth risk → **on R2 (zero egress)**, not Vercel. ✅
- **Edge Requests count even on cache hits** → **put Cloudflare in front of Vercel** with
  Cache Rules so cached tile/feed hits never reach Vercel. One report cut origin bandwidth
  ~1,600× this way. *(This is the one tactic to add beyond R2.)* ✅
- **Per-request middleware** amplifies edge requests + invocations → keep auth/geo
  middleware off the hot tile/feed paths (tight matchers). ✅
- **Image Optimization** surprised teams (~$115/mo in one case) → `unoptimized`. ✅
- **Bots/AI scrapers** spike public endpoints → Cloudflare WAF/rate-limiting in front. ✅
- **Heavy/long compute** penalized per-invocation → firehose off Vercel (DO). ✅
- **Ghost seats** silently leak $20 each → audit billable seats.

**Expected monthly cost for this app (tiles on R2, feeds edge-cached, firehose off-Vercel,
Cloudflare in front):**
- 10k visitors → ~$20/seat, usage inside the credit (≈ just seat cost).
- 50k visitors → ~$22 metered usage, absorbed by credit → effectively seat-only.
- 100k visitors → typically **< $100/mo** while egress < ~1 TB and edge requests < 10M.
- Without offloading, ~250k visitors already ≈ **$305/mo** — the offloading is what keeps
  us in the cheap band. Migration tipping point to all-Cloudflare is the >$1,000–1,500/mo
  zone (very high egress).

⚠️ Hobby is **non-commercial only** — a real product needs Pro.

## Net

This is a **three-host hybrid**: Vercel (app + cached routes), R2 (tiles), Durable Object
(stream), with **Cloudflare proxying the whole thing**. It gives the React/Next + Vercel DX
(previews, deploys) while structurally removing the line items that generate Vercel bill
shock. Realistic spend at portfolio/moderate traffic: **~$20–100/mo**, dominated by seat
cost, not usage. The all-Cloudflare baseline ($0–5) is still cheaper — the delta is what
you pay for the Vercel workflow.

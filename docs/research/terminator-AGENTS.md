# AGENTS.md

Build a real-time map + dashboard ("Terminator"). Stack chosen for clean, cheap,
single-vendor ops. Match installed library versions; fetch current docs before using an API.

## Stack (do not substitute without asking)

- **React + Vite** (TypeScript). No Next.js — this is a client-rendered WebGL SPA.
- **Map:** MapLibre GL JS + **deck.gl** GPU overlays. Use `@vis.gl/react-maplibre`.
- **Basemap:** Protomaps **PMTiles**, single `.pmtiles` file on **Cloudflare R2**.
- **State:** **Zustand** (single store). **Charts:** **uPlot** (`uplot-react`).
- **Host:** **Cloudflare Pages** (app) + **Workers** (feed proxies/cron) + **R2** (tiles)
  + **Durable Object** (live stream). One Cloudflare account, one `wrangler` config.

## Architecture rules

- Keep high-frequency data **out of React's render tree**. React renders structure only.
- deck.gl runs **outside React**: `MapboxOverlay` via `useControl`, interleaved mode,
  fed imperatively with `setProps`. Recreating layers per render is fine.
- **Never `setState` from a stream/`onHover`/`onViewStateChange` callback** (fires every
  frame). Buffer to a `useRef`, flush once per frame via `requestAnimationFrame`.
- Live values read the Zustand store **transiently** (`subscribe`/refs) so nodes update
  without re-rendering. `useSyncExternalStore` selectors only for low-frequency structural
  state (selected layer, panel open).
- Feed uPlot imperatively from the rAF flush; don't recreate the instance.

## Data rules

- **Compute on the client** what you can (terminator, % awake, births/deaths) — pure
  functions of time, run in a **Web Worker**. No network.
- **Poll, don't stream, periodic feeds** (aurora ~5min, weather/AQ hourly): a **Worker
  cron** fetches once → **KV/Cache** with `stale-while-revalidate`; clients read the
  cached copy. One upstream call per interval, never one per visitor.
- **Stream only the Wikimedia firehose:** one **Durable Object** subscribes once
  (SSE, `Last-Event-ID` resume), aggregates/throttles, fans out over **hibernatable
  WebSockets** (`acceptWebSocket` / `getWebSockets()` / `setWebSocketAutoResponse`).
  Same-origin → no token/CORS dance. $0 fallback: cron-write a snapshot to KV and poll it.

## Hosting rules

- Tiles served **directly from R2** (range requests, CORS allows `range`), Cloudflare cache
  in front. Never proxy tiles through a Worker function.
- PMTiles: register `pmtiles://` protocol in a `useEffect` with cleanup; source URL
  `pmtiles://https://<r2>/basemap.pmtiles`.
- Static-first, code-split the map (lazy import) so it's its own chunk. Tree-shake deck.gl
  (import layers individually). Keep it $0–5/mo.

## Don't

- No Next.js, no Vercel, no second vendor, no always-on server beyond the Durable Object.
- No new dependencies without a concrete reason. No SSR for the map.

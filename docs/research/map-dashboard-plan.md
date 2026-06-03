# Map + Dashboard — Unique Data & Visualization Plan

> Research deliverable (not implementation). Goal: a map + dashboard that showcases
> expert app-design skills by being **genuinely unique** in *what* data it shows and
> *how* it shows it. Reference baseline: [worldmonitor](https://github.com/koala73/worldmonitor).
> Theme was left open ("just be unique"); design emphasis is balanced across data
> uniqueness, interaction/motion, and information design.

---

## TL;DR — the recommendation

**Build "Terminator" — a real-time dashboard organized around the moving day/night
line, not around objects.**

Every popular map (worldmonitor, FlightRadar24, MarineTraffic, Windy, Liveuamap)
answers *"what objects are where right now?"* — flights, ships, storms, quakes, news
dots. The field is saturated with object-tracking on the same handful of free feeds.

The gap: **nobody makes the planet's daily rhythm the subject.** The terminator —
the line between day and night sweeping around Earth every 24h — is a free,
compute-only spatial *and* temporal organizing device. Anchor the whole product on
it, and split everything into **the dark side** (what's happening at night right now)
and **the light side** (what's happening in daylight), with a **human-rhythm pulse**
underneath (how much of humanity is awake, being born, editing Wikipedia, hearing the
call to prayer at this second).

It wins on all three axes the brief cares about:
- **Data uniqueness** — a fusion nobody packages: terminator + night-lights +
  stargazing quality + aurora + nocturnal bird migration on the dark side; weather
  pleasantness + clean-energy share on the light side; awake/asleep + births/deaths +
  live edit firehose as the heartbeat. All free, almost all key-free, no real-time
  feed it depends on is rate-limited into uselessness.
- **Interaction & motion** — the terminator animation, a GPU aurora/particle layer,
  and a **time-scrubber that runs the day forward/back** are inherently cinematic.
- **Information design** — the day/night split is a built-in *focus+context* frame
  and a natural dark-mode cartography story.

It is also realistically buildable solo on a 100%-free, no-billing stack
(MapLibre + Protomaps/PMTiles + deck.gl).

---

## 1. The landscape, and why this is the gap

What the popular tools actually show (and where the data comes from):

| Category | Tools | Data source | Status |
|---|---|---|---|
| Flights | FlightRadar24, FlightAware, OpenSky | crowdsourced ADS-B + MLAT + sat-ADS-B | **saturated** |
| Ships | MarineTraffic, VesselFinder | terrestrial + satellite AIS | **saturated** |
| Weather | Windy, Ventusky, Zoom Earth, earth.nullschool | GFS/ECMWF + GOES/Himawari imagery | **saturated** |
| Quakes/fire | USGS, NASA FIRMS maps | free gov GeoJSON feeds | **saturated** |
| Air quality | aqicn, IQAir | aggregated PM2.5 station networks | **saturated** |
| News/conflict | Liveuamap, GDELT, ACLED | curated incidents / event graph | saturated among monitors |
| Connectivity | Cloudflare Radar, NetBlocks | network-vantage telemetry | **rarer** |
| Energy | Electricity Maps | grid carbon intensity | **rarer** |
| Deforestation | Global Forest Watch | GLAD/RADD satellite alerts | **rarer** |
| Experiential | Radio Garden | 40k live radio streams on a globe | **rare UX** |

**worldmonitor's** own bet is *breadth + AI synthesis + cross-domain correlation*
(500+ feeds → one risk index) on a dual globe/flat-map engine. The individual layers
are commodities; its moat is fusion-into-a-risk-score. We should **not** try to
out-breadth it — that's an arms race. We differentiate on **a single, opinionated,
emotionally resonant concept** instead.

**The transferable lesson from the award-winners** (Information is Beautiful, The
Pudding, NYT/Reuters): the memorable ones don't plot raw feeds — they **derive a
second story on top**. The Ship Map computed CO₂ from AIS movement; Population
Mountains rendered census data as terrain; Cultural Borders of Songs treated taste as
geography. *Derived layer over raw* is the principle our concept is built on.

---

## 2. The concept: "Terminator — the planet's daily rhythm"

One sentence: **a live globe where the day/night line is the hero, and you watch the
night — and everything that lives in it — chase its way around the Earth.**

The organizing question flips from *"what's where?"* to **"what's happening on the
dark side of Earth right now, and how much of humanity is awake to see it?"**

### The dark side (night layers)
- **Terminator + twilight bands** — civil / nautical / astronomical twilight rings.
  Pure astronomy, computed in-browser, *no API, no limits, no key.*
- **City lights** — NASA Black Marble night-lights as the night-side basemap glow.
- **Stargazing quality** — light-pollution atlas → "where can you actually see stars
  tonight?" A derived, evocative layer.
- **Aurora oval** — NOAA SWPC OVATION grid + Kp index → live northern/southern lights
  probability. Key-free JSON.
- **Nocturnal bird migration** — BirdCast live (US, seasonal) → "rivers of birds"
  that only appear at night. Conservation hook ties straight to light pollution.
- **(Optional) ISS / bright satellite passes** overhead — "what's flying over the
  dark side."

### The light side (day layers)
- **Pleasantness** — Open-Meteo temp/wind + air quality → a "best place to be outside
  right now" index following the sun.
- **Clean-energy share** — how green the grid is in daylight hours (solar chasing the
  sunrise). *See caveat: Electricity Maps free tier is 1 zone — use the open
  `electricitymaps-contrib` dataset or scope this to a few showcase regions.*

### The heartbeat (human-rhythm pulse, the dashboard's emotional core)
- **% of humanity awake vs asleep** — population raster × local time × sleep window.
  A single derived number that changes every minute.
- **Live edit firehose** — Wikimedia EventStreams `recentchange` (free, no key) as an
  ambient "humanity is thinking" pulse. *Caveat below on geolocation.*
- **Births / deaths this minute** — derived from UN annual rates (à la Breathing
  Earth). Spawns dots; emotionally heavy, technically trivial.
- **The "midnight wave" / new-day line** and optionally the **call-to-prayer wave** —
  rolling events that sweep the globe with the terminator.

The through-line: **time and light, not objects.** That single editorial decision is
the whole differentiator.

---

## 3. Data sources (all free; auth/limits noted)

**Tier A — zero-key, no meaningful limits (build on these first):**
- Terminator / twilight / golden hour — computed (SunCalc-style), no API.
- **NOAA SWPC** aurora + Kp — `/json/ovation_aurora_latest.json`, public domain.
- **Wikimedia EventStreams** — SSE `recentchange`, no key.
- **Open-Meteo** — weather, no key (≤10k calls/day; CC BY 4.0).
- **USGS / NASA EONET** — natural events GeoJSON, no key (nice "live alerts" garnish).
- NASA **Black Marble** night-lights — downloadable raster tiles (static layer).
- Births/deaths — derived from public UN rates (no feed needed).

**Tier B — free but needs a key (easy):**
- **NASA FIRMS** (fire garnish) — free `MAP_KEY`, 5k/10min.
- **OpenAQ v3** / **WAQI** (air quality) — free key. *WAQI license forbids paid
  apps/resale — fine for a free portfolio piece, attribution required.*

**Tier C — free but constrained (design around the limit):**
- **Electricity Maps** free tier = **1 zone, 50 req/hr, non-commercial**. For a global
  clean-energy wave, use the open-source **`electricitymaps-contrib`** dataset or
  limit the live layer to a few showcase zones.
- **Cloudflare Radar** — CC BY-NC (non-commercial); fine here if you want an
  internet-activity garnish.
- **Light-pollution atlas** — CC BY-NC raster, static (not a live feed).
- **BirdCast** — US-only, seasonal, scrape/derived (no clean public API); treat as a
  seasonal showcase layer, not a core dependency.

**Caveats flagged during verification (build around these):**
- ⚠️ **Wikipedia geolocated edits broke in Nov 2025** (temp-accounts change). The edit
  *firehose still works* key-free — map it by **wiki language/project**, not by
  precise geo IP.
- ⚠️ **Spotify Charts API is deprecated** — if you ever want a "what each timezone is
  listening to" layer, route via Last.fm/MusicBrainz instead. (Not in the core plan.)

---

## 4. How we'd show it

### Stack (100% free/open, no tile billing, no server required)
- **Basemap:** MapLibre GL JS (BSD) with a **Protomaps / PMTiles** basemap served as
  a single file from static storage (Cloudflare R2 / S3) — *no tile server, no
  per-load billing.*
- **Data overlays:** **deck.gl** (MIT) for GPU layers — millions of points, animated
  `TripsLayer`/`ArcLayer`, hexbin/heatmap aggregation; first-class MapLibre overlay.
- **Globe hero:** MapLibre globe projection, or **globe.gl** (Three.js) for a
  stylized "Earth from space" hero with built-in arcs/rings/atmosphere.
- **Glue / charts:** react-maplibre + Observable Plot / D3-geo for side-panel charts.
- **Particle/flow** (aurora shimmer, wind): `weatherlayers/deck.gl-particle` or the
  classic texture-driven GPU particle technique (mapbox/webgl-wind) — ~1M particles
  smoothly.

### Layout (map-as-hero, Shneiderman's mantra: overview → zoom/filter → detail)
- **Hero:** the globe, opening on a calm full view with the terminator already
  sweeping — *no empty state*, it's alive at first paint.
- **Left rail = the heartbeat:** a few big-number metric cards (% awake, births/deaths
  this minute, edits/sec) — one big number + one comparison + one sparkline each.
  Cognitive cap ~5–9 widgets; resist the urge to cram.
- **Bottom = the time ring:** a 24h scrubber that **runs the day forward/back** and
  fast-forwards the terminator — the signature interaction.
- **Right = details-on-demand:** click a region → its local time, "is it night here,"
  stargazing quality, aurora odds, what's awake. Linked views: map state drives the
  panels.
- **Dark-mode cartography done right:** muted basemap, ≤2 chrome hues, saturated color
  reserved for data; night-lights glow as the dark-side fill. Tabular-figure sans
  (Inter/IBM Plex) for numbers; Okabe-Ito / Viridis ramps (colorblind-safe).

### Motion (where the "expert design" shows)
- Terminator sweep + a slow auto-orbit on idle ("attract mode").
- Time-scrub the whole planet's day; the heartbeat numbers animate with object
  constancy (staged transitions, no jarring redraws).
- GPU aurora/particle shimmer on the night side.
- Scrollytelling "moments": camera `flyTo` chapters — *"Right now it's midnight over
  Tokyo and the aurora is out over Tromsø"* — curated guided views for onboarding.

### What makes it feel premium (and avoids the amateur tells)
- Skeleton-shimmer loads, not spinners; 200ms eased panel transitions.
- One chart *type* per idea; whitespace; relative-over-raw legends.
- Restraint over flair — clarity is the flex.

---

## 5. Suggested build order (MVP → showcase)

1. **MVP (the hook):** MapLibre globe + PMTiles + computed terminator + Black Marble
   night fill + "% of humanity awake" counter + time-scrubber. Zero keys. This alone
   is already unique and demoable.
2. **+ Heartbeat:** Wikimedia edit firehose pulse + births/deaths ticker.
3. **+ Night magic:** NOAA aurora oval (GPU particle shimmer) + stargazing-quality
   (light-pollution) layer.
4. **+ Day side:** Open-Meteo pleasantness index following the sun.
5. **+ Polish:** scrollytelling "moments," curated tours, accessibility pass.
6. **Optional garnishes:** FIRMS/EONET live alerts, BirdCast (seasonal), clean-energy
   wave (scoped to showcase zones).

---

## 6. Alternates considered (strong runners-up)

- **"The Night Side of Earth"** — a tighter cut of the above, pure nocturnal:
  terminator + night-lights + light pollution + aurora + stargazing. Simplest, all
  Tier-A data, gorgeous. Good fallback if scope tightens.
- **"Clean-Energy Sunrise Wave"** — animate solar generation chasing the sunrise
  terminator. Beautiful climate-optimism story, but **gated by the Electricity Maps
  1-zone free tier** — needs the open contrib dataset to go global.
- **"Most Pleasant Place on Earth Right Now"** — weather + AQI + golden hour → one
  shareable answer. Delightful and viral, but thinner as a *dashboard* (more of a
  single-hook toy).
- **"Is Humanity Awake?" ambient room** — the heartbeat layers as a meditative,
  sound-on loop (Hatnote "Listen to Wikipedia" lineage). Great as a mode *inside*
  Terminator rather than a standalone.

All four share the same DNA — **time/light/rhythm over object-tracking** — so the
recommendation is to ship Terminator and treat these as modes/cuts of it.

---

## 7. Sources

Landscape: worldmonitor, FlightRadar24, FlightAware, OpenSky, MarineTraffic, Windy,
Ventusky, earth.nullschool, Zoom Earth, NASA FIRMS, USGS, aqicn/IQAir, Cloudflare
Radar, NetBlocks, Electricity Maps, Global Forest Watch, Liveuamap, ACLED, GDELT,
Kepler.gl, Datawrapper, Radio Garden.

Data APIs: OpenSky, airplanes.live, aisstream.io, USGS quakes, NASA FIRMS/EONET,
USGS Volcano/Water, NWS, Open-Meteo, NOAA SWPC, OpenAQ/WAQI, Cloudflare Radar, RIPE
Atlas, Electricity Maps free tier, GFW data-api, GDELT 2.0, GBIF, Copernicus,
Mobility Database, Wikimedia EventStreams, Raspberry Shake.

Fusion/inspiration: Information is Beautiful Awards (Ship Map), The Pudding (music
borders, population mountains, gastronomic borders), Hatnote Listen to Wikipedia,
in-the-sky twilight map, Electricity Maps, BirdCast, Movebank, TeleGeography cables,
lightpollutionmap, Breathing Earth, NASA Black Marble, timeanddate holidays.

Viz stack: MapLibre GL JS, Mapbox GL JS pricing, Protomaps/PMTiles, deck.gl
(TripsLayer/ArcLayer), Kepler.gl, react-maplibre, CesiumJS, globe.gl, d3-geo,
Observable Plot, Mapbox scroll-fly-to, MapLibre AnimationOptions, mapbox/webgl-wind,
weatherlayers/deck.gl-particle.

Info design: Shneiderman's mantra, Eleken map UI, Metabase maps, Stamen dark-mode
cartography, Okabe-Ito / Viridis / ColorBrewer, Joshua Stevens bivariate, Heer &
Robertson animated transitions, Datawrapper fonts, NN/g empty states, NASA Eyes
(Webby), dashboard anti-patterns (Databox/FusionCharts).

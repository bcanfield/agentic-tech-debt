# Terminator — Data Blueprint (Designer Handoff)

> Technical reference for the designer. States **what each data source provides, its
> shape, cadence, coverage, volume, and constraints** — the facts needed to decide how
> to visualize it. It deliberately makes **no layout or visual-encoding decisions**.
> Concept context lives in `map-dashboard-plan.md`.

## How to read this

For each source: **Type** (raw feed / derived / static), **Geometry** (the spatial
shape of the data), **Coverage**, **Update cadence**, **Volume**, **Value/units**,
**Access** (endpoint + auth + limits + license). "Derived" = we compute it client-side
from inputs, not fetched as-is. Geometry and volume are the facts that most constrain
how a thing can be drawn.

---

## A. Global frame

### Day/night terminator + twilight bands
- **Type:** Derived (in-browser astronomy; no network).
- **Geometry:** A great-circle line (the terminator) plus 3 offset bands — civil
  (−6°), nautical (−12°), astronomical (−18°) twilight. Expressible as polylines or
  filled polygons; recomputable for any timestamp.
- **Coverage:** Global. **Cadence:** Continuous — recompute on a clock tick or on
  time-scrub. **Volume:** Trivial (a few paths). **Value/units:** Solar elevation in
  degrees; position is a function of timestamp + sub-solar point.
- **Access:** Computed from SunCalc-style math. No API, key, limit, or license.

### Golden hour / sub-solar point
- **Type:** Derived. **Geometry:** A moving point (sub-solar) + optional band where sun
  altitude is low. **Coverage:** Global. **Cadence:** Continuous. **Access:** Computed.

---

## B. Dark-side layers (meaningful only where it is night)

### City night-lights (NASA Black Marble)
- **Type:** Static raster (baked into the build).
- **Geometry:** Global raster image / tile pyramid (luminance per pixel).
- **Coverage:** Global. **Cadence:** Static (annual composites; not live).
- **Volume:** Image tiles (large; pre-processed once). **Value/units:** Radiance
  (visual brightness of artificial light).
- **Access:** NASA SVS / Black Marble (VNP46) downloadable rasters. No live API. Public
  NASA data. We host the processed tiles ourselves.

### Light pollution / dark-sky quality
- **Type:** Static raster.
- **Geometry:** Global raster (sky-brightness value per pixel).
- **Coverage:** Global. **Cadence:** Static (atlas, periodic releases).
- **Volume:** Image/raster. **Value/units:** Sky brightness → maps to a discrete
  Bortle-style "can you see stars" scale.
- **Access:** Falchi World Atlas / VIIRS derivatives. **License: CC BY-NC** (non-commercial),
  attribution required. Static download, host ourselves.

### Aurora oval + Kp index (NOAA SWPC)
- **Type:** Raw feed.
- **Geometry:** A global grid of aurora-visibility probability values (lat/lon cells);
  plus a single scalar Kp index. Effectively a heat-field over high latitudes.
- **Coverage:** Global grid, signal concentrated near the poles. **Cadence:** Refreshed
  ~every few minutes. **Volume:** One gridded JSON per refresh (moderate). **Value/units:**
  Aurora probability 0–100% per cell; Kp 0–9.
- **Access:** `services.swpc.noaa.gov/json/ovation_aurora_latest.json` (+ Kp endpoints).
  **No key. Public domain.**

### Nocturnal bird migration (BirdCast) — optional/seasonal
- **Type:** Raw feed (constrained).
- **Geometry:** Regional intensity field (radar-derived) over the contiguous US.
- **Coverage:** **US-only.** **Cadence:** ~every 10 min, **night-only and seasonal**
  (active during migration seasons). **Volume:** Regional raster/field. **Value/units:**
  Birds-in-flight intensity.
- **Access:** BirdCast live maps. **No clean public API** (derived/scraped). Treat as a
  seasonal showcase layer, not a core dependency.

### Bright-satellite / ISS passes — optional
- **Type:** Derived (from public TLE orbital elements).
- **Geometry:** Moving point(s) + ground track lines; pass visibility depends on local
  darkness + sun-glint geometry. **Coverage:** Global. **Cadence:** Continuous (orbit
  propagation client-side). **Volume:** Small (few objects). **Access:** Public TLE sets;
  NASA "Spot the Station" for ISS pass times. No key for TLEs.

---

## C. Light-side layers (meaningful where it is day)

### Weather — temperature / wind (Open-Meteo)
- **Type:** Raw feed (an input to the derived "pleasantness" value).
- **Geometry:** Point query per lat/lon; we sample a grid of points to build a field.
- **Coverage:** Global. **Cadence:** Forecast model updates (hourly-scale); we poll as
  needed. **Volume:** One small JSON per point; field resolution is our choice (cost vs
  smoothness). **Value/units:** °C, m/s, etc.
- **Access:** Open-Meteo. **No key, no signup.** ~10k calls/day, ~600/min. **CC BY 4.0.**

### Air quality (OpenAQ v3 / WAQI)
- **Type:** Raw feed (second input to "pleasantness").
- **Geometry:** **Point** measurements at fixed monitoring stations (irregular,
  station-dependent density). **Coverage:** Global but uneven (dense in some countries,
  sparse elsewhere). **Cadence:** Station-dependent (hourly-scale). **Volume:** Thousands
  of station points. **Value/units:** PM2.5/PM10/NO2/O3 → AQI scale.
- **Access:** **OpenAQ v3** (free key, generous limit) or **WAQI** (free token, ~1000
  req/s). ⚠️ **WAQI license forbids paid apps / resale / caching**; attribution required.
  Fine for a free product.

### "Pleasantness" index
- **Type:** Derived (from weather + air quality + sun altitude).
- **Geometry:** A computed scalar field over sampled points. **Value/units:** A composite
  0–1 (or ranked) score — definition is ours. **Cadence:** Recompute when inputs refresh.

### Clean-energy / grid carbon intensity (Electricity Maps)
- **Type:** Raw feed (constrained).
- **Geometry:** **One scalar value per electricity zone** (country/region polygons), not
  a smooth field. **Coverage:** 200+ zones. **Cadence:** Hourly. **Volume:** One value per
  zone. **Value/units:** gCO₂eq/kWh + power-mix percentages.
- **Access:** **Electricity Maps free tier = 1 zone only, 50 req/hr, non-commercial.** For
  global coverage use the open-source **`electricitymaps-contrib`** dataset, or limit the
  live layer to a few showcase zones.

---

## D. Human-rhythm / heartbeat (global aggregate signals)

### % of humanity awake vs asleep
- **Type:** Derived (static population raster × local time × sleep window).
- **Geometry:** Produces both a single global scalar **and** a per-cell awake/asleep
  field (from the population grid). **Coverage:** Global. **Cadence:** Continuous (changes
  every minute as the terminator moves). **Volume:** Field = population-raster resolution
  (our choice); headline = one number. **Inputs:** A static gridded-population raster
  (e.g., open WorldPop/GPW-style) hosted by us; no live feed.

### Live edit firehose (Wikimedia EventStreams)
- **Type:** Raw streaming feed.
- **Geometry:** **No reliable coordinates** — ⚠️ geolocation broke Nov 2025. Each event
  carries a **wiki/project + language**, so it's mappable only to language regions or
  shown as a non-spatial pulse/rate. **Coverage:** Global (by language). **Cadence:**
  Real-time SSE, many events/sec. **Volume:** High-rate event stream (we sample/aggregate).
  **Value/units:** Edits per second; per-event metadata (title, user type, bytes changed).
- **Access:** `stream.wikimedia.org/v2/stream/recentchange` (Server-Sent Events). **No key.**

### Births / deaths this minute
- **Type:** Derived (public UN annual rates → per-second event rate).
- **Geometry:** Headline counters; optionally spawn points using a population raster for
  distribution. **Coverage:** Global. **Cadence:** Continuous. **Volume:** Two running
  counters + optional spawned dots. **Value/units:** Cumulative count / rate.

### "Midnight wave" / new-day line — optional
- **Type:** Derived. **Geometry:** A moving meridian (where local time crosses 00:00),
  i.e. a line sweeping with the clock. **Coverage:** Global. **Cadence:** Continuous.

---

## E. Optional garnishes (not core)

| Source | Type | Geometry | Coverage | Cadence | Access / constraints |
|---|---|---|---|---|---|
| **NASA EONET** natural events | Raw feed | Points (storms, volcanoes, icebergs) | Global | Daily-scale | GeoJSON, no key |
| **NASA FIRMS** active fires | Raw feed | Points (thermal hotspots) | Global | NRT (~3h global) | Free `MAP_KEY`, 5k/10min |
| **USGS earthquakes** | Raw feed | Points (mag, depth) | Global | Real-time | GeoJSON, no key, public domain |
| **Cloudflare Radar** internet activity | Raw feed | Per-country scalars | Global | Frequent | Token; **CC BY-NC** (non-commercial) |

---

## F. Characteristics summary (drives viz choices)

| Source | Raw/Derived/Static | Geometry | Live? | Coverage | Key? |
|---|---|---|---|---|---|
| Terminator + twilight | Derived | Lines/polygons | Live (computed) | Global | No |
| Night-lights | Static | Raster | No | Global | No (self-host) |
| Light pollution | Static | Raster | No | Global | No (self-host, CC BY-NC) |
| Aurora oval + Kp | Raw | Grid field + scalar | Yes (~min) | Global/poles | No |
| Bird migration | Raw | Regional field | Yes (night/seasonal) | US only | No clean API |
| ISS / satellites | Derived | Moving points + tracks | Live (computed) | Global | No |
| Weather | Raw | Sampled point field | Yes (hourly) | Global | No |
| Air quality | Raw | Station points (irregular) | Yes (hourly) | Global, uneven | Free key |
| Pleasantness | Derived | Scalar field | Live (recompute) | Global | n/a |
| Clean energy | Raw | Per-zone scalar (polygons) | Yes (hourly) | 200+ zones | 1-zone free cap |
| % awake | Derived | Scalar + raster field | Live (per-min) | Global | No |
| Edit firehose | Raw stream | Non-spatial / by language | Yes (real-time) | Global | No |
| Births/deaths | Derived | Counters (+ optional dots) | Live | Global | No |

## G. Constraints the designer should know up front

- **No-backend MVP is possible.** Terminator, night-lights, light pollution, %-awake,
  births/deaths, aurora, weather, and the edit stream need **no key and no server**
  (keyed feeds — OpenAQ/FIRMS — would sit behind a light proxy).
- **Static vs live split:** night-lights and light pollution are baked rasters (they
  don't change minute-to-minute); everything else listed "live" updates on its own clock
  and supports time-scrubbing where the value is time-dependent.
- **Coverage is uneven** for air quality (station density) and bird migration (US-only) —
  plan empty/sparse regions, not just full-globe density.
- **Geometry varies a lot:** lines (terminator), rasters (lights, pollution, aurora,
  pleasantness), irregular points (air-quality stations), per-zone polygons (clean
  energy), and non-spatial rates (edits, births/deaths). Each implies different treatment.
- **Two degraded feeds:** Wikipedia edit geolocation (map by language, not IP) and
  Electricity Maps live API (1-zone cap — use the open dataset for global).
- **License notes for anything shipped publicly:** Open-Meteo CC BY 4.0, light-pollution
  atlas CC BY-NC, WAQI no-resale, Cloudflare Radar CC BY-NC, NASA/USGS public domain.

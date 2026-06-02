# debt-ops concept animation

README "Why it exists" lifecycle animation (the VHS GIF is the hero). Built with
[Motion Canvas](https://motioncanvas.io/) (MIT, TypeScript).
Design and rationale: [`DESIGN.md`](./DESIGN.md).

Shipped:

- `debt-ops-concept.gif`: 960×540, ~12.8s, ~1.1 MB
- `poster.png`: static fallback

## Regenerate

```bash
npm install
npm start          # editor at http://localhost:9000
# click the blue RENDER button
npm run encode     # two-pass ffmpeg → GIF + poster
```

Frames render at 1280×720 / 25 fps. The encode pass downscales to 960 wide via
`palettegen stats_mode=diff` → `paletteuse sierra2_4a + diff_mode=rectangle`, so
a static background costs almost nothing.

## Iterate

Edit `src/scenes/main.tsx`. Vite hot-reloads, the editor preview scrubs in
real time. Eases and durations live in `src/theme.ts`. Indentation in the code
panel is a per-line column shift, not leading whitespace; see
[`DESIGN.md §10`](./DESIGN.md#10-determinism--build-pipeline) for the Motion
Canvas gotchas.

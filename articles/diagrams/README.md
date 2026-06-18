# Article diagrams

Each article ships **exactly one** custom diagram, rendered from text. The source
is a self-contained HTML file here (CSS grid/flex, no external assets); a browser
renders it (that's the validation — a broken layout is visible), and we screenshot
one element to a PNG committed next to the article, mirroring the cover image.

Naming is 1:1 with the article slug:

- source: `articles/diagrams/<slug>.html`
- output: `articles/<slug>.diagram.png` (cover is `<slug>.cover.jpg`)

## Regenerate a diagram

The browser can't open `file://`, so serve the dir first:

```bash
cd articles/diagrams
python3 -m http.server 8731
```

Then, via the Playwright MCP:

1. `browser_navigate` → `http://localhost:8731/<slug>.html?scale=2`
   (`?scale=2` renders at 2× for retina-sharp PNGs; omit for 1×)
2. `browser_take_screenshot` with `target: "#card"`, saving to
   `articles/<slug>.diagram.png`
3. `Read` the PNG back to confirm the layout rendered.

## Current diagrams

- `invisible-debt-is-the-problem.html` → `articles/invisible-debt-is-the-problem.diagram.png`
  — Fowler's deliberate/inadvertent × prudent/reckless debt quadrant.

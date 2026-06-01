import {defineConfig} from 'vite';
import motionCanvasImport from '@motion-canvas/vite-plugin';

// CJS interop: the plugin factory lands on .default under Vite 5's esbuild.
const motionCanvas =
  (motionCanvasImport as unknown as {default?: typeof motionCanvasImport})
    .default ?? motionCanvasImport;

// Motion Canvas editor + bundler. Dev server hosts the scrubbable editor;
// the image-sequence exporter writes PNG frames to ./output on RENDER.
export default defineConfig({
  plugins: [motionCanvas()],
});

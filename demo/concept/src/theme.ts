/**
 * Locked design tokens for the debt-ops concept animation.
 * Every value traces to DESIGN.md — colors (Catppuccin Mocha + Claude orange),
 * type, and the exact Material easing curves. Don't introduce ad-hoc values.
 */

// ── Color (Catppuccin Mocha + brand). Red is deliberately absent. ──
export const BG = '#181825'; // Mantle — canvas
export const SURFACE = '#1e1e2e'; // Base — panels
export const SURFACE0 = '#313244'; // cards
export const SURFACE1 = '#45475a'; // hairline borders
export const TEXT = '#cdd6f4';
export const SUBTEXT1 = '#bac2de';
export const SUBTEXT0 = '#a6adc8';
export const OVERLAY0 = '#6c7086'; // code comments (intentionally dim)
export const MAUVE = '#cba6f7'; // keywords / drop action
export const GREEN = '#a6e3a1'; // strings / "logged ✓"
export const BLUE = '#89b4fa'; // functions / slug (matches real CLI)
export const PEACH = '#fab387'; // deferral highlight + flying chip ("noticed")
export const ORANGE = '#d97757'; // brand accent — wordmark + registry mark

// ── Type ──
export const SANS = 'Inter';
export const MONO = 'JetBrains Mono';

// ── Easing: exact Material cubic-beziers via a Newton/​bisection solver. ──
// Returns a TimingFunction (progress 0..1 → eased 0..1).
export function cubicBezier(x1: number, y1: number, x2: number, y2: number) {
  const cx = 3 * x1;
  const bx = 3 * (x2 - x1) - cx;
  const ax = 1 - cx - bx;
  const cy = 3 * y1;
  const by = 3 * (y2 - y1) - cy;
  const ay = 1 - cy - by;
  const sampleX = (t: number) => ((ax * t + bx) * t + cx) * t;
  const sampleY = (t: number) => ((ay * t + by) * t + cy) * t;
  const sampleDX = (t: number) => (3 * ax * t + 2 * bx) * t + cx;
  const solveX = (x: number) => {
    let t = x;
    for (let i = 0; i < 8; i++) {
      const err = sampleX(t) - x;
      if (Math.abs(err) < 1e-6) return t;
      const d = sampleDX(t);
      if (Math.abs(d) < 1e-6) break;
      t -= err / d;
    }
    let lo = 0;
    let hi = 1;
    let tt = x;
    for (let i = 0; i < 24; i++) {
      const err = sampleX(tt) - x;
      if (Math.abs(err) < 1e-6) break;
      if (err > 0) hi = tt;
      else lo = tt;
      tt = (lo + hi) / 2;
    }
    return tt;
  };
  return (t: number) => sampleY(solveX(t));
}

export const STANDARD = cubicBezier(0.4, 0, 0.2, 1); // begins+ends on screen
export const ENTER = cubicBezier(0, 0, 0.2, 1); // decelerate — arriving
export const EXIT = cubicBezier(0.4, 0, 1, 1); // accelerate — leaving
export const EMPHASIZED = cubicBezier(0.05, 0.7, 0.1, 1); // hero catch

// ── Durations (seconds @ 25fps). From DESIGN.md §6. ──
export const D = {
  underline: 0.2,
  pulse: 0.4,
  anticipate: 0.12,
  arc: 0.7,
  snap: 0.3,
  check: 0.15,
  tick: 0.2,
  capIn: 0.25,
  capOut: 0.2,
  fastArc: 0.45,
  dropOut: 0.3,
  wordmark: 0.5,
  tagline: 0.3,
};

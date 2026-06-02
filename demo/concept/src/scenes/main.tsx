import {makeScene2D, Rect, Txt, Node} from '@motion-canvas/2d';
import {
  createRef,
  createRefArray,
  all,
  waitFor,
  chain,
  Vector2,
} from '@motion-canvas/core';
import * as T from '../theme';

// ── Geometry. Origin = view center (1280×720). Panel CHILDREN use LOCAL
// coordinates (relative to the panel's center). Text is left/right-anchored
// with `offset`; indentation is a column shift on the line, not whitespace. ──
const CODE = 20;
const CH = 12; // JetBrains Mono advance width at 20px (0.6em)
const LH = 30;

const codePanel = {x: -260, y: -10, w: 620, h: 320};
const regPanel = {x: 350, y: -10, w: 440, h: 320};

// MC collapses boundary whitespace between inline spans. NBSP keeps spacing.
const nb = (s: string) => s.replace(/ /g, String.fromCharCode(160));

const codeInnerW = codePanel.w - 68;
const codeLeft = -codeInnerW / 2;
const codeTop = -codePanel.h / 2 + 30;
const lineYL = (i: number) => codeTop + 44 + i * LH;
const charX = (k: number) => codeLeft + k * CH;
const regLeft = -regPanel.w / 2 + 34;
const regRight = regPanel.w / 2 - 34;

const cardA = {x: regPanel.x, y: -52, w: 400, h: 74};
const cardB = {x: regPanel.x, y: 38, w: 400, h: 74};

const codeLines: {indent: number; tokens: [string, string][]}[] = [
  {indent: 0, tokens: [['function ', T.MAUVE], ['checkout', T.BLUE], ['(session) {', T.TEXT]]},
  {indent: 2, tokens: [['const ', T.MAUVE], ['payload ', T.TEXT], ['= ', T.TEXT], ['buildCart', T.BLUE], ['(session)', T.TEXT]]},
  {indent: 2, tokens: [['payload.total ', T.TEXT], ['= ', T.TEXT], ['price', T.BLUE], ['(payload.items)', T.TEXT]]},
  {indent: 2, tokens: [['// TODO: tidy log format', T.OVERLAY0]]},
  {indent: 2, tokens: [['if ', T.MAUVE], ['(session.user) {', T.TEXT]]},
  {indent: 4, tokens: [['payload.email ', T.TEXT], ['= ', T.TEXT], ['session.email', T.TEXT]]},
];
const DEF_INDENT = 4;
const DEF_KEEP = 'payload.userId = session.user ';
const DEF_CAST = 'as any';

export default makeScene2D(function* (view) {
  const code = createRef<Rect>();
  const reg = createRef<Rect>();
  const lines = createRefArray<Txt>();
  const defLine = createRef<Txt>();
  const defCast = createRef<Txt>();
  const underline = createRef<Rect>();
  const pulse = createRef<Rect>();
  const chip = createRef<Rect>();
  const chipTxt = createRef<Txt>();
  const cardARef = createRef<Rect>();
  const cardBRef = createRef<Rect>();
  const checkA = createRef<Txt>();
  const strikeA = createRef<Rect>();
  const count = createRef<Txt>();
  const brand = createRef<Node>();

  view.add(
    <>
      <Rect width={460} height={460} x={regPanel.x} y={regPanel.y} radius={230} fill={T.ORANGE} opacity={0.04} />

      {/* code surface */}
      <Rect
        ref={code}
        x={codePanel.x}
        y={codePanel.y}
        width={codePanel.w}
        height={codePanel.h}
        radius={16}
        fill={T.SURFACE}
        stroke={T.SURFACE1}
        lineWidth={1}
        shadowColor={'#00000055'}
        shadowBlur={40}
        shadowOffsetY={12}
        opacity={0}
      >
        <Txt text={'api/checkout.ts'} fontFamily={T.SANS} fontSize={16} fontWeight={500} fill={T.SUBTEXT0} offset={[-1, 0]} x={codeLeft} y={codeTop} />
        {codeLines.map((line, i) => (
          <Txt ref={lines} fontFamily={T.MONO} fontSize={CODE} textWrap={false} offset={[-1, 0]} x={charX(line.indent)} y={lineYL(i)} opacity={0}>
            {line.tokens.map(([t, c]) => (
              <Txt text={nb(t)} fill={c} />
            ))}
          </Txt>
        ))}
        <Txt ref={defLine} fontFamily={T.MONO} fontSize={CODE} textWrap={false} offset={[-1, 0]} x={charX(DEF_INDENT)} y={lineYL(6)} opacity={0}>
          <Txt text={nb(DEF_KEEP)} fill={T.TEXT} />
          <Txt ref={defCast} text={nb(DEF_CAST)} fill={T.MAUVE} />
        </Txt>
        {/* highlight just the `as any` cast — col 34 is where it starts (after the 30-char prefix) */}
        <Rect ref={pulse} x={charX(37)} y={lineYL(6)} width={6 * CH} height={26} radius={6} fill={T.PEACH} opacity={0} />
        <Rect ref={underline} offset={[-1, 0]} x={charX(34)} y={lineYL(6) + 15} width={0} height={3} radius={2} fill={T.PEACH} />
      </Rect>

      {/* debt registry */}
      <Rect
        ref={reg}
        x={regPanel.x}
        y={regPanel.y}
        width={regPanel.w}
        height={regPanel.h}
        radius={16}
        fill={T.SURFACE}
        stroke={T.SURFACE1}
        lineWidth={1}
        shadowColor={'#00000055'}
        shadowBlur={40}
        shadowOffsetY={12}
        opacity={0}
      >
        <Txt text={'registry'} fontFamily={T.SANS} fontSize={22} fontWeight={600} fill={T.SUBTEXT0} offset={[-1, 0]} x={regLeft} y={codeTop} />
        <Txt ref={count} text={'0'} fontFamily={T.SANS} fontSize={22} fontWeight={800} fill={T.ORANGE} offset={[1, 0]} x={regRight} y={codeTop} />
      </Rect>

      {card(cardARef, checkA, strikeA, cardA, 'as-any-checkout-payload', 'A', 'loosened type · checkout')}
      {card(cardBRef, createRef<Txt>(), createRef<Rect>(), cardB, 'log-format-nit', 'B', 'code quality')}

      {/* flying chip */}
      <Rect ref={chip} radius={8} fill={T.SURFACE0} stroke={T.PEACH} lineWidth={1.5} padding={[6, 12]} layout opacity={0}>
        <Txt ref={chipTxt} text={DEF_CAST} fontFamily={T.MONO} fontSize={16} fill={T.PEACH} />
      </Rect>

      {/* brand resolve */}
      <Node ref={brand} opacity={0}>
        <Txt fontFamily={T.SANS} fontSize={84} fontWeight={800} y={-28}>
          <Txt text={'debt'} fill={T.TEXT} />
          <Txt text={'-ops'} fill={T.ORANGE} />
        </Txt>
        <Txt text={'Catches AI-introduced tech debt at write-time.'} fontFamily={T.SANS} fontSize={28} fontWeight={500} fill={T.SUBTEXT1} y={40} />
      </Node>
    </>,
  );

  cardARef().opacity(0).scale(0.9);
  cardBRef().opacity(0).scale(0.9);
  checkA().opacity(0);

  const inCode = (lx: number, ly: number) => new Vector2(codePanel.x + lx, codePanel.y + ly);

  // ════════ Beat 0 · Setup ════════
  yield* all(code().opacity(1, 0.5, T.ENTER), reg().opacity(1, 0.5, T.ENTER));
  for (let i = 0; i < lines.length; i++) {
    yield* lines[i].opacity(1, 0.09, T.STANDARD);
  }
  yield* defLine().opacity(1, 0.12, T.STANDARD);
  yield* waitFor(0.35);

  // ════════ Beat 1 · Shortcut born ════════
  yield* underline().width(6 * CH, T.D.underline, T.STANDARD);
  yield* waitFor(0.45); // brief beat; no caption, no need for long reading time

  // ════════ Beat 2 · The catch (hero) ════════
  yield* chain(pulse().opacity(0.18, T.D.pulse / 2, T.STANDARD), pulse().opacity(0, T.D.pulse / 2, T.STANDARD));
  yield* all(defLine().y(lineYL(6) - 4, T.D.anticipate, T.STANDARD), defLine().scale(1.05, T.D.anticipate, T.STANDARD));
  const chipStart = inCode(charX(37), lineYL(6));
  const slotA = new Vector2(cardA.x, cardA.y);
  const apexA = new Vector2((chipStart.x + slotA.x) / 2, Math.min(chipStart.y, slotA.y) - 120);
  chip().position(chipStart);
  yield* all(
    chip().opacity(1, 0.1, T.ENTER),
    defCast().opacity(0, 0.1, T.STANDARD),
    underline().opacity(0, 0.15, T.STANDARD),
    code().opacity(0.7, 0.2, T.STANDARD),
    defLine().y(lineYL(6), T.D.anticipate, T.STANDARD),
    defLine().scale(1, T.D.anticipate, T.STANDARD),
  );
  yield* chain(chip().position(apexA, T.D.arc / 2, T.EXIT), chip().position(slotA, T.D.arc / 2, T.ENTER));
  yield* all(
    chip().opacity(0, T.D.snap, T.EMPHASIZED),
    cardARef().opacity(1, T.D.snap, T.EMPHASIZED),
    cardARef().scale(1, T.D.snap, T.EMPHASIZED),
  );
  yield* waitFor(0.18); // card lands before the ✓ and count tick
  yield* all(checkA().opacity(1, T.D.check, T.ENTER), bumpCount(count, '1'));
  yield* waitFor(1.2); // hero hold — read the filed entry

  // ════════ Beat 3 · Continuous ════════
  // Now we're flying the *actual* `// TODO: tidy log format` comment off line 3.
  const chipStartB = inCode(charX(14), lineYL(3));
  chip().opacity(0).position(chipStartB);
  chipTxt().text('// TODO: tidy log format');
  const slotB = new Vector2(cardB.x, cardB.y);
  const apexB = new Vector2((chipStartB.x + slotB.x) / 2, -180);
  // Fade the line-3 comment as the chip "becomes" it.
  yield* all(
    chip().opacity(1, 0.08, T.ENTER),
    lines[3].opacity(0, 0.15, T.STANDARD),
  );
  yield* chain(chip().position(apexB, T.D.fastArc / 2, T.EXIT), chip().position(slotB, T.D.fastArc / 2, T.ENTER));
  yield* all(
    chip().opacity(0, T.D.snap, T.EMPHASIZED),
    cardBRef().opacity(1, T.D.snap, T.EMPHASIZED),
    cardBRef().scale(1, T.D.snap, T.EMPHASIZED),
    bumpCount(count, '2'),
  );
  yield* waitFor(0.85); // register the second card before the prune

  // ════════ Beat 4 · Drop the nit, complete the real one (all visual) ════════
  // First: card B (the nit) drops off the registry.
  yield* all(
    cardBRef().opacity(0, T.D.dropOut, T.EXIT),
    cardBRef().scale(0.85, T.D.dropOut, T.EXIT),
    cardBRef().x(cardB.x + 80, T.D.dropOut, T.EXIT),
    bumpCount(count, '1'),
  );
  yield* waitFor(0.28); // one card remains — the real one
  // Then: card A is paid down. Border + ✓ stamp + strikethrough + recede.
  const slugWidth = ('+1 entry: ' + 'as-any-checkout-payload' + ' (A)').length * 9.6;
  yield* all(
    cardARef().stroke(T.GREEN, 0.22, T.ENTER),
    cardARef().lineWidth(2.5, 0.22, T.ENTER),
    checkA().scale(1.6, 0.22, T.EMPHASIZED),
  );
  yield* all(
    strikeA().width(slugWidth, 0.28, T.STANDARD),
    checkA().scale(1.1, 0.18, T.EMPHASIZED),
  );
  yield* waitFor(0.18);
  yield* all(
    cardARef().opacity(0.35, 0.4, T.EXIT),
    cardARef().scale(0.93, 0.4, T.EXIT),
    cardARef().lineWidth(1, 0.4, T.EXIT),
    bumpCount(count, '0'),
  );
  yield* waitFor(0.7); // registry empty — managed

  // ════════ Beat 5 · Resolve / brand ════════
  yield* all(
    code().opacity(0, 0.5, T.EXIT),
    reg().opacity(0, 0.5, T.EXIT),
    cardARef().opacity(0, 0.5, T.EXIT),
  );
  yield* brand().opacity(1, T.D.wordmark, T.ENTER);
  yield* waitFor(1.9); // tagline reading
  yield* brand().opacity(0, 0.3, T.EXIT);
});

// A registry card (children use LOCAL coords; hidden until catch).
function card(
  ref: ReturnType<typeof createRef<Rect>>,
  check: ReturnType<typeof createRef<Txt>>,
  strike: ReturnType<typeof createRef<Rect>>,
  geo: {x: number; y: number; w: number; h: number},
  slug: string,
  letter: string,
  tag: string,
) {
  const left = -geo.w / 2 + 22;
  const right = geo.w / 2 - 22;
  return (
    <Rect ref={ref} x={geo.x} y={geo.y} width={geo.w} height={geo.h} radius={12} fill={T.SURFACE0} stroke={T.SURFACE1} lineWidth={1}>
      <Txt fontFamily={T.MONO} fontSize={16} textWrap={false} offset={[-1, 0]} x={left} y={-13}>
        <Txt text={nb('+1 entry: ')} fill={T.SUBTEXT0} />
        <Txt text={slug} fill={T.BLUE} />
        <Txt text={nb(` (${letter})`)} fill={T.OVERLAY0} />
      </Txt>
      <Txt text={tag} fontFamily={T.SANS} fontSize={14} fontWeight={500} fill={T.SUBTEXT0} offset={[-1, 0]} x={left} y={15} />
      <Txt ref={check} text={'✓'} fontFamily={T.SANS} fontSize={24} fill={T.GREEN} offset={[1, 0]} x={right} y={0} />
      <Rect ref={strike} offset={[-1, 0]} x={left} y={-13} width={0} height={2.5} radius={1.5} fill={T.GREEN} />
    </Rect>
  );
}

// Update the registry count with a small pop (secondary action).
function* bumpCount(ref: ReturnType<typeof createRef<Txt>>, value: string) {
  yield* ref().scale(1.3, T.D.tick / 2, T.STANDARD);
  ref().text(value);
  yield* ref().scale(1, T.D.tick / 2, T.STANDARD);
}

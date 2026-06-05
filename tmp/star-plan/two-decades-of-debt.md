# Two decades of tech-debt research, in a one-minute read

People have been studying messy code since the early 90s. Drop the academic
wording and it comes down to four things a normal person can act on today.

**Write it down.** Debt you can't see is debt you won't fix. When you cut a
corner, leave a note where you cut it. One running list, not a separate doc
nobody opens.

**Say why.** A single line explaining the trade-off saves the next person from
re-arguing it in six months. Usually that next person is you.

**Clean where the work is.** A small fraction of your files cause most of the
headaches. Fix those. The quiet corners can stay messy; nobody's touching them
anyway.

**A little, all the time.** Small steady cleanup beats the big rewrite. The big
rewrites tend to blow up.

That's the whole thing. None of it is hard. It just rarely happens, because the
moment to act and the moment you feel the pain are nowhere near each other. The
shortcut is fresh the day you cut it. The cost lands months later, debugging at
2am.

AI widened that gap. It writes code faster than anyone can read it, so the
corners get cut off-screen. One study of 211 million lines found refactoring fell
by more than half once AI tools took over, while copy-pasted code kept rising.

So the fix isn't a new framework. It's catching the debt the second it's
written, while you still remember why.

---

## Where this comes from

- The metaphor: Ward Cunningham, 1992. Rough code is a loan you pay interest on
  until you fix it.
- The four kinds of debt: Martin Fowler's quadrant. The "accidental and
  careless" corner is the one that bites.
- A shared definition: the Dagstuhl seminar, 2016.
- Writing down the "why": Architecture Decision Records, Michael Nygard, 2011.
- Clean the hotspots: behavioral code analysis (Adam Tornhill / CodeScene) and
  Google's debt study (Jaspan & Green, 2023). Roughly 20% of files drive 80% of
  the rework.
- A little, all the time: Shopify's 25% rule, Microsoft's bug cap, SAFe and
  Scrum.org. Windows XP SP2 is the rewrite that went sideways.
- Measuring it: DORA metrics, now including rework rate (2024).
- The AI gap: GitClear's study of 211M lines, 2020–2024.

Full sources and caveats: `docs/tech-debt-management.md`.

# Release Order: One Article Per Day

Daily publishing sequence for the 73 mainline articles in [ai-tech-debt-headlines.md](./ai-tech-debt-headlines.md)
(numbers reference that doc). **Launch: Monday, June 8, 2026 → Day 72: Tuesday, August 18, 2026.**
72 scheduled days + 1 bench article. Persona variants (#74–82) are not queue days — they ship as same-week
distribution wrappers (LinkedIn/newsletter/community posts) for the mainline piece they door into.

v2 — revised after adversarial review (see revision notes at bottom).

## Ordering criteria (priority order)

1. **Credibility before virality** — day 1 must survive a hostile HN thread. Open with undisputed material
   (Replit has named principals, screenshots, CEO confirmation); contested stats (METR) run mid-calendar with
   caveats load-bearing.
2. **Cornerstones + first playbook in days 1–5** — SEO compounds with time-live, and week-1 readers arrive
   from the repo README: the highest-intent visitors the blog will ever get. Don't make them wait for the CTA.
3. **News-peg decay, date-enforced** — curl (fresh June 2026 datapoint), LF initiative, and Microsoft
   (June 30 deadline) are pegged to real dates below.
4. **Variety** — no consecutive days on the same pillar or anchor, except marked `⟂ pair` (data piece → its
   essay or how-to).
5. **Pre-empt the rebuttal** — for disputed stories (Amazon), the dispute-defusing frame publishes *first*,
   not last. Every Amazon piece carries "estimated" + attribution inline.
6. **Series on fixed slots** — Amazon runs Mondays (days 8–36) so the arc is followable.
7. **Gates over plans** — order is firm two weeks out; gates below re-cut the rest.
8. **Bench** — #21 (Replit timeline) for breaking-news swap-ins; if it runs, it *replaces* #20 on day 44
   (headlines doc says pick 2 of 3 Replit angles, never all three).
9. **Capacity (accepted risk)** — daily cadence was chosen knowingly. Mitigation: pre-write a 2-week buffer
   before June 8, batch back-half evergreens early, and treat Gate C as the cut-to-3/week escape hatch if
   quality slips.

## Decision gates

- **Gate A — Day 14 (Jun 21).** Hook-style A/B runs on *distribution channel titles* (stat-led vs incident-led
  framings of the same pieces across HN/LinkedIn/newsletter, weeks 1–2), where sample size actually exists —
  not on publish order. Winner re-weights slot emphasis from day 22 onward (firm-two-weeks rule holds).
- **Gate B — Day 38 (Jul 15).** Persona-door CTR: by now every persona door has shipped (CTO via #54 d16 and
  #26 d36, staff-IC via #13 d31, security/DevEx/OSS/indie in weeks 1–3). Pick the two personas that get
  dedicated distribution emphasis and decide whether to commission more for that segment.
- **Gate C — ~Day 45 (Jul 22).** In-window signals only: vendor security pass-rate updates (Veracode-class)
  and our own engagement split between "AI breaks production" pieces and "AI debt is invisible/compounding"
  pieces. If security framings decay, shift remaining emphasis to comprehension/maintainability. Also the
  quality checkpoint: if the daily cadence is producing thin posts, cut to 3/week here and push the rest to
  backlog. (DORA 2026 publishes in the fall — that hedge is a post-calendar note, not a gate.)
- **Standing rule:** any breaking AI-debt incident bumps the day's slot; bumped article shifts right, bench fills gaps.

## The calendar

### Week 1 — Credibility launch (Jun 8–14) · undisputed incident, both cornerstones, CTA by day 3
| Day | Date | # | Article | Why this slot |
|---|---|---|---|---|
| 1 | Mon Jun 8 | 19 | Replit anatomy | Strongest *undisputed* incident — survives HN scrutiny on day 1 |
| 2 | Tue Jun 9 | 3 | Invisible debt is the problem | The on-brand cornerstone, compounding from day 2 |
| 3 | Wed Jun 10 | 56 | The debt-ops playbook | First BOFU — README arrivals are peak-intent readers |
| 4 | Thu Jun 11 | 33 | curl: a slop report every 18 hours | Reframed around the *June 2026* datapoint — freshest peg we have |
| 5 | Fri Jun 12 | 1 | Cheap to write, expensive to own | Cornerstone 2 |
| 6 | Sat Jun 13 | 27 | Tea: a decision nobody wrote down | Incident that lands the registry thesis |
| 7 | Sun Jun 14 | 37 | The 8x duplicate-code spike | Headline date-fixed (2024 data, no "last year") |

### Week 2 — Amazon opens on the front foot (Jun 15–21)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 8 | Mon Jun 15 | 25 | Amazon says it wasn't the AI — scarier | Series ep 1: the dispute-defusing frame leads; pre-empts every rebuttal |
| 9 | Tue Jun 16 | 2 | Verification debt | Cornerstone 3 |
| 10 | Wed Jun 17 | 40 | Veracode 45% | |
| 11 | Thu Jun 18 | 62 | Registry vs TODO vs Jira | BOFU; evergreen SEO comparison query |
| 12 | Fri Jun 19 | 35 | Vendors fund their own cleanup | LF initiative (Mar 18) — moved up before it goes stale |
| 13 | Sat Jun 20 | 46 | Google's own data (DORA) | The non-vendor credibility spine |
| 14 | Sun Jun 21 | 57 | The 20-minute debt audit | BOFU · **Gate A** |

### Week 3 (Jun 22–28)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 15 | Mon Jun 22 | 24 | Kiro deleted the environment | Series ep 2 (dispute already addressed in ep 1) |
| 16 | Tue Jun 23 | 54 | Gartner's 2,500% | CTO door ships early so Gate B can see it |
| 17 | Wed Jun 24 | 43 | 1 in 5 packages doesn't exist | |
| 18 | Thu Jun 25 | 59 | Vibe coding responsibly | BOFU |
| 19 | Fri Jun 26 | 48 | 84% use AI, 29% trust it | |
| 20 | Sat Jun 27 | 29 | Lovable: 170 apps, one inverted check | |
| 21 | Sun Jun 28 | 5 | Review is the new compile step | |

### Week 4 (Jun 29–Jul 5)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 22 | Mon Jun 29 | 23 | Amazon deleted the GenAI bullet point | Series ep 3 |
| 23 | Tue Jun 30 | 36 | Microsoft pulled the Claude licenses | Pegged to the June 30 license deadline — runs *on* it |
| 24 | Wed Jul 1 | 63 | 10 debt patterns to grep for | BOFU |
| 25 | Thu Jul 2 | 41 | 3x code, 10x vulnerabilities | |
| 26 | Fri Jul 3 | 8 | In defense of vibe coding | Contrarian — holiday-weekend discussion bait |
| 27 | Sat Jul 4 | 34 | Ghostty banned AI code | |
| 28 | Sun Jul 5 | 64 | Triage for "almost right" code | BOFU |

### Week 5 (Jul 6–12)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 29 | Mon Jul 6 | 22 | Amazon: 80% mandate, 6.3M orders | Series ep 4 — "estimated," attributed, post-#25 |
| 30 | Tue Jul 7 | 51 | Army of Juniors | |
| 31 | Wed Jul 8 | 13 | Nobody understands the codebase | Staff-IC door, pre-Gate B |
| 32 | Thu Jul 9 | 60 | Make agents confess their shortcuts | BOFU |
| 33 | Fri Jul 10 | 50 | AI PRs: 1.7x issues | |
| 34 | Sat Jul 11 | 31 | The zero-click RCE demo | |
| 35 | Sun Jul 12 | 67 | Fowler's quadrant + churn axis | BOFU — makes the tool's ranking model citable |

### Week 6 (Jul 13–19)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 36 | Mon Jul 13 | 26 | Vogels saw it coming | Series cap — links eps + cornerstone 2 |
| 37 | Tue Jul 14 | 45 | METR: felt 20% faster, was 19% slower | Mid-run with an audience built; caveats load-bearing |
| 38 | Wed Jul 15 | 18 | The felt-faster fallacy | `⟂ pair` w/ d37 — the essay version · **Gate B** |
| 39 | Thu Jul 16 | 39 | Churn is debt | |
| 40 | Fri Jul 17 | 65 | Track churn in your repo | BOFU `⟂ pair` w/ d39 |
| 41 | Sat Jul 18 | 32 | Every app missing the same protection | |
| 42 | Sun Jul 19 | 14 | Automation bias as root cause | |

### Week 7 (Jul 20–26)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 43 | Mon Jul 20 | 52 | Five studies, one conclusion | All five covered (d37, d10, d7, d25, d13) — synthesis lands |
| 44 | Tue Jul 21 | 20 | The AI lied about it | Replit revisit (replaced by bench #21 if that ran) |
| 45 | Wed Jul 22 | 10 | Your cleanup sprint is dead | **Gate C** |
| 46 | Thu Jul 23 | 69 | The 30-minute debt ritual | BOFU `⟂ pair` w/ d45 |
| 47 | Fri Jul 24 | 42 | +322% privilege escalation | |
| 48 | Sat Jul 25 | 44 | CVEs: 6 → 35+ in two months | |
| 49 | Sun Jul 26 | 7 | Registering beats preventing | |

### Week 8 (Jul 27–Aug 2)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 50 | Mon Jul 27 | 53 | The numbers behind verification debt | |
| 51 | Tue Jul 28 | 58 | The workflow that fills the gap | BOFU `⟂ pair` w/ d50 |
| 52 | Wed Jul 29 | 16 | Maintenance as specialist profession | |
| 53 | Thu Jul 30 | 61 | Hooks tutorial (Claude Code) | BOFU — the HN-native builder piece |
| 54 | Fri Jul 31 | 49 | Copilot's hidden tax on seniors | |
| 55 | Sat Aug 1 | 9 | You build it, you own it | |
| 56 | Sun Aug 2 | 73 | The you-build-it checklist | BOFU `⟂ pair` w/ d55 |

### Week 9 (Aug 3–9)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 57 | Mon Aug 3 | 4 | Did anyone decide anything? | |
| 58 | Tue Aug 4 | 38 | Refactoring fell 40% | |
| 59 | Wed Aug 5 | 66 | Baseline your repo's AI debt | BOFU |
| 60 | Thu Aug 6 | 30 | Your app will outlive your understanding | |
| 61 | Fri Aug 7 | 17 | Citizen developers are about to learn | |
| 62 | Sat Aug 8 | 68 | ADRs at agent speed | BOFU |
| 63 | Sun Aug 9 | 47 | Copilot made PRs 41% buggier | |

### Week 10 (Aug 10–18)
| Day | Date | # | Article | Why |
|---|---|---|---|---|
| 64 | Mon Aug 10 | 28 | "The antidote is… more AI" | Keeps an incident piece in the final stretch |
| 65 | Tue Aug 11 | 15 | Debt, not tokens, limits velocity | |
| 66 | Wed Aug 12 | 70 | Your retro is too slow | BOFU |
| 67 | Thu Aug 13 | 12 | We saw this in 2014 | |
| 68 | Fri Aug 14 | 55 | The $1.52T pile | |
| 69 | Sat Aug 15 | 6 | AI removed the throttle | |
| 70 | Sun Aug 16 | 71 | Drop-or-pay policy | BOFU |
| 71 | Mon Aug 17 | 11 | The reckoning is a slow leak | |
| 72 | Tue Aug 18 | 72 | Your team's first AI week | Closes the run on the strongest CTA |

**Bench:** #21 (Replit 12-day timeline) — swaps in for breaking news, and *replaces* #20 (day 44) if used.

## Why this shape

- **BOFU from day 3,** then 1–2/week through week 7, 2–3/week in weeks 8–10 — early high-intent readers get a
  CTA immediately; the back half converts the audience the front half built.
- **Every week carries at least one incident, one data piece, and one playbook** (week 10 included, via #28).
- **All dated pegs land on or before their dates:** curl reframe d4, LF initiative d12, Microsoft on the June 30
  deadline itself (d23), Amazon arc done by mid-July.
- **Back half is evergreen** thesis/methodology — cheapest to re-cut at the gates, safest to pre-write as buffer.

## Revision notes (v2, after adversarial review)

- Opened with Replit, not METR — METR is the most-contested study in the discourse; moved to d37 with the essay
  pair (S1). Cornerstones and first playbook moved to days 1–5 (S2/S6/S7).
- Week-1 publish-order A/B scrapped; hook A/B now runs on channel titles where sample size exists (S2/M3).
- Amazon series now leads with the dispute-defusing #25; "estimated" + attribution mandatory in every ep (S3);
  fixed to Mondays (M8).
- curl and GitClear headlines corrected for factual staleness; LF initiative pulled to week 2; calendar
  date-anchored so the Microsoft peg beats its June 30 deadline (S5).
- Gate B moved to d38, after all persona doors ship (M4). Gate C re-keyed to in-window signals; DORA 2026 is a
  post-calendar hedge (M5). Gate C doubles as the quality/cadence escape hatch (S8 — daily cadence kept
  deliberately, risk accepted with buffer mitigation).
- Phase 10 imports #28 to satisfy the adjacency and incident-mix rules (M2/M7); bench rule fixed so all three
  Replit angles never run (M9); BOFU-ramp claim corrected to match the table (M6).

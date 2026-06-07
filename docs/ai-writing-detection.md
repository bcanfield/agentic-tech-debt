# What makes prose "feel AI" after the surface tells are gone

Research base for the `ai-smell-review` skill. Deep-research run, June 2026: 22 sources
fetched, 110 claims extracted, 25 adversarially verified (3-vote), 2 refuted. Findings
ranked by evidence strength. Companion to the structural catalog in the humanize skill —
this doc covers the *non*-structural residue.

## Findings (ranked)

### 1. Expert humans are a near-ceiling detector — emulate them, not the detectors
A 5-person majority vote of people who frequently use LLMs misclassified **1 of 300**
non-fiction articles (~99.7%), and stayed at **100% TPR on deliberately humanized text**
where Binoculars collapsed to 6.7% and Fast-DetectGPT to 23.3%. Only Pangram (~99.3%)
kept pace. ([arXiv 2501.15654](https://arxiv.org/abs/2501.15654), ACL 2025.)
Refuted 0–3 in verification: "humans are worse than automatic discriminators."
Consequence: the reviewer should emulate the expert-annotator protocol, and a low
detector score on edited text is **not** evidence the prose passes human readers.

### 2. Their cues are enumerable — and the mix shifts once surface tells are scrubbed
Expert explanations: AI vocabulary 53.1%, sentence structure 35.9%, grammar/punctuation
24.8%, originality 23.7%. On *humanized* text, vocabulary mentions drop (57.1% → 42.3%)
and **quote/specificity cues rise to 33.8%** — for a pipeline that already runs a
surface audit (ours), specificity is the dominant residual cue. (Same ACL 2025 paper.)

### 3. The instruction-tuning grammatical fingerprint — most edit-actionable signal
GPT-4o-class instruct models write a register-invariant, noun-heavy house style
(Reinhart et al., [PNAS 2025](https://www.pnas.org/doi/10.1073/pnas.2422455122);
Biber-feature classifiers hit 93–98%):

| Feature | vs human rate | Edit direction |
|---|---|---|
| Present participial clauses ("..., making it...") | **5.3x** (d=1.38) | convert to finite clauses |
| Nominalizations ("the implementation of") | **2.1x** (d=1.23) | de-nominalize to verbs |
| That-clauses as subject | 2.6x | recast |
| Phrasal coordination ("X and Y" pairs) | 1.9x | break pairs |
| Agentless passives | **~0.5x** | humans use *more*; reintroduce where natural |

Base (non-instruct) Llama 3 is only ~75% separable from humans — the "AI accent" is an
RLHF artifact, not inherent to LLMs. Caveat: numbers are GPT-4o/Llama-3-era, in-domain.

### 4. Burstiness done right: surprisal *rhythm*, not level
The discriminative signal is how unpredictability fluctuates across sentences —
second-order dynamics carry 39.4% of feature importance (DivEye,
[arXiv 2509.18880](https://arxiv.org/abs/2509.18880), TMLR). Human text is spiky:
runs of plain sentences punctuated by dense, surprising ones. Editing proxy: hunt runs
of uniformly "expected" sentences; inject spiky specificity (numbers, version strings,
named incidents). Caveat: edit-time actionability is inferred, not demonstrated; the
rhythm features false-positive on formulaic human prose and non-native writers.

### 5. Stance and pragmatic flatness (medium confidence)
Default-neutral affect, less negative emotion, fewer expressive punctuation marks,
within-paragraph term repetition, overused attitude markers, **underused hedges and
self-mention**, "optimistically vague conclusions." Five-cue-family taxonomy (surface,
discourse/pragmatic, epistemic/content, predictability, provenance) puts
discourse/pragmatic second only to surface in differentiating power.
([BDCC rapid review, 2026](https://www.preprints.org/manuscript/202601.0350);
emotion findings are ChatGPT-3.5-era — treat direction, not magnitude.)

### 6. Detector asymmetry dictates the workflow
Perplexity-family detectors are "powerful yet fragile": a repetition penalty drops
accuracy up to 38 points (RAID, ACL 2024); paraphrase collapses Binoculars to 6.7% TPR.
Trained classifiers (Pangram-class) and expert humans are robust to the same evasions.
Consequence: Pangram-class **fail = block; pass = no signal**. Never treat a
GPTZero/Binoculars pass as meaning anything about human perception.

## The reviewer design these findings support

Inputs: the draft + 2–3 **venue-matched human exemplars** (HN front page / high-engagement
dev.to, topic-adjacent). Judge: a **fresh context, never the writer's** — we observed the
self-audit blindness directly (writer self-reported "one kicker"; an independent grader
counted four). Protocol: (1) blind pairwise reading against exemplars, demanding *located*
evidence; (2) cue-family rubric sweep in the scrubbed-pipeline priority order —
specificity gradient, grammatical fingerprint, surprisal rhythm, stance/pragmatics,
originality, ending check; (3) output a ranked edit list (exact span + cue family + why +
concrete rewrite), not a verdict. Implemented in `.claude/skills/ai-smell-review/`.

## Honest gaps
- No surviving study directly tested LLM-as-judge for AI-smell detection, or whether a
  different-family judge beats same-family self-audit — the design extrapolates the
  human-expert protocol. Treat the fresh-context-judge rule as engineering prudence.
- Fingerprint effect sizes are early-2025 models; 2026 frontier magnitudes may differ.
- The expert-ceiling result is 5 paid annotators, one genre.
- No study shows which cue families are *causal* for the "feels AI" percept.

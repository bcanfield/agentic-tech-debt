---
id: 20260626124215
title: articles-fail-visual-density-gate
principal: 1w
interest: gate blocks re-publish of each article until fixed
hotspot: articles/
business_capability: content-pipeline
payoff_trigger: before re-publishing/cross-posting any existing article, or if image-dense pieces start reading as AI-decorated
quadrant: prudent-deliberate
category: documentation
ai_authored: true
created: 2026-06-26
---

ADR 0022 raised the write-article visual contract: meme_check.py now requires >=3 committed body images (one a diagram) and no run of more than 2 prose paragraphs without a visual. The seven existing articles in articles/ were built under the old 2-anchor contract and now fail the gate — most have 2 images or fewer and several 3-paragraph runs (the running-tech-debt playbook has no diagram at all). Retrofit deferred: add a third anchor and break the long runs per article. Also carries ADR 0022's accepted risk that denser visuals can read as AI dressing.

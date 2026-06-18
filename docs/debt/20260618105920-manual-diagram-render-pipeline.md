---
id: 20260618105920
title: manual-diagram-render-pipeline
principal: 4h
interest: +15min/diagram, manual server+screenshot dance
hotspot: articles/diagrams/
business_capability: content-pipeline
payoff_trigger: a 2nd/3rd diagram makes the manual dance annoying, or before relying on it in CI
quadrant: prudent-deliberate
category: infrastructure
ai_authored: true
created: 2026-06-18
---

The article diagram pipeline is manual: start a throwaway `python3 -m http.server`, then drive Playwright by hand to navigate + screenshot the #card element. Chosen for now to prove the concept; not yet a single reproducible command/script. file:// is blocked in the browser backend, so the local-server step is unavoidable, but the navigate+screenshot steps could be scripted. README documents the manual steps as a stopgap.

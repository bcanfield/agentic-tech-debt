---
id: 20260618162926
title: cursor-plugin-unverified-live
principal: 1d
interest: broken flagship install ships silently until a Cursor user hits it
hotspot: cursor/.cursor-plugin/plugin.json, cursor/hooks/hooks.json
business_capability: distribution
payoff_trigger: live /add-plugin install of the cursor adapter confirms or contradicts ${CURSOR_PLUGIN_ROOT} expansion, plugin-hook cwd, and marketplace discovery
quadrant: prudent-deliberate
category: release
ai_authored: true
created: 2026-06-18
---

The Cursor marketplace packaging (plugin.json, marketplace.json, plugin-mode hooks.json with ${CURSOR_PLUGIN_ROOT}, and chdir_to_workspace) is grounded in Cursor's docs, the official cursor/plugins example plugins, and JSON-schema validation — but never run end-to-end on a live Cursor 2.5 install. Unconfirmed: that ${CURSOR_PLUGIN_ROOT} expands as expected, what cwd plugin hooks actually run with (hence whether chdir_to_workspace fires non-trivially), and that plugin.json/marketplace.json discovery works. Mirrors the ADR 0021 payoff trigger.

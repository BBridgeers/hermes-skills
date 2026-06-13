# DETOXXX V2 RE-AUDIT — Swarm Dispatch Prompt

The canonical 25-point critical audit prompt for dispatching the swarm workforce against the DETOXXX V2 Handbook. Includes mandatory minimum agent count and source document citation.

## Usage

Paste into the Swarm tab's Router Chat in Hermes Workspace, set mode to "Auto", and click "Route mission." The central agent will decompose across the 57-agent roster.

## Source Document

```
gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md
Access: rclone cat "gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md"
Size: ~4.4 MB — full 8-phase, 6-pillar protocol handbook
```

## Prompt

```
SOURCE DOCUMENT:
gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md
Access: rclone cat "gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md"
Size: ~4.4 MB — full 8-phase, 6-pillar protocol handbook

═══════════════════════════════════════
DISPATCH: Minimum 10 agents. The 57-agent roster exists to be used. Fewer than 10 is failure.
═══════════════════════════════════════

You are the master of this text. Lives depend on the quality of what follows. Hold nothing back.

For every section of the DETOXXX V2 Handbook, execute a merciless critical audit:

1. SURFACE EVERY WEAKNESS — thin detail, broken logic, obscured formatting. Be unabating.
2. GENERATE REPLACEMENT TEXT FOR EVERY FINDING — never critique without showing the fix.
3. AUDIT FOR COMPLETENESS — every section must answer: What? Why? What will I feel? What if it goes wrong? What if I skip it?
4. ENRICH PARALLELISM — PhD and mother-of-four must both understand.
5. REFORMAT FOR CLARITY — tables, callouts, tiered summaries.
6. BUILD PROGRESSIVE LAYERS — L1 (60s scan), L2 (10min read), L3 (deep study).
7. HUNT VAGUE PRONOUNS — every "this" and "that" becomes its concrete noun.
8. DEMAND SENSORY SPECIFICITY — where, what intensity, how long.
9. BUILD WHY SCAFFOLDING — WHAT→WHY→WHAT TO EXPECT adjacent, never separated.
10. VERIFY MECHANISM CHAINS — X→pathway→intermediate→Y or build the missing cascade.
11. CROSS-REFERENCE PILLARS — surface and bridge every missing intersection.
12. AUDIT CITATION DENSITY — label what is known, suspected, and guessed.
13. LABEL EVIDENCE TIERS — clinical trial, case series, mechanistic inference, or anecdote.
14. AUDIT GMF GATES — soft gates become hard. Vague measurements become operational.
15. CATASTROPHIZE FAILURE MODES — wrong dose, wrong timing, wrong order. Every deviation documented.
16. HARDEN AGAINST HUMAN ERROR — callout boxes, checklists, DON'T SKIP THIS anchors.
17. BUILD OPERATOR FIELD CARDS — condensed 1-2 page cards per tier.
18. CREATE RED-BOX AGENTS PAGE — highest-risk compounds, minimum supervision, non-negotiable preconditions.
19. TEST OPERATIONAL FOLLOWABILITY — zero assumed prior knowledge.
20. SPEAK LEAD SYSTEMS ARCHITECT VOICE — no hedging, no passive, no pleading.
21. MAP EMOTIONAL JOURNEY — write for the reader on their worst day.
22. BUILD PHYSICIAN EXECUTIVE BRIEF — 1-2 page MD/DO/ND front matter.
23. CROSS-REFERENCE FULL COMPENDIUM — Agent Registry, Supplement Registry, Scientific Knowledge Base.
24. BUILD DATA GAPS APPENDIX — "We don't know X. We suspect Y. The following are estimates."
25. TRACK WHAT CHANGED — safety-relevant changelog.

OUTPUT FORMAT per finding:
[PILLAR/SECTION] [REFERENCE]
FINDING: What's wrong.
REPLACEMENT: Exact substitute text.
RATIONALE: Why better.

Do not summarize. Do not be kind. Lives depend on this text.
```

## Notes

- Prompt includes mandatory minimum agent count as the first line after the source citation
- File path uses the rclone remote syntax for direct access from the VPS
- The 25 directives cover structure, clarity, evidence, safety, voice, and clinical packaging
- Designed to be decomposed by the central agent across research, analysis, critique, synthesis, and QA agents

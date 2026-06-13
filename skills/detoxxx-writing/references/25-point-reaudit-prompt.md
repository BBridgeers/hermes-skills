# DETOXXX V2 Handbook — 25-Point Re-Audit Prompt

This is the master critical-audit prompt that dispatches across all 25 directives. It was written June 2026 and dispatched via 12-agent swarm (api-70b78927d19574ab, June 7, 2026). The prompt decomposes into 25 directives grouped into 7 clusters.

## Source

SOURCE: `rclone cat "gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md"`
Size: ~4.4 MB, 8-phase, 6-pillar protocol handbook

## Directive Clusters

### STRUCTURAL & COMPLETENESS (1-3)
1. SURFACE EVERY WEAKNESS — thin detail, logic gaps, formatting issues
2. GENERATE REPLACEMENT TEXT FOR EVERY FINDING — exact substitute text
3. AUDIT FOR COMPLETENESS — what SHOULD the Handbook contain but doesn't? Five questions per Pillar: What? Why? What will I feel? What if it goes wrong? What if I skip it?

### CLARITY & ACCESSIBILITY (4-9)
4. ENRICH PARALLELISM — PhD vs parent translations
5. REFORMAT FOR CLARITY — tables, callouts, tiered summaries
6. BUILD PROGRESSIVE LAYER SYSTEM — L1 SCAN (60s), L2 READ (10min), L3 STUDY (deep dive)
7. HUNT AND DESTROY VAGUE PRONOUNS — every "this/that/these" named explicitly
8. DEMAND SENSORY SPECIFICITY — body location, quality, intensity, duration, danger threshold
9. BUILD "WHY" SCAFFOLDING — WHAT → WHY (mechanism) → WHAT TO EXPECT

### MECHANISM & EVIDENCE (10-13)
10. VERIFY MECHANISM CHAINS — X → pathway → intermediate → Y
11. CROSS-REFERENCE PILLARS — missing cross-links, bridge text
12. AUDIT CITATION DENSITY — qualifier or citation for every eyebrow-raising claim
13. LABEL EVIDENCE TIERS — CT/CS/MI/AN/MBE for every claim

### SAFETY & FAILURE RESILIENCE (14-19)
14. AUDIT GMF GATES — harden soft gates, operationalize vague measurements
15. CATASTROPHIZE FAILURE MODES — wrong dose, timing, combination, order
16. HARDEN AGAINST HUMAN ERROR — callout boxes, checklists, "DON'T SKIP THIS" anchors
17. BUILD OPERATOR FIELD CARDS — per tier: contraindications, labs, Herx tree, ER triggers, MVS, "cut order"
18. CONSOLIDATED RED-BOX AGENTS PAGE — highest-risk compounds, hard-stop preconditions
19. TEST OPERATIONAL FOLLOWABILITY — zero prior knowledge, text-only execution

### VOICE & TONE (20-21)
20. LEAD SYSTEMS ARCHITECT VOICE — zero hedging, zero passive, zero may/might
21. MAP EMOTIONAL JOURNEY — write for Blake on his worst day

### CLINICIAN-FACING & CROSS-REFERENCE (22-23)
22. PHYSICIAN EXECUTIVE BRIEF — 1-2 page MD/DO/ND front matter
23. CROSS-REFERENCE FULL COMPENDIUM — Agent Registry, Supplement Registry, Knowledge Base, Audit Notes

### VERSIONING & HONESTY (24-25)
24. DATA GAPS AND UNKNOWNS APPENDIX — "We don't know X. We suspect Y."
25. CHANGELOG — safety-relevant revision history

## Output Format

[PILLAR/SECTION] [LINE/PARA REFERENCE]
FINDING: What's wrong and why it matters.
REPLACEMENT: The exact text to substitute.
RATIONALE: Why this version is superior — what it fixes, who it serves, how it elevates.

## Dispatch Notes

- Minimum 10 agents from swarm roster — fewer is failure
- 12-agent dispatch proven June 7, 2026: deep-analyzer, content-builder, study-scope-coach, critique-agent, spec-architect, method-matchmaker, synth-agent, security-gatekeeper, root-cause-analyst, runbook-librarian, docs-scribe, strategist, fact-checker, research-planner
- Covered all 25 directives
- Output: 5 directive audit files + per-section hardening reports
- Top findings: Section 2 missing (142 dead refs), 6 competing Herxheimer copies, 38K-line handbook concatenated twice, GlyRS "2-3%" unverified, 6 citations in 4.6MB

# Source Synthesis Workflow for Tactical Protocols

When writing a DETOXXX V2 tactical protocol (Section 5) that must synthesize multiple external source documents into the Phase Map architecture, use this workflow. It was proven on Section 5.3 (CDS — Kalcker + Wenger + Phase Map + Audit Notes) and 5.4 (Colloidal Silver — Deep Research + Phase Map + Medical Dictionary PDF).

## Phase 1 — Source Discovery in Drive

1. Identify the Drive folder containing source materials (e.g., `Chlorine Dioxide_Collodial Silver & Monotomic Gold` at `1EJMANkdpdUOTnqDrD7PC2cUnLKIKscb7`).
2. List all files in the folder: `Drive API → files.list(q="'{folder_id}' in parents")`
3. Identify converted markdown versions first (`.md` files are readable by `read_file`; PDFs and EPUBs need extraction).
4. Also search the DETOXXX Handbook Docs folder (`1QqFi4ouGDoLYaW8AkV4VN_CvMsuVzIEZ`) for relevant Phase Map sections and audit notes.

## Phase 2 — Download & Extraction

1. Download all `.md` source files and the Phase Map in parallel using `execute_code` with direct Drive API media downloads.
2. For large files (>100KB, exceeding `read_file` limit), use `grep -n` to locate relevant sections, then `sed -n 'START,ENDp'` to extract only those blocks.
3. For PDFs: download for reference but prioritize markdown versions. The Training Course PDF was downloaded but not directly used because the Kalcker `.md` contained all operational data.

## Phase 3 — Data Extraction (Strip, Don't Summarize)

1. **Extract ONLY granular operational data**: dosing numbers, ppm math, route taxonomies, preparation details, timing rules, safety warnings, contraindications. Strip ALL philosophical framing, testimonials, historical narrative, regulatory commentary, beginner/course tone, and rhetorical persuasion.
2. **Use grep aggressively**: `grep -n -i "pattern1\|pattern2\|pattern3" source.md` to locate ALL mentions of key operational terms (dosing, routes, separation times, ppm, activation, precautions, nausea, stop criteria, contraindications).
3. **Read section-by-section**: After locating relevant line numbers, use `read_file(offset=X, limit=Y)` to read each protocol/section block in full. Do not rely on grep snippets alone — the surrounding context often contains the mechanism explanation needed for Pillar 6 density.

## Phase 4 — Cross-Source Synthesis

1. **Identify deviations between sources**: Kalcker vs Wenger vs Phase Map vs Deep Research. Where they disagree on dosing, timing, or mechanism, make an educated decision based on safety and consistency with the Phase Map architecture.
2. **The Phase Map is the authority**: All tactical protocol data must be subordinated into the Phase Map's phase architecture. If Kalcker says "use CDS for as long as needed" but the Phase Map says "CDS taper to zero by Day 65," the Phase Map wins. The source materials provide raw data; the Phase Map provides the architectural constraints.
3. **Merge best aspects**: Kalcker provides the richest operational detail (Protocol C, F, S, K, L, E, R, G, N — full dosing tables, route protocols, preparation methods). The Deep Research output provides mechanism depth, toxicological boundaries, and interaction mapping. The Phase Map provides phase deployment windows and hard gates. The Audit Notes provide redox separation rules and failure mode protocols. All four sources contribute to the final section.

## Phase 5 — Rebuild at Pillar 6 Density

1. Apply the detoxxx-writing skill's Tactical Protocol Section Architecture checklist (13 items).
2. Transform all "beginner/course" language into Resonate Protocol Architect voice — authoritative, clinical, mechanism-dense.
3. Replace general statements with named enzymes and pathways.
4. Add Hard Gates at every safety-critical junction.
5. Ensure the output reads as an integrated Phase Protocol embedded in the V2 regimen, not as a standalone book chapter.

## Proven Source Mapping (Section 5.3 example)

| Source | What It Provided |
|---|---|
| Kalcker CDS Guide (166KB .md) | Full protocol taxonomy (A-Z), dosing tables, route protocols, preparation methods, body-weight titration, precautions, emergency procedures |
| Phase Map Executive Brief (46KB .md) | CDS phase deployment (Phase 2 ramp → 3-4 peak → 5 taper → off), redox separation rules, hard gate architecture |
| HERMES_WAVE_EXECUTION_AUDIT_NOTES (201KB .md) | CDS overdose failure mode, redox conflict table with hourly daily schedule, antioxidant separation rules |
| Wenger Chlorine Dioxide (63KB .md) | Historical/philosophical context (mostly stripped — minimal operational data) |
| PHD VETTED CDS RESEARCH (70KB .txt) | Toxicity study references, safety data (stripped for mechanism-only extraction) |
| Deep Research Output (210KB .md) | Additional mechanism detail, regulatory context (stripped for mechanism-only extraction) |

## Pitfalls

- **The Kalcker guide has no markdown headers**: It uses HTML spans and inline styles from EPUB conversion. Use grep to find content by keyword, not by header structure.
- **Don't waste time on PDFs when .md conversions exist**: The Training Course PDF (3.2MB) was downloaded but never used — Kalcker's .md had all the same operational data in searchable text.
- **The Phase Map is short but architecturally dense**: The CDS-specific content is only ~20 lines out of 468. Read the entire Phase Map once to understand the full architecture, then extract only the CDS-specific deployment rules.
- **Source materials contradict each other on timing**: Kalcker says "2 hours" for antioxidant separation; Phase Map says "1 hour minimum, 4 hours preferred"; Audit Notes say "4 hours." The tactical protocol should use the strictest safe standard (4 hours) with the looser standard documented as the absolute floor (2 hours).

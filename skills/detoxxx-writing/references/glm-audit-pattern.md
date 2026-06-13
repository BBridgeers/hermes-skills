# GLM-5.1 Architecture Audit Pattern — Section 3 Case Study (May 22, 2026)

## Overview

Two-pass GLM-5.1 audit on Section 3 (Protocol Architecture) proved that a single audit pass misses errors. Two passes with different focal areas caught 15+ issues before shipping.

## Pass 1 — Catch Architecture Errors

**Focus**: Phase day ranges, lab timing, Phase Map contradictions.

**Prompt**: "Cross-check the Section 3 draft against the Audit Notes spec and Phase Map. Flag anything missing, incorrect, or architecturally inconsistent."

**Findings**:
1. Phase 1-2 day ranges wrong (1-8→1-10, 9-21→11-21) — **hard architectural error**
2. Gate 2 lab timing: Day 35 instead of Day 21 — **hard architectural error**
3. Gate 3 lab timing: Day 55 provoked urine instead of Day 35 — **hard architectural error**
4. Gate 4 lab timing: Day 70 serum metals instead of Day 56 — **hard architectural error**
5. Tier 3 expected duration: 155 days instead of 148 — arithmetic error

**Verdict**: "NEEDS PATCHES BEFORE UPLOAD. Two hard architectural errors make the draft actively contradictory to the Phase Map."

## Pass 2 — Catch What Pass 1 Missed

**Focus**: Vague criteria, Tier arithmetic, forward references, MVS/GSS completeness.

**Prompt**: "Second pass — find what you MISSED on first pass. Check: MVS agents in registry, cross-reference freshness, Tier 3 arithmetic (show work), gate column completeness, quantitative thresholds."

**Findings**:
1. Tier 3 standard-duration values wrong in 3 phases (text said "standard is 8" when Phase Map says 10, "standard is 21" when 11, "standard is 20" when 14)
2. 7 vague criteria across 4 gates lacking quantitative thresholds (CNS trajectory, nutritional status, HRV, sleep quality, exercise tolerance, functional capacity, drainage tolerance)
3. Phase 3 MVS ALA flagged as contradiction (false positive — MVS/GSS dual-column table is correct design)
4. 4/6 cross-referenced sections don't exist yet (forward references — expected for WIP handbook)
5. All gate tables structurally complete (4 columns present in every row)

**Verdict**: "Multiple patch-worthy issues found — the Phase 3 MVS ALA contradiction is architectural (not cosmetic), 4 referenced sections don't exist, 3 Tier 3 standard-duration values are numerically wrong, and 7 gate criteria lack quantitative thresholds."

## Key Pattern

- **Pass 1**: Broad architecture check — Phase Map alignment, day ranges, lab timing
- **Pass 2**: Surgical quality check — vague criteria, arithmetic, column completeness
- **Always**: Give GLM the Audit Notes spec + Phase Map + full draft. Don't summarize.
- **Always**: Run GLM via Ollama Cloud (no DeepSeek API key contention)
- **Never**: Use Kimi for architecture auditing — GLM only
- **After both passes**: Apply patches, re-upload single consolidated file, update tracker

## Prompt Size Limits (May 22, 2026)

GLM-5.1 via Ollama Cloud has practical limits on prompt size. Observations:
- **~600 lines / 38KB**: Processed in 1-3 minutes. Reliable.
- **~1,200 lines / 80KB**: Can take 3-5+ minutes. May timeout or produce no output.
- **19,000+ lines**: Cannot be sent as single prompt. Use targeted section audits instead.

**For full-handbook audits**: Run self-audit via grep/regex patterns on the assembled master file:
1. Cross-reference integrity: Extract all `Section X.Y` refs and verify target sections exist
2. Phase day ranges: grep for old V1 ranges and verify context
3. CDS timing: Check all CDS-reference lines for separation rule presence
4. Agent density: Count key agent references to verify coverage
5. Section presence: Verify all 13 section headers exist

**For architecture-critical sections**: Send individual sections (3+4 = ~1,200 lines) to GLM-5.1 as targeted prompts. This caught 15+ errors in Section 3 that self-audit would have missed.

## False Positives to Watch For

- MVS/GSS dual-column tables where the same agent appears at different doses in MVS vs GSS columns — this is correct design (MVS = minimum effective dose, GSS = optimal dose), not a contradiction
- Forward references to incomplete sections — expected in a sequentially-built handbook
- Subjective patient-reported outcomes with partial quantification — if they have a number (≥3/7 days, ≤3/10 score, 20-30 min) they're sufficiently quantified
- V2 Phase 5 days (57-70) appearing in context that references old V1 Phase 6 — verify context before flagging. The V2 Phase 5 IS Days 57-70.
- CDS-antioxidant lines flagged as "conflicts" when they're actually stating the separation rule — check for "separation," "4h," "after CDS," or "moat" keywords before flagging

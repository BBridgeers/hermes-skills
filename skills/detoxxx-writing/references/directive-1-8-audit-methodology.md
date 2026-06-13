# Directive 1+8 Assembly Audit — Structural Integrity + Sensory Specificity

## When to Use

When the assembled DETOXXX V2 Master Handbook (~19,000 lines, 2.3MB) needs a
structural integrity audit (Directive 1 — surface every weakness) combined with
a sensory specificity audit (Directive 8 — replace vague symptom descriptions
with body location, quality, intensity, duration). This is a read-only audit
workflow — it identifies findings; actual patching is a separate session.

## Prerequisites

- Assembled handbook at known path (typically `/opt/hermes/detoxxx_v2/DETOXXX_V2_MASTER_HANDBOOK.md`)
- Handbook is too large for `read_file` — use grep/sed exclusively
- Set `H=$HANDBOOK_PATH` for convenience

## Phase 1 — Structure Mapping

### Map section boundaries
```bash
grep -n "^# Section \|^## Section " $H
```

### Count lines per section (approximate)
```bash
awk '/^## Section/{s=$0; n=NR} /^# Section/{print s, n, "->", NR-n, "lines"}' $H
```

### Flag suspiciously thin sections
Sections under 200 lines in a 19,000-line handbook are candidates for content
gaps. Section 7 (Agent Encyclopedia) at ~8 lines and Section 12 (A-Z Index)
at ~106 lines are known thin spots.

## Phase 2 — Directive 1: Structural Weakness Scan (Parallel)

Run these simultaneously:

### 2a. Duplicate section detection
```bash
grep -n "^# 5\.1 " $H
```
Count occurrences of each section header. >1 occurrence of a major section
(like 5.1 Herxheimer) indicates duplicate concatenation.

### 2b. Missing section detection
Compare TOC entries against body content. The TOC is typically lines 161-175.
```bash
sed -n '161,175p' $H  # TOC entries
```
Then grep for each section's body header. If TOC lists it but no body content
follows, the section is MISSING.

Known issue: Section 2 (Clinical Safety) is listed in TOC but may be absent
from the body. Verify with:
```bash
sed -n '163,200p' $H | head -40
```

### 2c. Dead cross-reference detection
```bash
grep -c "Section 2\.[0-9]" $H
```
If Section 2 body content is absent, every one of these cross-references is
a dead link. Count them. Flag as CRITICAL if >10 dead refs exist.

### 2d. Mass duplication scan
Look for blocks that appear in multiple locations. A tell: identical warnings
at different line numbers.
```bash
grep -n "WARNING.*High-dose iodine" $H
```
If the same line count and line numbers are far apart, verify with diff:
```bash
diff <(sed -n '10821,10824p' $H) <(sed -n '12795,12798p' $H)
```

### 2e. Placeholder section detection
```bash
sed -n '14688,14696p' $H
```
Look for sections that are headers-only with no body content.

## Phase 3 — Directive 8: Sensory Specificity Scan (Parallel)

Run these simultaneously:

### 3a. Vague symptom language
```bash
grep -n -i "may cause\|could cause\|might cause\|can cause.*symptom" $H | \
  grep -i "symptom\|fatigue\|pain\|nausea\|headache\|dizzy\|brain fog\|malaise\|weak\|tired\|cramp\|ache\|sore\|anxiety\|depression\|insomnia\|rash\|itch" | \
  head -50
```

### 3b. Undefined symptom labels in profiles
```bash
grep -n "symptoms include\|symptoms may\|symptoms can\|symptoms.*include\|present with\|manifests as\|characterized by" $H | head -60
```

### 3c. Weasel-word symptom descriptions
```bash
grep -n -B1 -A2 "transient\|self.limiting\|generally mild\|usually mild\|typically mild\|mild symptom\|mild reaction\|expected and\|is expected\|resolve within\|resolves within" $H | \
  grep -i "symptom\|reaction\|headache\|fatigue\|nausea\|pain\|rash\|detox" | head -40
```

### 3d. "Depletion manifests as" — vagueness cascade
```bash
grep -n "Depletion Risk.*manifests as\|depletion.*manifests\|Manifests as:" $H
```
These statements describe what the PATIENT FEELS but typically lack body
location, quality, intensity, and duration. Every match is a finding.

### 3e. "Mood dysregulation" and other clinical abstractions
```bash
grep -n "mood dysregulation\|sleep fragmentation\|cognitive impairment\|immune dysregulation\|exercise intolerance" $H | head -20
```
These are clinical terms, not sensory experiences. Flag any that appear
without accompanying sensory-grounded description.

### 3f. Tier profile symptom vagueness
```bash
sed -n '683,780p' $H
```
Tier 1 and Tier 2 profiles use undefined symptom labels ("mild mercury
symptoms," "CIRS symptoms," "POTS-like symptoms"). These are TIERING
CRITERIA — vagueness here means patients can be misclassified.

## Phase 4 — Compile Findings by Severity

Organize every finding into:

```
[PILLAR/SECTION] [LINE REFERENCE]
FINDING: What's wrong and why it matters.
REPLACEMENT: The exact text to substitute.
RATIONALE: Why this version is superior.
```

### Severity Tiers
- **CRITICAL**: Safety-impacting (missing safety section, competing decision trees, dead safety cross-references)
- **HIGH**: Structural integrity (duplicate content, empty sections, mass dead references)
- **MEDIUM**: Content quality (vague symptoms used as decision criteria, opaque clinical descriptions)
- **LOW**: Minor (thin subsections, incomplete symptom lists)

### Summary Table
End the output with a severity-ranked summary table:
```
| # | Severity | Finding | Lines |
|---|----------|---------|-------|
```

## Phase 5 — Priority Order for Fixes

Fix in this order:
1. Section 2 (Clinical Safety) — insert before Section 3
2. Deduplicate 5.1 Herxheimer copies — retain ONE authoritative version
3. Deduplicate mass Pillar content — remove redundant blocks
4. Replace "halogen detox reaction" warning with sensory-specific table
5. Replace Tier 1/2 symptom profiles with sensory-grounded tables
6. Replace "depletion manifests as" entries with differential symptom tables
7. Replace opaque clinical abstractions with sensory-grounded descriptions

## Known Findings (May 2026 Audit)

The audit executed June 7, 2026 on the 19,147-line assembled handbook found:

- **CRITICAL**: Section 2 entirely missing (70 dead cross-references)
- **CRITICAL**: 6 competing versions of Section 5.1 (lines 1486-2620)
- **CRITICAL**: Mass Pillar content duplication (~10,000 lines)
- **HIGH**: Section 7 is 8-line placeholder
- **MEDIUM**: Section 12 at 106 lines (should be 400-800)
- **CRITICAL**: "Halogen detox reaction" warning — zero sensory specificity
- **HIGH**: Tier 1/2 symptom profiles — undefined labels used as tiering criteria
- **HIGH**: CDS "depletion manifests as" — 3 undifferentiated symptom cascades
- **MEDIUM**: "Mood dysregulation" and "neural circuit reconfiguration" — opaque abstractions

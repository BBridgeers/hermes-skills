# Directive 24 + 25 Execution Pattern

Proven methodology for building Data Gaps & Unknowns Appendix (Directive 24) and Safety Changelog (Directive 25) against the assembled DETOXXX V2 Master Handbook. Developed June 7, 2026 against the 19,147-line MASTER HANDBOOK.

## Prerequisites

1. Master Handbook must be local: `/opt/hermes/detoxxx_v2/DETOXXX_V2_MASTER_HANDBOOK.md`
2. Load `detoxxx-writing` skill for voice, evidence-tier framework, and quality standards
3. Load `protocol-handbook-authoring` for Drive integration
4. The completeness-and-evidence-tier-audit.md reference (Directive 3+13) provides the evidence-tier definitions — Directive 24 extends them into a comprehensive data gaps appendix

## Directive 24 — Data Gaps and Unknowns Appendix

### Phase 1: Systematic Grep Mining

Run these grep patterns against the handbook to locate all quantitative/pharmacodynamic claims that may outrun available data:

```bash
# Find model-based estimates and uncertainty language
grep -ni "approximately\|roughly\|estimated\|estimate\|projected\|model-based\|we don't know\|not measured\|not been measured\|not yet\|not studied\|no study\|no data\|data.*lacking\|unknown\|unresolved\|unclear\|uncertain\|speculative\|theoretical\|hypothetical" HANDBOOK.md

# Find quantitative claims (half-lives, binding affinities, pool sizes, percentages)
grep -ni "half-life\|t½\|clearance rate\|Km\|Vmax\|IC50\|EC50\|LD50\|Kd\|percent\|%\|gram\|mg/kg\|estimate\|population.*billion\|population.*million\|10-15" HANDBOOK.md

# Find specific model-based numeric estimates (highest priority)
grep -ni "GSH pool\|10-15 gram\|GlyRS\|2-3%\|2-3 percent\|argyria.*gram\|threshold.*gram\|deplet.*%\|substitution.*error" HANDBOOK.md
```

### Phase 2: Duplication Detection

The handbook contains structurally identical passages (the Herxheimer Three Choke Points breakdown appears in FULL at three locations: ~lines 1605, 2015, 2563). Detect duplicates:

```bash
# Find duplicate section headers
grep -n "^###.*Herxheimer\|^###.*Three Choke\|^###.*GSH\|^###.*Mitochondrial" HANDBOOK.md

# Find structural duplicates by signature phrase
grep -n "three-front assault\|combined Complex I and III\|cytokine-driven fibrinogen" HANDBOOK.md
```

When the same model-based estimate appears in duplicated passages, it propagates as if independently corroborated. Flag this in the cross-reference section of the appendix.

### Phase 3: Classification

Classify each finding using this hierarchy:

**Criticality:**
- CRITICAL: Underlies architecture across 4+ sections, no citation, load-bearing mechanism
- HIGH: Pharmacodynamic claim with no human trial data, or quantitative claim directly contradicted by handbook's own clinical vignettes
- MEDIUM: Population prevalence estimates applied to target demographic without specific data
- LOW: Minor quantitative claims that need qualification but don't undermine architecture

**Evidence Tier (from Directive 13):**
- Clinical Trial: Randomized controlled human study cited
- Case Series: Multiple documented human cases
- Mechanistic Inference: Biochemical logic, in vitro, animal models (default tier)
- Anecdote: Individual reports, practitioner experience

**Data Gap Flags:**
- MODEL-BASED ESTIMATE: Quantitative claim derived from models, not measurements
- THEORETICAL EXTRAPOLATION: Mechanism applied to unmeasured biological system
- IN VITRO/ANIMAL ONLY: Data from non-human systems, not validated in humans
- SINGLE-SOURCE UNCERTAINTY: Claim resting on one source or practitioner experience
- POPULATION-PREVALENCE UNCERTAINTY: Global estimate applied to specific demographic

### Phase 4: Uncertainty Label Language

For the highest-priority finding (GlyRS 2-3%), use this template (adapted from the Morgellons gold standard in the handbook itself):

```
THIS IS A MODEL-BASED ESTIMATE, NOT AN EMPIRICAL CONSTANT. The structural logic
(glyphosate as glycine analog, competitive at GlyRS) is biochemically sound, but
the quantitative error frequency is derived from analog misincorporation rates in
other aminoacyl-tRNA synthetase systems. Direct measurement of glyphosate
misincorporation into human fibrinogen in exposed populations has not been performed.
```

### Phase 5: Output Structure

The appendix should include:
1. Purpose section with evidence-tier definitions
2. CRITICAL findings (2-3 claims that underlie architecture)
3. HIGH findings (5-7 pharmacodynamic claims without human data)
4. MEDIUM findings (3-5 population prevalence estimates)
5. LOW findings (3-5 minor quantitative claims)
6. Gold standard identification (Morgellons pattern to replicate)
7. Summary table of all model-based numeric estimates needing prefix
8. Cross-reference: duplicated claim propagation flag
9. Consensus section: what the handbook gets right
10. Recommended actions (5 items, prioritized)

### Pitfalls

- **Do NOT flag the Morgellons section as a gap.** It is the gold standard for evidence-tier transparency. Identify it as the TEMPLATE to replicate for other uncertain domains.
- **Do NOT flag mechanism descriptions as gaps.** The handbook's strength is named-enzyme mechanism density. Flag quantitative claims that outrun available data, not the mechanisms themselves.
- **The "#1 data gap" is always the GlyRS 2-3% figure.** It is the most load-bearing quantitative claim in the handbook (underlies 6+ sections) and has NO citation. Every Directive 24 audit must flag this first.
- **When the handbook's own evidence contradicts a claim, USE it.** The colloidal silver "four orders of magnitude" safety margin is contradicted by the handbook's own clinical vignette showing argyria at ~18x, not ~10,000x. Point this out explicitly — it's the strongest form of internal audit.
- **Duplicated passages propagate uncertainty.** When the same model-based estimate appears in structurally identical passages at 3+ locations, it creates the illusion of independent corroboration. Flag this explicitly.

---

## Directive 25 — Safety Changelog

### Phase 1: Identify V2-Specific Safety Additions

Since no explicit V1-to-V2 diff exists, identify safety-relevant revisions by structural features UNIQUE to V2:

```bash
# Find Hard Gates (new in V2 — V1 had recommendations, not gates)
grep -n "HARD GATE\|== SEQUENCE MANDATE\|== NON-NEGOTIABLE\|HARD STOP" HANDBOOK.md

# Find dose ceilings (new explicit limits)
grep -n "must not exceed\|hard max\|maximum.*dose\|dose ceiling\|hard ceiling\|DO NOT" HANDBOOK.md

# Find safety lockouts (new phase-gated restrictions)
grep -n "must not begin until\|prerequisite\|confirmed before\|must be drawn at baseline" HANDBOOK.md

# Find codified rescue protocols (new structured interventions)
grep -n "RESCUE mode\|must not be withheld\|Grade 3-4 rescue\|EMERGENCY ROOM" HANDBOOK.md
```

### Phase 2: Classification

**CRITICAL — Life-Safety Additions:**
- Changes that prevent death or permanent organ damage
- Gate architecture (replaces calendar-based advancement)
- Structured Herxheimer management (replaces "push through" culture)
- Binder pre-load mandate (prevents CNS metal redistribution)
- Iodine ramp with mandatory cofactors (prevents Jod-Basedow crisis)

**HIGH — Dose Ceilings and Safety Lockouts:**
- Explicit dose ceilings not present in V1
- Hard stops with no-exception language
- Perpetual maintenance mandates
- Mandatory clearance confirmations before escalation

**MEDIUM — Architecture Refinements:**
- Tier systems (Case Archetypes, MVS/GSS)
- Codified rescue dosing
- Contraindication protections
- Agent separation windows

### Phase 3: V1 vs V2 Comparison Table

Build a feature-comparison table with these columns:
- Feature name
- V1 status (what existed before: unstructured, absent, recommendation-only, calendar-based, concurrent, unrestricted, none, all-or-nothing)
- V2 status (what changed: structured, mandatory, gated, pre-loaded, ramped, hard ceiling, perpetual, tiered)

Target 12-16 rows covering all safety architecture dimensions.

### Phase 4: Unresolved Safety Questions

Identify 5 questions the handbook does not answer:
1. Lifetime cumulative exposure ceilings (CDS, chelators)
2. Long-term organ surveillance beyond protocol end
3. Chronic high-dose nutrient safety (glycine 10-20g/day)
4. Combination agent bleeding risk (triple proteolytic enzymes)
5. Post-protocol regression monitoring

### Phase 5: Output Structure

The changelog should include:
1. Overview (methodology note since no explicit V1-V2 diff exists)
2. CRITICAL life-safety additions (3-4 items)
3. HIGH dose ceilings and safety lockouts (5-7 items)
4. MEDIUM architecture refinements (5-7 items)
5. V1 vs V2 comparison table
6. Unresolved safety questions for future revisions

### Pitfalls

- **Do NOT invent a V1 that didn't exist.** The handbook is V2. There is no V1 source document to diff against. Identify V2-specific features by the presence of structural safety elements (Hard Gates, Sequence Mandates, dose ceilings) that represent hardening beyond a V1 that had recommendations but not mandates.
- **Do NOT list every agent or dose as a changelog entry.** The changelog is for SAFETY-RELEVANT revisions — hard gates, dose ceilings, mandatory prerequisites, safety lockouts. Not for agent additions, dose adjustments, or phase reorganizations that don't carry safety implications.
- **The V1-V2 comparison table must be side-by-side.** "V1: Unstructured, V2: 4-grade severity + decision tree + ER notification" — not "V2 added a Herxheimer management system." The table format forces explicit comparison.
- **Include the clinical vignettes as evidence.** When a gate or ceiling exists because a specific failure mode is documented in a clinical vignette, name the vignette (age, gender, outcome) and cross-reference the line number. This anchors safety revisions in concrete documented harm, not hypothetical risk.

---

## File Output Conventions

Both deliverables go to `/opt/hermes/detoxxx_v2/`:
- `DIRECTIVE_24_DATA_GAPS_APPENDIX.md`
- `DIRECTIVE_25_CHANGELOG.md`

Target sizes:
- Directive 24: 350-400 lines, 3,000-3,500 words, 20-25KB
- Directive 25: 180-220 lines, 1,200-1,600 words, 9-12KB

After writing, verify with `wc -l -w -c` and `grep -c "U-[0-9]"` (should be 18+ uncertainty labels) and `grep -c "C-[0-9]"` (should be 14-16 changelog entries).

Upload to GDrive immediately per the detoxxx-writing skill's Upload-Immediately Mandate.

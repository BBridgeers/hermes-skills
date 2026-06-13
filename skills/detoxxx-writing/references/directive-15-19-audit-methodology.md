# Directives 15 + 19 Audit Methodology

## What These Directives Test

- **Directive 15 — Catastrophize failure modes:** For every protocol step, if the failure mode isn't documented at the point of instruction, flag it. The user must know what happens if they skip, mis-time, or mis-dose each step — at the moment they're deciding whether to follow it.
- **Directive 19 — Test operational followability:** Can a reader with ONLY the Handbook physically execute every protocol step? No prior knowledge, no external references, no assumed competency. Flag every missing scaffold: undefined abbreviations, missing visual references, unstated preparation steps, dead cross-references, ambiguous dosing.

## Audit Workflow

### Phase 1 — Document Acquisition

1. Retrieve the target document from Drive or local path
2. Save locally for grep/sed operations: `cp /source/path /tmp/audit_target.md`
3. Get line count: `wc -l` — determines chunking strategy

### Phase 2 — Structure Mapping

1. Extract all section headers: `grep -n "^# \|^## \|^### " target.md | head -200`
2. Identify the actionable sections — Daily Grids (Section 4), Tactical Protocols (Section 5), Phase Gates (Section 3) are highest priority for 15+19
3. Map section boundaries: note line numbers where each major section starts/ends
4. Check for duplication: `grep -c "^# 5\.[0-9]" target.md` — if count > section count, duplicates exist

### Phase 3 — Sectional Deep-Read

Read actionable sections in targeted chunks using sed:
```
sed -n 'START_LINE,END_LINEp' target.md
```

Priority order:
1. Master Daily Grids (Section 4) — all 8 phases
2. Tactical Protocols (Section 5) — CDS, chelation, iodine, enzymes
3. Phase Gates (Section 3.2) — pass/fail criteria
4. Pillar-to-Phase Matrix (Section 3.3) — agent timing
5. Clinical Safety (Section 2) — if it exists

### Phase 4 — Contradiction Detection

For every agent in the daily grids, cross-reference its tactical protocol:
- Same agent, different schedule? → CONTRADICTION
- Grid says "start Day X" but protocol says "start Phase Y"? → CONTRADICTION
- Grid has 5 doses/day but protocol says 8? → CONTRADICTION
- Grid implies continuous dosing but protocol says cycled? → CONTRADICTION
- Gate criterion references state only achievable AFTER entering the phase? → CIRCULAR DEPENDENCY

### Phase 5 — Operational Followability Scan (Directive 19)

Check every instruction in the daily grids against this checklist:

| Check | What to look for |
|---|---|
| Preparation timing | Agent required but prep window not stated before use |
| Concentration verification | "X ppm" but no method to verify concentration |
| Visual references | Chart/scale referenced but not included (Bristol, urine color) |
| Abbreviations | Medical shorthand (Q3H, Q8H, BID) never defined for lay reader |
| Weight-based dosing | Drug is weight-dosed but only fixed mg given (ivermectin, DMSA) |
| Unit conversion | mg/kg given but no lb→kg help or capsule rounding rules |
| Procurement guidance | Herbs/tinctures/specialty items with no sourcing info |
| Dead references | "Per Pillar X spec" but dose not stated in the grid row |
| Chemical identity | Substance name used in grid doesn't match the actual substance prepared |
| Gate circularity | Entry criterion requires state only achievable inside the target phase |

### Phase 6 — Missing Failure Mode Scan (Directive 15)

For every agent row in the daily grids, ask:

1. **What if user skips this entirely?** Is the consequence stated at THIS decision point?
2. **What if user mis-times it?** (too close to food, too close to another agent, wrong time of day)
3. **What if user mis-doses it?** (double dose, half dose, wrong concentration)
4. **What if user combines it with the wrong co-agent?** (CDS + antioxidant, DMSA without binder, iodine without selenium)
5. **What if the correct action produces a symptom the user misinterprets?** (Herx vs DILI, Herx vs redistribution)
6. **Is the failure VISIBLE to the user?** If not (CDS cancellation is invisible), is the operational consequence explained in terms the user cares about?

Common failure mode taxonomy that emerges across audits:

- **Invisible failures** — user can't detect they're failing (CDS-antioxidant cancellation)
- **Wrong-row warnings** — safety warning on companion row, not agent row (selenium warning not on iodine row)
- **Delayed consequence not at decision point** — Phase 6 crash mechanism in Gate section, not Phase 6 grid
- **Rule without consequence** — "Never empty stomach" stated, mechanism not explained
- **Missing differential** — two conditions with opposite responses (STOP vs CONTINUE) not distinguished
- **Intuitive wrong response** — what user naturally does (double missed dose) is dangerous

### Phase 7 — Output Compilation

Format: `[SECTION] [LINE] FINDING → REPLACEMENT → RATIONALE`

Group by:
1. Directive 19 findings (operational gaps)
2. Directive 15 findings (missing failure modes)
3. Structural findings (duplication, missing sections, lab scaffolding)

Severity tiering:
- **FATAL** — user physically cannot proceed past this step
- **CONTRADICTION** — two sections prescribe different protocols
- **HIGH** — safety risk present, warning missing at decision point
- **MEDIUM** — usability gap, doesn't block execution but reduces efficacy

Include replacement text for every finding. Replacement text should be:
- At Pillar 6 density (named enzymes, specific mechanisms, bond chemistry where relevant)
- Include a Bridge Box or consequence statement the user can understand
- State the mechanism, the consequence, and the correction
- Be insertable directly at the point of instruction

## Proven Pattern from June 2026 Handbook Audit

The 38,294-line master handbook produced 27 findings:
- **13 Directive 19** (operational followability)
- **11 Directive 15** (missing failure modes)
- **3 Structural** (duplication, missing Section 2, lab scaffolding)

Key finding categories that repeat across audits:
1. CDS preparation always gapped — 24h prep window not instructed at first grid reference
2. Iodine phase placement often contradictory between grids and protocol specs
3. ALA dosing (# of doses/day) is the most common grid vs protocol contradiction
4. Chelation cycling (daily vs ON/OFF) is the second most common
5. Bristol/urine charts referenced but never included
6. Medical abbreviations never defined for lay audience
7. Weight-based drugs given as fixed doses
8. Concentration verification missing for variable-concentration products
9. Gate criteria with circular phase dependencies
10. Failure mode warnings placed on wrong agent row (companion not primary)

## Pitfalls

- **Don't audit theory sections.** Directives 15+19 apply to OPERATIONAL content — daily grids, tactical protocols, dosing instructions. Mechanism explanations, research citations, and architectural rationale don't need followability checks.
- **Cross-reference contradictions are the highest-value find.** A user will follow either the grid OR the protocol doc. If they conflict, the user executes a different protocol than intended.
- **Invisible failures need visceral framing.** "Complete mutual cancellation" is biochemistry. "You took expensive salt water for 90 days" is operational. The latter drives compliance.
- **Warnings on wrong rows are stealth failures.** The user reads the agent they're about to take. If the warning is on the companion agent row (6 rows up in a dense grid), they miss it.
- **Replacement text must be insertion-ready.** Don't describe what should be added — write the actual text block that goes at that point in the document.

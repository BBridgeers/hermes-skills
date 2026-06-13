# Section 8 → Section 4 Cross-Reference Audit Pattern

**Developed**: May 22, 2026 — DETOXXX V2 Handbook completion session  
**Purpose**: Systematic audit to verify Section 4 daily grids reflect all agent, timing, and synergy requirements from Section 8 pathways.

## When to Run

- After Section 8 pathways are written or remapped to V2 Phase Map
- After Section 4 daily grids are built or modified
- As a final quality gate before master assembly

## Step 1 — Extract Section 8 Requirements

For each pathway file (section_8_1 through 8_9), extract:
- **Mandatory agents**: grep for "Protective mandate", "HARD GATE", "SEQUENCE MANDATE", "NON-NEGOTIABLE"
- **Co-administration pairs**: Agents that must be taken together (e.g., nattokinase + serrapeptase per 8.8A)
- **Separation rules**: Agents that must be separated by time (e.g., CDS 4h from antioxidants per 8.7)
- **Phase constraints**: Which phases each pathway operates in (from V2 Phase Architecture annotations)
- **Cofactor requirements**: Agents that require companion agents (e.g., iodine + selenium per 8.6C)

## Step 2 — Check Section 4 Compliance

For each requirement, check the appropriate phase grid(s):
- Is the agent present in the correct phase?
- Is it at the correct time slot? 
- Is it at the correct dose?
- Are co-administration pairs in the same time row?
- Are separation rules enforced with 🛑 markers?
- Are cofactors present alongside their primary agent?

## Step 3 — Classification

| Severity | Criteria | Example |
|:---|:---|:---|
| **CRITICAL** | Agent missing from ALL phases, or deployed in wrong phase | Humic/Fulvic Acid entirely absent — 8.3B HARD GATE requires 7-day pre-treatment before chelators |
| **HIGH** | Agent present but wrong phase, wrong time slot, or missing mandatory cofactor | Iodine in Phase 2 but Selenium missing — 8.6C HARD GATE: iodine without selenium = thyroid oxidative stress |
| **MEDIUM** | Dose below target, timing proximity issues, co-administration not simultaneous | Nattokinase and Serrapeptase 1h apart — 8.8A mandates co-administration for synergistic fibrinolytic action |

## Step 4 — Common Gaps Found (May 22, 2026)

### Missing Agents
| Agent | Section 8 Mandate | Where Missing |
|:---|:---|:---|
| **Glycine** | 5 pathways (8.1D, 8.2E, 8.3D, 8.5D, 8.9C) — GSH precursor, GlyRS competition, collagen | Phases 1-5 (only in 6, 8) |
| **Humic/Fulvic Acid** | 8.3B HARD GATE — 7-day pre-treatment before chelators for GO-metal surface competition | All phases |
| **Selenium** | 8.2E GSH triad, 8.6C iodine companion | Phase 1-2 |
| **CoQ10** | 8.5C ABSOLUTE CONTRAINDICATION for statin users without CoQ10 from Day 1 | Phase 1 |
| **Zinc Carnosine** | 8.1D tight junction pair with L-glutamine | Phase 2 |
| **Calcium D-Glucarate** | 8.2D Phase II glucuronidation block | All phases |
| **Phosphatidylcholine** | 8.2D biliary export priming from Phase 1 Day 1-7 | Phase 1-4 (only in 5-8) |
| **Sulforaphane** | 8.9C Nrf2/proteasome upregulation | Phases 4-6 |
| **Astragalus** | 8.4A Th1 rebalancing — IgG1/IgG3 class-switching | Phases 5-6 |

### Co-Administration Gaps
| Agents | Gap | Fix |
|:---|:---|:---|
| Nattokinase + Serrapeptase | 1h apart in Phase 4 | Co-administer at same time slot (08:00) |
| Iodine + Selenium | Selenium missing from Phase 2 | Add Selenium 200mcg at 07:30 with iodine at 14:00 |

### Timing Conflicts
| Issue | Detail | Fix |
|:---|:---|:---|
| Silver + NAC at 11:00 | Both at same time, both require 4h separation | Move silver to 07:00 (compatible with CDS) |
| Antioxidant window 18:00 | 3h after 15:00 silver (needs 4h) | Shift window to 19:00, move dinner to 18:00 |

## Step 5 — Apply Patches

- Insert missing agents at correct time slots in correct phase grids
- Move conflicting agents to resolve timing violations
- Update Daily Totals boxes
- Update pill counts
- Re-upload immediately after each patch
- Re-run cross-reference to verify fix

## False Positives to Watch For

- **Section 8.8 14-day enzyme pre-treatment rule**: This applies to dedicated biofilm-disruption antimicrobial strikes (oregano oil, berberine, garlic), NOT to the Phase 2 gentle antiparasitic botanical introduction (Black Walnut, Wormwood, Clove). The antiparasitic herbs target free-swimming parasites directly — they don't need biofilm penetration.
- **V1 phase names in Section 8**: Pathway names like "Gut Terrain Reset" and "Immune Recalibration" are pathway TITLES, not phase labels. Verify context before flagging.

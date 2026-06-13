# Directive 2 + 22 Execution Pattern
## Full-Handbook Audit + Replacement Generation + Physician Executive Brief

### When to Use

When the user requests Directive 2 (generate replacement text for every audit finding) and/or Directive 22 (physician executive brief) against the assembled DETOXXX V2 Master Handbook. This is the systematic workflow proven June 7, 2025 against the 38,294-line, 4.4MB assembled handbook, producing 18 findings across CRITICAL/HIGH/MEDIUM severity tiers with full replacement text and a 306-line physician brief.

### Prerequisites

- Assembled handbook downloaded to local disk (use rclone: `rclone cat "gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md"`)
- Handbook is too large for `read_file` at 4.4MB — use grep/sed exclusively
- Skills loaded: `detoxxx-writing`, `protocol-handbook-authoring`, `google-workspace`

### Phase 1 — Parallel Structural Scan (12 Operations)

Set `H=/path/to/handbook.md` and run all 12 grep/sed operations in parallel across 4 `terminal()` calls:

**Scan Group 1 — Structure Mapping:**
```bash
grep -n "^# Section \|^## Section " $H | head -40
awk '/^## Section/{s=$0; n=NR} /^# Section/{if(s) print s, "@ line", n, "->", NR-n, "lines"}' $H
```

**Scan Group 2 — Duplicates + Dead Refs:**
```bash
grep -n "^# 5\.1 \|^## 5\.1 \|^### 5\.1" $H | head -20
sed -n '1,200p' $H | grep -n "Section\|## \|# "
grep -c 'Section 2\.' $H  # dead cross-reference count
grep -c "WARNING.*High-dose iodine" $H  # duplication marker
```

**Scan Group 3 — Vague Symptoms + Undefined Labels:**
```bash
grep -n -i "may cause\|could cause\|might cause\|can cause.*symptom" $H | grep -i "symptom\|fatigue\|pain\|nausea\|headache\|dizzy\|brain fog\|malaise\|weak\|tired\|cramp" | head -50
grep -n "symptoms include\|symptoms may\|symptoms can\|symptoms.*include\|present with\|manifests as\|characterized by" $H | head -60
```

**Scan Group 4 — Weasel Words + Depletion + Abstractions + Tiers:**
```bash
grep -n -B1 -A2 "transient\|self.limiting\|generally mild\|usually mild\|typically mild\|mild symptom\|mild reaction\|expected and\|is expected\|resolve within\|resolves within" $H | grep -i "symptom\|reaction\|headache\|fatigue\|nausea\|pain\|rash\|detox" | head -40
grep -n "Depletion Risk.*manifests as\|depletion.*manifests\|Manifests as:" $H | head -20
grep -n "mood dysregulation\|sleep fragmentation\|cognitive impairment\|immune dysregulation\|exercise intolerance" $H | head -20
sed -n '650,850p' $H | grep -n "symptom\|signal\|indicator\|marker\|present\|profile" | head -30
```

### Phase 2 — Targeted Content Extraction for Replacement Text

Once scan results identify line numbers, extract the exact text blocks that need replacement:
```bash
sed -n 'START,ENDp' $H   # Tier profiles, depletion blocks, stop criteria, etc.
```

Key extraction targets (line numbers from 2025-06-07 audit):
- Tier profiles: `sed -n '30,140p' $H`
- Depletion manifest blocks: `sed -n '3110,3150p' $H`
- Bromide flu: `sed -n '1395,1425p' $H`
- Section 7 placeholder: `sed -n '14688,14700p' $H`
- Section 12 A-Z: `sed -n '18876,18982p' $H`
- Dose ceilings (CDS, silver, fibrinolytics, chelators): targeted grep for ceiling/max/limit patterns
- Contraindications: grep for ABSOLUTE CONTRA, contraindicated, MUST NOT
- Lab monitoring: grep for draw day, lab frequency, monitor weekly

### Phase 3 — Dose Ceiling Extraction (Separate Targeted Scan)

```bash
# CDS ceilings
grep -n -i "CDS.*ceiling\|CDS.*max\|CDS.*limit\|CDS.*mL\|maximum.*CDS\|dose.*cds.*mL" $H | head -30

# Colloidal silver ceilings
grep -n -i "silver.*ceiling\|silver.*max\|silver.*limit\|silver.*ppm\|colloidal.*dose\|silver.*mg" $H | head -30

# Fibrinolytic ceilings
grep -n -i "nattokinase.*ceiling\|serrapeptase.*ceiling\|fibrinolytic.*max\|nattokinase.*FU\|serrapeptase.*SU\|enzyme.*max.*dose" $H | head -20

# Chelator ceilings
grep -n -i "DMSA.*mg/kg\|EDTA.*mg/kg\|DMPS.*mg/kg\|chelat.*max\|chelat.*ceiling\|mg/kg.*max" $H | head -20

# Contraindications
grep -n -i "ABSOLUTE CONTRA\|contraindication\|contraindicated\|MUST NOT\|DO NOT USE\|do not use\|never use\|prohibited" $H | head -40

# Lab monitoring
grep -n -i "lab.*frequency\|monitor.*weekly\|lab.*every\|CBC.*every\|CMP.*every\|draw.*day\|lab.*draw\|lab draw" $H | head -30
```

### Phase 4 — Compile Findings by Severity

Every finding uses this format:
```
### FINDING [ID] — [SHORT TITLE]
**[Location] [Line reference]**

**FINDING:** What is wrong and why it matters.
**REPLACEMENT:** Exact text or structural fix.
**RATIONALE:** Why this version is superior.
```

### Severity Classification

| Tier | Criteria | Examples |
|:---|:---|:---|
| **CRITICAL** | Safety-impacting. Missing safety section, competing decision trees, dead safety cross-references, agent ceiling discrepancies that create unsafe dosing paths | Missing Section 2, 6 competing Herxheimer copies, silver ppm discrepancy |
| **HIGH** | Structural integrity or clinical decision quality. Vague symptoms used as decision criteria, opaque clinical descriptions, missing dose ceilings from prominent safety positions, undefined tiering criteria | Depletion lacks sensory specificity, Tier labels undefined, CDS ceiling buried, bromide flu "indistinguishable from viral illness" |
| **MEDIUM** | Content quality. Thin sections, incomplete indexes, undefined terms in clinical vignettes, insufficient qualification language | A-Z thin, Section 13 truncated, vignette terms undefined |

### Phase 5 — Generate Replacement Text

For each finding, the replacement text must meet Pillar 6 density standard:
- Named enzymes/pathways (never "liver enzyme" — always "CYP2E1", "GPx", "GST")
- Specific body locations ("epigastrium, 2 finger-widths below sternum" — not "stomach")
- Quantitative thresholds ("intensity 4-7/10, duration >4 hours" — not "severe")
- Differential diagnosis (distinguishing features between similar presentations)
- Tables with 4+ columns where the finding demands sensory specificity

For "depletion manifests as" findings specifically, the replacement format is a differential diagnosis table:

| Symptom | Body Location | Quality | Intensity Progression | Duration | Distinguishing Feature |

This table format gives patients an operational monitoring system: "My fatigue responds to NAC = GSH depletion. My fatigue responds to CoQ10 = mitochondrial depletion. My nausea is dose-immediate and epigastric = mucosal depletion."

### Phase 6 — Build the Physician Executive Brief (Directive 22)

The brief is a 1-2 page surgical extraction of physician-critical information. Required sections:

1. **Protocol Identity** — 8-phase architecture table (compact)
2. **Indications** — Primary, secondary, NOT indicated
3. **Absolute Contraindications** — All conditions with mechanism column
4. **Labs and Monitoring Cadence** — Baseline panel (12 items), phase boundary labs (7 gates), active-phase monitoring for Tier 3-4
5. **Dose Ceilings — Highest-Risk Agents** — CDS, colloidal silver, fibrinolytics, chelators, high-dose iodine. Each with: ceiling value, toxicity mechanism at excess, weight-based adjustments, clinical warning signs, separation rules, deployment phases
6. **Off-Label / Outside-Standard-of-Care Agents** — Table: Agent, Standard Use, DETOXXX Use, Off-Label Aspect, Primary Risk. Every agent requiring explicit informed consent beyond standard medical procedure consent.
7. **Phases Where Physician Must Be Actively Involved** — Phase-by-phase table with specific involvement requirements. Tier 3-4 non-negotiable rules.
8. **Three Sections Physician MUST Read Before Phase 3** — Safety-critical sections with interim authority note if Section 2 is missing
9. **Practitioner Responsibility Checklist** — 11-item documentation checklist
10. **Immediate Action Items From Audit** — Severity-ranked table of findings affecting physician decision-making

### Phase 7 — Write Deliverables to Disk

Use Python inline writes (NOT shell heredocs — `&` and `|` characters in DETOXXX content break heredocs):
```bash
python3 /dev/stdin << 'ENDPY'
content = """..."""
with open('/root/detoxxx_findings_replacements.md', 'w') as f:
    f.write(content)
ENDPY
```

Two output files:
1. `/root/detoxxx_findings_replacements.md` — All findings with replacement text
2. `/root/detoxxx_physician_brief.md` — Physician executive brief

Report final line/word/character counts with `wc -l -w -c` on both files.

### Common Pitfalls

- **PITFALL — Shell heredoc with DETOXXX content:** DETOXXX documents contain `&` characters (R&D, CD4+/CD8+, ADCC, etc.) that cause shell heredocs (`cat << 'EOF' ... EOF`, `python3 << 'PYEOF' ... PYEOF`) to fail. Use `python3 /dev/stdin << 'ENDPY'` instead. This pipes through stdin and avoids the `&` parsing issue entirely.

- **PITFALL — Handbook too large for read_file:** At 38K lines / 4.4MB, the assembled handbook exceeds all read_file limits. Use grep/sed targeted extraction exclusively. Map section boundaries first, then sed-extract specific ranges.

- **PITFALL — Missing Section 2 creates 142 dead cross-references:** When Section 2 (Clinical Safety) is missing from the body, every cross-reference to it in the handbook is dead. The physician brief must serve as interim safety authority until Section 2 is rebuilt.

- **PITFALL — Section 5.1 Herxheimer duplication:** The assembled handbook may contain 6+ competing copies of the Herxheimer Survival Algorithm. The most architecturally complete version includes: Bridge Box, seven checkpoints (Brain Fog, Headache, BP, Fever, GI, Myalgia, Platelets — each with four-grade action matrix), iNOS-mediated vasodilatory shock protocol, Phase-by-Phase Herx risk table, and dual clinical vignettes.

- **PITFALL — Silver ppm discrepancy across sections:** Section 5.4 (Tactical Protocol) specifies 5-10 ppm. Section 8 (Synergistic Pathways) may reference 10-50 ppm. Section 5.4 is authoritative — the Tactical Protocol is the operational authority. Flag the discrepancy and correct Section 8.

- **PITFALL — CDS absolute ceiling buried:** The 80 ml/day CDS ceiling (the single most important safety number in the CDS protocol) may appear only once in a dosing table. It must be promoted to prominent HARD GATE position in at minimum: (1) the CDS safety block before first dose, (2) the contraindications section, and (3) the Phase 4 grid notes.

### Proven Scan Results (2025-06-07 Audit)

The 12-parallel-scan approach against the 38,294-line handbook produced:

| Scan | Hits | Key Findings |
|:---|:---|:---|
| Structure Mapping | Section boundaries at lines 163-175, 184, 789, 806, 1330, 1347, 4418, 14688, 14696, 18026, 18876, 18982, and duplicate at 19310+ | 2 concatenated copies; Sections 2, 9, 10 have zero body content |
| Section 5.1 Duplicates | 12 hits (6 per copy) | 6 competing versions with different grading systems |
| Dead Cross-Refs | 142 total, 36 to Section 2.1 | Every cross-ref to Section 2 is a dead link |
| Vague Symptoms | ~50 hits across both copies | "may cause" language in safety-critical contexts |
| Undefined Labels | ~60 hits | "manifests as" without sensory specificity |
| Weasel Words | Heavy duplication — 6 copies each of Grade 1-4 Herxheimer tables | "transient" undefined, "self-limiting" without duration |
| Depletion Manifests | 6 instances (3 per copy) | GSH/mitochondrial/mucosal depletion described with identical vague language |
| Clinical Abstractions | "mood dysregulation", "sleep fragmentation", "neural circuit reconfiguration" | No operational definitions, no differential from primary pathology |
| Dose Ceilings | CDS ceiling at 1 location; silver ppm at 2 conflicting locations | Critical safety numbers buried or conflicting |

# Directive 16 + 17 Execution Pattern — Hardening + Field Cards

Proven June 2026 against the 38,294-line / 638K-word DETOXXX V2 Master Handbook. Use when the user asks to execute Directive 16 (harden against human error), Directive 17 (build operator field cards), or both together.

## Phase 1 — Source Ingestion

1. Fetch the master handbook from Drive via rclone: `rclone cat "gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md"`
2. If Drive is unreachable (OAuth expiration), fall back to local cache at `/opt/hermes/detoxxx_v2/DETOXXX_V2_MASTER_HANDBOOK.md`
3. Verify line/word/byte counts: `wc -l -w -c`
4. Load companion skills: `detoxxx-writing`, `protocol-handbook-authoring`, `google-workspace`

## Phase 2 — Structure Mapping

Map the handbook with targeted grep:

```bash
grep -n "^## " handbook.md | head -80        # H2 headers
grep -n "^# Section " handbook.md              # Section boundaries
grep -n "^# 5\." handbook.md                   # Tactical protocol starts
```

Extract critical sections with sed:

```bash
sed -n 'START,ENDp' handbook.md               # Tier definitions
sed -n 'START,ENDp' handbook.md               # MVS stacks
sed -n 'START,ENDp' handbook.md               # Triage / contraindications
```

## Phase 3 — Directive 16 Hardening Gap Scan

Run these targeted diagnostic scans on the assembled handbook OR on individual section files:

```bash
# 1. DON'T SKIP anchors (should be >0 in every file)
grep -c "DON'T SKIP\|DO NOT SKIP" *.md

# 2. Checklists — checkbox format (should be >0 in procedural sections)
grep -c "^- \[ \]" *.md

# 3. Bridge boxes (should be >=1 in every narrative section)
grep -c "Bridge Box\|What This Means" *.md

# 4. Hard gates (should be >=1 in every safety-relevant section)
grep -c "HARD GATE\|SEQUENCE MANDATE\|NON-NEGOTIABLE" *.md

# 5. Numbered multi-step sequences (indicates procedural content that needs checklists)
grep -c "^[0-9]\. " *.md
```

**Critical finding from June 2026 audit:** The handbook had zero DON'T SKIP anchors and zero checklists across all 45 section files, despite having excellent hard gate content and mechanism density. This is the universal hardening gap.

## Phase 4 — Per-Section Hardening Audit

For each section, produce:

1. **Gap list**: Which hardening elements are missing (anchors, checklists, callout boxes, summary tables, bridge boxes, hard gates)
2. **Specific anchor text**: The exact `> **[STOP] DON'T SKIP THIS — ...** ` blockquote to insert at the top
3. **Specific callout text**: The exact lethal warning callout box for that section's failure mode
4. **Checklist design**: What the checkbox items should be for multi-step sequences
5. **Priority assignment**: Immediate (safety-critical) vs This Week (usability) vs Next Week (polish)

## Phase 5 — Directive 17 Field Card Template

Every tier field card MUST contain these 7 elements:

### 1. [STOP] WHO SHOULD NOT RUN THIS PROTOCOL

Table: Contraindication | Mechanism of Exclusion. Pull from Section 9.1 absolute contraindications (RED LANE) + tier-specific additions from Section 3.6 case archetypes. Include mechanism column for every entry.

### 2. [CHECKLIST] MINIMUM LAB SET

Table: Lab | Required Threshold | If Below Threshold. Pull from Section 3.2 phase gates + Section 9.4 organ function modifiers. For Tier 3/4, include specialty labs (provoked urine metals, CIRS panel, D-dimer/fibrinogen). Include escalation rules for each abnormal result.

### 3. HERXHEIMER DECISION TREE

ASCII art decision tree condensed from Section 5.1. Format: vital signs assessment -> grade assignment -> per-grade action (continue/pause/stop/ER). Include tier-specific ER thresholds (Tier 3 has STRICTER thresholds than Tier 2; Tier 4 has MOST SENSITIVE thresholds).

### 4. [STOP] ER TRIGGERS — CALL 911 IMMEDIATELY

Checklist format (`- [ ]` items). Pull from:
- Section 5.1 Herxheimer Grade 4 criteria
- Section 5.1 Decision Checkpoints
- Section 1 Immediate Stop Criteria
- Add tier-specific triggers (e.g., Tier 4 adds "ANY neurological worsening", "ANY bleeding")

Include the ER COMMUNICATION SCRIPT inline — exact text the patient/caregiver should speak to the ER physician.

### 5. MVS-ONLY SCHEDULE

Time-gridded tables per phase: Time | Agent | Dose | Notes/Rules. Pull from Section 3.5 MVS columns. For Tier 3/4, pull from Section 3.6 phase modifications. Format rules:
- Bold timing-critical entries (e.g., "Day 43: COLLOIDAL SILVER HARD STOP")
- Add a "Non-Negotiable?" or "CRITICAL RULES" column
- For Tier 4, note "50% starting dose" on every table

### 6. "IF YOU MUST CUT, DO IT IN THIS ORDER" SIDEBAR

Per-phase ordered list: #1 is first to cut, last entry is NEVER CUT. Rationale for each never-cut agent. Pull from Section 3.5 MVS vs GSS distinctions — MVS agents are generally never-cut.

### 7. SUMMARY CARD

Compact reference table: Who this is for, what you take, what you DON'T take, duration, physician requirement, hardest phase, most common error, ER threshold. One-liner answers optimized for terrified first-read.

## Phase 6 — Implementation Priority Table

After audit, produce a combined Directive 16+17 implementation priority table:

| Priority | Action | Section(s) | Type |
|---|---|---|---|
| 1 (Immediate) | ... | ... | D16/D17 |
| 2 (This Week) | ... | ... | D16/D17 |
| 3 (Next Week) | ... | ... | D16/D17 |

Immediate items are safety-critical: ER card inserts, triage checklist conversion, lethal warning callout boxes, field card insertions. This-week items are usability: anchors, checklists, summary tables. Next-week items are polish: sidebar insertions, laminated card specs, cross-reference QA.

## Phase 7 — Deliverable Format

Write the complete audit + field cards as a single markdown file:

```
/opt/hermes/detoxxx_v2/DIRECTIVE_16_17_HARDENING_FIELD_CARDS.md
```

Structure:
```
# DIRECTIVE 16 + 17 — Title
## Audit metadata (date, handbook stats)

# PART 1: DIRECTIVE 16 — HARDEN AGAINST HUMAN ERROR
## Universal Gaps (table)
## Per-Section Hardening Audit (Section 1, 3, 4, 5.x, 8.x, 9.x, 10-13)
## Hardening Implementation Priority Order (table)

# PART 2: DIRECTIVE 17 — OPERATOR FIELD CARDS
## Field Card 1: Tier 1 (7 elements)
## Field Card 2: Tier 2 (7 elements)
## Field Card 3: Tier 3 (7 elements)
## Field Card 4: Tier 4 (7 elements)

# APPENDIX: IMPLEMENTATION PRIORITY — DIRECTIVE 16 + 17 COMBINED
```

## File Writing — Shell Heredoc Pitfall

**Do NOT use shell heredocs** (`cat > file << 'EOF'`) for this content. The field cards contain:
- `&` characters (acronyms like `TNF-alpha & IL-6`, `D-dimer & fibrinogen`)
- Pipe characters (`|`) in tables
- Backticks in code blocks

Shell heredocs will reject `&` with "Foreground command uses '&' backgrounding." Use `python3 << 'PYEOF'` with a raw string variable assignment instead:

```python
python3 << 'PYEOF'
content = r'''...full markdown content...'''
with open('/opt/hermes/detoxxx_v2/FILE.md', 'w') as f:
    f.write(content)
PYEOF
```

This pattern is reliable for markdown with any special characters. It also allows post-write verification (wc, grep, stat) in the same Python block.

## Upload

Upload to Google Drive immediately per `detoxxx-writing` upload mandate. Use OAuth token at `/root/.hermes/google_token.json`. If OAuth is expired (`RefreshError: invalid_grant`), fall back to local cache — the file at `/opt/hermes/detoxxx_v2/` is authoritative until OAuth is refreshed.

## Proven Numbers (June 2026 Audit)

- Handbook: 38,294 lines, 638,566 words, 4.6 MB
- Sections scanned: 45 individual section files
- Hard gate density: 434 matches across handbook
- Bridge box coverage: present in 33/45 section files (73%)
- DON'T SKIP anchors: ZERO (0/45)
- Checklists: ZERO (0/45)
- Field cards generated: 4 (Tiers 1-4), each with 7 elements
- Deliverable: 877 lines, 7,028 words, 42,479 bytes

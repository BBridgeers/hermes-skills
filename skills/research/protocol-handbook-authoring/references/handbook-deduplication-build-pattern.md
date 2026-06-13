# Handbook Deduplication & Clean Build Pattern

Proven 2026-06-08 against the DETOXXX V2 Master Handbook. Reduces 19,147-line concatenated mess to 13,956-line clean handbook (27-37% reduction).

## The Problem

Master handbooks assembled by concatenating multiple independent generation runs produce massive duplication:
- Section 5.1 (Herxheimer) appears 6 times
- PILLAR 3 appears twice (full and partial duplicates)
- PILLAR 6 appears 4 times (one full duplicate block spanning ~2,000 lines)
- Individual section files are clean but the concatenated master is not

## The Pattern

**Build from individual section files, NOT from the concatenated master.**

### Step 1: Inventory individual files

```bash
ls /opt/hermes/detoxxx_v2/section_*.md Section_*_Merged.md
```

Clean individual files (no duplication) typically exist at:
- `section_1_front_matter.md`
- `section_3_protocol_architecture.md`
- `section_4_master_daily_grids.md`
- `section_5_N_*.md` (10 subsections)
- `section_8_N_*.md` (9 subsections) or `Section_8_Merged.md`
- `section_9_N_*.md` or `Section_9_Merged.md`
- `section_10_N_*.md` or `Section_10_Merged.md`
- `section_11_N_*.md` (operational appendices)
- `section_12_az_index.md`
- `section_13_advanced_notes.md`

### Step 2: Pick best version when duplicates exist

For Section 5.1 (Herxheimer), 6 competing versions exist. Selection criteria:
- **Mechanism density** (count named enzymes/pathways — CYP2E1, GPx, GST, etc.)
- **Bridge Box quality** (household metaphor present? actionable?)
- **Clinical vignettes** (present? real failure arcs?)
- **Voice consistency** (Resonate Protocol Architect voice?)

In the 2026-06-08 run, `section_5_1_herxheimer_survival_algorithm.md` was chosen (175 lines, 43KB, 12 mechanism mentions) — identical to `deepseek_native` and `glm51_attempt2` in size/density.

### Step 3: Extract pillars from master with deduplication

Pillars 1-6 exist in the concatenated master but not as individual files. Extract from master:

```python
# PILLAR 1: unique, extract from first header to next DETOXXX header
p1_start = master.find('\n# PILLAR 1 —')
p1_end = master.find('\n# DETOXXX V2 PROTOCOL HANDBOOK', p1_start + 1)
pillar1 = master[p1_start:p1_end]

# PILLAR 3-6: extract each from first occurrence to first occurrence of next pillar
# PILLAR 6 has a FULL duplicate block at ~line 12710 — crop before it
p6_first = master.find('\n# PILLAR 6 —')
p6_dup = master.find('\n# PILLAR 6 —', p6_first + 500)  # ~1958 lines later
# Keep only master[p6_first:p6_dup], discard master[p6_dup:section7_pos]
```

### Step 4: Add section headers

Individual section files (Section_8_Merged.md, etc.) often lack `# Section N` H1 headers. After assembly, verify:

```bash
grep -c '^# Section ' handbook.md  # Should return 13
```

Insert missing headers at section boundaries. Use the approved titles from detoxxx-writing:
- Section 1: Preface & Protocol Overview
- Section 8: Synergistic Pathways & Agent Interactions
- Section 9: Personalization & Case Triage
- Section 10: Tracking, Labs & Progress Monitoring

### Step 5: Verify

```python
# All 13 sections present
for n in range(1, 14):
    assert f'# Section {n}' in clean

# All 6 pillars present (PILLAR 2 may be placeholder)
for n in range(1, 7):
    assert f'PILLAR {n}' in clean

# No H1 duplication
from collections import Counter
h1s = Counter(re.findall(r'^# (PILLAR \d)', clean, re.MULTILINE))
for p, c in h1s.items():
    assert c <= 2, f"{p} appears {c}x — dedup failed"
    # 2x is acceptable (taxonomy preamble + overview header — structural)
```

## Quality Signal: PILLAR 6 Dedup Check

PILLAR 6 is the most-duplicated section. After dedup, it should have exactly 2 H1 headers (taxonomy + overview), NOT 4. If 4 headers remain, the full duplicate block at ~line 12710 was not cropped.

## Output

The clean handbook from this pattern:
- 13,956 lines / 1.54 MB (down from 19,147 / 2.27 MB)
- 27-37% reduction depending on how many individual files are available
- All cross-references resolve (no dead links to non-existent sections)
- All 13 sections with proper H1 headers

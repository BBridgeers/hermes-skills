# Handbook Deduplication — Python Extraction Pattern

**Proven:** June 8, 2026. Deduplicated the 19,147-line DETOXXX_V2_MASTER_HANDBOOK.md (2.27 MB) down to 12,555 lines (1.44 MB) — 37% reduction, 6,592 lines removed.

## Root Cause

The master handbook was assembled by concatenating multiple independent generation runs. Section 5.1 (Herxheimer) appeared 6 times. PILLAR 3 appeared twice. PILLAR 6 appeared 4 times. The individual section files (`section_5_*.md`, `Section_8_Merged.md`, etc.) were clean — only the concatenated master had the duplication.

## Correct Approach: Build From Clean Individual Files

Do NOT attempt to deduplicate the concatenated mess. Instead, build the clean handbook from individual section files:

```python
import os, re

base = '/opt/hermes/detoxxx_v2'

def read_file(path):
    with open(path) as f:
        return f.read()

with open(os.path.join(base, 'DETOXXX_V2_MASTER_HANDBOOK.md')) as f:
    master = f.read()

parts = []

# Header (title + TOC before Section 3)
section3_pos = master.find('\n# Section 3 —')
parts.append(master[:section3_pos].strip())

# Section 1 — from individual file
parts.append('\n\n---\n\n')
parts.append(read_file(os.path.join(base, 'section_1_front_matter.md')).strip())

# Section 5 — Pick best Herxheimer version (longest, most mechanism-dense)
parts.append('\n\n---\n\n# Section 5 — Tactical Protocols\n')
parts.append('\n' + read_file(os.path.join(base, 'section_5_1_herxheimer_survival_algorithm.md')).strip())
for sub in ['5_2_pulse_dosing', '5_3_cds_protocol', ...]:
    parts.append('\n\n---\n\n')
    parts.append(read_file(os.path.join(base, f'section_{sub}.md')).strip())

# Section 6 — Extract UNIQUE pillar content from master
# Find first occurrence of each pillar H1, extract to next pillar or Section 7
p_first = {}
for m in re.finditer(r'^# PILLAR (\d)', master, re.MULTILINE):
    pnum = m.group(1)
    if pnum not in p_first:
        p_first[pnum] = m.start()

section7_pos = master.find('\n# Section 7 —')
pn = sorted([int(p) for p in p_first if p != '1'])

for i, pnum in enumerate(pn):
    pnum_str = str(pnum)
    start = p_first[pnum_str]
    end = p_first[str(pn[i+1])] if i+1 < len(pn) else section7_pos
    
    # For PILLAR 6: cut before the duplicate block
    if pnum_str == '6':
        dup_start = master.find('\n# PILLAR 6 — HALOGENS', start + 500)
        if dup_start > 0:
            content = master[start:dup_start].strip()
            # dup_start to end is the duplicate — skip it
    
    parts.append('\n\n---\n\n' + content)

# Sections 8-13 from merged individual files
for fname in ['Section_8_Merged.md', 'Section_9_Merged.md', 'Section_10_Merged.md']:
    parts.append('\n\n---\n\n' + read_file(os.path.join(base, fname)).strip())
```

## Key Findings From Deduplication

- **Section 2 (Clinical Safety & Risk Mitigation):** 88 cross-references, never generated. Placeholder needed.
- **PILLAR 2 (Viral Persistence):** 4 cross-references, never generated.
- **Herxheimer 5.1:** 6 competing versions. Keep the longest (survival_algorithm, 43KB, 12 mechanism mentions).
- **PILLAR 6 quadruplication:** Full 3,936-line duplicate block removed.
- **PILLAR 3 duplication:** 96K-char partial duplicate removed.

## Quality Signal For Version Selection

When multiple versions of the same section exist, pick by:
1. Mechanism density (count named enzymes, pathways, bond chemistry mentions)
2. Not line count — size alone doesn't indicate quality
3. Presence of hard gates, bridge boxes, clinical vignettes, cross-references

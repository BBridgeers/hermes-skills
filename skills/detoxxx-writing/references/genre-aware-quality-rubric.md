# Genre-Aware Quality Rubric & Automated Audit Script

The 7-point quality rubric (Bridge Box, Hard Gates, Dual-Lane, Three Choke Points, Clinical Vignette, Cross-References, Tables) was designed for Section 8-style biochemical pathway narrative writing. Applying it to all Handbook sections produces false negatives that waste audit time on non-gaps.

## Genre Categories

### Category A — Biochemical Pathway Narrative (Sections 2, 5, 8, 11)
**Full 7-point rubric applies.** Every file must score 7/7. Phase Compatibility Tables and Contraindications tables are REQUIRED for all Section 5 tactical protocols. Missing any marker = genuine gap to fix.

### Category B — Clinical Decision Support (Sections 9 — Personalization)
**Modified rubric.** The Dual-Lane requirement is satisfied by Bridge Box at the top + technical body below, NOT by requiring `### Plain Language` / `### Technical` headers. Kimi K2.6's pattern (Bridge Box → technical body with tables) is architecturally valid. Markdown table syntax (`|:---|`) is preferred but list-format data tables are acceptable when structurally complete. Quality markers: Bridge Box, Hard Gates, Three Choke Points, Clinical Vignettes, Cross-References. Phase Compatibility and Contraindications tables are NOT required here.

### Category C — Operational Templates (Section 10 — Tracking)
**Operational rubric, not pathway rubric.** Quality markers: Hard Gates (safety thresholds), lab reference ranges with units, actionable "if X, then Y" guidance, printable formatting, CPT codes, ICD-10 codes, insurance coding tips. Bridge Boxes and Cross-References are nice-to-have additions. Three Choke Points, Clinical Vignettes, Dual-Lane headers, and Phase Compatibility tables are NOT applicable — do not flag their absence as gaps.

### Category D — Pillar Chapters (Section 6)
**Pillar 6 standard.** Full tissue destination maps, redox window tables, cross-pillar co-dependency sections. Tissue Destination Maps require Primary Metabolic Block column.

## Automated Quality Scan Script

Copy this execute_code block to audit any set of DETOXXX Handbook files. It scans all 7 markers plus named enzyme count per file:

```python
import os, re

base = '/opt/hermes/detoxxx_v2'
all_files = sorted([f for f in os.listdir(base) if f.endswith('.md') and not f.startswith('Section_')])

results = []
for fname in all_files:
    fpath = os.path.join(base, fname)
    with open(fpath) as f:
        content = f.read()
    
    lines = content.count('\n')
    words = len(content.split())
    
    has_bridge = bool(re.search(r'Bridge Box.*What This Means', content))
    has_hard_gate = bool(re.search(r'HARD GATE|SEQUENCE MANDATE|NON-NEGOTIABLE|ABSOLUTE CONTRA', content))
    has_dual_lane = bool(re.search(r'### Plain Language', content)) and bool(re.search(r'### Technical', content))
    has_choke_points = bool(re.search(r'Three Choke Points|1\.\s*Glutathione System.*2\.\s*Mitochondrial', content, re.DOTALL))
    has_vignette = bool(re.search(r'Clinical Vignette', content))
    has_cross_refs = bool(re.search(r'Cross-References', content))
    has_table = bool(re.search(r'\|:---\|', content))
    
    enzyme_count = len(re.findall(r'CYP\d|TLR\d|NF-κB|NLRP\d|GPx|GST|iNOS|COX-\d|MMP-\d|STAT\d|mTOR|PPAR|Complex [IVX]+|kinase|reductase|synthase', content))
    score = sum([has_bridge, has_hard_gate, has_dual_lane, has_choke_points, has_vignette, has_cross_refs, has_table])
    
    # Genre detection
    is_section_10 = fname.startswith('section_10_')
    is_section_9 = fname.startswith('section_9_')
    genre = 'Template' if is_section_10 else ('DecisionSupport' if is_section_9 else 'Pathway')
    
    results.append({**locals(), 'file': fname, 'score': score, 'enzymes': enzyme_count})

# Print with genre-aware interpretation
print(f"{'File':<50} {'Type':<15} {'Ln':>5} {'Wrds':>6} B H D C V X T Sc Enz")
for r in results:
    print(f"{r['file']:<50} {r['genre']:<15} {r['lines']:>5} {r['words']:>6} "
          f"{'✓' if r['has_bridge'] else '✗'} {'✓' if r['has_hard_gate'] else '✗'} "
          f"{'✓' if r['has_dual_lane'] else '✗'} {'✓' if r['has_choke_points'] else '✗'} "
          f"{'✓' if r['has_vignette'] else '✗'} {'✓' if r['has_cross_refs'] else '✗'} "
          f"{'✓' if r['has_table'] else '✗'} {r['score']:>2} {r['enzymes']:>3}")

# Genre-aware gap analysis
print(f"\n{'File':<50} {'Genre':<15} {'Score':>5} {'Real Gaps'}")
for r in results:
    gaps = []
    if r['genre'] == 'Template':
        # Only Hard Gates are critical for templates
        if not r['has_hard_gate']: gaps.append('HardGate')
        if not r['has_bridge']: gaps.append('Bridge(NICE)')
        if not r['has_cross_refs']: gaps.append('CrossRef(NICE)')
    elif r['genre'] == 'DecisionSupport':
        # Bridge Box, Hard Gates, Choke Points, Vignettes, Cross-Refs matter
        if not r['has_bridge']: gaps.append('Bridge')
        if not r['has_hard_gate']: gaps.append('HardGate')
        if not r['has_choke_points']: gaps.append('Choke')
        if not r['has_vignette']: gaps.append('Vignette')
        if not r['has_cross_refs']: gaps.append('CrossRef')
        # Dual-Lane and Tables are nice-to-have for Decision Support
        if not r['has_dual_lane']: gaps.append('DualLane(NICE)')
        if not r['has_table']: gaps.append('Table(NICE)')
    else:
        # Full 7-point rubric for Pathway genre
        if not r['has_bridge']: gaps.append('Bridge')
        if not r['has_hard_gate']: gaps.append('HardGate')
        if not r['has_dual_lane']: gaps.append('DualLane')
        if not r['has_choke_points']: gaps.append('Choke')
        if not r['has_vignette']: gaps.append('Vignette')
        if not r['has_cross_refs']: gaps.append('CrossRef')
        if not r['has_table']: gaps.append('Table')
    
    if gaps:
        print(f"{r['file']:<50} {r['genre']:<15} {r['score']:>5}/7 ⚠️ {', '.join(gaps)}")
    else:
        print(f"{r['file']:<50} {r['genre']:<15} {r['score']:>5}/7 ✅")
```

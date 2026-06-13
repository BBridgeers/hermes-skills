#!/usr/bin/env python3
"""Section 4 Master Daily Grids — Operational Audit Script.
Proven May 22, 2026 — caught silver-NAC co-administration conflict at 11:00.
Usage: python3 section4-operational-audit.py [filepath]"""

import re, sys

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/hermes/detoxxx_v2/section_4_master_daily_grids.md'
with open(path) as f:
    content = f.read()

lines = content.split('\n')
phase_ranges = {1:(1,10), 2:(11,21), 3:(22,35), 4:(36,56), 5:(57,70), 6:(71,82), 7:(83,90)}

issues, warnings = [], []

# Pass 1: Phase day ranges
for p, (start, end) in phase_ranges.items():
    m = re.search(rf'## 4\.{p}.*?Days (\d+)[–-](\d+)', content)
    if m:
        s, e = int(m.group(1)), int(m.group(2))
        if s != start or e != end:
            issues.append(f"Phase {p}: Days {s}-{e} — expected {start}-{end}")

# Pass 2: CDS taper
if 'Day 65' not in content or 'ZERO' not in content:
    issues.append("CDS taper: Day 65 zero point not confirmed")

# Pass 3: Silver window
silver_stops = len(re.findall(r'Day 43.*[Ss]ilver|[Ss]ilver.*Day 43|HARD STOP.*[Ss]ilver|[Ss]ilver.*HARD STOP', content))
if silver_stops < 2:
    warnings.append(f"Silver hard stop Day 43: only {silver_stops} references")

# Pass 4: ALA Q3H
ala_refs = len(re.findall(r'ALA.*Q3H|Q3H.*ALA', content))
if ala_refs < 10:
    warnings.append(f"ALA Q3H: only {ala_refs} references")

# Pass 5: Structural elements per phase
for p in range(1, 9):
    p_start = content.find(f'## 4.{p} ')
    p_end = content.find(f'## 4.{p+1} ') if p < 8 else len(content)
    section = content[p_start:p_end] if p_start >= 0 else ''
    
    has_obj = 'Primary Objective' in section
    has_pillars = 'Active Pillar' in section
    has_totals = 'Daily Totals' in section or 'MVS Daily Totals' in section
    has_checkpoint = 'Checkpoint' in section or 'Red Flag' in section
    
    missing = []
    if not has_obj: missing.append('Objective')
    if not has_pillars: missing.append('Pillars')
    if not has_totals and p < 8: missing.append('Totals')
    if not has_checkpoint and p <= 5: missing.append('Checkpoint')
    if missing:
        warnings.append(f"Phase {p}: missing {', '.join(missing)}")

# Pass 6: Silver-NAC conflict
nac_lines = [l for l in lines if 'NAC' in l and ('silver' in l.lower() or 'Silver' in l)]
silver_lines = [l for l in lines if 'Colloidal Silver' in l and '|' in l]
if nac_lines and silver_lines:
    # Extract times
    nac_times = set()
    for l in nac_lines:
        parts = l.split('|')
        if len(parts) > 1:
            t = parts[1].strip().replace('**','').replace('*','')
            if ':' in t: nac_times.add(t)
    silver_times = set()
    for l in silver_lines:
        parts = l.split('|')
        if len(parts) > 1:
            t = parts[1].strip().replace('**','').replace('*','')
            if ':' in t: silver_times.add(t)
    
    for st in silver_times:
        st_hr = int(st.split(':')[0])
        for nt in nac_times:
            nt_hr = int(nt.split(':')[0])
            diff = abs(st_hr - nt_hr)
            if diff < 4 and diff > 0:
                issues.append(f"Silver-NAC proximity: silver at {st}, NAC at {nt} — only {diff}h gap (need 4h)")
            elif diff == 0:
                issues.append(f"CRITICAL: Silver and NAC at same time {st} — 4h separation violated")

# Report
print(f"Section 4 Audit: {path}")
print(f"Lines: {len(lines)}")
print(f"Hard Gates: {len(re.findall(r'HARD GATE|SEQUENCE MANDATE|NON-NEGOTIABLE', content))}")
print(f"🛑 markers: {content.count(chr(0x1F6D1))}")

if issues:
    print(f"\n❌ ISSUES ({len(issues)}):")
    for i in issues: print(f"  • {i}")
if warnings:
    print(f"\n⚠️ WARNINGS ({len(warnings)}):")
    for w in warnings: print(f"  • {w}")
if not issues and not warnings:
    print("\n✅ No issues found")

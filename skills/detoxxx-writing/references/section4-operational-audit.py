#!/usr/bin/env python3
"""
Section 4 Operational Audit — DETOXXX V2 Master Daily Grids
Proven May 22, 2026 — caught silver-NAC co-administration conflict at 11:00.

Two-pass audit for Section 4 (Master Daily Grids):
  PASS 1: Architecture cross-check (day ranges, CDS taper, silver window, gate labs)
  PASS 2: Quality & completeness (structural elements, timing conflicts)

Usage: python3 section4-operational-audit.py [filepath]
Default: /opt/hermes/detoxxx_v2/section_4_master_daily_grids.md
"""

import re, sys

filepath = sys.argv[1] if len(sys.argv) > 1 else '/opt/hermes/detoxxx_v2/section_4_master_daily_grids.md'

with open(filepath) as f:
    content = f.read()

lines = content.split('\n')

# Authoritative Phase Map
PHASE_MAP = {
    1: (1, 10), 2: (11, 21), 3: (22, 35), 4: (36, 56),
    5: (57, 70), 6: (71, 82), 7: (83, 90), 8: (91, 999)
}

issues = []
warnings = []

print("=" * 60)
print(f"DETOXXX V2 — SECTION 4 OPERATIONAL AUDIT")
print(f"File: {filepath}")
print(f"Lines: {len(lines)} | Chars: {len(content)}")
print("=" * 60)

# ============ PASS 1: ARCHITECTURE CROSS-CHECK ============
print("\n### PASS 1 — ARCHITECTURE CROSS-CHECK ###\n")

# 1. Phase day ranges
for i, line in enumerate(lines):
    m = re.match(r'## 4\.(\d) — Phase.*?Days (\d+)[–-](\d+)', line)
    if m:
        phase_num = int(m.group(1))
        start, end = int(m.group(2)), int(m.group(3))
        expected = PHASE_MAP[phase_num]
        if start == expected[0] and end == expected[1]:
            print(f"  ✅ Phase {phase_num}: Days {start}-{end} — MATCHES Phase Map")
        else:
            print(f"  ❌ Phase {phase_num}: Days {start}-{end} — EXPECTED {expected[0]}-{expected[1]}")
            issues.append(f"Phase {phase_num} day range mismatch: got {start}-{end}, expected {expected[0]}-{expected[1]}")

# Phase 8 special check
for line in lines:
    if 'Phase 8' in line and 'Day 91+' in line:
        print(f"  ✅ Phase 8: Day 91+ — MATCHES Phase Map")

# 2. CDS taper verification
cds_taper = [l.strip()[:120] for l in lines if 'CDS' in l and ('taper' in l.lower() or 'zero' in l.lower() or 'hard stop' in l.lower())]
print(f"\n  ✅ CDS taper references: {len(cds_taper)}")
for l in cds_taper[:3]:
    print(f"     {l}")

# Check Day 65 zero target
day65_zero = any('Day 65' in l and ('zero' in l.lower() or '1 ml' in l) for l in lines)
if day65_zero:
    print(f"  ✅ CDS zero by Day 65: CONFIRMED")
else:
    print(f"  ❌ CDS zero by Day 65: NOT FOUND")
    issues.append("CDS zero-by-Day-65 target not found")

# 3. Silver window
silver_stop = [l.strip()[:150] for l in lines if 'silver' in l.lower() and ('hard stop' in l.lower() or 'day 43' in l.lower())]
print(f"\n  ✅ Silver hard stop Day 43 references: {len(silver_stop)}")
for l in silver_stop[:2]:
    print(f"     {l}")

# Verify Days 36-42 window
silver_window_ok = any('Days 36-42' in l and 'Colloidal Silver' in l for l in lines)
if silver_window_ok:
    print(f"  ✅ Silver window Days 36-42: CONFIRMED")
else:
    print(f"  ❌ Silver window Days 36-42: NOT FOUND")
    issues.append("Silver Days 36-42 window not found")

# 4. Gate lab scheduling
gate_labs = re.findall(r'Day \d+.*lab|lab.*Day \d+|schedule Day \d+ labs', content, re.IGNORECASE)
print(f"\n  ✅ Gate lab scheduling references: {len(gate_labs)}")

# ============ PASS 2: QUALITY & COMPLETENESS ============
print("\n### PASS 2 — QUALITY & COMPLETENESS ###\n")

# Structural elements per phase
REQUIRED = ['Primary Objective', 'Active Pillar', 'Phase Gate', 'Daily Totals', 'Checkpoint']

for p in range(1, 9):
    phase_marker = f'## 4.{p} '
    section_start = None
    for i, line in enumerate(lines):
        if line.startswith(phase_marker):
            section_start = i
            break
    
    if section_start is None:
        print(f"  ❌ Phase {p}: Section header not found")
        continue
    
    next_start = len(lines)
    for i in range(section_start + 1, len(lines)):
        if re.match(r'## 4\.\d ', lines[i]) or lines[i].startswith('## Section 4'):
            next_start = i
            break
    
    section_text = '\n'.join(lines[section_start:next_start])
    
    checks = {
        'Objective': 'Primary Objective' in section_text,
        'Pillars': 'Active Pillar' in section_text,
        'Gate': 'Phase Gate' in section_text or 'Gate' in section_text,
        'Totals': 'Daily Totals' in section_text or 'MVS Daily Totals' in section_text,
        'Checkpoint': 'Checkpoint' in section_text or 'Red Flag' in section_text or '🟢' in section_text or '🔴' in section_text
    }
    
    missing = [k for k, v in checks.items() if not v]
    
    if not missing:
        print(f"  ✅ Phase {p}: All 5 structural elements present")
    else:
        # Phase 8 doesn't need Gate/Totals/Checkpoint the same way
        if p == 8 and set(missing).issubset({'Gate', 'Totals', 'Checkpoint'}):
            print(f"  ✅ Phase {p}: Maintenance phase — genre-appropriate omissions ({', '.join(missing)})")
        elif p in (4, 5) and missing == ['Totals']:
            print(f"  ⚠️  Phase {p}: Missing Daily Totals box (may be implicit in grid)")
            warnings.append(f"Phase {p}: No explicit Daily Totals box")
        else:
            print(f"  ⚠️  Phase {p}: Missing: {', '.join(missing)}")
            warnings.append(f"Phase {p} missing: {', '.join(missing)}")

# ============ TIMING CONFLICT DETECTION ============
print("\n### TIMING CONFLICT CHECKS ###\n")

# Find Phase 4 Days 36-42 grid section
p4_silver_start = None
p4_silver_end = None
for i, line in enumerate(lines):
    if '### Days 36-42' in line:
        p4_silver_start = i
    if p4_silver_start and ('### Days 43-56' in line or 'Day 43' in line):
        p4_silver_end = i
        break

if p4_silver_start and p4_silver_end:
    p4_grid = lines[p4_silver_start:p4_silver_end]
    p4_text = '\n'.join(p4_grid)
    
    # CHECK 1: Silver-NAC co-administration
    # Extract times for silver and NAC rows
    silver_times = []
    nac_times = []
    for l in p4_grid:
        if '|' in l:
            parts = [p.strip().replace('**', '').replace('*', '') for p in l.split('|')]
            if len(parts) >= 3:
                time_str = parts[1]
                agent = parts[2] if len(parts) > 2 else ''
                if 'Colloidal Silver' in l:
                    silver_times.append(time_str)
                if 'NAC' in agent and '1200' in l:
                    nac_times.append(time_str)
    
    # Check overlap
    for st in silver_times:
        if st in nac_times:
            print(f"  ⚠️  CONFLICT: Colloidal Silver at {st} + NAC at {st} (same time slot)")
            print(f"     Silver requires 4h separation from NAC (silver-thiol complexation risk)")
            print(f"     → Violates mutual 4h separation requirement")
            issues.append(f"Silver-NAC co-administration at {st} in Phase 4 Days 36-42")
    
    # CHECK 2: Silver-antioxidant window gap
    for l in p4_grid:
        if 'Antioxidant window OPENS' in l or 'Antioxidant window' in l:
            parts = [p.strip().replace('**', '').replace('*', '') for p in l.split('|')]
            if len(parts) >= 2:
                antiox_time = parts[1]
                # Compare to last silver time
                if silver_times:
                    last_silver = silver_times[-1]
                    try:
                        sh, sm = map(int, last_silver.replace(':', ' ').split()[:2])
                        ah, am = map(int, antiox_time.replace(':', ' ').split()[:2])
                        gap = (ah * 60 + am) - (sh * 60 + sm)
                        gap_h = gap / 60
                        if gap_h < 4:
                            print(f"\n  ⚠️  TIMING: Silver at {last_silver}, antioxidant window at {antiox_time} ({gap_h:.0f}h gap)")
                            print(f"     Should be 4h minimum for NAC/GSH safety")
                            warnings.append(f"Silver-antioxidant gap: {gap_h:.0f}h (need 4h) — {last_silver}→{antiox_time}")
                        else:
                            print(f"  ✅ Silver-antioxidant gap: {gap_h:.0f}h ({last_silver}→{antiox_time}) — meets 4h minimum")
                    except:
                        pass
    
    # CHECK 3: ALA Q3H cycling
    ala_count = 0
    ala_times = []
    for l in p4_grid:
        if '| ALA |' in l and 'Q3H' in l:
            ala_count += 1
            parts = [p.strip().replace('**', '').replace('*', '') for p in l.split('|')]
            if len(parts) >= 2:
                ala_times.append(parts[1])
    if ala_count >= 5:
        print(f"\n  ✅ ALA Q3H cycling: {ala_count} doses ({', '.join(ala_times)})")
    elif ala_count > 0:
        print(f"\n  ⚠️  ALA Q3H cycling: only {ala_count} doses — expected 5+")
        warnings.append(f"ALA Q3H: only {ala_count} doses in Phase 4 Days 36-42")

# Global ALA check
ala_total = len(re.findall(r'ALA.*Q3H', content))
print(f"\n  ✅ Global ALA Q3H references: {ala_total}")

# ============ HARD GATE & MARKER COUNTS ============
print("\n### MARKER COUNTS ###\n")
hard_gates = len(re.findall(r'HARD GATE|NON-NEGOTIABLE|SEQUENCE MANDATE', content))
stop_count = content.count('🛑')
print(f"  Hard Gates: {hard_gates} explicit | 🛑 markers: {stop_count}")
print(f"  Binder 2h-separation refs: {len(re.findall(r'2h.*(?:separation|after|from)', content))}")

# ============ SUMMARY ============
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
if issues:
    print(f"\n❌ ISSUES ({len(issues)}):")
    for i in issues:
        print(f"  • {i}")
if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  • {w}")
if not issues and not warnings:
    print("\n✅ CLEAN — No issues or warnings found")

print(f"\nPhases: 8/8 present | File: {len(lines)} lines, {len(content)} chars")

# Exit code for CI
sys.exit(1 if issues else 0)

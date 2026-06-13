#!/usr/bin/env python3
"""
Handbook Structural Audit — automated quality analysis for markdown protocol handbooks.
Detects: duplicate sections, wall-of-text blocks, voice violations, missing L1/L2/L3 markers,
WHAT/WHY separation, tableless sections, section ordering issues.
Output: diagnostic report to stdout plus structured findings.

Usage: python3 scripts/handbook-structural-audit.py <handbook.md> [--full]
  --full: also run Directive 9 (WHAT/WHY) and wall-of-text scans (slower on 19K+ line files)
"""

import re, sys, os

def audit(filepath, full=False):
    with open(filepath) as f:
        content = f.read()
        lines = content.split('\n')

    findings = []

    # --- SECTION HEADER COUNTS (duplicate detection) ---
    header_counts = {}
    header_lines = {}
    for i, line in enumerate(lines, 1):
        m = re.match(r'^(#{1,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            key = f"H{level}: {title}"
            header_counts.setdefault(key, 0)
            header_lines.setdefault(key, [])
            header_counts[key] += 1
            header_lines[key].append(i)

    dupes = {k: v for k, v in header_counts.items() if v > 1}
    findings.append(('DUPLICATE_SECTIONS', len(dupes), dupes))

    # --- L1/L2/L3 PROGRESSIVE LAYER MARKERS ---
    l1 = sum(content.count(s) for s in ['L1 SCAN', 'L1:', 'SCAN LAYER'])
    l2 = sum(content.count(s) for s in ['L2 READ', 'L2:', 'READ LAYER'])
    l3 = sum(content.count(s) for s in ['L3 STUDY', 'L3:', 'STUDY LAYER'])
    findings.append(('PROGRESSIVE_LAYERS', {'L1': l1, 'L2': l2, 'L3': l3, 'total': l1+l2+l3}))

    # --- STRUCTURAL MARKERS ---
    markers = {
        'dual_lane_bridge': len(re.findall(r'Dual-Lane Purpose|Bridge Box|What This Means', content)),
        'clinical_vignettes': len(re.findall(r'Clinical Vignette', content)),
        'three_choke_points': len(re.findall(r'Three Choke Points', content)),
        'hard_gates': len(re.findall(r'HARD GATE|SEQUENCE MANDATE|NON-NEGOTIABLE|ABSOLUTE CONTRA', content)),
    }
    findings.append(('STRUCTURAL_MARKERS', markers))

    # --- VOICE VIOLATIONS ---
    violations = {}
    filler_phrases = ['interestingly', 'fascinatingly', 'importantly,', 'research suggests',
                      'studies show', 'it is worth noting', 'it should be noted', 'it is important to']
    for phrase in filler_phrases:
        count = len(re.findall(re.escape(phrase), content, re.IGNORECASE))
        if count > 0:
            violations[phrase] = count
    findings.append(('VOICE_VIOLATIONS', violations))

    # --- OUT-OF-ORDER SECTION DETECTION ---
    # Find all numbered sections (e.g. "5.10", "5.1", "11.6") and check if they're sequential
    section_numbers = []
    for i, line in enumerate(lines, 1):
        m = re.match(r'^#\s+(\d+\.\d+)', line)
        if m:
            section_numbers.append((i, m.group(1)))
    
    ordering_issues = []
    seen_prefix = {}
    for ln, num in section_numbers:
        prefix = num.split('.')[0]
        parts = num.split('.')
        if len(parts) == 2:
            minor = int(parts[1])
            if prefix in seen_prefix:
                prev_minor = seen_prefix[prefix]
                if minor < prev_minor:
                    ordering_issues.append((ln, num, f"preceded by {prefix}.{prev_minor}"))
            seen_prefix[prefix] = minor
    findings.append(('OUT_OF_ORDER_SECTIONS', ordering_issues))

    if full:
        # --- WALL-OF-TEXT DETECTION ---
        wall_of_text = []
        current_wall = 0
        wall_start = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('|') or \
               stripped.startswith('-') or stripped.startswith('>') or stripped.startswith('```'):
                if current_wall > 20:
                    wall_of_text.append((wall_start, i-1, current_wall))
                current_wall = 0
                wall_start = i
            else:
                if current_wall == 0:
                    wall_start = i
                current_wall += 1
        findings.append(('WALL_OF_TEXT', wall_of_text))

        # --- WHAT/WHY SEPARATION ---
        what_why_separated = []
        for i, line in enumerate(lines, 1):
            if re.match(r'^###\s+\d', line):
                chunk = '\n'.join(lines[i:min(i+30, len(lines))])
                has_dosing = bool(re.search(r'(?i)dos(e|ing)|ml\s|drop|mg\s|ppm', chunk))
                has_mechanism_early = bool(re.search(r'(?i)mechanism|CYP\d|receptor|pathway|enzyme', chunk[:500]))
                if has_dosing and not has_mechanism_early:
                    what_why_separated.append((i, line.strip()))
        findings.append(('WHAT_WHY_SEPARATED', what_why_separated))

        # --- SECTIONS WITHOUT TABLES ---
        no_table_sections = []
        current_section = "PREAMBLE"
        has_table = False
        section_start = 1
        for i, line in enumerate(lines, 1):
            if re.match(r'^##\s+', line):
                if not has_table and current_section != "PREAMBLE":
                    no_table_sections.append((section_start, current_section))
                current_section = line.strip()
                section_start = i
                has_table = False
            if '|' in line and '---' in line:
                has_table = True
        if not has_table:
            no_table_sections.append((section_start, current_section))
        findings.append(('SECTIONS_WITHOUT_TABLES', no_table_sections))

    return findings


def report(filepath, findings):
    total_lines = sum(1 for _ in open(filepath))
    total_chars = os.path.getsize(filepath)

    print(f"# Handbook Structural Audit: {os.path.basename(filepath)}")
    print(f"Lines: {total_lines} | Size: {total_chars:,} bytes")
    print()

    for category, data in findings:
        if category == 'DUPLICATE_SECTIONS':
            print(f"## DUPLICATE SECTIONS: {data} unique headers appear 2+ times")
            for key, count in sorted(data.items(), key=lambda x: x[1] if isinstance(x, tuple) else 0):
                if isinstance(key, tuple):
                    key, count = key
                if count > 1:
                    # data is actually dupes dict
                    pass
            for key, count in sorted(data.items(), key=lambda x: -x[1]):
                print(f"  [{count}x] {key}")

        elif category == 'PROGRESSIVE_LAYERS':
            d = data
            print(f"## PROGRESSIVE LAYERS")
            print(f"  L1 SCAN:  {d['L1']}")
            print(f"  L2 READ:  {d['L2']}")
            print(f"  L3 STUDY: {d['L3']}")
            status = "ABSENT" if d['total'] == 0 else "PARTIAL" if d['total'] < 20 else "PRESENT"
            print(f"  STATUS: {status}")

        elif category == 'STRUCTURAL_MARKERS':
            print(f"## STRUCTURAL MARKERS")
            for k, v in data.items():
                print(f"  {k}: {v}")

        elif category == 'VOICE_VIOLATIONS':
            print(f"## VOICE VIOLATIONS: {sum(data.values())} occurrences")
            for phrase, count in data.items():
                print(f"  '{phrase}': {count}")

        elif category == 'OUT_OF_ORDER_SECTIONS':
            print(f"## OUT-OF-ORDER SECTIONS: {len(data)}")
            for ln, num, detail in data[:20]:
                print(f"  Line {ln}: #{num} ({detail})")

        elif category == 'WALL_OF_TEXT':
            print(f"## WALL-OF-TEXT BLOCKS (>20 consecutive lines): {len(data)}")
            for start, end, count in data[:10]:
                print(f"  Lines {start}-{end} ({count} lines)")

        elif category == 'WHAT_WHY_SEPARATED':
            print(f"## WHAT/WHY SEPARATED (dosing before mechanism): {len(data)}")
            for ln, title in data[:15]:
                print(f"  Line {ln}: {title[:90]}")

        elif category == 'SECTIONS_WITHOUT_TABLES':
            print(f"## SECTIONS WITHOUT TABLES: {len(data)}")
            for ln, title in data[:15]:
                print(f"  Line {ln}: {title[:90]}")

        print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 handbook-structural-audit.py <handbook.md> [--full]")
        sys.exit(1)
    filepath = sys.argv[1]
    full = '--full' in sys.argv
    findings = audit(filepath, full=full)
    report(filepath, findings)

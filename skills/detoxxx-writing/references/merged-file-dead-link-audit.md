# Merged File Dead Link Audit

May 21, 2026: Section_2_merged.md was found to have 5 of 12 subsections missing (2.6, 2.7, 2.8, 2.11, 2.12). Section 2.5 cross-referenced 2.6 six times — each a dead link pointing a user in Herx crisis to nothing.

## Root Cause
Individual subsection files existed as separate .md files in the Section 2 Drive folder but were never concatenated into the merged document. The merged file was assembled from a subset of available files.

## Detection
```bash
# Extract all cross-references from merged file
grep -oP 'Section \d+\.\d+' Section_2_merged.md | sort | uniq -c | sort -rn

# Verify each referenced section exists in merged file
for i in $(seq 1 12); do
  grep -q "# 2.$i " Section_2_merged.md && echo "2.$i ✅" || echo "2.$i ❌ MISSING"
done
```

## Fix
1. Download missing individual files from Drive
2. Locate insertion points in merged file (search for section headers)
3. Rebuild merged file with ALL sections concatenated in order
4. Re-verify all 12 sections present
5. Re-upload to Drive

## Prevention
Before shipping any merged section file, run the dead link audit. A section that says "go to Section X.Y" while X.Y doesn't exist is not a formatting issue — it is a life-safety failure. Users in medical crisis follow those links.
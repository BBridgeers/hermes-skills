# Section 8 V2 Remap Methodology

## Problem
Section 8 Synergistic Pathway files were written against V1 phase names (Gut Terrain, Hepatic Detox, Chelation, Immune Recalibration, Mitochondrial, Neurological, Biofilm Disruption, Maintenance). The locked DETOXXX V2 Phase Map uses different names and day ranges. Section 8.7's Phase Compatibility Table explicitly listed old phase names, making it impossible to cross-reference with Section 3 and Section 4.

## Remap Procedure (May 22, 2026)

### For Each Section 8 File

1. **Add V2 Phase Architecture annotation** — insert immediately after the title line, before Dual-Lane Purpose:
```markdown
**V2 Phase Architecture:** [concise mapping of pathway stages to V2 phases with day ranges]
```

2. **Use authoritative V2 Phase Map** — Phase 1: Drainage & Terrain Prep (D1-10), Phase 2: Foundation & Microbiome (D11-21), Phase 3: Mobilization & Parasite Strike I (D22-35), Phase 4: Intensive Strike (D36-56), Phase 5: Deep Tissue & CNS (D57-70), Phase 6: Biological Restoration (D71-82), Phase 7: Consolidation (D83-90), Phase 8: Perpetual Maintenance (D91+).

3. **For 8.7 specifically** — completely rewrite the Phase Compatibility Table. Old V1 columns (Phase 1 Gut Terrain, etc.) become V2 Phase | Days | CDS Compatibility | CS Compatibility | Notes. Each row must include day ranges and deployment specifics.

4. **For 8.8 specifically** — map the 4-stage biofilm cascade to V2 phase day ranges (Stage 1=Phases 2-3, Stage 2=Phase 4, Stage 3=Phases 4-5, Stage 4=Phases 5-7).

5. **Do NOT change body content** — the biochemistry, Bridge Boxes, clinical vignettes, and Three Choke Points are at Pillar 6 density. Only phase labels need updating.

### Verification
- Every file has `V2 Phase Architecture:` annotation
- 8.7 Phase Compatibility Table uses V2 names with day ranges
- No remaining V1 phase names (Gut Terrain, Hepatic Detox, Immune Recalibration, etc.) in phase-labeling context
- Cross-references verified (Section 3.1 for Phase Map, Section 4 for daily grids)

### File Locations
- Local: `/opt/hermes/detoxxx_v2/section_8_*.md`
- Drive: Section 8 folder ID `1sKapymGrrEeA6q-Qvg3_s6i82JVd3RcF`
- Uploaded via OAuth inline Python with `MediaIoBaseUpload` (update-in-place for existing files)

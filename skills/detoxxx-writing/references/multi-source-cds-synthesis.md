# Multi-Source CDS Synthesis Workflow

Pattern proven on Section 5.3 (CDS Full Protocol Specification, May 22, 2026). Use when synthesizing tactical protocol sections from multiple EPUB/PDF-derived source documents stored in Google Drive.

## Source Identification

CDS/Kalcker-class source files live in the Drive folder `Chlorine Dioxide_Collodial Silver & Monotomic Gold` (ID: `1EJMANkdpdUOTnqDrD7PC2cUnLKIKscb7`). Key filenames:

| File | Format | Line Count | Content Type |
|---|---|---|---|
| The Essentials protocol guide CDS (Andreas Kalcker).md | Markdown | 2,267 | Full Kalcker protocol guide — all protocols A-Z, preparation, dosing, routes, safety |
| Chlorine Dioxide (Jean Pierre Wenger).md | Markdown | 315 | Historical/contextual — limited operational data. Mostly philosophical framing. |
| PHD VETTED CHLORINE DIOXIDE RESEARCH.txt | Plaintext | 236 | Academic mechanism depth, toxicity studies, peer-reviewed citations |
| DEEP_RESEARCH_OUTPUT.md | Markdown | 1,123 | Comprehensive synthesis of CDS research across multiple sources |
| DETOXXX_V2_Phase_Map_Executive_Brief.md | Markdown | 468 | Phase-specific CDS deployment architecture (Drive: `1zFrD5DEiL1cl-CDBEW8FcugZZa5Dqk2b`) |
| HERMES_WAVE_EXECUTION_AUDIT_NOTES.md | Markdown | 3,568 | Redox window tables, CDS failure modes, separation rules, example daily schedules |
| Training_Course_CDS.pdf | PDF | N/A | 3.3MB — full CDS training course. Convert with pandoc if needed. |

## Extraction Pattern — Large Files (100K+ chars)

The Audit Notes (3,568 lines, 205KB) exceed read_file limits. Use grep/sed for targeted extraction:

```bash
# 1. Find all references to a section number
grep -n "5\.3\|CDS\|Chlorine Dioxide" /path/to/AUDIT_NOTES.md

# 2. Extract a line range once you know the boundaries
sed -n 'START_LINE,END_LINEp' /path/to/AUDIT_NOTES.md

# 3. For Kalcker guide (2,267 lines) — find protocol sections by header
grep -n "^#\|Protocol C\|Protocol F\|Protocol S\|Protocol K\|Protocol E\|Protocol R\|Protocol L\|Protocol G\|How to Prepare\|3000 ppm\|0,3%" /path/to/Kalcker.md

# 4. Read target sections with read_file(offset, limit)
read_file(path="/tmp/cds_sources/Kalcker_CDS_Guide.md", offset=794, limit=80)  # Protocol C
read_file(path="/tmp/cds_sources/Kalcker_CDS_Guide.md", offset=1994, limit=120) # Preparation
```

## Synthesis Decision Points

When source documents disagree, resolve with these heuristics (validated on Section 5.3):

### Activator preference (HCl vs Citric Acid)
- **Kalcker**: Prefers HCl 4% over citric acid. Citric acid produces Citrobacter-feeding sodium citrate residue and intestinal acidosis. Acceptable for CDS gas-transfer preparation only (acid doesn't enter final solution), NOT for direct CD ingestion.
- **Phase Map**: Doesn't specify activator.
- **Resolution**: Follow Kalcker's clinical preference. HCl 4% is the standard; citric 50% is fallback for CDS prep only.

### Antioxidant separation window
- **Kalcker**: "Wait at least four hours before antioxidant juices or, better yet, avoid them altogether." Also says 2 hours in some sections.
- **Phase Map**: Minimum 1-hour separation, preferred 4 hours. "CDS and antioxidants are mutually antagonistic at the biochemical level — co-administration results in complete mutual cancellation."
- **Audit Notes**: 4 hours for Vitamin C, Glutathione, NAC, H2O2. 2 hours for ALA, Curcumin.
- **Resolution**: Use the strictest standard — 4 hours for strong antioxidants (Vit C, GSH, NAC), 2 hours minimum for weaker ones (ALA, curcumin). The Phase Map's "complete mutual cancellation" language governs.

### Dose ceilings
- **Kalcker**: Protocol C: 10 ml/day standard, 30 ml severe, 80 ml critical. Protocol F: 8 ml in 2 hours maximum.
- **Phase Map**: CDS taper to zero by Day 65. Phase 6+ OFF.
- **Resolution**: Kalcker doses for the operational ceiling; Phase Map for phase windows. Both compatible.

### Emergency neutralization (Vitamin C vs Baking Soda)
- **Kalcker**: "Use only baking soda and never vitamin C (ascorbic acid) as previously recommended... If vitamin C is taken, the acid reacts with sodium chlorite and spontaneously produces chlorine dioxide gas, which is undesirable."
- **Audit Notes**: Activated charcoal 1000mg for CDS overdose.
- **Resolution**: Both are correct for different scenarios. Baking soda neutralizes ClO₂ chemically (immediate). Activated charcoal binds residual CDS in GI tract (prevent further absorption). NEVER use Vitamin C for CDS neutralization — it generates MORE ClO₂ gas from residual chlorite.

## Tone Stripping — Kalcker Source

The Kalcker guide contains extensive philosophical/rhetorical framing, personal anecdotes, and "beginner/course" tone that must be stripped before protocol integration:

**Strip**: Autobiographical content, firefighter analogies, antioxidant industry criticism, conspiratorial framing, "I have decided to follow my conscience" passages, dosage encouragement ("don't worry too much"), taste-masking tips (Coca-Cola, rice milk), non-medical testimonials, spiritual content.

**Keep**: Activation chemistry, protocol specifications (A-Z), dosing tables, preparation procedures, route descriptions, safety precautions, contraindications, weight-based dosing formulas, emergency procedures, storage requirements, concentration verification methods, material compatibility (glass vs PET vs metal).

**Rule**: If a sentence does not contain a number, a named chemical, a route specification, a safety rule, or a mechanism statement, it's probably framing — strip it.

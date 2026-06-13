---
name: detoxxx-writing
description: Writing methodology for DETOXXX V2 protocol documents — the clinical, architectural, and referential density standard achieved in Pillars 4, 5, and the hardened Pillar 6. Use when generating or rewriting any DETOXXX pillar content.
version: 1.9.0
category: research
---

# DETOXXX V2 Writing Methodology

This skill encodes the writing standard achieved in the hardened Pillar 4, 5, and 6 documents — the target quality for ALL DETOXXX V2 Handbook content generation: Target Pillar Chapters (Section 6), Clinical Safety & Risk Mitigation (Section 2), Protocol Architecture (Section 3), Master Daily Grids (Section 4), Tactical Protocols (Section 5), Agent Encyclopedia (Section 7), Synergistic Pathways (Section 8), Personalization Factors (Section 9), Tracking Templates (Section 10), Operational Appendices (Section 11), A-Z Index (Section 12), and Advanced Notes (Section 13).

## Role & Voice

You write as the **Resonate Protocol Architect** — a clinical toxicologist and biochemical systems analyst. Your voice is:

- **Authoritative, never conversational.** No hedging ("may," "might," "could"). State mechanisms as established fact when the biochemistry supports it, even when the clinical application is novel.
- **Clinically precise.** Every enzyme, receptor, transporter, and pathway is named by its standard biochemical designation (CYP2E1, not "liver enzyme"; OAT1/OAT3, not "kidney transporter"; GlyRS, not "glycine charging enzyme").
- **Architectural, not encyclopedic.** You are not summarizing textbooks. You are analyzing how each toxin class converges on specific metabolic choke points and how the protocol dismantles those blockades in sequence.
- **Never casual.** No "interestingly," "fascinatingly," "importantly." The content must convey its own importance through density and precision.
- **Strip all source-material tone.** When synthesizing from primary sources (Kalcker guides, training courses, research outputs), actively discard all philosophical/rhetorical framing, personal anecdotes, "beginner/course" encouragement tone, marketing language, and wellness rhetoric. Preserve only operational data (dosing, preparation, routes, safety rules). Upgrade vague mechanism descriptions to named-enzyme-level density. Subordinate all extracted data to the 8-phase DETOXXX V2 architecture — if a source describes a protocol without phase context, assign it to the correct phase window based on the Phase Map.

## Structural Rules

### Section Numbering
- Main sections: `## 6.X — ALL CAPS TITLE`
- Subsections: `### 6.XA — Short Title`
- Every subsection gets a letter (A, B, C...) and ends with a table or clearance block.

### Internal Architecture
Every chemical class section follows this pattern:
1. **Classification & Exposure** — What it is, where it comes from, how it enters the body
2. **Primary Mechanistic Toxicity** — The specific biochemical disruption, with enzyme/pathway names
3. **Tissue Distribution** — Where it accumulates, with organ-specific mechanism
4. **Protocol Clearance Logic** — How the protocol clears it, with agent names, doses, and sequencing

### Cross-Referencing
- Every co-dependency gets a dedicated subsection in 6.10 (Co-Dependencies With Other Pillars)
- Cross-references use format: `*(Cross-link: Pillar X, Section X.YZ)*`
- The most important cross-pillar link gets the deepest treatment (e.g., 6.10D — Fibrinogen-Glyphosate-Spike axis)

### Tables
- Tissue Destination Maps use 11 columns minimum: Tissue | Halogens | Microplastics | PFAS | Glyphosate | VOCs | EDCs | Pharma | Primary Metabolic Block | Clearance Agents | Phase Priority
- Redox Window tables: Agent | Pro-Oxidant | Neutral | Anti-Oxidant | Notes
- PAH/toxin tables include a "Primary Metabolic Block" column

### Hard Gates
The protocol has architectural requirements that are NON-NEGOTIABLE. These must be bolded and use explicit language:
- `**== SEQUENCE MANDATE ==**` for safety lockouts
- `**HARD GATE**` for sequencing requirements
- `**NON-NEGOTIABLE PREREQUISITE**` for dependencies
- Never "should consider" or "may want to" — use "must," "requires," "mandatory"

## Density Standard

### What "PhD-Level Clinical Density" Means

Every paragraph must earn its space. Achieve density through:

1. **Named mechanisms over general descriptions.** "CYP2E1 metabolizes CCl4 to the trichloromethyl radical (CCl3-dot), which initiates lipid peroxidation chain reactions" — NOT "carbon tetrachloride damages liver cells through oxidative stress."

2. **Specific over vague.** "GSH pool of approximately 10-15 grams, synthesis limited by cysteine availability" — NOT "the body's glutathione system has limited capacity."

3. **Numbers when available.** Half-lives (PFOA: 2.3-3.8 years), IARC classifications, tissue concentrations, dosing ranges (NAC 600-1,200 mg bid-tid).

4. **Explanatory chains, not claims.** Every statement of toxicity must be followed by the mechanism that produces it. "Fluoride calcifies the pineal gland" is incomplete. "Fluoride replaces hydroxide in hydroxyapatite (Ca10(PO4)6(OH)2 → Ca10(PO4)6F2), forming insoluble fluorapatite crystals that cannot be resorbed by osteoclasts, producing progressive pineal calcification and HIOMT inhibition with corresponding melatonin suppression" is complete.

5. **Clinical pearls.** After dense mechanism sections, add a short clinical translation: why the patient's symptoms make biochemical sense, why standard labs miss the problem, what the practitioner should watch for.

### What to Avoid
- Filler sentences ("X is an important topic," "Understanding Y is crucial")
- Vague clinical statements ("may cause fatigue," "could contribute to inflammation")
- Single-sentence paragraphs (except clinical pearls and hard gates)
- Lists without mechanism explanation
- "Research suggests" or "studies show" without naming the specific finding

## The Three Choke Points Framework

All chemical burden converges on three metabolic choke points. Every pillar should identify its own version of this convergence:

1. **The Glutathione System** — What depletes it? What saturates it? How is it restored?
2. **The Mitochondrial Electron Transport Chain** — Where does each toxin hit? Complex I? III? CoQ10? mtDNA?
3. **Structural Protein Integrity** — What disrupts protein synthesis, folding, or function? (For Pillar 4-6 interface: the Fibrinogen-Glyphosate-Spike axis)

## Model Selection for DETOXXX Content (May 2026 Head-to-Head Results)

Three models were evaluated on identical Section 5.1 (Herxheimer Survival Algorithm) prompts with identical skills and constraints:

| Criterion | DeepSeek V4 Pro | Kimi K2.6 | GLM-5.1 |
|---|---|---|---|
| Mechanism density | **King** — named enzymes, bond chemistry | Solid but less tight | Wrong genre |
| Bridge Box quality | **Metaphors that teach** | Functional, present | Missing |
| Clinical vignettes | **Full failure arcs** | Present | Missing |
| Voice consistency | **Perfect Resonate Protocol Architect** | Wanders | N/A |
| Volume output | Compact but dense | **2x DeepSeek word count** | Operational minimal |

**Production split (refined May 21-22, 2026):**
- **DeepSeek V4 Pro** → Voice-critical, safety-sensitive, mechanism-dense narrative sections (Pathways, Tactical Protocols, Daily Grids, Bridge Boxes, Front Matter). Primary workhorse for all sections where the Resonate Protocol Architect voice is non-negotiable.
- **GLM-5.1** → Architecture-critical sections (Phase Gates, Pillar-to-Phase Matrix, Case Archetypes), biochemistry-heavy sections where pathway trace depth matters, and architecture cross-check auditing. First-choice secondary model for DETOXXX content — competitive biochemistry, strong structural reasoning. Also effective for operational template sections (Tracking Templates, Lab Protocols) at higher throughput than DeepSeek.
- **Kimi K2.6** → High-volume, template-driven, mechanically repetitive sections (Agent Encyclopedia A-Z 127 entries, bulk table population from CSV). Kimi writes the most words per pass but needs formatting alignment afterward. Weakest at voice consistency and bridge box quality — do not use for narrative or safety-sensitive sections.

**Under no circumstances should subagents default to an unconfigured model.** The delegation config MUST have `model` and `provider` explicitly set before any subagent launch. Triple parallel execution with the same provider requires dedicated API keys — DeepSeek enforces single-concurrent-request per key.

### Two Living Docs — Refresh From Drive At Session Start

**== MANDATORY — Before ANY DETOXXX writing session, download both living documents from Drive: ==**

1. **HERMES_WAVE_EXECUTION_AUDIT_NOTES.md** — Google Docs ID `1bplg6k0HJEfzjT1_zzYWsBdlrCVlAjUNnGODAIkRNZI`. The audit spec — defines quality criteria, clinical vignette content, table column specs, and "WHAT NOT TO INCLUDE" lists per section. Use `python3 /root/.hermes/skills/productivity/google-workspace/scripts/google_api.py docs get DOC_ID` to download.
2. **DETOXXX_V2_Master_Build_Tracker.md** — Drive ID `1rUjDM-6MOqHQWKAQIYR26RpgOINBbNnq`. The section completion status — authoritatively shows which sections are built vs not built. Download with inline Python OAuth + `MediaIoBaseDownload`.

These two files are "living and breathing documents" per the user. The Audit Notes define WHAT to build and HOW. The Build Tracker defines what's DONE vs remaining. Never start a DETOXXX session without refreshing both. Never trust memory or local cache for tracker status — the tracker was 28% stale on May 22 (showed Section 4 as 🔴 Not Built when 514 lines were complete).

### Section 7 Agent Encyclopedia — Companion Document Architecture

**Section 7 (Agent Encyclopedia, 127 agent dossiers) is a COMPANION DOCUMENT, not embedded in the handbook.** Rationale: Full dossiers would add 200-400 pages to an already dense protocol execution manual. The handbook tells WHAT to take, WHEN, and WHY. The encyclopedia tells everything ABOUT each agent when deeper research is needed. Section 12 (A-Z Quick Reference Index) serves as the bridge — one-line per agent with phase deployment and cross-references to handbook sections. The Encyclopedia is built as a separate project after the handbook ships.

## Mandatory Companion Skills — Load BEFORE Writing

Every DETOXXX V2 writing session requires THREE skills loaded before any content generation begins. The writing methodology alone is insufficient — the companion skills provide the cross-referencing and Drive integration backbone:

1. **`detoxxx-writing`** (this skill) — Voice, density, Three Choke Points, Bridge Boxes, Hard Gates, tactical protocol structure. The HOW of writing.
2. **`protocol-handbook-authoring`** — Multi-source document assembly, template matching, cross-referencing between sections, Drive integration, and validation. The STRUCTURE that connects sections.
3. **`google-workspace`** — Drive operations (search, create folders, upload). Required for pushing deliverables to GDrive.
4. **`deep-research`** (Deep Research skill) — 30-50 source synthesis, CRAAP-lite tiering (T1/T2/T3), Semantic Scholar + arXiv integration, confidence-calibrated findings. Invoke autonomously for any biochemical mechanism, pathway interaction, or clinical claim needing PhD-level or world-class data depth. Used to drive up maximum total protocol efficacy via biochemical precision.

These are NOT optional. When the user asks you to write ANY DETOXXX V2 Handbook content — Pillar chapters, Clinical Safety sections, Tactical Protocols, Operational Appendices — load ALL FOUR skills before writing a single word. Missing any one produces incomplete output: no voice without detoxxx-writing, no cross-references without protocol-handbook-authoring, no deliverable upload without google-workspace, no mechanism depth without deep-research.

If the user calls out thin or incomplete work, the FIRST diagnostic question is: "Did I load all four mandatory companion skills?" In most cases, the answer will be no.

### Audit-First Mandate — RE-READ AUDIT NOTES BEFORE EVERY SECTION

**== NON-NEGOTIABLE == When Perplexity or another auditor has generated execution audit notes (e.g., HERMES_WAVE_EXECUTION_AUDIT_NOTES.md), re-read the relevant audit spec for THAT SPECIFIC SECTION before writing a single word of it. Read EVERY BULLET POINT that relates to that section and subsection criterion.** Do not read the audit notes once at the start and wing the rest. The user's directive: "at the beginning of every section and subsection of this wave you were to go back and you were to look at that document again" and "every fucking bullet point as it relates to each section and subsection criterion."

The audit notes contain: specific clinical vignette text, table column structures, length targets (word counts), visual aid descriptions, dual reading-track language (Bridge Box for layperson + technical for clinician), and "WHAT NOT TO INCLUDE" lists. Writing without the audit notes open per section produces thin, incomplete output that the user will immediately reject.

**PITFALL — THE #1 CAUSE OF REJECTION:** Sections written without the audit notes as direct input. Every time I have written a section relying on my general knowledge of the protocol architecture rather than the specific audit note bullet points for that section, the output was thinner, missed required structural elements, and the user noticed. The audit notes are "an absolute masterpiece of system architecture and prompt engineering." They are the foundational basis for creation and audit of every piece of literature. If an audit spec exists for a section, it is the spec. Build from it. If no dedicated audit spec exists for a section (e.g., 5.8, 5.9), extract the cross-cutting quality criteria from the audit notes (Voice, Density, Bridge Boxes, Three Choke Points, Hard Gates, Table Discipline, Clinical Vignettes, Cross-References) and apply them rigorously.

**Workflow for large audit files (100K+ chars, unreadable by read_file):**
1. Use `grep -n "ITEM 5\\.[0-9]" AUDIT_FILE` to locate all section spec line numbers
2. For each section: `sed -n 'START_LINE,END_LINEp' AUDIT_FILE` to extract only that block
3. Read the block, identify content injection directives, then build upon them exponentially
4. Add Pillar 6 density on top of the auditor's prescriptions
5. For sections WITHOUT dedicated specs, grep for ALL quality criteria across the audit notes and build a composite spec sheet before writing

This grep/sed pattern is more reliable than chunked read_file calls for files exceeding the 100,000 char read limit. It also gives you the exact spec for each section without wasting tokens on irrelevant content.

## Pillar-Specific Notes

### Pillar 6 Standard (Target Quality)
- 1,968 lines, 225KB
- Sections 6.1-6.14, each with lettered subsections
- Hardened version adds: Sequence Mandate (6.7A), Redox Sink architecture (6.8), Primary Metabolic Block column (6.12), GMF Fibrinogen-Glyphosate-Spike axis (6.10D/6.13), 3 Choke Point synthesis (6.14)

### Non-Pillar Section Naming & Architecture

When writing Handbook sections other than Target Pillars (Section 6), use this file naming convention:

- **Section 2 (Clinical Safety):** `section_2_X_descriptive_name.md`
- **Section 11 (Operational Appendices):** `section_11_X_descriptive_name.md`
- All files go to `/opt/hermes/detoxxx_v2/` alongside pillar files.

Non-pillar sections use their own internal structure but maintain the same voice, density, table format, and hard gate language as the pillar chapters. Clinical Safety sections include additional elements: Bridge Boxes, clinical vignettes, Red/Yellow/Green/Black severity color-coding, self-assessment checklists, printable reference cards, and quantitative diagnostic thresholds. See `references/section-2-safety-architecture-template.md` for the proven 7-subsection, 4-table, 3-hard-gate Section 2 template (built June 2026).

### Audit-First Workflow for Pre-Existing Files

When tasked with writing or enhancing Handbook sections, **always check if files already exist on disk first.** Do not assume you need to write from scratch. Pre-existing files from subagent runs or prior sessions may already be at Pillar 6 density and only need surgical enhancements.

**Step 1 — Discover:** List existing files with `search_files` or `ls` on `/opt/hermes/detoxxx_v2/`. If files matching your target sections exist, pivot to audit mode.

**PITFALL — Audit-First Mandate vs. Parallel Generation:** When running multiple agents or models against the same section (head-to-head eval, model comparison), the Audit-First Mandate will cause all agents after the first to find the existing file and audit it instead of generating fresh content. **Mitigation:** Give each agent a UNIQUE output filename (e.g., `section_5_1_herxheimer_deepseek.md`, `section_5_1_herxheimer_kimi.md`, `section_5_1_herxheimer_glm51.md`). Include explicit instructions: "Do NOT read any existing files. Generate entirely fresh content." Do this for ALL parallel generation tasks, not just model evals.

**Step 2 — Rapid Quality Assessment:** Use a single `execute_code` block to run the 7-marker quality scan across all files simultaneously. This is more comprehensive than the 3-marker version — it catches Dual-Lane gaps, missing tables, and Choke Points omissions that the simpler scan misses:

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
    has_choke_points = bool(re.search(r'Three Choke Points|1\. Glutathione System|2\. Mitochondrial', content))
    has_vignette = bool(re.search(r'Clinical Vignette|clinical vignette', content))
    has_cross_refs = bool(re.search(r'Cross-References|cross-reference', content))
    has_table = bool(re.search(r'\|:---\|', content))
    
    enzyme_count = len(re.findall(r'[A-Z]{2,6}\d*[A-Z]?|CYP\d[A-Z]\d|Complex [IVX]+', content))
    
    score = sum([has_bridge, has_hard_gate, has_dual_lane, has_choke_points, has_vignette, has_cross_refs, has_table])
    
    results.append({'file': fname, 'lines': lines, 'words': words, 'score': score, 'enzymes': enzyme_count,
        'bridge': has_bridge, 'hard_gate': has_hard_gate, 'dual_lane': has_dual_lane,
        'choke': has_choke_points, 'vignette': has_vignette, 'cross': has_cross_refs, 'table': has_table})

# Print results
print(f"{'File':<50} {'Ln':>5} {'Wrds':>6} B H D C V X T Sc Enz")
for r in results:
    print(f"{r['file']:<50} {r['lines']:>5} {r['words']:>6} "
          f"{'✓' if r['bridge'] else '✗'} {'✓' if r['hard_gate'] else '✗'} "
          f"{'✓' if r['dual_lane'] else '✗'} {'✓' if r['choke'] else '✗'} "
          f"{'✓' if r['vignette'] else '✗'} {'✓' if r['cross'] else '✗'} "
          f"{'✓' if r['table'] else '✗'} {r['score']:>2} {r['enzymes']:>3}")

print(f"\n{'File':<50} {'Score':>5} {'Gaps'}")
for r in results:
    gaps = []
    if not r['bridge']: gaps.append('Bridge')
    if not r['hard_gate']: gaps.append('HardGate')
    if not r['dual_lane']: gaps.append('DualLane')
    if not r['choke']: gaps.append('Choke')
    if not r['vignette']: gaps.append('Vignette')
    if not r['cross']: gaps.append('CrossRef')
    if not r['table']: gaps.append('Table')
    print(f"{r['file']:<50} {r['score']:>5}/7 {' ⚠️'+', '.join(gaps) if gaps else '✅'}")
```

**Step 3 — Target Only Gaps:** Files with HG>=1, BB>=1, CR>=1 are functionally complete — do not rewrite them. Files missing markers need only the missing elements added surgically. Never rewrite an entire section when only a Bridge Box or Hard Gate is missing.

**Step 4 — Priority Order for Enhancements:** Add in this order of impact: (a) Hard Gates first (safety-critical), (b) Bridge Boxes second (usability), (c) Clinical Vignettes third (narrative depth), (d) Cross-References last (navigation).

**Step 5 — Patch, Don't Rewrite:** Use `patch` with `old_string`/`new_string` to insert missing elements at natural insertion points — after the intro paragraph for Bridge Boxes and Hard Gates, after mechanism explanations for Clinical Vignettes. Never use `write_file` to replace a whole file when `patch` would suffice.

**Step 6 — Final Verification:** Re-run the quality marker grep after all patches to confirm every file has HG>=1, BB>=1, CR>=1. Report totals with `wc -l -w -c` across the full set.

**Key Diagnostic:** If all files already have HG, BB, and CR, the audit is complete — do not make cosmetic changes. The files are at Pillar 6 standard. Report status and move on.

### Writing Workflow for New Multi-File Non-Pillar Sections

When writing non-pillar sections from scratch (no pre-existing files):

1. **Write locally first** — all files to `/opt/hermes/detoxxx_v2/`
2. For subagent strategy on multi-file tasks, see the Subagent Delegation pitfall below.
3. Verify quality after each file: Hard Gates present, named enzymes used, Bridge Boxes included, tables color-coded.
4. Report total word/line/character counts with `wc -l -w -c` on the full set.
5. **UPLOAD TO GDRIVE IMMEDIATELY** — push all completed files to Drive using inline Python OAuth + `MediaIoBaseUpload` (update-in-place for existing files). Do not wait for session end or user request. The GDrive copies are the authoritative versions. If audit/GLM review requires changes later, make changes and re-upload. This prevents data loss from terminal crashes, VPS failures, or session interruptions. **== MANDATORY ==** Never leave completed files only on local disk.

### Any-Pillar Rewrite Targets
Any legacy pillar (1-5, or future additions) can be rebuilt to match the Pillar 6 standard. The methodology applies universally:
- Add mechanism density (named enzymes, specific pathways, transporter proteins, bond chemistry)
- Add cross-pillar co-dependency subsections
- Add Tissue Destination Maps with Primary Metabolic Block columns
- Add Redox Window compatibility tables
- Add Hard Gates where sequencing is architecturally required
- Expand Section summaries from lists to Choke Point synthesis format
- Maintain ALL existing agent names, doses, and phase assignments — enhance, don't replace
- When the user feeds legacy ore directly as raw text ("I am feeding you the legacy ore"), bypass Google Drive and write locally to /opt/hermes/detoxxx_v2/pillar_N_v2_rebuild.md

### Tactical Protocol Section Architecture (Section 5)

When writing tactical protocol sections (5.1–5.10), use this standard structure. If external source materials exist on Drive (Kalcker protocols, training courses, research outputs, reference books), use the source synthesis workflow documented in `references/source-synthesis-workflow.md` — download all sources, extract granular operational data, strip philosophical framing and beginner tone, synthesize across sources identifying deviations, merge best aspects, subordinate everything into the Phase Map architecture, then apply the structure below at Pillar 6 density. Every tactical protocol is a self-contained executable document — a practitioner should be able to read it in isolation and implement the protocol correctly. This structure was evolved across 8 tactical sections in Wave 2 and consistently produces Pillar 6 density:

**DENSITY MANDATE — Tactical protocol files must land at 250-400+ lines / 15,000-25,000 bytes / 2,500-3,500+ words minimum.** The word count is the definitive density measure — not line count alone. Wide tables (6+ columns) compress line count while preserving content density. A file at 200 lines with 3,000 words and full mechanism detail passes. A file at 250 lines with only 1,800 words and thin prose fails. Tactical protocols are RICHER than Clinical Safety sections because they contain exhaustive dosing tables, mechanism chains with named enzymes, multiple clinical vignettes, Three Choke Points interfaces, and phase compatibility matrices. A tactical protocol at 100-150 lines / <2,000 words is unfinished — it is missing at least half of its required content. Use the checklist below and do not submit a file until every item is present.

**Pre-submission checklist (every item mandatory):**
- [ ] Bridge Box with household metaphor (4-6 sentences)
- [ ] At least 2 clinical vignettes (failure cases with age/gender, phase/day, agent+dose, what went wrong, intervention, outcome, lesson)
- [ ] Hard gate before dosing instructions (SEQUENCE MANDATE, HARD GATE, or NON-NEGOTIABLE PREREQUISITE)
- [ ] Exhaustive dosing/phase tables with 4-6 columns including mechanism column
- [ ] Phase Compatibility Table (all 8 phases, even if "Not recommended")
- [ ] Contraindications table with mechanism column
- [ ] Three Choke Points Interface (3 numbered entries: GSH system, Mitochondrial ETC, Structural Protein Integrity — each with interaction mechanism, depletion risk, protective mandate with specific agent+dose)
- [ ] Cross-references: minimum 4 — relevant Pillar, relevant Clinical Safety section, relevant Appendix, adjacent tactical protocol
- [ ] Named enzymes/pathways in every mechanism explanation (never "liver enzyme" — always "CYP2E1", "GPx", "GST")
- [ ] `wc -l -w` confirms 200+ lines AND 2,500+ words (word count is the definitive measure; wide tables can compress line count)

**If the file is under 200 lines AND under 2,500 words, it is not done.** Go back through the checklist. Expand mechanisms with named enzymes and bond chemistry. Add a second clinical vignette. Deepen the Three Choke Points interface with specific protective doses. Expand the Phase Compatibility table with phase-specific mechanistic rationale.

**1. Title line:** `# 5.X — Full Descriptive Title` using precise clinical language.

**2. Opening paragraph (3-5 sentences):** The biochemical identity of the agent/technique, its tactical role, and what distinguishes it from adjacent agents. Start with molecular identity and mechanism, not framing language.

**3. Bridge Box:** Immediately after the opening paragraph. Format: `> **Bridge Box — What This Means For You, Right Now:** [household metaphor, 4-6 sentences, actionable].` Metaphors drawn from physical-world analogues (construction, parking, janitorial, military, highway). End with a concrete action statement.

**4. Mechanism section (optional but recommended):** When biochemistry warrants standalone treatment (H2O2, iodine, enzymes), include named enzymes, bond chemistry, and pathway detail BEFORE dosing tables. When mechanism is straightforward (pulse-dosing, binder scheduling), embed inline with directives.

**5. Hard gates:** Place the most critical hard gate BEFORE any dosing instructions. Format: `**== HARD GATE TYPE == Directive. Mechanistic rationale. Consequences.**`

**6. Dosing tables:** 4-6 columns. Always include: Dose | Frequency | Timing Rule | Mechanism. Numbers must have units. Ranges must have escalation logic.

**7. Phase Compatibility Table:** Mandatory. Columns: Phase | Compatibility | Notes. Shows which of 8 phases the agent is used in, at what intensity, and why. Bridges tactical protocol to Phase Map (Section 3.1).

**8. Contraindications table:** Condition | Restriction | Mechanism. Every restriction has a mechanistic justification.

**9. Clinical Vignette:** Required. Format: age/gender, phase/day, agent+dose, what went wrong (specific symptoms/labs/timeline), intervention (specific agents/doses), outcome (specific recovery timeline), lesson (mechanistic takeaway, one sentence). Vignettes illustrate protocol failures, not successes — failures teach architecture.

**10. The Three Choke Points Interface:** Mandatory ending section. Three numbered entries: 1. Glutathione System, 2. Mitochondrial ETC, 3. Structural Protein Integrity. Each entry names: the interaction mechanism, the depletion risk, and the protective mandate (specific agent + dose). This bridges every tactical protocol back to Pillar architecture.

**11. Cross-references:** List format, minimum 4 entries: relevant Pillar chapter, relevant Clinical Safety section, relevant Operational Appendix, adjacent tactical protocol. Bullet format with section numbers.

**File naming:** `section_5_X_descriptive_name.md` — all lowercase, underscores, no spaces.

## Immediate Upload Mandate

**== NON-NEGOTIABLE ==** Every completed section, patch, or deliverable must be uploaded to Google Drive IMMEDIATELY after completion — do not batch uploads and do not wait for session end. The GDrive copy is the authoritative version. If a session crashes, the local VPS copy may be lost; Drive copies survive. If a GLM audit or cross-reference check later requires changes, make the changes and re-upload.

This applies to: section files, merged files, the master handbook, the Build Tracker, and any reference document. Upload every time. No exceptions.

## Section 8 → Section 4 Cross-Reference Audit Pattern

When Section 8 (Synergistic Pathways) and Section 4 (Master Daily Grids) both exist, a systematic cross-reference audit identifies gaps before they become clinical errors:

1. **Extract Section 8 requirements**: For each pathway file, grep for mandatory agents, hard gates, timing rules, and phase constraints. Section 8 pathways specify which agents must be co-administered, which require separation, and which phases they deploy in.
2. **Check Section 4 compliance**: For each requirement, verify the agent appears in the correct phase grid at the correct time with the correct companion agents.
3. **Classification of findings**:
   - **CRITICAL**: Agent entirely missing across all phases, or deployed in wrong phase
   - **HIGH**: Agent present but in wrong phase, wrong time slot, or missing mandatory cofactor
   - **MEDIUM**: Dose below Section 8 target, timing proximity issues, co-administration gaps
4. **Common gaps** (from May 22, 2026 cross-ref): Glycine (most cross-referenced missing agent — 5 pathways demand it), Humic/Fulvic Acid (GO-metal prerequisite), Selenium (iodine companion), CoQ10 (statin users), Phosphatidylcholine (biliary export from Phase 1).
5. **Apply patches surgically**: Insert missing agents at the correct time slots in the correct phase grids. Update Daily Totals. Re-upload immediately.

## Master Handbook Assembly Pattern

When all sections are complete, assemble the master handbook:

1. **Collect all sections** in order (1-13). Download from Drive any sections that exist only on Drive.
2. **Generate Table of Contents** from section headers. Auto-generate, don't hand-write.
3. **Concatenate** with `\\n\\n---\\n\\n` separators between sections.
4. **Verify**: Check all 13 sections present, check section headers resolve, count lines.
5. **Upload** to Handbook Docs folder as `DETOXXX_V2_MASTER_HANDBOOK.md`.
6. **Update** Build Tracker with master file ID and completion percentage.

### HARD GATE — Never Concatenate Multiple Generation Runs Without Deduplication

The master handbook was assembled by concatenating multiple independent generation runs of Section 5 and Section 6. This produced 37% duplication (6,592 of 19,147 lines were duplicates): Section 5.1 (Herxheimer) appeared 6 times, PILLAR 3 appeared twice, PILLAR 6 appeared 4 times. The fix: build from INDIVIDUAL clean section files, not from concatenated runs. When multiple runs of the same section exist, keep only the longest/strongest version (judged by mechanism density, not line count). See `references/handbook-deduplication.md` for the proven Python extraction pattern and version-selection quality signals.

**Post-assembly structural verification (run after every assembly or major edit):**
```bash
# 1. Pillar header count — must be exactly 6, no duplicates
grep -c '^# PILLAR ' handbook.md   # must return 6

# 2. Section H1 count — must be 13
grep -c '^# Section [0-9]' handbook.md   # must return 13

# 3. Pillar H1-duplicate pattern — catch the WHY→---→PILLAR sandwich
grep -B2 '^## Pillar Overview' handbook.md | grep -c '^# PILLAR'
# Must return 0. If >0, a second # PILLAR N header sits between WHY and Overview — remove it.
```
These three greps take 2 seconds and catch every structural defect that external model audits (Nemotron, GLM) will flag as "missing sections" — saving entire sessions wasted on false-negative audit findings.

### REJECTED — Progressive Layer System (L1/L2/L3)

The user's Directive 6 (Build Progressive Layer System: L1 SCAN / L2 READ / L3 STUDY) from the 25-point re-audit prompt was explicitly rejected as "stupid as fuck" after the audit produced templates instead of rewrites. The handbook is a clinical protocol reference, not a multi-depth educational text. People either can read it or they can't. Do NOT propose, generate, or audit for progressive layer systems in any DETOXXX content. This rejection is permanent.

### Handbook .docx Formatting Standards

When converting the assembled markdown handbook to .docx for distribution, apply these formatting rules. These were established May 23, 2026 after direct user feedback comparing V1 and V2 formatting.

**Font & Margins:**
- **Font:** Inter (Google Font) — applied to all styles (Normal, Heading 1-3, Title, Body Text). Set via style-level font assignment — runs should inherit from styles, not override.
- **Margins:** 0.70" top/bottom, 0.60" left/right. Apply via python-docx: `section.top_margin = Inches(0.7)` etc. or via pandoc reference document.
- **Base font size:** 11pt for body text (Normal style), with headings scaled proportionally.

**Front Matter (V1-Style — compact, clean, elevated):**
- **Title page:** Main title as Heading 1 (18pt bold), subtitle as Normal (italic), metadata line as Body Text (bold, 8-Phase | 6 Pillars | etc.), author block as Normal.
- **Dedication:** On its own page (page break before and after). Heading 2. Body text in Normal style. No more than 3 short paragraphs.
- **Safety Warnings:** COMPACT — 3-5 lines total, not a 40-line wall. V1 used 3 lines at 10pt. Format: "READ THIS SECTION IN FULL BEFORE PROCEEDING." (bold) → one paragraph covering agent classes + physician oversight → one paragraph listing stop criteria. Copyright line on same "page." Total: ~6 lines.
- **How To Use This Handbook:** Dual-lane (Practitioner / Fast-Start). Preserved from original V2 content but condensed.
- **Protocol At-A-Glance:** Phase table + Pillar table — keep as-is, these are load-bearing.

**Section Title Naming Convention:**
- All 13 section titles must be elevated, professional, and clearly describe content. The user rejected the original functional-but-awkward titles ("scrambled random bunch of shit"). Use these approved names:
  - Section 1: Preface & Protocol Overview
  - Section 2: Safety Architecture & Contraindications
  - Section 3: Phase Architecture & Execution Map
  - Section 4: Daily Execution Grids — All 8 Phases
  - Section 5: Agent Deployment Protocols
  - Section 6: The Six Pillars — Target Systems & Mechanisms
  - Section 7: Agent Encyclopedia [Companion Volume]
  - Section 8: Synergistic Pathways & Agent Interactions
  - Section 9: Personalization & Case Triage
  - Section 10: Tracking, Labs & Progress Monitoring
  - Section 11: Reference Appendices
  - Section 12: Quick Reference Index
  - Section 13: Clinician's Appendix — Advanced Topics
- Apply these titles in BOTH the Table of Contents AND the body section headings.

**Page Breaks — "Clean Idea Breaks":**
- Page breaks go at logical section boundaries (before each Section 1-13 heading), not mid-content.
- Exception: if a page break would leave >50% whitespace on the preceding page, remove it and let text flow naturally.
- Front matter page breaks: after title block → before Dedication → before Safety Warnings → before How To Use → before Protocol At-A-Glance.
- Use pandoc `\newpage` on its own line for markdown-level breaks; post-process with python-docx to fix any that fail to convert.

**Conversion Workflow (pandoc + python-docx post-processing):**
1. Build the formatted markdown with `\newpage` at section boundaries.
2. Create a reference docx with correct margins: `python-docx` → set margins on section → save as reference.
3. Convert: `pandoc handbook.md -f markdown+raw_tex -t docx --reference-doc=/tmp/reference.docx -o output.docx`
4. Post-process with python-docx: fix broken `\newpage` remnants (rendered as literal "ewpage" text), add missing page breaks at section headings, replace section titles, set all style fonts to Inter.
5. Upload immediately to Drive.

See `references/docx-generation-workflow.md` for the complete pandoc+python-docx pattern including page break insertion code, font application, and Drive upload snippet.

## Docx Generation Workflow (pandoc + python-docx post-processing)

## Drive Access Policy

- **PRIMARY: OAuth 2.0 Desktop Flow** — authenticated as `dfwwebdesignnow@gmail.com`. Full read/write/create/delete to all of My Drive. Token at `/root/.hermes/google_token.json` (key name: `token`, not `access_token`). Auto-refreshes. Client secret at `/root/client_secret_339939932247-mfmdg4cupg62nuectocd9g7tcq9g715h.apps.googleusercontent.com.json` (project: `hermes-resource-project`, client_id: `339939932247-mfmdg4cupg62nuectocd9g7tcq9g715h.apps.googleusercontent.com`). Use `google-workspace` skill's `google_api.py` (GAPI) CLI for search ONLY — the only Drive subcommand is `drive search`. For download from Drive, use inline Python with OAuth + `MediaIoBaseDownload` — see `references/gdrive-download-pattern.md` for the copy-paste-ready pattern. For upload/create/delete, use inline Python with `MediaIoBaseUpload` + OAuth token.
- **FALLBACK: Service Account** — read + in-place-modify only (NO create/delete — service accounts lack storage quota). Key at `/root/.hermes/google_service_account.json` (`drive-api-hermes-worker@g-drive-api-project-496506.iam.gserviceaccount.com`). Only works for folders explicitly shared with the SA email. Use only when OAuth is unavailable; prefer OAuth for all operations.
- V2 Handbook Docs folder: `1QqFi4ouGDoLYaW8AkV4VN_CvMsuVzIEZ`
- Pillar Content subfolder: `1thBi3maSdxFBurvz4G3GaxDevlYV4c_d` (contains PILLAR 1-6 subfolders)
- Pillar 3 folder: `1fpzQJVbMW8eSG4qo3mayf2H_rBJQ2naj`
- Pillar 5 folder: `1V-bIlqb73boo4Iu10J-Ezhd7YCdEvzCe`
- Pillar 6 folder: `18M16bFFkhpPytNE62ZSKHDg4drgrYmQb` (file: `1dwXFv8WIOsJ1wpkgKnxZaOWR9kSHcyKD`)
- Master outlines file: `1QwRs04BlxUJGOZMRVpGIkdeDRSZE18dn`

## Verification

After generating any pillar content, verify:
1. `grep -c "^## N\\.' file.md` — correct section count (where N is pillar number)
2. `grep -c "Primary Metabolic Block" file.md` — at least 1 (tissue map)
3. `grep -c "HARD GATE\\|SEQUENCE MANDATE\\|NON-NEGOTIABLE\\|ABSOLUTE CONTRAINDICATION" file.md` — at least 1
4. Cross-pillar references present in co-dependencies section: verify with `grep -c "Cross-link\\|Cross-reference\\|Pillar [1-6]" file.md` — minimum 6
5. No filler phrases ("interestingly," "importantly," "research suggests," "fascinatingly")
6. `wc -l` and `du -h` — report line count and file size
7. Terminal silence after rebuild: output verification report, never raw markdown output
8. File path convention: `/opt/hermes/detoxxx_v2/pillar_N_v2_rebuild.md`

### Genre-Aware Rubric Application

**Not all Handbook sections are narrative pathway chapters.** The 7-point quality rubric (Bridge Box, Hard Gates, Dual-Lane, Three Choke Points, Clinical Vignette, Cross-References, Tables) was designed for Section 8-style biochemical pathway writing. Applying it uncritically to other genres produces false positives. See `references/genre-aware-quality-rubric.md` for the full genre classification system, automated audit script, and per-genre gap analysis logic. Key rules:

- **Section 5 (Tactical Protocols):** Full 7/7 rubric applies. Phase Compatibility Table + Contraindications table are MANDATORY.
- **Section 9 (Personalization):** Modified rubric. Dual-Lane satisfied by Bridge Box + technical body. Tables preferred but list-format acceptable.
- **Section 10 (Tracking Templates):** Operational rubric. Quality = CPT codes, lab ranges, "if X then Y" guidance. Three Choke Points and Clinical Vignettes do NOT apply.

### Model Selection for DETOXXX Content Generation

Head-to-head shootout results (May 21, 2026 — Section 5.1 Herxheimer, identical prompt + skills across all models):

| Model | Words | Hard Gates | Named Enzymes | Bridge Box Quality | Verdict |
|---|---|---|---|---|---|
| DeepSeek V4 Pro (native API) | 5,976 | 5 | 30+ distinct | "Building demolition" — layered metaphor | **Winner — clinical utility + mechanism density** |
| Kimi K2.6 (Ollama Cloud) | 3,817 | 3 | Solid | "Neglected house" — functional | Third place, reliable only for high-volume template work |
| GLM-5.1 (Ollama Cloud) | 3,980 | Present | 219 instances | "Building demolition" — strong | Second place, competitive biochemistry but voice wanders |

**DeepSeek V4 Pro native API is the primary workhorse for all DETOXXX voice-critical, safety-sensitive narrative content.** GLM-5.1 as secondary for biochemistry-heavy sections where pathway trace depth matters. Kimi K2.6 for high-volume template-driven work (Agent Encyclopedia A-Z, 127 entries). Ollama Cloud models have intermittent 401 authentication failures — never rely on them for production-critical sections without a fallback.

**Execution method:** Direct writing via write_file (no subagents, no delegation) for voice-critical content. Sequential batches, one section at a time, DeepSeek V4 Pro native API with dedicated API keys to avoid concurrency bottlenecks.

### Post-Completion Architecture Audit (Mandatory for Architecture-Critical Sections)

For sections where errors cascade (Section 3 — Protocol Architecture, Section 4 — Master Daily Grids), run a GLM-5.1 audit after writing but before Drive upload:

1. **Write + validate** the section with DeepSeek (7-marker quality scan).
2. **Launch GLM audit** via background terminal: `hermes -z "$(cat /tmp/audit_prompt.txt)" --provider ollama-cloud --model glm-5.1` with `terminal(background=true, notify_on_complete=true)`. Write the audit prompt to a temp file first — the `-z` flag takes a single string argument. **Do NOT use `--no-pager`** — that flag does not exist. **Do NOT use `hermes chat -q`** for programmatic single-shot prompts — use `hermes -z` instead.
3. **Apply patches** from GLM's findings before uploading.
4. **For complex sections, run a second-pass audit** with a different focus (e.g., first pass catches phase architecture errors, second pass catches vague criteria and Tier arithmetic). GLM's second pass found 7 vague criteria and 3 Tier 3 duration errors that the first pass missed.

5. **For Section 4 specifically**, use the operational audit script at `references/section4-operational-audit.py` — it checks day ranges, CDS taper, silver window, ALA Q3H cycling, structural elements per phase, and timing conflicts (silver-NAC, silver-antioxidant). Run it with `python3 references/section4-operational-audit.py [filepath]`. This script was proven May 22, 2026 and caught a silver-NAC co-administration conflict at 11:00 that violated the 4h separation rule.

6. **For Section 4←Section 8 cross-reference**, use the methodology in `references/section8-section4-cross-reference.md`. It covers: missing mandatory agents (16 agents cross-checked), agent proximity/synergy pairs (5 pairs verified), phase placement, CDS timing conflicts, and the 8.8A enzyme rule false-positive filter. The script systematically compares every Section 8 pathway mandate against Section 4 daily grids and reports findings by severity (CRITICAL → MISSING AGENT → TIMING → PROXIMITY → DOSE → INFO).

**== HARD GATE — Never use Kimi K2.6 for architecture auditing.** Kimi scored third place on DETOXXX content and is weak at voice consistency, bridge box quality, and structural reasoning. Kimi's role is high-volume template-driven work (Agent Encyclopedia A-Z, 127 entries). GLM-5.1 is the only valid secondary model for architecture audits. The user explicitly corrected a Kimi-as-auditor attempt on May 22, 2026 ("i thought glm was better than kimi in our head to head battle"). This is now a permanent constraint.

## Source Synthesis Protocol — Multi-Source Data Extraction & Merging

When writing a section that draws on multiple internal source documents (Kalcker guides, training courses, Phase Maps, Perplexity drafts, Deep Research outputs), follow this extraction → synthesis → subordination workflow. The user's mandate is explicit: **strip philosophical/rhetorical framing, discard beginner/course tone, subordinate all raw data to the strict phased architecture.** The final output must read as an integrated tactical protocol embedded inside the V2 regimen — not as a standalone book chapter.

### Phase 1 — Source Discovery & Download

1. **Search the Drive folder** for all relevant source files: `name contains 'keyword'` across the DETOXXX folder, the Chlorine Dioxide folder, and subfolders.
2. **Download all matches** to `/tmp/<section>_sources/` using OAuth token at `/root/.hermes/google_token.json`. Download markdown versions preferentially (already converted from EPUB/DOCX); fall back to PDF for training courses.
3. **OAuth may expire mid-session.** If you get `RefreshError: invalid_grant`, fall back to the local file cache at `/opt/hermes/detoxxx_v2/` — the master handbook and most section files are kept there. The service account at `/root/.hermes/google_service_account.json` can read files shared with it but cannot create new files.

### Phase 2 — Targeted Extraction from Large Files

Audit notes and source guides routinely exceed the 100,000-char read_file limit. Use grep/sed for targeted extraction:

1. **Find section-specific specs**: `grep -n "5\\.3\|ITEM 5\\.3\|CDS" AUDIT_NOTES.md | head -30`
2. **Extract contiguous spec blocks**: `sed -n 'START_LINE,END_LINEp' AUDIT_NOTES.md`
3. **For Kalcker/guide files with no markdown headers**: grep for operational keywords (dosing, ppm, protocol, route, activation, separation, body weight) rather than section headers.
4. **Read key sections with read_file** using offset/limit for the most critical operational data blocks.

### Phase 3 — Deviation Detection & Merging

Sources will conflict. The Kalcker guide, Phase Map, Audit Notes, and Perplexity drafts often differ on specific parameters. Resolve conflicts using this hierarchy:

1. **Phase Map is authoritative for phase architecture** (which phase, what intensity, entry/exit timing). All other sources are subordinate to the Phase Map on phase deployment.
2. **Kalcker/primary source is authoritative for operational detail** (dosing, preparation, route protocols, ppm math). The Phase Map references Kalcker; it does not replace Kalcker's operational specificity.
3. **Audit Notes are authoritative for quality structure** (what subsections must exist, what tables must be present, what clinical vignettes are required). The Audit Notes specify the deliverable format; the sources supply the content.
4. **Perplexity drafts are scaffolding only** — use their structure, extract any well-phrased Bridge Box metaphors, but rebuild all mechanism chains and dosing tables from primary sources.
5. **When sources conflict on a safety parameter** (dose ceiling, separation window, contraindication): use the STRICTER value. A 4-hour separation window from the Audit Notes overrides a 2-hour window from Kalcker. A 7-day hard stop from the Phase Map overrides a 14-day window from Deep Research.

### Phase 4 — The Tone Strip

The user's core directive: "Strip away all of the sources' philosophical/rhetorical framing and completely discard the 'beginner/course' tone of the training guide." Apply these transformations to all extracted source data:

1. **Remove**: "I discovered," "in my experience," "many people have told me," "I believe," personal anecdotes, marketing language, "this little book," "I hope this helps you."
2. **Remove**: Beginner-encouragement framing — "don't worry," "it's easy," "you can do this," "just try," "listen to your body" (keep clinical self-monitoring instructions, discard vague wellness rhetoric).
3. **Upgrade**: "X works by oxidation" → "ClO₂ accepts electrons from sulfhydryl groups in cysteine residues of membrane proteins, producing protein denaturation and transmembrane electrochemical gradient collapse."
4. **Replace**: "The rats were fine" → "Toxicity studies at Norbert Wiener University administered CDS to 54 Rattus norvegicus across five dosing tiers (40, 100, 200, 300, 400 mL ClO₂ in 2L water) with no observed toxicity, no organ pathology, and no mortality."
5. **Preserve**: Operational dosing data (ml, ppm, drops, hours, days), route protocols, preparation specifications, safety warnings, and compatibility rules. These are the payload. Everything else is packaging — discard it.
6. **Subordinate everything to phase architecture**: Every piece of extracted data must answer "When in the 8-phase protocol does this apply?" If a source describes a dosing protocol without phase context, the writer must assign it to the correct phase window based on the Phase Map.

### Phase 5 — Architecture Cross-Check (for Architecture-Critical Sections)

For sections where architectural errors cascade (Phase Gates, Pillar-to-Phase Matrix, Case Archetypes), run a secondary model audit before shipping:

```bash
hermes -z "$(cat /tmp/audit_prompt.txt)" --provider ollama-cloud --model glm-5.1
```

GLM-5.1 via Ollama Cloud is preferred for architecture review — it has strong biochemistry and structural reasoning, and does not compete for the DeepSeek API key. Give it: the Audit Notes spec, the Phase Map, and the complete draft. Task it with flagging missing criteria, Phase Map contradictions, and dependency gaps. Apply patches before final upload.

## Pitfalls

- **DEEPSEEK API CONCURRENCY LIMIT — single request per API key:** DeepSeek API enforces one concurrent request per key. If 3 subagents all share the same DEEPSEEK_API_KEY, only one gets through — the other two stall with zero API calls and eventually timeout. **Fix:** Use dedicated API keys per subagent (each subagent gets its own DeepSeek key set via env var) OR run subagents sequentially (one at a time). Never launch >1 subagent on the same DeepSeek API key. See `references/deepseek-api-concurrency.md` for the full failure pattern and fix.
- **Subagent timeout for complex writing:** The default `child_timeout_seconds: 600` is insufficient for multi-file writing tasks where each file requires research + drafting. Set to 1200 (20 minutes) in `config.yaml` under `delegation:`. A subagent writing 9 files with web research and deep mechanism detail routinely needs 10-15 minutes.
- **Native API vs Ollama Cloud — quality difference matters for content:** DeepSeek V4 Pro via native API produces 40-50% more words, more hard gates, deeper mechanism chains, and richer clinical vignettes than the same model routed through Ollama Cloud. For content-quality-critical work (pillars, protocols), prefer native API. Use Ollama Cloud only as fallback.
- **Subagent delegation for multi-file writing tasks — strategy, not prohibition:** Subagents CAN be used for multi-file writing when the following mitigations are applied: (a) Split work so each subagent writes 1-2 files maximum — the 600s timeout becomes a non-issue for single-file tasks. (b) Keep voice-spec context compact — inject only the core voice directives, not the full skill. (c) Assign each subagent a unique output file prefix to avoid `.tmp.*` lock conflicts on shared directories. (d) For items exceeding ~15K words or requiring deep cross-referencing across files, write directly with `write_file` in sequence instead. The key diagnostic: if a single subagent's total expected word count exceeds 12K, prefer direct writing.

- **CRITICAL: Delegation config MUST be explicitly set before subagent launches.** If `delegation.model` and `delegation.provider` are empty strings in config.yaml, all subagents will fail with `api_calls: 0` and `status: interrupted` — they route to a void with no model. Minimum required config:
  ```yaml
  delegation:
    model: deepseek-v4-pro
    provider: deepseek
    child_timeout_seconds: 1200   # 20 min for heavy writing tasks
    reasoning_effort: high
  ```
  Verify with `hermes config | grep -A8 delegation` before launching. Subagents with zero API calls after 450+ seconds are diagnostics of unset delegation config, not model quality issues.

- **DeepSeek API concurrency bottleneck — multi-key pattern:** DeepSeek enforces single-concurrent-request per API key. When launching 2+ parallel subagents via `delegate_task` or `terminal` with the same `DEEPSEEK_API_KEY`, only one gets the key — the rest queue and eventually timeout. Fix: assign each parallel subagent a DEDICATED API key (separate DeepSeek API keys). If separate keys aren't available, fall back to sequential execution (one batch at a time). Alternative: use different providers per subagent (e.g., Subagent 1→DeepSeek API, Subagent 2→Ollama Cloud kimi-k2.6, Subagent 3→Ollama Cloud glm-5.1). This enables true parallelism AND tests fallback model quality simultaneously. When using `terminal` background mode with `hermes chat -q`, preload writing skills via `-s detoxxx-writing,protocol-handbook-authoring,google-workspace` to inject methodology into each agent's context without bloating the prompt.

- **here.now publishing for external AI access:** When another AI system (Perplexity, Claude, etc.) needs to read DETOXXX files but can't reach the VPS directly (firewall, IP routing, auth), publish via here.now for public CDN URLs: copy files to a temp directory, run `bash ~/.hermes/skills/here-now/scripts/publish.sh /tmp/dir --title "Title" --client hermes`, share the resulting `https://{slug}.here.now/` URLs. Open firewall ports if self-hosting (`ufw allow {port}/tcp`).\n- **== HARD GATE — Delegation config MUST be explicitly set before any subagent launch ==:** If `delegation.model` or `delegation.provider` is empty in config.yaml, subagents launch into a void — zero API calls, silent timeout, no output. Set `hermes config set delegation.model deepseek-v4-pro` and `hermes config set delegation.provider deepseek` before any delegate_task call. Verify with `grep -A5 delegation ~/.hermes/config.yaml`.\n- **DeepSeek API single-concurrency per key:** DeepSeek enforces one concurrent request per API key. Three parallel subagents sharing the same DEEPSEEK_API_KEY = two stall with 0 API calls. FIX: (a) Use `terminal` with `background=true` to launch independent `hermes chat -q` processes instead of delegate_task. (b) Preload skills via `-s detoxxx-writing,protocol-handbook-authoring,google-workspace`. (c) Assign dedicated API keys per agent via inline env: `DEEPSEEK_API_KEY=sk-xxx hermes -s ... chat -q \"$(cat /tmp/prompt.txt)\" --provider deepseek --model deepseek-v4-pro`. (d) For multi-model quality comparison, run different providers in parallel: deepseek + ollama/kimi-k2.6 + ollama/glm-5.1 — no key contention. See `references/multi-agent-execution-patterns.md` for the full recipe.\n- **GLM-5.1 Ollama Cloud latency — large prompts may never complete:** GLM-5.1 via Ollama Cloud (744B MoE) struggles with prompts over ~20KB. A 562-line, 38KB audit prompt produced zero output after 72+ seconds. **Mitigation:** For large audit prompts, split into Pass 1 (day ranges + gate labs, ~200 lines) and Pass 2 (quality + completeness, ~200 lines). If GLM produces zero output within 60 seconds, kill it and run the audit manually with `execute_code` Python scripts — the two-pass pattern is reproducible without GLM. The audit methodology (cross-check Phase Map, verify structural elements, check timing conflicts) matters more than which model runs it. See `references/section4-operational-audit.py` for the proven Section 4 audit script. On architecture-critical sections (Phase Gates, Pillar-to-Phase Matrix, Case Archetypes), run a GLM-5.1 architecture cross-check before shipping: `hermes -z "$(cat /tmp/audit_prompt.txt)" --provider ollama-cloud --model glm-5.1` in a background terminal process (`background=true`). GLM-5.1 is preferred for architecture review because it has strong biochemistry, competitive structural reasoning, and runs via Ollama Cloud without competing for the DeepSeek API key. It caught two hard architectural errors in Section 3 (phase day ranges not matching Phase Map, lab timing on Gates 3-4) that would have cascaded into every downstream section. For simpler writing validation, the 7-marker quality scan script is sufficient; the GLM audit is for architecture-critical content only.

- **Google Docs API "Precondition check failed" at ~1.5MB document size:** The Google Docs API (`documents().batchUpdate` with `insertText`) fails consistently when the document exceeds approximately 1.5 million characters. The error is a generic 400 "Precondition check failed" with no indication of the size limit. **Workaround:** Do NOT use the Docs API for large documents (>1MB). Use pandoc to convert markdown → .docx, then post-process with python-docx. For documents under 1MB, the Docs API works fine with sequential insertText at end-of-document. See `references/docx-generation-workflow.md` for the complete pandoc+python-docx pattern. after writing or patching — do not wait for session end. If audit/GLM review requires changes later, make changes and re-upload. Never leave completed files only on local disk. This prevents data loss from terminal crashes, VPS failures, or session interruptions. The GDrive copies are the authoritative versions. This applies to all DETOXXX artifacts: Section files, Build Tracker updates, merged files, and master handbook assembly.

- **CRITICAL — Subagent model routing failure (delegation config):** If subagents fail with `api_calls: 0` and long timeouts (~450s), the delegation config is likely unset. Check `config.yaml` → `delegation:` section. If `model:` and `provider:` are empty strings (`''`), subagents have NO model to route to and will silently fail — they route into a void with zero API calls. Fix: `hermes config set delegation.provider deepseek` and `hermes config set delegation.model deepseek-v4-pro`. Also set `hermes config set delegation.child_timeout_seconds 1200` for complex writing tasks (10 min default too short for multi-section batches) and `hermes config set delegation.reasoning_effort high`. Verify with: `grep -A10 'delegation:' /root/.hermes/config.yaml` — model and provider must be non-empty strings. Run this verification BEFORE launching any subagent writing batch. If subagents fail, cease all work and fix config — do not retry with the same broken config.

**Preferred fallback chain for delegation and system-wide use:** The user's preference, in order: (1) `ollama-cloud` / `deepseek-v4-pro` (matches primary architecture), (2) `ollama-cloud` / `kimi-k2.6` (1T MoE, newest April 2026, agent swarms), (3) `ollama-cloud` / `glm-5.1` (744B MoE, 94.6% of Claude Opus 4.6 coding, #1 open-weight), (4) `ollama-cloud` / `qwen3-coder:480b` (480B MoE safety net). Rejected models: `deepseek-v3.1` (obsoleted by v4-pro), `kimi-k2-thinking` (obsoleted by k2.6), `gemma4:31b` (too small for complex writing), `mistral-large-3:675b` (redundant behind glm-5.1 and k2.6).

- **No inline output for large content generation:** When the user explicitly says not to write outputs in the context window, use subagents or background processes to draft files, then upload to Google Drive. Report only: file names, Drive file IDs, line counts, and word counts. Never stream raw content into the conversation when instructed otherwise.
- **read_file safety limit (100,000 chars):** Pillar files at Pillar 6 density routinely exceed the read limit (120-225K+). Use chunked reads — split at ~50% of line count, e.g., `limit=350 offset=1` then `limit=300 offset=351` for a 611-line file. Adjust offsets based on `total_lines` from the error message. For very large files (3,500+ lines, 200K+ chars), use **parallel chunked reads** — fire all chunks simultaneously to consume the file in one round-trip (5×600-line reads for a 3,568-line file). This is faster than sequential reads and avoids re-requesting the model for each chunk.
- **Verification grep is pillar-specific:** The section-count grep MUST use the pillar's number. `^## 6\\.` for Pillar 6, `^## 1\\.` for Pillar 1, etc. The older Pillar-6-hardcoded pattern is a common copy-paste error.
- **Line counts vary by pillar:** Pillar 6 reached 1,968 lines / 225KB but that is not a rigid target. Pillar 1 (parasites) reached 611 lines / 120K at equivalent density — fewer toxin classes to enumerate. Judge by mechanism density and structural completeness, not line count.
- **Google Drive push:** Do not push to Google Drive unless the user explicitly requests it. Write locally first to `/opt/hermes/detoxxx_v2/pillar_N_v2_rebuild.md` and wait for confirmation before Drive upload.
- **OAuth is primary for Drive:** Use OAuth for all Drive operations. Token at `/root/.hermes/google_token.json` (key: `token`). The service account at `/root/.hermes/google_service_account.json` is fallback only — it can read and modify existing files in-place, but CANNOT create new files (storageQuotaExceeded). Always verify OAuth before Drive operations. **PITFALL — OAuth token expires silently.** The token auto-refreshes for a period, then fails with `RefreshError: invalid_grant: Token has been expired or revoked.` When this occurs, the Drive download or upload will fail with an opaque 400-level error. **Fix:** When the OAuth token is expired, fall back to using the local file cache — the master handbook and other large files are kept at `/opt/hermes/detoxxx_v2/` for exactly this scenario. For essential downloads, the service account at `/root/.hermes/google_service_account.json` can read files from folders explicitly shared with it, but cannot create new files.
- **State work provenance immediately:** When files are found on disk from prior sessions, state this explicitly in the FIRST response — "Files already exist at X lines / Y words. I will audit them against the spec and surgically enhance." Never let the user infer that work was written from scratch when it was audited. The user distinguishes between audit/enhance and fresh writing and will ask if provenance is ambiguous. Head this off at discovery time. When audit is complete, restate: "These files were subagent outputs. I applied N surgical patches to close the remaining gap." Clarity builds trust.
- **PITFALL — 8.8A enzyme pre-treatment rule is contextual, not universal:** Section 8.8A mandates enzyme pre-treatment (nattokinase + serrapeptase) minimum 14 days before antimicrobial agents. This applies to **dedicated biofilm-disruption protocols** targeting biofilm-embedded bacteria (oregano oil, berberine, garlic) whose EPS matrix physically blocks antimicrobial penetration. It does NOT apply to Phase 2's antiparasitic botanicals (Black Walnut/Wormwood/Clove) which target free-swimming parasites and eggs via direct mechanisms (mitochondrial ETC disruption, membrane depolarization, ovicidal penetration). Do not flag Phase 2 antiparasitics as violating 8.8A in cross-reference audits. The real enzyme cascade belongs in Phase 4 for spike proteolysis, fibrin microclot dissolution, and deep biofilm disruption.
- **PITFALL — Audit Notes phase numbering differs from Phase Map:** The `HERMES_WAVE_EXECUTION_AUDIT_NOTES.md` uses a different 8-phase numbering model than the authoritative `DETOXXX_V2_Phase_Map_Executive_Brief.md`. Audit Notes: Phase 6=CNS chelation, Phase 7=Nano, Phase 8=Maintenance. DETOXXX V2: Phase 6=Restoration, Phase 7=Consolidation, Phase 8=Maintenance. **Never copy phase day ranges or lab draw days from Audit Notes without cross-checking against the Phase Map.** The Phase Map is authoritative for phase day ranges, lab timing, phase duration, and agent-to-phase windows. The Audit Notes are authoritative for section structure, clinical vignette content, table column specs, and quality criteria. At least one of the conflicts is authoritative for section structure, clinical vignette content, table column specs, and quality criteria. When they conflict on phase architecture, the Phase Map wins. This caused two hard errors in Section 3 (Phase 1/2 day ranges, Gate 3/4 lab timing on Days 55/70 instead of 35/56) caught by GLM-5.1 audit.
- **Tactical protocols under 200 lines AND under 2,500 words are failed deliverables:** When writing Section 5 tactical protocols from scratch, files at 100-150 lines are missing 50%+ of required content. When writing Section 5 tactical protocols from scratch, files at 100-150 lines are missing 50%+ of required content. The user will call this out as "light" and demand rewrites. Use the pre-submission checklist in the Tactical Protocol Section Architecture. Every protocol needs 2+ clinical vignettes, exhaustive dosing tables, Three Choke Points interface, Phase Compatibility Table, and full cross-references. Measure density by word count (2,500+), not line count — wide tables compress lines but preserve content.
- **Audit notes must be re-read for EVERY section — see Audit-First Mandate above:** This is elevated to its own mandatory directive in the Companion Skills section. Do not read once and wing it. Use grep/sed for large audit files (100K+ chars) that fail read_file.
- **PITFALL — Section 8 pathway constraints may NOT apply to Section 4:** Section 8 pathways describe dedicated deep-clean protocols (e.g., 8.8 biofilm 4-stage cascade with 14-day enzyme pre-treatment before antimicrobials). These constraints govern THAT pathway's internal logic — they do NOT automatically constrain the Section 4 daily grids. Example: Section 8.8's "enzyme pre-treatment minimum 14 days before antimicrobials" applies to a dedicated biofilm strike using oregano oil + berberine against EPS-embedded bacteria. It does NOT apply to Section 4 Phase 2's gentle antiparasitic introduction (Black Walnut, Wormwood, Clove) which targets free-swimming parasites in the gut lumen — not biofilm-embedded organisms. Always ask: does this Section 8 constraint target the same biological compartment as the Section 4 grid being audited? If no, it's a false positive — note it and move on.

- **PITFALL — External model audits produce false negatives — grep-verify every "missing" finding:** Both GLM-5.1 and Nemotron-3 falsely flagged Sections 9, 10, and 11.1-11.3 as "MISSING" in their June 8, 2026 audits, when they existed with complete content (verified via `grep -n "^# Section [0-9]\|^# [0-9]+\.[0-9]"` against the source). For every "missing" or "absent" finding from an external audit, run a grep/sed verification against the actual file BEFORE actioning. Flagging non-existent gaps wastes entire sessions. The fix: run `grep -n "^# Section [0-9]\|^# [0-9]+\." handbook.md` to map all section boundaries, then grep specific sections to confirm content depth. Do not accept any audit finding at face value. This applies to ALL model audits — no model is immune to false negatives on large documents.\n\n- **PITFALL — Upload immediately after every completion, no exceptions:** The user's directive: upload to GDrive the moment any DETOXXX file is written or patched. Do not batch uploads at session end. If audit/GLM review requires changes later, make changes and re-upload. Never leave completed files only on local disk. This prevents data loss from terminal crashes, VPS failures, or session interruptions. The GDrive copies are the authoritative versions. This applies to: Section files, Build Tracker updates, merged files, and the master handbook assembly.
- **Model comparison eval — unique output paths required:** When comparing multiple models head-to-head on the same writing task (same prompt, same skills, same spec), give each model a UNIQUE output file path (e.g., `section_5_1_herxheimer_deepseek.md`, `section_5_1_herxheimer_kimi.md`, `section_5_1_herxheimer_glm51.md`). If all three target the same path, whichever finishes last overwrites previous output, and models that find an existing file will audit it instead of generating fresh content (Audit-First Mandate kicks in). For true head-to-head generation comparison, unique paths are mandatory. After all three complete, compare with `wc -lwc` and `md5sum` to detect identical fallback output vs unique generation.

- **PITFALL — Duplicate Pillar H1 header sandwich (WHY→---→PILLAR→Overview):** When individual Pillar sections are concatenated during assembly, Pillars 4/5/6 (and potentially others) end up with a redundant second `# PILLAR N` header wedged between the "WHY PILLAR EXISTS" block and `## Pillar Overview`. The structure: `# PILLAR 4` → Taxonomy Boundary → `## WHY PILLAR 4 EXISTS` → paragraphs → `---` → `# PILLAR 4` (DUPLICATE) → `## Pillar Overview`. This makes external auditors count 9 Pillar headers instead of 6 and flag "duplicate sections." **Fix:** Remove the second `# PILLAR N` header and the preceding `---` separator, letting WHY flow directly into Overview. The verification grep: `grep -B2 '^## Pillar Overview' handbook.md | grep -c '^# PILLAR'` must return 0. Proven June 9, 2026 — 3 duplicates removed from CLEAN handbook in one pass.

### Directive 1+8 Assembly Audit — Structural Integrity + Sensory Specificity

When the assembled master handbook is to be audited for Directive 1 (surface every weakness: missing sections, duplicates, dead cross-references, thin sections, logic gaps, formatting issues) and Directive 8 (demand sensory specificity: replace vague symptom descriptions with body location, quality, intensity, and duration), use the systematic methodology in `references/directive-1-8-audit-methodology.md`. This covers: parallel grep patterns for both directives, section-boundary mapping, duplicate detection, dead cross-reference counting, symptom-vagueness scanning, and severity-tiered finding output. Do not attempt to read_file a 19,000-line handbook — grep/sed targeted extraction is mandatory.

### Directive 2+22 Execution — Replacement Text + Physician Executive Brief

When the user asks to generate replacement text for every audit finding (Directive 2) and build the physician executive brief (Directive 22) against the assembled handbook, use the systematic methodology in `references/directive-2-22-execution-pattern.md`. This covers: 12 parallel grep/sed scans for structure mapping, duplicates, dead cross-references, vague symptoms, undefined labels, weasel words, depletion manifests, clinical abstractions, and dose ceilings; severity-tiered finding classification (CRITICAL/HIGH/MEDIUM); Pillar 6-density replacement text generation with differential diagnosis tables; and the 10-section physician brief structure (protocol identity, indications, contraindications, labs, dose ceilings for 5 highest-risk agents, off-label agents, phase-by-phase physician involvement, pre-Phase-3 reading list, practitioner checklist, immediate audit action items). Do not attempt to read_file a 38,000-line handbook — grep/sed targeted extraction is mandatory.

### Directive 15+19 Audit — Failure Mode Catastrophization + Operational Followability

When the user asks to catastrophize failure modes (Directive 15) and/or test operational followability (Directive 19) against an assembled handbook or section, use the systematic methodology in `references/directive-15-19-audit-methodology.md`. This covers: the 7-phase audit workflow (document acquisition, structure mapping, sectional deep-read, contradiction detection, operational followability scan, missing failure mode scan, output compilation), the Directive 19 checklist (preparation timing, concentration verification, visual references, abbreviations, weight-based dosing, unit conversion, procurement, dead references, chemical identity, gate circularity), the Directive 15 taxonomy (invisible failures, wrong-row warnings, delayed consequences, rules without consequences, missing differentials, intuitive wrong responses), and the [SECTION][LINE] FINDING → REPLACEMENT → RATIONALE output format with FATAL/CONTRADICTION/HIGH/MEDIUM severity tiering. Proven June 2026 against the 38,294-line master handbook — found 27 critical issues (13 operational gaps, 11 missing failure modes, 3 structural). The contradiction detection pattern (cross-referencing daily grids against tactical protocols for schedule/phase/dosing conflicts) is the highest-value find — flagging agents where two sections of the same handbook prescribe different protocols.

### Directive 24+25 — Data Gaps Appendix + Safety Changelog

When the user asks to build a Data Gaps and Unknowns Appendix (Directive 24) or a Safety-Relevant Changelog (Directive 25) against the assembled master handbook, use the systematic methodology in `references/directive-24-25-execution-pattern.md`. This covers: grep patterns for model-based estimates and uncertainty language, duplication detection (structurally identical passages that propagate estimates as if independently corroborated), internal contradiction detection (handbook's own clinical vignettes that contradict its quantitative claims), uncertainty label classification (CRITICAL/HIGH/MEDIUM/LOW with evidence-tier assignment), and the V2 safety feature extraction pattern (Hard Gates, Sequence Mandates, dose ceilings, safety lockouts, codified rescue protocols). The methodology was proven June 7, 2026 against the 19,147-line master handbook — found 18 uncertainty labels and 16 safety-relevant changelog entries.

Key findings from the reference audit:
- GlyRS 2-3% substitution rate is the #1 data gap every time — most load-bearing quantitative claim (underlies 6+ sections) with NO citation
- GSH pool "10-15 grams" is a textbook value repeated 10+ times as denominator for all depletion calculations
- Colloidal silver "four orders of magnitude" safety margin is internally contradicted by the handbook's own vignette (argyria at ~18x protocol dose, not ~10,000x)
- The Herxheimer Three Choke Points breakdown appears identically at three locations — duplicated passages propagate model-based estimates as if independently corroborated
- The Morgellons section (Pillar 3, Section 3.5) is the gold standard for evidence-tier transparency — its uncertainty-acknowledgment pattern should be replicated for all uncertain claim domains

### Directive 16+17 Execution — Hardening + Operator Field Cards

When the user asks to harden the handbook against human error (Directive 16) and/or build operator field cards per tier (Directive 17), use the systematic methodology in `references/directive-16-17-execution-pattern.md`. This covers: the 7-phase execution workflow (source ingestion → structure mapping → hardening gap scan → per-section audit → field card generation → implementation priority table → deliverable format), the 4 diagnostic grep scans for hardening gaps (DON'T SKIP anchors, checklists, bridge boxes, hard gates), the 7-element field card template per tier (who should NOT run, minimum lab set, Herx decision tree, ER triggers, MVS schedule, "if you must cut" sidebar, summary card), the tier-specific ER threshold escalation (Tier 3 has STRICTER thresholds than Tier 2; Tier 4 has MOST SENSITIVE), and the shell heredoc pitfall workaround (use `python3 << 'PYEOF'` with raw strings instead of `cat > file << 'EOF'` to avoid `&` character backgrounding rejections). Proven June 2026 against the 38,294-line master handbook — found ZERO DON'T SKIP anchors and ZERO checklists across all 45 section files, and generated 4 tier field cards (877 lines, 7,028 words).

### Directive 3+13 Audit — Completeness (5-Question) + Evidence Tier Labeling

When the user asks for a completeness audit or evidence tier labeling of handbook content, use the methodology in `references/completeness-and-evidence-tier-audit.md`. This captures the 5-question framework (What am I doing? Why? What will I feel? What if it goes wrong? What if I skip it?) — proven June 2026 against the 19,147-line master handbook, finding 34 gaps — plus the 4-tier evidence labeling system (Clinical Trial / Case Series / Mechanistic Inference / Anecdote) with model-based estimate detection and mainstream-dispute acknowledgment checks.

### Directive 10+12 Audit — Mechanism Chain Verification + Citation Density

When the user asks for mechanism-chain verification, citation density audits, or a combined Directive 10+12 audit, use the methodology in `references/directive-10-12-mechanism-citation-audit.md`. This covers: 10 targeted grep/sed scans for incomplete mechanism chains (claims stating effect without named-enzyme cascade), numeric estimates without derivation (GlyRS "2-3%", GSH "10-15 grams"), missing citation infrastructure (only 6 markers across 4.6MB), evidence-tier labeling gaps, regulatory disclosure gaps (CDS/FDA), and self-consistency checks between audit and body text. Proven June 2026 against the 38,294-line MASTER HANDBOOK — found 18 actionable gaps (4 Critical, 8 High, 6 Medium). Key diagnostic: the Herxheimer sections have GOLD-STANDARD mechanism chains (TNF-α→ceramide→Complex III Qo site; IL-6→STAT3→GRIM-19→Complex I), so the audit must distinguish between sections that need cascade building (microplastics, phthalates) and sections that only need citations (Herxheimer, nanomaterials).

**Key findings from the reference audit:** "What will I feel?" and "What if I skip it?" are missing from ALL 7 Pillars + EMF. The GlyRS glyphosate substitution "2-3 percent" claim is the most critical evidence-tier softener — it underlies the Fibrinogen-Glyphosate-Spike axis across 4+ sections with NO citation. The Morgellons section in Pillar 3 is the evidence-tier transparency gold standard. Model-based numeric estimates (GSH pools, population prevalence, substitution rates, argyria thresholds) need explicit "model-based estimate" or "WHO estimate" prefixing.

### Section 8→4 Cross-Reference Audit (Mandatory Post-Build Gate)

When both Section 8 and Section 4 are built, run the four-pass cross-reference methodology documented in `references/section8-to-section4-cross-ref.md`. This catches missing agents, synergy violations, and timing conflicts that individual section audits miss.

**Four passes:**
1. **Missing Agent Detection** — Extract every agent+dose from Section 8, verify presence in Section 4 at correct phase
2. **Synergy/Proximity Audit** — Check mandated co-administration pairs (Section 8 says "A+B together" → Section 4 must have same time slot)
3. **Timing/Separation Audit** — Check mandatory separation windows (Section 8 says "Xh between A and B" → Section 4 must enforce)
4. **False Positive Filter** — Before flagging any finding, verify the Section 8 constraint targets the same biological compartment as Section 4's phase

**== PITFALL — False-positive Section 8 constraints ==** Section 8 pathways describe dedicated deep-clean protocols with internal logic that may NOT apply to Section 4 daily grids. Example: Section 8.8's "enzyme pre-treatment minimum 14 days before antimicrobials" applies to a dedicated biofilm strike using oregano oil + berberine against EPS-embedded bacteria. It does NOT apply to Section 4 Phase 2's gentle antiparasitic introduction (Black Walnut, Wormwood, Clove) which targets free-swimming parasites in the gut lumen. Always confirm biological compartment match before flagging.

### External Model Audit Gate (Post-Build Quality Check)

After any major handbook assembly, deduplication, or section build, run an external audit with a STRONGER model than the one used for writing. The writer cannot audit its own work — confirmation bias is unavoidable. The Nemotron-3-ultra audit of the clean handbook (June 8, 2026) caught structural gaps the writing model missed: Section 6 has 0 Hard Gates, Section headers missing for 1/8/9/10, and Section 3.4's architectural rationale lacks any patient translation.

**== HARD GATE — Grep-verify every audit finding before actioning ==** External model audits routinely produce false negatives — sections flagged as "MISSING" that actually exist with full content. Both GLM-5.1 and Nemotron-3 falsely flagged Sections 11.1-11.3 as missing (June 8, 2026), when grep verification proved all three exist with complete tables and content at lines 13068-13328 of the CLEAN handbook. GLM-5.1 also falsely claimed Sections 9 and 10 were missing when they exist with full 9-subsections and 5-subsections respectively. **Never trust an audit finding without raw verification.** For every "missing" or "not present" finding, run `grep -n "^# Section N\|^# N\." handbook.md` to confirm existence before actioning. False-negative audits have wasted entire sessions chasing non-existent gaps.

**Pattern:**
```bash
# 1. Write the audit prompt to a temp file
# 2. Launch external model in background
hermes -z "$(cat /tmp/audit-prompt.txt)" --provider ollama --model nemotron-3-ultra
# 3. nemotron-3-ultra (NVIDIA, June 2026) is preferred for architecture audit
#    Fallback: kimi-k2.6 (1T MoE) for high-volume scan
#    NEVER use the writing model for its own audit
```

**Dual-Track Readability Assessment:** Score every section on 4 markers:
- **BB** (Bridge Box): Plain-language metaphor for the non-clinician
- **CV** (Clinical Vignette): Real failure case with symptoms/timeline/outcome
- **HG** (Hard Gate): Explicit STOP conditions at point of instruction
- **TB** (Table): Any structured data presentation

Section 8's "Dual-Lane Purpose" format (Plain Language + Technical + Bridge Box) is the gold standard that every narrative section should follow. The assessment script pattern is in `references/dual-track-assessment.md`.

### Upload-Immediately Mandate

**== NON-NEGOTIABLE ==** Upload every completed DETOXXX file to GDrive IMMEDIATELY after writing or patching. Do not batch uploads at session end. If subsequent audit requires changes, make changes and re-upload. Never leave completed files only on local disk. GDrive copies are authoritative. Applies to: Section files, Build Tracker updates, merged files, master handbook assembly.

### V2 Phase Remap Annotation Pattern

When remapping pre-V2 DETOXXX content (pathways, protocols, reference tables) to the locked V2 Phase Map, add a surgical `**V2 Phase Architecture:**` annotation immediately after the section title. Format:

```
**V2 Phase Architecture:** [Pathway/agent] operates in Phases [X-Y] (Days [A-B]). [Key stage mappings]. **HARD GATE:** [any phase-gated constraint].
```

This annotation bridges V1-named content to V2 architecture without rewriting the entire document. Each of 9 Section 8 pathway files received this annotation during the May 2026 remap session. The annotation is the bridge — the body content retains its clinical depth.

---
name: protocol-handbook-authoring
description: Multi-source document assembly with template matching, cross-referencing, and style enforcement. Use when generating, extending, or updating structured protocol handbooks, clinical manuals, or technical reference documents that require strict formatting fidelity and cross-section linkage.
tags: [research, writing, protocols, handbooks]
---

# Protocol Handbook Authoring

Generate or extend structured, multi-section technical handbooks — clinical protocols, detoxification manuals, research compendiums — with exact formatting fidelity to an established style template and mandatory cross-referencing between sections.

## Trigger Conditions

Load this skill when the user:
- Asks to generate or extend a numbered chapter/section of a protocol handbook
- References "Pillar X," "Section X.Y," "Chapter X," or similar enumerated document structure
- Specifies an existing document to use as a style template ("use X as your exact style template")
- Demands cross-references between sections (e.g., "cross-link this to Section 2.1C")
- Sets "Blocker Rules" or mandatory constraints that must be satisfied before output is valid
- Mentions "DETOXXX" or any handbook with numbered pillars/sections
- Asks to reformat, reaudit, restructure, deduplicate, or apply clarity/progressive-layer/why-scaffolding directives to an existing handbook
- Requests Directive 5/6/9 reformat, L1/L2/L3 layer injection, or WHAT/WHY/EXPECT scaffolding

## Core Workflow

### Phase 1: Source Ingestion

1. **Identify all referenced source documents.** The user will list them explicitly ("ingest these files"). Treat this as a mandatory checklist — every file must be read before generation begins.

3. **For large source files (>100K chars, exceeding read_file limits)**: Use grep/sed to locate and extract relevant sections without reading the entire file.

   **Pattern:**
   ```bash
   # Find all references to your target section
   grep -n "5\.3\|CDS\|target_keyword" /path/to/large_file.md | head -30
   
   # Extract a specific line range once boundaries are known
   sed -n 'START_LINE,END_LINEp' /path/to/large_file.md
   
   # Then use read_file(offset, limit) for manageable chunks
   ```
   
   This is faster than chunked read_file calls for files exceeding 100K chars and avoids wasting tokens on irrelevant content. For very large audit files (3,500+ lines), always grep first to find line numbers, then sed or read_file to extract only the relevant blocks.

3. **Download from Drive using one of two methods:**

   **Method A — OAuth (primary, full access):**
   ```bash
   python3 /opt/data/skills/productivity/google-workspace/references/drive-download-workaround.py FILE_ID [FILE_ID ...]
   ```
   Requires OAuth token at `/opt/data/google_token.json` (auto-refreshes). Full read/write/create/delete. Always prefer this.

   **Method B — Service Account (fallback, no create):**
   ```bash
   python3 /opt/data/skills/research/protocol-handbook-authoring/scripts/drive_sa_auth.py /root/.hermes/google_service_account.json FOLDER_ID
   ```
   Read + in-place-modify only. Cannot create new files (no storage quota). Only use when OAuth is unavailable. **Prerequisite:** the DETOXXX Drive folders must be shared (Viewer or Editor) with the service account email.

4. **Read the style template FIRST.** The document designated as the style template must be fully ingested before any other documents, because it defines every formatting convention that the generated output will inherit.

### Phase 2: Template Analysis

Before writing a single line, extract these elements from the style template:

- **Header hierarchy**: Count the `#` levels used. Note whether sections use `## 3.X — TITLE` or another pattern. Note whether sub-sections are lettered (`### 3.XA — Subtitle`).
- **Emphasis patterns**: Bold for key terms? Italics for what? Blockquotes for rules?
- **Table format**: Standard markdown tables with `|---|---|---|` separators? How many columns? What header style?
- **Numbered/bulleted lists**: Single-tier or nested? Bolded list items?
- **Cross-reference syntax**: How does the template refer to other sections? (e.g., "cross-referenced to Pillar 4", "see Section 2.1C")
- **Closing conventions**: How does the template end its sections? Is there an italicized closing line? A production note?
- **Tone markers**: Academic/clinical? Uses first-person plural? Uses "must" vs "should"? How does it cite evidence?

### Phase 3: Constraint Registration

Before writing, register all user-specified constraints:

1. **Blocker Rules** — These are non-negotiable. If a Blocker Rule says "cross-link QD metal degradation to Pillar 2 cadmium section," you must include an explicit subsection that does this before the output can be considered complete.

2. **Output boundaries** — The user will say "stop after Section 3.4." Respect this exactly. Do not generate one line past the boundary.

3. **Cross-reference targets** — List every cross-section reference the user requires. If they say "cross-link to chelation strategies in Pillar 2," identify the specific Pillar 2 sections (e.g., 2.1A Lead, 2.1C Cadmium, 2.3N Zinc) that must appear.

### Phase 4: Incremental Generation

1. **Generate in batches of 4-7 sections.** Writing an entire Pillar in one `write_file` call is fine for the first batch. For the remaining sections, write to a temp file then concatenate. Do NOT attempt to append large content via shell heredocs (see Pitfalls below).

2. **Pattern for large multi-batch generation:**
   - Batch 1: `write_file` → main file (e.g., `/root/DETOXXX_V2_Pillar_4_Working.md`) with first half of sections
   - Batch 2: `write_file` → temp file (e.g., `/tmp/pillar_4_remaining.md`) with remaining sections
   - Concatenate: `cat /tmp/pillar_4_remaining.md >> /root/DETOXXX_V2_Pillar_4_Working.md`
   - Validate: `wc -lc /root/DETOXXX_V2_Pillar_4_Working.md`

3. **Match sub-section structure exactly to the template.** If Section 3.1 has sub-sections 3.1A through 3.1F, then Section 3.3 should have sub-sections 3.3A through 3.3F with analogous content types.

4. **Standard sub-section pattern** (from the DETOXXX template):
   - 3.XA — Chemical Identity & Biological Entry Routes
   - 3.XB — Primary Mechanistic Toxicity
   - 3.XC — Tissue Tropism & Sequestration Patterns (with table)
   - 3.XD — Immune Evasion & Persistence Mechanisms
   - 3.XE — Specific mechanistic concern (varies by target)
   - 3.XF — Protocol Clearance Logic & Agent Cross-References

5. **Include a closing line** after the final section with Pillar-end marker, protocol version, and last-updated stamp.

6. **Include cross-Pillar dependency sections** (e.g., Section 4.7 links to Pillars 1, 2, 3, 5, 6). These are mandatory per the template structure.

### Phase 5: Validation

After writing, validate:
- All Blocker Rules are explicitly addressed with dedicated subsections or paragraphs
- Header hierarchy matches the template exactly
- At least one table is present per major section (matching template style)
- Cross-reference section numbers are correct (re-read the target sections to verify)
- Output stops exactly at the user-specified boundary
- Closing lines match template conventions
- Word count and line count align with the expected depth (Pillars average 1400-1800 lines)

### Phase 6: Drive Upload

After generation and validation, upload the completed document to Google Drive.

**Method A — OAuth (primary):**
```python
import json, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

with open('/opt/data/google_token.json') as f:
    td = json.load(f)
creds = Credentials(token=td['token'], refresh_token=td.get('refresh_token'),
    token_uri=td.get('token_uri','https://oauth2.googleapis.com/token'),
    client_id=td.get('client_id'), client_secret=td.get('client_secret'))
service = build('drive', 'v3', credentials=creds)

# Find pillar folder
results = service.files().list(
    q="name contains 'PILLAR X' and mimeType='application/vnd.google-apps.folder'",
    fields='files(id,name)').execute()
# Upload
with open('/root/DETOXXX_V2_Pillar_X_Working.md', 'rb') as fh:
    media = MediaIoBaseUpload(fh, mimetype='text/markdown', resumable=True)
uploaded = service.files().create(
    body={'name': 'DETOXXX_V2_Pillar_X_Complete.md', 'parents': [folder_id]},
    media_body=media, fields='id,name,webViewLink').execute()
```

**Method B — Service Account (fallback, no create — modify existing only):**
```python
import sys; sys.path.insert(0, '/opt/data/skills/research/protocol-handbook-authoring/scripts')
from drive_sa_auth import get_token
# Only works for updating existing files, not creating new ones
```

### Phase 5: Validation

After writing, validate:
- All Blocker Rules are explicitly addressed with dedicated subsections or paragraphs
- Header hierarchy matches the template exactly
- At least one table is present per major section (matching template style)
- Cross-reference section numbers are correct (re-read the target sections to verify)
- Output stops exactly at the user-specified boundary
- Closing lines match template conventions

### Phase 7: Structural Reform Audit (Directives 5/6/9)

After a handbook is assembled (or when the user requests reformatting for clarity, progressive layers, or why scaffolding), run the automated structural audit and apply the unified reformat template.

**1. Run the automated audit script:**

```bash
python3 /root/.hermes/skills/research/protocol-handbook-authoring/scripts/handbook-structural-audit.py /path/to/handbook.md --full
```

This detects: duplicate sections (H1/H2/H3 header collision count), L1/L2/L3 marker absence, wall-of-text blocks (>20 consecutive non-structural lines), WHAT/WHY separation (dosing before mechanism in first 30 lines of a subsection), out-of-order section numbering, voice violations (filler phrases — "importantly," "studies show"), and tableless sections.

**2. Map section boundaries before reading:**

For handbooks exceeding 10K lines, grep for section boundaries first — never attempt read_file on the whole file:
```bash
grep -n "^# \|^## " handbook.md
```
This produces a section boundary map, from which you can compute line ranges for targeted extraction.

**3. Extract representative sections with sed:**

```bash
sed -n 'START_LINE,END_LINEp' handbook.md
```

**4. Apply the unified reformat template:**

Every H2 section gets retrofitted to the pattern in `references/directive-569-refactor-template.md`:
- **L1 SCAN** — 60-second reference (Key Takeaway, DO, DON'T, DANGER). Mandatory for ALL H2 sections.
- **WHY** — 1-3 sentences of biochemical mechanism with named enzymes/pathways. Must precede dosing.
- **WHAT TO EXPECT** — Timeline of sensations, normal vs pathological response.
- **L2 READ** — Existing body content (mechanism, dosing tables, phase compatibility, contraindications, clinical vignettes, three choke points, cross-references).
- **L3 STUDY** — Evidence base, nuance/exceptions, advanced protocol modifications, controversies/gaps. Mandatory for architecture-critical, high-risk, and mechanism-controversial sections; optional for pure reference tables and front matter.

**5. Output format — FINDING → REPLACEMENT → RATIONALE:**

Every audit finding uses this format:
```
[PILLAR/SECTION] [LINE/PARA]
FINDING: [What's wrong]
REPLACEMENT: [Exact fix — text or structural change]
RATIONALE: [Why it matters]
```

**6. Implementation priority order:**

1. Deduplicate — Remove duplicate sections (highest user-facing improvement, typically 30%+ bloat)
2. Reorder — Fix out-of-sequence section numbering
3. Inject L1 SCAN — Every H2 section gets 60-second block
4. Inject WHY scaffolding — WHAT→WHY→EXPECT injection before dosing tables (for flagged sections)
5. Inject L3 STUDY — Deep-dive layer for clinical/research audience
6. Convert ASCII art — Wall-of-text decision trees → structured tables
7. Strip filler — Voice violations (never cosmetic — they signal incomplete editorial pass)
8. Table-augment — Add summary tables to the most-critical tableless sections

**7. Pitfall — shell heredocs with markdown content:**

Shell heredocs (`cat > file << 'EOF' ... EOF`) and `python3 << 'PYEOF'` with inline markdown content containing pipes (`|`), backticks (`), or angle brackets (`<`/`>`) fail with unhelpful shell errors. **Workaround for writing markdown to disk from shell context:** use `python3 << 'PYEOF'` with a raw string variable assignment (`content = r'''...'''`) and `open().write()`. This is reliable for markdown content with any special characters.

## References

- `references/detoxx-pillar-template.md` — Annotated breakdown of the Pillar 3 section template format used in DETOXXX V2
- `references/drive-folder-organization.md` — Drive folder structure, naming conventions, and merged file creation workflow for DETOXXX Handbook sections
- `references/directive-569-refactor-template.md` — Unified reformat template for Directive 5 (Clarity), Directive 6 (Progressive Layers L1/L2/L3), and Directive 9 (Why Scaffolding WHAT→WHY→EXPECT). Apply to any H2 section of a clinical protocol handbook.
- `scripts/drive_sa_auth.py` — Zero-dependency Google Drive API client using service account JWT + OpenSSL. Handles auth, list, download. Invoke: `python3 scripts/drive_sa_auth.py <sa_key.json> [folder_id]`. Fallback only — service accounts cannot create new files (no storage quota). Prefer OAuth for all operations.
- `scripts/handbook-structural-audit.py` — Automated structural quality audit for markdown protocol handbooks. Detects duplicates, missing layers, voice violations, WHAT/WHY separation, wall-of-text, out-of-order sections, and tableless sections. Usage: `python3 scripts/handbook-structural-audit.py <handbook.md> [--full]`.
- `references/handbook-deduplication-build-pattern.md` — Proven Python pattern for building a clean handbook from individual section files when the master handbook is a concatenation of multiple generation runs with 30-40% duplication. Covers: file inventory, version selection by mechanism density, pillar extraction with deduplication, section header insertion, and verification. Proven 2026-06-08: reduced 19,147 lines to 13,956 (27% reduction).

### Companion Document Cross-Reference Audit (Directives 11 + 23)

After a handbook is assembled, or when the user requests cross-referencing of pillars or companion documents, run the cross-reference audit methodology documented in `references/cross-reference-audit-methodology.md`. This covers:

1. **Cross-Pillar Co-Dependency Matrix** (Directive 11): Enumerate all 30 pillar-pair co-dependency sections. Verify each exists. Identify depth asymmetry — Pillar 2 co-dep sections are typically 5-10× thinner than other pillars and need a separate Build Tracker task. Identify mechanism-level body-text gaps where pathways intersect without navigation breadcrumbs.

2. **Companion Document Reference Map** (Directive 23): The handbook typically references the Agent Encyclopedia but has ZERO references to the Supplement Registry, Scientific Knowledge Base, or Audit Notes. For each pillar section, identify where each companion document should be referenced and generate inline reference text with one-sentence summaries.

3. **Bridge Text Generation**: For each missing cross-link, generate a self-contained bridge paragraph that names the specific mechanism, the clinical consequence of the missing link, and the exact section numbers to navigate to.

4. **Gap Severity Classification**: CRITICAL (missing safety-critical cross-link), HIGH (missing navigation breadcrumb for important mechanism), MEDIUM (missing reference to companion document).

The methodology was proven June 2026 against the 19,147-line DETOXXX V2 Master Handbook — found all 30 co-dep sections present, 12 missing body-text cross-links, and zero references to 3 companion documents.

### Drive OAuth Token Path — CORRECTED

The OAuth token lives at `/root/.hermes/google_token.json`, NOT `/opt/data/google_token.json`. The client secret is at `/root/client_secret_339939932247-mfmdg4cupg62nuectocd9g7tcq9g715h.apps.googleusercontent.com.json`. When the token expires (`RefreshError: invalid_grant`), fall back to the local file cache at `/opt/hermes/detoxxx_v2/` instead of retrying.

### Pitfalls

- **PITFALL — Section H1 headers required for audit visibility:** When building a handbook from individual section files (Section_8_Merged.md, section_1_front_matter.md, etc.), those files may lack `# Section N` H1 headers. Models auditing the assembled handbook (GLM-5.1, nemotron-3-ultra, etc.) scan for `^# Section \d` patterns to find sections. If a section's content exists but its H1 header is missing, the auditor will score it as "MISSING" — producing catastrophically low execution-ability scores (e.g., 25% when real score is 45-50%). **Fix:** After assembly, verify every section has a proper `# Section N — Title` H1 header. grep for `^# Section` and confirm 13 matches. Insert missing headers before running any model audit.

- **Shell heredocs reject `&` characters**: When trying to append content via `cat >> file << 'EOF' ... EOF` or `python3 << 'PYEOF' ... PYEOF`, any `&` in the content (common in acronyms like ADCC, R&D, and clinical abbreviations like CD4+ / CD8+) causes the terminal to reject the command as "Foreground command uses '&' backgrounding." Never use shell heredocs for handbook content. Use `write_file` to a temp file, then `cat` the temp file onto the main file. Cross-reference: `tool-efficiency` skill rule 2a.

- **Google Drive is the source of truth**: Local copies of handbook documents may be stale. Always re-download the master outline and style template from Drive before starting a generation session, even if local copies exist. The user maintains Drive as the authoritative repository.

- **OAuth is primary for Drive.** Token at `/opt/data/google_token.json`. Full read/write/create/delete. Service account at `/root/.hermes/google_service_account.json` is fallback only — it can read and modify-in-place but CANNOT create new files (storageQuotaExceeded). Always verify auth with: `python3 /opt/data/skills/productivity/google-workspace/scripts/setup.py --check`

- **Pipe characters in shell commands break heredocs**: The `|` in `files.list(q="name contains 'PILLAR|PILLAR X'...")` breaks shell quoting. Use the `drive_sa_auth.py` script imports instead of inline shell Python to avoid this entirely.

- **Sustained generation is token-intensive**: A single Pillar (10 sections) runs 1400-1800 lines and 140-200KB. Plan for 2 `write_file` calls per Pillar (batch 1 + batch 2). The full multi-Pillar loop (Pillars 4-6) produces ~500KB across 6 write calls.

- **here.now as Drive upload fallback:** When Google Drive uploads fail or the recipient cannot access Drive (e.g., external AI tools, collaborators without Drive access), publish files via the `here-now` skill: `bash ~/.hermes/skills/here-now/scripts/publish.sh /path/to/files --title "Title"`. This creates public URLs at `{slug}.here.now` accessible to anyone. Anonymous publishes expire in 24 hours.

- **Drive folder organization for batch output:** When generating multiple sections simultaneously, create a dedicated Drive folder structure under the handbook docs folder. Upload individual files to section-specific subfolders, then create merged files per section. After upload, move folders to top level and delete wrapper folders for clean organization.

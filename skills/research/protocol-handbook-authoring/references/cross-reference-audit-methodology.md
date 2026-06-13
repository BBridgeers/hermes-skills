# Cross-Reference Audit Methodology (Directives 11 + 23)

Systematic methodology for auditing pillar cross-references and companion document
references in assembled multi-section protocol handbooks. Proven June 2026 against
the DETOXXX V2 Master Handbook (19,147 lines).

## Directive 11 — Cross-Reference Pillars

Every Pillar must speak to every other Pillar where mechanisms intersect. Surface
missing cross-links. Generate the bridge text.

### Step 1: Map the Co-Dependency Matrix

Each of N pillars should have a co-dependency section with N-1 entries. For a
6-pillar handbook, that's 30 directional pairs:

```
grep -n "^\#\#\# [0-9]\.[0-9]*[A-E] — Pillar" HANDBOOK.md
```

Verify all 30 directional pairs exist. Note depth asymmetry — some pillars'
co-dep sections may be 5-10x thinner than others (1-2 sentences vs 200+ lines
with mechanism tables).

### Step 2: Search for Body-Text Mechanism Intersections

Co-dep sections are structural. The real gaps are in body text where a mechanism
crosses pillar boundaries without a navigation breadcrumb. Search for:

- Shared enzyme systems (CYP450, GST, GSH, MT)
- Shared immune pathways (NLRP3, TLR4, NF-kB, Th17)
- Shared transport systems (ASBT, OAT1/OAT3, NIS, B0AT1)
- Shared structural convergence points (fibrinogen, tight junctions, ECM)

For each hit, check if the paragraph includes a cross-link to the other pillar.
If a mechanism is described but the reader has no path to the related section in
another pillar, it's a gap.

### Step 3: Bridge Text Format

For each missing link, generate:

```
### [LINK N] PX→PY: Descriptive Title

**Location:** Pillar X, Section X.YZ
**Gap:** What exists vs what's missing

**BRIDGE TEXT:** Self-contained paragraph naming:
- The specific mechanism (named enzymes, pathways)
- The clinical consequence of the missing link
- The exact section numbers to navigate to

**RATIONALE:** Cross-link: Pillar Y, Section Y.AB — Specific Subsection Name
```

### Step 4: Depth Asymmetry Detection

Count lines per co-dep section. If any pillar's co-dep entries are <10% the
depth of others, flag as Priority HIGH. The bridge pillar (connecting biological
to chemical burden) should be the MOST detailed.

## Directive 23 — Cross-Reference Full Compendium

For every Pillar section, identify what companion documents should be referenced.
Generate the inline reference plus a one-sentence summary.

### Companion Documents to Check

1. **Agent Encyclopedia** — 127-agent dossiers with mechanisms, dosing, interactions, citations
2. **Supplement Registry** — Sourcing standards, purity verification, brand-tested equivalencies
3. **Scientific Knowledge Base** — Peer-reviewed primary literature for every biochemical claim
4. **Audit Notes (Execution Audit)** — Construction specifications, quality criteria, clinical vignette content

### Step 1: Count Existing References

```
grep -c "Agent Encyclopedia\|Companion Volume\|Registry\|Knowledge Base\|Audit Notes" HANDBOOK.md
```

Typically, the Agent Encyclopedia is referenced 10-15 times. The other three have
ZERO references.

### Step 2: Map Reference Points Per Section

For each major section, identify what companion document content is directly
relevant:

- **Agent Encyclopedia references** go where agents are first introduced or dosed
- **Supplement Registry references** go where agent sourcing/safety is discussed
- **Scientific Knowledge Base references** go where mechanism claims need evidence backing
- **Audit Notes references** go at section openings (construction spec) and where quality criteria are defined

### Step 3: Inline Reference Format

```
### [PILLAR-REF-N] Pillar N, Section X.YZ — Topic

**INLINE REFERENCE:**
> 📚 **Companion Document Name:** Specific content relevant to this section —
> named agents with mechanisms, specific studies with findings, specific
> sourcing standards with purity thresholds, specific audit criteria with
> required structural elements.

**One-sentence summary:** What the companion document provides that the
handbook reader needs at this exact point.
```

### Step 4: Global Architecture References

Add 3 global references that apply to the entire handbook:
1. Every Section Opening → Audit Notes (construction spec)
2. Every Agent Introduction → Agent Encyclopedia (full dossier)
3. Every Cross-Reference Point → All 4 companion documents (architecture overview)

## Common Findings (from June 2026 Audit)

### Directive 11 — Common Missing Cross-Links

1. **Parasitic sequestration of non-metal toxins** (P1→P6: metallothioneins bind glyphosate too)
2. **CYP450 as shared infrastructure** (P2→P6: metal inhibition blocks chemical clearance)
3. **Immune evasion mechanisms co-opted across pillars** (P1→P3: exosomes as nanoparticle carriers)
4. **Morphotype switching triggered by one pillar's targets** (P2→P5: cadmium → hyphal Candida)
5. **Transporter competition between pillars** (P6→P2: PFAS displacing chelated metals at ASBT)
6. **Fungal CYP450 as distributed bioactivation engine** (P5→P6: Aspergillus oxidizing VOCs faster than human CYP2E1)

### Directive 23 — Always-Missing References

- **Supplement Registry**: 0 references in every audit. The handbook discusses agents
  extensively but never links to sourcing verification.
- **Scientific Knowledge Base**: 0 references. Mechanism claims have no evidence breadcrumbs.
- **Audit Notes**: 0 references. Handbook sections have no construction spec links.

## Pitfalls

- **OAuth token expiration blocks Drive downloads.** When `RefreshError: invalid_grant`
  occurs, fall back to local file cache at `/opt/hermes/detoxxx_v2/` — do not retry.
  The service account can read but not create.
- **Terminal blocks long commands.** When writing audit documents >10K chars, use
  `python3 -c "..."` or `python3 /dev/stdin << 'EOF'` with small payloads (~500-1000
  chars each). For large documents, write in 30-40 small append operations.
- **Don't read_file a 19,000-line handbook.** Use grep/sed for targeted extraction:
  `grep -n "^##\|^###" HANDBOOK.md` for structure, `sed -n 'START,ENDp'` for content.

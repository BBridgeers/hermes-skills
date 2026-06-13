# Directive 5/6/9 Unified Reformat Template

Use this template to retrofit any H2-level section of a clinical protocol handbook with
Directive 5 (Clarity), Directive 6 (Progressive Layers), and Directive 9 (Why Scaffolding)
simultaneously. The template is a complete section wrapper — insert existing L2 content
in the marked area.

## The Unified Template

```
## X.Y — Section Title

**▌L1 SCAN — 60 Seconds ▌**
- **Key Takeaway:** [One sentence — what this section is about]
- **DO:** [1-3 bullet action items]
- **DON'T:** [1-2 bullet prohibitions]
- **⚠️ DANGER:** [Stop condition if applicable — omit if not safety-critical]

> **Bridge Box — What This Means:** [Household metaphor, 4-6 sentences, actionable. Only if section is for general audience. Omit for clinician-only sections.]

---

**WHY this works:** [1-3 sentences — biochemical mechanism, named enzymes, pathway rationale. Answer: why does this agent/technique/procedure produce the outcome it does?]

**WHAT TO EXPECT:** [Timeline of sensations, normal vs abnormal response, when to be concerned, when to escalate. Answer: what will the patient feel, and when?]

---

[EXISTING L2 READ CONTENT HERE — mechanism, dosing tables, phase compatibility, contraindications, clinical vignettes, three choke points interface, cross-references. This is the existing body of the section.]

---

**▌L3 STUDY — Deep Dive ▌**
- **Evidence Base:** [Key studies, data sources, citation counts, recency]
- **Nuance & Exceptions:** [Edge cases, special populations, Tier-dependent modifications]
- **Advanced Protocol:** [Off-label applications, research-grade modifications, clinician extensions]
- **Controversies & Gaps:** [What's unproven, what's speculative, what needs more data, what would falsify]
```

## Implementation Rules

1. **L1 is mandatory for every H2 section.** No exceptions. Even a 3-line L1 is better than none.
2. **L3 is mandatory for:**
   - Architecture-critical sections (Phase Maps, Pillar matrices, Gate systems)
   - High-risk tactical protocols (CDS, chelation, colloidal silver)
   - Sections with controversial or speculative mechanisms
   - Sections that a clinician or researcher would want to verify
3. **L3 is optional for:**
   - Pure reference tables (binder compatibility grids, redox window matrices)
   - Front matter (dedication, copyright, how-to-use)
   - Table of contents
4. **Bridge Box** is mandatory for sections a patient or household operator might read. Omit for clinician-only or researcher-only sections.
5. **WHY must precede WHAT (dosing/procedure).** Never place dosing instructions before the mechanism that justifies them. The WHY paragraph uses named enzymes, bond chemistry, and pathway detail — it is not "X is important because Y" — it is "CYP2E1 metabolizes X to Y, which binds Z receptor, producing A outcome."
6. **WHAT TO EXPECT must follow WHY.** The reader needs to know what is normal and what is pathological BEFORE they execute the protocol. This prevents unnecessary Herxheimer stops and unsafe dose escalations.

## Finding → Replacement → Rationale Format

When auditing existing sections, use this format for each finding:

```
[PILLAR/SECTION] [LINE/PARA]
FINDING: [What's wrong — missing layer, separated WHAT/WHY, duplication, voice violation]
REPLACEMENT: [The exact text or structural change that fixes it]
RATIONALE: [Why this matters — clinical safety, usability, architectural integrity, voice standard]
```

## Known Pitfalls

- **Do not add L3 to sections that are pure reference tables.** The binder compatibility matrix and redox window table don't need "evidence base" — they ARE the evidence.
- **Do not duplicate the Bridge Box metaphor pattern across adjacent sections.** If Section 5.3 uses "building demolition" for CDS, Section 5.4 should not also use "building demolition" for colloidal silver. Use `search_files` to check for metaphor collisions before writing.
- **L1 bullets are NOT a table of contents.** They are the minimum a panicked person needs at 2 AM. If the section describes a stop condition, the L1 must include it. If the section describes a dose, the L1 must include the starting dose.
- **WHAT TO EXPECT is clinical, not motivational.** "You may feel tired" is worthless. "Grade 1-2 fatigue peaks at Day 3-5 as endotoxin (LPS) from gram-negative parasite die-off activates TLR4 on macrophages, producing transient IL-6 and TNF-α elevation. This resolves as the parasite load decreases and does not indicate protocol failure" is useful.

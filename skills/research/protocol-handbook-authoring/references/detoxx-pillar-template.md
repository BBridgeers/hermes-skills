# DETOXXX Pillar Section Template — Annotated Breakdown

This reference documents the exact formatting conventions of the DETOXXX V2 Pillar 3 template (from `DETOXXX_V2_Pillar_3_Sections_1_and_2.md`), used as the style authority for all Pillar content generation.

## Header Hierarchy

```
# DETOXXX V2 PROTOCOL HANDBOOK
## CHAPTER: THE SIX TARGET PILLARS
### PILLAR 3 — SYNTHETIC BIOLOGY, NANOMATERIALS, HYDROGELS & QUANTUM DOTS
#### *Complete Granular Expansion — Sections 3.X–3.Y — Final Locked Version*
```

Key rules:
- `#` H1 is reserved for the handbook title (one per file)
- `##` H2 is the chapter/domain (one per pilllar file)
- `###` H3 is the pillar name
- `####` H4 is the document subtitle (italic, locked version declaration)
- Section headers within the pillar use `## 3.X — TITLE IN CAPS`
- Sub-sections use `### 3.XA — Subtitle With Key Terms Bolded`

## Horizontal Rule Convention

`---` is used to separate major sections. It appears:
- After the taxonomy rule blockquote
- After the "Why This Pillar Exists" section
- Between major numbered sections (between 3.1 and 3.2, etc.)

## Blockquote Convention

```markdown
> **Foundational Taxonomy Rule (Locked):** ...
```

Blockquotes contain locked rules, taxonomy boundaries, and non-negotiable structural constraints. They use bold labels followed by explanatory text.

## Emphasis Patterns

- **Bold**: Used for key terms on first introduction, mechanism names, agent names, and critical clinical points.
- *Italic*: Used only in document subtitles and closing notes.
- No inline code formatting for chemical formulas — Cd²⁺, Pb²⁺, O₂•⁻ written directly.
- Superscripts/subscripts use Unicode characters (², ₃, •⁻, etc.), not HTML tags.

## Table Format

All tables use the standard markdown format:

```markdown
| Column 1 | Column 2 | Column 3 |
|---|---|---|
| Value | Value | Value |
```

- Every cell has leading and trailing spaces around the pipe.
- Header row is capitalized.
- No bold in table cells.

## Numbered Lists

Multi-tier numbered lists use:
- **Bold lead-in** followed by a dash and explanation
- Nested bullets under numbered items
- Consistent indentation

## Cross-Reference Syntax

- "cross-referenced to Pillar 4"
- "see Section 3.1D"
- "(Cross-Pillar 2 mechanism)"
- "Pillar 2, Section 2.1C"
- "detailed in Pillar 2, Section 2.3N"

Always include both the Pillar number AND the specific section number.

## Sub-Section Pattern

Each numbered section (3.1, 3.2, 3.3, etc.) follows this exact pattern:

- **3.X — TITLE** : 1–3 paragraph overview introducing the class of material
- **3.XA — Chemical Identity & Biological Entry Routes** : Chemical composition, entry routes listed as bold-tagged bullets
- **3.XB — Primary Mechanistic Toxicity** : Numbered list (1–7 typical) of toxicity mechanisms, each with bold title and paragraph explanation
- **3.XC — Tissue Tropism & Sequestration Patterns** : Markdown table + a critical sequestration insight paragraph in bold-tagged format
- **3.XD — Immune Evasion & Persistence Mechanisms** : Numbered list of evasion strategies
- **3.XE — Specific Mechanistic Concern** : Varies by target — for QDs it's the Pillar 2 cross-link, for hydrogels it's enzymatic disruption
- **3.XF — Protocol Clearance Logic & Agent Cross-References** : Mechanism-based clearance strategy (numbered 1–4) with agent lists, timing rules, and phase assignments

## Agent Naming Convention

- Agent name followed by dosage in parentheses: **NAC (600mg)**
- Bold agent name, non-bold dosage
- Timing rules set as bulleted sub-items under agents

## Closing Conventions

```markdown
*Sections 3.X and 3.Y complete. Sections 3.Z ... to follow in subsequent generation passes.*

---

**Structural Note for Production Team:** ...
```

The structural note is mandatory — it documents what was generated, confirms template fidelity, and lists what follows.

## Phase Map Cross-Reference

When referencing protocol phases, use:
- Phase X (Days Y–Z) — e.g., Phase 3 (Days 22–35)
- Phase colors may be referenced but aren't required in Pillar content
- Agent phase assignments use the format: "enters at Phase 3 (Day 22), reaches full dose by Phase 4 (Day 28–36)"

## Tone Rules

- PhD-level clinical depth — assume reader has graduate-level biology/chemistry literacy
- Definitive, not speculative — "is," not "may be" unless genuinely uncertain
- Mechanism-first: name the mechanism before discussing its consequences
- No first-person outside of the locked blockquotes
- No marketing language, no wellness-generalist framing
- Chemical specificity over clinical generalities — "Cd²⁺ inhibits Complex III of the ETC" not "cadmium damages mitochondria"

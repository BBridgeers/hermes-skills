# Directive 3 + 13 Audit Methodology

Proven methodology for auditing DETOXXX V2 Handbook sections for 5-question completeness (Directive 3) and evidence-tier labeling (Directive 13). Developed June 2026 against the 19,147-line MASTER HANDBOOK — found 34 completeness gaps and 14 evidence-tier actions.

## Directive 3 — Completeness Audit (5 Questions)

Every Pillar, tactical protocol, and major section MUST answer these 5 questions. These are not optional — they are the patient's minimum orientation framework.

### The 5 Questions

1. **What am I doing?** — What does this Pillar/protocol/section do? (Pillar Overview, Classification & Exposure)
2. **Why?** — Why does this matter? (Prevalence, clinical significance, rationale)
3. **What will I feel?** — What is the expected experience during execution? (Bounded range of normal, differentiation from abnormal)
4. **What if it goes wrong?** — What are the adverse events, failure modes, troubleshooting, stop criteria?
5. **What if I skip it?** — What are the consequences of omission or severe under-delivery? (Tie to Three Choke Points, sequential architecture)

### Detection Patterns (grep-friendly)

Strongest single-regex per question:

```
# Q1 - What am I doing?
grep -iP 'Pillar\s+Overview|Classification\s+&|What\s+It\s+Is' FILE.md

# Q2 - Why?  
grep -iP 'rationale|justification|significance|importance|clinical\s+relevance' FILE.md

# Q3 - What will I feel?
grep -iP 'what\s+(you|to)\s+(will\s+)?(feel|expect|experience)|expected\s+(response|experience)' FILE.md

# Q4 - What if it goes wrong?
grep -iP 'HARD\s+GATE|emergency\s+stop|adverse\s+(reaction|event)|clinical\s+vignette|complication' FILE.md

# Q5 - What if I skip it?
grep -iP 'what\s+if\s+(i|you)\s+skip|consequences?\s+of\s+(not|skipping|omitting)|without\s+this\s+(pillar|phase)' FILE.md
```

### Scan Script (Python — works on files of any size)

```python
import re

with open('FILE.md', 'r') as f:
    lines = f.readlines()

# Define pillar/section boundaries as (name, start_line, end_line) 0-indexed
sections = [
    ('Pillar 1', 5063, 5322),
    # ... add all sections
]

completeness_patterns = {
    'what': r'(?i)Pillar\s+Overview|Classification\s+&',
    'why': r'(?i)rationale|justification|significance|importance',
    'feel': r'(?i)what\s+(you|to)\s+(will\s+)?(feel|expect)|expected\s+(response|experience)',
    'wrong': r'(?i)HARD\s+GATE|emergency\s+stop|adverse\s+(reaction|event)|clinical\s+vignette',
    'skip': r'(?i)what\s+if\s+(i|you)\s+skip|consequences?\s+of\s+(not|skipping|omitting)',
}

for name, start, end in sections:
    section_text = ''.join(lines[start:end])
    missing = []
    for qkey, pattern in completeness_patterns.items():
        if not re.search(pattern, section_text):
            missing.append(qkey)
    if missing:
        print(f"GAP: {name} — missing: {', '.join(missing)}")
```

### Q3 (Feel) — What Makes a Good Answer

The "What will I feel?" answer must:
- Give a BOUNDED range of normal (e.g., "symptoms peak 24-72 hours after escalation and subside — not worsen")
- Explicitly differentiate between normal die-off and abnormal toxicity
- List specific STOP criteria (not vague "if you feel bad, stop")
- Reference the Herxheimer Survival Algorithm (Section 5.1) for the decision tree
- Use Bridge Box format for patient accessibility

Pattern from June 2026 audit:
```
> **What You Will Feel During [Pillar X]:** The expected experience is [pattern].
> Expected: [symptoms A, B, C]. These are normal within the first [N] hours.
> What is NOT normal: [symptoms D, E, F]. These are STOP criteria.
```

### Q5 (Skip) — What Makes a Good Answer

The "What if I skip it?" answer must:
- Tie the omission consequence to the Three Choke Points framework (GSH system, Mitochondrial ETC, Structural Protein Integrity)
- Explain why downstream phases cannot compensate for upstream omission — the sequential architecture rationale
- Name the specific toxin class or mechanism that persists without intervention
- Avoid scaremongering — state biochemical consequences, not emotional appeals

## Directive 13 — Evidence Tier Labeling

### The 4 Tiers

| Tier | Definition | Detection |
|------|-----------|-----------|
| **Clinical Trial** | Randomized controlled human study cited | `grep -iP 'RCT|randomi[sz]ed|controlled\s+trial|placebo.controlled'` |
| **Case Series** | Multiple documented cases / observational human data | `grep -iP 'human\s+(subject|study|trial)|clinical\s+(trial|study)|patient\s+(series|cohort)'` |
| **Mechanistic Inference** | Biochemical logic, in vitro, animal models | Default tier — mechanism described but no human trial data |
| **Anecdote** | Individual reports, practitioner experience | `grep -iP 'case\s+report|anecdot|personal\s+experience|practitioner\s+report'` |

### Claim Categories That Need Tier Labeling (Priority Order)

1. **Glyphosate-GlyRS substitution claims** — highest priority. The "2-3 percent error frequency" at GlyRS is the single most load-bearing mechanistic claim in the handbook. It underlies the Fibrinogen-Glyphosate-Spike axis. NO citation exists. Must be explicitly qualified as model-based mechanistic inference.

2. **CDS/ClO2 efficacy claims** — no human trials cited. FDA/EPA/EMA classify ClO2 as disinfectant, not therapeutic. Acknowledge mainstream regulatory position.

3. **Colloidal silver claims** — FDA/WHO positions already acknowledged (good). Argyria thresholds and half-life are model-based estimates.

4. **Chelation cycling architecture** — DMSA/DMPS/ALA have FDA-approved indications for specific poisonings. The protocol's 3-ON/4-OFF cycling for chronic body burden is protocol-derived, not trial-supported.

5. **GO/CNT/QD toxicity** — strongest evidence. Peer-reviewed literature exists. Add example citations.

6. **EMF-nanomaterial interaction** — weakest evidence. Emerging field with limited human data.

### Model-Based Numeric Estimates — Must Be Prefixed

When these numbers appear without qualification, flag them. They need "model-based estimate" or "WHO estimate" prefix:

- Hepatic GSH pool "10-15 grams" (appears 10+ times)
- Population prevalence numbers (billions/millions)
- Glyphosate substitution rates (2-3 percent)
- Argyria threshold grams
- Eosinophil GSH depletion percentages
- Chelator ATP reduction percentages

Pattern: search for `(estimated|approximately|roughly|about)` near numeric values.

### Evidence Tier Transparency — Gold Standard

The Morgellons section (Pillar 3, Section 3.5) is the gold standard for evidence-tier transparency in the handbook. It explicitly states:
- "This section explicitly acknowledges the limitation: the field lacks a unified, peer-reviewed consensus..."
- "The protocol addresses them with appropriate scientific caution: naming what is documented, distinguishing observation from interpretation..."
- "This protocol takes no position on the self-replication hypothesis beyond noting that it remains unresolved..."

This pattern should be replicated for ALL uncertain claim domains: CDS efficacy, glyphosate substitution mechanisms, EMF-nanomaterial interactions, colloidal silver biofilm claims.

### Evidence Tier Scan Script

```python
import re

with open('FILE.md', 'r') as f:
    content = f.read()

# Evidence indicators
has_citation = bool(re.search(r'(?i)\[\d+\]|\(\d+\)|ref\.|published|study|trial|RCT|meta.analysis|DOI|PMID', content))
has_invitro = bool(re.search(r'(?i)in\s*vitro|cell\s+(line|culture)|animal\s+(model|study)|murin|rat|mouse', content))
has_human = bool(re.search(r'(?i)human\s+(subject|study|trial)|clinical\s+(trial|study)|patient\s+(series|cohort)', content))
has_mechanistic = bool(re.search(r'(?i)mechanism|pathway|biochemical|molecular|enzyme|receptor', content))

# Tier determination
if has_human and re.search(r'(?i)RCT|randomi[sz]ed|controlled\s+trial', content):
    tier = 'clinical_trial'
elif has_human and has_citation:
    tier = 'case_series'
elif has_citation or has_mechanistic:
    tier = 'mechanistic_inference'
elif has_invitro:
    tier = 'mechanistic_inference'
else:
    tier = 'anecdote'

# Flag model-based estimates
model_estimates = re.findall(
    r'(estimated|approximately|roughly|about)\s+[\d,]+\s*(billion|million|thousand|\%|percent|years|grams|mg)',
    content)
if model_estimates:
    print(f"MODEL-BASED ESTIMATES (need prefix): {model_estimates}")

# Check for mainstream dispute acknowledgment
disputes = {
    'CDS': (r'CDS|ClO2|chlorine\s+dioxide', r'FDA|EPA|EMA|regulatory|not\s+approved'),
    'colloidal silver': (r'colloidal\s+silver|silver\s+nanoparticle', r'FDA|WHO|regulatory|not\s+GRASE'),
    'EMF': (r'EMF|electromagnetic\s+field', r'uncertain|emerging|limited\s+data|debate'),
}
for claim_type, (claim_regex, dispute_regex) in disputes.items():
    has_claim = bool(re.search(claim_regex, content, re.IGNORECASE))
    has_dispute = bool(re.search(dispute_regex, content, re.IGNORECASE))
    if has_claim and not has_dispute:
        print(f"EVIDENCE GAP: {claim_type} claims present but no mainstream dispute acknowledgment")
```

## Complete Audit Workflow

1. **Get handbook** — download from Drive if not local. The MASTER HANDBOOK is at `/opt/hermes/detoxxx_v2/DETOXXX_V2_MASTER_HANDBOOK.md` (19K+ lines, 2.3MB).

2. **Extract pillar boundaries** — grep for `^# PILLAR` and `^## 6\.` headers to map section line ranges.

3. **Run 5-question scan** — use the Python script above. Flag every missing question per Pillar.

4. **Run evidence tier scan** — for each claim category of interest (CDS, colloidal silver, chelation, GlyRS, GO/CNT/QD, EMF), determine evidence tier and check for dispute acknowledgment.

5. **Generate replacement text** — for each gap found, write replacement text that:
   - Uses DETOXXX V2 voice (named enzymes, clinical precision, no hedging)
   - Specifies exact insertion point (line number, after/before specific heading)
   - Includes rationale explaining why this text closes the gap

6. **Prioritize** — Critical: safety-sensitive gaps (Q4 "what if it goes wrong"). High: patient-experience gaps (Q3 "feel"), architecture-rationale gaps (Q5 "skip"). Medium: citation additions, softening language.

7. **Format output** — Use `[SECTION] [LINE/PARA] FINDING -> REPLACEMENT -> RATIONALE` format for each finding.

## Pitfalls

- **The "feel" question is NOT the same as clinical vignettes.** Clinical vignettes tell failure stories. The "feel" question tells the expected-experience story. Both are needed — they serve different functions. Many sections have vignettes but no expected-experience description.

- **The "skip" question is NOT the same as "why."** "Why" justifies the Pillar's existence. "Skip" explains the consequences of NOT executing it — tying to downstream architecture. These are distinct.

- **Evidence-tier labeling is NOT about removing claims.** It's about qualifying them. A mechanistic inference claim is still valid content — it just needs to be labeled as such. The goal is transparency, not deletion.

- **The Morgellons section is the template, not an outlier.** Its explicit acknowledgment of scientific uncertainty should be replicated across ALL uncertain claim domains, not treated as a one-off.

- **GlyRS substitution claim is the highest-leverage single fix.** Softening this one claim with evidence-tier language improves credibility across 4+ sections that reference it.

# Directive 10 + 12 Audit Methodology — Mechanism Chains + Citation Density

Proven methodology for auditing DETOXXX V2 Handbook sections for mechanism-chain completeness (Directive 10) and citation density / evidence-tier qualifiers (Directive 12). Developed June 2026 against the 38,294-line, 4.6MB MASTER HANDBOOK — identified 18 actionable findings across both directives.

## Pre-Audit: Handbook Retrieval & Structural Map

1. Download the full handbook: `rclone cat "gdrive_personal:DETOXXX/DETOXXX V2 HANDBOOK DOCS/DETOXXX_V2_MASTER_HANDBOOK.md" > /tmp/handbook_full.md`
2. Check for duplicate concatenation: `grep -n "^# Section [0-9]" /tmp/handbook_full.md` — if each section number appears twice with ~19K-line offset, the handbook is duplicated. Note this before patching.
3. Map section boundaries: `grep -n "^# Section \|^# PILLAR " /tmp/handbook_full.md`

## Directive 10 — Mechanism Chain Verification

### What Makes a Mechanism Chain Complete

A mechanism chain goes from **agent/toxin** through **specific intermediate step(s)** to **observed effect**, naming enzymes, receptors, transporters, bond chemistry at each step.

**COMPLETE (gold standard):**
> TNF-α binding to TNFR1 activates sphingomyelinase → generating ceramide → directly inhibits Complex III (cytochrome bc1 complex) at the Qo site → blocking electron transfer from ubiquinol to cytochrome c → generating reverse electron flow (REF) at Complex I → massive superoxide production.

**INCOMPLETE (needs cascade):**
> Microplastics interact with mitochondria, disrupting electron transport and generating mitochondrial ROS.

Missing: HOW they interact. At which Complex? Via what molecular mechanism?

### Scan 1: Find Claims That State Effect Without Cascade

Target: statements where a toxin or agent "causes/disrupts/inhibits/triggers" an effect but the intermediate mechanism is missing.

```bash
# Find "X inhibits Y" or "X disrupts Y" patterns
grep -n -i "inhibit\|disrupt.*barrier\|disrupt.*membrane\|disrupt.*function\|impairs.*function" \
  handbook.md | grep -v "CYP\|GPx\|GST\|Complex\|ETC\|NADPH\|caspase\|apoptosis\|kinase\|receptor\|channel\|transporter\|enzyme\|synthase\|polymerase\|hydrolase\|peroxidase\|reductase\|dehydrogenase\|ATPase\|ATP"
```

### Scan 2: Find Numeric Claims Without Derivation

Target: precise numbers presented as constants but actually model-based estimates.

```bash
# Glyphosate-GlyRS substitution rate — the #1 gap
grep -n -i "glyphosate\|glyrs\|glycine substitution\|2.3 percent\|2-3 percent\|error frequency" handbook.md

# Model-based estimates without qualifier
grep -n -i "estimated.*[0-9]\|approximately [0-9].*gram\|about [0-9].*pool" handbook.md
```

**Known model-based estimates in the handbook (need qualifiers):**
- Hepatic GSH pool "10-15 grams" — appears 64+ times. Derived from hepatic concentration × tissue mass.
- Glyphosate "2-3% error frequency" at GlyRS — in silico modeling, not measured.
- Argyria threshold grams — literature ranges are wide.
- Eosinophil GSH depletion percentages.
- Chelator ATP reduction percentages.
- Population prevalence numbers (billions/millions of infections).

### Scan 3: Find Hedging Language — Is It Appropriate or Gapping?

```bash
grep -n -i "research suggests\|studies suggest\|thought to\|may be due\|evidence suggests\|appears to\|is hypothesized\|currently unknown\|mechanism.*unclear\|poorly understood\|not fully understood" handbook.md
```

**Rule:** If the handbook says "poorly understood" or "mechanism is unclear," that's appropriate for genuinely uncertain topics. If it states a precise claim with no cascade and no citation, that's a gap.

### Scan 4: Check Named-Enzyme Density Per Section

Sections with zero named enzymes in mechanism claims are underbuilt. For each section:

```bash
# Count enzyme/pathway references in a section
sed -n 'SECTION_START,SECTION_ENDp' handbook.md | grep -c "CYP\|GPx\|GST\|Complex [IVX]\|NADPH\|caspase\|kinase\|receptor\|channel\|transporter\|synthase\|polymerase\|hydrolase\|peroxidase\|reductase\|dehydrogenase"
```

### How to Build a Missing Cascade

When a claim states "X causes Y" without intermediates:

1. **Identify the biological compartment** — where does the toxin accumulate? (mitochondria, plasma membrane, cytosol, ECM)
2. **Identify the molecular target** — what does it bind to? (specific enzyme active site, receptor domain, lipid bilayer, DNA)
3. **Trace the consequence chain** — what happens after binding? (enzyme inhibition → substrate accumulation → downstream pathway stall → cellular effect)
4. **Name everything** — every enzyme, every receptor, every transporter. No "liver enzyme" — always "CYP2E1."
5. **Add an evidence tier label** — is this measured in humans? In vitro? In silico?

## Directive 12 — Citation Density Audit

### Scan 5: Citation Count

```bash
grep -c -i "DOI\|PMID\|doi.*10\.\|pubmed\|ncbi\|nlm\.nih\|\[[0-9]\+\]" handbook.md
```

A handbook making thousands of specific biochemical claims should have more than single-digit citation markers.

### Scan 6: Evidence-Tier Qualifiers

```bash
grep -c -i "evidence tier\|mechanistic inference\|model-based estimate\|WHO estimate\|clinical trial tier\|case series tier\|anecdotal tier\|evidence status\|evidence level" handbook.md
```

If zero, the handbook lacks any systematic evidence labeling.

### Scan 7: Specific Citations for Load-Bearing Claims

For the most critical numeric/half-life/prevalence claims, check if they have source attribution:

| Claim Type | What to Check | Expected Source |
|---|---|---|
| Toxin half-lives | PFOA 2.3-3.8 years, TCDD 7-11 years, Cd 10-30 years | EPA, WHO/IPCS, peer-reviewed PK studies |
| Prevalence numbers | 1.5B nematode infections, 280M Giardia | WHO fact sheets |
| IARC classifications | Group 1, Group 2B carcinogens | IARC monograph volume numbers |
| Chelator stability constants | log K values for EDTA, DMSA, DMPS | Martell & Smith Critical Stability Constants |
| Enzyme inhibition kinetics | Complex III ceramide inhibition, STAT3/GRIM-19 | Peer-reviewed biochemistry (JBC, Science, etc.) |
| Clinical thresholds | GSH pool size, argyria dose | Model-based estimate vs. measured |

### Scan 8: Regulatory Position Disclosures

For therapeutic claims that conflict with regulatory classifications, check if the handbook discloses the regulatory position:

```bash
# CDS/ClO2 — should mention FDA/EPA classification
grep -n "CDS\|ClO2\|chlorine dioxide" handbook.md | head -20
# Then check if FDA/EPA/EMA appear in those sections
grep -n "FDA\|EPA\|EMA\|regulatory\|not approved\|disinfectant" handbook.md | head -20
```

### Scan 9: Self-Consistency — Audit vs. Body Text

If the handbook has an internal audit section (e.g., Directive 2+22 execution output), the audit findings must match the body text. Check:

```bash
# Does the audit section qualify claims that the body text presents as hard facts?
grep -n "unquantified\|not.*demonstrated\|no.*human.*data\|mechanistically plausible" handbook.md
```

If the audit text is more cautious than the body text, the body text needs updating to match the audit.

### Scan 10: Duplicate Detection

```bash
grep -n "^# Section " handbook.md
# If each section number appears twice with a ~19K-line gap, the document contains two concatenated copies
```

## The 4-Tier Evidence Framework

Every claim in the handbook should fall into one of these tiers. The tiers should be defined in a front-matter "Evidence Framework" section so readers know what standard applies:

| Tier | Name | Detection | Example |
|------|------|-----------|---------|
| T1 | Clinical Trial | RCT, systematic review, meta-analysis | NTP 2024 fluoride/IQ |
| T2 | Case Series | Multiple human cases, observational data | Clinical vignettes (n=1) |
| T3 | Mechanistic Inference | In vitro, animal models, in silico | GlyRS docking studies, GSH pool estimates |
| T4 | Protocol-Derived | Practitioner experience, architecture design | Phase sequencing, cycling rules |

**Default tier for most handbook claims is T3.** This is not a weakness — it's a transparency requirement.

## Replacement Text Standards

When generating replacement text for gaps found:

1. **Use named enzymes and pathways** — never generic terms
2. **Add evidence-tier label** in brackets at the end: `[Evidence tier: Mechanistic Inference — in vitro only.]`
3. **Name the experimental basis** when known: "TEM in HepG2 cell lines," not "experimentally verified"
4. **Admit uncertainty explicitly** when appropriate: "in vivo frequency unquantified," not "approximately"
5. **Specify exact insertion point** — line number, before/after which heading

## Priority Matrix

| Risk | Fix Now | Fix Before Distribution |
|---|---|---|
| Precise number without source | Yes | Yes |
| Model estimate presented as measurement | Yes | Yes |
| No evidence-tier labeling system | — | Yes |
| Foundational safety claim without trial support | — | Yes |
| Missing cascade (named enzyme, step) | — | Yes |
| Minor citation gap | — | Optional |

## Pitfalls

- **The Herxheimer sections are NOT the problem.** They have the best mechanism chains in the handbook. The gap is citation, not biochemistry. Don't dilute them with qualifiers that undermine their authority.
- **The Morgellons section is the gold standard for uncertainty.** Its pattern of "may be attributable to: (a)... (b)... or (c)" should be replicated elsewhere, not fixed.
- **The audit text and body text must agree.** If the audit qualifies a claim (e.g., GlyRS substitution "unquantified"), the body text must match. Internal contradiction is worse than either version alone.
- **Don't strip "approximately" without adding epistemic labeling.** The fix is "approximately 10-15 grams [model-based estimate from hepatic GSH concentration × tissue mass]" — not removing the qualifier.
- **This audit methodology assumes a 19K+ line handbook.** For sections under 500 lines, direct read_file may work. For sections over 1,000 lines, grep/sed targeted extraction is mandatory.

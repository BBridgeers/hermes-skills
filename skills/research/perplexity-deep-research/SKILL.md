---\nname: perplexity-deep-research\ndescription: [SUPERSEDED by deep_research_r1_tavily] High-volume autonomous deep inquiry using Perplexity's sonar-deep-research model with iterative gap analysis.\ntags: [research, deep-research, perplexity, analysis, investigation, SUPERSEDED]\n---\n\n> **SUPERSEDED (2026-05-04)**: This skill lacks a valid PERPLEXITY_API_KEY.\n> Use the **`deep_research_r1_tavily`** skill instead — configured in\n> `/root/.hermes/config.yaml` under `skills:`. It uses DeepSeek reasoning\n> models + Tavily live web search, achieving the same multi-pass deep research\n> with working credentials.

# Perplexity Deep Research — Autonomous Iterative Inquiry

> Trigger: `perplexity-deep-research`  
> Produces 100-200KB+ multi-pass research reports with gap-aware expansion passes.

## Purpose

Conduct exhaustive technical deep dives by streaming a long-form inquiry through Perplexity's `sonar-deep-research` model, then iteratively identifying research gaps and expanding the report until it reaches the target volume. This is NOT a one-shot QA tool — it's a multi-pass engine that audits its own output and backfills missing perspectives.

## When To Use

- **Technical investigations**: firmware security audits, PCB thermal analysis, component lifecycle research
- **Competitive benchmarking**: market landscape, feature matrices, pricing comparisons
- **Due diligence**: supply chain risk, regulatory compliance, patent landscape
- **Hardware reviews**: BOM analysis, MTBF estimation, alternative component sourcing
- Any task where a 20KB summary is insufficient and you need 150KB+ of structured analysis

Do NOT use for simple Q&A, quick facts, or anything answerable in under 5KB.

## Architecture

The engine has three core components:

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│  Research Prompt    │ ──▶ │  deep_research.py    │ ──▶ │  Output Report (.md)│
│  (templated .txt)   │     │  (streaming engine)  │     │  100-200KB+         │
└─────────────────────┘     └──────────┬───────────┘     └─────────────────────┘
                                       │
                              ┌────────▼───────────┐
                              │  Gap Analysis Pass  │ ◀── loops until target KB
                              │  (sonar, non-stream)│
                              └────────────────────┘
```

1. **Initial Pass**: Full deep research streamed to file + stdout
2. **Gap Analysis**: Identifies 3-5 missing dimensions (engineering perspective, MTBF data, supply chain risks, etc.)
3. **Expansion Pass**: Targets those gaps explicitly, adding 10-20KB per pass
4. **Repeat** until target KB reached or max passes exhausted

## Quick Start

### 1. Set your API key

```bash
export PERPLEXITY_API_KEY="pplx-..."
```

Or pass it inline: `--api-key pplx-...`

### 2. Create a research prompt

Copy and fill the template:

```bash
cp ~/.hermes/skills/research/perplexity-deep-research/templates/research_prompt.txt my_inquiry.txt
```

Edit `my_inquiry.txt` — replace every `{{VARIABLE}}` with your actual content.
See [Prompt Template Variables](#prompt-template-variables) below.

### 3. Run the inquiry

```bash
python3 ~/.hermes/skills/research/perplexity-deep-research/scripts/deep_research.py \
  --prompt my_inquiry.txt \
  --output my_report.md \
  --target-kb 150
```

Watch the console — output streams live. Gap analysis results print to stderr.

### 4. Review

Open `my_report.md`. Cross-reference tables against citations. If sections feel thin, re-run with a higher `--target-kb`.

## Prompt Template Variables

The template at `templates/research_prompt.txt` uses these placeholders:

| Variable | Description |
|----------|-------------|
| `{{RESEARCH_GOAL}}` | One-line description of the inquiry (e.g., "Deep technical audit of NFC antenna designs") |
| `{{PROJECT_NAME}}` | Project identifier for the report header |
| `{{DESIGN_CONTEXT}}` | High-level overview: what, why, who, current state |
| `{{TECHNICAL_SPECS}}` | Core data points — components, stack, market data. Use `- **Key**: Value` format |
| `{{RESEARCH_DOMAINS}}` | 3-5 domains with specific instructions per domain (see domain structure below) |
| `{{TARGET_KB}}` | Minimum output size in KB (matches `--target-kb` value) |

### Domain structure

Each domain block should follow this format:

```
### Domain N: [Name — e.g., Security Audit]
- [Specific instruction 1]
- [Specific instruction 2]
- [Specific instruction 3]
```

Example:

```
### Domain 1: Firmware Security
- Audit all OTA update mechanisms for MITM vulnerabilities
- Review secure boot chain — verify each stage's attestation
- Analyze flash memory protection against cold-boot extraction

### Domain 2: Thermal Performance
- Model heat dissipation under sustained load (85°C ambient)
- Compare 3 alternative thermal interface materials
- Calculate MTBF degradation curves for each thermal scenario
```

## Script CLI Reference

```
deep_research.py [OPTIONS]

Required:
  --prompt, -p PATH      Path to the filled research prompt file
  --output, -o PATH      Path for the output markdown report

Options:
  --target-kb, -k KB     Minimum output size in KB (default: 100)
  --max-passes, -n N     Maximum expansion passes (default: 30)
  --api-key KEY          Perplexity API key (overrides env var)
  --temperature FLOAT    Generation temperature (default: 0.15)
```

Expansion passes stop when EITHER the target KB is reached OR max passes is exhausted.

## How Hermes Uses This Skill

When you trigger `perplexity-deep-research`, Hermes should:

1. **Load the skill** and confirm the inquiry scope with you
2. **Populate the prompt template** — ask you to fill in any missing fields, or auto-populate from context
3. **Write the filled prompt** to a temp file (e.g., `/tmp/hermes_inquiry_XXXX.txt`)
4. **Run the script** with appropriate `--target-kb` (default 100, raise to 200+ for mission-critical research)
5. **Monitor streaming output** — the script already streams to stdout
6. **Deliver the report** — notify when done, provide the output path
7. **Offer follow-up** — ask if any sections need deeper expansion

### Hermes integration pattern

```bash
# Hermes executes:
python3 ~/.hermes/skills/research/perplexity-deep-research/scripts/deep_research.py \
  --prompt /tmp/hermes_inquiry_XXXX.txt \
  --output ~/research_reports/$(date +%Y%m%d_%H%M%S)_report.md \
  --target-kb 150
```

Output goes to both stdout (for Hermes to monitor) and the report file.

## Key Strictures

These are non-negotiable rules embedded in the system prompt:

1. **Never summarize** — always aim for maximum verbosity and depth
2. **Recursive auditing** — if a section is "done," approach it from a new angle (edge cases, failure modes, historical analogs, alternative architectures)
3. **Table-first comparisons** — any multi-factor comparison MUST use markdown tables
4. **Citation density** — cite specific sources, datasheets, standards documents wherever possible
5. **Anti-completion bias** — the model is explicitly instructed to find new angles rather than declaring completeness

## Gap Analysis

The iterative gap analysis is what distinguishes this from a simple API call. Between passes, the engine:

1. Takes the last ~8KB of research output
2. Sends it to Perplexity's `sonar` model (fast, non-streaming)
3. Asks: "What are 3-5 critical technical gaps?"
4. Feeds those gaps back as explicit instructions in the next expansion pass

This creates a self-correcting loop — the engine doesn't just "write more," it writes what's missing.

## Limitations

- **Rate limits**: Perplexity API may throttle multi-pass runs. The script handles errors gracefully but long runs may need retry logic.
- **Cost**: Each pass consumes tokens. A 150KB report with 3-4 passes may use significant API credits.
- **Hallucination risk**: Deep research models can fabricate citations. Always cross-reference critical claims.
- **No web browsing**: The model works from training data — it cannot fetch live URLs or current pricing.

## Verification

Test the skill is wired correctly:

```bash
# Check script is executable
test -x ~/.hermes/skills/research/perplexity-deep-research/scripts/deep_research.py && echo "READY"

# Check --help works
python3 ~/.hermes/skills/research/perplexity-deep-research/scripts/deep_research.py --help
```

Expected: the help text prints with all options listed.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — skill definition and usage |
| `templates/research_prompt.txt` | Prompt template with `{{VARIABLES}}` to fill |
| `scripts/deep_research.py` | Main streaming research engine |  

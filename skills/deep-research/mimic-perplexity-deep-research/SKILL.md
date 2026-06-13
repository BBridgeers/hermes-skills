---
name: mimic-perplexity-deep-research
description: Architectural replica of Perplexity Deep Research — planning agent, parallel search swarm, multi-stage retrieval with LLM-as-judge reranking + algorithmic recency, iterative synthesis with gap detection, TTC budget controller, and [#source_id] → numbered citation normalization. Delivers Perplexity-quality deep research reports with full citation provenance.
tags: [research, deep-research, swarm, perplexity]
related_skills: [master-deep-research]
---

> **🔗 SUPERSEDED BY `master-deep-research`** — The master skill inlines every phase of this skill (parallel swarm, content-type routing, TTC budget, iterative synthesis, citation normalization) AND adds CRAAP-lite source tiering, triple-weighted scoring (relevance × recency × tier), per-finding confidence calibration, falsifiable claims, and a size-driven auto-expansion loop (`--min-kb` / `--min-words`). Load `master-deep-research` instead of this skill. This skill is preserved for reference and for the hypothesis-verification shortcut pattern.

# mimic-perplexity-deep-research

Architectural replica of Perplexity Deep Research's execution pattern. This skill reproduces the *how* — planning agent, tool swarm, multi-stage retrieval pipeline, iterative synthesis, TTC budget controller, and citation-span mapping — not the *what* (source credibility tiering; delegate that to the existing `deep-research` skill when both are wanted).

**Trigger:** User asks for "Perplexity-style deep research," "mimic perplexity," "deep dive like Perplexity," or any research query where they explicitly want the full multi-agent pipeline with numbered citations.

**Depth:** There is one mode — **deep**. This is not a quick-search tool. Every run goes through the full pipeline. If the user wants something lighter, point them to `web_search_plus(mode='research')` or the existing `deep-research` skill.

## When NOT To Use This Skill — The Hypothesis-Verification Shortcut

The full pipeline (planning → swarm → reranking → iterative synthesis → citation normalization) is designed for **broad survey research** — open-ended topics requiring multi-section reports with diverse source bases. It is OVERKILL for **targeted hypothesis verification** where the user asks a specific yes/no question with a narrow scope.

**Use the full pipeline when:**
- The query is broad: "How are enterprises deploying on-prem LLMs in 2026?"
- The query demands a multi-section report with structured findings
- The user explicitly requests "Perplexity-style deep research"

**Use the parallel-search shortcut when:**
- The query is a specific hypothesis: "Do drug X and drug Y increase nanomaterial uptake?"
- The answer is a definitive yes/no with mechanistic explanation
- The user needs speed over formal structure
- The source base will be narrow (5-15 key sources, not 50+)

**The shortcut pattern (proven effective — May 2026):**

1. **Parallel search wave:** Launch 3+ `web_search_plus(mode='research')` calls simultaneously, each with a DIFFERENT angle on the same question (different search terms, different phrasings, different source types). This replaces Phase 2's subagent swarm.
2. **Synthesize in-context:** The main agent reads all results, identifies the key sources, and writes the report directly. This replaces Phases 1, 3, 4, and 5 — the main agent IS the planner, reranker, and writer.
3. **Extract only critical sources:** Use `web_extract_plus` on the 2-5 most important sources for deep reading. Don't extract everything.
4. **Write directly:** Use `write_file` to produce the final report with inline citations. Skip the formal citation normalization — numbered citations with URLs in a Sources section are sufficient.
5. **Deliver summary + file:** Give the user the verdict in the response, with the full report at a file path.

**Shortcut deliverables:**
- A definitive answer in the terminal response (executive summary)
- A detailed report file with all sources cited
- No session artifacts (no plan.json, budget.json, evidence_store.txt)

**Cost comparison:** The full pipeline consumes ~30 LLM calls, ~15 searches, and ~5 minutes. The shortcut consumes ~5 LLM calls, ~5 searches, and ~2 minutes. For hypothesis verification, the shortcut produces higher-quality output because the main agent's full reasoning is applied to synthesis rather than being split across swarm workers.

**When in doubt:** If the user's question can be answered with "Yes, because X" or "No, because Y" in a single sentence, use the shortcut. If the answer demands "It depends on A, B, C, D, and E across multiple domains," use the full pipeline.

---

## Architecture Overview

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────┐
│   PHASE 0: CLARIFICATION (optional)  │
│   Main agent evaluates specificity   │
│   Encouraged if scope is grey        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      PHASE 1: RESEARCH PLAN         │
│   Main agent produces:              │
│   • Section outline (4-8 sections)  │
│   • Search queries per section      │
│   • Hypotheses to test              │
│   • TTC budget allocation           │
│   Output: plan.json                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PHASE 2: PARALLEL SEARCH SWARM    │
│   delegate_task → 3 subagents       │
│   Each: search + content-type route │
│   Each: extract + structured output │
│   Merge → evidence_store.json       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PHASE 3: RETRIEVAL & RERANKING    │
│   execute_code pipeline:            │
│   1. Dedup by URL + content hash    │
│   2. Source diversity cap/domain    │
│   3. Algorithmic recency scoring    │
│   4. LLM-as-judge relevance scoring │
│   5. Combined final_score           │
│   6. Per-section top-K selection    │
│   Output: ranked_evidence.json      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PHASE 4: ITERATIVE SYNTHESIS      │
│   Section-by-section drafting       │
│   [#source_id] citation tags        │
│   Gap detection → targeted refetch  │
│   TTC budget gates each pass        │
│   Output: draft_report.md           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PHASE 5: CITATION NORMALIZATION   │
│   execute_code: parse all [#S] tags │
│   Aggregate by source URL           │
│   Number 1..N by first appearance   │
│   Replace [#S] → [N]                │
│   Build numbered source list        │
│   Output: final_report.md           │
└──────────────┬──────────────────────┘
               │
               ▼
          FINAL REPORT
```

---

## Session Setup

Before any phase, create the session directory and budget file:

```bash
SESSION_ID=$(date +%Y-%m-%d)-$(echo "$QUERY" | tr ' ' '-' | tr -cd '[:alnum:]-' | cut -c1-40)
SESSION_DIR="$HOME/.hermes/research_sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"
```

Initialize `budget.json`:

```json
{
  "max_llm_calls": 30,
  "max_searches": 50,
  "max_urls_fetched": 250,
  "max_wall_clock_s": 300,
  "hard_wall_clock_s": 420,
  "llm_calls_used": 0,
  "searches_used": 0,
  "urls_fetched": 0,
  "start_time": "<ISO timestamp>",
  "phase": "init"
}
```

Update this file after every phase. Every tool call that consumes budget must increment the counter. The main agent checks `budget.json` before each LLM call and each search dispatch.

---

## Phase 0: Clarification (Optional, Encouraged)

**Goal:** Replicate Perplexity Advanced Deep Research's clarifying-questions behavior.

**When to trigger:** The main agent evaluates the query. If any of these are true, offer clarification:
- The query is a single vague term or phrase ("tell me about fusion energy")
- The query could be interpreted multiple ways ("deep dive on transformers" — electrical? ML? organizational?)
- The user didn't specify scope, timeframe, or depth expectations
- The query crosses multiple domains without a clear lens

**Mechanism:** Use `clarify()` to present 2-4 concrete questions:

```
Before I run the full pipeline on this, a few clarifications would sharpen the research plan:

1. [Scope question — e.g., "Focus on technical implementation or business/market angle?"]
2. [Timeframe question — e.g., "Current state only, or historical trajectory?"]
3. [Depth question — e.g., "Practitioner-level detail or executive overview?"]
```

**If user skips:** Proceed with reasonable defaults. Note in the report: "Scope was not user-clarified; defaults assumed."

**If user answers:** Append answers to the query for Phase 1. Answers become constraints in the plan.

---

## Phase 1: Research Planning

**Goal:** Produce a structured research plan with search queries, section outline, hypotheses, and initial budget allocation.

**Mechanism:** Single LLM call with the planning prompt.

**Planning prompt:**

```
You are a research planner. Given a research query, produce a JSON research plan.
Generate 4-8 sections. Every section gets 1-3 concrete search queries.

Output format:
{
  "report_title": "Concise title for the final report",
  "sections": [
    {
      "id": "s1",
      "title": "Section Title",
      "sub_questions": ["Specific question this section answers"],
      "search_queries": ["exact search query string 1", "exact search query string 2"],
      "hypotheses": ["Claim to verify or falsify with evidence"],
      "priority": "high"
    }
  ],
  "cross_cutting_questions": ["Questions spanning multiple sections"],
  "estimated_total_searches": <number>,
  "estimated_total_sources": <number>
}

Rules:
- 4-8 sections. Fewer for narrow queries, more for broad.
- At least 1 search query per section. 2-3 for high-priority sections.
- Include at least one "critical/contrarian/criticism" search for the topic.
- Search queries should be diverse: different phrasings, different angles, different source types.
- Cross-cutting questions are answered during the final synthesis pass.
- Priority: "high" for core sections, "medium" for supporting context.
```

Save to `$SESSION_DIR/plan.json`.

Print checkpoint:
```
📋 Plan: {N} sections, {M} search queries across {K} sub-questions
   Budget estimate: ~{estimated_total_sources} sources, ~{estimated_total_searches} searches
```

---

## Phase 2: Parallel Search Swarm

**Goal:** Execute all search queries in parallel batches, extract content with content-type routing, and produce structured evidence blocks.

### Step 2.1: Query Batching

Divide all search queries from `plan.json` into batches of roughly equal size, up to 3 batches per wave (matching the 3-subagent concurrency limit). If more queries exist, run multiple waves.

Batch assignment rules:
- High-priority section queries go in Wave 1
- Each batch gets queries from multiple sections (not all s1 queries in one batch)
- Each batch: 5-8 queries max

### Step 2.2: Subagent Instructions

Every subagent receives this instruction:

```
You are a search-and-extract worker. You have a batch of search queries to process.

FOR EACH QUERY in your batch:

STEP 1: SEARCH
Run web_search_plus(query, mode='research', count=10)
This returns search results with auto-extraction where available.

STEP 2: IDENTIFY TOP RESULTS
Select the top 5-8 results by relevance. Prioritize:
- Official sources (.gov, .edu, official org domains)
- Technical publications (arxiv.org, documentation sites)
- Reputable news/analysis (avoid content farms and thin aggregators)
- Diversity: don't pick 5 results from the same domain

STEP 3: CONTENT-TYPE ROUTE AND EXTRACT
For each selected result, route by content type:

A) HTML / Standard web pages → web_extract(urls=[url])
   Primary method. Works for most pages.

B) PDF (url ends in .pdf OR content-type is PDF) → web_extract(urls=[url])
   Try web_extract first. If it returns error or truncated content,
   try web_extract_plus(urls=[url], provider='firecrawl').

C) GitHub repository (github.com/{user}/{repo}) → terminal command:
   git clone --depth 1 {url} /tmp/repo_clone_{source_id}
   Then read_file on README.md and any key documentation files.
   Then terminal: rm -rf /tmp/repo_clone_{source_id}

D) Paywalled content (URL contains /paywall, /subscribe, /sign-in,
   or returns "subscribe to continue") → browser_navigate(url)
   then browser_snapshot(full=true). If browser access also blocked,
   flag as "PAYWALLED: not accessible" and use the search snippet instead.

E) Unknown / failed extraction → use the search result snippet as fallback.
   Flag as "FALLBACK: used search snippet only"

STEP 4: EXTRACT DATE
For every successfully extracted page, attempt to find the publication date:
- Check for meta tags, article:published_time, or schema.org date in the extracted content
- Check for date patterns in the first 500 characters (YYYY-MM-DD, "Published Month DD, YYYY", etc.)
- Check URL patterns (e.g., /2026/05/21/slug)
- If no date found, use the search result's date if available
- If still no date, mark as "unknown"

STEP 5: PRODUCE EVIDENCE BLOCK
For each extracted page, output:

--- EVIDENCE BLOCK ---
SOURCE_ID: <your worker base offset + incremental counter>
URL: <full url>
TITLE: <page title>
DOMAIN: <domain only, e.g. nature.com>
DATE: <YYYY-MM-DD or "unknown">
CONTENT_TYPE: <html|pdf|github|paywalled|fallback>
SECTION_ID: <which plan section this is for, e.g. s2>
QUERY_USED: <the search query that found this>
RECENCY_DAYS: <days since publication, or -1 if unknown>
SNIPPET: <most relevant paragraph — trim to 500 words max>
KEY_CLAIM: <one specific claim from this source>
KEY_CLAIM: <another claim if present>
DATA: <statistic or number> | <context around that data point>
DATA: <another data point if present> | <context>
FULL_SUMMARY: <2-4 sentence summary of the entire page's contribution>
--- END ---

CRITICAL RULES:
- Every source gets exactly one evidence block
- SNIPPET must be the most relevant paragraph for the assigned section, not just the first paragraph
- KEY_CLAIM lines: extract verifiable claims, not vague statements
- DATA lines: extract specific numbers/statistics with surrounding context
- RECENCY_DAYS: compute accurately from DATE. If DATE is "unknown", set to -1.
- SOURCE_ID must be unique. Use your worker base offset + sequential counter.

YOUR WORKER BASE OFFSET: <offset>
Start your SOURCE_ID at <offset> and increment by 1 for each source.

Return ALL evidence blocks concatenated. No narrative, no commentary — just the blocks.
```

### Step 2.3: Worker ID Offsets

| Wave | Worker 1 | Worker 2 | Worker 3 |
|---|---|---|---|
| Wave 1 | 1000 | 2000 | 3000 |
| Wave 2 | 4000 | 5000 | 6000 |
| Wave 3 | 7000 | 8000 | 9000 |

Formula: `offset = (wave - 1) * 3000 + (worker_index * 1000)`

Pass the offset to each subagent. The offset is embedded in the instruction at `YOUR WORKER BASE OFFSET: <offset>`.

### Step 2.4: Subagent Toolset

Each subagent gets `['web', 'browser', 'terminal', 'file']` — full access needed for content-type routing (browser for paywalls, terminal for GitHub clones, file for temp storage).

### Step 2.5: Merge

After all subagents in a wave complete, concatenate all evidence blocks into `$SESSION_DIR/evidence_store.txt`.

If multiple waves are needed, append each wave's output to the same file.

Print checkpoint:
```
🔍 Wave {N}: {X} queries → {Y} sources extracted ({Z} unique domains)
   Content types: HTML:{a} PDF:{b} GitHub:{c} Paywalled:{d} Fallback:{e}
```

### Step 2.6: Search Budget Check

After each wave, update `budget.json`:
- `searches_used += number of search queries dispatched this wave`
- `urls_fetched += number of sources extracted this wave`

If `searches_used >= max_searches` or `urls_fetched >= max_urls_fetched`, do not dispatch additional waves. Flag remaining unprocessed queries.

---

## Phase 3: Retrieval & Reranking

**Goal:** Take the raw evidence store and produce a ranked, deduplicated, diversity-enforced, recency-weighted, LLM-judged set of evidence per section.

**Mechanism:** `execute_code` Python script that processes `evidence_store.txt`, then an LLM-as-judge scoring pass.

### Step 3.1: Parse Evidence Store

```python
import re, json, hashlib
from datetime import datetime, timedelta

# Parse evidence_store.txt into structured records
# Pattern: --- EVIDENCE BLOCK --- ... --- END ---
blocks = re.split(r'--- EVIDENCE BLOCK ---', evidence_text)
records = []
for block in blocks:
    if not block.strip():
        continue
    rec = {}
    for line in block.strip().split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            key = key.strip().lower()
            val = val.strip()
            if key in ('key_claim', 'data'):
                rec.setdefault(key + 's', []).append(val)
            else:
                rec[key] = val
    records.append(rec)
```

### Step 3.2: Deduplication

```python
# Pass 1: Exact URL match
seen_urls = set()
unique = []
for r in records:
    url = r.get('url', '')
    if url not in seen_urls:
        seen_urls.add(url)
        unique.append(r)

# Pass 2: Near-duplicate content detection
# Compute 3-gram Jaccard on SNIPPET field
# If Jaccard > 0.7 between two records, keep the one with more DATA entries
def jaccard_3gram(a, b):
    def ngrams(s, n=3):
        s = re.sub(r'\s+', ' ', s.lower())
        return set(s[i:i+n] for i in range(len(s)-n+1))
    sa, sb = ngrams(a), ngrams(b)
    if not sa or not sb:
        return 0
    return len(sa & sb) / len(sa | sb)

deduped = []
for i, r in enumerate(unique):
    is_dup = False
    for j, existing in enumerate(deduped):
        snippet_a = r.get('snippet', '')
        snippet_b = existing.get('snippet', '')
        if jaccard_3gram(snippet_a, snippet_b) > 0.7:
            # Keep the one with more data
            if len(r.get('datas', [])) > len(existing.get('datas', [])):
                deduped[j] = r
            is_dup = True
            break
    if not is_dup:
        deduped.append(r)
```

### Step 3.3: Source Diversity Enforcement

```python
# Max 5 sources per domain across the entire evidence set
# Max 3 sources per domain within any single section
from collections import defaultdict

domain_counts = defaultdict(int)
diversified = []
for r in deduped:
    domain = r.get('domain', '')
    if domain_counts[domain] < 5:
        domain_counts[domain] += 1
        r['domain_rank'] = domain_counts[domain]
        diversified.append(r)
```

### Step 3.4: Algorithmic Recency Scoring

```python
# Compute recency_multiplier based on RECENCY_DAYS
def recency_multiplier(recency_days):
    if recency_days < 0:
        return 0.75    # unknown date — penalize but don't destroy
    if recency_days <= 90:
        return 1.0
    elif recency_days <= 180:
        return 0.95
    elif recency_days <= 365:
        return 0.85
    elif recency_days <= 730:
        return 0.7
    else:
        return 0.5     # >2 years old — significant penalty

for r in diversified:
    days = int(r.get('recency_days', -1))
    r['recency_multiplier'] = recency_multiplier(days)
```

Save intermediate results to `$SESSION_DIR/pre_ranked.json`.

### Step 3.5: LLM-as-Judge Relevance Scoring

Now the LLM scores each evidence block for relevance to its assigned section's sub-questions.

Group evidence blocks by `SECTION_ID`. For each section, pass the section's sub-questions (from `plan.json`) and up to 50 evidence blocks (the ones with highest recency_multiplier first) to the LLM:

```
You are scoring evidence relevance. You will receive:
- A section's sub-questions
- Evidence blocks, each with SOURCE_ID, TITLE, DOMAIN, DATE, SNIPPET, KEY_CLAIMs, DATA points, and RECENCY_DAYS

For each evidence block, score its relevance to the sub-questions on a 1-5 scale:
5 = Directly answers a sub-question with specific, verifiable data. Essential for this section.
4 = Strongly relevant, provides substantial evidence or authoritative context.
3 = Moderately relevant, adds useful context or partial evidence.
2 = Tangentially related, minor contribution.
1 = Irrelevant or too thin to cite.

Factor recency into your score naturally — a 2026 source on current trends should score higher than a 2019 source making the same claim, unless the 2019 source is foundational/authoritative.

Return ONLY a JSON array:
[{"source_id": 1003, "score": 5}, {"source_id": 2007, "score": 3}, ...]
```

The LLM returns relevance scores. These are combined with the algorithmic recency:

```python
for r in diversified:
    llm_score = llm_scores.get(r['source_id'], 2)  # default 2 if not scored
    r['relevance_score'] = llm_score
    r['final_score'] = llm_score * r['recency_multiplier']
```

### Step 3.6: Per-Section Top-K Selection

```python
per_section = defaultdict(list)
for r in diversified:
    per_section[r.get('section_id', 'unassigned')].append(r)

# For each section: sort by final_score descending, take top 15
# Then enforce within-section domain diversity: max 3 per domain
ranked = {}
for section_id, records in per_section.items():
    records.sort(key=lambda r: r['final_score'], reverse=True)
    domain_counts = defaultdict(int)
    selected = []
    for r in records:
        domain = r.get('domain', '')
        if domain_counts[domain] < 3:
            domain_counts[domain] += 1
            selected.append(r)
        if len(selected) >= 15:
            break
    ranked[section_id] = selected
```

Save to `$SESSION_DIR/ranked_evidence.json`.

Print checkpoint:
```
📊 Reranking: {total_before} sources → {after_dedup} after dedup → {after_diversity} diversity-capped
   → {final_count} ranked across {section_count} sections
   Recency distribution: ≤90d:{a} 90-180d:{b} 180-365d:{c} 1-2y:{d} >2y:{e} unknown:{f}
   Score range: {min_score}-{max_score} (median: {median_score})
```

---

## Phase 4: Iterative Synthesis

**Goal:** Write the report section by section with `[#source_id]` citation tags, detect evidence gaps, retarget searches within budget, and produce the draft report.

**Mechanism:** Main agent iterates over sections, calling the writer LLM once per section (with possible retries for gap-filling).

### System Prompt for Writer

```
You are a research report writer. You write ONE section at a time.

Given:
- Section title and sub-questions
- Ranked evidence blocks (each with SOURCE_ID, SNIPPET, KEY_CLAIMs, DATA, FULL_SUMMARY, final_score)

Rules:
1. Write in clear, authoritative prose suitable for an analyst-grade report.
2. EVERY factual claim, statistic, or specific statement MUST be immediately followed by a citation tag: [#SOURCE_ID]
   Example: "Market revenue reached $4.2B in Q1 2026[#1003], driven by enterprise adoption[#2007]."
3. If you use data from a source, cite it inline — do not bunch citations at the end of paragraphs.
4. Prioritize high final_score sources. Use low-score sources only for supplementary context.
5. If multiple sources corroborate a claim, cite all of them: "The trend is accelerating[#1003][#2007][#3002]."
6. If sources contradict each other, surface the contradiction explicitly:
   "Source A reports X[#1003], while Source B finds Y[#2007]. The discrepancy may stem from..."
7. If you lack sufficient evidence for a sub-question, output the section as best you can, then append:
   GAP: <description of what evidence is missing>
8. DO NOT fabricate claims. If evidence is thin, write what you can and flag the gap.
9. DO NOT cite sources you didn't actually use.

Output format:
## {section_title}

{body text with [#SOURCE_ID] citations}

GAPS: {list of gaps, or "none"}
```

### Per-Section Flow

For each section in priority order (high → medium):

1. **Load evidence:** Read the section's ranked evidence from `ranked_evidence.json`
2. **Check budget:** If `llm_calls_used >= max_llm_calls - 3`, switch to rapid mode (combine remaining sections into one pass)
3. **Call writer LLM:** Pass section context + evidence
4. **Process output:**
   - If GAPS is empty or "none": append to `draft_report.md`, proceed to next section
   - If GAPS detected: enter gap-fill loop
     ```
     LOOP (no artificial cap — budget is the only exit):
       a. Check budget: searches_used < max_searches? wall_clock < hard_wall_clock_s - 60?
          If either exhausted → exit loop, append section as-is, flag remaining gaps
       b. Run 1 targeted web_search_plus for the most critical gap
       c. Extract top 3 results, append to section evidence
       d. Call writer LLM again with augmented evidence
       e. If new GAPS is empty or "none" → exit loop, section complete
       f. If same gaps persist AND this is a low-priority section → exit loop (don't burn budget)
       g. If same gaps persist AND high-priority section → continue loop
     ```
   - Flag any unresolved gaps in the report with: "Finding not fully verified within research budget."
5. **Update budget:** Increment `llm_calls_used`, `searches_used`, `urls_fetched`
6. **Print checkpoint:** `✍️ Section {N}/{total}: "{title}" — {word_count} words, {citation_count} citations`

### Gap Detection Budget Rules

- **No artificial retry cap.** The TTC budget is the ONLY governor. If budget remains, retry as many times as needed for high-priority gaps. If budget is exhausted, stop — regardless of retry count.
- Gap-fill searches are narrow: `site:domain` or specific fact-lookup queries, not broad re-searches.
- If gap persists when budget runs out, the report notes: "This finding could not be fully verified within the research budget."
- Low-priority section gaps are always capped at 1 retry (not worth burning budget on). High-priority section gaps get unlimited retries within remaining budget.

### Rapid Mode Trigger

If `llm_calls_used >= max_llm_calls - 3` OR `wall_clock > 200s`:
- Combine all remaining unwritten sections into a single LLM call
- Produce condensed versions (1-2 paragraphs each)
- No gap-filling for rapid-mode sections
- Flag in report: "Sections {X-Y} were produced in rapid mode due to budget constraints."

### Cross-Cutting Questions

After all sections are drafted, if LLM budget remains (≥2 calls), answer the cross-cutting questions from `plan.json` in a "Cross-Cutting Insights" section. Otherwise skip.

### Draft Report Structure

```markdown
# {report_title}
*Deep Research — {date} — {source_count} sources cited*

## Executive Summary
[Written last, after all sections. 5-8 sentences synthesizing the most important findings.]

## {Section 1 Title}
[Body with [#SOURCE_ID] citations]
...

## {Section N Title}
...

## Cross-Cutting Insights
[If budget allowed]

## Gaps & Limitations
[All unresolved gaps from individual sections, consolidated]

## Source List
[Raw list of SOURCE_ID → URL — will be normalized in Phase 5]
```

Save to `$SESSION_DIR/draft_report.md`.

---

## Phase 5: Citation Normalization

**Goal:** Convert raw `[#SOURCE_ID]` tags into numbered citations with a proper source list.

**Mechanism:** `execute_code` Python script.

### Algorithm

```python
import re, json

# 1. Read draft_report.md
with open(f'{session_dir}/draft_report.md') as f:
    draft = f.read()

# 2. Find all unique [#NNNN] tags
tags = re.findall(r'\[#(\d+)\]', draft)
seen = []
unique_tags = []
for t in tags:
    if t not in seen:
        seen.append(t)
        unique_tags.append(t)

# 3. Load evidence store for URL mapping
with open(f'{session_dir}/evidence_store.json') as f:
    evidence = json.load(f)

# Build source_id → {url, title, domain} mapping
source_map = {}
for e in evidence:
    sid = str(e.get('source_id', ''))
    if sid:
        source_map[sid] = {
            'url': e.get('url', ''),
            'title': e.get('title', 'Untitled'),
            'domain': e.get('domain', '')
        }

# 4. Assign citation numbers 1..N in order of first appearance
citation_map = {}
for i, sid in enumerate(unique_tags, 1):
    citation_map[sid] = i

# 5. Replace [#NNNN] → [N] throughout the report
def replace_tag(match):
    sid = match.group(1)
    if sid in citation_map:
        return f'[{citation_map[sid]}]'
    return match.group(0)  # leave unrecognized tags as-is

report = re.sub(r'\[#(\d+)\]', replace_tag, draft)

# 6. Build numbered source list
source_list_lines = ['\n## Sources\n']
for sid in unique_tags:
    if sid in citation_map and sid in source_map:
        num = citation_map[sid]
        info = source_map[sid]
        source_list_lines.append(
            f'{num}. [{info["title"]}]({info["url"]}) — {info["domain"]}'
        )

# 7. Append source list to report
report += '\n'.join(source_list_lines)

# 8. Write final report
with open(f'{session_dir}/final_report.md', 'w') as f:
    f.write(report)

# 9. Also save citation metadata for hover/preview
citation_metadata = {}
for sid in unique_tags:
    if sid in citation_map and sid in source_map:
        num = citation_map[sid]
        citation_metadata[str(num)] = {
            'url': source_map[sid]['url'],
            'title': source_map[sid]['title'],
            'domain': source_map[sid]['domain']
        }
with open(f'{session_dir}/citations.json', 'w') as f:
    json.dump(citation_metadata, f, indent=2)
```

Save to `$SESSION_DIR/final_report.md` and `$SESSION_DIR/citations.json`.

Print checkpoint:
```
📝 Citations normalized: {N} unique sources → numbered [1]-[{N}]
   Report: {word_count} words, {section_count} sections
```

---

## Phase 6: Delivery

### Primary Output

The final report is at `$SESSION_DIR/final_report.md`. Read it and deliver the content directly in the response (the user wants to see the report, not just a file path).

If the report exceeds reasonable terminal display (~5000 words), deliver:
1. Executive Summary in full
2. Section headers with key finding one-liners
3. Full path to the file

### File Delivery

Copy the final report to the articles directory:
```bash
cp "$SESSION_DIR/final_report.md" "$HOME/.hermes/articles/perplexity-dr-${SESSION_ID}.md"
```

Also copy citations.json for reference:
```bash
cp "$SESSION_DIR/citations.json" "$HOME/.hermes/articles/perplexity-dr-${SESSION_ID}-citations.json"
```

### Session Artifacts

All artifacts are preserved at `$SESSION_DIR/`:
- `plan.json` — research plan
- `budget.json` — final budget state
- `evidence_store.txt` — raw evidence blocks
- `ranked_evidence.json` — post-reranking evidence
- `draft_report.md` — pre-normalization draft
- `final_report.md` — finalized report
- `citations.json` — citation metadata
- `session.log` — phase-by-phase log with timing

### Slack Notification

If Slack is available, send a summary via `send_message`:

```
🧠 *Perplexity-style Deep Research — {date}*

*{report_title}*

Sources: {raw_count} → {deduped_count} after dedup → {final_count} cited
Sections: {section_count} | Words: {word_count}
Time: {elapsed} | LLM calls: {llm_used}/{llm_max} | Searches: {searches_used}/{searches_max}

Top findings:
• {finding_1_title}: {one_sentence}
• {finding_2_title}: {one_sentence}
• {finding_3_title}: {one_sentence}

📄 Full report: ~/.hermes/articles/perplexity-dr-{session_id}.md
🔗 Session data: ~/.hermes/research_sessions/{session_id}/
```

---

## TTC Budget System — Full Specification

### Budget File Format

`$SESSION_DIR/budget.json`:

```json
{
  "max_llm_calls": 30,
  "max_searches": 50,
  "max_urls_fetched": 250,
  "max_wall_clock_s": 300,
  "hard_wall_clock_s": 420,
  "llm_calls_used": 0,
  "searches_used": 0,
  "urls_fetched": 0,
  "start_time": "2026-05-21T14:30:00Z",
  "phase": "planning",
  "waves_completed": 0,
  "sections_completed": 0,
  "gaps_remaining": 0,
  "mode": "normal"
}
```

### Update Protocol

After each phase, update the budget file using `write_file`. The main agent reads it before every significant decision:
- Before dispatching a subagent wave → check `searches_used` and `urls_fetched`
- Before each section write → check `llm_calls_used` and wall clock
- Before gap-fill searches → check all limits

### Wall Clock Check

```python
elapsed = (datetime.now() - datetime.fromisoformat(budget['start_time'])).total_seconds()
if elapsed > budget['hard_wall_clock_s']:
    # Stop immediately, normalize whatever we have
    mode = 'hard_stop'
elif elapsed > budget['max_wall_clock_s']:
    # Switch to rapid mode
    mode = 'rapid'
```

### Budget Exhaustion Behavior

| Resource Exhausted | Action |
|---|---|
| `llm_calls_used >= max_llm_calls - 3` | Rapid mode: combine remaining sections |
| `searches_used >= max_searches` | No more searches. Use existing evidence only. |
| `urls_fetched >= max_urls_fetched` | No more extraction. Use snippets from search results. |
| Wall clock > `max_wall_clock_s` | Rapid mode, skip low-priority sections |
| Wall clock > `hard_wall_clock_s` | Hard stop. Normalize immediately. |

---

## Content-Type Router — Detailed Specification

The content-type router lives in the subagent instructions (Phase 2). Here is the exact decision logic each subagent follows for every URL:

```
For URL: {url}

1. CHECK URL PATTERN:
   - Ends in .pdf → route to PDF handler
   - Matches github.com/{user}/{repo} (not /issues, /pull, /blob) → route to GitHub handler
   - Contains /paywall, /subscribe, /sign-in, /premium, /member → route to Paywall handler
   - Otherwise → route to HTML handler

2. HTML HANDLER:
   a. web_extract(urls=[url])
   b. If returns error or empty content → web_extract_plus(urls=[url], provider='firecrawl')
   c. If STILL fails → route to Fallback handler

3. PDF HANDLER:
   a. web_extract(urls=[url])
   b. If returns error or content < 500 chars → web_extract_plus(urls=[url], provider='firecrawl')
   c. If PDF too large (>2M chars rejected) → note "PDF too large, extracted prefix only"
   d. If STILL fails → route to Fallback handler

4. GITHUB HANDLER:
   a. Extract repo name from URL
   b. terminal: git clone --depth 1 {url} /tmp/repo_{source_id}
   c. read_file: /tmp/repo_{source_id}/README.md
   d. search_files: pattern='*.md' in /tmp/repo_{source_id}/ for key docs
   e. Use README content + any relevant .md files as the extracted content
   f. terminal: rm -rf /tmp/repo_{source_id}

5. PAYWALL HANDLER:
   a. browser_navigate(url)
   b. browser_snapshot(full=true)
   c. If snapshot contains article text → use it
   d. If snapshot shows paywall/gate → flag as "PAYWALLED: content behind paywall"
   e. Fall back to search result snippet for evidence

6. FALLBACK HANDLER:
   a. Use the description/snippet from the search result
   b. Flag as "FALLBACK: used search snippet only — full content unavailable"
   c. Still produce an evidence block with what's available
```

---

## Recency Signal — Detailed Specification

### Date Extraction (Phase 2, in subagent)

The subagent attempts to find the publication date in this order:

1. **Metadata in extracted content:** Look for `Published:`, `date:`, `article:published_time`, `<time datetime="...">`, schema.org `datePublished`
2. **Date patterns in first 500 chars:** `YYYY-MM-DD`, `Month DD, YYYY`, `MM/DD/YYYY`
3. **URL pattern:** `/YYYY/MM/DD/`, `?year=YYYY&month=MM`
4. **Search result metadata:** The search API sometimes returns dates
5. **If nothing found:** DATE = "unknown", RECENCY_DAYS = -1

### Recency Multiplier Table (Phase 3)

| RECENCY_DAYS | Multiplier | Rationale |
|---|---|---|
| -1 (unknown) | 0.75 | Penalize but don't destroy — content may still be valuable |
| 0–90 | 1.00 | Current. Full weight. |
| 91–180 | 0.95 | Very recent. Near-full weight. |
| 181–365 | 0.85 | Last year. Slight discount. |
| 366–730 | 0.70 | 1–2 years old. Moderate discount. |
| 731+ | 0.50 | >2 years old. Significant discount unless LLM overrides via high relevance score. |

### Combined Scoring (Phase 3.5)

```
final_score = llm_relevance_score * recency_multiplier
```

**Why this works:** The LLM judges semantic relevance on a 1-5 scale. A foundational 2019 paper might get a 5 from the LLM, then ×0.5 recency = 2.5 final. A mediocre 2026 blog post might get a 3 × 1.0 = 3.0. The recency penalty is real but the LLM can still elevate exceptional older sources.

**Example:**

| Source | LLM Relevance | Recency Days | Recency × | Final Score |
|---|---|---|---|---|
| 2026 industry report | 4 | 15 | 1.00 | 4.00 |
| 2025 academic paper | 5 | 300 | 0.85 | 4.25 |
| Foundational 2019 paper | 5 | 2500 | 0.50 | 2.50 |
| 2024 blog post | 3 | 500 | 0.70 | 2.10 |
| Unknown date, high quality | 4 | -1 | 0.75 | 3.00 |

The 2025 paper edges out the 2026 report because the LLM scored it higher (better evidence quality). The 2019 foundational paper is penalized but still potentially makes top-K if evidence is thin. This is the right behavior.

---

## Tool Mapping

| Perplexity Component | Hermes Equivalent | Notes |
|---|---|---|
| Search API | `web_search_plus(mode='research', count=10)` | Multi-provider with auto-extraction |
| Browser/Document Reader | `web_extract` + `web_extract_plus` + `browser_navigate` | Content-type routed |
| Code Sandbox | `execute_code` | Python for data analysis, Phase 3/5 processing |
| Planner LLM | Main agent with planning prompt | Separate system prompt for planning role |
| Search Workers | `delegate_task` subagents (up to 3 concurrent) | Parallel waves if needed |
| Cross-encoder Reranker | LLM-as-judge scoring in Phase 3.5 | Relevance 1-5 per evidence block |
| Report Writer | Main agent with writer prompt | Section-at-a-time iterative drafting |
| TTC Controller | `budget.json` file + main agent checks | Budget gates at every phase transition |
| Citation System | `execute_code` post-processing | Parse [#S] → numbered list |
| Progress UI | Checkpoint prints between phases | No streaming during subagent execution |

---

## Integration with Existing `deep-research` Skill

These two skills compose cleanly. The `mimic-perplexity-deep-research` skill handles execution architecture. The existing `deep-research` skill handles source quality tiering.

**Composition mode (user requests both):**

1. Run `mimic-perplexity-deep-research` through Phase 4 (produce `draft_report.md` with citation tags)
2. Load the existing `deep-research` skill via `skill_view(name='deep-research')`
3. Run its source classification (Phase 4 from that skill — CRAAP-lite) on all cited sources
4. Inject tier labels into the draft: replace `[#1003]` with `[#1003|T1]` for T1 sources, etc.
5. Apply its confidence calibration to each finding (High/Medium/Low)
6. Add its "Falsifiable Claims" and "Source Diversity Audit" sections
7. Proceed with Phase 5 citation normalization (the normalizer handles the `|T1` suffix)

**Non-composition mode (default):** Run `mimic-perplexity-deep-research` standalone. No formal source-tiering, but the LLM-as-judge scoring naturally favors authoritative sources.

---

## Failure Modes & Recovery

| Failure | Detection | Recovery |
|---|---|---|
| Subagent timeout (>3 min) | `delegate_task` returns timeout | Use partial results from completed workers. Flag sections with missing workers as "limited coverage." |
| Subagent produces unparseable output | Merge step fails regex matching | Retry the failed subagent ONCE with stricter formatting instructions. If still broken, extract what's parseable with best-effort regex. |
| Extract failures across many URLs | High fallback count in checkpoint | Flag in report: "N sources were only accessible via search snippet due to extraction failures." Continue with what's available. |
| Evidence too thin (<3 sources per section) | Phase 3 top-K selection produces small sets | Before Phase 4, run 2-3 supplementary searches targeting the thinnest section. If still thin, flag in report and narrow that section's scope. |
| LLM hallucinates citation IDs | Phase 5 normalization finds IDs not in evidence store | Strip unrecognized citation tags. Log warning. The claim loses its citation but the report stays honest. |
| Context window pressure | Phase 4 writer calls fail or truncate | Trim evidence: send only top-8 sources per section instead of top-15. If still failing, switch to rapid mode. |
| Budget blown before all sections written | `llm_calls_used >= max_llm_calls - 3` | Rapid mode: combine remaining sections into one call. Produce condensed versions. Flag in report. |
| Wall clock hard stop | `elapsed > hard_wall_clock_s` | Stop immediately. Run Phase 5 on whatever draft exists. Flag sections that weren't written. |
| Subagent ID collision | Two evidence blocks with same SOURCE_ID | Phase 3 dedup step catches same-ID blocks. Keep the one with more DATA entries. The offset scheme makes collisions unlikely but this is the safety net. |
| GitHub clone failure | `git clone` times out or repo is private | Flag as "GitHub: repository inaccessible." Use the repo's description from search results. Move on. |
| Paywall browser failure | `browser_navigate` blocked or CAPTCHA | Flag as "PAYWALLED: browser access blocked." Use search snippet. Move on. |
| Budget file corruption | JSON parse fails | Re-initialize with conservative estimates based on what's been completed. Log the corruption event. |

---

## Example Run

### Input
```
User: "Run a Perplexity-style deep research on: How are enterprises actually deploying on-premise LLMs in 2026, and what's the TCO vs cloud API?"
```

### Phase 0: Clarification
```
Agent: Before I run the full pipeline, a few clarifications:

1. Focus on large enterprises (F500) or include mid-market/SMB?
2. Geography: global or US-specific?
3. Any specific model families (LLaMA, DeepSeek, Mistral) or all open-weight models?

User: "F500 US only, all open-weight models"
```

### Phase 1: Plan
```
📋 Plan: 6 sections, 14 search queries across 12 sub-questions
   Budget estimate: ~120 sources, ~14 searches
```

### Phase 2: Swarm Wave 1
```
🔍 Wave 1: 10 queries → 47 sources extracted (31 unique domains)
   Content types: HTML:38 PDF:4 GitHub:3 Paywalled:0 Fallback:2
```

### Phase 2: Swarm Wave 2
```
🔍 Wave 2: 4 queries → 18 sources extracted (14 unique domains)
   Content types: HTML:15 PDF:2 GitHub:0 Paywalled:1 Fallback:0
```

### Phase 3: Reranking
```
📊 Reranking: 65 sources → 58 after dedup → 47 diversity-capped
   → 41 ranked across 6 sections
   Recency distribution: ≤90d:22 90-180d:10 180-365d:6 1-2y:1 >2y:0 unknown:2
   Score range: 1.10-4.85 (median: 3.40)
```

### Phase 4: Synthesis
```
✍️ Section 1/6: "Current State of Enterprise On-Prem LLM Deployments" — 312 words, 8 citations
✍️ Section 2/6: "Hardware & Infrastructure Requirements" — 287 words, 11 citations
✍️ Section 3/6: "TCO Analysis: On-Prem vs Cloud API" — 425 words, 14 citations
   [GAP: missing recent pricing data for Dell/HP enterprise GPU servers → targeted search → resolved]
✍️ Section 4/6: "Model Selection & Fine-Tuning Patterns" — 298 words, 9 citations
✍️ Section 5/6: "Security, Compliance & Governance Drivers" — 264 words, 7 citations
✍️ Section 6/6: "2026 Outlook & Emerging Patterns" — 203 words, 6 citations
```

### Phase 5: Normalization
```
📝 Citations normalized: 41 unique sources → numbered [1]-[41]
   Report: 1,789 words, 6 sections
```

### Delivery
```
Full report delivered in terminal + saved to:
~/.hermes/articles/perplexity-dr-2026-05-21-enterprise-onprem-llm-tco.md
Session data: ~/.hermes/research_sessions/2026-05-21-enterprise-onprem-llm-tco/
```

---

## Constraints

- **No hallucination:** Every factual claim carries a `[#SOURCE_ID]` tag. Phase 5 strips any tag not found in the evidence store.
- **Budget is law:** The TTC budget gates every major decision. Never exceed hard limits. Log all budget decisions.
- **Single mode only:** This skill always runs deep. There is no quick/shallow variant. For lighter research, use the existing `deep-research` skill or `web_search_plus`.
- **Subagent resilience:** Partial subagent failures do not kill the run. Use what's available, flag what's missing.
- **Content-type coverage:** Every URL gets routed. No extraction method is tried more than twice per URL.
- **Citation provenance:** Every citation number maps to exactly one URL. The `citations.json` sidecar enables hover-preview in compatible UIs.
- **Session preservation:** All intermediate artifacts are saved. A run can be inspected, debugged, or resumed from any phase.
- **Recency transparency:** The recency distribution is printed in the Phase 3 checkpoint. The reader can see if the source base skews old.
- **Rapid mode is never silent:** If the pipeline switches to rapid mode, the report explicitly flags which sections were condensed.

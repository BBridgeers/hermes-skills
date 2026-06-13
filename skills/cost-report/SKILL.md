---
name: cost-report
description: Weekly OpenRouter API cost report — computes dollar costs from model token usage, flags anomalies, forecasts burn, and prescribes concrete optimizations
tags: [meta, finops]
version: "1.0.0"
---

# Cost Report — Hermes OpenRouter Spend Analytics

Generate a cost report from Hermes token usage data. **The output must prescribe action, not just describe spend** — every section either names an anomaly, forecasts risk, or recommends a concrete move.

## Model Pricing (OpenRouter — per million tokens)

All pricing below reflects OpenRouter listed rates, verified 2026-06-01 via `/api/v1/models`. Cache read/write pricing applies only when OpenRouter reports it in the API response (prompt caching).

| Model | Input $/1M | Output $/1M | Cache Read $/1M | Cache Write $/1M |
|-------|-----------|-------------|-----------------|-------------------|
| anthropic/claude-opus-4-7 | $15.00 | $75.00 | $1.50 | $18.75 |
| anthropic/claude-sonnet-4-6 | $3.00 | $15.00 | $0.30 | $3.75 |
| anthropic/claude-haiku-4-5-20251001 | $0.80 | $4.00 | $0.08 | $1.00 |
| google/gemini-3-pro | $1.25 | $10.00 | — | — |
| google/gemini-3-flash | $0.15 | $0.60 | — | — |
| openai/gpt-5.2 | $2.50 | $10.00 | $1.25 | $12.50 |
| deepseek/deepseek-v4-pro | $0.435 | $0.870 | $0.003625 | — |
| deepseek/deepseek-chat-v4 | $1.10 | $4.40 | — | — |
| deepseek/deepseek-chat (v3) | $0.27 | $1.10 | — | — |
| deepseek/deepseek-r1 | $2.19 | $8.76 | — | — |
| moonshotai/kimi-k2.6 | $0.684 | $3.420 | $0.144 | — |
| moonshotai/kimi-k2.5 | $1.00 | $4.00 | — | — |
| qwen/qwen3.7-max | $1.25 | $3.75 | $0.25 | $1.5625 |
| qwen/qwen3-coder-next | $0.11 | $0.80 | $0.07 | — |
| qwen/qwen3-coder | $0.22 | $1.80 | — | — |
| z-ai/glm-5.1 | $0.98 | $3.08 | $0.182 | — |
| z-ai/glm-5 (free) | $0.00 | $0.00 | — | — |
| inclusionai/ring-2.6-1t | $0.30 | $2.50 | $0.06 | — |
| meta-llama/llama-4-maverick | $0.20 | $0.60 | — | — |

### Model Downgrade Hierarchy (for optimization suggestions)

When suggesting model downgrades, follow this chain:
```
claude-opus-4-7 → claude-sonnet-4-6 → claude-haiku-4-5 → deepseek-v4-pro → qwen3-coder-next → gemini-3-flash
qwen3.7-max → deepseek-v4-pro → qwen3-coder-next → gemini-3-flash
glm-5.1 → deepseek-v4-pro → qwen3-coder-next → gemini-3-flash
gpt-5.2 → deepseek-v4-pro → qwen3-coder-next → gemini-3-flash
gemini-3-pro → gemini-3-flash
deepseek-r1 → deepseek-v4-pro → deepseek-chat-v4 → deepseek-chat (v3)
kimi-k2.6 → qwen3-coder-next → gemini-3-flash
```

### Model Name Normalization (session DB → OpenRouter canonical)

When reading from `state.db`, session `model` values may differ from OpenRouter's canonical model ID. Normalize before pricing lookup:
```
"qwen3.7-max" → "qwen/qwen3.7-max"
"qwen3.7-max/OpenRouter" → "qwen/qwen3.7-max"
"deepseek-v4-pro" → "deepseek/deepseek-v4-pro"
"glm-5.1" → "z-ai/glm-5.1"
"kimi-k2.6" → "moonshotai/kimi-k2.6"
"qwen3-coder-next" → "qwen/qwen3-coder-next"
"qwen3-coder" → "qwen/qwen3-coder"
"inclusionai/ring-2.6-1t" → "inclusionai/ring-2.6-1t"
"glm-5-free" → "z-ai/glm-5" (free tier, $0 pricing)
```

If a CSV row references a model not in the pricing table, treat it as an **unknown model**: price it at claude-opus-4-7 rates (conservative), add it to the "Pricing drift" callout in the report so rates can be updated, and continue. Do not crash.

## Steps

### 0. Build token-usage.csv from Hermes sessions

Hermes does not auto-generate a token-usage.csv. Build it first:

```bash
python3 ~/.hermes/skills/cost-report/scripts/extract_usage.py --days 7 --output ~/.hermes/data/token-usage.csv
```

The extraction script reads `~/.hermes/sessions/*.jsonl` and `~/.hermes/sessions/session_*.json`, extracting:
- `date` — session date (from session_start or first message timestamp)
- `skill` — inferred from the first user message intent or session metadata (use "uncategorized" if ambiguous)
- `model` — from session metadata `model` field
- `input_tokens` — aggregated from provider usage records in the session
- `output_tokens` — aggregated from provider usage records in the session
- `cache_read` — from usage.prompt_tokens_details.cached_tokens if available
- `cache_creation` — from usage.prompt_tokens_details.cache_creation_input_tokens if available

If usage data is not directly available in sessions, estimate tokens from message content lengths:
- Input tokens ≈ total user + system message characters ÷ 4
- Output tokens ≈ total assistant message characters ÷ 4

Tag estimated rows with `source=estimated` in a notes column.

### 1. Determine the report window

- Default: 7 days. To change, edit the `--days` argument in step 0 or pass `DAYS=N` when invoking.
- Compute `CUTOFF_DATE = today − N days`. All rows where `date >= CUTOFF_DATE` are in-window.
- If the CSV has ≥ `2 × N` days of history, also compute `PRIOR_CUTOFF = today − 2N days` for week-over-week.

### 2. Read token usage data

- File: `~/.hermes/data/token-usage.csv` (create via step 0)
- Columns: `date,skill,model,input_tokens,output_tokens,cache_read,cache_creation`
- If the file is missing: log `COST_REPORT_SKIP: no token-usage.csv yet` and stop (no notification).
- If 0 rows in-window: log `COST_REPORT_SKIP: no runs in last N days` and stop.
- Parse numeric columns defensively — skip malformed rows, count them as `csv_malformed` for the source-status footer.

### 3. Compute per-row cost

For each valid in-window row, look up the model's rates and calculate:
```
input_cost       = input_tokens    / 1e6 × rate_input
output_cost      = output_tokens   / 1e6 × rate_output
cache_read_cost  = cache_read      / 1e6 × rate_cache_read
cache_write_cost = cache_creation  / 1e6 × rate_cache_write
row_cost         = input_cost + output_cost + cache_read_cost + cache_write_cost
```
If a model doesn't support cache pricing, treat cache_read_cost and cache_write_cost as $0.

### 4. Core aggregates (ground truth — keep these)

a. **Total cost** for the window (and break out input/output/cache_read/cache_write dollar shares).
b. **Per-skill** — top 10 by cost. Columns: Skill | Runs | Total Tokens | Cost | Avg Cost/Run.
c. **Per-model** — total runs, total tokens, total cost per model.
d. **Week-over-week** — only if ≥ `2N` days of history. `delta_pct = (this_window − prior_window) / prior_window`.

### 5. Decision sections (this is the point of the skill)

#### 5a. Verdict line (one sentence, top of report)

Compose one sentence that captures the week. Pattern:
> "Spent **$X.XX** across **N runs** ({{↑/↓ Y% WoW | no prior-week baseline}}); **M anomalies flagged**, projected monthly burn **~$Z.ZZ**."

#### 5b. Anomaly detection (per-skill, per-model cost spikes)

For each (skill, model) pair with ≥ 3 runs in-window:
- Compute mean µ and std-dev σ of `row_cost`.
- Flag any run where `row_cost > µ + 2σ` AND `row_cost > $0.10` (ignore sub-cent noise).
- Flag skills whose **total** cost this window is ≥ 2× the same skill's prior-window total (only if prior window exists and prior total ≥ $0.25).

Output a table: `Skill | Model | When | Run Cost | vs µ | Why (tokens_input / tokens_output / cache_write)`. If no anomalies, write "No anomalies." — do not omit the section.

#### 5c. Monthly burn forecast

- `daily_avg_cost = total_cost / N`
- `projected_monthly = daily_avg_cost × 30`
- Show: "At current rate, 30-day spend ≈ **$X.XX**."
- If projected_monthly > $50, add a "⚠ burn-rate watch" note.
- If projected_monthly > $200, add "🚨 high burn — review optimization recommendations immediately."

#### 5d. Optimization opportunities (top 3, actionable)

Scan the in-window data and produce up to 3 concrete recommendations. Each must name (i) a specific skill, (ii) a specific change, (iii) estimated weekly savings. Candidate patterns:

- **Model downgrade**: skill runs on an expensive model (e.g., claude-opus-4-7), its median `output_tokens / input_tokens` ratio across runs is < 0.3, AND its avg run cost > $0.25. → Suggest the next model down the hierarchy; savings = `this_skill_cost × (1 − downgrade_rate_mix / current_rate_mix)`.
- **Cache underuse**: skill's `cache_read / (cache_read + input_tokens)` ratio < 0.2 across runs AND avg run cost > $0.10 AND model supports caching. → "Add a stable prompt prefix so the provider can cache it — would move ~X% of input tokens to cache_read at 10× savings."
- **Config mismatch**: `~/.hermes/config.yaml` sets a `model:` override for a skill or task but the CSV shows runs on a different model. → "Model override drift — config says X, runs show Y."
- **Long-tail waste**: a skill with >10 runs in-window where avg cost/run < $0.01 AND it produces no written artifact (no `~/.hermes/articles/` file, no notification). → "Possible no-op loop."
- **Reasoning overuse**: model is deepseek-r1 or another reasoning model but the task output shows simple, non-analytical responses. → "Switch to deepseek-chat-v4 — reasoning model adds cost without benefit."

If fewer than 3 candidates pass the filters, say so — do not pad. If zero candidates, write "No optimization levers found this week."

#### 5e. Pricing drift callout

If any CSV row referenced a model not in the active pricing table, list those model names and the total tokens attributed to them. Note: "Add rates to skills/cost-report/SKILL.md." If all rows matched, omit this block.

### 6. Write the full report

Path: `~/.hermes/articles/cost-report-DATE.md` (replace DATE with ISO date, e.g., `cost-report-2026-05-03.md`). If the file already exists, overwrite it (idempotent).

```markdown
# Hermes Cost Report — DATE
*Period: last N days · provider: OpenRouter*

> {{verdict line from 5a}}

## Anomalies
{{table from 5b, or "No anomalies."}}

## Burn forecast
- Daily avg: $X.XX
- 30-day projection: $X.XX {{⚠ burn-rate watch if >$50}}{{🚨 high burn if >$200}}

## Optimization opportunities
1. **{{skill}}** — {{action}}. Est. savings: ~$X.XX/week.
2. ...
3. ...
{{or "No optimization levers found this week."}}

## Cost by Skill (Top 10)
| Skill | Runs | Tokens | Cost | Avg/Run |
|-------|------|--------|------|---------|

## Cost by Model
| Model | Runs | Tokens | Cost |
|-------|------|--------|------|

## Composition
- Input: $X.XX · Output: $X.XX · Cache read: $X.XX · Cache write: $X.XX

## Week-over-week
- This window: $X.XX · Prior window: $X.XX · Δ {{+/−}}X% {{or "no prior-week baseline"}}

## Pricing drift
{{list of unknown models, or omit if none}}

---
*Sources: token-usage.csv ({{ok|degraded: M malformed rows skipped}}) · Pricing table last reviewed in SKILL.md.*
*Generated by Hermes cost-report skill.*
```

### 7. Send notification via `send_message` to Slack

Lead with the verdict, then the top 3 actions. Keep under ~15 lines.

```
*Cost Report — DATE (last N days)*

{{verdict line from 5a}}

Top 3 by cost:
1. skill-a — $X.XX (N runs)
2. skill-b — $X.XX
3. skill-c — $X.XX

{{If any optimization opportunities:}}
Actions this week:
• {{skill}} → {{action}} (~$X.XX/wk)
• ...

{{If any anomalies:}} ⚠ M anomalies flagged — see report.
{{If pricing drift:}} ⚠ unknown models in CSV — see report.

30-day projection: $X.XX
Full: ~/.hermes/articles/cost-report-DATE.md
```

### 8. Log to `~/.hermes/logs/cost-report/YYYY-MM-DD.md`

```
## Cost Report
- Period: last N days (provider: OpenRouter)
- Total: $X.XX across N runs
- Verdict: {{copy verdict line}}
- Anomalies flagged: M
- Monthly projection: $X.XX
- Optimization suggestions: {{count}} ({{brief list}})
- Week-over-week: +/-X% (or "no baseline")
- Pricing drift: {{none | list of unknown models}}
- Source status: csv={{ok|degraded}}
- Article: ~/.hermes/articles/cost-report-DATE.md
- Notification sent via send_message to Slack
```

## Constraints

- **Anomaly threshold** is intentionally conservative (µ + 2σ AND >$0.10) — cheap runs should not be flagged as noise.
- **Optimization recommendations must name a skill and an estimated dollar impact.** "Use Sonnet more" without a target skill is not useful — skip the slot instead.
- **Do not send a notification** if the CSV is missing or the window is empty — silently log and exit.
- **Do not change the pricing tables** without verifying rates against OpenRouter's current published pricing.
- **Preserve idempotency**: rerunning on the same day overwrites the article, does not append.

## Cron Setup

This skill is designed to run weekly. Set up via Hermes cron:

```bash
hermes cron create "0 9 * * MON" --prompt "Load skill cost-report, build token-usage.csv, generate weekly OpenRouter spend report" --delivery slack
```

Or run manually:
```bash
hermes chat -q "Load skill cost-report and generate the weekly cost report"
```

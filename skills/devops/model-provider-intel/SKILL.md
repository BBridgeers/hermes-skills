---
name: model-provider-intel
version: 3
description: Scan provider availability, pricing, and benchmarks for new LLM models. Also covers API key audit patterns, credit drain diagnostics, and free model catalog maintenance.
last-updated: 2026-06-06
triggered-by: User asks "is X model available on Y provider" or "compare pricing for X model across providers"
---

# Skill: Model Provider Intelligence
Version: 1
Triggered-by: New model availability scan, provider pricing comparison, "who has model X" questions
Notes: Created 2026-05-30 — Qwen 3.7 Max provider scan across 10+ endpoints

## Pattern
A new LLM model is released (or the user is considering switching models). They want to know: which providers carry it, what's the pricing, and how does it compare to alternatives.

## Protocol

### Phase 1: Scan Major Providers
Run availability checks in parallel where possible:

**OpenRouter** — most comprehensive, check first:
```bash
curl -s "https://openrouter.ai/api/v1/models" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" | \
  python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin).get('data',[]) if '<model_keyword>' in m.get('id','').lower()]"
```

**Ollama Cloud** — open-weight models:
```bash
curl -s https://ollama.com/v1/models | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('data',[])),'models')"
```

**DeepSeek API** — DeepSeek-native only:
```bash
curl -s https://api.deepseek.com/models -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

**Groq** — Llama/GPT-OSS family only (NO Qwen, NO DeepSeek):
```bash
curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"
```

**OpenCode Zen** — curated agent-coding models:
```bash
# Check zen docs at https://opencode.ai/docs/zen/
```

**OpenCode Go** — subscription open models ($10/mo):
```bash
# Check go docs at https://opencode.ai/docs/go/
# Note: Go has Qwen 3.5/3.6 Plus but NOT Max variants
```

**Alibaba Cloud (DashScope)** — direct/native:
```bash
# Check https://www.alibabacloud.com/help/en/model-studio/model-pricing
# International (Singapore): dashscope-intl.aliyuncs.com
# China Mainland (Beijing): dashscope.aliyuncs.com (~34% cheaper)
```

**Together AI**, **Novita AI** — niche providers, check web docs.

### Phase 2: Pricing Comparison
Assemble pricing table. Key fields per provider: input/1M, output/1M, cache read/1M, context window, free trial.

**Pricing tiers matter** — Alibaba Cloud has two regions:
- International (Singapore): higher price, global routing
- China Mainland (Beijing): ~34% cheaper, compute restricted to China

**OpenRouter pricing** — the API response `pricing` field is authoritative (not the web page). Web page may show list price; API shows actual cost.

### Phase 3: Benchmark Comparison (if requested)
When comparing two models, use the model's own published benchmark tables when available (same harness, same judge). Third-party leaderboards may use different harnesses and aren't directly comparable.

Key benchmark categories:
- **Coding Agent**: SWE-Bench Verified/Pro, Terminal-Bench 2.0, SciCode
- **General Agent**: MCP-Mark, MCP-Atlas, SkillsBench, BFCL
- **Reasoning**: GPQA Diamond, HLE, HMMT, LiveCodeBench
- **Long Context**: MRCR-v2, Kernel Bench L3

### Phase 4: Hermes Integration
Hermes Config (add new model/providers):

For a new model on an existing provider, add the model ID to that provider's model list, then run `model-catalog-sync` and restart the gateway.

For a NEW provider (e.g., Anthropic native), you need a full provider block in config.yaml (see Tier 5 above). Then add a quick command and run the catalog sync.

For Hermes profiles:
```bash
# Set model across profiles
hermes config set model.default <model_id>
hermes config set model.provider <provider>

# For specific profiles
hermes -p <profile> config set model.default <model_id>
hermes -p <profile> config set model.provider <provider>

# Batch all profiles
for p in /root/.hermes/profiles/*/config.yaml; do
  name=$(basename $(dirname $p))
  hermes -p $name config set model.default <model_id>
  hermes -p $name config set model.provider <provider>
done

# Update delegation model
hermes config set delegation.model <model_id>
hermes config set delegation.provider <provider>

# Sync models.json for workspace visibility
python3 -c "
import json
# Add new model, remove deprecated provider entries
...
with open('/root/.hermes/models.json', 'w') as f:
    json.dump(merged, f, indent=2)
"

# Restart services
systemctl --user restart hermes-gateway
systemctl --user restart hermes-workspace
```

### Tier 5 — Anthropic Native (Free early-access, then paid credits ~$0.01-0.03/1M tokens)

Anthropic provides native API access to Claude models. The `claude-fable-5` model was available for early-access testing before its paid launch on June 27-29 2026.

**Setup (Hermes native provider, NOT OpenRouter):**
```yaml
# Add to ~/.hermes/config.yaml providers section
anthropic:
  api_key_env: ANTHROPIC_API_KEY
  base_url: https://api.anthropic.com
  models:
  - claude-fable-5
```

Set `ANTHROPIC_API_KEY` in `~/.hermes/.env` with the `sk-ant-...` key. Access via:
- `ermie-fable` quick command: `/provider anthropic; /model claude-fable-5`
- `/ermie-fable` (CLI alias)
- `ermie-fable-or` for OpenRouter route: `/provider openrouter; /model anthropic/claude-fable-5`
- Via model picker in Workspace / Slack / Telegram

Note: The native Anthropic API has a different chat completions format than OpenAI. Hermes handles the translation internally via the provider adapter.

## Provider Capability Matrix (known as of 2026-06-05)

### Tier 0 — OpenRouter's OWN Free Models (NO :free suffix)

These are OpenRouter's in-house models — free by default, not tagged `:free`. They are INVISIBLE to `:free` searches on openrouter.ai/models. Must be checked separately.

| Model ID | Context | Params | Notes |
|----------|---------|--------|-------|
| openrouter/owl-alpha | 1M | — | Agentic workloads, tool use, code gen. $0/M input+output |
| openrouter/elephant-alpha | 262K | 100B | Code completion, debugging. Token-efficient. $0/M (was Ling-2.6-flash) |
| openrouter/free | varies | — | "Free Models Router" — auto-routes to random :free models |

Stealth/discontinued (may still work as endpoints):
| openrouter/hunter-alpha | 1M | 1T | Early test of MiMo-V2-Pro |
| openrouter/healer-alpha | 262K | — | Omni-modal (vision, audio, reasoning, action) |
| openrouter/body-builder | ? | — | Beta, may 404 |

### Tier 1 — Third-Party :free Models (OpenRouter)

Complete :free model catalog (23 text + 2 image + 1 embedding — June 2026):

TEXT (23):
  nvidia/nemotron-3-ultra:free
  nvidia/nemotron-3.5-content-safety:free
  nvidia/nemotron-3-super-120b-a12b:free      1M ctx, 120B MoE
  nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free  256K, reasoning
  nvidia/nemotron-3-nano-30b-a3b:free          256K
  nvidia/nemotron-nano-12b-v2-vl:free          128K, vision\n  nex-agi/nex-n2-pro:free                      262K, vision\n  nvidia/nemotron-nano-9b-v2:free              128K\n  poolside/laguna-m.1:free                     262K, coding agent
  poolside/laguna-xs.2:free
  moonshotai/kimi-k2.6:free                    262K
  google/gemma-4-26b-a4b-it:free
  google/gemma-4-31b-it:free
  liquid/lfm-2.5-1.2b-thinking:free
  liquid/lfm-2.5-1.2b-instruct:free
  qwen/qwen3-next-80b-a3b-instruct:free
  qwen/qwen3-coder-480b-a35b:free              1M ctx, coding
  openai/gpt-oss-120b:free                     131K ctx
  openai/gpt-oss-20b:free
  z-ai/glm-4.5-air:free
  venice/uncensored:free
  meta-llama/llama-3.3-70b-instruct:free
  meta-llama/llama-3.2-3b-instruct:free
  nousresearch/hermes-3-llama-3.1-405b:free

IMAGE (2):
  sourceful/riverflow-v2.5-pro:free
  sourceful/riverflow-v2.5-fast:free

Vision capability verification: NOT all free models with text+image input actually handle vision well in practice. Always test with a minimal image before pinning. openrouter/owl-alpha is text-only despite intelligent appearance — do NOT assign it to vision tasks. The `:free` suffix on OpenRouter models means the model itself is free, but some free models may still require a funded OpenRouter account (credits > $0) to access.

EMBEDDING (1):
  nvidia/llama-nemotron-embed-vl-1b-v2:free

Rate limits: 20 req/min, 200 req/day per model on OpenRouter free tier.

### Tier 2 — Dirt Cheap (Not Free, Negligible Cost)

| Model | Provider | Input/1M | Output/1M | Context | Notes |
|-------|----------|----------|-----------|---------|-------|
| DeepSeek V4 Pro | DeepSeek native | ~$0.50 | ~$1.10 | 1M | **RECOMMENDED PRIMARY** — 50-100x cheaper than OR |
| DeepSeek V4 Flash | DeepSeek native | cheaper | cheaper | 1M | Lightweight primary or fallback |
| DeepSeek V3.1 | DeepSeek native | ~$0.14 | ~$0.28 | 1M | Budget option |

### Tier 3 — OpenCode Zen Free Models (4 total)

Zen is pay-per-token for most models, but has 4 free ones:

| Model ID | Context | Notes |
|----------|---------|-------|
| opencode/deepseek-v4-flash-free | 1M | Limited time, data may be used to improve model |
| opencode/mimo-v2.5-free | — | Limited time, data may be used to improve model |
| opencode/nemotron-3-super-free | 205K | NVIDIA trial terms, prompts+outputs logged |
| opencode/big-pickle | — | Stealth model, free for limited time |

OpenCode Go is $10/mo subscription — NOT free. Includes 9 models: glm-5.1, glm-5, kimi-k2.6, kimi-k2.5, minimax-m2.7, minimax-m2.5, qwen3.6-plus, qwen3.5-plus, nemotron-3-super.

### Tier 4 — Ollama Cloud Free (Weekly Rate Limit, 19+ models)

Complete Ollama Cloud free catalog (ollama.com/search?c=cloud):

  minimax-m3              1M ctx, coding & agentic frontier
  deepseek-v4-pro          1M ctx, 3 reasoning modes
  deepseek-v4-flash        1M ctx, MoE 284B/13B active
  deepseek-v3.2            reasoning + agent performance
  glm-5.1                  agentic engineering, SWE-Bench leader
  glm-5                    744B MoE (40B active)
  glm-4.7                  coding focus
  qwen3.5                  multimodal, multiple sizes
  qwen3-coder-next         coding agent specialist
  qwen3-next               parameter efficient
  gemma4                   frontier, 4 size variants
  gemini-3-flash-preview   speed focused
  minimax-m2.7             coding & professional productivity
  minimax-m2.5             productivity & coding
  minimax-m2.1             multilingual code engineering
  kimi-k2.6                multimodal agentic, long-horizon coding
  nemotron-3-super         120B MoE (12B active)
  nemotron-3-nano          4B, efficient agentic
  devstral-small-2         24B, codebase exploration + tool use
  rnj-1                    8B, code & STEM, open-weight

### Recommended Model Stack (June 2026)

```
PRIMARY:     deepseek → deepseek-v4-pro        ($0.50/M input, 1M ctx)
FALLBACK 1:  deepseek → deepseek-v4-flash      (cheaper, same provider, 1M ctx)
EMERGENCY:   openrouter → nvidia/nemotron-3-super-120b-a12b:free  (FREE, 120B)
CRON JOBS:   deepseek → deepseek-v4-flash      (cheapest paid, background work)
```

### Why This Stack

- NO OpenRouter dependency for primary — eliminates credit drain risk
- NO Google/Gemini — user has explicitly rejected Gemini as unreliable, misleading, and incapable. Do NOT recommend, suggest, or configure Gemini as primary or fallback for this user.
- DeepSeek native API is ~50-100x cheaper than OpenRouter for same-tier models
- OpenRouter only as last-resort emergency fallback (free models)
- Projected monthly cost: $3-10 for DeepSeek primary, near-zero for flash fallback

## Pitfalls

- **USER HATES GEMINI.** Do NOT recommend, suggest, configure, or fall back to any Google Gemini model. The user considers them misleading, unreliable, and incapable. This applies to Gemini 2.5 Flash, Gemini 2.5 Pro, Gemini 3.x, and all variants. Google provider may still be used for non-Gemini models (Gemma) if the user approves.
- **qwen3.7-max via OpenRouter is a CREDIT SINK.** At 60K-87K prompt tokens per tool-calling turn (typical Hermes session), the model costs ~$0.04-$0.11 per API call. A single active 65-minute session burned $2.88 across 107 calls. At that rate, $10 vanishes in ~3 hours. Use DeepSeek V4 Pro direct instead (50-100x cheaper for same-tier intelligence). **Never configure qwen3.7-max as primary or fallback on OpenRouter.**
- **OpenRouter has stealth free models WITHOUT `:free` suffix.** Searching openrouter.ai/models for `:free` will NOT return openrouter/owl-alpha, openrouter/elephant-alpha, or the free router. These are OpenRouter's own in-house models — free by default, $0/M input+output. Must search for provider=openrouter separately. Elephant Alpha = rebranded Ling-2.6-flash. Hunter Alpha = early MiMo-V2-Pro (may be discontinued). Healer Alpha = omni-modal stealth. Body Builder = beta. Always check openrouter-owned models separately from the :free catalog when doing a comprehensive free model audit.
- **OpenRouter web page price ≠ API price**. The web page may show a higher "list price." The API `pricing` field in the model object is what you actually pay.
- **Two-provider simultaneous drain is a real failure mode.** OpenRouter (402 out of credits) + Ollama Cloud (429 weekly limit) = complete fallback chain collapse. Keep at least 3 providers funded or on free tiers.
- **Closed-weight models can't run on Ollama**. Qwen 3.7 Max, Claude, GPT are all API-only.
- **Go ≠ Zen on OpenCode**. Go is subscription ($10/mo, open models only). Zen is pay-per-token (all curated models). Go has fewer models. Both require active payment — NOT free.
- **Hermes config set only changes active profile**. Use `hermes -p <name>` for other profiles.
- **models.json doesn't auto-sync**. After model changes, manually rebuild models.json or workspace dropdowns won't show new models.
- **UFW not on Hostinger**. The VPS firewall is panel.hostinger.com, not UFW.
- **When user asks for raw lists/model catalogs, give them EXACTLY that.** Do not add analysis, tier rankings, stack recommendations, or commentary unless explicitly asked. The user will tell you what they want — deliver that and stop. Adding unsolicited advice after being told exactly what to produce triggers intense frustration. Present the data, shut up, wait for the next instruction.
- **CSV parsing breaks on commas inside CapabilityClass fields during model assignment ingestion.** When importing model assignment tables from external audits (e.g., Perplexity Deep Research), fields like "Sourcing, Ranking & Search" or "Narrative, Coaching & Communication" contain commas that break standard CSV parsers. The comma splits the field mid-value, shifting all subsequent columns — the CapabilityClass bleeds into PrimaryModel, producing nonsense assignments (agents get "Ranking & Search" as their model ID). Detection: scan for model IDs that look like prose text rather than real model identifiers. Fix: manually reassign the affected agents, or pre-process the CSV to quote fields containing commas before parsing.
- **Per-agent model assignment must NEVER bucket.** Assigning one model to 10+ agents under a loose label ("General", "Reasoning") is a hard failure. The user rejects bucketed assignments on sight. Every agent must get a model explicitly chosen for its specific function, with a written justification. Capability classes (Deep Reasoning, Heavy Coding, Verification, Research, Narrative, Sourcing, Lightweight) help organize THINKING but must not dictate assignments — two agents in the same class may still get different models. When the user calls out bucketing, restart from scratch with per-agent justifications. No model should serve more than ~4 agents without clear justification for why those 4 have genuinely identical needs.
- **OpenRouter's model browse UI uses virtual scrolling.** Not all models load in the DOM at once. To extract the full list, scroll down repeatedly (3-5 times) and run `document.body.innerText.split('\n').filter(l => l.includes('(free)'))` in the browser console after each scroll. Deduplicate across snapshots. For OpenRouter-owned models (no `:free` suffix), search `?q=openrouter` separately.
- **Config.yaml model insertion is best done via Python script.** Read the YAML, extend the list, sort, write back. This avoids manual line-by-line patching of a 1000-line config file. Use the pattern: `or_models.extend(to_add); or_models.sort()` then `yaml.dump(config, f, sort_keys=False)` to preserve structure.

24. **Swarm dispatch hits OpenRouter :free rate limits immediately**: When multiple swarm agents use OpenRouter :free models simultaneously, the 200 req/day per-model limit is exhausted in minutes. Symptom: agents block with "Error code: 400". Fix: replace :free models with Ollama Cloud equivalents (deepseek-v4-pro, qwen3.5, glm-5.1 — weekly limits only) for dispatch-heavy agents. The AV1 Perplexity audit distributes load: 25 agents on Ollama Cloud, 35 on OpenRouter.

25. **Ollama Cloud model 404 — "No endpoints available matching"**: Not all Ollama Cloud models in the catalog are actually API-accessible. Test before assigning: `curl -s https://ollama.com/v1/chat/completions -d '{"model":"<id>","messages":[{"role":"user","content":"test"}]}'`. If 404, fall back to deepseek-v4-pro (most reliable Ollama Cloud model). This occurred with qwen3-coder-next during swarm dispatch.
- **Ollama Cloud uses different model IDs and provider than OpenRouter.** Ollama Cloud models use short IDs (`deepseek-v4-pro`, `qwen3.5`, `glm-5.1`, `qwen3-coder-next`, `deepseek-v3.2`, `deepseek-v4-flash`) with provider `ollama`. OpenRouter models use full IDs with `:free` suffix. When updating profile `config.yaml`, the `model.provider` must match — an Ollama Cloud model ID with provider `openrouter` will fail silently. Use a mapping function: check if the model ID is in the Ollama Cloud list; if not, default to `openrouter`. The Perplexity-audited 60-agent workforce assignment table uses both providers; 25 agents run on Ollama Cloud, 35 on OpenRouter.
- **External audit CSVs may contain commas in CapabilityClass fields.** The category "Sourcing, Ranking & Search" contains a comma that breaks standard CSV parsing, causing the CapabilityClass to leak into the PrimaryModel column. Detection: any agent whose model field contains a phrase like "Ranking & Search" instead of a real model ID. Affected agents in the 60-agent workforce: telemetry-curator, opportunity-mapper, vehicle-sourcing, housing-sourcing, role-match. Fix: manually reassign affected agents, or pre-process CSV to quote comma-containing fields. This is independent of the model-assignment-optimizer skill.

## Task-REDACTED Model Selection Workflow

When the user asks "which free model should I use for X," do NOT just dump the catalog. Match model strengths to task constraints along these axes:

### Axes to Evaluate (in order)

1. **Architecture fit**: Dense models apply every parameter to every token — better for deep reading comprehension where you can't afford diluted attention. MoE models are faster/cheaper per token but attention is split across experts. For bulk reading, profiling, and comprehension-heavy tasks: **dense > MoE** at equivalent param counts.

2. **Context window vs task volume**: 128K context ≈ 80-100 pages. If the task exceeds that, either chunk or switch to a long-context specialist (Kimi). Bigger context = fewer chunk boundaries = better profile continuity.

3. **Format adherence**: Some models drift output structure under sustained load. For tasks requiring structured output (JSON outlines, consistent formatting), prefer models with strong instruction-following track records (Llama 3.3, not early Kimi/Nemotron releases).

4. **Free-tier throughput**: Larger models on free tiers get throttled harder. 70B is the sweet spot where you get reasonable tokens/sec without 550B-tier rate limiting.

5. **Reading comprehension quality**: Not all models read equally well. Benchmark signals: MMLU, reading comprehension subsets, summarization accuracy. Dense 70B models consistently outperform MoE models at equivalent sizes for pure reading tasks.

### Recommended Picks by Task Class

| Task Class | Primary Pick | Runner-Up | Why |
|---|---|---|---|
| Bulk reading + profile building | `meta-llama/llama-3.3-70b-instruct:free` | `moonshotai/kimi-k2.6:free` | 70B dense, proven reading comp, 128K ctx, strong format adherence |
| Extreme long doc (200+ pages) | `moonshotai/kimi-k2.6:free` | `nvidia/nemotron-3-super-120b-a12b:free` | Kimi built for extreme context; Nemotron as fallback with 1M ctx |
| Fast parallel batch processing | Spread across Llama 3.3 + Nemotron-super | — | Two free models = double throughput without rate-limit stacking |

### Anti-Patterns

- **Don't recommend 550B MoE for reading tasks** — massive model but free-tier rate limiting makes it unusable for sustained work, and MoE attention dilution hurts reading depth.
- **Don't recommend sub-30B models for comprehension** — fine for classification/simple tasks, lose too much nuance for profiling.
- **Don't recommend a model without checking if it's actually in the user's config.yaml** — always grep config first, not the OpenRouter catalog.

## References
- `references/qwen3.7-max-full-scan.md` — Full Qwen 3.7 Max provider scan results (2026-05-30)
- `references/qwen3.7-vs-deepseek-v4-pro-benchmarks.md` — Head-to-head benchmark comparison
- `references/free-model-landscape-2026-06.md` — Complete free model catalog across all providers
- `references/free-model-strength-ranking.md` — Benchmark-ranked functional groups (coding, reasoning, general, multimodal, speed, specialized) with S/A/B/C tiers. Use when the user asks "which free model is best for X"
- `references/provider-key-audit.md` — Lightweight API key health check pattern
- `references/models-json-sync.md` — Syncing config.yaml models to workspace dropdown with free tagging
- `references/groq-key-pool-pattern.md` — Multi-key API pool pattern for resilience against silent key expiration
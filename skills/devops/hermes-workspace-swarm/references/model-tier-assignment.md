# Model Tier Assignment — Bench-Backed Framework

> How to pick the right model for each swarm agent using objective benchmarks and cost data.

## The Tier System

| Tier | Purpose | Bench Threshold | Cost Range /Mtok | Models |
|------|---------|----------------|------------------|--------|
| **S: Deep Reasoning** | Orchestrator, architecture, synthesis | SWE-bench 75%+ , Terminal-Bench 55%+ | $0.28–$5/$1.10–$30 | `deepseek-v4-pro` (DS direct, 1M ctx), `gpt-5.5`, `claude-opus-4-7` |
| **A: Coding Specialist** | Code review, refactoring, debugging | SWE-bench 70%+ | $0.50–$3/$3–$15 | `claude-sonnet-4-6`, `gpt-5.3-codex`, `glm-5`, `kimi-k2.6`, `qwen3.6-plus` |
| **B: Speed/Throughput** | Curl, grep, validation, structured parsing | — (overqualified) | $0.06–$0.30/$0.24–$1.20 | `deepseek-v4-flash`, `minimax-m2.7`, `qwen3.5-plus` |
| **V: Vision/Multimodal** | Screenshots, PDFs, images | — (capability-gated) | $0.50–$2/$3–$12 | `gemini-3.1-pro`, `gemini-2.5-pro` |

**Free tier disruptors:** `qwen3-coder-next` (OpenRouter free) scores 70%+ SWE-bench — A-tier capability at B-tier cost (zero). Always evaluate free models first for A/B-tier tasks before assigning paid models.

## Assignment Rules (Mandatory)

1. **Orchestrator always S-Tier** — must hold all agent outputs in context, cross-reference, synthesize
2. **Context requirement gates model choice** — an orchestrator coordinating 4+ agents needs 1M context. Models with 200K or 262K context CANNOT orchestrate a 5-agent swarm.
3. **Vision tasks get V-Tier** — but browser `snapshot` returns TEXT accessibility trees, not images. Vision models are only needed for screenshot/image analysis, not DOM testing.
4. **Free first** — check if a free model meets the tier requirements before assigning paid. `qwen3-coder-next` (free, 70%+ SWE-bench) should be the default for all B-tier and many A-tier tasks.
5. **Never over-assign** — don't put S-Tier on curl loops. Don't put V-Tier on text-based DOM testing.
6. **Cost-aware gating** — `gpt-5.5` at $30/Mtok output vs `claude-sonnet-4-6` at $15/Mtok for the same SWE-bench tier. Use the cheaper option when capability is equivalent.

## Benchmarks Reference (May 2026)

| Model | SWE-bench Verified | Terminal-Bench 2.0 | Cost /Mtok (in/out) | Context |
|-------|-------------------|-------------------|---------------------|---------|
| `claude-sonnet-4-6` | 80.9% | 57.9% | $3/$15 | 200K |
| `glm-5` | 77.8% | 56.2% | $1.40/$4.40 | 200K |
| `kimi-k2.6` | ~76.8% (K2.5) | 50.8% (K2.5) | $0.95/$4.00 | Unknown |
| `qwen3-coder-next` | 70%+ | — | **FREE** (OR free tier) | 262K |
| `qwen3.6-plus` | — | — | $0.50/$3.00 | Unknown |
| `deepseek-v4-pro` | — | — | $0.28/$1.10 (DS direct) | **1M** |
| `deepseek-v4-flash` | — | — | $0.06/$0.24 | 1M |

## Anti-Pattern: Gemini for Methodical Work

**Do NOT assign Gemini models** (`gemini-3.1-pro`, `gemini-2.5-pro`, `gemini-2.5-flash`) to agents doing:
- DOM state reporting (button states, field values, console errors)
- Structured QA checklists
- HTTP status code validation  
- Systematic procedure following

User has experienced Gemini hallucinating button states, inventing console errors, and confabulating field values. For methodical testing, use `claude-sonnet-4-6`. Reserve Gemini only for loose visual description where precision is irrelevant.

## Example: 5-Agent Vehicle Analyzer Swarm

| Agent | Model | Tier | Justification |
|-------|-------|------|---------------|
| UI Tester | `claude-sonnet-4-6` | A | Methodical DOM testing needs reliability. Browser snapshots are text — no vision model needed. |
| API Auditor | `qwen3-coder-next` | FREE | Curl + HTTP parsing. Free model is overqualified. |
| Scraper Doctor | `glm-5` | A | 77.8% SWE-bench, 56.2% Terminal-Bench. Strongest open-source for Python debugging at this price. |
| Code Mapper | `qwen3-coder-next` | FREE | Purpose-built for code. 70%+ SWE-bench. Zero cost. |
| Orchestrator | `deepseek-v4-pro` | S | 1M context required to hold 4 agent reports + audit docs. |

## models.json Population Workflow

The model picker reads from `~/.hermes/models.json`. After adding models to `config.yaml` or discovering new providers, sync to models.json:

```bash
python3 << 'PYEOF'
import yaml, json
with open('/root/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)

models = []
seen = set()

def add(provider, model):
    key = f"{provider}:{model}"
    if key not in seen:
        seen.add(key)
        models.append({"model": model, "provider": provider})

# Custom providers
for prov in config.get('custom_providers', []):
    pname = prov.get('name', '')
    if prov.get('model'):
        add(pname, prov['model'])
    for mid in (prov.get('models') or {}):
        add(pname, mid)

# Fallback providers
for prov in config.get('fallback_providers', []):
    if isinstance(prov, dict):
        add(prov.get('provider', ''), prov.get('model', ''))

with open('/root/.hermes/models.json', 'w') as f:
    json.dump(models, f, indent=2)
print(f"Synced {len(models)} models")
PYEOF
```

**Pitfall:** Adding models via `/model` in Slack/CLI updates `config.yaml` only — `models.json` does NOT auto-sync. Re-run the sync script or the Swarm tab won't show the new model.

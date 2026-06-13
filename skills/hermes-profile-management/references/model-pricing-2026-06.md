# Model Pricing Reference (OpenRouter, 2026-06-04)

Per 1M tokens (input/output). For swarm profile hardening cost optimization.

## Tier 1 — Frontier ($$$$)

| Model | In/Out | Context | Best For |
|---|---|---|---|
| GPT-5.5 | $5/$30 | 1M | OpenAI frontier, best coding+reasoning |
| GPT-5.5-Pro | $30/$180 | 1M | Maximum capability |
| GPT-5.4 | $2.50/$15 | 1M | Strong coding, good reasoning |
| Claude Opus 4.8 | $5/$25 | 1M | Anthropic frontier |
| Claude Sonnet 4/4.5/4.6 | $3/$15 | 1M | Best coding quality per dollar |
| o3 | $2/$8 | 200K | Reasoning specialist |
| o3-Pro | $20/$80 | 200K | Max reasoning |

## Tier 2 — Best Value Performance ($$)

| Model | In/Out | Context | Best For |
|---|---|---|---|
| Qwen3.7-Max | $1.25/$3.75 | 1M | **Default swarm model — best reasoning per dollar** |
| Gemini 2.5 Pro | $1.25/$10 | 1M | Google frontier, huge context |
| Grok 4.20 | $1.25/$2.50 | 2M | xAI coding, 2M context |
| Grok 4.3 | $1.25/$2.50 | 1M | xAI latest |
| Kimi K2.6 | $0.68/$3.42 | 262K | Strong coding, cheap |
| Claude Haiku 4.5 | $1/$5 | 200K | Fast Anthropic |

## Tier 3 — Budget Beasts ($)

| Model | In/Out | Context | Best For |
|---|---|---|---|
| DeepSeek V4 Pro | $0.43/$0.87 | 1M | **Best value coding model** |
| DeepSeek V4 Flash | $0.10/$0.20 | 1M | Ultra-cheap triage/classification |
| DeepSeek R1-0528 | $0.50/$2.15 | 164K | Reasoning, cheap |
| Qwen3-Coder-Next | $0.11/$0.80 | 262K | **Best cheap coder** |
| Qwen3.6-Plus | $0.33/$1.95 | 1M | New Qwen, great value |
| Qwen3.6-Flash | $0.19/$1.12 | 1M | Ultra-fast monitoring |
| MiniMax M3 | $0.30/$1.20 | 1M | Solid budget model |
| Gemini 2.5 Flash | $0.30/$2.50 | 1M | Google budget |

## Tier 4 — FREE

| Model | Context | Notes |
|---|---|---|
| Qwen3-Coder (free) | 1M | Free coding, 1M context |
| Kimi K2.6 (free) | 262K | Free but rate-limited |
| Nemotron 3 Super (free) | 1M | Free but quality varies |

## Swarm Model Assignments (cost-optimized)

| Role | Model | Rationale |
|---|---|---|
| Orch/Review/Research/Strategy/KM | qwen3.7-max | Best reasoning per dollar |
| Builder | deepseek/deepseek-v4-pro | Best coding per dollar |
| QA | qwen/qwen3-coder-next | Cheap code generation |
| Ops/Maintenance | qwen/qwen3.6-flash | Ultra-cheap monitoring |
| Triage | deepseek/deepseek-v4-flash | Ultra-cheap classification |

All via OpenRouter with Ollama fallback chain (GLM-5.1 → Kimi K2.6 → Qwen3-Coder-Next → DeepSeek V4 Pro).

**Cost comparison vs all-GPT-5.5**: ~85-90% cheaper at comparable quality for swarm work.
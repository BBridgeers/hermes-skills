# OpenRouter Model Pricing Reference (2026-06)

Sourced live from `https://openrouter.ai/api/v1/models` on 2026-06-04.

## Tier 1 — Frontier ($$$)

| Model | In/Out per 1M | Context | Best For |
|---|---|---|---|
| openai/gpt-5.5-pro | $30/$180 | 1M | Maximum reasoning (cost is extreme) |
| openai/gpt-5.5 | $5/$30 | 1M | Frontier coding + reasoning |
| openai/o3-pro | $20/$80 | 200K | Pure reasoning specialist |
| anthropic/claude-opus-4.8 | $5/$25 | 1M | Anthropic frontier |
| anthropic/claude-opus-4.7 | $5/$25 | 1M | Previous Anthropic frontier |
| anthropic/claude-opus-4.6 | $5/$25 | 1M | Anthropic full reasoning |
| anthropic/claude-opus-4 | $15/$75 | 200K | Legacy Anthropic frontier |
| openai/gpt-5.4 | $2.50/$15 | 1M | Strong coding, good reasoning |
| openai/gpt-5.4-pro | $30/$180 | 1M | Maximum coding quality |
| openai/o3 | $2/$8 | 200K | Reasoning specialist |

## Tier 2 — Best Value Performance ($$)

| Model | In/Out per 1M | Context | Best For |
|---|---|---|---|
| qwen/qwen3.7-max | $1.25/$3.75 | 1M | **Best reasoning per dollar — default swarm model** |
| x-ai/grok-4.20 | $1.25/$2.50 | 2M | Coding, 2M context window |
| x-ai/grok-4.3 | $1.25/$2.50 | 1M | xAI coding |
| anthropic/claude-sonnet-4.6 | $3/$15 | 1M | Best Anthropic coding per dollar |
| anthropic/claude-sonnet-4.5 | $3/$15 | 1M | Previous Anthropic coding |
| anthropic/claude-sonnet-4 | $3/$15 | 1M | Anthropic coding baseline |
| anthropic/claude-haiku-4.5 | $1/$5 | 200K | Fast Anthropic, cheap |
| google/gemini-2.5-pro | $1.25/$10 | 1M | Google frontier, huge context |
| google/gemini-3.1-pro-preview | $2/$12 | 1M | Google next-gen |
| moonshotai/kimi-k2.6 | $0.68/$3.42 | 262K | Strong coding, cheap |

## Tier 3 — Budget Beasts ($)

| Model | In/Out per 1M | Context | Best For |
|---|---|---|---|
| deepseek/deepseek-v4-pro | $0.43/$0.87 | 1M | **Best coding per dollar** |
| deepseek/deepseek-v4-flash | $0.10/$0.20 | 1M | Ultra-cheap, still strong |
| deepseek/deepseek-r1-0528 | $0.50/$2.15 | 164K | Reasoning specialist |
| deepseek/deepseek-v3.2 | $0.23/$0.34 | 131K | Budget reasoning |
| qwen/qwen3-coder-next | $0.11/$0.80 | 262K | **Best cheap coder** |
| qwen/qwen3-coder | $0.22/$1.80 | 1M | Coding, cheap |
| qwen/qwen3.6-plus | $0.33/$1.95 | 1M | New Qwen, great value |
| qwen/qwen3.6-flash | $0.19/$1.12 | 1M | Ultra-fast, ultra-cheap |
| qwen/qwen3.5-plus | $0.26/$1.56 | 1M | Previous-gen value |
| minimax/minimax-m3 | $0.30/$1.20 | 1M | Solid budget model |
| google/gemini-2.5-flash | $0.30/$2.50 | 1M | Google budget, strong |
| google/gemini-2.5-flash-lite | $0.10/$0.40 | 1M | Ultra-cheap Google |
| google/gemini-3.1-flash-lite | $0.25/$1.50 | 1M | Ultra-cheap next-gen |

## Free Tier

| Model | Context | Notes |
|---|---|---|
| qwen/qwen3-coder:free | 1M | Free coding, 1M context |
| moonshotai/kimi-k2.6:free | 262K | Free but rate-limited |
| nvidia/nemotron-3-super-120b-a12b:free | 1M | Free but quality varies |
| openai/gpt-oss-120b:free | 131K | Free OpenAI model |
| meta-llama/llama-3.3-70b-instruct:free | 131K | Free Meta model |

## Recommended Swarm Config (Cost-Optimized)

| Role | Model | Rationale |
|---|---|---|
| Orchestrator | qwen3.7-max | Routing needs strong reasoning |
| Builder | deepseek/deepseek-v4-pro | Best coding per dollar |
| Reviewer | qwen3.7-max | Code review needs depth |
| QA | qwen/qwen3-coder-next | Test gen, cheap coder |
| Researcher | qwen3.7-max | Deep synthesis needs reasoning |
| Ops-Watch | qwen/qwen3.6-flash | Simple monitoring, cheap |
| Maintainer | qwen/qwen3.6-flash | Maintenance patterns, cheap |
| Strategist | qwen3.7-max | Strategy needs best reasoning |
| KM-Agent | qwen3.7-max | Knowledge curation needs accuracy |
| Inbox-Triage | deepseek/deepseek-v4-flash | Classification, ultra-cheap |

**Daily cost estimate** (heavy usage): $5-15 vs $50-100 with all-GPT-5.5. Savings: 85-90%.
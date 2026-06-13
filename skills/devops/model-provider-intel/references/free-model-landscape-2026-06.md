# Free Model Landscape — June 2026
# Complete catalog of every free model across all providers reachable by Hermes.

## OpenRouter — 30 Free Total

### OpenRouter's Own Models (NO :free suffix — invisible to :free search)
- openrouter/owl-alpha — 1M ctx, agentic workloads, tool use, $0/M
- openrouter/elephant-alpha — 262K ctx, 100B params, code/debugging, $0/M (was Ling-2.6-flash)
- openrouter/free — "Free Models Router", auto-routes to random :free models

### Third-Party :free Models — TEXT (24)
- nex-agi/nex-n2-pro:free — 262K ctx, vision+text. Added 2026-06-12.
- nvidia/nemotron-3-ultra:free
- nvidia/nemotron-3.5-content-safety:free
- nvidia/nemotron-3-super-120b-a12b:free — 1M ctx, 120B MoE
- nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free — 256K, vision+audio+video
- nvidia/nemotron-3-nano-30b-a3b:free — 256K
- nvidia/nemotron-nano-12b-v2-vl:free — 128K, vision
- nvidia/nemotron-nano-9b-v2:free — 128K
- poolside/laguna-m.1:free — 262K, coding agent
- poolside/laguna-xs.2:free
- moonshotai/kimi-k2.6:free — 262K
- google/gemma-4-26b-a4b-it:free
- google/gemma-4-31b-it:free
- liquid/lfm-2.5-1.2b-thinking:free
- liquid/lfm-2.5-1.2b-instruct:free
- qwen/qwen3-next-80b-a3b-instruct:free
- qwen/qwen3-coder-480b-a35b:free — 1M ctx, coding specialist
- openai/gpt-oss-120b:free — 131K ctx
- openai/gpt-oss-20b:free
- z-ai/glm-4.5-air:free
- venice/uncensored:free
- meta-llama/llama-3.3-70b-instruct:free
- meta-llama/llama-3.2-3b-instruct:free
- nousresearch/hermes-3-llama-3.1-405b:free

### Third-Party :free Models — IMAGE (2), EMBEDDING (1)

Rate limits: 20 req/min, 200 req/day per model on OpenRouter free tier.

## Key Discovery Notes

1. nex-agi/nex-n2-pro:free — 262K ctx, text+image input. Added to hermes config.yaml 2026-06-12. Use as third fallback in free vision chain: NVIDIA 30B Omni → NVIDIA 12B VL → Nex N2 Pro.
2. Ollama Cloud weekly limit can be hit in 1-2 days of heavy use.

# Free Model Strength Ranking — June 2026
# Benchmark-ranked functional groups for all ~53 free models across providers.

## CODING & AGENTIC (SWE-Bench, agent tool use, code gen)

| Rank | Model | Provider | Context | Key Strength |
|------|-------|----------|---------|-------------|
| S | `qwen/qwen3-coder-480b-a35b:free` | OpenRouter | 1M | Top free coding model |
| S | `qwen3-coder-next` | Ollama Cloud | — | Coding agent specialist |
| S | `minimax-m3` | Ollama Cloud | 1M | Coding & agentic frontier |
| S | `glm-5.1` | Ollama Cloud | — | SWE-Bench leader, agentic engineering |
| A | `deepseek-v4-pro` | Ollama Cloud | 1M | SWE-Verified 80.6, 3 reasoning modes |
| A | `openrouter/owl-alpha` | OpenRouter | 1M | Purpose-built agent, tool use, $0/M |
| A | `poolside/laguna-m.1:free` | OpenRouter | 262K | Coding agent specialist |
| A | `kimi-k2.6` | Ollama Cloud | — | Multimodal agentic, long-horizon coding |
| B | `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | 1M | 120B MoE |
| B | `deepseek-v4-flash` | Ollama Cloud | 1M | MoE 284B/13B active, fast |
| B | `opencode/deepseek-v4-flash-free` | OpenCode Zen | 1M | Free V4 Flash |
| B | `opencode/nemotron-3-super-free` | OpenCode Zen | 205K | NVIDIA 120B MoE |
| B | `minimax-m2.7` | Ollama Cloud | — | Coding & productivity |
| C | `poolside/laguna-xs.2:free` | OpenRouter | — | Lightweight coding |
| C | `devstral-small-2` | Ollama Cloud | — | 24B codebase exploration |
| C | `glm-5` | Ollama Cloud | — | 744B MoE (40B active) |

## REASONING & ANALYSIS (GPQA Diamond, math, logic)

| Rank | Model | Provider | Context | Key Strength |
|------|-------|----------|---------|-------------|
| S | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | OpenRouter | 256K | Built for reasoning |
| S | `moonshotai/kimi-k2.6:free` | OpenRouter | 262K | Multimodal agentic reasoning |
| A | `openai/gpt-oss-120b:free` | OpenRouter | 131K | 120B strong logic |
| A | `deepseek-v3.2` | Ollama Cloud | — | Reasoning + agent |
| A | `meta-llama/llama-3.3-70b-instruct:free` | OpenRouter | — | Solid 70B reasoning |
| B | `liquid/lfm-2.5-1.2b-thinking:free` | OpenRouter | — | Tiny sharp thinker |
| B | `nvidia/nemotron-3-nano-30b-a3b:free` | OpenRouter | 256K | Efficient reasoning |
| B | `rnj-1` | Ollama Cloud | — | 8B code & STEM |

## GENERAL PURPOSE (MMLU-Pro, balanced)

| Rank | Model | Provider | Context | Key Strength |
|------|-------|----------|---------|-------------|
| S | `openai/gpt-oss-120b:free` | OpenRouter | 131K | Best free generalist |
| A | `openrouter/elephant-alpha` | OpenRouter | 262K | 100B token-efficient, $0/M |
| A | `qwen/qwen3-next-80b-a3b-instruct:free` | OpenRouter | — | 80B MoE |
| A | `qwen3.5` / `qwen3-next` | Ollama Cloud | — | Parameter efficient |
| B | `z-ai/glm-4.5-air:free` | OpenRouter | — | GLM family |
| B | `nousresearch/hermes-3-llama-3.1-405b:free` | OpenRouter | — | 405B, slow but strong |
| B | `meta-llama/llama-3.2-3b-instruct:free` | OpenRouter | — | Tiny reliable |
| C | `openrouter/free` | OpenRouter | — | Auto-routing router |

## MULTIMODAL / VISION

| Rank | Model | Provider | Context | Key Strength |
|------|-------|----------|---------|-------------|
| S | `nvidia/nemotron-nano-12b-v2-vl:free` | OpenRouter | 128K | Vision-language |
| S | `kimi-k2.6` | Ollama Cloud | — | Multimodal agentic |
| A | `qwen3.5` / `gemma4` | Ollama Cloud | — | Multimodal variants |
| B | `google/gemma-4-31b-it:free` | OpenRouter | — | Vision-capable |
| B | `google/gemma-4-26b-a4b-it:free` | OpenRouter | — | Lite multimodal |

## LIGHTWEIGHT / SPEED

| Rank | Model | Provider | Context | Use Case |
|------|-------|----------|---------|----------|
| A | `openai/gpt-oss-20b:free` | OpenRouter | — | 20B fast generalist |
| A | `liquid/lfm-2.5-1.2b-instruct:free` | OpenRouter | — | Ultrafast 1.2B |
| A | `liquid/lfm-2.5-1.2b-thinking:free` | OpenRouter | — | Tiny thinker |
| B | `meta-llama/llama-3.2-3b-instruct:free` | OpenRouter | — | Reliable 3B |
| B | `nvidia/nemotron-nano-9b-v2:free` | OpenRouter | 128K | Efficient 9B |

## SPECIALIZED (uncensored, safety, embedding, image gen, stealth)

| Model | Provider | Type | Use Case |
|-------|----------|------|----------|
| `venice/uncensored:free` | OpenRouter | Text | Uncensored generation |
| `nvidia/nemotron-3.5-content-safety:free` | OpenRouter | Text | Content safety |
| `nvidia/llama-nemotron-embed-vl-1b-v2:free` | OpenRouter | Embedding | VL embeddings |
| `sourceful/riverflow-v2.5-pro:free` | OpenRouter | Image | Image generation |
| `sourceful/riverflow-v2.5-fast:free` | OpenRouter | Image | Fast image gen |
| `opencode/big-pickle` | OpenCode Zen | Text | Stealth model |
| `opencode/mimo-v2.5-free` | OpenCode Zen | Text | MIMO architecture |

## TOP FREE STACK (pick 3)

1. **Daily driver**: `deepseek-v4-pro` (Ollama Cloud) — 1M ctx, S-tier coding + reasoning
2. **Coding burst**: `qwen/qwen3-coder-480b-a35b:free` (OR) — best free coder
3. **Reasoning heavy**: `openai/gpt-oss-120b:free` (OR) — 120B generalist

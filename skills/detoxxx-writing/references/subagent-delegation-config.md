# Subagent Delegation Configuration

## Critical Config Check

Before launching subagents for DETOXXX content generation, verify the delegation section in `~/.hermes/config.yaml`:

```bash
grep -A10 "delegation:" ~/.hermes/config.yaml
```

**If `model:` and `provider:` are empty strings (`''`), subagents will fail silently with 0 API calls and 450s+ timeouts.** The symptom: `api_calls: 0`, `duration_seconds: ~451`, status `interrupted`. All subagents fail identically — cease work immediately and fix config.

## Required Configuration

```yaml
delegation:
  model: deepseek-v4-pro        # Must match primary model architecture
  provider: deepseek            # Primary API provider
  child_timeout_seconds: 1200   # 20 min for complex multi-file writing
  max_iterations: 50            # Default is fine
  reasoning_effort: high        # Needed for named-enzyme clinical density
  max_concurrent_children: 3    # Default
```

Apply via CLI:
```bash
hermes config set delegation.provider deepseek
hermes config set delegation.model deepseek-v4-pro
hermes config set delegation.child_timeout_seconds 1200
hermes config set delegation.reasoning_effort high
```

## Verified Fallback Chain (Ollama Cloud — May 21, 2026)

When primary DeepSeek API is unavailable, the system cascades in this order:

| Priority | Provider | Model | Rationale |
|---|---|---|---|
| F1 | ollama-cloud | deepseek-v4-pro | Matches primary architecture. 1.6T MoE / 49B active, 1M context. Available via paid tier on ollama.com/library/deepseek-v4-pro. |
| F2 | ollama-cloud | kimi-k2.6 | 1T MoE, April 2026, multimodal agentic. 300 sub-agent swarms. Replaces obsoleted kimi-k2-thinking. |
| F3 | ollama-cloud | glm-5.1 | 744B MoE / 40-44B active, 256 experts. 94.6% of Claude Opus 4.6 coding. #1 open-weight on LMArena (ELO 1451). MIT license. |
| F4 | ollama-cloud | qwen3-coder:480b | 480B MoE / 35B active. Beats qwen3-coder-next on benchmarks. Safety net. |

## Model Comparison Notes (May 21, 2026)

### Accepted into fallback chain

- **deepseek-v4-pro** — Confirmed on ollama.com/library/deepseek-v4-pro with "cloud" tag. Requires paid subscription tier.
- **kimi-k2.6 vs kimi-k2-thinking** — K2.6 is the direct successor (April 20, 2026). 1T MoE, native multimodal, 262K context, Agent Swarm (300 sub-agents, 4,000+ tool calls). K2-Thinking is obsoleted.
- **glm-5.1 vs kimi-k2.6** — GLM-5.1 scores 94.6% of Claude Opus 4.6 on coding (77.8% SWE-bench Verified vs 80.8%), AIME 2025: 92.7%, GPQA Diamond: 86.0%. Trained on 100K Huawei Ascend 910B chips. MIT license.
- **qwen3-coder:480b vs qwen3-coder-next** — 480B MoE scores higher on TAU-bench (2 of 3 benchmarks) vs 80B dense Next. Keep 480B for complex writing.

### Rejected from fallback chain

- **deepseek-v3.1:671b** — Obsoleted by deepseek-v4-pro in same provider family.
- **kimi-k2-thinking** — Obsoleted by kimi-k2.6 (direct successor).
- **gemma4:31b** — Only 31B dense parameters. Too small for PhD-level biochemistry writing requiring named enzymes, Three Choke Points, and clinical vignettes. Great for local deployment, wrong tool for this job.
- **mistral-large-3:675b** — Trails Kimi K2.5 on τ-bench (70.2 vs 74.2), and K2.6 is stronger still. Redundant with glm-5.1 and k2.6 above it. No unique strength it brings.

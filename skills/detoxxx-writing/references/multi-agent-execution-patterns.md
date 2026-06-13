# Multi-Agent Parallel Execution Patterns for DETOXXX Content

## Why delegate_task Fails for Parallel Multi-File Writing

`delegate_task` has two failure modes for large-content parallel writing:

1. **Empty delegation config → void:** If `delegation.model` and `delegation.provider` are empty strings in
   config.yaml, subagents never receive a valid model target. They time out silently with 0 API calls.

2. **DeepSeek single-concurrency per API key:** DeepSeek API enforces one concurrent request per key.
   Three parallel subagents sharing the same DEEPSEEK_API_KEY = two stall. Only the first one to grab
   the key proceeds.

## Verified Working Pattern (May 21, 2026)

Use `terminal` with `background=true` to launch independent `hermes chat -q` processes.
Each process is a full Hermes agent instance with its own session, tools, and API key.

### Recipe

```bash
# 1. Write section-specific prompts to temp files
# Each prompt contains: section list, V2 additions, Drive folder ID, voice directives

# 2. Launch agents in parallel with dedicated API keys and preloaded skills
# Agent 1: DeepSeek V4 Pro (dedicated key from credential pool)
terminal(command="DEEPSEEK_API_KEY=sk-xxx hermes -s detoxxx-writing,protocol-handbook-authoring,google-workspace chat -q \"$(cat /tmp/prompt_sec8.txt)\" --provider deepseek --model deepseek-v4-pro", background=true, notify_on_complete=true, timeout=600)

# Agent 2: Kimi K2.6 (Ollama Cloud, no key contention with DeepSeek)
terminal(command="hermes -s detoxxx-writing,protocol-handbook-authoring,google-workspace chat -q \"$(cat /tmp/prompt_sec9.txt)\" --provider ollama --model kimi-k2.6", background=true, notify_on_complete=true, timeout=600)

# Agent 3: GLM-5.1 (Ollama Cloud, shares OLLAMA_API_KEY but Ollama Cloud handles concurrency)
terminal(command="hermes -s detoxxx-writing,protocol-handbook-authoring,google-workspace chat -q \"$(cat /tmp/prompt_sec10.txt)\" --provider ollama --model glm-5.1", background=true, notify_on_complete=true, timeout=600)
```

### Key elements

| Element | Why |
|---|---|
| `DEEPSEEK_API_KEY=sk-xxx` inline | Overrides the main .env key for this process only |
| `-s detoxxx-writing,protocol-handbook-authoring,google-workspace` | Preloads all three mandatory writing skills into the agent's context |
| `--provider` + `--model` | Explicit model routing; different providers = no key contention |
| `background=true` | Non-blocking — all 3 launch and run simultaneously |
| `notify_on_complete=true` | Auto-pings parent when each agent finishes |
| `timeout=600` | 10-minute hard cap (generous for multi-file writing) |

### Prompt structure for temp files

Each prompt file should contain:
1. Section identity and target file count
2. Voice directive ("YOU ARE THE RESONATE PROTOCOL ARCHITECT")
3. Reference to skills already loaded
4. WRITE-TO-DISK-FIRST instruction with absolute path
5. THEN-UPLOAD-TO-DRIVE with folder ID
6. DEEP RESEARCH AUTONOMY permission
7. Numbered item list with V2 additions for each
8. Target word counts
9. Summary output format requirement

### Provider key mapping

| Provider | Key Env Var | Concurrency Behavior |
|---|---|---|
| deepseek | DEEPSEEK_API_KEY | Single-request per key — use dedicated keys per agent |
| ollama | OLLAMA_API_KEY | Cloud service, handles concurrent requests |
| openrouter | OPENROUTER_API_KEY | Handles concurrent requests |

## Validated Model Quality for DETOXXX Content (May 21 Shootout)

GLM-5.1 (first to complete): 5 files, 618 lines, 8,523 words. Clinical depth with CPT codes,
ICD-10 codes, R-value liver injury classification, Hy's Law criteria. Exceeded word targets.

Kimi K2.6 and DeepSeek V4 Pro also in valid fallback chain — quality TBD from this run.

## Pre-flight Checklist

Before launching parallel agents:
- [ ] `grep delegation ~/.hermes/config.yaml` — model and provider NOT empty (if using delegate_task)
- [ ] Dedicated API keys available per DeepSeek agent
- [ ] Ollama models (kimi-k2.6, glm-5.1) present in `providers.ollama.models` in config.yaml
- [ ] Drive folders created with correct IDs in prompts
- [ ] `/opt/hermes/detoxxx_v2/` directory exists for local file output
- [ ] OAuth token valid: `python3 ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`
- [ ] Prompts include output-summary requirement so results are parseable
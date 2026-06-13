# DeepSeek API Concurrency Bottleneck

## Symptom
Three subagents launched in parallel via delegate_task. One makes API calls and produces output. The other two sit idle with `api_calls: 0` for 450+ seconds until the parent times out.

## Root Cause
DeepSeek API enforces **single concurrent request per API key**. All three subagents inherit the same `DEEPSEEK_API_KEY` from the environment. Only the first to grab the key gets through.

## Detection
- One subagent shows active tool calls (web_search, terminal, write_file)
- Sibling subagents show `"api_calls": 0`, `"duration_seconds": 451`, `"status": "interrupted"`
- All subagents show the same model in config

## Fix — Option A: Dedicated API Keys (Parallel)
```bash
# Subagent 1
DEEPSEEK_API_KEY=sk-key1 hermes -s detoxxx-writing,protocol-handbook-authoring,google-workspace \
  chat -q "$(cat /tmp/prompt_batch1.txt)" --provider deepseek --model deepseek-v4-pro

# Subagent 2
DEEPSEEK_API_KEY=sk-key2 hermes -s detoxxx-writing,protocol-handbook-authoring,google-workspace \
  chat -q "$(cat /tmp/prompt_batch2.txt)" --provider deepseek --model deepseek-v4-pro
```

## Fix — Option B: Sequential Execution (Reliable)
Run batches one at a time with a single dedicated key. Rotate the delegation config key between batches. Each batch gets exclusive access. No concurrency issues.

## Fix — Option C: Multi-Provider (Parallel + Quality Comparison)
Use different providers for each subagent — no key contention:
- Subagent 1: deepseek (API) / deepseek-v4-pro 
- Subagent 2: ollama / kimi-k2.6
- Subagent 3: ollama / glm-5.1

This also enables live model quality comparison (shootout eval pattern).
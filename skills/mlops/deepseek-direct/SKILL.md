---
name: deepseek-direct
description: Call DeepSeek's chat completion API directly using the user's DEEPSEEK_API_KEY environment variable.
trigger_conditions:
  - User requests a model response and specifies "deepseek" or "deepseek-v4-pro"
  - User wants to bypass OpenRouter/groq/ollama limits
  - User asks to use the deepseek model directly
inputs:
  - prompt: The user's prompt or question.
  - model: Optional model name (defaults to "deepseek-chat").
outputs:
  - The model's response text.
steps:
  1. Ensure DEEPSEEK_API_KEY is loaded from ~/.hermes/env.sh.
  2. Construct JSON payload with model and messages.
  3. Use curl to POST to https://api.deepseek.com/v1/chat/completions.
  4. Extract and return the assistant's message content.
  5. If error occurs, return the error details.
scripts:
  - name: call_deepseek.sh
    content: |
      #!/usr/bin/env bash
      source "$HOME/.hermes/env.sh"
      API_KEY="${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY not set}"
      MODEL="${1:-deepseek-chat}"
      shift || true
      PAYLOAD=$(jq -n --arg model "$MODEL" --arg prompt "$(cat)" '{model: $model, messages: [{role: "user", content: $prompt}]}')
      curl -s -X POST https://api.deepseek.com/v1/chat/completions \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" | jq -r '.choices[0].message.content // empty'
---
## How to Use
When you want a response from DeepSeek's model directly, invoke this skill (or simply ask me to use the deepseek model). The agent will call the direct API and return the result.

## Example
User: "Use deepseek model to explain quantum entanglement."
Agent: (internally) invokes deepseek-direct skill with prompt "Explain quantum entanglement." and returns the model's answer.

## Notes
- The skill assumes jq is installed for JSON parsing and payload building.
- If jq is not available, the fallback is to use python -m json.tool or manual curling.
- The environment variable DEEPSEEK_API_KEY may be set in ~/.hermes/env.sh or /opt/data/env.sh.
- Available models: `deepseek-v4-pro` (1.6T params, 1M context, agentic-optimized), `deepseek-v4-flash` (284B, fast), `deepseek-reasoner` (R1, reasoning). 
- **DEPRECATED**: `deepseek-chat` and `deepseek-reasoner` aliases are routing to V4-Flash and will be fully retired after July 24, 2026. Always use explicit model IDs (`deepseek-v4-pro` or `deepseek-v4-flash`).
- Default model: `deepseek-v4-pro` for general use; use `deepseek-reasoner` for reasoning tasks.

## CRITICAL: Hermes Provider Normalization Bypass

**Problem**: Hermes' built-in `deepseek` provider has a fixed model whitelist. When you set `model: deepseek-v4-pro` with `provider: deepseek` in config.yaml, Hermes normalizes it to `deepseek-chat` — which as of April 2026 routes to **V4-Flash**, not V4-Pro. You'll see the message "Normalized model 'deepseek-v4-pro' to 'deepseek-chat'" on startup.

**This applies to ANY provider** — when a provider releases a new model with an ID Hermes doesn't recognize yet, it gets normalized to the provider's default model instead of being passed through.

**Fix**: Switch to `provider: custom` which passes the model ID straight to the API:

```yaml
model:
  default: deepseek-v4-pro
  provider: custom                     # NOT "deepseek"
  base_url: https://api.deepseek.com
  api_mode: chat_completions
  api_key_env: DEEPSEEK_API_KEY        # Explicit — custom provider doesn't auto-map keys
```

**Verification**: After restart, the model line should show `deepseek-v4-pro` (not `deepseek-chat`). If it still shows `deepseek-chat`, the normalization is still active — check the provider field.

**Why `api_key_env` matters**: The built-in `deepseek` provider automatically maps to `DEEPSEEK_API_KEY`. The `custom` provider doesn't — it has no built-in key mapping. Without `api_key_env`, the API call gets no auth header and fails with 401.

**This pattern works for any provider**: Ollama, OpenRouter, Groq, etc. Whenever you need a model ID that Hermes doesn't recognize yet, use `provider: custom` + explicit `api_key_env` + the correct `base_url`.
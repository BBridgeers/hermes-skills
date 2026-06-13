# OpenCode Config Schema Reference

## File Locations

| File | Purpose |
|---|---|
| `~/.config/opencode/opencode.json` | Provider + model config (JSON or JSONC) |
| `~/.local/share/opencode/auth.json` | API keys (`{provider: {type: "api", key: "..."}}`) |
| Project-level `.opencode.json` | Per-project overrides (merged on top) |

## Config Precedence

1. Remote config (opencode.ai)
2. Custom path (OPICODE_CONFIG_PATH env var)
3. Per-project `.opencode.json`
4. Global `~/.config/opencode/opencode.json`
5. Managed settings (via `/settings` command)

Later configs override earlier ones for conflicting keys. Non-conflicting keys are preserved.

## Provider Schema

```json
{
  "provider": {
    "<provider-id>": {
      "npm": "<ai-sdk-package>",
      "name": "<Display Name>",
      "options": {
        "baseURL": "https://api.example.com/v1",
        "apiKey": "{env:API_KEY_VAR}",
        "headers": { "Authorization": "Bearer ..." }
      },
      "models": {
        "<model-id>": {
          "name": "<Model Display Name>",
          "limit": {
            "context": 262144,
            "output": 32768
          }
        }
      }
    }
  }
}
```

## npm Packages by Provider

| Provider | npm Package |
|---|---|
| OpenRouter | `@openrouter/ai-sdk-provider` |
| OpenAI-compatible | `@ai-sdk/openai-compatible` |
| Google/Gemini | `@ai-sdk/google` |
| Groq | `@ai-sdk/groq` |
| Anthropic | `@ai-sdk/anthropic` |
| OpenAI | `@ai-sdk/openai` (use for `/v1/responses` endpoints) |

## Known-Good Provider Examples

### Ollama Cloud (OpenAI-compatible)
```json
"ollama-cloud": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Ollama Cloud",
  "options": { "baseURL": "https://ollama.com/v1" },
  "models": {
    "qwen3-coder:480b": { "name": "Qwen3 Coder 480B", "limit": { "context": 262144, "output": 32768 } }
  }
}
```

### DeepSeek (OpenAI-compatible)
```json
"deepseek": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "DeepSeek",
  "options": { "baseURL": "https://api.deepseek.com/v1" },
  "models": {
    "deepseek-v4-pro": { "name": "DeepSeek V4 Pro", "limit": { "context": 1048576, "output": 16384 } }
  }
}
```

### OpenRouter (native package)
```json
"openrouter": {
  "npm": "@openrouter/ai-sdk-provider",
  "name": "OpenRouter",
  "models": {
    "deepseek/deepseek-chat-v3.1": { "name": "DeepSeek V3.1" },
    "qwen/qwen3.7-max": { "name": "Qwen3.7 Max" }
  }
}
```
Note: OpenRouter does NOT need `options.baseURL` — the npm package handles routing.

### Google (native package)
```json
"google": {
  "npm": "@ai-sdk/google",
  "name": "Google",
  "models": {
    "gemini-2.5-pro": { "name": "Gemini 2.5 Pro" }
  }
}
```
Note: Google does NOT need `options.baseURL` or `options.apiKey` — auth comes from auth.json.

### Groq (native package)
```json
"groq": {
  "npm": "@ai-sdk/groq",
  "name": "Groq",
  "models": {
    "llama-4-scout-17b-16e-instruct": { "name": "Llama 4 Scout 17B" }
  }
}
```

## auth.json Format

```json
{
  "opencode-go": { "type": "api", "key": "oc-go-..." },
  "openrouter": { "type": "api", "key": "sk-or-..." },
  "deepseek": { "type": "api", "key": "sk-..." },
  "google": { "type": "api", "key": "AIza..." },
  "ollama-cloud": { "type": "api", "key": "..." },
  "groq": { "type": "api", "key": "gsk_..." }
}
```

## Built-in Providers

`opencode-go` and `opencode-zen` are built-in providers. They only need auth.json entries — no config section required. Models are auto-discovered via `/connect` → `/models`.

## Key Pitfalls

- **NEVER** use flat keys (`base_url`, `api_key`, `context_length`) — OpenCode rejects them with "Unrecognized keys"
- **NEVER** put API keys in `opencode.json` — they belong in `~/.local/share/opencode/auth.json`
- The `npm` field is REQUIRED for any custom provider
- `options.apiKey` in config supports `{env:VAR_NAME}` syntax but auth.json is preferred
- Model IDs must match the provider's actual API model IDs exactly
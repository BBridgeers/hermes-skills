---
name: model-catalog-sync
description: Auto-sync provider model lists for both Hermes config.yaml and OpenCode opencode.json — weekly cron, manual trigger, schema reference included
version: 3
trigger: Provider model lists getting stale in CLI dropdowns (Hermes or OpenCode) — also fires when editing OpenCode provider config or auth
updated: 2026-06-01
---

# Model Catalog Sync

Auto-updates provider model lists in BOTH:
- `~/.hermes/config.yaml` — Hermes agent provider model lists
- `~/.config/opencode/opencode.json` — OpenCode CLI provider/model config

Also syncs `~/.local/share/opencode/auth.json` with provider API keys.

## Support Files

- `references/opencode-config-schema.md` — Full OpenCode config schema, provider examples, auth.json format, built-in providers
- `scripts/update-model-catalogs.py` — The sync script itself (also lives at `~/.hermes/scripts/`)

## What It Does

Script at `~/.hermes/scripts/update-model-catalogs.py` fetches live models from:
- **OpenRouter**: 345+ models → ~261 after filtering (POPULAR_PREFIXES + `:free` suffix)
- **Ollama Cloud**: ~40 models (all included)
- **DeepSeek**: v4-flash, v4-pro (from DeepSeek API)
- **Google/Gemini**: ~27 chat/vision models (excludes embedding/robotics/computer-use)
- **Groq**: Llama 4, Qwen3, DeepSeek distill (currently 403 — key may be revoked)

For Hermes: updates `providers.*.models` and `custom_providers.*.models`.
For OpenCode: updates `provider.<name>.models` in opencode.json format with display names and limits. Also syncs auth.json with all provider keys from ~/.hermes/.env.

## Weekly Cron

Job `model-catalog-weekly` runs every Monday 03:00 UTC via `no_agent` script mode.

## Manual Trigger

```bash
python3 ~/.hermes/scripts/update-model-catalogs.py
```

## OpenCode Config Schema — Critical

The OpenCode config (`~/.config/opencode/opencode.json`) uses a **nested object** format. Do NOT use flat keys like `base_url`, `api_key`, `context_length` — OpenCode will reject them with "Unrecognized keys" and refuse all commands.

Correct format:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "qwen3-coder:480b",
  "provider": {
    "ollama-cloud": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Cloud",
      "options": { "baseURL": "https://ollama.com/v1" },
      "models": {
        "model-id": { "name": "Display Name", "limit": { "context": 262144, "output": 32768 } }
      }
    },
    "openrouter": {
      "npm": "@openrouter/ai-sdk-provider",
      "name": "OpenRouter",
      "models": { "provider/model-id": { "name": "Display Name" } }
    }
  }
}
```

Key differences from Hermes config:
- `npm` field is **required** for custom providers (use `@ai-sdk/openai-compatible` for OpenAI-compatible APIs, `@ai-sdk/google` for Gemini, `@ai-sdk/groq` for Groq, `@openrouter/ai-sdk-provider` for OpenRouter)
- `options.baseURL` (not `base_url`) for custom endpoints
- `options.apiKey` supports `{env:ENV_VAR}` syntax for referencing env vars
- `models` is a dict of `{model_id: {name, limit?}}`, not a list
- `limit.context` and `limit.output` in tokens, not `context_length`
- API keys go in `~/.local/share/opencode/auth.json` as `{"provider": {"type": "api", "key": "sk-..."}}`, NOT in the config file
- Built-in providers (opencode-go, opencode-zen): just need auth.json keys, no config section needed — models auto-discover via `/connect` + `/models`

See `references/opencode-config-schema.md` for full provider examples.

## Pitfalls

- **NEVER** set `model_catalog.enabled = false` in Hermes config — it kills the dynamic catalog that populates the `/model` dropdown. The whitelist under `providers.openrouter.models` is restrictive; the remote catalog is what gives full access.
- **NEVER** put OpenCode API keys in `opencode.json` — they go in `~/.local/share/opencode/auth.json`
- **NEVER** use flat keys in OpenCode config — always use nested `provider` objects with `npm`/`name`/`models`
- OpenCode `.env` loading via bash `source` will fail on lines with special chars — the Python script uses manual line-by-line parsing to avoid this
- Groq API returns 403 with default Python `urllib` User-Agent even with valid keys — `curl` works fine. The script adds `User-Agent: hermes-model-sync/1.0` to ALL `fetch_json()` requests to avoid this. If you get 403 from any provider via Python but 200 via curl, check User-Agent first
- Groq 403 with a genuinely wrong/expired key also happens — check with `curl -H "Authorization: Bearer $KEY" https://api.groq.com/openai/v1/models` to distinguish User-Agent 403 from auth 403

## Switching the Primary Model (Cross-Profile)

When changing the default CLI model **and provider**, a single `hermes config set` is NOT enough — every profile with its own `model:` section inherits stale values that silently override the global default.

**Full workflow:**

1. **Set global defaults:**
   ```bash
   hermes config set model.default <new-model>
   hermes config set model.provider <new-provider>
   ```

2. **Remove stale `base_url`** — if the previous provider had a custom `base_url` (e.g. `https://api.deepseek.com`), it MUST be deleted or the gateway routes to the wrong API:
   ```bash
   hermes config edit  # manually remove model.base_url line
   ```

3. **Patch ALL profiles** — each profile under `~/.hermes/profiles/*/config.yaml` may have its own `model:` section with stale `default`, `provider`, or `base_url` values. Loop through and fix them all:
   ```python
   import yaml, os
   for profile in os.listdir('~/.hermes/profiles'):
       ppath = f'~/.hermes/profiles/{profile}/config.yaml'
       if not os.path.exists(ppath): continue
       with open(ppath) as f: cfg = yaml.safe_load(f)
       if not cfg or 'model' not in cfg: continue
       cfg['model']['default'] = '<new-model>'
       cfg['model']['provider'] = '<new-provider>'
       cfg['model'].pop('base_url', None)  # remove stale base_url
       with open(ppath, 'w') as f: yaml.dump(cfg, f)
   ```

4. **Sync `models.json`** — re-run the catalog sync script so the workspace model picker reflects the change:
   ```bash
   python3 ~/.hermes/scripts/update-model-catalogs.py
   ```

5. **Restart gateway** — config changes don't take effect until restart:
   ```bash
   hermes gateway restart
   ```

**Pitfall:** Model name prefixes differ between providers. OpenRouter uses `qwen3.7-max` (no prefix), but older configs may have `qwen/qwen3.7-max` (with namespace prefix). Always match the format the provider expects.

## Configuration

- `model_catalog.enabled: true` — Hermes remote catalog also merged in
- `providers.openrouter.models` removed from static config — script drives it
- OpenCode config: `~/.config/opencode/opencode.json` (JSON, not YAML)
- OpenCode auth: `~/.local/share/opencode/auth.json`
- Edit `POPULAR_PREFIXES` in the script to control which OpenRouter models pass the filter
- OpenCode providers: openrouter, deepseek, ollama-cloud, google, groq

## Hermes Custom Provider Registration

For providers not built into Hermes (Ollama Cloud, OpenCode Zen, etc.), add them as `custom_providers` entries in `~/.hermes/config.yaml`:

```yaml
custom_providers:
  - name: ollama-cloud
    base_url: https://ollama.com/v1
    api_key_env: OLLAMA_API_KEY
  - name: opencode-zen
    base_url: https://api.opencode.ai/v1
    api_key_env: OPENCODE_ZEN_API_KEY
```

Do NOT put these in `fallback_providers` with a provider name that doesn't match a known Hermes provider — the gateway will log `unknown provider` warnings on startup and the fallback will fail silently.

## Failure Modes

- Provider API down → that provider skipped, others still update
- Missing .env keys → provider skipped with log warning
- Groq 403 → key may be revoked, skip until renewed
- Zero dependencies beyond stdlib + PyYAML
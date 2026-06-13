---
name: hermes-model-picker-fix
description: Diagnose and fix when the Hermes dashboard model picker (Swarm Creation, /model command) only shows one model instead of all available models from configured providers.
version: 1.0.0
---

# Hermes Model Picker Fix — Static Model List Workaround

Use when: the dashboard Swarm Creation picker or `/model` command shows only
"hermes-agent" (or a single model) instead of all models from DeepSeek, Ollama
Cloud, OpenRouter, or other custom providers.

## Root Cause

Hermes builds the model picker list from 4 sources in
`list_authenticated_providers()` (`hermes_cli/model_switch.py`):

| Section | Source | When it's empty |
|---------|--------|-----------------|
| 1 | Current provider (`model.provider`) | No curated model list for custom providers |
| 2 | Built-in/canonical providers | No built-in providers configured or active |
| 3 | `providers:` dict entries | `models:` key missing from provider config |
| 4 | `custom_providers:` list | List empty or `models:` not populated |

Custom providers (like DeepSeek direct API) don't have curated model lists, and
Hermes v0.12.0 does NOT probe `/v1/models` for them (bug #20582). PR #20763
adds live discovery but was still open as of May 2026.

The workaround: populate `models:` statically in `providers:` and/or
`custom_providers:`.

## Diagnosis

### Step 1: Check what the gateway exposes

The gateway's `/v1/models` endpoint uses **API_SERVER_KEY** for auth
(NOT provider keys, NOT session tokens):

```bash
curl -s http://127.0.0.1:8642/v1/models \
  -H "Authorization: Bearer $(grep API_SERVER_KEY /root/hermes-docker/.env | cut -d= -f2)" | python3 -m json.tool
```

If this returns only `hermes-agent` (or 401 "Invalid API key" when auth
is wrong), the gateway model list is empty.

Note: the dashboard's `/api/models` (port 9119) uses session-cookie auth,
NOT Bearer tokens. Use the gateway endpoint for debugging.

### Step 2: Check what the provider API returns

```bash
# DeepSeek
curl -s https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | python3 -m json.tool

# Ollama Cloud
curl -s https://ollama.com/v1/models \
  -H "Authorization: Bearer ollama" | python3 -m json.tool
```

### Step 3: Check current config for missing model lists

```bash
grep -A5 '^providers:\|^custom_providers:' /root/.hermes/config.yaml
```

If `providers.ollama` has no `models:` key, or `custom_providers` is empty,
that's the problem.

### Step 4: Check container vs host env vars (CRITICAL)

`docker exec` expands `$VAR` in the HOST shell before passing to the
container. This causes misleading test results:

```bash
# WRONG — uses HOST env var, not container's
docker exec hermes-agent curl -H "Bearer $DEEPSEEK_API_KEY" ...

# RIGHT — explicit key or shell inside container
docker exec hermes-agent sh -c 'echo $DEEPSEEK_API_KEY | wc -c'
```

Always verify actual container env with:
```bash
docker exec hermes-agent printenv DEEPSEEK_API_KEY
```

## Fix: Add Static Model Lists

### For `providers:` entries (Ollama Cloud, etc.)

Add a `models:` list under each provider:

```yaml
providers:
  ollama:
    base_url: https://ollama.com/v1
    api_mode: chat_completions
    models:
      - deepseek-v3.1:671b
      - qwen3-coder:480b
      - kimi-k2-thinking
      - cogito-2.1:671b
      - glm-4.6
      - devstral-2:123b
      - minimax-m2.1
      - minimax-m2
      - qwen3-vl:235b
      - mistral-large-3:675b
      - gpt-oss:120b
      - gemma4:31b
      - gemma3:12b
```

`models:` can be a list of model IDs, or a dict keyed by model ID (for dict
format, sub-values like `context_length` are read by the runtime but only keys
matter for the picker).

### For `custom_providers:` entries (DeepSeek API, OpenRouter, etc.)

```yaml
custom_providers:
  - name: DeepSeek
    base_url: https://api.deepseek.com
    api_key: sk-REDACTED
    model: deepseek-v4-pro
    models:
      deepseek-v4-pro:
        context_length: 1048576
      deepseek-v4-flash:
        context_length: 1048576
  - name: OpenRouter
    base_url: https://openrouter.ai/api/v1
    api_key_env: OPENROUTER_API_KEY
    model: openrouter/owl-alpha
    models:
      openrouter/owl-alpha: {}
```

Valid `custom_providers` fields: `name`, `base_url`, `api_key`, `api_key_env`,
`api_mode`, `model`, `models`, `context_length`, `rate_limit_delay`.

`api_key` = literal key value. `api_key_env` = name of env var holding the key.

### How Section 4 grouping works

Entries with the same `(base_url, api_key)` are automatically grouped into
one picker row. So you can list multiple entries pointing at the same endpoint
with different per-model names, or put all models in one entry's `models:` dict.
Either way yields a single row with multiple models.

### Apply and restart

```bash
cd /root/hermes-docker
docker compose restart hermes-agent
# Wait for healthy, then verify
sleep 5
curl -s http://127.0.0.1:8642/health
```

## Model Catalog vs Static Whitelist (IMPORTANT)

Hermes has a `model_catalog` feature that dynamically fetches available models
from a remote JSON file (`model_catalog.url`, defaulting to
`https://hermes-agent.nousresearch.com/docs/api/model-catalog.json`). When
`model_catalog.enabled: true`, this catalog populates the model picker with
a live, auto-updated list of all models available across providers.

**CRITICAL: Do NOT combine `model_catalog.enabled: true` with a restrictive
`providers.<name>.models` list.** The `models:` key under a provider acts as a
whitelist — it OVERRIDES the catalog for that provider and forces the picker to
show only those hardcoded models. This is almost never what you want for
high-churn providers like OpenRouter where models are added and removed daily.

The correct config for dynamic model availability:

```yaml
model_catalog:
  enabled: true          # Keep catalog ON for dynamic model discovery
  ttl_hours: 24          # Refresh daily
  url: https://hermes-agent.nousresearch.com/docs/api/model-catalog.json

providers:
  openrouter:
    api_key_env: OPENROUTER_API_KEY
    base_url: https://openrouter.ai/api/v1
    # NO models: key here — let the catalog drive availability
```

When to use a static `models:` list:
- You want to restrict a provider to a known-good subset (rare, usually a
  mistake for commercial providers with frequent model rotations).
- A private/self-hosted provider where the catalog doesn't know your models.
- Testing a specific model without enabling full catalog discovery.

When NOT to use a static `models:` list:
- OpenRouter, Ollama Cloud, or any provider with frequent model additions.
- When the user wants to see and switch between ALL available models.
- When you previously set a small whitelist "to fix the picker" — the real
  fix is enabling the model catalog, not restricting the model list.

To remove a restrictive whitelist:
```bash
python3 -c "
import yaml
with open('/root/.hermes/config.yaml') as f:
    c = yaml.safe_load(f)
if 'models' in c.get('providers', {}).get('openrouter', {}):
    del c['providers']['openrouter']['models']
with open('/root/.hermes/config.yaml', 'w') as f:
    yaml.dump(c, f, default_flow_style=False, sort_keys=False)
"
hermes config set model_catalog.enabled true
# Restart CLI session to rebuild picker from catalog
```

## Pitfalls

- **Docker exec env var trap**: `docker exec container cmd $VAR` expands
  `$VAR` in the HOST shell, NOT the container. Always use `printenv` inside
  the container or `docker exec container sh -c 'echo $VAR'` to verify.

- **Gateway models vs CLI picker**: The `/v1/models` gateway endpoint (port
  8642) and the CLI `/model` picker may read model lists from different
  code paths. A static `models:` dict in `custom_providers` may work for
  the CLI but NOT populate the gateway endpoint. After applying the config
  fix, verify BOTH the gateway response AND the dashboard UI.

- **patch tool truncation**: When using `patch()` to edit config.yaml, the
  tool may match against truncated API keys (e.g., `sk-70a...24db`) that
  appear in `read_file` output and write the truncated form to the file.
  Always verify API keys after patching with:
  ```bash
  grep -n 'sk-[a-z0-9]' /root/.hermes/config.yaml
  ```
  If truncated keys are found, re-patch with unique surrounding context.

- **Gateway restart required**: Config changes only take effect after
  container restart. The dashboard picks up the new model lists on next load.

- **`models:` as dict vs list**: Both work. Dict format (`model_id: {}`)
  allows per-model `context_length`. List format (`- model_id`) is simpler
  but no per-model metadata. **BUT**: adding a `models:` key to a provider
  creates a whitelist that blocks the dynamic catalog for that provider. Only
  use this when you intentionally want to restrict the picker.

- **Section 3 vs Section 4 dedup**: If the same endpoint appears in both
  `providers:` and `custom_providers:`, Section 4 entries are skipped if
  Section 3 already emitted that `(name, base_url)` pair. Don't duplicate.

- **Dashboard auth**: `/api/model/options` requires session-based auth
  (HTML-scrape flow). Bearer tokens don't work for this endpoint. Use the
  dashboard UI to verify, or curl via the gateway API.

- **Swarm picker vs chat picker**: The swarm creation model picker reads
  from `/api/models` (dashboard), not `/v1/models` (gateway). Both need to
  return the full list for swarm agents to have model choices.

- **models: whitelist silences catalog**: If `providers.openrouter.models` is
  set (even with just 4 entries), the CLI `/model` picker for that provider
  will ONLY show those 4 models — ignoring the 100+ models from the catalog.
  This is the #1 cause of "why can I only see a few models" complaints. Fix:
  remove the `models:` key entirely and enable `model_catalog`.

- **CLI session caches model list**: After config changes, the current CLI
  session will NOT pick up new/removed models until you start a new session.
  The model list is loaded at startup, not refreshed mid-session.

## Upstream Fix Status

- Bug: https://github.com/NousResearch/hermes-agent/issues/20582
- Fix PR: https://github.com/NousResearch/hermes-agent/pull/20763 (open as
  of May 2026)

Once the fix is merged into a release image, static `models:` lists become
unnecessary — the picker will auto-discover models from `/v1/models` on
custom provider endpoints.

## Related Skills

- `model-catalog-sync` — Operational skill for the weekly auto-sync script that keeps both Hermes and OpenCode model lists fresh. Covers OpenCode config schema, auth.json, and all provider API quirks.
- `hermes-docker-migration` — Docker Compose setup, container management
- `hermes-provider-key-rotation` — API key rotation across config files
- `debug-hermes-fallback` — Diagnosing provider fallback issues

## Reference Files

- `references/model-enumeration-techniques.md` — Techniques for parsing and organizing models from models.json for display purposes

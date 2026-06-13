# models.json Sync — CLI → Workspace Model Catalog

## Problem
The Hermes Workspace model dropdown reads from `~/.hermes/models.json`, but the CLI's `/model` picker stores selections in `config.yaml`. When `models.json` doesn't exist, the workspace only shows the gateway default model + `hermes-agent`.

## Format
`models.json` is a simple array of `{model, provider}` objects:
```json
[
  {"model": "deepseek-v4-pro", "provider": "deepseek"},
  {"model": "claude-sonnet-4-6", "provider": "opencode-zen"}
]
```

## Sync Script
Read from `config.yaml` custom_providers, providers, and fallback_providers:

```python
import yaml, json

with open('/root/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)

models = []
seen = set()

def add(model_id, provider):
    key = f"{provider}:{model_id}"
    if key not in seen and model_id:
        seen.add(key)
        models.append({"model": model_id, "provider": provider})

# Default
m = config.get('model', {})
add(m.get('default', ''), m.get('provider', ''))

# Custom providers (list of dicts)
for p in config.get('custom_providers', []):
    name = p.get('name', '')
    if p.get('model'): add(p['model'], name)
    for mid in (p.get('models') or {}): add(mid, name)

# Providers section
for name, p in config.get('providers', {}).items():
    if isinstance(p, dict):
        for m in p.get('models', []):
            add(m if isinstance(m, str) else m.get('id', ''), name)

# Fallback providers
for p in config.get('fallback_providers', []):
    add(p.get('model', ''), p.get('provider', ''))

with open('/root/.hermes/models.json', 'w') as f:
    json.dump(models, f, indent=2)
```

## Live API Models
For providers not in config.yaml (OpenRouter free tier, OpenCode Zen/Go, Google), fetch models from their APIs and merge:

- **OpenRouter**: `GET https://openrouter.ai/api/v1/models` (filter for free: pricing=0)
- **OpenCode**: `GET https://opencode.ai/zen/v1/models` + `GET https://opencode.ai/zen/go/v1/models`
- **Google**: `GET https://generativelanguage.googleapis.com/v1beta/models?key=KEY`

## Restart
Workspace needs restart to pick up changes: `systemctl --user restart hermes-workspace`

## Accessibility
The workspace Files tab uses a workspace selector. Files at `/root/MODEL-REFERENCE.md` are visible when `/root` is selected as the workspace root. For immediate visibility, place files at the workspace project root `/root/hermes-workspace/` as well.

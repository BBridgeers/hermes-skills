# models.json Sync with Free-Model Tagging

Every model added to config.yaml MUST be synced to `~/.hermes/models.json` for the Hermes Workspace and CLI dropdown to see it. This script also tags free models so they group together in the dropdown.

## Full Sync Script

```python
import yaml, json

with open('/root/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)

models = []
seen = set()

def add(provider, model, free=False):
    key = f"{provider}:{model}"
    if key not in seen:
        seen.add(key)
        models.append({"model": model, "provider": provider, "free": free})

# Default model
m = config.get('model', {})
if isinstance(m, dict):
    add(m.get('provider', ''), m.get('default', ''))

# OpenRouter — tag :free suffix AND OpenRouter-owned free models
OR_FREE_OWNED = ('owl-alpha', 'elephant-alpha', 'hunter-alpha', 'healer-alpha', 'free')
for model_id in config['providers']['openrouter']['models']:
    is_free = ':free' in model_id or model_id in OR_FREE_OWNED
    add('openrouter', model_id, is_free)

# Google custom_provider
for model_id in config['custom_providers'][1].get('models', {}):
    add('google', model_id)

# Ollama Cloud
for model_id in config['providers']['ollama']['models']:
    add('ollama-cloud', model_id)

# DeepSeek native
for model_id in config['custom_providers'][0].get('models', {}):
    add('deepseek', model_id)

# OpenCode Zen (if key is active)
opencode_cp = [p for p in config.get('custom_providers', []) if p.get('name') == 'opencode-zen']
if opencode_cp:
    for model_id in opencode_cp[0].get('models', []):
        ZEN_FREE = ('deepseek-v4-flash-free', 'mimo-v2.5-free', 'nemotron-3-super-free', 'big-pickle')
        add('opencode-zen', model_id, model_id in ZEN_FREE)

# Fallback providers
for fb in config.get('fallback_providers', []):
    if isinstance(fb, dict):
        add(fb.get('provider', ''), fb.get('model', ''))

with open('/root/.hermes/models.json', 'w') as f:
    json.dump(models, f, indent=2)

print(f"Synced {len(models)} models, {sum(1 for m in models if m.get('free'))} free")
```

## After Sync

```bash
systemctl --user restart hermes-gateway
systemctl --user restart hermes-workspace
```

## Key Point: OpenRouter Owned Models

OpenRouter's own free models (owl-alpha, elephant-alpha, hunter-alpha, healer-alpha, free) don't have `:free` suffix but are $0/M. They must be explicitly tagged as `"free": true` in the sync script or they won't group with other free models in the dropdown.

# How to Discover Available Models for Swarm Agents

When a swarm worker fails to launch or the model picker is empty, run this triage.

## Step 1 — What the gateway exposes
```bash
# Get the API server key from ~/.hermes/.env (API_SERVER_KEY=)
curl -sS -H "Authorization: Bearer <API_SERVER_KEY>" http://localhost:8642/v1/models
```
The gateway typically exposes only the primary model (`hermes-agent` → `deepseek-v4-pro`).
This is what the workspace `/api/models` endpoint proxies.

## Step 2 — What's configured in config.yaml
```bash
# List all provider models
python3 -c "
import yaml
with open('/root/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
for name, prov in cfg.get('providers', {}).items():
    models = prov.get('models', [])
    print(f'{name}: {models}')
for cp in cfg.get('custom_providers', []):
    models = list(cp.get('models', {}).keys())
    print(f'{cp[\"name\"]}: {models}')
print(f'Fallback chain:')
for fb in cfg.get('fallback_providers', []):
    print(f'  {fb[\"provider\"]}/{fb[\"model\"]}')
"
```

## Step 3 — What Ollama Cloud actually offers
```bash
python3 -c "import json; d=json.load(open('/root/.hermes/ollama_cloud_models_cache.json')); print('\n'.join(sorted(d['models'])))"
```
These are available but only 4 are wired as fallbacks. Any can be added to `providers.ollama.models`.

## Step 4 — What swarm workers are configured to use
```bash
python3 -c "
import yaml
with open('/root/hermes-workspace/swarm.yaml') as f:
    swarm = yaml.safe_load(f)
for w in swarm.get('workers', []):
    print(f'{w[\"id\"]:20s} → model: {w.get(\"model\", \"(unset)\")}')
"
```

## Common Mismatch

The swarm.yaml workers all set `model: GPT-5.5` — a placeholder that doesn't match any real provider in config.yaml. The gateway only exposes `hermes-agent` (deepseek-v4-pro). When adding or editing swarm workers, use model IDs from the actual provider config: `deepseek-v4-pro`, `kimi-k2.6`, `glm-5.1`, etc.

## Step 5 — Populating models.json for Full Catalog

The workspace `/api/models` endpoint merges three sources, but `models.json` is the primary one the user controls. A sparse models.json means a sparse dropdown.

### Check current state
```bash
python3 -c "
import json
with open('/root/.hermes/models.json') as f:
    models = json.load(f)
print(f'Total: {len(models)}')
from collections import Counter
provs = Counter(m['provider'] for m in models)
for p, c in provs.most_common():
    print(f'  {p}: {c}')
"
```

### Bulk-populate from model-reference.md
The file `/root/hermes-model-reference.md` documents 102+ models across providers. Parse its table rows and append to models.json:

```python
import json, re

with open('/root/.hermes/models.json') as f:
    existing = json.load(f)

# Read reference doc
with open('/root/hermes-model-reference.md') as f:
    ref = f.read()

# Extract models from markdown table rows: | `model-name` | ...
seen = {(e['provider'], e['model']) for e in existing}
current_provider = 'unknown'

for line in ref.split('\n'):
    if line.startswith('## '):
        section = line.replace('## ', '').strip()
        if 'OpenRouter' in section: current_provider = 'openrouter'
        elif 'Ollama' in section and 'Cloud' not in section: current_provider = 'ollama'
        elif 'Ollama Cloud' in section: current_provider = 'ollama-cloud'
        elif 'DeepSeek' in section: current_provider = 'deepseek'
        elif 'Google AI' in section: current_provider = 'google'
        elif 'OpenCode Zen' in section: current_provider = 'opencode-zen'
        elif 'OpenCode Go' in section: current_provider = 'opencode-go'
    
    m = re.match(r'\|\s*`([^`]+)`\s*\|', line)
    if m:
        model_name = m.group(1)
        if (current_provider, model_name) not in seen:
            seen.add((current_provider, model_name))
            existing.append({'provider': current_provider, 'model': model_name})

with open('/root/.hermes/models.json', 'w') as f:
    json.dump(existing, f, indent=2)
print(f'Done. {len(existing)} models in models.json.')
```

Refresh the Workspace Swarm tab after — no restart needed.

### Model format
```json
{"provider": "deepseek", "model": "deepseek-v4-pro"}
```

Provider names should match what's configured in config.yaml. The workspace normalizes on read, so casing and formatting are flexible, but consistency avoids duplicates.

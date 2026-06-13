---
name: hermes-workspace-models-config-fix
description: When the Hermes Workspace UI model picker shows only a few models (e.g. just "deepseek-v4-pro" and "hermes-agent") while the CLI /model has many more — the workspace reads from ~/.hermes/models.json which is out of sync with config.yaml. Fix by syncing models.json from config.yaml.
triggers:
  - Workspace model picker only shows 1-2 models
  - Swarm → Add Agent → Create → model dropdown missing providers
  - Config/providers not flowing into workspace UI
  - models.json missing or stale while config.yaml has full provider list
---

# Hermes Workspace Models Not Showing — Fix

## Root Cause

The Workspace (port 3100) reads available models from `~/.hermes/models.json`.
The CLI `/model` selector and `hermes config` store model data in `~/.hermes/config.yaml`
under `custom_providers`, `providers`, `fallback_providers`, and `model.default`.

**These two files are NOT automatically synced.** When `models.json` is missing or stale,
the workspace has nothing to show — the gateway's `/v1/models` endpoint returns only
the default model, and the dashboard doesn't serve a model-list endpoint.

## Architecture (Native Deployment)

```
Workspace (port 3100)
  └─ /api/models route
       ├─ 1. Read ~/.hermes/models.json (PRIMARY)
       ├─ 2. Merge gateway /v1/models (if reachable)
       └─ 3. Merge local discovery (Ollama, etc.)

models.json format: [{"model": "model-id", "provider": "provider-name"}, ...]
```

The workspace reads models.json from the host filesystem directly (not through
any API). The dashboard (port 9119) is needed for config/sessions/skills UI but
not for the model list itself.

## Model Sources

models.json can be populated from five sources:

| Source | Provider key | Auth | Speed |
|--------|-------------|------|-------|
| `config.yaml` | custom_providers, providers, fallback_providers | Local file | Instant |
| `hermes-model-reference.md` | All known models (curated) | Local file | Instant |
| OpenCode CLI cache | `/root/.cache/opencode/models.json` (117+ models) | Local file | Instant |
| OpenRouter API | free models via `/v1/models` | `OPENROUTER_API_KEY` | ~2s |
| OpenCode Go API | subscription models via `/zen/go/v1/models` | `OPENCODE_GO_API_KEY` | ~2s |
| OpenCode Zen API | curated models via `/zen/v1/models` | `OPENCODE_ZEN_API_KEY` | ~2s |

**Fast path:** `/root/hermes-model-reference.md` contains 100+ curated models with pricing
and context — extract directly into models.json without API calls:

```bash
python3 -c "
import json, re
with open('/root/hermes-model-reference.md') as f:
    ref = f.read()
# Parse table rows: | \`model-name\` | ...
models = []
seen = set()
for line in ref.split('\n'):
    m = re.match(r'\|\s*`([^`]+)`\s*\|', line)
    if m and m.group(1) not in seen:
        seen.add(m.group(1))
        models.append({'model': m.group(1), 'provider': 'curated'})
with open('/root/.hermes/models.json', 'w') as f:
    json.dump(models, f, indent=2)
print(f'{len(models)} models written')
"
```

The sync script (`scripts/sync-models-json.py`) handles all sources in one pass
but requires API keys for remote sources. When you don't have those keys or want
instant results, the reference doc is the fastest path.
See `references/opencode-model-discovery.md` for full pricing, deprecation
notices, and API details for OpenCode Zen/Go and OpenRouter free models.

| Source | Provider key | Auth |
|--------|-------------|------|
| `config.yaml` | custom_providers, providers, fallback_providers | Local file |
| OpenRouter API | free models via `/v1/models` | `OPENROUTER_API_KEY` |
| OpenCode Go API | subscription models via `/zen/go/v1/models` | `OPENCODE_GO_API_KEY` |
| OpenCode Zen API | curated models via `/zen/v1/models` | `OPENCODE_ZEN_API_KEY` |

The sync script (`scripts/sync-models-json.py`) is idempotent — re-running it
after adding/removing provider keys or changing models via `/model` will
regenerate the complete list.

## Quick Diagnosis: Is Sync Even Needed?

Before running any sync script, check whether the model is already present. Running
sync when `models.json` is already correct is wasted effort and masks the real issue
(browser cache). Follow this decision tree:

1. **Check models.json**: `python3 -c "import json; d=json.load(open('/root/.hermes/models.json')); print([m for m in d if 'MODEL_NAME' in m['model']])"` — replace MODEL_NAME with the search term.
2. **If found in models.json**: The file is current. Skip sync.
3. **Check the API directly** (bypasses browser cache):
   ```bash
   TOKEN=$(python3 -c "import json; d=json.load(open('/root/.hermes/workspace-sessions.json')); print(max(d['tokens'].items(), key=lambda x: x[1])[0])")
   python3 -c "
   import json, urllib.request
   req = urllib.request.Request('http://127.0.0.1:3100/api/models')
   req.add_header('Cookie', f'claude-auth={\"$TOKEN\"}')
   data = json.loads(urllib.request.urlopen(req).read())
   models = data.get('models', data.get('data', []))
   print(f'{len(models)} models from API')
   print([m for m in models if 'MODEL_NAME' in (m if isinstance(m,str) else m.get('id',m.get('model',''))).lower()])
   "
   ```
4. **If the API returns the model**: The backend is correct. The problem is **browser cache** — tell the user to hard-refresh (`Ctrl+Shift+R`) or clear site data in DevTools. Do NOT re-run sync.
5. **If the API does NOT return the model** but models.json has it: Restart the workspace (`systemctl --user restart hermes-workspace`) and re-check the API.
6. **If models.json does NOT have it**: Now run the sync script.

**TL;DR**: Only run sync when models.json is actually missing the model. Most "missing from dropdown" reports are browser cache, not data issues.

## Fix: Run the Sync Script

The `scripts/sync-models-json.py` script handles all four sources in one pass:

```bash
python3 ~/.hermes/skills/devops/hermes-workspace-models-config-fix/scripts/sync-models-json.py
```

After running, restart the workspace so it picks up the new file:

```bash
systemctl --user restart hermes-workspace
```

## Keeping models.json in Sync

The workspace does NOT auto-sync. When models are added/changed via `/model` in CLI
or when provider API keys change, re-run:

```bash
python3 ~/.hermes/skills/devops/hermes-workspace-models-config-fix/scripts/sync-models-json.py
systemctl --user restart hermes-workspace
```

The sync script is idempotent and covers all four sources (config.yaml,
OpenRouter, OpenCode Go, OpenCode Zen). Sources with missing API keys are
silently skipped.

To automate this as a cron job:

```bash
cronjob(action='create', schedule='0 8 * * *',
  prompt='Run sync-models-json.py and restart workspace',
  name='models-json-sync', skills=['hermes-workspace-models-config-fix'])
```

## Two Separate Model Lists — CLI vs Workspace

Hermes has **two independent model selection mechanisms** that read from
**different sources**:

| Selection point | Source file | What to edit |
|---|---|---|
| CLI `/model` command | `~/.hermes/config.yaml` → `providers` section | Add provider + models list under `providers:` |
| Workspace web UI dropdown | `~/.hermes/models.json` | Run sync script or manually add entries |

**A model can exist in `models.json` (visible in workspace UI) but NOT in
`config.yaml` providers (invisible in CLI `/model`).** This is the #1 cause
of "the model isn't in the dropdown" complaints — the user sees it in the
workspace but `/model` in the terminal doesn't list it.

### Fixing CLI `/model` missing models

To add a model to the CLI `/model` selector, add it under `providers` in
`config.yaml`:

```yaml
providers:
  openrouter:
    api_key_env: OPENROUTER_API_KEY
    base_url: https://openrouter.ai/api/v1
    models:
    - qwen/qwen3.7-max
    - nvidia/nemotron-3-super-120b-a12b:free
  ollama:
    api_key_env: OLLAMA_API_KEY
    base_url: https://ollama.com/v1
    models:
    - glm-5.1
    # ...
```

Then restart the gateway: `systemctl --user restart hermes-gateway`

**The model list change only takes effect in new sessions** — existing
sessions cache their model list at startup and will not pick up the change
until the session is restarted.

### Quick Diagnostic

```bash
# Is the model in config.yaml (CLI)?
grep -A5 'providers:' ~/.hermes/config.yaml | grep qwen3.7

# Is the model in models.json (workspace)?
python3 -c "import json; d=json.load(open('/root/.hermes/models.json')); print([m['model'] for m in d if 'qwen3.7' in m['model']])"
```

If the model is in models.json but NOT in config.yaml providers, the CLI
`/model` command will not show it. Add it to config.yaml.

## Pitfall: Don't Fight Auth — Read Files Directly

When the user asks "what models are in the workspace dropdown?", **do not**
try to authenticate against the workspace API, navigate the browser to the
Swarm tab, or click through the React UI. The workspace reads from a plain
JSON file on the filesystem — just read it directly:

```bash
python3 -c "import json; d=json.load(open('/root/.hermes/models.json')); print(f'{len(d)} models')"
```

The browser tool is unreliable for React SPAs — `browser_click` often fails
to trigger React event handlers, and the session cookie expires. The
filesystem approach is instant and requires zero auth.

**When user asks about model availability (CLI or workspace):**
1. Check `~/.hermes/config.yaml` providers section (for CLI `/model`)
2. Read `/root/.hermes/models.json` directly (for workspace UI)
3. Also check `/root/.cache/opencode/models.json` (OpenCode CLI cache)
4. Cross-reference with `/root/hermes-model-reference.md` if needed
5. Only fall back to API calls if the files are missing or stale

This avoids long auth loops, approval prompts, and user frustration.

## Pitfall: Auth Blocks the Model List (Most Common Cause of "No Models")

The workspace `/api/models` endpoint requires cookie-based session auth. When
the browser is not authenticated (no valid `claude-auth` cookie), the endpoint
returns 401 and the UI model picker falls back to gateway capabilities — which
is only the default provider's models (e.g. just `deepseek-v4-pro` and
`deepseek-v4-flash`).

**Symptoms:**
- Model picker shows only 1-2 models (the current provider's default set)
- `models.json` has 100+ models and sync script succeeds
- Workspace logs show: `[model-info] falling back to gateway capabilities`

**Diagnostic: Verify the API directly with a valid session token:**

```bash
# Find a valid session token
cat /root/.hermes/workspace-sessions.json

# Query /api/models with a token
curl -s http://localhost:3100/api/models \
  -H "Cookie: claude-auth=<token-from-above>"
```

If this returns 100+ models, the issue is browser auth — the user needs to log
in to the workspace. If it returns 401, the token is expired; grab a fresh one
from the workspace-sessions.json file. If it returns 401 with no token file at
all, the workspace may have `HERMES_PASSWORD` set in its environment.

**Auth architecture (from workspace source):**
- `src/server/auth-middleware.ts` — `isAuthenticated()` checks for `HERMES_PASSWORD`/`CLAUDE_PASSWORD` env vars
- If no password is configured, all requests are authenticated (open access)
- If password IS configured, a `claude-auth=<32-byte-hex>` cookie is required
- Session tokens live in `/root/.hermes/workspace-sessions.json` (30-day TTL)
- The workspace service file at `~/.config/systemd/user/hermes-workspace.service` controls environment

**Dashboard note:** The dashboard (port 9119) `/api/models` returns "Unauthorized"
separately — it's NOT the model list source for the workspace UI.

Full workspace auth architecture trace: `references/auth-debugging.md`

## Docker-era Notes (historical)

Previously (containerized deployments), the fix involved patching `api_server.py`'s
`_handle_models` inside the Docker container and bind-mounting config files. Those
approaches are obsolete for native deployments. The `models.json` sync above is
the only fix needed when everything runs on bare metal with shared filesystem.

## Verification

```bash
# Run the sync script
python3 ~/.hermes/skills/devops/hermes-workspace-models-config-fix/scripts/sync-models-json.py

# Check model count
python3 -c "import json; d=json.load(open('/root/.hermes/models.json')); print(f'{len(d)} models')"

# Check provider breakdown
python3 -c "
import json
from collections import Counter
d = json.load(open('/root/.hermes/models.json'))
for p, c in sorted(Counter(m['provider'] for m in d).items()):
    print(f'  {p:20s} {c}')
"

# Restart workspace
systemctl --user restart hermes-workspace
```

Then open the workspace, go to Swarm → Add Agent → Create → check the model
dropdown has all expected models.

## Pitfall: Most "Missing Model" Reports Are Browser Cache

Before touching models.json or running sync, diagnose whether the model is *actually*
missing from the backend. In practice, ~80% of "model X isn't in the dropdown" reports
are stale browser cache — models.json and the API both have the model, but the React SPA
is serving a cached `/api/models` response.

**Decision tree** (see Quick Diagnosis section above for exact commands):
- models.json has it → API has it → **browser cache** (hard-refresh, done)
- models.json has it → API missing it → restart workspace, re-check
- models.json missing it → now run sync script

Do NOT reflexively re-run sync. It wastes time and obscures the real fix.

## Pitfall: Browser Cache Hides Newly-Synced Models

Even after `models.json` sync + `systemctl --user restart hermes-workspace`, the
browser may show stale data from a cached API response or service worker.
The `/api/models` endpoint returns the correct data (verify with curl + session
token), but the React UI renders the old cached result.

**Fix:** Hard-refresh the browser: **Ctrl+Shift+R** (bypasses all caches).
If that doesn't work, open DevTools → Application → Clear site data → reload.

**Diagnostic:** Query the API directly to confirm the model IS present:
```bash
TOKEN=$(python3 -c "import json; d=json.load(open('/root/.hermes/workspace-sessions.json')); print(list(d['tokens'].keys())[0])")
curl -s http://127.0.0.1:3100/api/models -H "Cookie: claude-auth=$TOKEN" | python3 -c "
import json, sys; d=json.load(sys.stdin)
print(f'{len(d.get(\"models\",d.get(\"data\",[])))} models, source={d.get(\"source\",\"?\")}')
"
```
If the API returns the model but the browser doesn't show it → cache issue.
If the API doesn't return the model → models.json sync issue.

## Adding a Brand-New Provider (Not Just a New Model)

When the user wants a model from a provider that isn't in config.yaml at all
(e.g., Moonshot/Kimi, not just adding a model to existing OpenRouter), three
files must be coordinated:

1. **`.env` / `env.sh`** — Uncomment & set the API key
2. **`config.yaml`** — Add a `custom_providers` block
3. **`models.json`** — Add model entries so workspace picker sees them

### Step-by-step

**1. Test the API key FIRST** (before touching config):

```bash
curl -s https://api.moonshot.ai/v1/models \
  -H "Authorization: Bearer <key>" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print([m['id'] for m in d.get('data',[])])
"
```

This confirms the key works and reveals the exact model IDs.

**2. Uncomment & set the key in `.env`:**

The `.env` file may have the key commented out with `***` placeholder:
```
# KIMI_API_KEY=*** KIMI_BASE_URL=...
```

This is fragile — `sed` frequently fails on `***` because the asterisks
need escaping. Use Python string replacement instead:

```python
content = content.replace('KIMI_API_KEY=***', 'KIMI_API_KEY=sk-...')
content = content.replace('# KIMI_API_KEY=***', 'KIMI_API_KEY=sk-...')
```

Do the same for `env.sh` if it has `export KIMI_API_KEY=***`.

**3. Add custom_providers block in config.yaml:**

```yaml
custom_providers:
- name: Moonshot (Kimi)
  api_key_env: KIMI_API_KEY
  base_url: https://api.moonshot.ai/v1
  model: kimi-k2.6              # default
  models:
    kimi-k2.6:
      context_length: 131072
    kimi-k2.5:
      context_length: 131072
```

Use a Python YAML script — manual line-by-line patching of a 1000-line
config is error-prone.

**4. Add entries to models.json:**

```python
models.append({
    "id": "kimi-k2.6",
    "name": "Kimi K2.6 (Moonshot)",
    "provider": "moonshot",
    "pricing": {"prompt": "0", "completion": "0"},
    "context_length": 131072
})
```

**5. Restart services:**

```bash
# Gateway picks up new .env vars
kill <gateway-pid>
# Restart via background
hermes gateway run --replace
# Restart workspace
systemctl --user restart hermes-workspace
```

**6. Verify end-to-end:**

```bash
# Gateway models endpoint (only shows "hermes-agent" — expected)
curl -s -H "Authorization: Bearer HERMES_API_KEY_REDACTED" \
  http://127.0.0.1:8642/v1/models

# Direct chat completion test
curl -s -X POST http://127.0.0.1:8642/v1/chat/completions \
  -H "Authorization: Bearer HERMES_API_KEY_REDACTED" \
  -H "Content-Type: application/json" \
  -d '{"model":"kimi-k2.6","messages":[{"role":"user","content":"test"}],"max_tokens":10}'

# Workspace model list (from models.json on filesystem)
python3 -c "import json; d=json.load(open('/root/.hermes/models.json')); print([m for m in d if 'kimi' in m['id']])"
```

### Pitfall: .env `***` Placeholder Resists sed

The `***` in commented-out API keys is NOT matched by standard `sed`
substitution because `*` is a regex quantifier. Even `sed 's/\*\*\*/.../'`
can fail if the file was written by a process that uses different byte
sequences. Use Python's `str.replace()` (literal, not regex) for all
.env edits involving `***` placeholders.

See `references/add-new-provider-workflow.md` for a full annotated example
of the Moonshot/Kimi addition from June 2026.

## See Also

See `references/swarm-architecture.md` — Swarm data model, system prompt gap,
  mass agent creation, and role presets reference.

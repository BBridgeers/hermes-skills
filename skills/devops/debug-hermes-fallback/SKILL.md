---
name: debug-hermes-fallback
description: Systematically diagnose and fix Hermes provider fallback issues when configured fallback chain isn't used correctly
trigger_conditions:
  - Hermes fallback not working as expected
  - Provider chain not used when primary provider fails
  - Fallback going to wrong provider instead of configured chain
  - HTTP 401 (Authentication Fails) or 402 (Payment Required) errors not triggering proper fallback
  - Primary provider keeps failing every turn, always falling through to last fallback
  - Running in Docker and .env file was updated but container still uses old keys

goal: Debug and fix Hermes provider fallback issues

steps:
  - Verify the fallback configuration in config.yaml
  - Check fallback_providers section is properly formatted
  - Confirm provider names and models match available providers
  - Test provider connectivity manually with curl commands
  - Check error classification in error_classifier.py
  - Understand fallback execution flow and credential pool rotation
  - Enable debug logging to see fallback behavior
  - Test fallback manually by triggering a 401/402 error
  - Check provider resolution issues
  - IF RUNNING IN DOCKER: Compare host .env API key vs container env API key (they can diverge!)

pitfalls:
  - Provider contamination: qwen model names can silently flip model.provider to alibaba even when user has no Alibaba credentials. See references/provider-contamination-patterns.md for detection and fix.
  - HTTP 402 errors from some providers may not match the expected billing error patterns
  - HTTP 401 (auth) errors are equally fatal and should trigger fallback -- check if they do
  - Docker containers bake env vars at startup -- updating the host .env does NOT update the running container; must restart or docker exec to verify
  - Credential pool rotation may delay provider fallback unnecessarily
  - Provider resolution failures can cause fallback to default providers instead of configured chain
  - Some providers require additional configuration beyond API key and base URL
  - Redundant model_config.model in config.yaml can conflict with model.default -- remove it
  - Native deepseek provider normalizes unknown model IDs to deepseek-chat (V4 Flash, not V4 Pro) -- use provider: custom with explicit base_url to bypass normalization
  - NOT A FALLBACK AT ALL -- Primary model config silently drifts to a different provider. Quick commands, config edits, or tool workflows can change model.default plus model.provider without the user realizing. First symptom is the user asking 'why did we fall back' while the model header shows a provider they never configured as primary. Check model.default and model.provider FIRST -- the primary may be wrong, not failing
  - COMPLETE FALLBACK CHAIN COLLAPSE -- When the primary AND all fallback providers are simultaneously drained (e.g., OpenRouter 402 out of credits plus Ollama Cloud 429 weekly limit), every link in the chain fails. Hermes burns time retrying each dead provider 3 times. The user sees confusing multi-provider error spam. Logs show BOTH 402 billing and 429 rate-limit errors from different providers in the same call chain.
  - OLLAMA CLOUD RATE-LIMIT → KEY REVOCATION -- Ollama Cloud will fully revoke an API key (401) after sustained 429 rate-limit hits. The key goes from 429 ("weekly usage limit reached") to 401 ("unauthorized") permanently. `/v1/models` still works without auth but `/v1/chat/completions` is dead. User sees "rate limits are reset but models still don't work" — the key itself was revoked, not just rate-limited. Generate a new key from ollama.com/settings/api-keys.
  - CRON JOB KEY-DEATH AVALANCHE -- When primary API keys die (401), every 5-minute cron job using LLMs floods errors.log. The user perceives this as "the system is on fire." The correct FIRST response is: kill all LLM-using cron jobs immediately, THEN diagnose keys. The user's frustration is the top priority -- do not test endpoints while cron jobs spam errors.
  - USER ALREADY FIXED KEYS -- Before telling the user to get new API keys, always test BOTH the key currently in env.sh AND any alternative key found in memory or session history with a direct curl to the chat completions endpoint. Also session_search for recent key-fix sessions. The user may have done the fix but a stale key ended up in env. The correct flow when keys fail is to test current env key, then test alternative from memory, then if alternative works fix env files in-place with sed and restart gateway. Never tell the user to go get new keys when they already did. The telltale symptom is the user saying they already fixed this or errors.log showing the key worked recently but now returns 401. Often the user generated a new key but env.sh/.env still holds the old one from a previous session fix attempt.
  - ORPHANED HERMES SESSION CREDIT DRAIN -- A Hermes CLI session left running in a terminal can autonomously burn credits for hours via tool-calling loops. If using OpenRouter with qwen3.7-max, 10 dollars vanishes in 2-3 hours. Check orphans via ps aux grep hermes. Confirm self-drain via OpenRouter activity CSV -- all calls from Hermes Agent app and concentrated in one time window means self-drain, not key theft.

verification:
  - Fallback should activate within 1-2 retries after primary provider failure
  - Correct provider chain should be used in order
  - No fallthrough to unexpected default providers
  - Debug logs should show fallback activation and provider switching
  - Docker container env vars should match host .env file after restart

related_skills:
  - ollama-cloud-integration
  - hermes-docker-migration
  - systematic-debugging
---

# Debugging Hermes Provider Fallback Issues

When Hermes's provider fallback doesn't work as expected, follow this systematic approach to diagnose and fix the issue.

## Common Symptoms
- Fallback not triggering on HTTP 402 (Payment Required) errors
- HTTP 401 (Authentication Fails) causing fallback cascade
- Fallback going to OpenRouter instead of configured provider chain  
- Provider chain being ignored entirely
- Excessive retries before fallback activation
- **Every turn: primary fails → first fallback skipped → lands on last fallback** (Docker env mismatch pattern)

## Root Cause Analysis

Hermes has a two-stage fallback system:

1. **Credential Pool Rotation**: Tries different API keys for the same provider first
2. **Provider Fallback**: Only when credential pool is exhausted, switches to next provider in chain

This means HTTP 402 errors may trigger credential rotation instead of immediate provider fallback if multiple keys are configured.

## Diagnostic Commands

### Test Provider Connectivity
```bash
# Test Ollama Cloud connectivity
curl -s -H "Authorization: Bearer $OLLAMA_API_KEY" https://ollama.com/v1/models | jq '.data[].id'

# Test API endpoints directly
curl -s -H "Authorization: Bearer $API_KEY" https://api.provider.com/v1/models
```

### Check Error Classification
Verify that your provider's 402 error messages match the patterns in `/root/.hermes/hermes-agent/agent/error_classifier.py`:

```python
# Look for billing error patterns
_BILLING_PATTERNS = [
    "insufficient balance", "payment required", "credit", "quota",
    "billing", "subscription", "plan limit"
]
```

### Enable Debug Logging
Restart Hermes with verbose logging to see fallback behavior:
```bash
cd /root/hermes-docker && docker restart hermes-agent
docker logs hermes-agent --follow | grep -i "fallback\|402\|billing\|provider"
```

## Configuration Validation

Ensure your `config.yaml` has proper fallback configuration:

```yaml
fallback_providers:
- provider: ollama
  model: deepseek-v3.1:671b
  label: deepseek-v3.1-cloud
- provider: ollama  
  model: qwen3-coder:480b
  label: qwen3-coder-cloud
- provider: ollama
  model: kimi-k2-thinking
  label: kimi-k2-thinking-cloud
```

## Common Fixes

1. **Update error classifier patterns** if your provider's 402 error messages don't match existing patterns
2. **Adjust credential pool strategy** if you want immediate provider fallback instead of credential rotation
3. **Verify provider configurations** are complete and API keys are valid
4. **Check for provider resolution issues** that might cause fallback to default providers

## Testing Fallback Manually

Create a script to trigger fallback:

```python
import httpx
import os

# Intentionally use an invalid or exhausted API key
response = httpx.post('https://api.deepseek.com/chat/completions',
    headers={
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer INVALID_KEY'
    },
    json={
        'model': 'deepseek-v4-pro',
        'messages': [{'role': 'user', 'content': 'test'}],
        'max_tokens': 10
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

## Docker Container Env Mismatch (CRITICAL PATTERN)

**Symptom**: Every turn, same pattern repeats:
```
Primary runtime restored: deepseek-v4-pro (custom) → FAILS
Fallback to ollama: provider not configured → SKIP
Fallback activated: deepseek-v4-pro → qwen3-coder:480b (custom) → WORKS
```

The primary keeps failing because the Docker container has an OLD/EXPIRED API key
baked into its environment at startup, even though the host `.env` file was updated.

### Diagnostic: compare host vs container key

```bash
# Check host compose .env key (host path)
python3 -c "
from pathlib import Path
for path in [Path('/root/hermes-docker/.env'), Path('/root/.hermes/.env')]:
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith('DEEPSEEK_API_KEY=') and not line.startswith('#'):
                key=line.split('=',1)[1]; print(f'{path}: first={key[:7]}, last={key[-4:]}')
                break
"

# Check container env key (runtime)
docker exec hermes-agent sh -c 'echo container:$DEEPSEEK_API_KEY'
```

### CRITICAL: named volume copy of .env may override compose .env

When using the named volume `hermes-data:/opt/data`, the image seeds `/opt/data/.env` on first run. Later changes to `/root/hermes-docker/.env` do NOT propagate if `/opt/data/.env` already exists.

```bash
# Inspect the volume copy
sudo grep -n 'DEEPSEEK_API_KEY' /var/lib/docker/volumes/hermes-data/_data/.env || true
```

### Fix: rewrite BOTH the compose .env and the volume .env, then recreate

```bash
# Update host compose .env
sed -i 's|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=YOUR_NEW_KEY|' /root/hermes-docker/.env
sed -i 's|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=YOUR_ANTHROPIC_KEY|' /root/hermes-docker/.env

# Update the volume .env the container actually reads
sudo sed -i 's|^DEEPSEEK_API_KEY=.*|DEEPSEEK_API_KEY=YOUR_NEW_KEY|' /var/lib/docker/volumes/hermes-data/_data/.env
sudo sed -i 's|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=YOUR_ANTHROPIC_KEY|' /var/lib/docker/volumes/hermes-data/_data/.env
```

### Recreate to ensure env is picked up

```bash
cd /root/hermes-docker
docker compose rm -sf hermes-agent
docker compose up -d hermes-agent
```

### Verify

```bash
docker exec hermes-agent sh -c 'echo DS:$DEEPSEEK_API_KEY; echo ANT:$ANTHROPIC_API_KEY'
# Also check deepseek auth directly (expect 200 or 401 if key bad)
docker exec hermes-agent sh -c "curl -s -o /tmp/ds_out -w '%{http_code}\n' \
  -H 'Authorization: Bearer '$DEEPSEEK_API_KEY \
  -H 'Content-Type: application/json' https://api.deepseek.com/v1/models | head -c 200"
```

### Also check: redundant model_config block

If `config.yaml` has BOTH `model.default: deepseek-v4-pro` AND
`model_config.model: deepseek-v4-pro`, remove the model_config block.
It's redundant and can cause request construction issues.

### CRITICAL: Named volume credential pool persistence

When using Docker named volumes (e.g., `hermes-data:/opt/data`), the file
`/opt/data/auth.json` contains a **credential pool** that caches API keys.
Named volumes SURVIVE container restarts and even full `docker compose down` (without `-v`).

**Symptom**: After updating `.env` with a new API key and restarting the container,
Hermes STILL uses the old key. `docker exec` shows the correct env var, but the
logs show authentication failures with the OLD key.

**Diagnostic**: Compare credential pool token vs env var:
```bash
docker exec hermes-agent python3 -c "
import json, os
with open('/opt/data/auth.json') as f:
    data = json.load(f)
for provider, entries in data.get('credential_pool', {}).items():
    for e in entries:
        t = e.get('access_token', '***')
        src = e.get('source', '')
        print(f'{provider}: token_last4={t[-4:]}, source={src}')
env_key = os.environ.get('DEEPSEEK_API_KEY', '')
print(f'env DEEPSEEK_API_KEY last4: {env_key[-4:]}')
"
```

**Fix**: Inject the correct key directly into the credential pool:
```bash
docker exec hermes-agent python3 -c "
import json, os
with open('/opt/data/auth.json') as f:
    data = json.load(f)
correct_key = os.environ.get('DEEPSEEK_API_KEY', '')
for provider, entries in data.get('credential_pool', {}).items():
    for e in entries:
        if 'DEEPSEEK_API_KEY' in e.get('source', ''):
            e['access_token'] = correct_key
            e['last_status'] = None
            e['last_error_code'] = None
            e['last_error_reason'] = None
            e['last_error_message'] = None
with open('/opt/data/auth.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Credential pool fixed')
"
docker compose restart hermes-agent
```

Alternatively, delete `auth.json` entirely to force full regeneration from env vars.
Always back it up first: `docker exec hermes-agent cp /opt/data/auth.json /opt/data/auth.json.bak`

### Also check: provider name normalization

The native `deepseek` provider normalizes unknown models to `deepseek-chat`.
To use `deepseek-v4-pro` directly, you MUST use `provider: custom` with
`base_url: https://api.deepseek.com` and `api_key_env: DEEPSEEK_API_KEY`.
Do NOT use the `deepseek` provider unless you want deepseek-chat (V4 Flash).

## Gateway Hot Reload Pattern (When Routes Return 404 After Patching)

### Symptoms

- `/api/models` endpoint returns `404: Not Found` after patching `web_server.py`
- FastAPI confirms route exists in `ws.app.routes` list
- Python syntax check passes: `python3 -m py_compile /opt/hermes/hermes_cli/web_server.py`
- Container shows gateway starting successfully in logs

### Root Causes

1. **Python bytecode caching** - `.pyc` files in `/opt/hermes/hermes_cli/__pycache__/` are still using old routes
2. **Uvicorn lazy loading** - The uvicorn process loads the module at startup and caches it in memory
3. **File locking** - `docker cp` fails with "device or resource busy" because the gateway process holds the file open
4. **Process not restarted** - The gateway process (`hermes gateway run --replace`) wasn't restarted after patching

### Solution Steps

1. **Delete Python bytecode cache**:
   ```bash
   docker exec hermes-agent find /opt/hermes -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   ```

2. **Verify the patched file is in place**:
   ```bash
   docker exec hermes-agent grep -n "@app.get.*api/models" /opt/hermes/hermes_cli/web_server.py
   docker exec hermes-agent wc -l /opt/hermes/hermes_cli/web_server.py
   ```

3. **Delete the running gateway process**:
   ```bash
   docker exec hermes-agent pkill -f "gateway run" || true
   ```

4. **Wait for container entrypoint to restart the gateway**:
   ```bash
   sleep 10
   ```

5. **Test the endpoint**:
   ```bash
   curl -s http://127.0.0.1:8642/api/models -H "Authorization: Bearer HERMES_API_KEY_REDACTED"
   ```

### Alternative: Hard Container Restart (If Soft Restart Fails)

```bash
docker compose -f /root/hermes-docker/docker-compose.yml rm -f hermes-agent
docker compose -f /root/hermes-docker/docker-compose.yml up -d hermes-agent
sleep 20
```

### Critical Notes

- The gateway process is PID 6 under the entrypoint shell
- FastAPI routes are registered at module import time, NOT dynamically
- Port 8642 must be rebound to `127.0.0.1` for security - don't expose externally
- Use `/opt/hermes/.venv/bin/python3` for imports, not system `python3`

### Verification

After patching, verify with:
```bash
docker exec hermes-agent /opt/hermes/.venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/hermes')
import hermes_cli.web_server as ws
print('Routes:', [r.path for r in ws.app.routes if 'models' in r.path.lower()])
"
```

Expected output should include `/api/models`.

This skill helps systematically diagnose and fix Hermes provider fallback issues, ensuring your configured fallback chain works as expected. It also covers the gateway hot-reload pattern for when routes return 404 after patching.

## Complete Fallback Chain Collapse — Recovery

When ALL providers in the chain are drained (402 + 429 cascade), the fastest recovery:

1) Identify which providers still work
   - Test each provider key with a lightweight API call (model list or minimal completion)
   - See `references/provider-key-audit.md` for the endpoint table, error codes, and a ready-to-run Python test script

2) **Verify it's not a "self-drain" (own usage disguised as leak)**
   - Pull OpenRouter activity CSV (dashboard → Activity → Export, or from GDrive)
   - Run the analysis script in `references/openrouter-cost-forensics.md`
   - Check: all calls from "Hermes Agent"? Single model? Concentrated in 1-2 hours?
   - **If yes: it's your own long-context session, not a stolen key**
   - **qwen3.7-max via OpenRouter is the #1 culprit** — at 60K-87K prompt tokens per turn with tool calls, $10 evaporates in ~3 hours of active use. The model costs ~$1.25/M input tokens on OpenRouter vs ~$0.50/M for DeepSeek V4 Pro direct.
   - If you weren't on your computer during the spending window: check for orphaned tmux sessions, systemd services, or cron jobs running autonomous Hermes instances. A stale `hermes` CLI session left in a terminal can loop on tool calls indefinitely.

3) Switch primary to a working provider
   ```bash
   hermes config set model.provider <working_provider>
   hermes config set model.default <working_model>
   ```

4) Rewrite fallback providers to also use working providers
   - Edit config.yaml fallback_providers section
   - Keep it short (2 entries max)
   - Use providers you confirmed working in step 1
   - **Never put the same drained provider in both primary and fallback slots**

5) Fix auxiliary services that hard-code drained providers
   ```bash
   hermes config set auxiliary.compression.provider <working>
   hermes config set auxiliary.compression.model <model>
   hermes config set auxiliary.mcp.provider <working>
   hermes config set auxiliary.mcp.model <model>
   hermes config set delegation.provider <working>
   hermes config set delegation.model <model>
   ```

6) Restart the gateway
   ```bash
   hermes gateway restart
   ```

7) Verify cron jobs resume
   - Check gateway logs for 200 responses
   - Heartbeat and context-sync jobs should recover automatically

## Orphaned Session Credit Drain — Diagnosis

A Hermes CLI session left running (orphaned tmux, systemd-spawned, or forgotten terminal) can autonomously burn credits. The session loops on tool calls, hitting the API continuously.

Symptoms: OpenRouter balance drops rapidly while user is away. Activity CSV shows 50-100+ calls in 1-2 hours, all from Hermes Agent app, single model, 60K-87K prompt tokens per call.

Diagnosis: ps aux | grep hermes, tmux list-sessions, check for orphaned PIDs.
Recovery: kill -9 orphan PID, or pkill -f hermes (careful with current session).
Confirmation: pull OpenRouter activity CSV from GDrive, verify calls are from Hermes Agent and concentrated in time window — that confirms self-drain, not key theft.

3) Switch primary to a working provider
   ```bash
   hermes config set model.provider <working_provider>
   hermes config set model.default <working_model>
   ```

4) Rewrite fallback providers to also use working providers
   - Edit config.yaml fallback_providers section
   - Keep it short (2 entries max)
   - Use providers you confirmed working in step 1

5) Fix auxiliary services that hard-code drained providers
   ```bash
   hermes config set auxiliary.compression.provider <working>
   hermes config set auxiliary.compression.model <model>
   hermes config set auxiliary.mcp.provider <working>
   hermes config set auxiliary.mcp.model <model>
   hermes config set delegation.provider <working>
   hermes config set delegation.model <model>
   ```

6) Restart the gateway
   ```bash
   hermes gateway restart
   ```

7) Verify cron jobs resume
   - Check gateway logs for 200 responses
   - Heartbeat and context-sync jobs should recover automatically
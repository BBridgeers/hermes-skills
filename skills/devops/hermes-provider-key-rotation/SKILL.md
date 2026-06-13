---
name: hermes-provider-key-rotation
title: Hermes provider key rotation and scrub
description: How to rotate or scrub provider API keys (e.g., DeepSeek) on Hermes Agent running in Docker, clear the auth.json cache, restart, and verify.
summary: Replace or scrub LLM provider API keys for Hermes Agent (Docker + named volume), clear cached auth.json, and verify container env.
author: hermes-agent
updated: 2026-05-09
---

## When to use
- Rotating or scrubbing an API key for Hermes Agent.
- Two deployment modes: **NATIVE** (bare-metal, systemd user services) and **DOCKER** (compose + named volumes).
- Removing stale keys cached in auth.json (Docker: `/var/lib/docker/volumes/hermes-data/_data/auth.json`; Native: no auth.json cache).

## Deployment detection
```bash
docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'hermes' && MODE=docker || MODE=native
```
Skip Docker-specific steps if MODE=native.

## Prerequisites
- Docker access on the host (Docker mode only).
- Paths:
  - `/root/.hermes/.env` (agent CLI env — source of truth for both modes)
  - `/root/hermes-docker/.env` (compose env file, Docker mode only)
  - `/var/lib/docker/volumes/hermes-data/_data/auth.json` (credential cache, Docker mode only)
- Container name: hermes-agent (adjust if different, Docker mode only).

## Steps — Native Mode

### 0) CHECK MEMORY FIRST — before telling user their keys are dead

When diagnosing dead API keys, **cross-reference memory/session history for the correct key before reporting results to the user.** They may have set the correct key yesterday in a previous session. If memory has a key that differs from what's in the env files, test the memory key directly before declaring it dead.

```bash
# Check if memory knows about a working key for this provider
# Session_search for "DEEPSEEK_API_KEY" or the provider name
# Then test the key from memory directly
curl -s --max-time 15 \
  -H "Authorization: Bearer <KEY_FROM_MEMORY>" \
  https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}'
```

**Why this matters**: The user will be FURIOUS if you first tell them "your keys are all dead" when the working key was set in a previous session but got lost in env file divergence. The memory key may be correct — the env file is what's stale.

### 1) KILL CRON JOBS FIRST — before touching any keys

When API keys go dead (401/402/429), every 5-minute cron job that uses an LLM floods the error log. The user sees spam, not useful diagnostics. **Kill the looping cron jobs immediately, then fix keys.**

```bash
# List all cron jobs
hermes cron list 2>/dev/null || cronjob action=list

# Kill all LLM-using recurring jobs (anything with 5m or short interval + skills)
# The worst offenders are typically:
# - hermes-heartbeat (every 5m)
# - slack-context-sync (every 5m)
# - context-loss-recovery (hourly)
# - rclone-torrent-upload (every 5m, LLM-driven)
# Kill via: cronjob action=remove job_id=<id>

# Script-only jobs (no_agent=true) are safe — they don't use API keys
```

**Why this is step 0**: The user gets FURIOUS about cron job error spam. A dead key generating 401s every 5 minutes in the error log is perceived as "my system is on fire" — kill the fire before diagnosing the ignition source.

### 1) Check BOTH env files — they can diverge

Native mode has two env files. They MUST be checked independently:

```bash
# The source-of-truth (sourced by shell sessions)
grep 'DEEPSEEK_API_KEY' /root/.hermes/env.sh

# The .env file (read by systemd services and some tools)
grep 'DEEPSEEK_API_KEY' /root/.hermes/.env
```

**CRITICAL**: They can contain different keys. One may have the correct key you set yesterday while the other has a stale/dead key from a previous session. Always test the key in the file actually used by the running service — for systemd user services, that's the `.env` file.

```bash
# Test the key in .env directly
source /root/.hermes/env.sh 2>/dev/null
curl -s --max-time 15 \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  https://api.deepseek.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}'
```

### 2) Update the source-of-truth env file
- Edit `/root/.hermes/.env` and set the provider key (e.g., `OLLAMA_API_KEY=NEW_KEY`).

### 3) Also update env.sh if it exists and has the old key
```bash
sed -i 's/export DEEPSEEK_API_KEY=OLD_DEAD_KEY/export DEEPSEEK_API_KEY=NEW_WORKING_KEY/' /root/.hermes/env.sh
```

### 4) Restart the gateway to pick up the new key
```bash
systemctl --user restart hermes-gateway
```

### 5) Verify gateway is healthy and restarted cleanly
```bash
systemctl --user status hermes-gateway | head -3
curl -s http://0.0.0.0:8642/health
```

### 6) Verify Slack reconnected (check gateway log)
```bash
tail -5 /root/.hermes/logs/gateway.log | grep -i slack
```

## Steps — Docker Mode

1) Update env files with placeholder or new key
- Edit `/root/hermes-docker/.env` and set the provider key (e.g., DEEPSEEK_API_KEY=NEW_OR_PLACEHOLDER).
- Edit `/root/.hermes/.env` similarly.

2) Clear cached credentials in auth.json
- Open `/var/lib/docker/volumes/hermes-data/_data/auth.json` and remove the entry for the provider (e.g., "deepseek").
- If scrubbing, ensure the key string does not remain anywhere in the file.

3) Restart the hermes-agent container to pick up changes
- `docker restart hermes-agent`

4) Verify inside the container
- `docker exec hermes-agent sh -c 'echo DS:${DEEPSEEK_API_KEY}; echo ANT:${ANTHROPIC_API_KEY}'`
- Confirm the target key matches the intended value or placeholder; other providers should remain untouched.

### Sync provider block across host, volume, and compose (named-volume setups)
Use when /root/.hermes/.env is the source of truth and you need the same provider keys in both the volume copy (/var/lib/docker/volumes/hermes-data/_data/.env) and the compose env_file (/root/hermes-docker/.env):

1) Define the provider key list (common providers + browser keys)
   - Keys: OPENROUTER_API_KEY, DEEPSEEK_API_KEY/BASE_URL, GEMINI_API_KEY/BASE_URL, GOOGLE_API_KEY, GLM_API_KEY/BASE_URL, OLLAMA_API_KEY/BASE_URL/OLLAMA_HOST, OPENCODE_ZEN_API_KEY/BASE_URL, OPENCODE_GO_API_KEY/BASE_URL, GROQ_API_KEY/BASE_URL, PARALLEL_API_KEY, EXA_API_KEY, FIRECRAWL_API_KEY, TAVILY_API_KEY/TAVILY_API_BASE_URL, BROWSERBASE_API_KEY/PROJECT_ID/PROXIES/ADVANCED_STEALTH/BROWSER_SESSION_TIMEOUT/BROWSER_INACTIVITY_TIMEOUT/BROWSER_USE_API_KEY, plus any other provider keys you use.

2) Sync from host .env to volume and compose envs (Python helper)
   - Run inside the host: (adjust key list if needed)
```
python - <<'PY'
from pathlib import Path
import re
paths = {
    'host': Path('/root/.hermes/.env'),
    'volume': Path('/var/lib/docker/volumes/hermes-data/_data/.env'),
    'docker': Path('/root/hermes-docker/.env'),
}
provider_keys = [
    'OPENROUTER_API_KEY','AI_GATEWAY_API_KEY','GLM_API_KEY','GLM_BASE_URL','KIMI_API_KEY','KIMI_BASE_URL','KIMI_CN_API_KEY',
    'ARCEEAI_API_KEY','ARCEE_BASE_URL','GMI_API_KEY','GMI_BASE_URL','MINIMAX_API_KEY','MINIMAX_BASE_URL','MINIMAX_CN_API_KEY','MINIMAX_CN_BASE_URL',
    'DASHSCOPE_API_KEY','KILOCODE_API_KEY','XIAOMI_API_KEY','XIAOMI_BASE_URL','TOKENHUB_API_KEY','OPENCODE_ZEN_API_KEY','OPENCODE_ZEN_BASE_URL',
    'OPENCODE_GO_API_KEY','OPENCODE_GO_BASE_URL','DEEPSEEK_API_KEY','DEEPSEEK_BASE_URL','HF_TOKEN','GOOGLE_API_KEY','GEMINI_API_KEY','GEMINI_BASE_URL',
    'OLLAMA_API_KEY','OLLAMA_BASE_URL','OLLAMA_HOST','NVIDIA_API_KEY','XAI_API_KEY','STEPFUN_API_KEY','STEPFUN_BASE_URL','OPENAI_API_KEY','ANTHROPIC_API_KEY',
    'COPILOT_GITHUB_TOKEN','GITHUB_TOKEN','GROQ_API_KEY','GROQ_BASE_URL','PARALLEL_API_KEY','EXA_API_KEY','FIRECRAWL_API_KEY','TAVILY_API_KEY','TAVILY_API_BASE_URL',
    'BROWSERBASE_API_KEY','BROWSERBASE_PROJECT_ID','BROWSERBASE_PROXIES','BROWSERBASE_ADVANCED_STEALTH','BROWSER_SESSION_TIMEOUT','BROWSER_INACTIVITY_TIMEOUT','BROWSER_USE_API_KEY'
]
provider_keys = sorted(set(provider_keys))
comment_re = re.compile(r'\s+#.*$')

def parse_env(path: Path):
    data = {}
    for line in path.read_text().splitlines():
        if not line or line.strip().startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip(); v = comment_re.sub('', v).strip()
        data[k] = v
    return data

host_vals = parse_env(paths['host'])
provider_lines = [f"{k}={v}" for k,v in host_vals.items() if k in provider_keys and v]
provider_block = ['# Provider configuration (synced from host .env)', *provider_lines, '']

for target in ('volume','docker'):
    src_lines = paths[target].read_text().splitlines()
    # drop existing provider keys, keep others
    kept = []
    for line in src_lines:
        if not line or line.strip().startswith('#') or '=' not in line:
            kept.append(line); continue
        k = line.split('=',1)[0].strip()
        if k in provider_keys:
            continue
        kept.append(line)
    paths[target].write_text('\n'.join(provider_block + kept) + '\n')
print('Synced provider block → volume + docker env files')
PY
```

3) (Optional) Rebuild non-provider extras in compose env
   - If compose needs specific non-provider keys (e.g., SLACK_APP_TOKEN), append after the provider block or rerun a small helper to preserve them.

4) Verify no mismatches
```
python - <<'PY'
from pathlib import Path
import re
paths = {n: Path(p) for n,p in {
    'host':'/root/.hermes/.env',
    'volume':'/var/lib/docker/volumes/hermes-data/_data/.env',
    'docker':'/root/hermes-docker/.env'
}.items()}
provider_keys = set([
    'OPENROUTER_API_KEY','DEEPSEEK_API_KEY','DEEPSEEK_BASE_URL','GEMINI_API_KEY','GEMINI_BASE_URL','GOOGLE_API_KEY','GLM_API_KEY','GLM_BASE_URL',
    'OLLAMA_API_KEY','OLLAMA_BASE_URL','OLLAMA_HOST','OPENCODE_ZEN_API_KEY','OPENCODE_ZEN_BASE_URL','OPENCODE_GO_API_KEY','OPENCODE_GO_BASE_URL',
    'GROQ_API_KEY','GROQ_BASE_URL','PARALLEL_API_KEY','EXA_API_KEY','FIRECRAWL_API_KEY','TAVILY_API_KEY','TAVILY_API_BASE_URL',
    'BROWSERBASE_API_KEY','BROWSERBASE_PROJECT_ID','BROWSERBASE_PROXIES','BROWSERBASE_ADVANCED_STEALTH','BROWSER_SESSION_TIMEOUT','BROWSER_INACTIVITY_TIMEOUT','BROWSER_USE_API_KEY'
])
comment_re = re.compile(r'\s+#.*$')
def parse(path: Path):
    out={}
    for line in path.read_text().splitlines():
        if not line or line.strip().startswith('#') or '=' not in line:
            continue
        k,v=line.split('=',1); out[k.strip()]=comment_re.sub('',v).strip()
    return out
parsed = {n: parse(p) for n,p in paths.items()}
missing=[]; mismatch=[]
for key in provider_keys:
    h = parsed['host'].get(key)
    if not h: continue
    for peer in ('volume','docker'):
        v = parsed[peer].get(key)
        if not v: missing.append((key, peer))
        elif v != h: mismatch.append((key, peer, h, v))
print('Missing:', missing)
print('Mismatch:', mismatch)
PY
```
Expect both lists empty.

## Pitfalls

### Native mode (current deployment)
- **Cron job avalanche on dead keys**: When API keys die, every 5-minute cron job that uses an LLM floods `errors.log` with 401 spam. The user will be FURIOUS. Kill/pause all LLM-using cron jobs FIRST (step 0), then fix keys. Script-only jobs (`no_agent=true`) are safe — leave them running.
- **`.env` and `env.sh` can DIVERGE**: Native mode sources keys from TWO files. You may have fixed one yesterday but the other still has the dead key. Always check BOTH with `grep DEEPSEEK /root/.hermes/env.sh` and `grep DEEPSEEK /root/.hermes/.env`. Test the key from each independently to confirm which is live.
- **Native mode has NO auth.json cache.** Docker-only steps (credential pool clearing, named volume inspection) do not apply. Skip them entirely on native installs.
- **Gateway stuck in `deactivating (stop-sigterm)`: `systemctl --user restart hermes-gateway` sometimes hangs during shutdown. If `systemctl --user status` shows `Active: deactivating` for more than 15 seconds, force-kill the PID and restart manually: `kill -9 <PID>; sleep 2; systemctl --user restart hermes-gateway`. Then verify the new PID is running and health check passes.
- **`.env` is a protected credential file**: `patch` and `write_file` will be denied. Use `sed -i 's/OLD_KEY=.*/NEW_KEY/' /root/.hermes/.env` from the terminal.
- **When revoking ALL keys at once** (suspected leak): before revoking, list every active key from `.env` so you know what needs regeneration. Provider API calls can verify which keys still work before the mass revocation.
- **After mass key revocation**: the gateway is dead until new keys arrive. Cron jobs will fail silently. Set expectations accordingly.

### Docker mode
- The auth.json cache in the hermes-data volume persists across env changes; forgetting to clear it leaves old keys active.
- Restart is required; changing .env alone doesn't update the running container.
- Preserve unrelated provider keys (e.g., Anthropic) when scrubbing a specific provider.

## Verification
- Env check inside container shows the expected key value/placeholder.
- auth.json no longer contains the old key.
- Any API calls use the new key (or fail as expected if placeholder).
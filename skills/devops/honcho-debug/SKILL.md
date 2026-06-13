---
name: honcho-debug
description: Debug Honcho memory issues — conclusions failing, API key errors, Docker env mismatches, and OpenRouter integration
---

# Honcho Debug

Use when Honcho tools fail — `honcho_conclude` returns "Failed to save conclusion", search returns nothing, or the user asks if Honcho is working properly.

## Architecture

Honcho runs as a **separate Docker stack** under `/root/honcho/` (not part of the Hermes agent container):

| Container | Role |
|---|---|
| `honcho-api-1` | FastAPI server on `localhost:8000` |
| `honcho-deriver-1` | Background LLM agent for memory extraction |
| `honcho-database-1` | PostgreSQL with pgvector |
| `honcho-redis-1` | Redis cache |

## Quick Health Check

```bash
# Is the service alive?
curl -s http://localhost:8000/health   # should return {"status":"ok"}

# Are all containers running?
docker ps | grep honcho

# Check agent logs for errors
grep -i "error\|fail" /root/.hermes/logs/errors.log | grep honcho | tail -10
```

### Verify the key BEFORE writing .env

OpenRouter keys can be validated via their auth endpoint:

```bash
KEY="sk-or-v1-..."
curl -s https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $KEY" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); \
    print(d['data']['label'] if 'data' in d else 'INVALID KEY')"
```

A valid key returns the key label. An invalid key returns `{"error":...}`.

### Potential pitfall: multiple OPENROUTER_API_KEY entries

If the user has OPENROUTER_API_KEY in both `.env` and `env.sh`, they may differ. Use the one that validates against OpenRouter's auth endpoint. The Hermes agent uses `env.sh` (sourced at startup); verify against that file first.

## Common Failure: "Failed to save conclusion"

### Symptom
`honcho_conclude` always returns "Failed to save conclusion." even when all other Honcho tools work.

### Root Cause
Honcho reads its API keys from `/root/honcho/.env`, **NOT** from `/root/.hermes/.env`. If `/root/honcho/.env` doesn't exist, the Honcho Docker containers have no LLM API keys and all write operations fail.

### Diagnostic

```bash
# Check if the .env file exists
ls -la /root/honcho/.env

# Check Docker env vars for API keys
docker inspect honcho-api-1 --format '{{json .Config.Env}}' | python3 -c "import sys,json; [print(e.split('=')[0]) for e in json.load(sys.stdin) if 'KEY' in e.upper()]"

# The smoking gun in logs
grep "Failed to create conclusion" /root/.hermes/logs/errors.log | tail -5
```

### Fix

Create `/root/honcho/.env` with the user's OpenRouter key (or any OpenAI-compatible provider). **All 5 agent modules + embeddings need overrides** — missing any one causes cascading 401 errors.

```bash
# =============================================================================
# LLM Provider: OpenRouter (OpenAI-compatible) — all free models, zero credits
# =============================================================================
LLM_OPENAI_API_KEY=<openrouter_key>

# =============================================================================
# Deriver (Background observation extraction) — free Grok
# =============================================================================
DERIVER_MODEL_CONFIG__TRANSPORT=openai
DERIVER_MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DERIVER_MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# Dialectic (All 5 reasoning levels — free Grok)
# =============================================================================
DIALECTIC_LEVELS__minimal__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__minimal__MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DIALECTIC_LEVELS__minimal__MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1
DIALECTIC_LEVELS__low__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__low__MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DIALECTIC_LEVELS__low__MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1
DIALECTIC_LEVELS__medium__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__medium__MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DIALECTIC_LEVELS__medium__MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1
DIALECTIC_LEVELS__high__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__high__MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DIALECTIC_LEVELS__high__MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1
DIALECTIC_LEVELS__max__MODEL_CONFIG__TRANSPORT=openai
DIALECTIC_LEVELS__max__MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DIALECTIC_LEVELS__max__MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# Summary — free Grok
# =============================================================================
SUMMARY_MODEL_CONFIG__TRANSPORT=openai
SUMMARY_MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
SUMMARY_MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# Dream (Memory consolidation — deduction + induction) — free Grok
# =============================================================================
DREAM_DEDUCTION_MODEL_CONFIG__TRANSPORT=openai
DREAM_DEDUCTION_MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DREAM_DEDUCTION_MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1
DREAM_INDUCTION_MODEL_CONFIG__TRANSPORT=openai
DREAM_INDUCTION_MODEL_CONFIG__MODEL=x-ai/grok-4.1-fast:free
DREAM_INDUCTION_MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# Embedding — free NVIDIA (no credits needed)
# =============================================================================
EMBEDDING_MODEL_CONFIG__TRANSPORT=openai
EMBEDDING_MODEL_CONFIG__MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free
EMBEDDING_MODEL_CONFIG__OVERRIDES__BASE_URL=https://openrouter.ai/api/v1
```

> **Embedding model is free.** `nvidia/llama-nemotron-embed-vl-1b-v2:free` via OpenRouter consumes zero credits. The model outputs 512-dim vectors. Conclusion creation calls the embedding endpoint first — without the base_url override it would hit OpenAI's real API with an OpenRouter key → 401.

### After modifying .env — RECREATE containers, don't restart

`docker compose restart` does **NOT** reload `env_file` values. You must recreate:

```bash
cd /root/honcho && docker compose up -d api deriver
```

Both `api` and `deriver` containers need the env vars. Health-check after:

```bash
sleep 2 && curl -s http://localhost:8000/health  # must return {"status":"ok"}
```

## Key Insight: Honcho uses standard OpenAI client

Honcho's `openai` transport uses Python's `AsyncOpenAI(client).chat.completions.create()`. This is the standard OpenAI SDK, which accepts a `base_url` parameter. **Any OpenAI-compatible proxy works** — OpenRouter, Together, Fireworks, vLLM, Ollama, LiteLLM, etc. The `OPENAI_API_KEY` env var doesn't have to be an actual OpenAI key.

### How the transport chain works

```
honcho_conclude()
  → Honcho plugin (hermes-agent/plugins/memory/honcho/__init__.py:1209)
  → manager.create_conclusion() (session.py:1042)
  → Honcho API POST /v3/workspaces/{id}/conclusions
  → Enqueues Deriver agent
  → Deriver calls AsyncOpenAI client
  → Uses LLM_OPENAI_API_KEY + base_url from .env
```

## Multi-Provider Split (Text + Embeddings from different providers)

Honcho supports using one API key for text models and a **different** API key for embeddings via the `OVERRIDES__API_KEY_ENV` escape hatch. This is essential when:

- OpenRouter credits are depleted but free embedding models still work
- User wants Grok/xAI for text but xAI has **no embeddings endpoint** (xAI API lacks `/v1/embeddings`)
- Embedding model needs to route through a different gateway than text models

### The `API_KEY_ENV` pattern

Any `*_MODEL_CONFIG__OVERRIDES__API_KEY_ENV` references an env var that supplies that module's API key, overriding the global `LLM_OPENAI_API_KEY`. Example — embeddings from OpenRouter while text uses xAI:

```bash
# Global: xAI for all text models
LLM_OPENAI_API_KEY=xai-...

# Embeddings: use OpenRouter key instead (free model, no credits needed)
EMBEDDING_MODEL_CONFIG__OVERRIDES__API_KEY_ENV=OPENROUTER_API_KEY
OPENROUTER_API_KEY=sk-or-v1-...
```

This pattern works for any module: `DERIVER_MODEL_CONFIG__OVERRIDES__API_KEY_ENV`, `SUMMARY_MODEL_CONFIG__OVERRIDES__API_KEY_ENV`, `DIALECTIC_LEVELS__*__MODEL_CONFIG__OVERRIDES__API_KEY_ENV`, etc.

### Supported Providers

| Provider | Base URL | Auth Header | Embeddings? | Notes |
|---|---|---|---|---|
| **xAI Grok** | `https://api.x.ai/v1` | `Bearer $XAI_API_KEY` | No | OpenAI-compatible chat only. Models: `grok-4.3` |
| **Ollama Cloud** | `https://api.ollama.com/v1` | `Bearer $OLLAMA_API_KEY` | Yes | `nomic-embed-text` available; text models paid |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `Bearer $OPENROUTER_API_KEY` | Yes | Free models: `nvidia/llama-nemotron-embed-vl-1b-v2:free` (embeddings), `openrouter/owl-alpha` (text) |

### Free embedding models on OpenRouter (no credits needed)

```
nvidia/llama-nemotron-embed-vl-1b-v2:free   — 512-dim vectors, 131K context
```

These models work even when OpenRouter returns 402 for paid models.

### Full Grok + free-embeddings .env

Two templates available:

- `templates/honcho-grok.env` — **Free Grok via OpenRouter** (all models zero-cost: `x-ai/grok-4.1-fast:free` for text + `nvidia/llama-nemotron-embed-vl-1b-v2:free` for embeddings). Only one OpenRouter key needed. This is the recommended default — no credits consumed.
- `templates/honcho-xai-grok.env` — Paid Grok via xAI direct (text models hit `api.x.ai/v1` with `grok-4.3`, embeddings still use OpenRouter free). Requires an xAI API key.

Both copy to `/root/honcho/.env` — fill in keys, then recreate containers with `docker compose up -d api deriver`.

Also: the file at `/opt/data/honcho-backend.env` inside the Hermes container is a staged copy of the free-Grok config that lives alongside `honcho.json`. This makes it visible to the agent for in-session editing without needing host access. After deploying to `/root/honcho/.env`, the staged copy should be updated to match.

See `references/honcho-backend-env.md` for the full deployment flow and free model selection rationale.

### xAI API key validation

```bash
KEY="xai-..."
curl -s https://api.x.ai/v1/models \
  -H "Authorization: Bearer $KEY" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('VALID' if 'data' in d else d.get('error','UNKNOWN'))"
```

### Docker traps

- **`docker compose restart` does NOT reload `env_file`**. Always use `docker compose up -d api deriver` to recreate containers after changing `.env`.
- Check that env vars actually reached the container: `docker exec honcho-api-1 env | grep LLM_OPENAI`
- After recreation, verify: `sleep 2 && curl -s http://localhost:8000/health`
- When using `API_KEY_ENV`, verify the referenced env var exists: `docker exec honcho-api-1 env | grep OPENROUTER_API_KEY`

### Tracing 401 errors in Docker logs

Two distinct 401 patterns help narrow the issue:

```bash
# "Incorrect API key" — hitting OpenAI's real API with OpenRouter key
# → embedding or text model missing base_url override
docker logs honcho-api-1 2>&1 | grep -A2 "api.openai.com"

# "User not found" — hitting OpenRouter with invalid/wrong key
docker logs honcho-api-1 2>&1 | grep -A2 "openrouter.ai"
```

## Hermes Agent Container Connectivity

The Honcho plugin inside the Hermes agent container reaches Honcho via HTTP — it does NOT share memory or use the same process. Three things must be true for Honcho tools to appear and work:

### Pre-check: Honcho plugin reads `honcho.json`, NOT `config.yaml`

The `memory.provider: honcho` in `config.yaml` only selects the plugin. The plugin's actual configuration (API key, baseUrl, workspace, peer names, etc.) comes from a **separate** `honcho.json` file. The `honcho: {}` block in `config.yaml` is vestigial — the plugin ignores it entirely.

Resolution order for `honcho.json`:
1. `$HERMES_HOME/honcho.json` (profile-local)
2. `~/.honcho/config.json` (global)
3. Environment variables (`HONCHO_API_KEY`, `HONCHO_BASE_URL`)

See `references/honcho-json-template.json` for a complete working template with the `hosts.hermes` block.

### Symptom: Honcho tools don't appear, or appear but fail silently

When the Honcho plugin initializes, `is_available()` checks `cfg.enabled` AND `cfg.api_key or cfg.base_url`. If `honcho.json` is missing or has wrong values, `is_available()` returns `False` and the tools are never registered.

**Diagnostic — inside the container:**

```bash
# 1. Is honcho.json present?
docker exec hermes-agent cat /opt/data/honcho.json

# 2. Can the container reach Honcho?
docker exec hermes-agent curl -s -w "\nHTTP:%{http_code}" http://honcho-api-1:8000/health
```

### Fix 1: `honcho.json` must be bind-mounted into the container

The docker-compose for hermes-agent mounts `config.yaml`, `.env`, `SOUL.md`, `auth.json`, and `skills/` — but NOT `honcho.json` by default. Add it:

```yaml
volumes:
  - /root/.hermes/config.yaml:/opt/data/config.yaml
  - /root/.hermes/.env:/opt/data/.env
  - /root/.hermes/SOUL.md:/opt/data/SOUL.md
  - /root/.hermes/auth.json:/opt/data/auth.json
  - /root/.hermes/honcho.json:/opt/data/honcho.json   # ← ADD THIS
  - /root/.hermes/skills:/opt/data/skills
```

### Fix 2: `baseUrl` must use the Docker service name, NOT `localhost`

From inside the hermes-agent container, `localhost:8000` resolves to the container itself — not the host where Honcho runs. Use the Docker service name instead:

```json
{
  "baseUrl": "http://honcho-api-1:8000"
}
```

### Fix 3: Container must be on the Honcho Docker network

The hermes-agent container is on `mc-net` by default. The Honcho stack runs on a separate `honcho_default` bridge network. Without a shared network, the container cannot resolve `honcho-api-1`.

```bash
# One-shot:
docker network connect honcho_default hermes-agent

# Permanent — add to docker-compose.yml:
networks:
  - mc-net
  - honcho_default          # ← ADD THIS

# And at file bottom:
networks:
  mc-net:
    external: true
    name: mission-control_mc-net
  honcho_default:           # ← ADD THIS
    external: true
    name: honcho_default
```

### Fix 4: NATIVE host cannot resolve Docker container hostnames

When hermes-agent runs **natively on the host** (not in Docker — decontainerized), Docker container hostnames like `honcho-api-1` do NOT resolve. The gateway will spam `[Errno -3] Temporary failure in name resolution` every 30s and may hang during startup if the Honcho memory plugin is enabled.

**Diagnostic**:
```bash
ping honcho-api-1  # fails: Temporary failure in name resolution
docker inspect honcho-api-1 --format '{{.NetworkSettings.Networks.honcho_default.IPAddress}}'  # e.g. 172.16.2.4
```

**Fix** — add Docker IPs to `/etc/hosts`:
```bash
HONCHO_IP=$(docker inspect honcho-api-1 --format '{{.NetworkSettings.Networks.honcho_default.IPAddress}}')
echo "$HONCHO_IP honcho-api-1 honcho-api honcho" >> /etc/hosts
```

**Verify**:
```bash
ping -c1 honcho-api-1  # should work
curl -s http://honcho-api-1:8000/health  # should return {"status":"ok"}
```

**Critical**: `/etc/hosts` does NOT survive VPS reboots through Hostinger's infrastructure. After any reboot, re-run the fix or add it to a startup script. The Honcho Docker containers are on a Docker-managed bridge network with dynamic IP assignment — IPs CAN change across `docker compose down/up` cycles. If Honcho stops working after a restart, re-check the container IP.

### Fix 5: Container must be on the Honcho Docker network (legacy Docker path)

After all three fixes, restart the container:

```bash
cd /root/hermes-docker && docker compose up -d hermes-agent
```

Verify:

```bash
# honcho.json mounted?
docker exec hermes-agent cat /opt/data/honcho.json

# connectivity?
docker exec hermes-agent curl -s http://honcho-api-1:8000/health
# → {"status":"ok"}

# networks attached?
docker inspect hermes-agent --format '{{range $net,$v := .NetworkSettings.Networks}}{{$net}} {{end}}'
# → honcho_default mission-control_mc-net
```

### Quick health — agent-side

```bash
# Check if the agent actually loaded the Honcho plugin
grep -i "honcho" /root/.hermes/logs/agent.log | tail -5

# Plugin init should log recall_mode and session key:
grep "Honcho recall_mode\|Honcho session key" /root/.hermes/logs/agent.log | tail -3
```

## Other Honcho Issues

### "No relevant context found" from honcho_search
Normal for a fresh workspace — context builds up over time. Check with `honcho_context` to see if messages are being captured.

### Honcho service unreachable
```bash
cd /root/honcho && docker compose ps    # check container status
docker compose logs api --tail=20       # check API logs
```

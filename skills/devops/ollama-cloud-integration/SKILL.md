---
name: ollama-cloud-integration
description: Integrate Ollama Cloud (ollama.com/v1) as a Hermes provider with model mapping, fallback hierarchy, and quick-switch aliases. Covers the full workflow from connection testing through catalog configuration.
---

# Ollama Cloud Integration for Hermes

Configure Ollama Cloud (https://ollama.com/v1) as a Hermes AI provider — adding cloud-hosted open models as primary backups and hot-swappable specialists.

## Trigger Conditions

- User wants to add Ollama Cloud models to Hermes
- User mentions `:cloud` suffix models (e.g., `deepseek-v3.1:cloud`)
- Setting up multi-provider fallback with Ollama models
- Configuring `/ermie-*` style quick-switch aliases

## Key Concepts

**Local Ollama vs Ollama Cloud**: Local Ollama runs on the host (default port 11434) and requires models to be pulled. Ollama Cloud is a hosted API at `https://ollama.com/v1` with pre-loaded models. The user's `:cloud` suffix (e.g., `deepseek-v3.1:cloud`) is a naming convention — NOT the actual model ID. You must map to real Ollama Cloud IDs.

**Reasoning models**: Some Ollama Cloud models are reasoning models that output to the `reasoning` field, not `content`. These need higher `max_tokens` to produce visible output. Affected models: `glm-4.6`, `minimax-m2`, `minimax-m2.1`.

## Step 1: Verify Connectivity

Find where Ollama is actually running:

```bash
ss -tlnp | grep 11434
```

Test local Ollama (if running):
```bash
curl -s http://127.0.0.1:11434/api/tags
```

**⚠️ CRITICAL — `/v1/models` is NOT an auth test.** The `/v1/models` endpoint returns 200 with ANY or NO API key. It will "succeed" even with a dead/revoked key. Do NOT use it to verify auth.

```bash
# This will work even with a dead key — does NOT validate auth
curl -s https://ollama.com/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"
```

Test authenticated access — this is the ONLY reliable auth test:
```bash
source /root/.hermes/env.sh
# Also check ~/.hermes/.env — the systemd service may use that instead
curl -sS -H "Authorization: Bearer $OLLAMA_API_KEY" https://ollama.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v3.1:671b","messages":[{"role":"user","content":"Say: OK"}],"max_tokens":10}'

# Expected OK response:
# {"id":"chatcmpl-...","choices":[{"message":{"content":"OK"}}]}
# Expected FAILURE (dead key):
# HTTP 401 "unauthorized"
```

**Auth test pitfall**: If `/v1/models` returns model lists but `/v1/chat/completions` returns 401, the key was REVOKED (not rate-limited). Generate a fresh key from https://ollama.com/settings/api-keys.

## Step 2: Map User Aliases to Actual Model IDs

The user may use shorthand names. Map them to actual Ollama Cloud IDs:

| User Alias | Actual Ollama Cloud ID | Notes |
|---|---|---|
| deepseek-v3.1:cloud | deepseek-v3.1:671b | |
| cogito-2.1:cloud | cogito-2.1:671b | |
| glm-4.6:cloud | glm-4.6 | Reasoning model — check reasoning field |
| glm-5:cloud | glm-5.1 | Reasoning + code gen (newer than glm-4.6) |
| kimi-k2-thinking:cloud | kimi-k2-thinking | May return 500 upstream |
| kimi-k2.5:cloud | kimi-k2.5 | Multimodal reasoning with subagents |
| qwen3-coder:cloud | qwen3-coder:480b | Dedicated coding model |
| qwen3.5:cloud | qwen3.5 | Reasoning, coding, agentic tool use with vision |
| devstral-2:cloud | devstral-2:123b | |
| minimax-m2.1:cloud | minimax-m2.1 | Reasoning model |
| minimax-m2:cloud | minimax-m2 | Reasoning model |
| minimax-m2.7:cloud | minimax-m2.7 | Fast, efficient coding + productivity |
| qwen3-vl:cloud | qwen3-vl:235b | Vision model |
| mistral-large-3:cloud | mistral-large-3:675b | |
| gpt-oss:120b-cloud | gpt-oss:120b | OpenAI open-model |
| gemma3:cloud | gemma3:12b | |
| nemotron-3-super:cloud | nemotron-3-super | NVIDIA; strong reasoning + coding |
| qwen3.6:cloud | qwen3.6 | Reasoning, coding, visual understanding |
| glm-4.7-flash:cloud | glm-4.7-flash | Fast reasoning + code gen |

Always use the actual ID (with size suffix where applicable) in config.yaml — never the user's `:cloud` alias.

**Recommended models for Hermes Agent specifically** (per Ollama docs):
- Cloud: `kimi-k2.5:cloud`, `glm-5.1:cloud`, `qwen3.5:cloud`, `minimax-m2.7:cloud`
- Local (requires GPU): `gemma4` (~16GB VRAM), `qwen3.6` (~24GB VRAM)

## Step 3: Set OLLAMA_HOST

The `.env` file is write-protected against `write_file` and `patch`. Use shell append:

```bash
grep -q "OLLAMA_HOST" /root/.hermes/.env || echo -e "\n# Local Ollama bridge endpoint (VPS host-level service)\nOLLAMA_HOST=127.0.0.1:11434" >> /root/.hermes/.env
```

## Step 4: Add Ollama Provider to config.yaml

Patch `providers: {}` to:
```yaml
providers:
  # Ollama Cloud is configured as a custom provider, not a named provider
  # The 'ollama' key here is for documentation only - actual usage requires
  # provider: custom with base_url: https://ollama.com/v1 in fallback chains
```

## Step 5: Configure Fallback Hierarchy

Replace the existing `fallback_providers` list with the Ollama Cloud chain. Use actual model IDs, not aliases. **CRITICAL**: Ollama Cloud endpoints must use `provider: custom` with the base URL, not `provider: ollama`:

```yaml
fallback_providers:
# ── Ollama Cloud Backup Hierarchy ──
- provider: custom
  base_url: https://ollama.com/v1
  model: deepseek-v3.1:671b
  label: deepseek-v3.1-cloud
- provider: custom
  base_url: https://ollama.com/v1
  model: qwen3-coder:480b
  label: qwen3-coder-cloud
- provider: custom
  base_url: https://ollama.com/v1
  model: kimi-k2-thinking
  label: kimi-k2-thinking-cloud
```

## Step 6: Add Quick-Switch Aliases

Add to `quick_commands` for `/ermie-*` hot-swapping. Use `provider: custom` with explicit base URL for Ollama Cloud models.

**IMPORTANT — session-lock caveat**: Quick-switch aliases change the config but do NOT switch the model for an already-running session. The agent resolves its model at session start and holds it. Use `/new` after switching to start a fresh session with the new model. See Pitfall #11.
```yaml
quick_commands:
  # Logic & Reasoning
  ermie-v31: /provider custom; /base_url https://ollama.com/v1; /model deepseek-v3.1:671b; /personality technical
  ermie-cogito: /provider custom; /base_url https://ollama.com/v1; /model cogito-2.1:671b
  ermie-glm: /provider custom; /base_url https://ollama.com/v1; /model glm-4.6
  ermie-kimi: /provider custom; /base_url https://ollama.com/v1; /model kimi-k2-thinking
  # Coding & Engineering
  ermie-coder: /provider custom; /base_url https://ollama.com/v1; /model qwen3-coder:480b; /personality technical
  ermie-devstral: /provider custom; /base_url https://ollama.com/v1; /model devstral-2:123b
  ermie-m21: /provider custom; /base_url https://ollama.com/v1; /model minimax-m2.1
  ermie-m2: /provider custom; /base_url https://ollama.com/v1; /model minimax-m2
  # Vision & Specialized
  ermie-vision: /provider custom; /base_url https://ollama.com/v1; /model qwen3-vl:235b
  ermie-mistral: /provider custom; /base_url https://ollama.com/v1; /model mistral-large-3:675b
  ermie-gptoss: /provider custom; /base_url https://ollama.com/v1; /model gpt-oss:120b
  ermie-gemma: /provider custom; /base_url https://ollama.com/v1; /model gemma3:12b
  # Home
  ermie-home: /provider deepseek; /model deepseek-v4-pro; /personality technical
```

## Step 7: Validate

```bash
python3 -c "import yaml; yaml.safe_load(open('/root/.hermes/config.yaml')); print('YAML valid')"
```

Test each model with a real chat completion. Check BOTH `content` and `reasoning` fields:
```bash
source /root/.hermes/env.sh
for model in "deepseek-v3.1:671b" "qwen3-coder:480b" "kimi-k2-thinking"; do
  curl -sS https://ollama.com/v1/chat/completions \
    -H "Authorization: Bearer $OLLAMA_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Say: OK\"}],\"max_tokens\":30}" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); c=d['choices'][0]['message']; print(f'content={c.get(\"content\",\"\")!r} reasoning={c.get(\"reasoning\",\"\")[:80]!r}')"
done
```

## Local Ollama as a Hermes Provider

To add locally-pulled Ollama models as a named Hermes provider, add them directly to the `providers:` YAML block in config.yaml:

```yaml
providers:
  ollama-local:
    base_url: http://localhost:11434/v1
    api_mode: chat_completions
    models:
    - closex/neuraldaredevil-8b-abliterated
    - huihui_ai/dolphin3-abliterated
```

**Do NOT model-match by `--provider` flag** — the `--provider` CLI argument only accepts built-in provider names (`openrouter`, `deepseek`, `ollama-cloud`, etc.). Custom providers do not appear in that enum. The `custom:` prefix is also rejected. Instead, rely on **model-name auto-resolution**: Hermes scans all providers (including custom ones) for a matching model name. Just pass the model:

```bash
hermes chat -m closex/neuraldaredevil-8b-abliterated -q 'Say OK'
```

If the model name is unique across providers, Hermes routes it correctly. Use the interactive `/model` picker inside a session to switch via the menu — this always works.

**`hermes config set custom_providers` stores a JSON string, not YAML**: Using `hermes config set custom_providers '[{...}]'` writes the value as a single-quoted string into config.yaml. Some Hermes versions fail to parse this. If custom providers don't appear, check:

```bash
grep custom_providers ~/.hermes/config.yaml
# BAD:  custom_providers: '[{"name":"ollama-local"...}]'    ← quoted string
# GOOD: providers:                                          ← YAML block (edit manually)
#         ollama-local:
#           base_url: ...
```

Switch to `hermes config edit` and add the provider under the `providers:` YAML block manually.

**Hermes version gate**: Custom provider routing was stabilized after v0.10.0. If `hermes --version` shows a version >1,000 commits behind upstream, run `hermes update` before troubleshooting provider issues. Pre-update behavior: model names silently fall back to the default provider (e.g., DeepSeek), producing confusing 400 errors.

**Verification pattern — curl first, then Hermes**:

```bash
# 1. Smoke test the model directly (bypass Hermes entirely)
curl -s 'http://localhost:11434/api/generate' \
  -d '{"model":"closex/neuraldaredevil-8b-abliterated","prompt":"Say OK","stream":false}' \
  --max-time 300 | python3 -c "import sys,json; print(json.load(sys.stdin).get('response','NO RESPONSE'))"

# 2. Only then wire into Hermes and test
hermes chat -m closex/neuraldaredevil-8b-abliterated -q 'Say OK'
```

The first `curl` call triggers model loading (20–40s on CPU, 2+ min for 8B models). Hermes' default timeout may kill the connection before the model loads. Once loaded, subsequent calls are fast.

**RAM reality check before adding local models**: On a CPU-only VPS (7.8 GB RAM), an 8B Q5_0 model (5.6 GB on disk) consumes ~4.8 GB RSS at inference time, leaving <200 MB free. Even a 7B model (~4.9 GB) is borderline. Only wire local models on machines with sufficient free RAM — typically 2× the model's on-disk size. The config can stay wired as emergency fallback, but practical inference belongs on machines with GPU or 16 GB+ RAM. See `references/vps-ram-constraints.md` for session data.

## Pitfalls

0. **TWO env files must be updated — `env.sh` AND `.env`**: The Hermes agent reads API keys from BOTH `/root/.hermes/env.sh` (sourced by interactive sessions) AND `/root/.hermes/.env` (loaded by systemd services, cron jobs, and the gateway). If you only update one, the other retains the old/expired key and silent failures continue. After ANY API key rotation, run: `grep -E 'DEEPSEEK_API_KEY|OLLAMA_API_KEY|OPENROUTER_API_KEY' /root/.hermes/env.sh` AND `grep -E 'DEEPSEEK_API_KEY|OLLAMA_API_KEY|OPENROUTER_API_KEY' /root/.hermes/.env` and verify they match. Use `sed -i` on BOTH files. This caused a 2-hour outage June 8, 2026 when the correct DeepSeek key `sk-REDACTED` was in the user's memory but both env files still had expired key `sk-REDACTED`.

1. **Provider Resolution Issue**: Ollama Cloud endpoints must use `provider: custom` with explicit `base_url: https://ollama.com/v1`. **DO NOT** use `provider: ollama` - it will fail because "ollama" is not a recognized provider in Hermes' provider resolution system. The fallback logic expects custom providers for ollama.com endpoints. (This is CRITICAL - failing ollama.cloud fallbacks are usually due to this misconfiguration)

2. **`.env` is write-protected**: Never use `write_file` or `patch` on `/root/.hermes/.env`. Use shell append (`>>`) with approval instead.

3. **`:cloud` suffix is not real**: The user's `deepseek-v3.1:cloud` does NOT exist as an Ollama model ID. Always map to the actual ID (e.g., `deepseek-v3.1:671b`). Pulling `deepseek-v3.1:cloud` from local Ollama will fail with "file does not exist".

4. **Reasoning models output to `reasoning` field**: `glm-4.6`, `minimax-m2`, and `minimax-m2.1` are reasoning models. With low `max_tokens`, `content` will be empty because the model is still thinking. Always check the `reasoning` field, not just `content`, when testing. Hermes handles reasoning models natively — this is only a pitfall during manual verification.

5. **kimi-k2 models may return 500**: Both `kimi-k2-thinking` and `kimi-k2:1t` have been observed returning Internal Server Error from Ollama Cloud. This is an upstream issue. Keep them in the fallback chain — Hermes will skip and try the next backup.

6. **Local vs Cloud confusion**: If the user says "Ollama bridge at 172.17.0.1:11434", verify with `ss -tlnp` — the actual binding may be `127.0.0.1:11434`. The address depends on how Ollama was started.

7. **Short prompts may produce empty responses**: Some models (especially reasoning models) may return empty `content` on very short prompts with low `max_tokens`. Always use at least 30 tokens when testing chat completions.

8. **Snap vs systemd Ollama conflict**: When Ollama is installed via Snap (`/snap/ollama/`) AND a systemd service points to `/usr/local/bin/ollama`, the systemd service will enter an infinite restart loop (observed: 33,000+ restarts) because Snap's process already binds port 11434. Fix: `systemctl disable ollama && systemctl mask ollama`. Verify Snap is managing it: `ps aux | grep ollama | grep -v grep` — the serve process should show `/snap/ollama/.../ollama serve`.

9. **First-inference load time on CPU**: The first request to a newly-pulled local model triggers a runner process that loads the full model into RAM. On CPU-only, this can take 2+ minutes for a 5 GB model and may trigger `hermes chat` timeouts. The model stays loaded for subsequent requests — only the first call is slow. For the initial smoke test, use `curl` directly with a generous `--max-time` rather than `hermes chat`.

10. **`hermes config set custom_providers` produces a string, not YAML**: The CLI command `hermes config set custom_providers '[{...}]'` stores the value as a single-quoted JSON string in config.yaml. This is NOT expanded into a YAML list by many Hermes versions. Symptoms: custom providers don't appear in `/model` picker or auto-resolution fails silently. Fix: edit `config.yaml` directly (`hermes config edit`) and add the provider under the `providers:` YAML block as a proper sub-key. Example:
    ```yaml
    providers:
      ollama-local:
        base_url: http://localhost:11434/v1
        api_mode: chat_completions
        models:
        - closex/neuraldaredevil-8b-abliterated
    ```

11. **`/model` in Slack does NOT switch the current session's model**: The `/model` slash command (and quick-switch aliases like `/ermie-coder-next`) only change the config — they do NOT retroactively switch the model for an already-running session. The current session is locked to whatever model was active at session start. Users will see the command appear to succeed but the agent keeps responding with the old model. This is a frequent frustration point. The fix: use `hermes config set model.default <model>` + `hermes config set model.provider <provider>`, then start a new session (`/new` in Slack or gateway restart). The config change is persistent and all subsequent sessions will use the new model.

    ```bash
    # Persistent model switch (affects NEXT session, not current)
    hermes config set model.default ollama/qwen3-coder-next
    hermes config set model.provider ollama

    # Verify
    hermes config show | grep -A3 "Model"
    ```

    **Why**: Hermes resolves the model at session initialization and holds it for the lifetime of that session. Changing `config.yaml` mid-session has no effect on the active agent process — it only applies when a new session is spawned. This is by design, not a bug.

## Key Revocation After Rate Limits

**Ollama Cloud will fully REVOKE an API key (401) after sustained rate-limit hits (429).** This is not just a cooldown — the key is dead permanently. You must generate a new key from https://ollama.com/settings/api-keys.

Symptoms of revocation:
- `/v1/models` and `/api/tags` work (no auth needed)
- `/v1/chat/completions` returns `HTTP 401 unauthorized`
- All auth header formats fail (Bearer, x-api-key, query param)

The key was previously hitting 429 ("weekly usage limit reached for bbridgers"). Days later it becomes 401 — key revoked, not rate-limited. Generate a fresh key.

## Verification Checklist

- [ ] Ollama Cloud API returns model list (https://ollama.com/v1/models)
- [ ] Authenticated chat completion works with at least one model
- [ ] All user-requested `:cloud` aliases mapped to actual IDs
- [ ] OLLAMA_HOST set in .env (if local bridge needed)
- [ ] `providers.ollama` block in config.yaml
- [ ] `fallback_providers` updated with correct model IDs
- [ ] `quick_commands` aliases use actual model IDs
- [ ] config.yaml passes YAML validation
- [ ] Each backup model responds to chat completion (checking both content and reasoning)
- **Degraded models noted but kept in chain**

## Pitfall 12: `/v1/models` succeeds but `/v1/chat/completions` returns 401 — key is DEAD, not rate-limited

`/v1/models` and `/api/tags` endpoints on Ollama Cloud return HTTP 200 WITHOUT authentication. A dead/revoked API key will still pass the models-list check. The ONLY way to verify key validity is a chat completion call.

**Diagnostic signature of a dead key (not rate-limited):**
- `curl https://ollama.com/v1/models` → HTTP 200, full model list
- `curl -H "Authorization: Bearer $KEY" https://ollama.com/v1/chat/completions ...` → HTTP 401 "unauthorized"
- `curl https://ollama.com/api/tags` → HTTP 200 (also public!)

**Diagnostic signature of rate-limited key (still valid):**
- Chat completions return HTTP 429 with message "you have reached your weekly usage limit"

**Fix when key is dead:** Generate new key at https://ollama.com/settings/api-keys. Update both `/root/.hermes/env.sh` (export line) and `/root/.hermes/.env` (bare assignment). The gateway reads `.env`; CLI sessions source `env.sh`. Both must be updated.

**Cron job amplification:** When an API key dies, every LLM-using cron job (hermes-heartbeat, slack-context-sync, etc.) will hammer the dead key every 5 minutes with 401 errors, flooding `errors.log`. Kill cron jobs FIRST (`cronjob action=remove`), then fix keys, then restart gateway, then recreate cron jobs. In that order. Otherwise the error flood continues while you debug.

## Pitfall 14: Systemd override for OLLAMA_HOST — rogue process conflict

When changing Ollama's bind address via systemd override (e.g., `127.0.0.1:11434` → `0.0.0.0:11434`), a non-systemd-managed ollama process from a previous manual launch may still hold the port. Symptoms:

```
Error: listen tcp 0.0.0.0:11434: bind: address already in use
```

The port shows `LISTEN 127.0.0.1:11434` from a PID not managed by systemd.

**Fix — identify, kill, restart:**

```bash
# 1. Identify the rogue process
ss -tlnp | grep 11434
# → LISTEN 127.0.0.1:11434 users:(("ollama",pid=3495,fd=3))

# 2. Kill it
kill 3495

# 3. Restart the systemd-managed instance
systemctl restart ollama

# 4. Verify — should now show *:11434 (not 127.0.0.1:11434)
ss -tlnp | grep 11434
```

**Systemd override file location**: `/etc/systemd/system/ollama.service.d/override.conf`:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

After writing: `systemctl daemon-reload && systemctl restart ollama`.

**Prevention**: Before changing bind address, check for stray processes: `ps aux | grep ollama | grep -v grep`. Any ollama process NOT under systemd cgroup must be killed before restart.

**⚠️ Model data loss after migration**: A rogue ollama process running as root (HOME=/root) stores models under `/root/.ollama/models/`. The systemd-managed ollama runs as user `ollama` with HOME=/usr/share/ollama — a completely separate model store. Models pulled under the rogue process are LOST when you kill it and switch to systemd. They do NOT migrate. After migration, always verify with `ollama list` — if models are missing, they were pulled into the rogue's HOME and must be re-pulled. Check both storage locations to confirm:

```bash
ls /usr/share/ollama/.ollama/models/blobs/   # systemd ollama store
ls /root/.ollama/models/blobs/ 2>/dev/null   # rogue root ollama store (may not exist)
ollama list                                    # what the live service actually sees
```

## Pitfall 15: Dev server zombies — kill verification is insufficient

Killing a process (Vite dev, Next.js dev, etc.) isn't enough. Verify the port is actually clear AND audit for resurrection vectors:

```bash
# 1. Kill the process
kill <pid>

# 2. VERIFY the port is actually clear
ss -tlnp | grep <port> || echo "CLEAR"

# 3. Audit resurrection vectors — any of these could respawn it:
systemctl list-units --type=service --state=running | grep -iE 'vite|dev|workspace'
pm2 list 2>/dev/null
crontab -l 2>/dev/null | grep -iE 'vite|dev|workspace'
ps aux | grep -iE 'vite|dev.*server' | grep -v grep
```

A process that survives across sessions with no systemd/pm2/cron pinning is a rogue — it was started manually and never cleaned up. The user may have killed it days ago, but a **different instance** (different PID, same port) may have been started separately in another session that was forgotten. Always verify with `ss -tlnp`, not just `ps`. Also check for stale `--host 0.0.0.0` vs intended `--host 127.0.0.1` bindings — a dev server bound to 0.0.0.0 is a security exposure AND likely unintended.

## Pitfall 13: Reasoning models need high max_tokens — empty content is normal at low token counts

Models `nemotron-3-ultra`, `kimi-k2.6`, `glm-4.6`, `minimax-m2`, and `minimax-m2.1` are reasoning models — output goes to the `reasoning` field before `content`. With `max_tokens` below ~50, they may return empty `content` because the model is still "thinking." Hermes handles reasoning fields natively, but manual curl verification must use `max_tokens` ≥ 200.

## Reference Files

- `references/ollama-env-vars.md` — Complete environment variable catalog (server config, GPU, performance, debugging, model preloading)
- `references/ollama-launch-ecosystem.md` — Full `ollama launch` ecosystem: coding agents, IDE integrations, assistants, RAG, automation, notebooks, and security sandboxing
- `references/vps-ram-constraints.md` — Session data: 8B/7B model RAM consumption on CPU-only VPS, safe-model-size formula, when to redirect to local machine
- `references/local-model-benchmarks.md` — Comparison: NeuralDaredevil-8B vs Dolphin3-abliterated, benchmark scores, download stats, verdicts

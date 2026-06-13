# Provider Contamination Patterns

> Generated 2026-05-24 — concrete instances of silent provider drift in Hermes config.

## Pattern 1: Qwen model → Alibaba auto-routing

**Symptom:** `model.default: qwen3-coder-next` with `model.provider: alibaba` and `model.base_url: https://api.deepseek.com` — despite the user having NO Alibaba credentials and wanting Ollama Cloud.

**Root cause:** Quick commands, config edits, or model-switch workflows can change `model.default` + `model.provider` as a pair. The qwen family is associated with Alibaba in Hermes's internal provider mapping, so selecting a qwen model can silently flip the provider to alibaba.

**Detection:**
```bash
hermes config 2>&1 | grep -E "model.*provider|model.*default|model.*base_url"
# Should show: provider='ollama-cloud', default='qwen3-coder-next', base_url='https://ollama.com/v1'
```

**Fix:**
```bash
hermes config set model.provider ollama-cloud
hermes config set model.base_url https://ollama.com/v1
hermes config set model.default qwen3-coder-next
```

Then scrub ALL alibaba references from config files:
```bash
grep -rn -i "alibaba\|qwen.ai" ~/.hermes/config.yaml ~/.hermes/.env ~/.hermes/env.sh
# Remove any matches — sed or patch them out
```

Restart gateway after fix: `systemctl --user restart hermes-gateway`

## Pattern 2: Stale env.sh variables

**Symptom:** `HERMES_QWEN_BASE_URL=https://qwen.ai` in `~/.hermes/env.sh` even after provider was switched to ollama-cloud. This is inert (env.sh is a user convenience loader, not auto-sourced) but misleading.

**Fix:** `sed -i '/HERMES_QWEN_BASE_URL/d' ~/.hermes/env.sh`

## Pattern 3: Commented-out Alibaba references in .env

**Symptom:** `.env` contains commented-out lines like `# HERMES_QWEN_BASE_URL=https://portal.qwen.ai/v1`. Inert but causes false positives when grepping for contamination.

**Fix:** Remove or leave — comments don't affect runtime. Prefer removing if user is sensitive to seeing the name at all.

## Prevention

- Never use `hermes config set model.default` without also explicitly setting `model.provider` in the same session
- After any model switch via `/model` or Slack, verify: `hermes config | grep model`
- The heartbeat skill checks for provider drift at P2 — let it catch this early

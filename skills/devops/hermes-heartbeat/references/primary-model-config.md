# Primary Model Configuration Expectations

## Canonical Configuration

**Expected Primary Model**: `deepseek-v4-pro`  
**Expected Provider**: `deepseek`  
**Expected Base URL**: null (use provider default)

> **Note**: The operator may intentionally change the active model via the workspace UI or CLI
> (e.g., to `qwen/qwen3.7-max/openrouter` or `ollama/glm-5.1/ollama`). These are **operator-driven
> drift** — flag as P2 CONFIG DRIFT (ongoing) but do NOT auto-revert. The canonical value
> represents the **default/baseline** the system should be on unless intentionally changed.

## Configuration Drift Detection

Check `~/.hermes/config.yaml` for:
```yaml
model:
  default: "deepseek-v4-pro"
  provider: "deepseek"
  base_url: null
```

## Silent Drift Scenarios
- Quick commands or skills accidentally rewriting primary to a different model/provider
- Provider key rotation changing default model behavior
- Manual edits via workspace UI that persist across restarts
- Model name format variations: `ollama/glm-5.1` vs `glm-5.1`, `qwen/qwen3.7-max` vs `qwen3.7-max`

## Impact of Drift
- User gets unexpected model behavior without knowing
- Performance characteristics change silently
- Cost profiles may shift unexpectedly
- Quality and capability variations
- Cron jobs may inherit wrong model if they use `model: null` (falls back to default)

## Verification Command
```bash
python3 -c "
import yaml
config = yaml.safe_load(open('/root/.hermes/config.yaml'))
m = config.get('model', {})
print('Model:', m.get('default'))
print('Provider:', m.get('provider'))
print('Base URL:', m.get('base_url'))
"
```

## Status Determination
- **MATCH**: Model=deepseek-v4-pro, Provider=deepseek → OK
- **DRIFT (operator-driven)**: Model changed intentionally via UI/CLI → P2 CONFIG DRIFT (ongoing, note first-flagged date)
- **DRIFT (unintended)**: Model changed without operator action → P2 CONFIG DRIFT, investigate cause
- **NULL**: Missing model/provider configuration → P2 CONFIG

## Model Drift History

| Date | Model | Provider | Classification |
|------|-------|----------|---------------|
| 2026-05-30 06:58 | deepseek-v4-pro | deepseek | Canonical (OK) |
| 2026-05-30 07:05 | qwen/qwen3.7-max | openrouter | P2 DRIFT (first flagged) |
| 2026-06-01 01:05 | ollama/glm-5.1 | ollama | P2 DRIFT (operator-driven) |

- **May 23 2026**: Drift from `deepseek-v4-pro/deepseek` to `qwen3-coder-next/ollama-cloud` (detected and logged)
- **May 24 2026**: Verified `qwen3-coder-next/ollama-cloud` — was briefly canonical
- **May 30 2026**: Canonical established as `deepseek-v4-pro/deepseek` per operator preference
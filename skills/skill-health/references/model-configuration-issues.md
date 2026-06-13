# Model Configuration Issues — Diagnosis and Resolution

## Common Patterns

### HTTP 404: model "..." not found
This error occurs when Hermes attempts to use a model that is not available from the configured provider.

**Typical causes:**
- Model name typo in configuration
- Model deprecated or removed from provider
- Provider-specific model naming conventions not followed
- Attempting to use an Ollama model when provider is set to OpenRouter (or vice versa)

## Diagnosis Steps

### 1. Identify the failing job
From cron job output or logs, note:
- Exact model name that failed (e.g., `ollama/qwen3-coder-next`)
- Provider being used (check job configuration or default provider)
- Time of failure

### 2. Check model availability
**For OpenRouter models:**
```bash
curl -s "https://openrouter.ai/api/v1/models" | jq -r '.data[].id' | grep -i "<model-name>"
```

**For Ollama models:**
```bash
ollama list  # if ollama CLI is available
curl -s http://localhost:11434/api/tags  # direct API call
```

### 3. Verify provider configuration
Check:
- Job-specific provider/model settings in cron job definition
- Global `model.provider` and `model.default` in `~/.hermes/config.yaml`
- Any provider-specific configuration in `custom_providers` section

## Resolution Paths

### If model name is incorrect:
- Correct the spelling/casing in the job's model configuration
- Use exact model identifier from provider's model list

### If model is deprecated:
- Find replacement model from same provider
- Update job configuration with new model identifier
- Consider if newer model version maintains required capabilities

### If provider mismatch:
- Ensure job's provider matches where model is actually hosted
- For Ollama models: provider should be `ollama` (or `ollama-cloud`)
- For OpenRouter models: provider should be `openrouter`
- Check if custom provider configuration is needed

### If model requires special access:
- Verify API keys are configured correctly
- Check if model requires specific subscription tier
- Confirm provider credentials in `~/.hermes/env.sh` or platform secrets

## Prevention

### Configuration best practices:
1. Use variables for model names in job templates when possible
2. Validate model availability during skill/job creation
3. Pin to specific model versions when reproducibility is critical
4. Monitor model deprecation announcements from providers

### Monitoring:
- Skill-health will detect `model "..." not found` errors in logs
- Set up alerts for recurring model configuration failures
- Periodically validate critical job configurations against provider model lists

## Provider-Specific Notes

### Ollama:
- Model names typically follow `organization/model:tag` format
- Local Ollama server must be running and accessible
- Use `ollama pull <model>` to manually verify model availability

### OpenRouter:
- Model names include provider prefix: `provider/model-name`
- Free models may have `:free` suffix
- Model availability can change based on licensing agreements

### Custom Providers:
- Verify `base_url` and `api_key_env` are correctly configured
- Check custom provider implementation supports requested model
- Ensure authentication headers are properly formatted

## Example Fixes

### Correcting Ollama model reference:
```yaml
# Before (incorrect)
model: ollama/qwen3-coder-next
provider: ollama

# After (correct - verify exact name with `ollama list`)
model: qwen3-coder
provider: ollama
```

### Switching to OpenRouter equivalent:
```yaml
# Before (Ollama model not available)
model: ollama/qwen3-coder-next
provider: ollama

# After (OpenRouter equivalent)
model: openrouter/qwen3-coder-next
provider: openrouter
```

### Using free tier model:
```yaml
# Before (paid model)
model: openrouter/qwen3-coder-next
provider: openrouter

# After (free alternative)
model: openrouter/openchat-3.5:free
provider: openrouter
```

## Related References
- `references/primary-model-config.md` — Canonical model configuration expectations
- `references/cron-jobs-json-schema.md` — Understanding job configuration structure
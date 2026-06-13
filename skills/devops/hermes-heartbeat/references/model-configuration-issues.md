# Model Configuration Issues in Cron Jobs

This document details common model configuration problems found in Hermes cron jobs, their diagnosis, and resolution paths.

## Common Model Configuration Errors

### 1. Ring-2.6-1T Model Transitioned to Paid
### 1. Ring-2.6-1T Model Transitioned to Paid
**Error Message**: 
```
RuntimeError: HTTP 404: Ring-2.6-1T is no longer available as a free model. It has transitioned to a paid model. Continue using it here: https://openrouter.ai/inclusionai/ring-2.6-1t
```

**Affected Jobs**:
- slack-context-sync (41919d76eb4d)
- Job Pipeline — Follow-Up Decay Monitor (597ab2bac72e)

**Diagnosis**:
- The Ring-2.6-1T model was previously available as a free model on OpenRouter
- It has since transitioned to a paid-only model
- Jobs referencing this model will fail with HTTP 404

**Resolution**:
1. Update the job's model configuration to use a currently available free model
2. Alternative: If the user has paid access, configure billing for OpenRouter
3. Recommended replacements:
   - For reasoning tasks: `deepseek/deepseek-chat` or `deepseek/deepseek-coder`
   - For general tasks: `anthropic/claude-3-haiku` or `openai/gpt-4o-mini`

**Verification**:
After updating the job configuration, the next run should succeed with `last_status: "ok"`.

### 2. Ollama Model Not Found

**Error Message**:
```
RuntimeError: HTTP 404: model "ollama/qwen3-coder-next" not found
```

**Affected Jobs**:
- skill-health-daily (885f2783d48a)

**Diagnosis**:
- The job references an Ollama model that doesn't exist in the local Ollama library
- Either the model was never pulled, or the name is incorrect
- Ollama models must be pulled locally before use (`ollama pull <model>`)

**Resolution**:
1. Check available Ollama models: `ollama list`
2. If the model doesn't exist, pull it: `ollama pull qwen3-coder-next`
3. Alternatively, update the job to use an available model
4. Verify the model exists in Ollama before referencing it in jobs

**Prevention**:
- Always verify model availability before configuring cron jobs
- For Ollama models, run `ollama pull <model>` as part of job setup
- Consider adding a pre-check script that validates model availability

### 3. General Model Configuration Drift

**Symptoms**:
- Jobs suddenly failing with model-related errors
- User noticing unexpected model behavior or capabilities
- Cost increases from using unintended paid models

**Detection**:
- Check `~/.hermes/config.yaml` for `model.default` and `model.provider`
- Audit all cron jobs for model/provider overrides
- Compare against expected primary model (currently `deepseek-v4-pro` / provider `deepseek`)

**Resolution**:
1. Restore correct model configuration in config.yaml
2. Audit and fix any job-specific model overrides
3. Implement model configuration verification in regular heartbeat checks

## Best Practices for Model Configuration

1. **Use aliases over specific versions**: Prefer `deepseek-chat` over `deepseek-chat-v3-0324` when possible
2. **Document model choices**: Add comments explaining why a specific model was chosen
3. **Verify before deploying**: Test model availability in a interactive session before adding to cron
4. **Monitor for changes**: Regularly check if free models have changed to paid status
5. **Fallback chains**: Consider implementing fallback models in critical jobs

## Related References

- `references/primary-model-config.md` - Canonical model configuration expectations
- `references/cron-jobs-json-schema.md` - Field definitions and health signal mapping
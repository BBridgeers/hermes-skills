# Ring-2.6-1T Model Paywalled Issue

## Problem Description
The Ring-2.6-1T model was previously available as a free model on OpenRouter but has transitioned to a paid model. Jobs configured to use this model now fail with HTTP 404 errors.

## Error Message
```
RuntimeError: HTTP 404: Ring-2.6-1T is no longer available as a free model. It has transitioned to a paid model.
Continue using it here: https://openrouter.ai/inclusionai/ring-2.6-1t
```

## Affected Jobs
- slack-context-sync (id: 41919d76eb4d)
- Job Pipeline — Follow-Up Decay Monitor (id: 597ab2bac72e)

## Root Cause
OpenRouter changed the availability of Ring-2.6-1T from free to paid tier. The model is still accessible but requires payment/configuration.

## Resolution Paths

### Option 1: Update to Free Alternative Model
Replace Ring-2.6-1T with a comparable free model:
- deepseek-v4-pro (current primary model)
- deepseek-chat-v3
- Other free models in OpenRouter catalog

### Option 2: Configure Payment for Ring-2.6-1T
If Ring-2.6-1T is specifically required:
1. Add OpenRouter credits to account
2. Update job configuration to enable paid model usage
3. Verify model accessibility

### Verification Steps
1. Check model availability: `curl -s "https://openrouter.ai/api/v1/models" | grep ring-2.6-1t`
2. Test model inference with small prompt
3. Update cron job configuration in `/root/.hermes/cron/jobs.json` or via skill system
4. Monitor next job run for success

## Prevention
- Regular heartbeat checks should flag model not found/paywall errors
- Subscribe to OpenRouter model announcements
- Maintain model configuration inventory in skills/references/

## Related References
- model-configuration-issues.md
- primary-model-config.md
- known-recurring-patterns.md
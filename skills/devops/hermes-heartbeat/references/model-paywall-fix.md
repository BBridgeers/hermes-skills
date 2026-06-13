# Fixing Ring-2.6-1T Model Paywall Errors

When a cron job fails with `HTTP 404: Ring-2.6-1T is no longer available as a free model`, update the job's model configuration to a free alternative.

## Steps

1. Identify the affected job ID from the heartbeat log or `cronjob(action='list')`.
2. Open the job definition (usually in the prompt or skill configuration).
3. Replace `Ring-2.6-1T` with a free model such as `deepseek-v4-pro` or another available model on OpenRouter.
4. Save the job configuration (via `skill_manage` if it's a skill, or update the cron job via the appropriate method).
5. Optionally, run the job manually to verify it succeeds.

## Example

For the `slack-context-sync` job, update its model configuration in the job definition or in `config.yaml` under `model.default` if it inherits the primary model.

## Prevention

- Regularly check the OpenRouter model list for changes.
- Use the `hermes-model-picker-fix` skill to diagnose model picker issues.
- Subscribe to model deprecation announcements from providers.
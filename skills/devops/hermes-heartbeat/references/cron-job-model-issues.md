# Known Cron Job Model Issues and Fixes

## Issue 1: skill-health-daily fails with "model \"ollama/qwen3-coder-next\" not found"
- **Error**: `RuntimeError: HTTP 404: model "ollama/qwen3-coder-next" not found`
- **Cause**: The skill-health skill (or its configuration) attempts to use the Ollama model `qwen3-coder-next`, which is not available in the Ollama library.
- **Fix**: Update the skill-health skill to use an available model (e.g., `deepseek-v4-pro` via the DeepSeek provider) or adjust the cron job configuration to specify a valid model and provider.
  - For the cron job, ensure the job definition does not override the model/provider incorrectly.
  - Alternatively, modify the skill-health skill to use a fallback model.

## Issue 2: slack-context-sync fails with "Ring-2.6-1T is no longer available as a free model"
- **Error**: `RuntimeError: HTTP 404: Ring-2.6-1T is no longer available as a free model. Continue using it here: https://openrouter.ai/inclusionai/ring-2.6-1t`
- **Cause**: The skill (or its configuration) attempts to use the free model `inclusionai/ring-2.6-1t`, which has transitioned to a paid model.
- **Fix**: Update the skill or cron job to use a different free model (e.g., `deepseek-v4-pro` via DeepSeek) or configure the job to use the paid model with appropriate API credits.
  - Check the skill's model configuration and replace `inclusionai/ring-2.6-1t` with an available free model.
  - If using the paid model, ensure the OpenRouter API key has sufficient credits and the model is correctly specified.

## General Approach
1. Identify the skill or cron job configuration that specifies the problematic model.
2. Update the model to an available alternative (preferably one already configured in `config.yaml` under `model.default` or a custom provider).
3. If the skill is designed to try multiple models, ensure the fallback chain includes only available models.
4. After updating, manually trigger the job to verify the fix.
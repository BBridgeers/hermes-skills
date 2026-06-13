#!/usr/bin/env bash
# Try both common locations for the API key
if [ -f "$HOME/.hermes/env.sh" ]; then
  source "$HOME/.hermes/env.sh"
elif [ -f "/opt/data/env.sh" ]; then
  source "/opt/data/env.sh"
fi
API_KEY="${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY not set}"
MODEL="${1:-deepseek-v4-pro}"
shift || true
      PAYLOAD=$(jq -n --arg model "$MODEL" --arg prompt "$(cat)" '{model: $model, messages: [{role: "user", content: $prompt}]}')
curl -s -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq -r '.choices[0].message.content // empty'
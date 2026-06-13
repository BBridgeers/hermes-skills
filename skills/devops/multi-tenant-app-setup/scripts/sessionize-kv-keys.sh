#!/bin/bash
# sessionize-kv-keys.sh — rename flat KV keys to user-scoped format

# Usage: source ./sessionize-kv-keys.sh && sessionize_kv_keys

# Run from Redis CLI (docker exec honcho-redis-1 redis-cli)
# Or connect locally: redis-cli -h 127.0.0.1 -p 6379

sessionize_kv_keys() {
  # Example migration commands for flat keys -> user-scoped keys:
  # eval "redis-cli keys 'vera_fleet_*'" | while read key; do
  #   redis-cli rename "$key" "user:blake:${key##vera_}"
  # done

  echo "=== MIGRATION PLAN ==="
  echo "# OLD KEY                        -> NEW KEY (blake)"
  echo "# vera_fleet_prod              -> user:blake:vera_fleet_prod"
  echo "# vera_comparison_ids          -> user:blake:vera_comparison_ids"
  echo "# vera_chat_sessions           -> user:blake:vera_chat_sessions"
  echo ""
  echo "# For automation, run this in redis-cli or via docker:"
  echo "# docker exec honcho-redis-1 redis-cli EVAL "
  echo '  "for i,ke in ipairs(redis.call(\"KEYS\",\"vera_*\")) do redis.call(\"RENAME\",ke,\"user:blake:\"..string.gsub(strsub(ke,6),\"_\",\"\")) end" 0'
}

sessionize_kv_keys

# Swarm Agent Blocked Diagnostic Flow

When agents are stuck after a swarm dispatch, run these checks in order.

## Step 1: Find Blocked Agents

```bash
for f in ~/.hermes/profiles/*/runtime.json; do
  w=$(basename $(dirname $f))
  state=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('state','no_file'))" 2>/dev/null)
  if [ "$state" != "idle" ] && [ "$state" != "no_file" ]; then
    reason=$(python3 -c "import json; d=json.load(open('$f')); print(d.get('blockedReason','')[:200])" 2>/dev/null)
    echo "BLOCKED: $w — $reason"
  fi
done
```

## Step 2: Classify the Block

| blockedReason contains | Root Cause | Fix |
|---|---|---|
| `ENOENT` or `spawn` | Binary path wrong or broken venv | Check binary: `ls /root/.hermes/hermes-agent/venv/bin/hermes`. Test: `<path> --version`. If "required file not found", venv symlinks broken. Relink to real install. |
| `model` or `provider` or `not found` | Model ID doesn't exist in provider | Verify model in `config.yaml` exists in the provider's model list. Check `swarm.yaml` model field against actual provider catalog. |
| `timeout` or `timed out` | API timeout | Check provider health, rate limits. Try simpler query. |
| `auth` or `401` or `403` | API key issue | Verify credentials in `~/.hermes/.env`. |

## Step 3: Clear Blocked State

```python
import json
for w in ['agent-id-1', 'agent-id-2']:  # replace with actual IDs
    d = {
        'workerId': w, 'state': 'idle', 'phase': None,
        'currentTask': None, 'currentMissionId': None,
        'currentAssignmentId': None, 'checkpointStatus': None,
        'needsHuman': False, 'blockedReason': None,
        'lastDispatchAt': None, 'lastDispatchMode': None,
        'lastDispatchResult': None, 'lastCheckIn': None,
        'lastSummary': None, 'lastControlMessage': None,
        'nextAction': None
    }
    json.dump(d, open(f'/root/.hermes/profiles/{w}/runtime.json', 'w'), indent=2)
```

## Step 4: Clear Associated State

```bash
# Kill stale log watchers
kill $(ps aux | grep "tail.*agent.log" | grep -v grep | awk '{print $2}') 2>/dev/null

# Clear swarm mission memory
rm -rf /root/hermes-workspace/memory/swarm/*
rm -f /root/hermes-workspace/memory/handoffs/swarm/*-latest.md

# Clear per-worker mission memory
for w in agent-id-1 agent-id-2; do
  rm -rf ~/.hermes/profiles/$w/memory/missions/*
  rm -rf ~/.hermes/profiles/$w/memory/handoffs/*
done
```

## Step 5: Restart and Retry

```bash
systemctl --user restart hermes-workspace
# Refresh Swarm tab in browser before re-dispatching
```

## Why Only 3 Agents Dispatch

If the swarm spun up only 3 agents for a complex mission:
1. The orchestrator's decomposition may be limited or routing to wrong agents
2. Agents may have been the first N matching a coarse role filter
3. For mission-critical dispatches, embed explicit agent assignment in the prompt

# Swarm Clearing Procedure

## When to Use

Agents stuck in "blocked" state from old/stale missions. Symptoms:
- `runtime.json` shows `"state": "blocked"` or `"dispatched"` with a stale `lastCheckIn`
- `tail -F` processes watching agent logs from old sessions
- Swarm tab shows persistent active missions that won't resolve

## Protocol

### 1. Kill Log Watchers

```bash
kill $(ps aux | grep "tail -n 200 -F" | grep -E "builder|maintainer|ops-watch" | awk '{print $2}')
```

Check with: `ps aux | grep "tail.*agent.log" | grep -v grep`

### 2. Reset runtime.json

For each stuck agent, overwrite with idle state:

```json
{
  "workerId": "<agent-id>",
  "state": "idle",
  "phase": null,
  "currentTask": null,
  "currentMissionId": null,
  "currentAssignmentId": null,
  "checkpointStatus": null,
  "needsHuman": false,
  "blockedReason": null,
  "lastDispatchAt": null,
  "lastDispatchMode": null,
  "lastDispatchResult": null,
  "lastCheckIn": null,
  "lastSummary": null,
  "lastControlMessage": null,
  "nextAction": null
}
```

Path: `~/.hermes/profiles/<agent-id>/runtime.json`

### 3. Clear Workspace Swarm Mission Memory

```bash
rm -rf /root/hermes-workspace/memory/swarm/<mission-id>*
rm -f /root/hermes-workspace/memory/handoffs/swarm/<agent-id>-latest.md
rm -f /root/hermes-workspace/memory/swarm/PROJECT.md
```

### 4. Clear Per-Worker Mission Memory

```bash
rm -rf ~/.hermes/profiles/<agent-id>/memory/missions/*
rm -rf ~/.hermes/profiles/<agent-id>/memory/handoffs/*
rm -f ~/.hermes/profiles/<agent-id>/memory/IDENTITY.md
```

### 5. Verify

```bash
# All runtime.json should be "idle"
for f in ~/.hermes/profiles/*/runtime.json; do
  w=$(basename $(dirname $f))
  state=$(python3 -c "import json; print(json.load(open('$f')).get('state','no file'))")
  [ "$state" != "idle" ] && echo "⚠️  $w: $state"
done

# No tail watchers remaining
ps aux | grep "tail.*agent.log" | grep -v grep | wc -l
# Expected: 0
```

## Bulk Clear (Python)

```python
import json, os, glob

STUCK = ["builder", "maintainer", "ops-watch"]

# Kill tail watchers
import subprocess
for w in STUCK:
    subprocess.run(f"pkill -f 'tail.*{w}/logs/agent.log'", shell=True)

# Reset runtime.json
idle = {"state": "idle", "phase": None, "currentTask": None, "currentMissionId": None}
for w in STUCK:
    path = os.path.expanduser(f"~/.hermes/profiles/{w}/runtime.json")
    with open(path, "w") as f:
        json.dump({**idle, "workerId": w}, f, indent=2)

# Clear memory
for w in STUCK:
    for d in ["memory/missions", "memory/handoffs"]:
        path = os.path.expanduser(f"~/.hermes/profiles/{w}/{d}")
        if os.path.isdir(path):
            for f in glob.glob(f"{path}/*"):
                os.remove(f)
```

## Post-Clear

Refresh the Workspace Swarm tab (`:3100/swarm`). All agents should show idle. If the workspace caches state, restart: `systemctl --user restart hermes-workspace`.

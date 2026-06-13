# Swarm Dispatch Diagnostics — Full Flow

## Why the swarm only dispatches 2-3 agents

The swarm dispatch system has MULTIPLE independent limiting factors. All must be checked when the swarm dispatches too few agents.

### Check 1: Backend hard cap
`/root/hermes-workspace/src/routes/api/swarm-dispatch.ts` line ~1076:
```typescript
if (assignments.length > 12) {
    throw new SwarmDispatchError('Maximum 12 workers per dispatch')
}
```
Raise this to match the full roster size (78 for the 60-agent workforce). Requires workspace rebuild.

### Check 2: Central agent decomposition quality
The workspace Router Chat sends the prompt to the CENTRAL CHAT AGENT (not the swarm-orchestrator profile). The central agent reads `~/.hermes/config.yaml`. If the central agent's system_prompt doesn't have:
- A broad-decomposition directive ("decompose aggressively, complex missions deserve many workers")
- The full agent roster (names, specialties, skills)
...it will conservatively decompose into 2-3 generic tasks.

**Fix**: inject the full roster + decomposition directive into `~/.hermes/config.yaml`'s `agent.system_prompt`. Restart gateway + rebuild workspace.

### Check 3: Model availability
Agents dispatch but immediately block if their assigned model is unreachable:
- OpenRouter `:free` models hit 200 req/day rate limits → 400 errors
- Ollama Cloud models sometimes return 404 ("No endpoints available")
- Check block reason in `~/.hermes/profiles/<id>/runtime.json` → `blockedReason` field

### Check 4: Broken venv symlinks
`ENOENT` errors on spawn mean the hermes binary can't execute. The Docker decontainerization left broken venv symlinks at `~/.hermes/hermes-agent/venv/bin/`. See pitfall 22 in parent skill.

### Check 5: Legacy agents in swarm.yaml
If old agent profiles still exist on disk but aren't in swarm.yaml, they can still be dispatched by cached state. See pitfall 27 in parent skill.

## Full diagnostic procedure

1. Check runtime states: `python3 -c "import json,os; [print(f'{p}: {json.load(open(os.path.join(os.path.expanduser(\"~/.hermes/profiles\"),p,\"runtime.json\"))).get(\"state\")}') for p in os.listdir(os.path.expanduser(\"~/.hermes/profiles\")) if os.path.exists(os.path.join(os.path.expanduser(\"~/.hermes/profiles\"),p,\"runtime.json\"))]"`
2. Check blocked reasons: `python3 -c "import json,os; [print(f'{p}: {json.load(open(os.path.join(os.path.expanduser(\"~/.hermes/profiles\"),p,\"runtime.json\"))).get(\"blockedReason\",\"\")[:100]}') for p in os.listdir(os.path.expanduser(\"~/.hermes/profiles\")) if os.path.exists(os.path.join(os.path.expanduser(\"~/.hermes/profiles\"),p,\"runtime.json\")) and json.load(open(os.path.join(os.path.expanduser(\"~/.hermes/profiles\"),p,\"runtime.json\"))).get(\"state\") not in (\"idle\",None)]"`
3. Check PTY watchers: `ps aux | grep pty-helper | grep -v grep`
4. Check session files: `ls ~/.hermes/profiles/<id>/sessions/`
5. Verify central agent roster: check `~/.hermes/config.yaml` for agent list in system_prompt

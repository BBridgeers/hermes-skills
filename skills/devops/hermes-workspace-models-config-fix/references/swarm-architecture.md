# Hermes Workspace Swarm — Data Architecture

## Source of Truth: `swarm.yaml`

**Location:** `$CWD/swarm.yaml` (resolves to `/root/hermes-workspace/swarm.yaml` on native VPS)

The workspace's `/api/swarm-roster` endpoint reads and writes this single YAML file.
Every agent in the Swarm tab is defined here. Mass-creation is done by editing this
file directly — no UI clicking needed.

### Schema (from `src/server/swarm-roster.ts`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | e.g. "swarm13" or semantic "builder" |
| `name` | string | - | Display name |
| `role` | string | - | Maps to frontend ROLE_PRESETS |
| `specialty` | string | - | Short focus area |
| `model` | string | - | Model ID (from models.json) |
| `mission` | string | - | Standing mission |
| `profile` | string | - | Dir under `~/.hermes/profiles/<id>/` |
| `modes` | string[] | - | Launch modes (e.g. ["task"]) |
| `tools` | string[] | - | Enabled tools |
| `skills` | string[] | - | Skills loaded at startup |
| `plugins` | string[] | - | Plugin names |
| `pluginToolsets` | string[] | - | Plugin toolset names |
| `mcpServers` | string[] | - | MCP server names |
| `wrapper` | string | - | Wrapper in `~/.local/bin/` |
| `capabilities` | string[] | - | Capability tags |
| `defaultCwd` | string | - | Default working directory |
| `preferredTaskTypes` | string[] | - | Task type tags |
| `greenlightRequiredFor` | string[] | - | Actions requiring approval |
| `maxConcurrentTasks` | int | - | Default 1 |
| `acceptsBroadcast` | bool | - | Default true |
| `reviewRequired` | bool | - | Default false |

### System Prompt Gap

The "System prompt (embedded with role)" field in the Add Swarm UI is **NOT
persisted to swarm.yaml**. Here's the trace:

1. Frontend sends `systemPrompt` in POST body (swarm2-screen.tsx line 1459)
2. Backend Zod schema (`SwarmRosterWorkerSchema`) has **no `systemPrompt` field**
3. Zod's `.parse()` silently strips it out
4. The UI shows it as "embedded with role" — meaning it comes from the
   **hardcoded `ROLE_PRESETS` array** in `swarm2-screen.tsx` (lines 242-330),
   not from swarm.yaml

**To give agents custom system prompts:**
- **Option A (skill-based):** Create a `<worker-id>-core` skill with the system
  prompt content and reference it in the agent's `skills` array. This is what
  the existing semantic workers do (e.g., `builder-core`, `reviewer-core`).
- **Option B (patch backend):** Add `systemPrompt` to `SwarmRosterWorkerSchema`
  in `src/server/swarm-roster.ts` and rebuild the workspace.

### Related Files

| What | Where |
|------|-------|
| Agent definitions | `/root/hermes-workspace/swarm.yaml` |
| Model catalog | `/root/.hermes/models.json` |
| Worker profiles | `~/.hermes/profiles/<worker-id>/` |
| Wrappers | `~/.local/bin/<wrapper-name>` |
| Role presets | `src/screens/swarm2/swarm2-screen.tsx` line 242 |
| Runtime state | `~/.hermes/profiles/<id>/runtime.json` |
| Missions/routing | `/root/hermes-workspace/.runtime/swarm-missions.json` |

### Mass-Creating Agents

Edit `swarm.yaml` directly — it's plain YAML:

```yaml
version: 1
workers:
- id: swarm13
  name: Swarm13
  role: Builder
  model: deepseek-v4-pro
  mission: "Standing mission here"
  skills: [swarm-worker-core]
  tools: [terminal, file, web]
```

Or loop via script:

```bash
for i in $(seq 13 53); do
  cat <<EOF >> /root/hermes-workspace/swarm.yaml
- id: swarm${i}
  name: Swarm${i}
  role: Builder
  model: deepseek-v4-pro
  mission: "Agent ${i} standing mission"
  skills: [swarm-worker-core]
EOF
done
```

### List of Role Presets

Hardcoded in `swarm2-screen.tsx`:
Orchestrator, Builder, Reviewer, Triage, Lab, Sage, Scribe, Foundation, QA,
Mirror Integrations, Custom

# session_search Browse-Mode Blind Spots

## The failure pattern

`session_search()` with no arguments (browse mode) can return a tiny fraction of
actual active sessions — sometimes NONE of the non-cron sessions. This causes
heartbeats to return [SILENT] when there's substantial activity.

## Concrete example — May 21, 2026 (22:54 UTC heartbeat)

**Browse mode returned:** 3 sessions (all cron)
- `cron_cfc9f7fe605a_20260521_225438` (this sync heartbeat)
- `cron_cfc9f7fe605a_20260521_224452` (hermes-heartbeat)
- `cron_cfc9f7fe605a_20260521_223457` (hermes-heartbeat)

**`find -mmin -60` found:** 20 sessions total, including 10 non-cron sessions:

| Session | Msgs | Content |
|---|---|---|
| `20260521_223550_d9f1a6` | 315 | DETOXXX V2 — skill patching (detoxxx-writing, protocol-handbook-authoring) |
| `20260521_222422_e6cc27` | 301 | DETOXXX V2 — quality audit, model selection guidance |
| `20260521_220625_6555b0` | 264 | DETOXXX V2 — quality marker scan, merged file dead-link |
| `20260521_223821_6231d3` | 50 | Hermes workspace swarm model discovery |
| `20260521_221219_49060d` | 51 | slack-context-sync (prior heartbeat) |
| `20260521_223135_ea57a1` | 44 | Hermes workspace swarm config |
| `20260521_223636_1e78f8` | 16 | DETOXXX V2 Section 5.1 audit |
| `20260521_222414_6d7cf5` | 15 | (swarm-related) |
| `20260521_222413_77f5f0` | 21 | (swarm-related) |
| `20260521_222411_4a5417` | 22 | (swarm-related) |

**Miss rate:** browse mode captured 0 of 10 non-cron sessions. Every single one
of these had `last_active` within 30 minutes of the heartbeat.

## Why this is catastrophic for heartbeats

The [SILENT] rule says: "Session search returns only routine cron sessions" →
suppress delivery. Browse mode makes this rule fire when the opposite is true:
there's massive non-cron activity.

## The reliable alternative

```bash
# Step 1: Find recent session files (NOT via session_search)
find /root/.hermes/sessions -name "session_*.json" -mmin -60 -type f

# Step 2: Extract message counts
for f in <files>; do
  python3 -c "import json; d=json.load(open('$f')); msgs=d.get('messages',[]); print(f'$f: {len(msgs)} msgs')"
done

# Step 3: For sessions with >10 msgs, extract content
python3 -c "
import json
d = json.load(open('<session_path>'))
msgs = d.get('messages', [])
user_msgs = [m for m in msgs if m.get('role') == 'user']
for m in user_msgs[:3]:
    print(str(m.get('content', ''))[:200])
"
```

## `session_search(session_id=...)` also unreliable

When you have a session ID from `find` and try `session_search(session_id="20260521_223550_d9f1a6")`,
it returns `"session_id not found"` even though the file exists on disk. Both
browse and ID-lookup modes have gaps. Treat `session_search` as a convenience
for initial discovery, not a source of truth.

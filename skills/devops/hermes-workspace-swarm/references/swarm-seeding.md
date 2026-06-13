# Swarm Agent Initialization — State.DB Seeding

## Problem

After deploying a fresh swarm workforce (e.g., the 60-agent AV1 workforce), the swarm tab at `:3100/swarm` shows only a handful of agents as "live" or "available." The rest appear as "unknown" or are missing entirely.

Root cause: `/api/crew-status` reads `state.db` from each profile directory. Profiles without a `state.db` file (or with zero sessions) show `sessionCount: 0, lastSessionAt: null` — and the swarm UI treats them as inactive.

## Fix

Seed a starter `state.db` with one init session for every profile that lacks one.

```python
import sqlite3, os, time

profiles_dir = os.path.expanduser("~/.hermes/profiles")
now = time.time()

for profile in os.listdir(profiles_dir):
    state_db = os.path.join(profiles_dir, profile, "state.db")
    
    # Skip if already has sessions
    if os.path.exists(state_db):
        try:
            conn = sqlite3.connect(state_db)
            count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            conn.close()
            if count > 0:
                continue
        except:
            pass
    
    conn = sqlite3.connect(state_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            source TEXT,
            user_id TEXT,
            model TEXT,
            started_at REAL,
            ended_at REAL,
            message_count INTEGER DEFAULT 0,
            title TEXT
        )
    """)
    
    session_id = f"init_{profile}_{int(now)}"
    conn.execute(
        "INSERT INTO sessions (id, source, model, started_at, message_count, title) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, "swarm-init", "deepseek-v4-pro", now, 1, f"{profile} initialized")
    )
    conn.commit()
    conn.close()

print("Done — restart workspace after seeding")
```

## Verification

```bash
# Count profiles with session data
for d in ~/.hermes/profiles/*/; do
  name=$(basename "$d")
  count=$(python3 -c "import sqlite3; conn=sqlite3.connect('$d/state.db'); print(conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0])" 2>/dev/null || echo 0)
  echo "$name: $count sessions"
done
```

## Related

- Pitfall 28 in `hermes-workspace-swarm` skill — full context
- Pitfall 24 — session file persistence (separate issue from state.db)
- Pitfall 21 — swarm dispatch decomposition failures

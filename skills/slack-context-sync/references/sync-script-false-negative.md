# Sync Script False Negative — Production Example

**Date**: 2026-05-21  
**Heartbeat session**: `cron_41919d76eb4d_20260521_184711`

## Scenario

The sync script (`scripts/sync-context.sh`) returned empty (exit code 0) at 18:47 UTC, indicating "no new activity." But the context file was **9 hours stale** (last written 09:38 UTC) and there were **5+ non-cron sessions** from 18:27–18:45 UTC with 146, 163, 116, 55, 27 messages each — all DETOXXX V2 handbook swarm writing.

## Root cause

Three heartbeats ran between 09:38 and 18:47. Each found the context file "recent enough" from the prior heartbeat and returned [SILENT]. Meanwhile, the user ran a 146-msg Slack session starting at ~07:52 that spanned hours, spawning bulk subagent sessions at 18:09, 18:27, 18:37, 18:40, and 18:42 — none of which were captured by any heartbeat.

The sync script's staleness logic: if the file is < some threshold old, it assumes nothing changed and returns empty. But when a session is long-running (07:52–18:40+) or when new sessions start between heartbeat ticks, the file can be "fresh" while missing all substantive activity.

## Detection pattern

When the sync script returns empty:
1. **Always check the context file timestamp.** If >2 hours stale, don't trust the script.
2. **Run `find` on session files** to find non-cron sessions within the gap:

```bash
find /root/.hermes/sessions/ -maxdepth 1 \
  -name "session_$(date +%Y%m%d)_*.json" ! -name "*cron_*" \
  -mmin -180 -printf '%T@ %p\n' | sort -rn | head -10
```

3. **Read the top candidates directly** with `python3 -c` (bypasses `read_file` dedup):

```python
python3 -c "
import json, os, glob
sessions = sorted(
    glob.glob('/root/.hermes/sessions/session_20260521_*.json'),
    key=os.path.getmtime, reverse=True
)[:10]
for s in sessions:
    if 'cron_' in os.path.basename(s):
        continue
    with open(s) as f:
        data = json.load(f)
    msgs = data.get('messages', [])
    user_msgs = [m for m in msgs if m.get('role') == 'user']
    first_3 = [str(m.get('content',''))[:120] for m in user_msgs[:3]]
    print(f'{os.path.basename(s)}: {len(msgs)} msgs, src={data.get(\"source\",\"?\")}')
    for um in first_3:
        print(f'  → {um}')
    print()
"
```

4. **Compare against the context file.** If the session topics differ from what's in the file, the sync script was a false negative — proceed with a full context write.

## Production Example 2 — Tighter Window (May 22, 2026)

**Date**: 2026-05-22 22:29 UTC  
**Heartbeat session**: `cron_cfc9f7fe605a_20260522_2223xx`

The sync script returned empty (exit 0) with a context file only **10 minutes old** (written 22:15 UTC). The staleness logic considered this "fresh." But `find` revealed **7 non-cron sessions** started after 22:15:

| Session | Msgs | Content |
|---|---|---|
| `222041_09c548` | 69 | DETOXXX V2 Section 4 audit — GLM-5.1 launched in background |
| `222418_8c7b02` | 44 | Ubuntu terminal crash followup — hardening completed via Slack |
| `222337_d3e26b` | 42 | Context sync pass + skill library update |
| `221205_bba7ad` | 367 | Gateway health → IP blocking, swarm construction, skills import |
| `220630_593cff` | 340 | Gateway health → part-time job search |
| `220433_f9369f` | 25 | Context sync pass |
| `215633_4967cd` | 322 | Gateway health → UI/UX skill import |

**Total: 1,209 messages across 7 sessions — all missed by a 10-minute "fresh" file.**

Key difference from Example 1: the window was MINUTES, not hours. A burst of high-velocity Slack activity (gateway health megathread + DETOXXX audit) landed entirely between two heartbeat ticks. The script had no way to know.

## Production Example 3 — Tighter Still (May 22, 2026, 22:45 UTC)

**Date**: 2026-05-22 22:45 UTC
**Heartbeat session**: `cron_cfc9f7fe605a_20260522_2238xx`

The sync script returned empty (exit 0) with a context file only **7 minutes old** (written 22:38 UTC). The staleness logic considered this "fresh." But `find` revealed **2 non-cron sessions** modified after 22:38:

| Session | Msgs | User Turns | Content |
|---|---|---|---|
| `222041_09c548` | 137 | ~20 | DETOXXX V2 Section 4 GLM-5.1 audit (already captured in context) |
| `011859_608358bf` | 366 | 28 | Gateway health → swarm construction (60 agents, 350+ skills), VPS Fort Knox hardening (6 IPs blocked), job search results (11 matches), Fort Knox local prompt, OBLITERATUS recovery — **14+ hour session**, started at 01:18 UTC, still active at 22:45 UTC |

**Total: 503 messages — 366 of them from a session that had evolved completely past what the context file captured.**

Key difference from Example 2: The staleness bound tightened again. A 7-minute-old file was stale. The long-running session (`011859_608358bf`, 14+ hours, 28 user turns) crossed multiple heartbeat boundaries and its content evolved into entirely different work (from "gateway health" at 01:18 to swarm construction, Fort Knox, job search, and OBLITERATUS by 22:45). This matches the **extreme-duration session** pattern documented in the main skill — `last_active - started_at > 2 hours` with `message_count > 100` is a mandatory deep-investigation target.

## When this happens

- Long-running sessions that span multiple heartbeat ticks (the first tick sees it as too-new-to-summarize, the second sees context as "fresh enough")
- Sessions that start immediately after a heartbeat's context write (T+1 minute)
- **High-velocity Slack bursts**: multiple sessions start and complete entirely between two 5-min heartbeat ticks with the context file looking "fresh" the whole time (May 22 example)
- Heavy swarm/bulk subagent work where child sessions appear and complete between ticks
- The user works on the same "project" across hours but individual heartbeats only see 5-minute windows
- **ANY time the sync script returns empty, regardless of context file age** — a 7-minute-old file can already be stale

## Mitigation

- **MANDATORY: After EVERY sync-context.sh run that returns empty**, run `find` on session files comparing against the context file's timestamp. The May 22 examples prove a 7-minute-old file can be stale. Do not skip this because "the file looks fresh."
- **Don't treat sync-script emptiness as authoritative** — even when the context file is only minutes old
- **Always run `find` on session files** as a backstop, even when script says "no activity"
- **Prioritize non-cron sessions** by filtering out `cron_` prefixed files
- **Read the first 3 user messages** of each candidate session — that reveals the actual project, even when `session_search` labels are misleading

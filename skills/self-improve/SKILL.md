---
name: self-improve
description: Improve Hermes itself — better skills, prompts, config, and SOUL based on recent logs and performance
tags: [meta]
---

# Self-Improve — Autonomous Agent Refinement

> Adapted from Aeon's self-improve skill. Replaces git/PR workflow with targeted patches and ~/.hermes/logs/ tracking. One fix per run, highest-impact lowest-effort.

## Purpose

Periodically scan Hermes' own operational logs, error patterns, and skill performance for low-hanging improvements. Apply minimal, targeted fixes via the `patch` tool. Log every change. Notify the operator only when something is fixed.

## Steps

### 1. Preflight — check for improvement backlog

Search `~/.hermes/logs/` for recent self-improve entries. If there are 3+ self-improve log lines from the last 2 days, the improvement pipeline is backed up — log `self-improve: 3+ unreviewed entries in logs, waiting for review` and exit.

```bash
grep -c "self-improve:" ~/.hermes/logs/self-improve.log 2>/dev/null || echo 0
```

Also count entries in `~/.hermes/logs/agent.log` from the last 2 days:
```bash
grep "self-improve:" ~/.hermes/logs/agent.log 2>/dev/null | tail -20
```

If 3+ entries across both, bail. Don't pile up unreviewed changes.

### 2. Identify what to improve

Read the last 2 days of `~/.hermes/logs/agent.log` and `~/.hermes/logs/errors.log` for:
- Skills that failed or produced low-quality/outputless runs
- Errors, timeouts, rate limiting, zero-output
- Notifications that didn't send or were truncated
- Memory or state consolidation problems
- Config drift or missing dependencies

Read `~/.hermes/memories/MEMORY.md` for context on known issues.

Check `~/.hermes/state/` for any skill-health or success-rate tracking data.

Check `~/.hermes/logs/skill-health/issues/INDEX.md` for open issues — these are pre-triaged problems with known severity and affected skills. An open CRITICAL or HIGH issue is often the highest-impact target.

**Pitfall — re-fired security fixes:** When a security-block issue (e.g., `exfil_curl_auth_header`) is "resolved" but re-fires days later under a new ISS, the original fix was incomplete — it patched the primary code path but missed a fallback section. Scan the ENTIRE skill for all instances of the threat pattern, not just the previously-patched section. See `references/incomplete-security-fixes.md`.

Also scan for **config drift** specifically:
- Deprecated model variants in `~/.hermes/config.yaml` (e.g., `:free` suffixes on models whose free tier was removed from OpenRouter). These cause silent fallback failures.
- Provider entries pointing to endpoints that no longer serve the listed model.
- Use `curl -s https://openrouter.ai/api/v1/models` (via Python, not piped curl) to verify model IDs still exist.

Pick the **highest-impact, smallest-effort** fix. Exactly one change per run.

### 3. Understand the area before changing

Read the relevant files thoroughly:
- Skills: `~/.hermes/skills/{name}/SKILL.md`
- Config: `~/.hermes/config.yaml`
- Identity: `~/.hermes/SOUL.md`
- Memory: `~/.hermes/memories/MEMORY.md`

Understand current behavior completely before touching anything.

### 4. Implement the fix

Use the `patch` tool for minimal, targeted edits. Guidelines:

| Problem | Fix |
|---------|-----|
| Skill prompt unclear | Rewrite the ambiguous section — keep diff under 30 lines |
| Hitting rate limits | Add backoff guidance or reduce request frequency in the skill |
| Output quality low | Tighten the prompt, add examples, clarify expected format |
| Notification broken | Fix formatting, truncation, or channel reference |
| Config wrong | Targeted edit to `~/.hermes/config.yaml` |
| Missing tool/dependency | Add install instruction to the skill's requirements section |

Do NOT:
- Rewrite entire skills from scratch
- Add new features (that's a different workflow)
- Change the core architecture
- Modify secrets or environment variables
- Touch `.github/workflows/`
- Improve the self-improve skill itself (no circular improvements)

### 5. Log the change

Append to `~/.hermes/logs/self-improve.log`:
```
self-improve: YYYY-MM-DD HH:MM
  Target: [skill name or file path]
  Problem: [what was failing — one line]
  Fix: [what was changed — one line]
  File: [path to edited file]
```

Also ensure the log directory exists:
```bash
mkdir -p ~/.hermes/logs
touch ~/.hermes/logs/self-improve.log
```

### 6. Notify

Send a single message via `send_message` to Slack:
```
self-improve: [skill name or file] — [one-line description of what was fixed]
```

If `send_message` is unavailable, log `SELF_IMPROVE_NOTIFY_FAILED` and continue — the log file is the authoritative record.

### 7. Guardrails

- If nothing needs improvement: log `self-improve: everything looks healthy` and exit. No notification needed.
- Never modify the same skill more than once in a 24h period (check `~/.hermes/state/self-improve-history.json`).
- If the fix category is unclear, append diagnostic notes to the log and exit without editing.
- Always prefer a one-line prompt tweak over a multi-paragraph rewrite.

## Verification

Manual trigger: "Run the self-improve skill"
Expected: scans `~/.hermes/logs/`, identifies (or doesn't) an improvement target, applies a minimal patch if warranted, logs to `~/.hermes/logs/self-improve.log`, and notifies via Slack if a fix was made.

## Constraints

- ONE fix per run. Never bundle unrelated changes.
- Smallest viable fix. A one-line tweak beats a full rewrite.
- Read before writing. Always load and understand the target file.
- Log every run — even healthy ones. The log IS the improvement history.
- Never create circular improvements. Don't fix self-improve with self-improve.
- If `send_message` fails, the log is still valid — don't retry the whole run.

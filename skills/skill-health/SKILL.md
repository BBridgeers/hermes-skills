---
name: skill-health
description: Audit skill quality metrics, detect degradation, file/resolve issues, and notify on state change via Slack. Runs as a cron job on the VPS — no GitHub Actions dependency.
tags: [meta, devops, monitoring]
---

# Skill Health — Hermes Skill Quality Monitor

> Adapted from Aeon's skill-health architecture. Core methodology, quality gates, and scoring logic preserved. Adapted for VPS-based Hermes: replaces GitHub Actions runs with cron job logs, gh CLI with terminal log parsing, and `./notify` with Slack `send_message`.

## Purpose

Audit skill quality metrics, detect API degradation, **file issues for new failures and resolve them when skills recover**, and notify only when fleet health state actually changes.

## Data sources

1. **`~/.hermes/memory/skill-health/cron-state.json`** — Per-skill quality metrics maintained across runs. Created if missing.
2. **`~/.hermes/memory/skill-health/last-report.json`** — Last run's classification snapshot (this skill writes it). Used to dedup notifications and detect flapping.
3. **Hermes cron system** — Run `hermes cron list` to enumerate scheduled skills.
4. **`~/.hermes/skills/`** — All installed skill directories. Scan for SKILL.md files.
5. **`/root/.hermes/logs/agent.log`** and **`/root/.hermes/logs/errors.log`** — Agent-level log files for failure signatures.
6. **`~/.hermes/logs/skill-health/issues/`** — Open issues tracker (INDEX.md + ISS-NNN.md files). Check before filing, update on recovery.
7. **Session logs** — `~/.hermes/sessions/` directory. Grep recent sessions for `SKILL_*_ERROR` or `EMPTY` signatures keyed to skills.
8. **`~/.hermes/skills/skill-health/references/model-configuration-issues.md`** — Guidance on diagnosing and resolving "model not found" errors in cron jobs and skills.
9. **`~/.hermes/skills/skill-health/references/provider-credit-exhaustion.md`** — Provider-agnostic guide to detecting and classifying HTTP 402 credit exhaustion from any provider (OpenRouter, DeepSeek, etc.), with provider-specific signatures and detection commands.

## Steps

### 1. Gather state

- List all scheduled cron jobs: `terminal("hermes cron list")`. Parse skill names from job names.
- Scan `~/.hermes/skills/` for all installed skill directories → list of installed skills.
- Load `~/.hermes/memory/skill-health/cron-state.json`. If missing or unparseable, treat as empty (first run).
- Load `~/.hermes/memory/skill-health/last-report.json` if present → `prev_report`. If missing, `prev_report = {}`.
Use terminal grep commands: `grep -c 'Error code: 429' /root/.hermes/logs/agent.log`, `grep -c 'Error code: 402' /root/.hermes/logs/agent.log`. For systemic 402/429 detection, also grep unique session prefixes: `grep -oP '\\[cron_\\K[^_]+' /root/.hermes/logs/agent.log | sort -u | wc -l`.
- Parse `/root/.hermes/logs/errors.log` for failure signatures that live there — security blocks (`grep -c 'Blocked.*threat pattern' /root/.hermes/logs/errors.log`), HTTP 402 credit exhaustion, and provider-level errors. Always use terminal `grep`, not `search_files`.
- Search recent session files in `~/.hermes/sessions/` (last 7 days) for `SKILL_*_ERROR` or `EMPTY` patterns. Use `terminal("grep -l ...")` rather than `search_files` — session files are JSON and `search_files` regex rarely matches the embedded error strings.
- Parse `~/.hermes/logs/skill-health/issues/INDEX.md` if it exists → extract open issues with `detected_by: skill-health`. If missing, treat as empty.

### 2. Classify each enabled skill

For each skill, assign one status using the **first matching rule**:

| Status | Trigger |
|---|---|
| **CRITICAL** | `consecutive_failures >= 3` OR (status==failed AND days_since_last_success >= 3) |
| **DEGRADED** | `success_rate < 0.6` OR (latest quality analysis avg_score < 2.5 over ≥3 runs) |
| **FLAPPING** | 3+ status transitions (success↔failed) in last 7 days per cron-state history or log evidence |
| **WARNING** | `success_rate < 0.8` OR `consecutive_failures >= 1` |
| **HEALTHY** | `success_rate >= 0.8` AND `consecutive_failures == 0` AND (no quality data OR avg_score >= 3) |
| **NO DATA** | no entry in cron-state AND never seen in logs |

Compute **severity score** for sorting: `consecutive_failures × (1 + days_since_last_success/7)`. Ties broken by days_since_last_success desc.

For each CRITICAL/DEGRADED/FLAPPING skill, record:
- `last_error` (from cron-state or nearest log signature)
- `api_host` if the error clearly names one (e.g. `api.coingecko.com`, `api.github.com`)
- `suggested_action` — one of: `FIX CONFIG` (missing secret, bad arg), `WAIT-API` (rate limit, 5xx, timeout on third-party host), `INVESTIGATE` (unrecognised error), `DISPATCH-SKILL` (NO DATA but scheduled — cron gap)

### 3. Detect systemic patterns

Group non-HEALTHY skills by shared `api_host` OR shared `last_error` signature. If ≥2 skills share one:
- Emit a single `SYSTEMIC:` callout (e.g. `SYSTEMIC: 3 skills failing on api.coingecko.com (rate_limit)`).
- Do **not** duplicate the same error across per-skill rows — reference the systemic line.

**Special systemic: Provider credit exhaustion (any provider).** If `errors.log` shows `HTTP 402: Insufficient Balance` from ANY provider (OpenRouter, DeepSeek, etc.) affecting ≥2 cron session prefixes, this is a fleet-wide issue. Unlike OpenRouter 402 (where jobs silently fall back to secondary provider), native provider 402 (e.g. DeepSeek at `api.deepseek.com`) causes hard failures with no fallback. Detect with: `terminal("grep -c 'HTTP 402: Insufficient Balance' /root/.hermes/logs/errors.log")` and `terminal("grep -oP 'cron_\\w+' /root/.hermes/logs/errors.log | sort -u | wc -l")`. Classify as SYSTEMIC with `category: rate-limit` and `suggested_action: WAIT-API` (account top-up needed). Create a single ISS covering all affected skills. See `references/provider-credit-exhaustion.md` for provider-specific detection commands.

**Special systemic: Ollama Cloud weekly usage limit.** If agent.log shows `Error code: 429.*weekly usage limit` from `ollama.com` affecting ≥2 cron session prefixes, this is a fleet-wide outage — ALL skills using `ollama-cloud/glm-5.1` as either primary or fallback provider are blocked. Unlike OpenRouter 402, Ollama 429 causes hard failures (no fallback below the fallback). Detect with `terminal("grep -c 'weekly usage limit' /root/.hermes/logs/agent.log")`. File a single SYSTEMIC issue covering all affected skills. If OpenRouter 402 is also active simultaneously, note the compounding effect: daily jobs have zero viable providers and are in a hard-block state.

### 4. Reconcile with issues

**Precondition guard:** only perform issue filing/resolution if `~/.hermes/logs/skill-health/issues/INDEX.md` already exists. If it is missing, the operator has not opted into the issue-tracker contract yet — log `SKILL_HEALTH_ISSUE_TRACKER_MISSING` to the daily log, skip this entire step (and the reconciliation side of step 5), and continue with classification + notification only. Do **not** auto-create `INDEX.md`.

For each CRITICAL or FLAPPING skill, check if an open issue already exists with this skill in `affected_skills` AND a matching `root_cause` signature:

- **Open issue exists, same root cause** → do nothing (no new file, no notification for this skill).
- **Open issue exists, different root cause** → append a note to the existing ISS file's body: `Update YYYY-MM-DD: new signature: <error>`. Do not file a new issue.
- **No open issue** → file a new one (see below).

For each skill now HEALTHY whose name appears in any open issue's `affected_skills`:
- Remove it from that issue's `affected_skills`. If the list becomes empty, set `status: resolved`, set `resolved_at: <now ISO>`, and move the row from Open to Resolved in INDEX.md.

**Filing a new issue:**
1. Find next ID: scan `~/.hermes/logs/skill-health/issues/ISS-*.md`, take max `NNN`, add 1. Format as zero-padded 3 digits (`ISS-042`).
2. Write `~/.hermes/logs/skill-health/issues/ISS-NNN.md` with YAML frontmatter:
   ```yaml
   ---
   id: ISS-NNN
   title: <skill> <concise failure>
   status: open
   severity: critical | high | medium | low   # critical=CRITICAL status, high=FLAPPING, medium=DEGRADED
   category: rate-limit | timeout | missing-secret | config | api-change | vps-limitation | unknown
   detected_by: skill-health
   detected_at: <ISO timestamp>
   affected_skills: [<skill>, ...]    # may grow later
   root_cause: <error signature, 1 line>
   fix_pr: null
   ---
   
   ## What happened
   <2-3 line summary>
   
   ## Signal
   - consecutive_failures: N
   - days_since_last_success: N
   - last_error: "<error>"
   - related skills: <list or "none">
   ```
3. Append a row to `~/.hermes/logs/skill-health/issues/INDEX.md` under **Open**: `| ISS-NNN | title | severity | category | YYYY-MM-DD | skill-a, skill-b |`.

All issue writes must be atomic per file — never partial updates mid-run.

### 5. Decide whether to notify

Build a stable signature from the current classification: sorted list of `CRITICAL+FLAPPING+DEGRADED skill names + SYSTEMIC callouts`. Generate a hash of it → `current_hash`.

- If `current_hash == prev_report.hash` AND `now - prev_report.last_notified_at < 24h` → **do not notify**. State unchanged.
- Otherwise → **notify** (there's new signal or the daily reminder cadence elapsed).

Always write `~/.hermes/memory/skill-health/last-report.json`:
```json
{
  "hash": "<current_hash>",
  "last_notified_at": "<ISO if notified this run, else previous value>",
  "last_run_at": "<ISO now>",
  "classification": { "critical": [...], "degraded": [...], "flapping": [...], "warning": [...], "healthy_count": N, "no_data": [...] }
}
```

### 6. Format the report

**Top line:** `HEALTH: OK` | `HEALTH: WARNING(W)` | `HEALTH: DEGRADED(D)` | `HEALTH: CRITICAL(C)` — most severe wins.

**Body (Slack message format, max 1 message):**

```
*Skill Health — ${today}*
HEALTH: CRITICAL(2)  [systemic: api.coingecko.com rate_limit — 3 skills]

🔴 CRITICAL
• token-movers — 5 fails, 3d down — WAIT-API (rate_limit) → ISS-042
• defi-monitor — 4 fails, 2d down — WAIT-API (rate_limit) → ISS-042

🟡 DEGRADED / FLAPPING
• digest — 52% success (14d), avg quality 2.1 — INVESTIGATE → ISS-043

⚪ NO DATA (2): skill-x, skill-y — DISPATCH-SKILL
🟢 HEALTHY: 34

Open issues: 2 · Resolved this run: 1 (rss-digest)
```

Rules for formatting:
- Cap per-section rows at 5; collapse the rest as `+N more — see ~/.hermes/logs/skill-health/issues/INDEX.md`.
- Omit HEALTHY list (count only). Omit any empty section.
- Always end with `Open issues: X · Resolved this run: Y`.
- If NO CRITICAL/DEGRADED/FLAPPING and no new/resolved issues → body is just `HEALTH: OK — N skills healthy`.

### 7. Notify and persist

- If the gate in step 5 said notify → `send_message` to Slack with the report body. Update `last_notified_at` in last-report.json to now.
- If gate said skip → do not call `send_message`. Log to `~/.hermes/logs/skill-health/run-log.md`:
  ```
  ### skill-health — YYYY-MM-DD HH:MM
  - SKILL_HEALTH_NOOP — state unchanged since <prev_run_at>, hash=<short>
  ```

On notify, log to `~/.hermes/logs/skill-health/run-log.md`:
```
### skill-health — YYYY-MM-DD HH:MM
- HEALTH: <OK|WARNING|DEGRADED|CRITICAL>
- filed: [ISS-NNN, ...]
- resolved: [ISS-NNN, ...]
- open: N
- systemic: <pattern or none>
```

### 8. Update persistent state

After the run, use the `memory` tool to store key facts:
- Last run timestamp and overall health status
- Count of critical/degraded/flapping skills
- Any systemic patterns detected

If the Honcho integration is available, use `honcho_conclude` to persist the session state for cross-session recall.

## Pitfalls — learned from production runs

1. **`hermes cron list` may fail silently.** Exit code is 0 even when the binary can't execute (e.g. venv symlink broken). Always check stdout for `HERMES_CRON_LIST_FAILED` or error text, don't trust exit code alone. Fall back to reading `cron-state.json` for the list of scheduled skills.
2. **`~/.hermes/cron/jobs.json` may not exist.** On this VPS, the cron job definitions are managed by the Hermes API, not a local file. When `hermes cron list` fails, `cron-state.json` is the ground truth for which skills have run and their status.
3. **Tirith security guard blocks `cat | python3` pipes.** Commands like `cat file.json | python3 -c "..."` are flagged as `pipe_to_interpreter` and blocked. Use `search_files` or `python3 -c "import json; data=json.load(open('file'))..."` without piped input instead.
4. **Issue tracking path is nested.** On this VPS the canonical issue tracker path is `/root/.hermes/home/.hermes/logs/skill-health/issues/` — not `~/.hermes/logs/skill-health/issues/`. Always `find` or glob for the actual path rather than hardcoding.
5. **Re-fired issues need new ISS files.** When a resolved issue's root cause re-appears (e.g. ISS-001 external-feature security block re-firing), file a new ISS with `related: ISS-NNN` in the body. Never reopen a Resolved issue.
6. **HTTP 402 from any provider is a systemic signal.** When any provider returns HTTP 402 "Insufficient Balance", all cron jobs configured to use that provider fail. Detect in `errors.log` (NOT agent.log — agent.log's `out=402` is a token count abbreviation, not an error code): `terminal("grep -c 'HTTP 402: Insufficient Balance' /root/.hermes/logs/errors.log")`. Identify the provider with: `terminal("grep 'HTTP 402' /root/.hermes/logs/errors.log | grep -oP 'provider=\\K\\w+' | sort | uniq -c | sort -rn")`. Each provider's 402 is a distinct billing failure — do not conflate OpenRouter 402 with DeepSeek 402. File a single SYSTEMIC ISS per affected provider, not per-skill WARNINGs.
7. **Honcho DNS errors are transient and benign.** `[Errno -3] Temporary failure in name resolution` at gateway startup typically resolves within seconds. Do not flag the Honcho plugin as DEGRADED for these — they're startup raciness, not skill failure.
8. **`cron-state.json` does not natively track `days_since_last_success`.** The classification table requires this for CRITICAL threshold computation, but the file only stores `last_success` timestamps. Compute `days_since_last_success` as `(now - last_success).days` at classification time. If `last_success` is null/missing and the skill has failures, treat it as 7+ days.
9. **Session file grep requires `find -mtime` + `grep -l`.** The `search_files` tool cannot reliably match patterns inside JSON session files. Use `terminal("find /root/.hermes/sessions/ -name '*.json' -mtime -7 -exec grep -l PATTERN {} \\;")` instead.
10. **Cron job skill names are on a `Skills:` line, not the `Name:` line.** `hermes cron list` outputs `Name:` (human label) and `Skills:` (comma-separated skill list) on separate lines. Parse the `Skills:` line, not `Name:`, to map cron jobs to tracked skills.
11. **`search_files` is unreliable for agent.log pattern matching.** The `search_files` tool with regex patterns like `Error code: 402` or `Error code: 429` returned 0 results on `/root/.hermes/logs/agent.log` despite the file containing 553 and 6,098 matches respectively. The agent.log entries are multi-line JSON-formatted strings that `search_files` (ripgrep-backed) may not handle correctly. **Always use terminal `grep` for agent.log and errors.log scanning.** E.g., `terminal("grep -c 'Error code: 429.*weekly usage limit' /root/.hermes/logs/agent.log")` returns accurate counts; `search_files` on the same file returns 0.
12. **`read_file` may fail on `~` paths or dedup incorrectly.** Using `read_file` with `~/.hermes/home/...` paths can return "File not found" even when the file exists (terminal `cat` on the resolved absolute path works). Also, `read_file` has a dedup mechanism where a failed read caches "not found" and subsequent attempts on the same path return "unchanged" without retrying. **Prefer terminal `cat <absolute-path>` for files at known absolute locations**, especially under `/root/.hermes/home/.hermes/logs/skill-health/issues/`. Use `terminal("cat /root/.hermes/home/.hermes/logs/skill-health/issues/INDEX.md")` to read the issue index reliably.
13. **402 detection: errors.log, not agent.log.** `grep -c 'Error code: 402'` on `agent.log` returned 0 on a day with 898 real 402 errors. The string `out=402` in agent.log is a token count abbreviation (e.g. `in=111019 out=402 total=111421`), not an error. Real HTTP 402 errors appear in `errors.log` with patterns like `HTTP 402: Insufficient Balance` or `Error code: 402 - {'error': {'message': 'Insufficient Balance'...}}`. **Always scan `errors.log` for 402 detection**, using: `terminal("grep -c 'HTTP 402\\|Insufficient Balance' /root/.hermes/logs/errors.log")`.
14. **`cron-state.json` can be stale; `hermes cron list` is authoritative.** The cron list output includes the definitive last-run status for each job with timestamps. When `cron-state.json` was last written days ago (e.g., June 7 on a June 9 run), the cron list captures failures that occurred since the last state write. Always cross-reference cron list statuses against cron-state entries and update the state file with the fresher data.
15. **`~` expands to `/root/.hermes/home/` on this VPS, not `/root/`.** Terminal commands using `~/.hermes/logs/agent.log` resolve to `/root/.hermes/home/.hermes/logs/agent.log` — which exists as a directory but does NOT contain the live log files. The actual agent.log and errors.log live at `/root/.hermes/logs/`. All grep commands in this skill now use absolute `/root/.hermes/logs/` paths to avoid this mismatch. When adding new commands that reference log files, always use `/root/.hermes/logs/`.
16. **Security blocks (Blocked: prompt matches threat pattern) are in errors.log, not agent.log.** `grep -c 'Blocked: prompt matches threat pattern'` on `agent.log` returns 0 even when the cron list shows security-blocked jobs with hundreds of instances. Threat-pattern blocks from the Tirith security guard are logged to `errors.log`. Detect with: `terminal("grep -c 'Blocked.*threat pattern' /root/.hermes/logs/errors.log")`. This is the same class of data-source mismatch as pitfall #13 (402 detection).

## VPS note

This skill runs directly on the Linux VPS with full terminal access. No sandbox restrictions. All data sources are local files (`~/.hermes/` tree) or accessible via the `terminal()` tool. No outbound API calls to GitHub Actions needed — skill run history is derived from agent logs and cron state.

## Constraints

- Never file two open issues for the same `(skill, root_cause)` pair — always check INDEX.md first.
- Never edit a Resolved issue. If a previously-resolved issue re-fires, file a new ISS with a pointer (`related: ISS-NNN`) in the body.
- Do not notify on pure HEALTHY runs more than once per 24h.
- Never touch `~/.hermes/logs/skill-health/issues/INDEX.md` Resolved section except to move rows into it; never delete rows.
- If the `send_message` tool is unavailable, log `SKILL_HEALTH_NOTIFY_FAILED` to the run log and continue — don't fail the whole audit.

## Verification

Manual trigger: "Run the skill-health audit"
Expected: console output showing HEALTH status (OK/WARNING/DEGRADED/CRITICAL) and any flagged items.
If CRITICAL: issue files created in `~/.hermes/logs/skill-health/issues/`, Slack notification sent.
If OK and not notified in last 24h: short Slack confirmation that audit ran clean.
If OK and notified <24h ago: run log entry only, no notification.

## Model Usage\n\nThis skill uses the configured default model from Hermes config (model.default/model.provider) for any internal LLM calls (e.g., for summarizing logs or generating reports). If the config is unavailable, it falls back to deepseek-v4-pro/deepseek.\n\nNote: If this skill fails due to a \"model not found\" error, it may indicate a configuration drift in the global model settings — this failure itself is a useful signal that the skill-health system is working as intended to detect configuration issues.\n\n## Self-Check: Verifying Skill-Health's Own Configuration\n\nSince skill-health audits other skills for model configuration issues, it's important to verify its own cron job is correctly configured. If you see skill-health-daily failing with \"model not found\" errors:\n\n1. Check the skill-health-daily cron job definition in `~/.hermes/cron/jobs.json`\n2. Verify the `model` and `provider` fields are either null (to use defaults) or set to valid values\n3. The skill is designed to fall back to `deepseek-v4-pro/deepseek` when config is unavailable\n4. If specifying a model explicitly, ensure it exists in the provider's model list\n5. See `references/model-configuration-issues.md` for diagnosis steps\n\nThis self-check prevents the auditor from becoming unauditable due to its own misconfiguration.

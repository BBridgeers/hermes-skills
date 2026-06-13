---
name: tool-builder
description: Build automation scripts from recurring command patterns and session logs — ship small, self-contained CLI tools that pass quality gates
tags: [dev, build, meta]
---

# Tool Builder — Automated Script Generation

> Adapted from Aeon's tool-builder. Replaces `./notify` with Slack `send_message`, `memory/logs/`/action-converter with `~/.hermes/logs/` + `session_search()`, git branch/commit/PR flow with script-create-test-log, and `scripts/` with `~/.hermes/scripts/`. Core scoring, quality gates, bash-first philosophy, and ≤150-line constraint preserved.

Your job is to ship one small, self-contained CLI tool that future Hermes agent runs (and the operator) will actually re-use. The bar for "shippable" is the **Quality gates** in step 3 — a tool that doesn't pass them is not done.

If the operator specifies a tool name (e.g., "build a cron-doctor script"), build that specific tool. Otherwise, auto-discover the highest-scoring opportunity.

## Steps

### 1. Find an opportunity

Score candidates from these sources, then build the highest-scoring one. Each source contributes at least one concrete pattern; do not invent ideas with no grounding.

| Source | What to look for |
|--------|------------------|
| `~/.hermes/logs/` (last 14 days) | Recurring shell incantations (`gh api …`, `curl … \| jq …`) repeated across days |
| `session_search()` | Search past sessions for repeated command patterns — the same tool invocations, error recovery sequences, or multi-step pipelines |
| Persistent memory | Stated goals, tracked items, preferences that suggest automation |
| Cron failures | Run `hermes cron list` to find skills with consecutive failures — a retry/diagnose helper may be the right tool |
| `~/.hermes/scripts/` directory | Existing TODOs in headers, near-duplicate scripts that could share a helper |

**Score each candidate** as `occurrences × estimated_minutes_saved_per_run × reusability` where:
- `occurrences` = distinct days the pattern shows up (1 if speculative)
- `estimated_minutes_saved_per_run` = realistic, not aspirational
- `reusability` = 1 (one-skill use) to 3 (used by many skills or operator-facing)

Drop candidates that:
- Already exist in `~/.hermes/scripts/` (scan with `search_files(target='files', pattern='*', path='~/.hermes/scripts/')`). Treat near-name matches as duplicates unless clearly different.
- Are better solved by a new skill than a script (multi-step reasoning, LLM-driven output → skill, not script).
- Have score < 4. If nothing scores ≥ 4, abort with a Slack `send_message("tool-builder: no opportunity scored ≥ 4 today — skipping")` and log the top 3 candidates to `~/.hermes/logs/tool-builder.md` for next time. Do not build a low-value tool just to ship something.

Record the chosen candidate's name, source, score, and one-sentence purpose before building.

### 2. Design the tool

State explicitly, in 5 lines max:
- **Name**: kebab-case, ≤24 chars, no extension (e.g. `cron-doctor`, not `cron_doctor.sh`)
- **Purpose**: one sentence, present tense
- **Inputs**: positional args, flags, env vars, stdin
- **Outputs**: stdout shape (text or JSON), stderr usage, file writes (if any), exit codes
- **Dependencies**: prefer `bash + jq + gh + curl + date` (already available). Node.js or Python only when bash gets ugly. **No `npm install`, no `pip install`.**

### 3. Build it — Quality gates (all must pass)

Write to `~/.hermes/scripts/{tool-name}` (no extension). Match the conventions of existing Hermes scripts. Every shipped tool must satisfy **all** gates below; if a gate doesn't apply, say why in the header comment.

**Header (mandatory):**
```bash
#!/usr/bin/env bash
# {tool-name} — {one-sentence purpose}
#
# Usage:
#   ~/.hermes/scripts/{tool-name}                  # default
#   ~/.hermes/scripts/{tool-name} --json           # machine-readable
#   ~/.hermes/scripts/{tool-name} --dry-run        # show what would happen
#   ~/.hermes/scripts/{tool-name} --help           # this message
#
# Exit codes:
#   0  success
#   1  generic failure
#   64 usage error           (EX_USAGE)
#   75 transient failure     (EX_TEMPFAIL — retry-able, e.g. network)
#   78 missing configuration (EX_CONFIG — e.g. required env var unset)
#
# Used by: {skills or "operator-only" — be honest}
# Dependencies: {jq, gh, curl, date, etc.}

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
```

**CLI gates:**
1. `--help` / `-h` prints the header (using `sed -n '2,N p' "$0" | sed 's/^# \?//'`) and exits 0.
2. Unknown arg exits 64 with a one-line error to stderr.
3. `--json` (when output is structured) emits valid JSON to stdout, nothing else. No mixed text + JSON.
4. `--dry-run` is required for any tool that writes files, posts to APIs, mutates state, or sends notifications. It must print the intended actions to stderr and make zero side effects.
5. **stdout = data, stderr = diagnostics.** Progress messages, warnings, and errors go to stderr so `tool | jq` works.
6. **Idempotent**: a second consecutive invocation with the same args produces the same end state and same exit code 0. If real idempotency is impossible (e.g. the tool fetches live data), idempotency means "no duplicate writes / no double-posts" — say so in the header.
7. Required env vars are checked at startup; if missing, exit 78 with `error: $VAR_NAME required` to stderr.
8. **Path-portable**: use `SCRIPT_DIR` (above) for any repo-relative paths. No hardcoded `/home/runner/...`.
9. Bash uses `set -euo pipefail`. Python uses `from __future__ import annotations` + explicit error handling. Node uses `process.exit(code)` and try/catch around async work.
10. Final line of bash scripts is a meaningful command — no trailing `exit 0` unless deliberate.

### 4. Verify (multi-step)

Run, in order, and only proceed if each passes:

```bash
mkdir -p ~/.hermes/scripts
chmod +x ~/.hermes/scripts/{tool-name}
~/.hermes/scripts/{tool-name} --help                                    # → exits 0, prints usage
~/.hermes/scripts/{tool-name} --notarealflag 2>/dev/null; [ $? -eq 64 ] # → unknown arg exits 64
~/.hermes/scripts/{tool-name} --dry-run [args]   2>/dev/null            # → exits 0, no side effects
~/.hermes/scripts/{tool-name} [args]              # real run            # → exits 0
~/.hermes/scripts/{tool-name} [args]              # second run          # → exits 0, no duplicates
```

If `--json` is supported, also: `~/.hermes/scripts/{tool-name} --json [args] | jq . >/dev/null` must succeed.

If any verification fails: fix once. If still failing, **abort the build** — delete the half-built script (`rm ~/.hermes/scripts/{tool-name}`), send `send_message("tool-builder: aborted {tool-name} — {reason}")`, log the attempt to `~/.hermes/logs/tool-builder.md`, and exit. Do not ship broken tools.

If a required secret is unavailable in this environment, **still ship the tool** but document the env var clearly in the header and have it exit 78 cleanly when unset.

### 5. Log the result

Append to `~/.hermes/logs/tool-builder.md` (create the file if it doesn't exist):

```markdown
## {date} — Tool Builder
- **Tool:** ~/.hermes/scripts/{tool-name}
- **Purpose:** {one-line}
- **Source:** {what triggered this — session_search pattern, log repetition, cron failure, etc.}
- **Score:** {occurrences} × {minutes_saved} × {reusability} = {N}
- **Gates:** all passed (help/dry-run/json/idempotent/exit-codes)
- **Verification:** all steps passed before log
```

If you aborted in step 1 (no candidate ≥ 4) or step 4 (verification failed), log it with `**Outcome:** skipped — {reason}` and the top 3 candidates considered, so the next run can pick up the trail.

### 6. Notify

Send a single message via `send_message` to Slack:
```
tool-builder: built ~/.hermes/scripts/{tool-name} — {one-line purpose}
score: {N} | source: {source} | log: ~/.hermes/logs/tool-builder.md
```

If `send_message` is unavailable, log `TOOL_BUILDER_NOTIFY_FAILED` and continue — the log file is the authoritative record.

## Guidelines

- **Bash first, Node second, Python third.** Match the existing Hermes codebase conventions.
- **Small and focused.** One tool, one job. If a tool needs >150 lines of bash, it's probably two tools.
- **Don't duplicate skills.** Skills do reasoning; scripts do mechanical work. If the task needs an LLM, it's a skill, not a script.
- **Don't add new dependencies.** Only use binaries already available (`jq`, `gh`, `curl`, `date`, `python3`, `node`).
- **Operator-friendly.** Every tool must be runnable with `~/.hermes/scripts/{name}` — no cron-only shortcuts.
- **No backwards-compat shims.** If you need to refactor a script, change it; we don't keep dead flags.
- **Path-portable.** Use `$HOME/.hermes/` or `SCRIPT_DIR` for all internal paths. Never hardcode absolute paths.

## Constraints

- Do not ship a tool that fails any quality gate. Aborting is a valid outcome — log it.
- Do not invent opportunities. If the score floor (≥ 4) is not met, skip the run.
- If the operator names a specific tool, build that one regardless of score.
- Keep tools focused: one job, ≤150 lines, bash-first.

---
name: skill-repair
description: Diagnose and fix failing skills or cron jobs automatically — systemic-first triage, per-category playbooks, verification plan. Adapted from Aeon's self-healing repair architecture.
var: ""
tags: [meta, devops, self-healing]
---

# Skill Repair — Autonomous Failure Remediation

> Adapted from Aeon's skill-repair playbook architecture. Phases: PREFLIGHT → TRIAGE → DIAGNOSE → REPAIR → VERIFY → LOG

## Purpose

Autonomously diagnose and repair failing Hermes skills or cron jobs. Prefers a single shared fix over multiple per-skill patches when failures cluster. Never edits blindly. Never touches secrets.

## Exit taxonomy

| Code | Meaning |
|------|---------|
| `REPAIR_OK_FIXED` | Per-skill fix applied |
| `REPAIR_OK_SYSTEMIC` | Shared root cause across N skills — single fix |
| `REPAIR_DIAGNOSED_NO_FIX` | Root cause known but requires operator action |
| `REPAIR_NO_TARGETS` | All tracked skills healthy |
| `REPAIR_BLOCKED` | Preflight failed or cooldown active |

## Phase 1: PREFLIGHT

Bail with `REPAIR_BLOCKED` if:
- Cannot access skills directory (`~/.hermes/skills/`)
- No recent failures found in memory or session history
- Target skill was repaired in last 24h (check `~/.hermes/state/skill-repair-history.json` — create `{}` if absent)

## Phase 2: TRIAGE (find what to fix)

Two paths:

**Path A — `${var}` set explicitly**: repair that specific skill.

**Path B — auto-select (using session_search and memory):**

1. Search for recent failures: `session_search(query="skill OR cronjob OR failed OR broken OR error")`
2. Check memory for known-broken skills or patterns
3. **Cluster by error signature.** If 2+ skills share the same error pattern (e.g., same API returning 403, same dependency missing), this is systemic. Prefer one shared fix.
4. Pick worst target: highest failure count, most recent failure, highest impact.

## Phase 3: DIAGNOSE (build dossier before touching anything)

For the target skill:
1. **Read the SKILL.md** — note declared dependencies, APIs, external calls, env var references
2. **Read recent session context** — what errors appeared? What was the last successful state?
3. **Check for regressions** — was the skill recently edited? Check `git log -- skills/{name}/SKILL.md` if in a git repo
4. **Classify the failure** into exactly one category:
   - `api-change` — external API changed
   - `rate-limit` — being throttled
   - `timeout` — took too long
   - `dependency-missing` — required tool/library absent
   - `prompt-bug` — skill instructions are wrong/incomplete
   - `output-format` — skill produces malformed output
   - `missing-secret` — env var / API key missing
   - `config` — misconfiguration
   - `permanent-limitation` — cannot be fixed (fundamental constraint)
   - `unknown` — unclear root cause

## Phase 4: REPAIR — per-category playbook

Apply the matching playbook:

| Category | Playbook |
|----------|----------|
| **api-change** | Search for the API's current docs. Update endpoints, payload shape, headers. Cite source URL in fix notes. |
| **rate-limit** | Add delay/backoff. Reduce request frequency. Suggest less frequent cron schedule. |
| **timeout** | Split work into smaller chunks. Increase timeout. Downgrade model for cheaper/faster runs. |
| **dependency-missing** | Install missing tool (`apt install`, `pip install`, `npm install`). Update skill to declare dependency. |
| **prompt-bug** | **Minimum-edit.** Add the missing constraint, forbidden phrase, or clarifying example. Do NOT rewrite entire skill. Diff should be <30 lines. |
| **output-format** | Fix output structure. Add validation. Ensure parseable format. |
| **missing-secret** | **NEVER edit the skill to remove the secret requirement.** File a clear notification identifying the missing secret name. Exit `REPAIR_DIAGNOSED_NO_FIX`. |
| **config** | Small config edits only. Never add/remove top-level structure. |
| **permanent-limitation** | Skip. Exit `REPAIR_DIAGNOSED_NO_FIX`. |
| **unknown** | Do NOT edit blindly. Append diagnostic notes. Exit `REPAIR_DIAGNOSED_NO_FIX`. |

**Risk classification:**
- **LOW** — prompt tweak, dependency install, comment change (<30 lines)
- **MED** — data source change, output format change
- **HIGH** — touches config, disables a skill, modifies secrets. Must flag for manual review.

## Phase 5: VERIFY

After applying fix:
1. Re-read the edited SKILL.md — confirm YAML frontmatter intact (name, description, tags)
2. If possible, dry-run or test the skill
3. Write a verification plan: "To verify: run skill {name} with {params}. Expected: {result}."

## Phase 6: BRANCH, COMMIT, LOG

If in a git repo:
```bash
git checkout -b fix/skill-repair-{name}-$(date +%Y%m%d)
git add skills/{name}/SKILL.md
git commit -m "fix({name}): [one-line root cause → fix]"
```

Document in memory:
```
skill-repair — {EXIT_CODE}
Target: {name}
Category: {category}
Root cause: [one line]
Fix: [one line] (risk: LOW|MED|HIGH)
```

Update `~/.hermes/state/skill-repair-history.json` with cooldown entry.

## Constraints

- One target per run (or one systemic cluster)
- Minimum-edit principle: keep diffs tiny
- Never modify secrets or delete security checks
- Never auto-merge HIGH-risk changes
- If category is `unknown`, append diagnostics only — never guess
- 24h cooldown per target (to prevent repair loops)

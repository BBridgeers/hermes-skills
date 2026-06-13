# Skill Repair — Playbook Reference

> Adapted from Aeon's 10-category repair playbook architecture.

## Phase Flow

```
PREFLIGHT → TRIAGE → DIAGNOSE → REPAIR → VERIFY → LOG
```

Stop early at the appropriate exit code if any phase finds nothing actionable.

## Exit Codes

| Code | Meaning |
|------|---------|
| `REPAIR_OK_FIXED` | Per-skill fix applied |
| `REPAIR_OK_SYSTEMIC` | Shared root cause across N skills — single fix |
| `REPAIR_DIAGNOSED_NO_FIX` | Root cause known but requires operator action |
| `REPAIR_NO_TARGETS` | All tracked skills healthy |
| `REPAIR_DRY_RUN` | `${var}=dry-run:NAME` — diagnostic only |
| `REPAIR_BLOCKED` | Preflight failed or cooldown active |

## 10 Playbooks

| Category | Trigger | Action | Risk |
|----------|---------|--------|------|
| **api-change** | External API errors, 401/403/404 on known endpoints | Web-search current API spec. Update endpoints, payload shape, headers. Cite source URL. Never guess. | MED |
| **rate-limit** | 429 responses, "too many requests" | Add delay/backoff. Reduce request count or add fallback endpoint. Suggest less frequent cron schedule (but don't edit config unless authorized). | LOW |
| **timeout** | Task exceeds time limit, partial output | Split work into stages. Add early-return on partial success. Downgrade model for cheaper/faster runs. | MED |
| **dependency-missing** | "command not found", import errors | Install missing tool (`apt install`, `pip install`, `npm install`). Update skill to declare dependency in its SKILL.md description. | LOW |
| **prompt-bug** | Wrong output structure, missing data, hallucinated content | **Minimum-edit specificity insertion.** Add missing constraint, forbidden phrase, required output structure, or clarifying example. Keep diff <30 lines. | LOW |
| **output-format** | Malformed JSON, wrong schema, parse errors | Fix output structure. Cross-reference any eval assertions. Add validation step. | MED |
| **missing-secret** | "API key not found", auth errors | **NEVER modify the skill to remove the secret requirement.** File clear notification identifying the missing env var name. Exit `REPAIR_DIAGNOSED_NO_FIX`. | — |
| **config** | Misconfiguration, wrong paths | Small reversible config edits only (`schedule`, `var`, `model`, `enabled`). Never add/remove top-level structure. Keep diff <5 lines. | MED-HIGH |
| **permanent-limitation** | Sandbox limitation, platform restriction | Skip. Should not reach repair. Update issue. Exit `REPAIR_DIAGNOSED_NO_FIX`. | — |
| **unknown** | Unclear root cause, intermittent | **Do NOT edit blindly.** Append full diagnostic dossier to issue. Exit `REPAIR_DIAGNOSED_NO_FIX`. Operator triages. | — |

## Systemic-First Triage

Before fixing individual skills, cluster failures by:
1. Error signature (normalize: lowercase, strip timestamps/IDs/digits)
2. Category match
3. Shared dependency (same API, same tool, same env var)

If 2+ skills share a signature: one shared fix > N per-skill patches.

## Cooldown & Idempotency

- 24h cooldown per target (stored in `~/.hermes/state/skill-repair-history.json`)
- Check for existing open PRs (search session history)
- Max 3 repair PRs per day
- `${var}=dry-run:NAME` bypasses cooldown (diagnostic only)

## Risk Classification

| Level | Criteria | Auto-merge? |
|-------|----------|-------------|
| **LOW** | Prompt tweak, dependency install, comment change (<30 lines diff) | Yes |
| **MED** | Data source change, output format change, new env var reference | Flagged |
| **HIGH** | Config changes, feature removal, skill disable | `manual-review` required |

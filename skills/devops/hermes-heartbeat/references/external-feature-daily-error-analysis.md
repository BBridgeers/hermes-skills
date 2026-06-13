# External Feature Cron Job Error Analysis

**Job ID**: `1f1e541dd9ca`  
**Job Name**: external-feature-daily  
**Last Status**: `error`  
**Last Run**: `2026-05-24T04:00:48.771854+00:00`  
**Error Message**: `Blocked: prompt matches threat pattern 'exfil_curl_auth_header'. Cron prompts must not contain injection or exfiltration payloads.`  

## Root Cause

The external-feature skill's cron prompt includes a `curl` command pattern with a bearer token in the Authorization header. The tirith security scanner flagged this as a potential **credential exfiltration** pattern (regex matching `curl ... -H "Authorization: Bearer ..."`).

This is a **security guardrail working as designed**, not a malfunction.

## Resolution Paths

### Option 1 — Modify External Feature Skill Prompt
Remove or neutralize the auth header from the cron prompt. Instead of including auth headers in curl commands, use environment variable substitution, `python3 -c` with `requests`/`urllib`, or Hermes' native toolsets (`web_search`, `web_extract`) where possible.

### Option 2 — Whitelist the Job (Not Recommended)
Add an exception in `security.acked_advisories` to suppress this specific pattern for this job.  
**Why not preferred**: weakens the global guardrail; if the external-feature workflow changes, the same flaw could reappear.

### Option 3 — Accept the Failure and Skip
Since external-feature is a proactively-enhanced repo job, let it fail and log the block. No user-facing impact. The skill's `notify` step checks if new issues/features were actually created before reporting — in this case, nothing new was created, so the failure is silently discarded.

## Recommendation

- **Short-term**: Accept that this job will fail each cycle until external-feature's workflow is updated to avoid the `curl` auth-header pattern.
- **Medium-term**: Submit a PR to `external-feature` skill to use API client libraries instead of raw `curl` commands, or refactor to use Hermes' native toolsets (`web_search`, `web_extract`) where possible.
- **Long-term**: Add a `security-exempt-jobs` config in cron to explicitly whitelist jobs that require elevated toolsets but pass a separate lint-style check.

## Session Context

- Triggered heartbeat run: `2026-05-25T16:46:34+00:00`
- Cron analysis performed via `read_file('/root/.hermes/cron/jobs.json')`
- Error status retrieved and logged in heartbeat output

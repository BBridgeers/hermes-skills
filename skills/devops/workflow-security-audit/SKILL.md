---
name: workflow-security-audit
description: Audit Hermes cron jobs, shell scripts (~/.hermes/scripts/*.sh), Docker configs, and any GitHub Actions workflows — with zizmor/actionlint, shellcheck, hadolint, and hand-rolled pattern checks. Classify findings against prior audit, auto-fix Critical/High regressions, notify via Slack only when something changes.
tags: [devops, security]
---

Today is `${today}`. Audit Hermes cron jobs, shell scripts, Docker configurations, and any GitHub Actions workflows. Classify findings against the most recent prior audit, auto-apply fixes for NEW Critical/High items, and notify via Slack **only if the delta is non-empty**.

**Core principle:** surface *changes* (new vulns, regressions of fixed ones) with an attacker's-eye-view per finding, and stay silent on clean runs so the notify isn't trained-to-ignore.

## Preflight

### 0a. Bootstrap variables

```bash
today=$(date -u +%F)
HOSTNAME=$(hostname 2>/dev/null || echo "hermes")
```

### 0b. Install scanners

Install only what's missing. Failures are non-fatal — the hand-rolled checks always run as backstop.

```bash
# shellcheck — static analysis for shell scripts
if ! command -v shellcheck >/dev/null 2>&1; then
  apt-get update -qq && apt-get install -y -qq shellcheck 2>/dev/null || true
fi

# hadolint — Dockerfile linter
if ! command -v hadolint >/dev/null 2>&1; then
  wget -q -O /usr/local/bin/hadolint \
    "https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64" 2>/dev/null \
    && chmod +x /usr/local/bin/hadolint || true
fi

# zizmor + actionlint — only if GitHub workflows exist
if [ -d ".github/workflows" ] || [ -d ".github/actions" ]; then
  if ! command -v zizmor >/dev/null 2>&1; then
    pipx install "zizmor" 2>/dev/null \
      || python3 -m pip install --user "zizmor" 2>/dev/null \
      || true
    export PATH="$HOME/.local/bin:$PATH"
  fi
  if ! command -v actionlint >/dev/null 2>&1; then
    bash <(curl -sL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 2>/dev/null || true
    export PATH="$PWD:$PATH"
  fi
fi
```

If `shellcheck` fails to install, mark it degraded and continue. If `hadolint` fails, fall back to manual Dockerfile pattern checks in step 2c. If `zizmor` + `actionlint` both fail but GH workflows exist, continue with hand-rolled checks but mark as `WORKFLOW_AUDIT_TOOL_DEGRADED`.

### 0c. Agent tool blocklist vs security patterns

Several security-relevant substrings (e.g., `mkfs`, `chmod 777`) are on the agent's hardline command blocklist. Shelling out to `grep -E` with these patterns in the command will be **silently blocked**. Use `search_files` (the agent's built-in content search) for pattern matching on file contents — it doesn't execute shell commands. Split compound patterns into individual safe regexes if needed. This applies to all hand-rolled checks in steps 2a–2d.

### 0d. Profile-qualified skill and script paths

Hermes stores runtime skills under `~/.hermes/home/.hermes/skills/` (profile-qualified), not just `~/.hermes/skills/`. Shell scripts that skills invoke live at both paths. The `find` commands in step 1 should search both trees.

### 0e. Co-tenant Docker configs

On a shared VPS, Docker configs for **co-tenant** projects (e.g., `/root/honcho/`, `/root/hermes-docker/`, `/root/vehicle-analyzer/`) are security-relevant even though they're outside `~/.hermes/`. The `find` in step 1 uses `~ -maxdepth 3` which covers these. If configs are nested deeper, increase maxdepth. Always include co-tenant compose files — they affect the same host's attack surface.

## Steps

### 1. Enumerate audit targets

```bash
# Shell scripts
SCRIPT_TARGETS=$(find ~/.hermes/scripts -type f -name "*.sh" 2>/dev/null)
# Also scan hooks
HOOK_TARGETS=$(find ~/.hermes/hooks -type f 2>/dev/null)
# Also scan skill companion scripts
SKILL_SCRIPTS=$(find ~/.hermes/skills ~/.hermes/home/.hermes/skills -type f \( -name "*.sh" -o -name "*.py" \) 2>/dev/null)

# Docker configs — use maxdepth 4 to catch co-tenant projects
DOCKER_TARGETS=$(find ~ -maxdepth 4 -type f \( -name "Dockerfile" -o -name "Dockerfile.*" -o -name "docker-compose.yml" -o -name "docker-compose.yaml" \) 2>/dev/null | grep -v '.cache' | grep -v 'node_modules')

# GitHub workflows (may not exist)
GH_WORKFLOW_TARGETS=$(find .github/workflows -maxdepth 2 -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null; \
                      find .github/actions -type f \( -name "action.yml" -o -name "action.yaml" \) 2>/dev/null)

# Cron jobs — capture the full output for analysis
CRON_JOBS=$(hermes cron list 2>/dev/null || echo "")
```

If ALL target sets are empty, exit with `WORKFLOW_AUDIT_NO_TARGETS` — notify `*Workflow security audit* — no auditable targets found (no scripts, docker configs, workflows, or cron jobs)` and stop.

### 2. Run scanners

#### 2a. Shell scripts — shellcheck

```bash
mkdir -p ~/.hermes/.audit
SHELLCHECK_OUT=""
for script in $SCRIPT_TARGETS $HOOK_TARGETS; do
  if [ -f "$script" ]; then
    result=$(shellcheck -f json "$script" 2>/dev/null || echo "[]")
    SHELLCHECK_OUT="${SHELLCHECK_OUT}${SHELLCHECK_OUT:+$'\n'}${result}"
  fi
done
echo "$SHELLCHECK_OUT" > ~/.hermes/.audit/shellcheck.json
```

Map shellcheck severity:
- `error` → **High** (script may fail or behave unexpectedly)
- `warning` with codes SC2086 (unquoted), SC2046 (unquoted cmd substitution), SC2068 (unquoted array) → **Critical** (injection risk)
- Other `warning` → **Medium**
- `info` → **Low**
- `style` → **Low**

#### 2b. Shell scripts — hand-rolled injection checks

Always run, even when shellcheck succeeds. These backstop gaps shellcheck misses:

- **Unsanitized variable interpolation into `eval`, `source`, `.`**: `eval "$VAR"`, `source "$VAR"`, `. "$VAR"` where `$VAR` derives from user/external input. Severity: **Critical**.
- **`curl | bash` or `wget -O- | sh`**: pipe-to-shell from external URLs. Severity: **Critical**.
- **Secret exposure in `echo`/`printf`**: `echo $TOKEN`, `printf '%s' $SECRET` (unquoted — leaks via word splitting). Severity: **High**.
- **`chmod 777`**: world-writable permissions. Severity: **High**.
- **`rm -rf /` or `rm -rf /*` or `rm -rf ~`**: destructive patterns. Severity: **Critical**.
- **Hardcoded credentials**: lines matching `PASSWORD=`, `TOKEN=`, `SECRET=`, `API_KEY=` with a non-empty, non-placeholder value that isn't `${...}`. Severity: **Critical** if in script body, **High** if commented.
- **`sudo` without restricted command**: bare `sudo` or `sudo su`. Severity: **Medium**.

#### 2c. Docker configs — hadolint + hand-rolled

```bash
# hadolint for Dockerfiles
for df in $(echo "$DOCKER_TARGETS" | grep -i dockerfile); do
  if command -v hadolint >/dev/null 2>&1; then
    hadolint -f json "$df" 2>/dev/null >> ~/.hermes/.audit/hadolint.json || true
  fi
done
```

Map hadolint to severity:
- `DL3006` (no HEALTHCHECK), `DL3008`/`DL3009` (unpinned apt), `DL3018`/`DL3019` (unpinned pip/apk) → **Medium**
- `DL3002` (last USER is root), `DL3004` (sudo used), `DL3020` (ADD instead of COPY) → **High**
- `DL3025` (CMD with `/bin/sh -c` when ENTRYPOINT exists), `DL4006` (SHELL not set with pipefail) → **Low**

**Hand-rolled Docker checks (always run):**

- **`USER root` or no `USER` directive**: container runs as root. Severity: **Critical**.
- **Secrets in ENV**: `ENV.*PASSWORD`, `ENV.*SECRET`, `ENV.*TOKEN`, `ENV.*API_KEY` with literal values (not `ARG` or build-time). Severity: **Critical**.
- **`COPY --chown` with `777` or world-writable**: Severity: **High**.
- **`EXPOSE` without `127.0.0.1` bind** (docker-compose only): ports bound to `0.0.0.0`. Severity: **High**.
- **`privileged: true`** (docker-compose): full host access. Severity: **Critical**.
- **`cap_add: ALL` or `cap_add: SYS_ADMIN`**: excessive capabilities. Severity: **Critical**.
- **No `restart: unless-stopped`** or equivalent: missing restart policy. Severity: **Low**.
- **`depends_on` without `condition: service_healthy`**: may start before db is ready. Severity: **Low**.
- **Bind-mounting docker socket** (`/var/run/docker.sock`): container breakout risk. Severity: **Critical**.
- **`network_mode: host`**: bypasses network isolation. Severity: **High**.
- **`pid: host`**: shares host process namespace. Severity: **Critical**.
- **Read-only rootfs not set** for stateless services: `read_only: true` absent. Severity: **Low**.
- **Default passwords for well-known services** (postgres/postgres, admin/admin, redis with no password). Severity: **High**.

#### 2d. Cron jobs — hand-rolled checks

Parse the output of `hermes cron list` for each active job. Check:

- **`hermes cron list` output reveals command injection patterns**: unquoted user input, eval, backticks. Severity: **Critical**.
- **Cron job runs as root context**: check if the job's deliver target or command implies elevated privileges. Severity: **Medium**.
- **No error handling in cron command**: pipe chains without `|| exit 1` or `set -e`. Severity: **Low**.

```bash
# Extract cron job details into parseable form
hermes cron list 2>/dev/null | grep -A 20 'active' | grep -E 'Name:|Schedule:|Command:' > ~/.hermes/.audit/cron_jobs.txt 2>/dev/null
```

#### 2e. GitHub workflows — zizmor + actionlint (if targets exist)

If `$GH_WORKFLOW_TARGETS` is non-empty, run the same pipeline as the original Aeon audit:

**zizmor:**
```bash
zizmor --format sarif --persona auditor .github/workflows .github/actions \
  > ~/.hermes/.audit/zizmor.sarif 2> ~/.hermes/.audit/zizmor.err || true
```

Map zizmor severity → our severity:
- `error` + confidence ≥ `high` → **Critical**
- `error` (other confidence) or `warning` + confidence = `high` → **High**
- `warning` → **Medium**
- `note` → **Low**

**actionlint:**
```bash
actionlint -format '{{json .}}' > ~/.hermes/.audit/actionlint.json 2> ~/.hermes/.audit/actionlint.err || true
```

Raise actionlint errors to **Medium** unless they touch security-relevant rules (`expression`, `shellcheck` with `SC2086`/`SC2046` over `${{ github.* }}` interpolation), in which case **High**.

**GH workflow hand-rolled checks:**
- **toJson-into-shell injection**: `echo '${{ toJson(github.event` piped to `jq` or command substitution. Severity: **Critical**.
- **`persist-credentials: true` + `ref: ${{ github.event.pull_request.head.sha }}`**: poisoned-pipeline. Severity: **Critical** on `pull_request_target`, **High** on `workflow_run`.
- **`GITHUB_ENV` / `GITHUB_OUTPUT` writes with user-controlled data**: newline-injection. Severity: **High**.
- **Mutable ref on third-party action**: `uses: owner/action@branch` or `@vN` where owner is not `actions`, `github`, `docker`, or `aws-actions`. Severity: **Medium**.

### 3. Build the current-run findings set

For each finding, emit a canonical record:

```json
{
  "fingerprint": "sha256(<rule_id>|<file>|<step_or_line_context>)",
  "severity": "Critical|High|Medium|Low",
  "rule_id": "shellcheck-SC2086|docker-root-user|hadolint-DL3002|cron-injection|zizmor-template-injection|...",
  "file": "~/.hermes/scripts/deploy.sh",
  "line": 42,
  "step": "Deploy step",
  "pattern": "<verbatim vulnerable snippet, ≤120 chars>",
  "source": "shellcheck|hadolint|hand-rolled|zizmor|actionlint",
  "target_type": "script|docker|docker-compose|cron|github-workflow"
}
```

The fingerprint is the key for delta classification — anchor to step/rule-id rather than line number (lines drift on unrelated edits).

### 4. Classify against prior audit (delta)

Find the most recent prior report:

```bash
PRIOR=$(ls -1 ~/.hermes/articles/workflow-security-audit-*.md 2>/dev/null | sort | tail -1)
```

If `$PRIOR` exists, extract its fingerprints from the machine-readable HTML comment trailer. Then label each current finding:

- **NEW** — fingerprint absent from prior report
- **REINTRODUCED** — fingerprint was marked `Auto-fixed` or `Resolved` in prior report, now present again
- **UNCHANGED** — fingerprint present in prior report, still present
- **RESOLVED** — fingerprint was present in prior report, now absent from current scan (emit as separate section)

If `$PRIOR` does not exist, every finding is NEW.

### 5. Determine verdict and exit mode

| Condition | Verdict | Exit mode |
|---|---|---|
| No findings at all | `WORKFLOW_AUDIT_CLEAN — no findings across N targets` | `CLEAN` |
| Only UNCHANGED findings, no NEW/REINTRODUCED | `WORKFLOW_AUDIT_UNCHANGED — N carried over from ${PRIOR_DATE}` | `UNCHANGED` |
| ≥1 REINTRODUCED | `WORKFLOW_AUDIT_REGRESSION — N previously-fixed finding(s) reintroduced` | `REGRESSION` |
| ≥1 NEW Critical | `WORKFLOW_AUDIT_NEW_CRITICAL — N new critical finding(s)` | `NEW_CRITICAL` |
| ≥1 NEW High (no critical) | `WORKFLOW_AUDIT_NEW_HIGH — N new high-severity finding(s)` | `NEW_HIGH` |
| NEW Medium/Low only | `WORKFLOW_AUDIT_NEW_INFO — N new lower-severity finding(s)` | `NEW_INFO` |
| All scanners failed / no targets | `WORKFLOW_AUDIT_NO_TARGETS` or `WORKFLOW_AUDIT_TOOL_FAIL` | `TOOL_FAIL` |

**Gating rule:** in `CLEAN` and `UNCHANGED` modes, do not notify via Slack. Write a log-only entry. Silence is correct on no-delta runs.

### 6. Write the audit report

Path: `~/.hermes/articles/workflow-security-audit-${today}.md` (overwrite if exists — latest audit of the day is authoritative).

```markdown
# Workflow Security Audit — ${today}

**Verdict:** ${VERDICT_LINE}
**Host:** ${HOSTNAME}
**Targets audited:** ${script_count} scripts, ${docker_count} docker configs, ${cron_count} cron jobs, ${gh_count} GH workflows
**Findings this run:** ${total} (${crit} critical, ${high} high, ${med} medium, ${low} low)
**Delta vs ${PRIOR_DATE or "(no prior audit)"}:** ${new_count} new, ${reintroduced_count} reintroduced, ${unchanged_count} unchanged, ${resolved_count} resolved
**Auto-fixed:** ${fixed_count}

## Regressions (previously-fixed findings now present again)

[One subsection per REINTRODUCED finding.]

## New findings

[One subsection per NEW finding.]

### [CRITICAL|HIGH] ${rule_id} — ${short title}
**File:** `${file}` · **Line:** ${line} · **Target type:** ${target_type}
**Pattern:**
\`\`\`
${verbatim snippet}
\`\`\`

**Attack chain:**
1. **Entry:** ${trigger} — reachable by ${who}
2. **Vector:** ${what is attacker-controlled}
3. **Sink:** ${where exploitation happens}
4. **Blast radius:** ${what's exposed}

**Fix:**
\`\`\`
# BEFORE
...
# AFTER
...
\`\`\`

**Status:** Auto-fixed / Manual review required

---

[Medium and Low findings get a compact one-line-per-finding table, no attack chain.]

## Carried over (unchanged)

| Severity | Rule | File | First seen |
|---|---|---|---|
| ... | | | |

## Resolved since ${PRIOR_DATE}

- ${finding title} in `${file}` — no longer present

## Source status

- shellcheck: ${ok|fail|degraded}
- hadolint: ${ok|fail|degraded|not-applicable}
- zizmor: ${ok|fail|degraded|not-applicable}
- actionlint: ${ok|fail|degraded|not-applicable}
- hand-rolled: ${ok|fail}

<!--
workflow-security-audit-fingerprints
${fingerprint_1} severity=Critical status=auto-fixed rule=shellcheck-SC2086 file=~/.hermes/scripts/deploy.sh step=Deploy
${fingerprint_2} severity=High status=manual rule=docker-root-user file=Dockerfile step=FROM
...
-->
```

The HTML-comment trailer at the bottom is the machine-readable fingerprint set the *next* run reads in step 4. Don't omit it.

### 7. Auto-fix NEW Critical/High findings

For each NEW Critical and NEW High finding (**not** UNCHANGED — those failed a prior fix or are known-manual):

#### Shell scripts

**Injection fix (SC2086, SC2046, hand-rolled eval/curl-pipe):**
- If `$VAR` is unquoted where it should be: wrap in double quotes `"$VAR"`
- If `eval "$VAR"` or `source "$VAR"` where VAR is user-controlled: replace with explicit dispatch (case statement or sanitized variable)
- If `curl URL | bash`: replace with checksum-verified download + execute
- If hardcoded credentials found: replace with `"${ENV_VAR}"` reference and add a comment: `# Set via environment: export ENV_VAR=...`
- If `chmod 777`: change to `chmod 755` or `chmod 700`

Use the `patch` tool for inline modifications. Do not rewrite whole files.

**Idempotency check before fixing:**
1. Read the relevant lines.
2. If the fix is already applied (quotes present, env var reference used, correct permissions), skip — flag as stale finding in report.
3. After editing, validate: `shellcheck "$FILE"` — if it introduces new errors, revert and mark as `Manual required`.

#### Docker configs

**For `USER root` or missing USER:**
- Add `USER 1000:1000` (or appropriate non-root user) before CMD/ENTRYPOINT
- If user doesn't exist in image, add `RUN addgroup --system app && adduser --system --group app` before the USER directive

**For secrets in ENV:**
- Replace with `ARG` + comment: `# ARG set at build time: docker build --build-arg DB_PASSWORD=...`
- In docker-compose: move to `.env` file reference

**For `privileged: true`:**
- Remove `privileged: true` and add only the specific `cap_add` entries needed (e.g., `NET_ADMIN`, `SYS_PTRACE`)

**For docker socket mounts:**
- Comment out and add: `# SECURITY: mounting docker.sock allows container escape. Consider using a dedicated CI runner or podman.`

Do NOT auto-fix: permission scope decisions (`cap_add`, `network_mode`), pinning decisions (image tags), or architectural changes (read_only rootfs). Flag these as `Manual required`.

#### Cron jobs

Do not auto-fix cron jobs — the operator must review command changes. Flag as `Manual required` with the recommended fix in the report.

### 8. Notify via Slack (gated)

Only in exit modes `NEW_CRITICAL`, `NEW_HIGH`, `REGRESSION`, `TOOL_FAIL`:

Use `send_message` to Slack with a single-paragraph message:

```
*Workflow security audit — ${today}*
${VERDICT_LINE}
Host: ${HOSTNAME}
${script_count} scripts · ${docker_count} docker configs · ${cron_count} cron jobs · ${gh_count} GH workflows
Findings: ${total} total (${crit}C / ${high}H / ${med}M / ${low}L)
Delta: ${new_count} new · ${reintroduced_count} reintroduced · ${resolved_count} resolved
Auto-fixed: ${fixed_count} · Manual review: ${manual_count}
Report: ~/.hermes/articles/workflow-security-audit-${today}.md
```

Exit mode `NEW_INFO` (medium/low only): log only — do not notify.

If `send_message` is unavailable, log `WORKFLOW_AUDIT_NOTIFY_FAILED` and continue — the article is the authoritative record.

### 9. Log

Append to `~/.hermes/logs/${today}.md`:

```
## Workflow Security Audit
- Exit: ${EXIT_MODE}
- Verdict: ${VERDICT_LINE}
- Targets: ${script_count} scripts, ${docker_count} docker configs, ${cron_count} cron jobs, ${gh_count} GH workflows
- Findings: ${total} total (${crit}C / ${high}H / ${med}M / ${low}L)
- Delta: ${new_count} new, ${reintroduced_count} reintroduced, ${unchanged_count} unchanged, ${resolved_count} resolved
- Auto-fixed: ${fixed_count}
- Report: ~/.hermes/articles/workflow-security-audit-${today}.md
- Source status: shellcheck=${ok|fail} hadolint=${ok|fail} zizmor=${ok|fail} actionlint=${ok|fail} hand-rolled=${ok|fail}
```

## Constraints

- Never auto-fix `UNCHANGED` findings (if they didn't get fixed the first time there's a reason). Auto-fix is for NEW and REINTRODUCED Critical/High only.
- Never auto-fix **cron jobs**, **docker capabilities/pinning/network decisions**, or **GH workflow permissions** — always flag as Manual.
- Preserve the existing Hermes state — all audit artifacts go under `~/.hermes/.audit/` and `~/.hermes/articles/`.
- If exit mode is `CLEAN` or `UNCHANGED`, skip Slack notification — log only.
- No new env vars required beyond what's in `~/.hermes/config.yaml`.
- `send_message` is the notification channel. If it's unavailable, log the failure and continue.

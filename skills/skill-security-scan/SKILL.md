---
name: skill-security-scan
description: Audit Hermes skills and companion scripts for injection, exfiltration, traversal, and prompt-override risks with delta tracking, baseline suppression, issue filing, and per-finding remediation
var: ""
tags: [security, devops, meta]
---

> **${var}** — a SKILL.md path, a skill name (e.g. `token-movers`), or a directory. Empty = full corpus scan.

Today is ${today}. Audit the Hermes skills codebase for security risks in skill instructions and companion scripts before they run.

## Threat categories

Files instruct Hermes Agent to take actions. Adversarial or sloppy files can:

- **Shell injection** — unquoted variable expansion, `eval`, backticks, `$(...)` in bash blocks
- **Secret exfiltration** — env vars or file contents piped into outbound HTTP requests
- **Path traversal** — access files outside skills directory via `../..` chains or absolute paths
- **Prompt override** — instructions in fetched content or skill bodies attempting to make the agent disregard prior guidance, switch persona, or act on new "system" rules
- **Destructive commands** — irreversible ops like recursive deletes from root, device writes, forced pushes to main
- **Obfuscation** — zero-width Unicode (U+200B, U+FEFF), bidi override (U+202E / Trojan Source), base64-decoded payloads, `fromCharCode`, hex-escaped command strings, webhook SSRF hosts (ngrok, interact.sh, webhook.site, burpcollaborator, pipedream, requestbin)

> **For external repo auditing**, see `references/deep-scan-methodology.md` — two-pass approach with REAL threat patterns (not documentation words) for evaluating public skill repos before import. Most broad-scan hits on documentation-heavy repos are false positives.

> **For VPS SSH hardening**, see `references/vps-ssh-hardening.md` — cloud-init.conf override trap, fail2ban setup, attacker blocking, and the `sshd -T` verification pattern.

> **For inline scanning when scan.sh is unavailable or agent blocks grep patterns**, see `references/inline-scan-methodology.md` — pattern-splitting strategy, `search_files` fallback, code-fence downgrade, and tool installation fallbacks.

## Coverage

Scan every run:
- `~/.hermes/skills/*/SKILL.md` (primary)
- `~/.hermes/skills/*/*.sh` and `~/.hermes/skills/*/*.py` (companion scripts that skills invoke)

When `${var}` is set:
- If it matches an existing SKILL.md path (absolute or relative) → scan that file only
- Else if a directory exists at `~/.hermes/skills/${var}/` → scan everything under it
- Else if it looks like a bare skill name and `~/.hermes/skills/${var}/SKILL.md` exists → scan that file
- Else abort with `ERROR: scope not found for var=${var}`

## Inputs and state

| Path | Purpose |
|------|---------|
| `~/.hermes/skills/skill-security-scan/scan.sh` | Raw regex scanner (HIGH/MEDIUM/LOW pattern library) |
| `~/.hermes/skills/skill-security-scan/scan-baseline.yml` | Human-reviewed-as-safe suppressions (bootstrap if missing) |
| `~/.hermes/memory/state/security-scan.json` | Prior scan snapshot — used for delta |
| `~/.hermes/memory/issues/INDEX.md` | Open/resolved issue index (HIGH findings file here) |
| `~/.hermes/memory/articles/security-scan-${today}.md` | Report output (only written if there are findings or a delta) |

### Baseline file format

`~/.hermes/skills/skill-security-scan/scan-baseline.yml`:
```yaml
# Each entry suppresses a specific (file, line_range, pattern) match that a human has reviewed.
# Format:
#   - file: <path>
#     pattern: <regex pattern from scan.sh HIGH_PATTERNS/MEDIUM_PATTERNS/LOW_PATTERNS>
#     lines: "15-25"          # optional line range; omit to suppress across whole file
#     reason: "documentation in threat model section"
#     reviewed_by: "operator"
#     reviewed_at: "2026-05-03"
suppressions: []
```

Seed `suppressions` at bootstrap with the self-documenting matches that we already know are false positives:
1. `~/.hermes/skills/skill-security-scan/SKILL.md` — all prompt-override pattern matches inside the "Threat categories" section (documentation, not payload)
2. `~/.hermes/skills/devops/security-guard/SKILL.md` — any curl/token pattern inside fenced code blocks showing example usage

## Steps

1. **Read memory.** Read `~/.hermes/memory/MEMORY.md` and today's `~/.hermes/memory/logs/${today}.md` (create if missing) for context.

2. **Bootstrap baseline.** If `~/.hermes/skills/skill-security-scan/scan-baseline.yml` does not exist, create it with the seed suppressions listed above and record `BASELINE_BOOTSTRAPPED` in the exit status.

3. **Resolve scope** per the `${var}` rules above. Log the chosen scope.

4. **Preflight scanner.** Verify `~/.hermes/skills/skill-security-scan/scan.sh` is present and executable. If missing, fall back to inline Grep using the same HIGH/MEDIUM/LOW pattern library defined in `scan.sh` — never silently skip.

5. **Run scanner in JSON mode** — invoke `scan.sh --all --json` (or with a specific path for scoped scans) and capture the structured output: `[{skill, status, file, high, medium, low}, ...]`. Do not parse stderr into findings.

6. **Code-fence downgrade.** For each finding, re-read the file around the finding's line. If the line is inside a fenced code block (between ` ``` ` markers in a Markdown file), downgrade severity by one tier (HIGH → MEDIUM, MEDIUM → LOW, LOW → drop).

7. **Apply baseline suppression.** Drop any finding whose (file, pattern, line) tuple is in `~/.hermes/skills/skill-security-scan/scan-baseline.yml`.

8. **Compute delta** against `~/.hermes/memory/state/security-scan.json` (previous run's finding set, keyed by `sha256(file+line_content+pattern)`):
   - **NEW** — findings present now but not last run
   - **RESOLVED** — findings present last run but gone now
   - **PERSISTENT** — findings in both runs (not re-notified, but still counted)

9. **File/close issues** in `~/.hermes/memory/issues/`:
   - For each NEW HIGH finding (post-suppression): create `~/.hermes/memory/issues/ISS-{next_id}.md` with YAML frontmatter (`id`, `title`, `status: open`, `severity: high`, `category: quality-regression`, `detected_by: skill-security-scan`, `detected_at: ${today}`, `affected_skills`) and append a row to `INDEX.md` under `## Open`.
   - For each RESOLVED finding that corresponds to an open ISS filed by `skill-security-scan`: set `status: resolved`, `resolved_at: ${today}`, move the row from `## Open` to `## Resolved` in `INDEX.md`.
   - Do NOT file issues for NEW MEDIUM or LOW findings — those live in the article report only.

10. **Write the report** to `~/.hermes/memory/articles/security-scan-${today}.md` only if there are any NEW, RESOLVED, or current HIGH findings. Structure:

    ```markdown
    # Security Scan — ${today}

    **Verdict:** [CLEAN | ATTENTION | DEGRADED]
    **Scope:** [full corpus | ${var}]
    **Counts:** N files scanned · H HIGH · M MEDIUM · L LOW · X new · Y resolved since last scan

    ## Needs attention (NEW high-severity this run)
    For each: file:line, pattern that matched, one-line remediation snippet (see table below).

    ## Resolved since last scan
    List of findings that disappeared — good for confirming fixes.

    ## Persistent findings (unchanged)
    Count per severity; full list only in the appendix.

    ## Per-file results
    Table: file, status (PASS/WARN/FAIL), HIGH count, MEDIUM count, LOW count.

    ## Appendix — all current findings
    Full structured dump.
    ```

11. **Remediation snippets.** For each HIGH finding, attach a one-line fix hint keyed off the pattern. Map (non-exhaustive — extend as new patterns are added to `scan.sh`):

    | Pattern category | Remediation |
    |---|---|
    | Shell eval / backticks / `$(...)` with variable | Quote the variable; prefer `${VAR}` with explicit quoting; replace `eval` with a function |
    | `curl`/`wget` with an env var in the URL or body | Move secret into a pre-fetch script; never interpolate secrets into shell-block strings |
    | Path-traversal sequence | Validate input against `~/.hermes/skills/*/` or explicit allow-list; reject absolute paths |
    | Prompt-override phrasing | If the string is documentation, add a baseline suppression entry; if it's a payload, delete it |
    | Recursive delete rooted at `/` or `~` | Scope to a specific subdir; never take a variable as the delete root |
    | Force-push to main | Remove the option or gate behind explicit human dispatch |
    | Obfuscation (zero-width / bidi / base64-decode pipe) | Delete unless there's a documented, reviewed reason |

12. **Persist state.** Write the full current finding set to `~/.hermes/memory/state/security-scan.json` so the next run can compute delta. Include `{generated_at, scope, findings: [{file, line, pattern, severity, fingerprint}]}`.

13. **Notify** via Slack `send_message` only when there is something new for the operator:
    - If any NEW HIGH finding → one paragraph summary naming affected skill(s), finding count, and path to the report.
    - If any RESOLVED HIGH finding (but no new HIGH) → short "Resolved: X HIGH findings cleared since last scan."
    - If only MEDIUM/LOW changes → skip notification (report is written, operator reads on demand).
    - If no findings and no delta → skip notification; emit `SECURITY_SCAN_OK` to stdout so heartbeat can log it.

14. **Log** to `~/.hermes/memory/logs/${today}.md` with an `### skill-security-scan` section: scope, exit status code, counts by severity, new/resolved counts, issue IDs filed, report path.

## Exit status codes

Emit exactly one to stdout (on its own line) before normal output:

- `SECURITY_SCAN_OK` — no findings after suppression, no delta
- `SECURITY_SCAN_NEW` — at least one NEW HIGH finding
- `SECURITY_SCAN_RESOLVED` — no new HIGH findings, but at least one was resolved
- `SECURITY_SCAN_NOCHANGE` — findings exist but identical to last run
- `SECURITY_SCAN_BOOTSTRAPPED` — baseline file was just created; this run writes initial state
- `SECURITY_SCAN_ERROR` — scope unresolvable, scanner missing, or write failure

## Constraints

- Never auto-delete a finding from `scan-baseline.yml`. Suppression is a human decision; the skill only *adds* seed entries on first bootstrap.
- Never file an issue for a finding that is already represented by an open ISS (match by fingerprint — file+line+pattern).
- Never change `scan.sh`'s pattern library from inside this skill. Pattern evolution happens in a separate, reviewed update.
- Never notify on a pure no-op week. Silence is correct when nothing has changed.

## Pitfalls

### scan.sh location mismatch
The `scan.sh` scanner script is installed from the aeon repo at `/root/aeon/skills/skill-security-scan/scan.sh`. At runtime, the skill looks for it at `~/.hermes/skills/skill-security-scan/scan.sh` — but this path often doesn't exist because aeon skills are synced to a different location (`~/.hermes/home/.hermes/skills/`). **Always check both paths** before falling back to inline grep. If neither exists, proceed with `search_files` (the agent's built-in grep tool) using the HIGH/MEDIUM/LOW pattern library defined above.

### Profile-qualified skill paths
Hermes stores runtime skills under `~/.hermes/home/.hermes/skills/` (profile-qualified), not just `~/.hermes/skills/`. When enumerating `SKILL.md` files, scan BOTH:
- `~/.hermes/skills/*/SKILL.md`
- `~/.hermes/home/.hermes/skills/*/SKILL.md`
Same for companion scripts: `*.sh` and `*.py` in both trees.

### Agent tool blocklist vs security patterns
Several HIGH/MEDIUM patterns (e.g., `mkfs`, `chmod 777`) match substrings that appear on the agent's hardline command blocklist. Shelling out to `grep -E` with these patterns will be **blocked by the agent runtime**. Use `search_files` (the agent's built-in content search) instead — it scans file contents without executing shell commands that contain blocked substrings. Split compound patterns into individual safe regexes if needed.

## VPS note

This skill reads local files and shells out to `scan.sh`; no network calls required. If `scan.sh` is unavailable, perform the scan inline using `search_files` with the same pattern library — never silently skip. The Slack `send_message` call uses the standard Hermes messaging integration.

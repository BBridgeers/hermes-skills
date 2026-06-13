---
name: External Feature
description: Proactively enhance watched repos — fix issues, add features, improve code
tags: [dev, build]
---

# External Feature — Proactive Repo Enhancement

> Adapted from Aeon's external-feature. Replaces `./notify` with Slack `send_message`, `gh` CLI fork/clone/PR flow with `git` on VPS, `memory/` paths with `~/.hermes/articles/`, and removes sandbox/var mechanics. Core methodology — pick a repo, understand it deeply, make one high-impact improvement — preserved.

## Goal

Proactively improve one of your watched GitHub repos each run. Pick the highest-impact, lowest-risk change: fix a bug, close an issue, add a missing test, or ship a small feature. One change per run. Small, high-quality commits > ambitious rewrites.

## Watched Repos

The skill reads `~/.hermes/skills/external-feature/watched-repos.md` for the list of repos to monitor. Format — one per line:

```
owner/repo  # optional comment about stack, purpose, opportunities
```

If the file doesn't exist, create it with at least one repo before running.

Also check `~/.hermes/logs/external-feature/` for recent runs to avoid re-working the same repo too frequently (skip repos enhanced in the last 7 days).

## Steps

### 1. Read context

Read `~/.hermes/skills/external-feature/watched-repos.md` for the repo catalog. If empty or missing, check these alternate locations before giving up: `~/.hermes/aeon/memory/watched-repos.md`, `~/aeon/memory/watched-repos.md`, `~/.hermes-backup/skills/external-feature/watched-repos.md`. If still none found, send `send_message "external-feature: no watched repos configured. Add repos to ~/.hermes/skills/external-feature/watched-repos.md"` and exit.

Check `~/.hermes/logs/external-feature/` for recent enhancements. Skip any repo worked on in the last 7 days.

Pick a repo that:
- Is actively maintained (recent commits)
- Has clear opportunities (open issues, TODOs, missing tests, feature gaps)
- Aligns with your current priorities
- Hasn't been enhanced recently

### 2. Clone and understand the repo

```bash
REPO="owner/repo"
WORK_DIR="/tmp/hermes-external-work"
rm -rf "$WORK_DIR"
git clone --depth 50 "git@github.com:${REPO}.git" "$WORK_DIR"
cd "$WORK_DIR"
```

Before making any changes, deeply understand the codebase:
- Read `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` if they exist
- Check the project structure, language, framework
- Read `package.json` / `Cargo.toml` / `pyproject.toml` / `go.mod` etc.
- Read recent commits: `git log --oneline -20`
- Check open issues on GitHub via `web_extract` on `https://github.com/${REPO}/issues`
- Check open PRs on GitHub via `web_extract` on `https://github.com/${REPO}/pulls`
- Understand the test setup if tests exist

### 3. Decide what to do

Pick ONE thing from this priority list:

**Priority 1 — Open issues** (if any exist):
- Fix a bug or implement a requested feature
- Prefer issues labelled `bug`, `enhancement`, `good-first-issue`, `help-wanted`

**Priority 2 — Code improvements** (if no good issues):
- Fix TODOs/FIXMEs in the code
- Add missing error handling for external API calls
- Add or improve tests for untested critical paths
- Fix security issues (exposed secrets, injection risks, outdated deps)
- Improve performance of obviously slow code

**Priority 3 — New features** (if codebase is clean):
- Add a useful feature that fits the project's purpose
- Improve DX (better README, CLI help, config validation)
- Add CI/CD if missing
- Add type annotations if project lacks them

Pick the highest-impact, lowest-risk change. One change per run.

### 4. Implement it

Write clean, production-ready code:
- Match the existing code style exactly — indentation, naming, patterns
- Include tests if the repo has a test suite
- Don't introduce new dependencies unless absolutely necessary
- Don't refactor unrelated code — stay focused on one improvement

### 5. Create a branch and commit

```bash
BRANCH="hermes/SHORT-DESCRIPTION"
git checkout -b "$BRANCH"
git add -A
git commit -m "TYPE: [description]

[optional body explaining why]"
```

Use conventional commit types: `fix:`, `feat:`, `test:`, `docs:`, `chore:`.
If fixing an issue, add `Closes #N` to the commit body.

### 6. Push changes

```bash
git push -u origin "$BRANCH"
```

**If push fails with "Permission denied":** you don't have write access to the upstream repo. Fork it first via `gh` CLI (no auth headers in prompt — avoids tirith scanner):

```bash
# Fork the repo via gh CLI (uses stored GITHUB_TOKEN automatically)
gh repo fork "$REPO" --clone=false 2>/dev/null || \
  gh repo fork "$REPO" --remote 2>/dev/null

# Then add your fork as a remote and push there
git remote add fork "git@github.com:${YOUR_USERNAME}/$(basename $REPO).git"
git push -u fork "$BRANCH"
```

If `gh` CLI is unavailable or `gh auth login` fails (limited-scope tokens), use `gh api` which authenticates via stored token without exposing auth headers in the prompt:

```bash
# Fork via gh api (token read from GH_TOKEN/GITHUB_TOKEN env or gh config)
gh api repos/${REPO}/forks -X POST

# Create PR via gh api (write body to file first to avoid shell escaping)
echo '{"title":"...","head":"YOUR_USERNAME:BRANCH","base":"main","body":"..."}' > /tmp/pr-body.json
gh api repos/${REPO}/pulls -X POST --input /tmp/pr-body.json
```

**If `gh repo fork` and `gh api` fork both return HTTP 403:** the token is authenticated but lacks the `repo` scope required for forking. This is common with fine-grained PATs that only have `read:org` or `workflow` scopes — they can read repos and push to branches the token owns but cannot create forks. Save the patch with `git format-patch` and document the fix in the article/log so a human can push it later. Do not silently discard the work.

```bash
# Save the patch for manual push
git format-patch main --stdout > ~/.hermes/articles/external-feature-$(date -u +%F).patch
```

**If no GitHub token is available at all**, same fallback: save the patch with `git format-patch`.

After a successful push, open a PR. Prefer `gh pr create --repo "$REPO" --head "${YOUR_USERNAME}:${BRANCH}" --title "..." --body "..."`. Fall back to `gh api` as above. The `--body-file` flag (`gh pr create --body-file /tmp/pr-body.json`) or `--input /tmp/pr-body.json` (gh api) avoid shell-escaping pitfalls and tirith scanner triggers.

### 7. Notify (skip if cron job)

**Interactive mode:** Send `send_message`:

```
🔧 external-feature: owner/repo — [what was done]
PR: [url]
```

**Cron mode:** Skip this step entirely. The system auto-delivers your final response — put the report content directly in your response. If nothing meaningful was done, respond with `[SILENT]` to suppress delivery.

### 8. Write article

Save a summary to `~/.hermes/articles/external-feature-YYYY-MM-DD.md`:

```markdown
# External Feature — YYYY-MM-DD

- **Repo:** owner/repo
- **What:** [description of enhancement]
- **PR:** [url]
- **Why:** [what prompted it — issue, TODO, proactive improvement]
- **Changes:**
  - [file-level summary of changes]
```

### 9. Log the run

Append to `~/.hermes/logs/external-feature/YYYY-MM-DD.md`:

```markdown
## External Feature
- **Repo:** owner/repo
- **What:** [description of enhancement]
- **PR:** [url]
- **Why:** [what prompted it]
```

## Prerequisites

- SSH key configured for GitHub (for `git clone git@github.com:...`)
- Git user.name and user.email configured
- `send_message` available for Slack notifications

## Guidelines

- ONE enhancement per run. Don't bundle multiple unrelated changes.
- Understand before you change. Read the codebase first. Don't guess at conventions.
- Match the repo's style. If they use tabs, use tabs. If they use semicolons, use semicolons.
- Small, high-quality changes > ambitious rewrites. A 10-line bug fix beats a 500-line refactor.
- If the repo has CI, make sure your changes won't break it.
- Never push to main/master. Always branch.
- If you can't find anything worth doing, that's fine. Log "repo is in good shape" and exit.
- Don't add unnecessary abstractions, comments, or documentation the repo doesn't need.
- Prioritize changes that make the project more useful, not just "cleaner."
- When debugging shell scripts with `set -euo pipefail` that exit silently, check for empty-array for-loop nounset traps on bash < 4.4. See `references/bash-nounset-empty-array.md`.
- When configuring cron jobs for this skill, avoid including raw HTTP request commands with embedded credentials in the prompt, as they trigger the tirith security scanner. Instead, use the web_extract tool or similar within the skill's steps to make HTTP requests. See `references/tirith-safe-http.md`.

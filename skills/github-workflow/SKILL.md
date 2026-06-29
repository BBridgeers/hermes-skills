---
name: github-workflow
description: DFW GitHub workflow SOP — commit SOPs, tag deliverables, and open auto-PRs for client handoffs.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, GitHub, Git, Workflow, SOP]
    related_skills: [dfw-web-design-now]
---

# GitHub Workflow

Commit, tag, and ship DFW deliverables through the `BBridgeers/hermes-skills` repo and client handoff repos.

## Pattern
Every DFW deliverable that is reusable or client-facing should land in a GitHub repo with a clean commit message, optional tag, and PR when handoff is to an external repo.

## Protocol

1. **Stage files** with `mcp_server_git_git_add` or shell `git add`.
2. **Commit** using convention:
   - `dfw(<client>): <what changed>` — e.g., `dfw(acme-hvac): add homepage spec build`
   - `sop(<skill>): <what changed>` — e.g., `sop(github-workflow): add PR template`
3. **Tag deliverables** when a phase gate completes: `git tag -a dfw/<client>/v<phase>-<date> -m "<message>"`
4. **Push** to the appropriate branch (`main` for hermes-skills, `client/<name>` for client repos).
5. **Auto-PR** for client handoffs using `mcp_github_create_pull_request` when a client repo branch is ready.
6. **Back-reference** the Taskwarrior task UUID and client-data record ID in the PR body.

## Commit Convention

| Prefix | Use Case | Example |
|---|---|---|
| `dfw(<client>):` | Client deliverable | `dfw(acme-hvac): homepage build v1` |
| `sop(<skill>):` | Skill/SOP change | `sop(build-executor): add Playwright gate` |
| `ops:` | Infra/config | `ops: add agent-graph node` |
| `docs:` | README/matrix | `docs: update MCP classification matrix` |

## Failure Modes
- Untracked deliverables in `/tmp` get lost on reboot.
- Generic commit messages make rollback impossible.
- Pushing to `main` on client repos skips review and breaks trust.

## Examples
```bash
# Commit a new DFW skill
git add skills/client-site-audit/SKILL.md
git commit -m "sop(client-site-audit): add pre-redesign audit SOP"
git push origin main

# Tag a completed client build
git tag -a dfw/acme-hvac/build-2026-06-29 -m "Build phase complete, ready for QA"
git push origin dfw/acme-hvac/build-2026-06-29
```

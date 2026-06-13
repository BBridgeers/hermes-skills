---
name: antigravity-cli-setup
description: Install and configure Google Antigravity CLI (agy) as a peer AI agent on the VPS alongside Hermes. Covers installation, skill ecosystem (antigravity-awesome-skills), bundle activation, and curated top-20 skill selection for Blake's stack.
version: 2
last-updated: 2026-05-27
triggered-by: Initial install (v1, 102 skills) + job-search expansion (v2, 136 skills) — discovered 8 job-specific skills (linkedin-automation, linkedin-cli, linkedin-profile-optimizer, ai-dev-jobs-mcp, interview-coach, jobgpt, hugging-face-jobs, jobs-to-be-done-analyst)
---

# Antigravity CLI Setup

Install, configure, and arm Google's Antigravity CLI (`agy`) as a peer coding agent on the VPS. agy runs alongside Hermes with its own skill ecosystem — the two agents should complement, not compete.

## Quick Install

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Installs to `/root/.local/bin/agy`. PATH is auto-appended to bashrc, zshrc, and profile.

## Core Modes

| Mode | Command | Use Case |
|---|---|---|
| Interactive TUI | `agy` | Full session |
| Non-interactive | `agy -p "prompt"` | One-shot, scriptable, cron-compatible |
| Continue | `agy -c` | Resume last conversation |
| Resume specific | `agy --conversation <id>` | Pick up a known session |
| Sandbox | `agy --sandbox` | Restricted terminal access |

## Skill Ecosystem

### Install the Awesome Skills Library

```bash
npx antigravity-awesome-skills --antigravity
```

This installs 1,470+ skills to `/root/.agents/skills/`. The GitHub repo is `sickn33/antigravity-awesome-skills` (38.8k stars).

### How Bundle Activation Works

The npx installer only copies skills — it does NOT include the activation scripts. For bundle activation, clone the full repo:

```bash
cd /tmp && git clone --depth 1 https://github.com/sickn33/antigravity-awesome-skills.git
```

Then activate bundles or individual skills:

```bash
# Activate bundles (clear existing active skills, then load bundle):
cd /tmp/antigravity-awesome-skills
bash scripts/activate-skills.sh --clear "Web Wizard" "DevOps & Cloud"

# Activate individual skills (append to existing):
bash scripts/activate-skills.sh skill-name-1 skill-name-2

# Append without clearing (layering):
bash scripts/activate-skills.sh "Python Pro"
```

The script uses a library/active split:
- **Library**: `~/.agents/skills_library/` — full copy of all 1,470 skills
- **Active**: `~/.agents/skills/` — subset copied from library
- `--clear` archives current active skills before loading new ones
- Without `--clear`, skills are layered on top

### Blake's Curated Pack (136 skills, 14 bundles)

Core packs for Blake's stack:
1. **DevOps & Cloud** — docker-expert, bash-linux, terraform-specialist, deployment-procedures
2. **Web Wizard** — react-best-practices, nextjs-best-practices, frontend-design, tailwind-patterns
3. **Python Pro** — python-pro, fastapi-pro, async-python-patterns, python-testing-patterns
4. **Full-Stack Developer** — senior-fullstack, api-patterns, database-design, stripe-integration
5. **Agent Architect** — mcp-builder, ai-agents-architect, agent-evaluation, prompt-engineering
6. **LLM Application Developer** — llm-app-patterns, rag-implementation, context-window-management
7. **QA & Testing** — browser-automation, e2e-testing-patterns, test-driven-development
8. **Security Engineer** — ethical-hacking-methodology, linux-privilege-escalation, vulnerability-scanner
9. **Security Developer** — api-security-best-practices, auth-implementation-patterns
10. **Startup Founder** — product-manager-toolkit, competitive-landscape, launch-strategy
11. **Marketing & Growth** — seo-audit, programmatic-seo, content-creator
12. **Skill Author** — skill-creator, skill-developer, writing-skills
13. **Documents & Presentations** — docx-official, pdf-official, pptx-official, xlsx-official
14. **Job Search & Career** — linkedin-automation, linkedin-cli, linkedin-profile-optimizer, ai-dev-jobs-mcp, interview-coach, jobgpt, hugging-face-jobs, jobs-to-be-done-analyst

Plus 22 standalone deep-cut skills (firecrawl-scraper, google-drive-automation, deep-research, etc.). See `references/top-20-deepcuts.md` for the full ranked analysis with domain breakdowns and activation commands.

## How Skills Are Invoked

In agy, skills are invoked by name:
```
@frontend-design help me with the Vehicle Analyzer cards
@deep-research analyze the DETOXXX protocol against industry standards
```

## Pitfalls

- **npx install doesn't include scripts**: The `npx antigravity-awesome-skills --antigravity` command only copies skill directories. For the activation scripts and bundle helpers, you must clone the full repo separately.
- **Bundle names must match exactly**: Bundle names are case-sensitive and must match what's in `docs/users/bundles.md`. Use quotes for multi-word names.
- **agy vs agy path**: After install, `agy` only works if `~/.local/bin` is in PATH. New SSH sessions get it automatically; existing sessions need `export PATH="$HOME/.local/bin:$PATH"`.
- **Gemini model note**: agy defaults to Gemini 3.5 Flash. Blake does NOT use Gemini for reasoning/coding tasks. Use agy for its skill ecosystem and browser/sandbox capabilities, not as primary reasoning engine.

## Verification

```bash
agy --version          # Should show installed version
ls /root/.agents/skills/ | wc -l   # Count active skills
```

## Supporting Files

- `references/top-20-deepcuts.md` — Full ranked analysis of the top 20 deep-cut skills with domain breakdowns, activation commands, and justification for each selection.

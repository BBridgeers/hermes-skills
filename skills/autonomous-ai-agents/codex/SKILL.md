---
name: codex
description: Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR reviews, and batch issue fixing. Requires the codex CLI and a git repository.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Codex, OpenAI, Code-Review, Refactoring]
    related_skills: [claude-code, hermes-agent]
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI API key OR Ollama running locally (see Ollama Proxy Mode below)
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

## Ollama Proxy Mode (Use Any Open-Weight Model)

Codex can run through Ollama's OpenAI-compatible API. Two paths:

### Path A: Local Ollama Proxy

```bash
ollama launch codex
ollama launch codex --model qwen3-coder:480b-cloud

# Manual: use --oss flag to auto-discover Ollama
codex --oss
codex --oss -m gpt-oss:120b-cloud
```

### Path B: Ollama Cloud Direct (API key — for headless VPS)

When the local Ollama isn't signed in, hit ollama.com directly. Add to `~/.codex/config.toml`:

```toml
[model_providers.ollama-cloud]
name = "Ollama Cloud"
base_url = "https://ollama.com/v1"

[profiles.cloud-coder]
model = "qwen3-coder:480b"
model_provider = "ollama-cloud"

[profiles.cloud-kimi]
model = "kimi-k2.6"
model_provider = "ollama-cloud"

[profiles.cloud-glm]
model = "glm-5.1"
model_provider = "ollama-cloud"

[profiles.cloud-gptoss]
model = "gpt-oss:120b"
model_provider = "ollama-cloud"

[profiles.cloud-dsv4pro]
model = "deepseek-v4-pro"
model_provider = "ollama-cloud"

[profiles.cloud-dsv4flash]
model = "deepseek-v4-flash"
model_provider = "ollama-cloud"
```

Set API key: `export CODEX_API_KEY="<ollama_api_key>"` (or embed in provider config)

Then run: `codex --profile cloud-coder "task description"`

### Pitfall: `--oss` downloads models locally

The `codex --oss` flag attempts to download the full model locally (e.g., 270GB for qwen3-coder:480b). For cloud models, always use `--profile <name>` with a cloud provider config instead. The `--oss` flag is for local Ollama instances that already have models pulled.

### Recommended Cloud Models (May 2026)

Coding-focused: `qwen3-coder:480b`, `kimi-k2.6`, `glm-5.1`, `gpt-oss:120b`, `deepseek-v4-pro`, `deepseek-v4-flash`, `minimax-m2.7`, `gemma4:31b`, `qwen3.5`, `nemotron-3-super`, `qwen3-coder-next`

Full catalog: `~/.hermes/skills/autonomous-ai-agents/pi/references/ollama-cloud-models.md`

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building** — auto-approves changes within the sandbox
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work

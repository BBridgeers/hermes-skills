---
name: pi
description: Delegate coding tasks to Pi CLI agent — a minimal extensible coding agent with a unique extension system and autonomous experiment loops (pi-autoresearch). Supports Ollama Cloud direct API.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Coding-Agent, Pi, Autonomous, Experiment-Loop, Optimization]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# Pi — Minimal Extensible Coding Agent

Delegate coding tasks to [Pi](https://github.com/badlogic/pi-mono) via the Hermes terminal. Pi is a lightweight coding agent with a unique extension system and autonomous experiment loops (`pi-autoresearch`). Its core tools are `read`, `write`, `edit`, and `bash` — all other capabilities come through extensions.

## When to Use

- Autonomous experiment loops (optimize test speed, bundle size, build time)
- Quick terminal coding sessions with minimal overhead
- Extension-based workflows (web search, custom tools)
- Tasks where Claude Code is blocked (root user) or Codex is downloading models

## Prerequisites

- Pi installed: `npm install -g @mariozechner/pi-coding-agent`
- Ollama running locally OR Ollama Cloud API key for cloud models
- Git repository for code tasks (recommended)

## Ollama Provider Configuration

Pi connects via OpenAI-compatible API. Config at `~/.pi/agent/models.json`:

### Local Ollama Proxy
```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [
        { "id": "qwen3-coder" },
        { "id": "qwen3-coder:480b-cloud" },
        { "id": "kimi-k2.6:cloud" }
      ]
    }
  }
}
```

### Ollama Cloud Direct (API key — for headless VPS)
```json
{
  "providers": {
    "ollama-cloud": {
      "baseUrl": "https://ollama.com/v1",
      "api": "openai-completions",
      "apiKey": "<ollama_api_key>",
      "models": [
        { "id": "qwen3-coder:480b" },
        { "id": "kimi-k2.6" },
        { "id": "glm-5.1" },
        { "id": "gpt-oss:120b" },
        { "id": "deepseek-v4-pro" },
        { "id": "deepseek-v4-flash" },
        { "id": "gemma4:31b" },
        { "id": "qwen3.5" },
        { "id": "minimax-m2.7" },
        { "id": "nemotron-3-super" },
        { "id": "qwen3-coder-next" }
      ]
    }
  }
}
```

Settings at `~/.pi/agent/settings.json`:
```json
{
  "defaultProvider": "ollama-cloud",
  "defaultModel": "qwen3-coder:480b"
}
```

Quick launch: `ollama launch pi` or `ollama launch pi --model qwen3.5:cloud`

## Extension System

Pi ships with 4 core tools: `read`, `write`, `edit`, `bash`. Everything else is an extension:

```
pi install npm:@foo/some-tools
pi install git:github.com/user/repo@v1
```

### Web Search Extension

```
pi install npm:@ollama/pi-web-search
```

When launched through Ollama, this is auto-installed.

### Pi-Autoresearch (Autonomous Experiment Loops)

[pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) is Pi's killer feature — autonomous optimization loops. It turns any measurable metric into an optimization target:

```
pi install https://github.com/davebcn87/pi-autoresearch
```

**How it works:**
1. Tell Pi what to optimize (test speed, bundle size, build time, Lighthouse scores, model training loss)
2. Pi runs experiments autonomously
3. Benchmarks each experiment
4. Keeps improvements, reverts regressions
5. Repeats until convergence or stop
6. Built-in dashboard tracks every run with confidence scoring
7. Each kept experiment is auto-committed; each failed one is reverted
8. When done, Pi groups improvements into independent branches for clean review/merge

**Usage:**
```
/autoresearch optimize unit test runtime
/autoresearch optimize bundle size
/autoresearch optimize build time
```

**From Hermes:**
```
terminal(command="pi -p '/autoresearch optimize test runtime'", workdir="~/project", background=true, pty=true)
```

## Interactive Sessions

Pi is an interactive terminal app:

```
terminal(command="pi", workdir="~/project", background=true, pty=true)
process(action="submit", session_id="<id>", data="Refactor the auth module")
process(action="poll", session_id="<id>")
```

## Manual Configuration (No ollama launch)

Add to `~/.pi/agent/models.json`:
```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "ollama",
      "models": [{ "id": "qwen3-coder" }]
    }
  }
}
```

`~/.pi/agent/settings.json`:
```json
{
  "defaultProvider": "ollama",
  "defaultModel": "qwen3-coder"
}
```

## Recommended Cloud Models (May 2026)

Coding-focused: `qwen3-coder:480b`, `kimi-k2.6`, `glm-5.1`, `gpt-oss:120b`, `deepseek-v4-pro`, `deepseek-v4-flash`, `minimax-m2.7`, `gemma4:31b`, `qwen3.5`, `nemotron-3-super`, `qwen3-coder-next`

Full list: `curl -s "https://ollama.com/search?c=cloud"` — also catalogued at `references/ollama-cloud-models.md`

## Pitfalls

- Pi extensions (`pi install`) may fail if npm isn't in PATH from the Hermes environment
- Pi is interactive — use `pty=true` for interactive sessions, or pass prompts directly
- The autoresearch module needs a measurable metric — qualitative goals won't work
- Cloud model names via direct API omit the `:cloud` suffix (e.g., `qwen3-coder:480b` not `qwen3-coder:480b-cloud`)

## Rules

1. Use Pi for experiment loops and optimization tasks — its unique strength
2. For general coding tasks, Claude Code or Codex may be more capable
3. Always verify the defaultProvider and defaultModel in settings.json before delegating
4. Pi is lighter than Codex/Claude Code — good for quick one-shot terminal tasks

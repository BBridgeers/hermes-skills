# Ollama Launch Ecosystem — Coding Agents & Integrations
*Source: docs.ollama.com — crawled 2026-05-21*

## `ollama launch` — One-Command Integration

Ollama v0.18+ provides `ollama launch <integration>` which auto-installs, configures, and launches coding agents using Ollama models as the backend. This eliminates manual env var configuration.

```
ollama launch                    # interactive selector
ollama launch <tool>             # specific integration
ollama launch <tool> --model X   # with specific model
ollama launch <tool> --config    # configure without launching
ollama launch <tool> --yes       # non-interactive (headless/CI)
```

## Supported Coding Agents

| Tool | Command | Install Method | Notes |
|---|---|---|---|
| **Claude Code** | `ollama launch claude` | curl install script | Anthropic-compatible API. Non-interactive: `--yes -- -p "prompt"` |
| **Codex CLI** | `ollama launch codex` | `npm install -g @openai/codex` | OpenAI-compatible API. Manual: `codex --oss -m model` |
| **Codex App** | `ollama launch codex-app` | macOS/Windows desktop app | Desktop coding agent. Has built-in browser + review mode |
| **Copilot CLI** | `ollama launch copilot` | brew/npm install | GitHub's agentic CLI. Manual: set `COPILOT_PROVIDER_BASE_URL` |
| **OpenCode** | `ollama launch opencode` | curl install script | Open-source terminal coding assistant |
| **Droid** | `ollama launch droid` | curl install script | Factory's AI coding agent. Config at `~/.factory/config.json` |
| **Goose** | GUI config | Desktop/CLI app | Block's extensible agent. Settings → Configure Provider → Ollama |
| **Pi** | `ollama launch pi` | `npm install -g @mariozechner/pi-coding-agent` | Minimal. Has extension system + autoresearch |
| **Pool** | `ollama launch pool` | Poolside install | Enterprise terminal agent. Env vars: `POOLSIDE_STANDALONE_BASE_URL` |

## Claude Code Manual Setup (Without ollama launch)

```bash
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
export ANTHROPIC_BASE_URL=http://localhost:11434
claude --model qwen3.5
```

Claude Code also supports:
- `/loop <interval> <prompt>` — scheduled recurring tasks
- Telegram bot integration via plugin
- Permission rules for autonomous operation

## Codex CLI Manual Setup

```bash
codex --oss                          # auto-detect Ollama models
codex --oss -m gpt-oss:120b          # specific model
codex --oss -m gpt-oss:120b-cloud    # cloud model
```

Profile-based (persistent) in `~/.codex/config.toml`:
```toml
[model_providers.ollama-launch]
name = "Ollama"
base_url = "http://localhost:11434/v1"

[profiles.ollama-launch]
model = "gpt-oss:120b"
model_provider = "ollama-launch"
```

## Copilot CLI Manual Setup

```bash
export COPILOT_PROVIDER_BASE_URL=http://localhost:11434/v1
export COPILOT_PROVIDER_API_KEY=
export COPILOT_PROVIDER_WIRE_API=responses
export COPILOT_MODEL=qwen3.5
copilot
```

## Droid Manual Setup

`~/.factory/config.json`:
```json
{
  "custom_models": [{
    "model_display_name": "qwen3-coder [Ollama]",
    "model": "qwen3-coder",
    "base_url": "http://localhost:11434/v1/",
    "api_key": "not-needed",
    "provider": "generic-chat-completion-api",
    "max_tokens": 32000
  }]
}
```

For cloud models: use `qwen3-coder:480b-cloud` as model, same base_url.

## Pi Extension System

Pi ships with 4 core tools (read, write, edit, bash). Extensions add capabilities:

```
pi install npm:@ollama/pi-web-search    # web search + fetch
pi install npm:@foo/some-tools          # any npm package
pi install git:github.com/user/repo@v1  # git-based extensions
```

[pi-autoresearch](https://github.com/davebcn87/pi-autoresearch) — autonomous experiment loops:
```
pi install https://github.com/davebcn87/pi-autoresearch
/autoresearch optimize unit test runtime
```

## IDE & Editor Integrations

| Tool | Integration Method | Notes |
|---|---|---|
| **VS Code** | `ollama launch vscode` | Copilot Chat ext 0.41.0+. Select "Local" in model picker |
| **Cline** | Settings → API Provider → Ollama | Min 32K context. Cloud: set base URL to `https://ollama.com` |
| **Roo Code** | Settings → API Provider → Ollama | Min 32K context |
| **JetBrains** | Settings → Local Models → Ollama | Requires JetBrains AI Subscription |
| **Xcode** | Settings → Locally Hosted → port 11434 | macOS only. Xcode 26.0+ |
| **Zed** | Star icon → Configure → Ollama | Host URL: `http://localhost:11434` |

## Assistants

| Tool | Command | Description |
|---|---|---|
| **Hermes Agent** | `ollama launch hermes` | Auto-installs via Nous Research script, configures provider, sets up gateway (Telegram/Discord/Slack/WhatsApp/Signal/Email) |
| **OpenClaw** | `ollama launch openclaw` | Personal AI assistant. Bridges messaging to coding agents. Has bundled Ollama web search. Previously "Clawdbot" |

## Hermes Agent Specific Integration (from Ollama Docs)

```
ollama launch hermes
```

What it does:
1. Installs Hermes Agent via Nous Research install script (if not present)
2. Launches model selector (local or cloud models)
3. Configures Ollama provider — points Hermes at `http://127.0.0.1:11434/v1`
4. Sets selected model as primary
5. Optionally connects messaging platform via `hermes gateway setup`
6. Launches Hermes chat

Manual setup alternative:
```
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```
Then in Hermes setup wizard: More providers → Custom endpoint → `http://127.0.0.1:11434/v1` (leave API key blank for local Ollama).

Hermes on Windows requires WSL2 (`wsl --install`).

## Chat & RAG

| Tool | Description |
|---|---|
| **Onyx** | Self-hosted Chat UI. Features: custom agents, web search, Deep Research, RAG over docs/connected apps (Google Drive, Email, Slack), MCP/OpenAPI actions, image generation, RBAC/SSO. Deploy via Docker |

## Automation

| Tool | Description |
|---|---|
| **n8n** | Visual workflow automation. Ollama node available for AI steps. Connect via Credentials → Ollama → Base URL `http://localhost:11434` |

## Notebooks

| Tool | Description |
|---|---|
| **marimo** | Interactive Python notebooks. Configure Ollama in Settings → AI tab → Base URL `http://localhost:11434/v1`. Supports inline code completion |

## Security Sandboxing

| Tool | Description |
|---|---|
| **NemoClaw** | NVIDIA's security stack for OpenClaw. Kernel-level sandboxing via OpenShell runtime. Network policy controls + audit trails. Requires Docker. Linux (Ubuntu 22.04+) primary. |

## Common Requirements Across Coding Agents

- **Context length**: All coding agents recommend ≥64K tokens (32K minimum for Cline/Roo Code)
- **Cloud models**: Set context to maximum by default — preferred over local for coding
- **Recommended coding models**: `kimi-k2.5:cloud`, `qwen3-coder:480b-cloud`, `glm-5:cloud`, `qwen3.5:cloud`
- **Non-interactive mode**: Most support `--yes` flag for CI/CD/headless use

---
name: hermes-agent
description: Complete guide to using and extending Hermes Agent — CLI usage, setup, configuration, spawning additional agents, gateway platforms, skills, voice, tools, profiles, and a concise contributor reference. Load this skill when helping users configure Hermes, troubleshoot issues, spawn agent instances, or make code contributions.
version: 2.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: [claude-code, codex, opencode]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-REDACTED agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL (to disk — permanent recovery)
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

**Permanent Session Recovery (when chat clears)**:

When your chat context vanishes — tab switch, browser refresh, "where were we?", "chat cleared" — use these commands to restore state:

```bash
# Export a session to disk (before or after context loss)
hermes sessions export --session-id <ID> /root/.hermes/pinned-sessions/<filename>.json

# List pinned sessions (always available)
ls -la /root/.hermes/pinned-sessions/

# Re-import in any new session
hermes sessions import /root/.hermes/pinned-sessions/<filename>.json
```

**Add to `~/.bashrc` for instant recovery**:
```bash
alias recovery='session_search(query="<project> <context>", limit=2, sort="newest")'
```

**Before ending a productive session**:
```bash
hermes sessions export --session-id $(hermes status | grep "Session ID" | cut -d: -f2 | tr -d ' ') \
  /root/.hermes/pinned-sessions/$(date +%Y%m%d_%H%M%S)_prod.json
echo "Context pinned: /root/.hermes/pinned-sessions/*_prod.json"
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/btw                 Ephemeral side question (doesn't interrupt main task)
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
~/.hermes/skills/           Installed skills
~/.hermes/plugins/          Installed plugins
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/memories/         Memory entries (MEMORY.md, USER.md)
~/.hermes/SOUL.md           Persona / identity / voice constraints
~/.hermes/models.json       Exported model catalog for workspace UI
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

See `references/docker-deployment.md` for Docker-specific path mappings and filesystem topology (bind mounts vs. named volumes).

See `references/models-json-sync.md` for syncing the CLI model catalog to workspace.
See `references/native-workspace-install.md` for native (bare-metal) deployment of Workspace + Dashboard with systemd services, Tailscale remote access, and model sync.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Community tap skills not indexing
`hermes skills tap add REPO` registers a tap in config, but `hermes skills update` does NOT fetch or clone the tap repos. You must manually clone them into `~/.hermes/skills/`:

```bash
cd ~/.hermes/skills/
git clone https://github.com/OWNER/REPO.git my_tap_name
hermes skills list  # should now show the new skills
```

Not all GitHub repos contain Hermes skills — they must have `SKILL.md` files in subdirectories. Repos like "awesome-hermes-agent" are curated lists (no SKILL.md), and repos like "hermes-plugins" may contain MCP servers (Python scripts) rather than skills. Check for SKILL.md files before assuming a repo has installable skills.

### Gateway not starting / restart loop

**Cause 1: Manual systemd unit file** — The gateway regenerates its unit on startup; mismatches trigger reloads that systemd escalates to SIGKILL.

Fix:
```bash
systemctl --user stop hermes-gateway
rm ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
hermes gateway install
hermes gateway start
```

**Cause 2: Git merge conflict in source code** — A `git stash` or `git merge` that left `<<<<<<< Updated upstream` / `=======` / `>>>>>>> Stashed changes` markers in a Python file under `~/.hermes/hermes-agent/` causes a `SyntaxError` on import. The gateway imports all platform adapters at startup, so even an unresolved conflict in `api_server.py`, `telegram.py`, or `slack.py` kills the entire process.

Symptom in logs:
```
File "/root/.hermes/hermes-agent/gateway/platforms/api_server.py", line 4112
    <<<<<<< Updated upstream
SyntaxError: expected 'except' or 'finally' block
```

Fix:
```bash
# Find conflict markers in gateway source
grep -rn '<<<<<<\|>>>>>>\|=======' ~/.hermes/hermes-agent/gateway/platforms/

# Edit the file, resolve the conflict (pick one branch, remove markers)
# Then restart
systemctl --user restart hermes-gateway
```

### Dashboard fails with Docker errors on native installs
On bare-metal (non-Docker) installs, `hermes dashboard` may fail with "No such container: hermes-agent". Use the Python module directly:

```bash
HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist \
  python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
```

Pre-build the web UI first: `cd /usr/local/lib/hermes-agent/web && npm install && npm run build`

### Workspace model dropdown only shows default model
The workspace reads available models from `~/.hermes/models.json`, but the CLI stores them in `config.yaml`. Sync models manually:
```python
import yaml, json
with open('/root/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)
models = []
# Extract from custom_providers, providers, fallback_providers...
# Write to ~/.hermes/models.json as [{"model": "...", "provider": "..."}]
```

See `references/native-deployment.md` for the full native VPS deployment topology.

```bash
# Add to the [Service] section of the service file:
# EnvironmentFile=/root/.hermes/.env

# Or via Python:
python3 -c "
with open('/root/.config/systemd/user/hermes-gateway.service', 'r') as f:
    content = f.read()
content = content.replace(
    'Environment=\"PATH=',
    'EnvironmentFile=/root/.hermes/.env\nEnvironment=\"PATH='
)
with open('/root/.config/systemd/user/hermes-gateway.service', 'w') as f:
    f.write(content)
"
systemctl --user daemon-reload
hermes gateway restart
```

After editing, restart: `hermes gateway restart`. Check logs: `journalctl --user -u hermes-gateway -f`

### Dashboard won't start (Docker container error)
`hermes dashboard` may fail immediately with `Error response from daemon: No such container: hermes-agent` on native (non-Docker) installs. The CLI wrapper hits a Docker check before reaching the dashboard code. Workaround:
```bash
# Build the web UI first:
cd /usr/local/lib/hermes-agent/web && npm install && npm run build

# Start dashboard directly (bypasses the Docker check):
HERMES_WEB_DIST=/usr/local/lib/hermes-agent/hermes_cli/web_dist \
  python3 -m hermes_cli.main dashboard --port 9119 --host 127.0.0.1 --skip-build --no-open
```

### Gateway restart loop (manual service file)
If you wrote the gateway systemd service file by hand, the gateway will overwrite it on every startup with `↻ Updated gateway user service definition`, triggering a systemd reload that restarts the gateway in a 5-minute loop. Fix: remove the manual service file and let the gateway install its own:
```bash
systemctl --user stop hermes-gateway
rm ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
hermes gateway install
hermes gateway start
```

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\\|error" ~/.hermes/logs/gateway.log | tail -20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires linger enabled via Windows service wrapper.
- **Gateway restart loop (SIGTERM→SIGKILL every 5 min)**: Caused by a hand-written systemd service file that doesn't match what `generate_systemd_unit()` produces. The gateway overwrites it, runs `systemctl daemon-reload`, and systemd cycles the service. Fix:
  ```bash
  systemctl --user stop hermes-gateway
  rm ~/.config/systemd/user/hermes-gateway.service
  systemctl --user daemon-reload
  hermes gateway install  # generates the correct service file
  ```

### Dashboard — Required for Workspace Features

The Hermes dashboard (`hermes dashboard --port 9119`) is a separate service from the gateway. It serves the web UI for models, config, sessions, skills, and cron management. **The Hermes Workspace web UI depends on the dashboard** — if port 9119 is down, the workspace model picker, config editor, sessions list, and settings screens are all silently disabled.

The dashboard and gateway are independent services:
- **Gateway (:8642)** — chat/completions, /health, tool execution
- **Dashboard (:9119)** — models, config, sessions, skills, cron, env vars

For native (non-Docker) deployments, the dashboard CLI may fail with a Docker container lookup error. Workaround: invoke the Python module directly with the web dist path set. Full procedure in `references/native-workspace-install.md`.

### Workspace Model Picker — Empty or Missing Models

The Hermes Workspace reads available models from `~/.hermes/models.json` (NOT from `config.yaml`). If this file is missing, only the gateway's default model appears. Format:
```json
[{"model": "deepseek-v4-pro", "provider": "deepseek"}]
```
Sync from `config.yaml` custom_providers + fallback_providers, or query live provider APIs (OpenRouter `/api/v1/models`, OpenCode `/zen/v1/models`, Google `/v1beta/models`). See `references/native-workspace-install.md` for the full sync recipe.

### Workspace Files Tab — File Not Visible

The workspace Files panel uses a **workspace selector** dropdown at the top. It does NOT automatically show the home directory. The user must explicitly select a root directory (e.g., `/root/`). When placing reference files for workspace access, put them at a top-level path the user can select, not buried in a project subdirectory.
For native (non-Docker) deployments, the dashboard may fail with a Docker container lookup error. Workaround: invoke the Python module directly with the web dist path set. Full procedure in the `hermes-onboard` skill, `references/native-workspace-install.md`.
When removing a provider (e.g., OpenRouter), check ALL these config sections:
```bash
# 1. Primary model routing
hermes config set model.provider ollama-cloud
hermes config set model.default deepseek-v3.1:671b

# 2. Custom providers section  
# Remove the unwanted provider entry

# 3. Fallback providers
# Remove fallback entries pointing to unwanted providers

# 4. Auxiliary services (check each)
hermes config set auxiliary.compression.provider ollama-cloud
hermes config set auxiliary.compression.model deepseek-v3.1:671b
hermes config set auxiliary.mcp.provider ollama-cloud  
hermes config set auxiliary.mcp.model qwen3-coder:480b
hermes config set auxiliary.session_search.provider ollama-cloud
hermes config set auxiliary.skills_hub.provider ollama-cloud
hermes config set auxiliary.approval.provider ollama-cloud

# 5. Remove quick commands referencing unwanted provider
# Check: hermes config | grep -A5 -B5 "quick_commands"
```

### Provider Preference Enforcement
To ensure consistent provider selection across all services:
```bash
# Set all services to explicit provider (disable 'auto')
hermes config set auxiliary.compression.provider ollama-cloud
hermes config set auxiliary.mcp.provider ollama-cloud
hermes config set auxiliary.session_search.provider ollama-cloud  
hermes config set auxiliary.skills_hub.provider ollama-cloud
hermes config set auxiliary.approval.provider ollama-cloud
hermes config set auxiliary.title_generation.provider ollama-cloud
hermes config set auxiliary.flush_memories.provider ollama-cloud
```

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Auxiliary models not working
If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set explicit provider configuration or check for complete provider removal:
```bash
# Check what provider 'auto' is falling back to
hermes config | grep -A3 -B3 "provider: auto"

# Set explicit provider instead
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

---

## Making Models Visible in Workspace

The workspace reads available models from `~/.hermes/models.json` — NOT from `config.yaml`. If models configured via `/model` in the CLI are missing from workspace dropdowns (Swarm → Add Agent → model picker), `models.json` either doesn't exist or is stale.

**Sync pattern:**
```bash
# Extract models from config.yaml + live API calls → models.json
python3 << 'PYEOF'
import yaml, json
with open('/root/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)

models = []
seen = set()

def add(provider, model):
    key = f"{provider}:{model}"
    if key not in seen:
        seen.add(key)
        models.append({"model": model, "provider": provider})

# Default model
m = config.get('model', {})
if isinstance(m, dict):
    add(m.get('provider', ''), m.get('default', ''))

# Custom providers (list of dicts with nested 'models' dicts)
for prov in config.get('custom_providers', []):
    pname = prov.get('name', '')
    if prov.get('model'):
        add(pname, prov['model'])
    for mid in (prov.get('models') or {}):
        add(pname, mid)

# Fallback providers
for prov in config.get('fallback_providers', []):
    if isinstance(prov, dict):
        add(prov.get('provider', ''), prov.get('model', ''))

with open('/root/.hermes/models.json', 'w') as f:
    json.dump(models, f, indent=2)
print(f"Wrote {len(models)} models")
PYEOF
systemctl --user restart hermes-workspace
```

**For live API models** (OpenRouter, OpenCode, Google), fetch from their `/v1/models` endpoints and merge into `models.json`. OpenRouter free models: filter on `pricing.prompt == "0"`. OpenCode Zen/Go: use the API keys from `.env`.

**Pitfall:** Adding models via `/model` in the CLI updates `config.yaml` only — `models.json` does NOT auto-sync. After model changes, re-run the sync. Consider a cron job if models change frequently.

## Where to Find Things

| Looking for... | Location |
|----------------|----------|
| Config options | `hermes config edit` or [Configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) |
| Available tools | `hermes tools list` or [Tools reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference) |
| Slash commands | `/help` in session or [Slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) |
| Skills catalog | `hermes skills browse` or [Skills catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog) |
| Provider setup | `hermes model` or [Providers guide](https://hermes-agent.nousresearch.com/docs/integrations/providers) |
| Platform setup | `hermes gateway setup` or [Messaging docs](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/) |
| MCP servers | `hermes mcp list` or [MCP guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) |
| Profiles | `hermes profile list` or [Profiles docs](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) |
| Cron jobs | `hermes cron list` or [Cron docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) |
| Memory | `hermes memory status` or [Memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) |
| Env variables | `hermes config env-path` or [Env vars reference](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) |
| CLI commands | `hermes --help` or [CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) |
| Gateway logs | `~/.hermes/logs/gateway.log` |
| Session files | `~/.hermes/sessions/` or `hermes sessions browse` |
| Source code | `~/.hermes/hermes-agent/` |

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Style & Output Expectations

**For this user:**
- VIN is a PRIMARY entry modality, not just one among many — treat it first in analysis
- Deliver data directly — dump the list/data, skip architecture narratives unless asked
- For UI/function validation: LIVE BROWSER TESTING — not code analysis, not theory
- Prefer concise output — no "Let me explain...", no "Here is the output:"
- When user says "test every button", literally test every button, document every result

## Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met

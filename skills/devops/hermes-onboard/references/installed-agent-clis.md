# Installed Agent CLIs on VPS

All coding agent CLIs available on srv1617682 (VPS_IP_REDACTED). Each can be invoked from the terminal for delegated tasks or comparison.

| CLI | Binary | Version | Install Path | Skills/Plugins Dir | Notes |
|---|---|---|---|---|---|
| Claude Code | `claude` | 2.1.146 | npm global | `~/.claude/skills/` | Anthropic's agent |
| Codex CLI | `codex` | 0.133.0 | npm global | `~/.codex/skills/` | OpenAI's agent |
| Pi | `pi` | 0.73.1 | npm global | `~/.pi/skills/` | Minimal extensible agent |
| OpenCode | `opencode` | 1.15.7 | npm global | `~/.opencode/skills/` | Open-source agent |
| Antigravity CLI | `agy` | 1.0.2 | `/root/.local/bin/agy` | `/root/.agents/skills/` | Google's agent (Gemini-backed) |

## Antigravity CLI (`agy`) — Quick Reference

- **Install**: `curl -fsSL https://antigravity.google/cli/install.sh | bash`
- **Interactive**: `agy`
- **Non-interactive**: `agy -p "prompt"` or `agy --print "prompt"`
- **Continue**: `agy -c` / `agy --continue`
- **Resume**: `agy --conversation <id>`
- **Sandbox**: `agy --sandbox` (restricted terminal)
- **Plugin import**: `agy plugin import gemini` or `agy plugin import claude`
- **Plugin marketplace**: `agy plugin install <name>@marketplace`

### antigravity-awesome-skills (installed 2026-05-27)

- **Repo**: github.com/sickn33/antigravity-awesome-skills
- **Installed at**: `/root/.agents/skills/` — 1,470 skills, v11.7.0
- **Install cmd**: `npx antigravity-awesome-skills --antigravity`
- **Bundle docs**: `/root/.agents/skills/` → `docs/users/bundles.md`
- **Activation**: `cd /root/.agents && ./scripts/activate-skills.sh --clear "Bundle Name"`

### Top bundles for this VPS's workload

| Bundle | Use Case |
|---|---|
| DevOps & Cloud | VPS admin, Docker, deployments |
| Web Wizard | Vehicle Analyzer (Next.js/React/Tailwind) |
| Python Pro | FB scraper, sweep pipeline, Hermes plugins |
| Agent Architect | Swarm management, MCP servers |
| Full-Stack Developer | veracar.co end-to-end |
| QA & Testing | Browser automation, E2E testing |
| Security Engineer | VPS hardening, vulnerability scanning |
| Startup Founder | Product strategy, competitive analysis |

## Integration Note

All five CLIs can run side-by-side on the VPS. Hermes delegates to them via `delegate_task` with the appropriate `acp_command` or by calling them directly in `terminal()`. Each has independent skill/plugin directories that don't conflict.

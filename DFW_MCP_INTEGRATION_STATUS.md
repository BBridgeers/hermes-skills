# DFW Web Design NOW — MCP Integration Status

> Auto-generated 2026-06-29. Tracks Hermes MCP server classification matrix implementation.

## Summary

| Layer | Target | Installed |
|---|---|---|
| Immediate MCP servers | 11 | 11 |
| Near-future MCP servers | 13 | 13 configured |
| Distant MCP servers | 10 | 10 configured |
| DFW skills | 13 | 13 |
| Agent graph nodes | 10 | 10 |

## Immediate MCP Servers (config.yaml)

All 11 servers are registered in `/root/.hermes/config.yaml`:

- `mcp_installer`
- `github`
- `server_git`
- `filesystem`
- `mcp_server_commands`
- `mcp_shell_server`
- `fetch_mcp`
- `website_downloader`
- `dbhub`
- `proposalcraft`
- `mcp_server_taskwarrior`

## DFW Skills (this repo)

| Skill | Wrapped Tools | Purpose |
|---|---|---|
| `github-workflow` | server-github + server-git | Commit/tag/PR convention for DFW deliverables |
| `build-executor` | mcp-server-commands + mcp-shell-server | Phase-gated Awwwards build pipeline |
| `competitor-research` | fetch-mcp | Competitor DOM/structure/token extraction |
| `client-site-audit` | website-downloader + fetch-mcp | Pre-redesign site mirror + tech audit |
| `debug-loop` | claude-debugs-for-you pattern | JS/TS breakpoint-evaluate-patch-verify cycle |
| `client-data` | bytebase/dbhub | SQLite schema for clients/projects/proposals/communications |
| `proposal-gen` | proposalcraft | Draft + review + format DFW proposals |
| `project-tracker` | mcp-server-taskwarrior | Phase-gate Taskwarrior templates |
| `cloudflare-deploy` | mcp-server-cloudflare | Pages deploy + DNS verification |
| `client-preview` | edgeone-pages-mcp | Shareable preview URL + review email |
| `design-asset-gen` | imagen3-mcp + openai-gpt-image-mcp | Industry-aware image prompt library |
| `client-onboarding-automation` | pipedream | Intake → CRM → invoice → welcome → kickoff task |
| `lead-qualification` | mcp-gtm-suite | Tech stack + ICP scoring for DFW prospects |

## Agent Graph Nodes

Declared in `agent-graph/graph.yaml`:

| Node | Powered By | Status |
|---|---|---|
| `filesystem-node` | server-filesystem | immediate |
| `shell-execution-node` | mcp-server-commands | immediate |
| `web-fetch-node` | fetch-mcp | immediate |
| `data-layer-node` | bytebase/dbhub | immediate |
| `deployment-node` | cloudflare/mcp-server-cloudflare | near-future |
| `monitoring-node` | server-sentry | near-future |
| `qa-security-node` | qianniuspace + semgrep | near-future |
| `client-isolation-node` | mcp-server-multiverse | near-future |
| `aggregator-node` | 1mcp/agent | distant |
| `management-plane-node` | metatool-ai/metatool-app | distant |

## Required Environment Variables

The following env vars must be set in `/root/.hermes/.env` (or system env) for near-future/distant servers to function:

```bash
CLOUDFLARE_API_TOKEN=
SENTRY_AUTH_TOKEN=
GRAFANA_URL=
GRAFANA_API_KEY=
EDGEONE_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
PIPEDREAM_API_KEY=
GTM_SUITE_API_KEY=
VIRUSTOTAL_API_KEY=
LOGFIRE_TOKEN=
SHODAN_API_KEY=
TFMCP_API_KEY=
```

## Notes

- Servers requiring credentials are configured but will not start until env vars are populated.
- `sakura-mcp` is skipped per the matrix.
- The `mcp-security-audit` matrix row appears twice (npm audit + semgrep); both functions are represented by the single `security_audit` server config plus the `qa-security-node` in the agent graph.

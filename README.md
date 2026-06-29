# Hermes Skills Repository

**372 AI agent skills** exported from a production Hermes Agent deployment.  
Exported: 2026-06-13  
Skills cleaned of all secrets, API keys, tokens, and credentials.

## What Are These?

These are `SKILL.md` files — executable procedural memory for the [Hermes Agent](https://hermes-agent.nousresearch.com/) by Nous Research. Each skill contains:

- **Trigger conditions** — when to load this skill
- **Step-by-step protocols** — exact commands and workflows
- **Pitfalls and failure modes** — what breaks and how to fix it
- **References** — supporting scripts, templates, and documentation

## DFW Web Design NOW Integration

This repo now hosts the DFW Web Design NOW MCP integration:

- **13 DFW skills** under `skills/` (e.g., `build-executor`, `client-data`, `proposal-gen`)
- **Agent graph** at `agent-graph/graph.yaml` with 10 dependency nodes
- **Integration status** in `DFW_MCP_INTEGRATION_STATUS.md`

These skills wrap MCP tools from the DFW classification matrix into executable SOPs.

## Categories

|| Domain | Count |
|---|---|---|
|| DevOps & Infrastructure | ~70 |
|| Software Development | ~65 |
| Research & Deep Research | ~25 |
| Autonomous AI Agents | ~20 |
| Marketing & GTM | ~15 |
| ML Ops & AI Engineering | ~15 |
| Code Review & QA | ~15 |
| Social Media & Scraping | ~15 |
| Productivity & Business | ~15 |
| Creative & Design | ~12 |
| Security & Threat Modeling | ~10 |
| Career & Job Search | ~10 |
| GitHub Workflows | ~8 |
| Communication & Messaging | ~8 |
| Housing & Real Estate | ~6 |
| Vehicle & Marketplace | ~5 |
| Gaming | ~5 |
| Smart Home | ~3 |
| Media & Music | ~3 |
| Other | ~40+ |

## Usage

These skills work with [Hermes Agent](https://github.com/NousResearch/hermes-agent). To use:

```bash
# Install Hermes Agent
pip install hermes-agent

# Copy skills to your skills directory
cp -r skills/* ~/.hermes/skills/

# Or symlink for live updates
ln -s $(pwd)/skills/* ~/.hermes/skills/
```

Then in any Hermes session, skills auto-load based on trigger conditions matching your task.

## Notes

- **372 active skills** (22 archived skills excluded from export)
- All API keys, passwords, usernames, and IP addresses have been redacted
- `.archive/`, `.curator_backups/`, and internal tracking files excluded
- These represent a real production deployment with battle-tested patterns

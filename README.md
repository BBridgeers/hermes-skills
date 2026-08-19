# Hermes Skills — Unified Knowledge Base

**The complete portable Hermes Agent corpus:** 372 production skills, research documentation across 13 domains, and a 60-agent AV1 Swarm workforce — all in one repo.

Merged 2026-08-19 from three repositories:
- `hermes-skills` — 372 production SKILL.md files (the skill library)
- `hermes-agent-base` — 13 research docs cataloging 163 authored skills + ~600 research findings (the knowledge index)
- `hermes-av1-workforce` — 60-agent swarm profiles, per-agent core prompts, swarm.yaml generator (the workforce layer)

---

## Repository Layout

```
hermes-skills/
├── README.md                          ← this file
├── README-agent-base.md               ← original hermes-agent-base README (legend + index)
├── DFW_MCP_INTEGRATION_STATUS.md      ← DFW Web Design NOW integration status
├── skills/                            ← 372 production SKILL.md files (262 items: dirs + loose .md)
├── agent-graph/
│   └── graph.yaml                     ← DFW dependency graph (10 nodes)
├── docs/                              ← Research documentation (from hermes-agent-base)
│   ├── 00-master-inventory.md         ← ★ COMPLETE corpus: all 163 installed skills + research finds, deduped
│   ├── 01-osint.md                    ← OSINT: tools, skills, dossiers
│   ├── 02-red-team.md                 ← Red teaming: C2, frameworks, skills
│   ├── 03-frontend-backend.md         ← Design, performance, code execution
│   ├── 04-security.md                 ← Hardening, auditing, scanning
│   ├── 05-agentic-workflow.md         ← Agent design, orchestration, workflows
│   ├── 06-music-production.md         ← Music/beat creation
│   ├── 07-capability.md               ← Generic capability primitives (scraping, testing, MCP builder)
│   ├── 08-research-vault.md           ← RAW master list of every discovered tool/MCP
│   ├── 09-claude-adaptation.md        ← ★ Claude/Codex/OpenCode skills + adaptation playbook
│   ├── 10-top-tier-remaining.md       ← ★ Finance/ML/creative/marketing/legal/web3/health best-of
│   ├── 11-curated-per-domain.md       ← ★ Top 20–30 per domain (8 domains) — deep-sweep curated
│   └── 12-travel-hotel-car-rental.md  ← ★ Travel, hotel, car rental & discount/deal skills + MCPs
└── av1-workforce/                     ← AV1 Swarm Workforce (standalone, unmodified)
    ├── AGENT_GUIDE.md
    ├── README.md
    ├── hermes-agents/                 ← 60 agent markdown profiles in 8 pod dirs
    ├── skills/                        ← 60 per-agent core skill files (*-core.md)
    ├── scripts/
    │   └── generate_swarm.py          ← CSV → swarm.yaml generator
    └── swarm-agents.csv               ← canonical 60-agent roster
```

---

## What Are These?

### skills/ — The Skill Library

`SKILL.md` files — executable procedural memory for the [Hermes Agent](https://hermes-agent.nousresearch.com/) by Nous Research. Each skill contains:

- **Trigger conditions** — when to load this skill
- **Step-by-step protocols** — exact commands and workflows
- **Pitfalls and failure modes** — what breaks and how to fix it
- **References** — supporting scripts, templates, and documentation

### docs/ — The Knowledge Index

Research documentation compiled from a full research + authoring session (2026-08-17): GitHub API hunts across 4 domains (OSINT, Red Teaming, Frontend/Backend Design & Performance, Security, Agentic Workflow, Music Production), the official NousResearch/hermes-agent skill hub, and starred-repo clones. Every item is verified to exist — either authored into the skills library or captured as a research finding with its source URL.

**Start with `docs/00-master-inventory.md`** — it is the complete, deduplicated corpus. See `README-agent-base.md` for the full legend and category index.

### av1-workforce/ — The Swarm Workforce

A production-ready 60-agent identity repository for the Hermes Agent Swarm. Contains:

- **60 agent markdown profiles** with full expanded schemas (Role, Model, Purpose, Responsibilities, Inputs, Outputs, Tools, Coordination & Handoffs, Guardrails, Failure Modes, Core System Instructions)
- **60 per-agent skill files** (`*-core.md`) with long-form system prompts
- **swarm-agents.csv** — canonical roster for bulk swarm.yaml generation
- **generate_swarm.py** — reads CSV → installs skills → generates swarm.yaml

| Pod | Agents | Purpose |
|-----|--------|---------|
| Core Command | 4 | Global routing, coordination, workspace management |
| Technical Core | 11 | Code, review, QA, knowledge, research, strategy |
| Knowledge & Strategy | 12 | Research, analysis, critique, synthesis, security |
| Startup & Ideation | 14 | Business creation, validation, experiments, launch |
| Communications | 5 | Email/LinkedIn triage, replies, follow-ups, automation |
| Vehicle Pod | 2 | VeraCar operations, vehicle sourcing |
| Career Pod | 6 | Job discovery, resume, applications, interviews, offers |
| Housing Pod | 6 | Rental sourcing, landlord fit, packets, outreach, coordination |

---

## DFW Web Design NOW Integration

This repo hosts the DFW Web Design NOW MCP integration:

- **13 DFW skills** under `skills/` (e.g., `build-executor`, `client-data`, `proposal-gen`)
- **Agent graph** at `agent-graph/graph.yaml` with 10 dependency nodes
- **Integration status** in `DFW_MCP_INTEGRATION_STATUS.md`

---

## Dedup Notes

- `hermes-agent-base` contained **only docs/** (no skill files) — zero overlap with `skills/`. Merged as `docs/` + `README-agent-base.md`.
- `hermes-av1-workforce/skills/` had 60 `*-core.md` files, **59 of which were already in `hermes-skills/skills/`** (identical content). The 1 difference (`task-orchestrator-core.md`) was a redaction artifact in the skills repo (`task-REDACTED` vs `task-orchestrator`). The av1-workforce copy is the unredacted original. The workforce is preserved as a standalone subfolder per the merge requirement — nothing edited or removed.
- No skills were deleted or modified during the merge.

---

## Usage

```bash
# Clone
git clone https://github.com/BBridgeers/hermes-skills.git
cd hermes-skills

# Install skills to Hermes
cp -r skills/* ~/.hermes/skills/

# Or symlink for live updates
ln -s $(pwd)/skills/* ~/.hermes/skills/

# Deploy the AV1 Swarm
cd av1-workforce
python3 scripts/generate_swarm.py
```

Then in any Hermes session, skills auto-load based on trigger conditions matching your task.

---

## Notes

- **372 active skills** (22 archived skills excluded from original export)
- All API keys, passwords, usernames, and IP addresses have been redacted
- `.archive/`, `.curator_backups/`, and internal tracking files excluded
- These represent a real production deployment with battle-tested patterns
- **Never push secrets.** This repo is public. API keys live in `~/.hermes/.env`, never in skills.
- **The 60-char rule.** Hermes rejects skill descriptions >60 chars.
- **MCP servers need config.** Items marked `[MCP]` in docs/ require `setup_mcp` consent + API keys.
- **Authorized use only.** All offensive-security skills carry an authorized-use constraint.
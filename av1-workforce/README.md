# Hermes AV1 Swarm Workforce

Complete 60-agent workforce for the Hermes Agent Swarm — designed for Blake's multi-pod autonomous operations.

## What This Is

A production-ready agent identity repository containing:
- **60 agent markdown profiles** with full expanded schemas (Role, Model, Purpose, Responsibilities, Inputs, Outputs, Tools, Coordination & Handoffs, Guardrails, Failure Modes, Core System Instructions)
- **60 per-agent skill files** (`<worker-id>-core.md`) with long-form system prompts ready for Hermes skill loading
- **swarm-agents.csv** — canonical roster for bulk swarm.yaml generation
- **generate_swarm.py** — Python script that reads CSV → installs skills → generates swarm.yaml

## Pod Structure

| Pod | Agents | Purpose |
|-----|--------|---------|
| **Core Command** | 4 | Global routing, coordination, workspace management |
| **Technical Core** | 11 | Code, review, QA, knowledge, research, strategy |
| **Knowledge & Strategy** | 12 | Research, analysis, critique, synthesis, security |
| **Startup & Ideation** | 14 | Business creation, validation, experiments, launch |
| **Communications** | 5 | Email/LinkedIn triage, replies, follow-ups, automation |
| **Vehicle Pod** | 2 | VeraCar operations, vehicle sourcing |
| **Career Pod** | 6 | Job discovery, resume, applications, interviews, offers |
| **Housing Pod** | 6 | Rental sourcing, landlord fit, packets, outreach, coordination |

## Quick Deploy

```bash
# 1. Clone the repo
git clone https://github.com/BBridgeers/hermes-av1-workforce.git
cd hermes-av1-workforce

# 2. Generate swarm.yaml and install skills
python3 scripts/generate_swarm.py

# 3. Restart Hermes Workspace
systemctl --user restart hermes-workspace

# 4. Verify at http://187.127.254.195:3100/swarm
```

## Design Philosophy

- **Skill-based per-agent prompts** — system prompts live in skills, referenced by `swarm.yaml`, not patched into backend schemas
- **Identity-first** — markdown profiles are the source of truth; swarm.yaml is a build artifact
- **Disaster recovery** — clone repo, run generator, swarm is rebuilt
- **Cross-platform** — same markdown profiles adapt to non-Hermes systems (OpenSwarm, CrewAI, vLLM)

## Model Selection

Every agent has an individually optimized model from Blake's 126-model inventory, chosen by role type:
- Orchestration/planning: `gpt-5.5-pro`, `claude-opus-4-7`
- Code/repo: `gpt-5.3-codex`, `gpt-5.1-codex-max`
- Fast triage/lightweight: `claude-haiku-4-5`, `gpt-5.4-mini`, `gemini-3-flash`
- Research/synthesis: `claude-opus-4-6`, `gemini-3.1-pro`
- Search/sourcing: `gemini-3.1-pro`, `gpt-5.5`

## Phased Deployment

1. Command Layer: Orchestrator, Chief of Staff, Task Orchestrator
2. Technical Core: Builder, Maintainer, Reviewer, QA, Workspace Steward
3. Communications: Comms Triage, Draft Reply, Follow-Up Nudge, Process Automation
4. High-Urgency Pods: Housing, Career, Vehicle
5. Strategy/Research/Startup expansion

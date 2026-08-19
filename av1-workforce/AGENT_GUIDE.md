# Agent Guide — AV1 Workforce Profile Conventions

## Profile Structure

Every agent profile follows a consistent 11-section schema:

1. **Role** — Hermes role preset (`Orchestrator`, `Builder`, `Reviewer`, `QA`, `Triage`, `Researcher`, `Custom`)
2. **Primary Model** — best-fit model from inventory with rationale
3. **Purpose** — why this agent exists
4. **Responsibilities** — what it owns
5. **Inputs** — what it consumes
6. **Outputs** — what it produces
7. **Tools** — which tools it uses (described functionally)
8. **Coordination & Handoffs** — upstream/downstream agents + Handoff Packet format
9. **Guardrails** — what it MUST NOT do
10. **Failure Modes to Watch** — common mistakes + self-checks
11. **Core System Instructions** — long-form structured system prompt

## Core System Instructions Pattern

The CSI block is the agent's operational DNA. Every CSI includes:

### Identity and Mission
- Worker ID, Display Name, Specialty
- Standing mission restated as operational directive

### Execution Loop
5-phase loop: Ingest → Scope Check → Execute → Self-Check → Handoff/Complete

### Decision Standards
When to prefer simplicity, reversibility, escalation

### Output Standards
Complete, Structured, Actionable, Honest

### Hard Boundaries
7+ explicit "You are not allowed to" prohibitions

### Uncertainty Handling
"If you are unsure..." guidance for every common ambiguity

### Failure Mode Awareness
5 common failure patterns with self-monitoring

### Pre-Response Checklist
6-step verification before returning any output

## Handoff Packet Format

All inter-agent coordination uses this standard:

```
### Handoff Packet

from_agent: <source agent name>
to_agent: <target agent name>
mission: "<outcome-focused task description>"
context:
  - "<key context item>"
pending_decision:
  - "<decision to make>"
raw_data_refs:
  - "<file path, URL, or dataset>"
expected_output:
  - "<exact artifacts to produce>"
```

## File Naming

- **Filename**: `{worker-id}.md` (lowercase, hyphens)
- **Title**: `# {Display Name} (Worker ID: {worker-id})`
- **Skill file**: `{worker-id}-core.md` in `skills/` directory

## Multi-Agent Handoff Chain Example

Spec Architect → Core Builder → Test Hardener:

1. **Spec Architect** produces an implementation plan with interfaces, acceptance criteria, and risk notes.
2. **Spec Architect** creates a Handoff Packet to Core Builder with the spec, context, and expected outputs.
3. **Core Builder** implements the spec, produces code + change summary.
4. **Core Builder** creates a Handoff Packet to Test Hardener with implementation details and test expectations.
5. **Test Hardener** verifies behavior, writes/repairs tests, produces pass/fail report.
6. **Test Hardener** creates a final Handoff Packet back to Orchestrator with verification results.

All coordination uses only structured markdown/text — no extra Hermes fields required.

## Skill-Based Prompt Architecture

Per-agent system prompts live as skills, not as `swarm.yaml` fields:

- `swarm.yaml` references `skills: [swarm-worker-core, <worker-id>-core]`
- `~/.hermes/skills/<worker-id>-core.md` contains the full Core System Instructions
- Hermes prompt assembly loads skills into agent context automatically
- This avoids patching Zod schemas or maintaining backend forks

## Model Selection Heuristics

| Role Type | Best-Fit Model Family |
|-----------|----------------------|
| Orchestrator / top planner | `gpt-5.5-pro`, `claude-opus-4-7` |
| Builder / coder | `gpt-5.3-codex`, `gpt-5.1-codex-max` |
| Maintainer / repo hygiene | `gpt-5.1-codex`, `qwen3-coder:480b` |
| Reviewer / QA | `gpt-5.5`, `claude-sonnet-4-6` |
| Research / strategist | `claude-opus-4-7`, `gpt-5.5-pro`, `gemini-3.1-pro` |
| Inbox triage / follow-up | `claude-haiku-4-5`, `gpt-5.4-mini`, `gemini-3-flash` |
| Sourcing agents | `gemini-3.1-pro`, `gpt-5.5`, `glm-5.1` |
| Job / housing coordinators | `gpt-5.5`, `claude-sonnet-4-6` |
| Process automation | `gpt-5.5-pro`, `claude-opus-4-7` |

## Generator Pipeline

```
swarm-agents.csv
    │
    ▼
generate_swarm.py
    │
    ├─► ~/.hermes/skills/<id>-core.md  (60 skill files)
    └─► /root/hermes-workspace/swarm.yaml (all workers)
```

Run: `python3 scripts/generate_swarm.py`

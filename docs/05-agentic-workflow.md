# 05 — Agent / Agentic & Workflow Design

**Scope:** multi-agent frameworks, workflow design, agent orchestration, skill-authoring methodology.
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## ✅ Authored Skills (installed)

| Skill | Category | Description | Source |
|---|---|---|---|
| `effective-agent-skills` | meta | **The gold standard** — verbatim davidondrej authoring methodology (323 lines). | davidondrej/skills |
| `hermes-agent` | autonomous-ai-agents | Use, configure, theme, extend, orchestrate Hermes Agent (18 references). | HUB |
| `hermes-auxiliary-model-routing` | autonomous-ai-agents | Allocate auxiliary tasks to optimal models. | HUB |
| `merge-reconciler` | autonomous-ai-agents | Neutral third-party resolution of agent merge conflicts. | HUB |
| `context-engineering` | software-development | Engineer context for AI coding agents. | STARS (addy) |
| `spec-driven-development` | software-development | Write a spec before code. | STARS (addy) |
| `plan` | software-development | Write a markdown plan; no execution. | HUB |
| `claude-code` / `codex` / `opencode` | autonomous-ai-agents | Delegate coding to external agent CLIs. | HUB |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

### Frameworks (reference — install as tools, not skills)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `openai/openai-agents-python` | 28,724 | Canonical multi-agent workflow framework | HIGH (ref) |
| `HKUDS/nanobot` | 47,100 | Ultra-lightweight self-hosted personal AI agent | MED (ref) |
| `deepset-ai/haystack` | 26,234 | Production LLM orchestration | LOW (ref) |
| `microsoft/agent-framework` | 12,854 | Multi-agent build/orchestrate/deploy | LOW (ref) |
| `The-Pocket/PocketFlow` | 11,108 | 100-line LLM framework — agents build agents | MED (ref) |
| `google-labs-code/stitch-skills` | 8,082 | Agent Skills for Stitch MCP server | MED |

### Workflow Design Skills (authorable)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `AkoliteZA/hermes-agent-idea-workflow` | 259 | **Hermes-native**: idea → design doc → spec → summary | **TOP** |
| `cosmicstack-labs/mercury-agent-skills` | 368 | Curated registry for Mercury/OpenClaw/**Hermes** workflows | TOP |
| `itgoyo/hermes-skills` | 43 | **310+ Hermes Agent Skills** catalog | HIGH |
| `appautomaton/agent-designer` | 131 | Issue-driven workflow design, cross-agent | HIGH |
| `sdi2200262/agentic-project-management` | 2,386 | Spec-driven multi-agent project mgmt | MED |
| `product-on-purpose/pm-skills` | 543 | 68 product-management skills for agents | MED |
| `wcgomes/agents-workspace` | 9 | Lightweight agents+skills workspace | LOW |
| `HsienW/ai-agent-coding-solution-kit` | 42 | Agent design, OpenSpec/SDD, context engineering | LOW |
| `preangelleo/workflow-design-bible` | 34 | Constitution generator for agent-run projects | LOW |
| `self-improve` (aeon) | — | Agent self-improvement loops | LOW |

---

## 🧩 MCP Servers (Agent/Workflow)

| Repo | ★ | What it gives | Key? |
|---|---|---|---|
| `stacklok/toolhive` | 2,023 | Enterprise MCP server management platform | No |
| `INQUIRELAB/mcp-bridge-api` | 67 | LLM-agnostic proxy to multiple MCP servers | No |
| `cyanheads/mcp-ts-core` | 147 | Agent-native TS framework for building MCP servers | No |

---

## ⚠️ Notes
- **`effective-agent-skills` is non-negotiable**: every skill in this base was authored to it. Future skills MUST follow it (description ≤60 chars, name==folder, one concern).
- The frameworks list is reference-only — you already run Hermes as your agent runtime; don't install competing frameworks unless a task demands it.
- `hermes-agent-idea-workflow` is the highest-value *native* addition for workflow design.

## 🔑 The Gold Standard (reproduced here for portability)

```
name: effective-agent-skills
description: "Author effective agent skills. Use when writing SKILL.md."

Rules (from davidondrej/skills effective-agent-skills):
1. Description routes; body executes. What+when+differentiator, ≤60 chars, ends with period.
2. Tokens scarce, files cheap → progressive disclosure (references/ loaded on demand).
3. Determinism from code; judgment from prompts.
4. One skill, one concern. Composition beats bundling.
5. Agents have no memory → persistent artifacts (ADRs, CONTEXT.md).
6. Don't re-teach what the model knows.
7. Validate before completing (verify → fix → re-verify loops).
8. Skills are code — version, test, audit, review.
```

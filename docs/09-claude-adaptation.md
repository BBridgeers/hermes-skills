# 09 — Claude / Codex / OpenCode Skill Adaptation Layer

> ## 🏆 THE SOLE GOLD STANDARD OF SKILL AUTHORING (READ FIRST)
>
> **Every skill in this corpus — and every skill authored now or in the future — MUST be authored per the
> `effective-agent-skills` methodology by David Ondrej (davidondrej/skills).**
>
> **The process is:**
> 1. **CLONE FIRST** — `git clone https://github.com/davidondrej/skills.git` (or copy from
>    `~/.hermes/skills/meta/effective-agent-skills/`, the verbatim 323-line clone already installed).
> 2. **THEN AUTHOR** using that methodology. Non-negotiable rules:
>    - `name` = folder name, lowercase-hyphens, 1–64 chars, matches exactly
>    - `description` ≤ **60 chars**, trigger-first, ends with period (what + when + differentiator)
>    - One skill = one concern (compose, never bundle)
>    - Progressive disclosure: SKILL.md lean, detail in `references/` loaded on demand
>    - Bash-first, prose-second; determinism in scripts, judgment in prompts
>    - Validation loops (verify → fix → re-verify); state-check before action
>    - Relative paths only; no time-sensitive info; no human-facing docs inside skill folder
>    - No secrets, no absolute paths, no re-teaching what the model already knows
> 3. **Verify** — description ≤60, name==folder, YAML parses, loads via `skills_list`.
>
> **This document catalogs Claude/Codex/OpenCode-oriented skills so a Hermes agent can CLONE → ADAPT → AUTHOR them
> using the gold standard. Nothing here is used verbatim without adaptation.**

---

**Scope:** Every skill, plugin, and MCP server discovered that is oriented toward Claude Code, Codex, OpenCode, or other agents — but is NOT yet Hermes-native. The Agent Skills format is an open standard (agentskills.io); Claude-oriented SKILL.md files adapt to Hermes with a small, mechanical transformation (see the Playbook below). **They belong in the corpus for exactly that reason.**

**Legend:**
- 🔍 `[RESEARCH]` = discovered, source URL given, NOT installed
- 🧩 `[MCP]` = MCP server · 🛠️ `[TOOL]` = standalone · 📚 `[INDEX]` = curated list / guide
- ★N = GitHub stars at research time (2026-08-17)

---

## 1. The Adaptation Playbook (Claude → Hermes)

Most Claude Code skills are plain `SKILL.md` (YAML frontmatter + markdown). Adapting them to Hermes is mechanical:

### 1.1 Frontmatter conversion
```markdown
# Claude-native:
---
name: my-skill
description: Long, prose-heavy trigger description...   # often 150-400 chars
---
```
```markdown
# Hermes-native (gold standard):
---
name: my-skill
description: "What it does. Use when [trigger phrases]."
---
```
- **Rewrite the description to ≤60 chars.** This is the #1 change — Claude allows long descriptions; Hermes truncates them in the index at 57 chars.
- Keep `name` identical (it must match the folder).

### 1.2 Tool-name rewrites
| Claude Code tool | Hermes equivalent |
|---|---|
| `Read` / `Edit` / `Write` | `read_file` / `patch` / `write_file` |
| `Bash` | `terminal` |
| `Glob` / `Grep` | `search_files` |
| `WebSearch` / `WebFetch` | `web_search` / `web_extract` (or duckduckgo/searxng skills) |
| `TodoWrite` | `todo` |
| `AskUserQuestion` | `clarify` |
| `SlashCommand` (/cmd) | Convert to a skill trigger phrase or cron/webhook |

### 1.3 Structural rewrites
- `# ...` heading stays; `## When to Use` → fold trigger phrases into the description
- `### Usage` examples → bash-first blocks
- Add a `Pitfalls` section if the source lacks one
- `references/`, `scripts/`, `assets/` copy verbatim — they're portable
- Remove Claude-specific hooks (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`)

### 1.4 Validation (mandatory)
- `description` ≤60 chars · `name` == folder · YAML parses · loads via `skills_list`
- Run the repo's own `skills_guard.py` scan on any third-party skill before installing

### 1.5 When NOT to adapt
- Skills that hard-depend on Claude-specific features (hooks, subagents-as-files, `claude -p`)
- Bundles so large they'd bloat the system prompt (e.g. CyberStrike's 7,600 skills → take a curated subset)

---

## 2. HIGH-VALUE Claude-Oriented Catalog (adapt on demand, deduped)

> Priority = how valuable the *adaptation* is for Hermes. These are the ones a future instance should clone → adapt → author first.

### 2a. Design & Frontend (★ = stars)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `Leonxlnx/taste-skill` | 77,383 | Anti-slop "AI taste" — most-starred skill | 🔴 TOP |
| `nextlevelbuilder/ui-ux-pro-max-skill` | 117,610 | Design intelligence for pro UI/UX | 🔴 TOP |
| `Nutlope/hallmark` | 25,530 | Anti-AI-slop design skill | HIGH |
| `blader/humanizer` | 36,159 | Removes AI-generated writing signs | HIGH |
| `bergside/awesome-design-skills` | 2,400 | 67 DESIGN.md/SKILL.md design skills (index) | HIGH |
| `zarazhangrui/frontend-slides` | 27,686 | Beautiful web slides via frontend skills | MED |
| `op7418/guizang-ppt-skill` | 24,269 | Editorial/Swiss HTML slide decks | MED |
| `alchaincyf/huashu-design` | 23,199 | HTML-native design skill (high-fidelity prototypes) | MED |
| `nexu-io/html-anything` | 8,324 | 75 skills × 9 surfaces (magazine/deck/…) | MED |

### 2b. Engineering Workflow & Code Quality
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `addyosmani/agent-skills` | 88,026 | Production-grade engineering skills (**already adapted** — our addy clones) | DONE |
| `OthmanAdi/planning-with-files` | 26,211 | Crash-proof file-based planning, session recovery | 🔴 TOP |
| `mksglu/context-mode` | 19,925 | Context-window optimization, 98% tool-output reduction | HIGH |
| `zhaoxuya520/reverse-skill` | 26,001 | RE / pentest / security-research skill router | HIGH |
| `trailofbits/skills` | 6,631 | Trail of Bits security research & vuln detection | HIGH |
| `gotalab/cc-sdd` | 3,619 | Spec-driven autonomous implementation | MED |
| `alirezarezvani/claude-skills` | 24,570 | 345 skills, 30+ agents, 70+ commands (big bundle — subset) | MED |
| `NeoLabHQ/context-engineering-kit` | 1,338 | Context engineering skills (matches our context-engineering) | MED |
| `refly-ai/refly` | 7,491 | Open-source agent skills builder | MED |
| `rohitg00/pro-workflow` | 2,775 | Self-correcting memory over 50+ sessions | MED |

### 2c. Security & OSINT (also see docs 01/02/04)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `mukul975/Anthropic-Cybersecurity-Skills` | 28,352 | 817 skills, MITRE/NIST/ATLAS/D3FEND mapped | HIGH (subset) |
| `elementalsouls/Claude-OSINT` | 2,306 | 8 skills, 100+ recon caps, 80 dorks | 🔴 TOP |
| `elementalsouls/Claude-BugHunter` | 3,636 | 82 skills, 681 disclosed-report patterns | 🔴 TOP (core already adapted) |
| `ljagiello/ctf-skills` | 3,017 | CTF skills: pwn, crypto, RE, forensics, OSINT | HIGH |
| `zhaoxuya520/reverse-skill` | 26,001 | RE/pentest router | HIGH (dup above) |
| `GoldenWing-360/claude-security-skills` | 15 | 25 defensive skills | MED |

### 2d. Agentic Workflow & Orchestration
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `ruvnet/ruflo` | 68,076 | Agent meta-harness, multi-player swarms | MED (ref) |
| `affaan-m/ECC` | 240,685 | Agent harness performance optimization system | HIGH |
| `K-Dense-AI/scientific-agent-skills` | 33,745 | #1 science agent skills library | MED |
| `alirezarezvani/claude-code-skill-factory` | 850 | Build/deploy production Claude skills | MED |
| `FrancyJGLisboa/agent-skill-creator` | 2,261 | Turn workflows into skills on 17 platforms | MED |
| `mohitagw15856/pm-claude-skills` | 1,292 | 1,098 professional agent skills | LOW (bundle) |

### 2e. Music & Creative
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `Donchitos/Claude-Code-Game-Studios` | 24,010 | Game dev studio: 49 agents, 72 skills | LOW (game) |
| `calesthio/OpenMontage` | 48,591 | Agentic video production, 12 pipelines | MED |
| `AgriciDaniel/claude-music` | 33 | ACE-Step 1.5 song generation | MED (see 06) |

---

## 3. MCP Servers Discovered in Claude-Oriented Sweep (adaptable to Hermes)

| Repo | ★ | What it gives | Key? |
|---|---|---|---|
| `Simon-Kansara/ableton-live-mcp-server` | 393 | Ableton OSC (see 06) | No |
| `kepano/obsidian-skills` | 46,499 | Obsidian CLI/open formats | No |
| `zilliztech/memsearch` | 2,479 | Unified agent memory layer | Config |
| `officecli` (iOfficeAI) | 28,622 | Office suite for agents (Word/Excel/PPT) | No |
| `posthog/ai-plugin` | 76 | Analytics plugin | Key |

---

## 4. Curated Indexes / Guides (use to DISCOVER more, not to install)

| Repo | ★ | What it is |
|---|---|---|
| `VoltAgent/awesome-agent-skills` | 30,449 | 1000+ agent skills, official + community |
| `ComposioHQ/awesome-claude-skills` | 72,673 | Curated Claude skills/resources |
| `hesreallyhim/awesome-claude-code` | 52,492 | Finest Claude Code resources |
| `anthropics/claude-plugins-official` | 33,618 | Official Anthropic plugin directory |
| `travisvn/awesome-claude-skills` | 14,689 | Curated Claude skills |
| `openai/skills` | 25,006 | **Official Codex skills catalog** |
| `NVIDIA/skills` | 2,987 | NVIDIA product skills (Physical AI, robotics) |
| `itgoyo/awesome-agent-skills` | 176 | Hot agent-skills collection |
| `lingxling/awesome-skills-cn` | 253 | 7000+ skills aggregated (11w+ stars across sources) |
| `fleurytian/awesome-claude-skills` | 311 | Brain-worker Claude skills |
| `alirezarezvani/claude-skills` | 24,570 | 345 skills bundle |
| `gamedev-skills/awesome-gamedev-agent-skills` | 532 | 67 game-dev skills |

---

## 5. Notes

- **These are NOT installed.** They are the adapt-on-demand pool. A future Hermes instance: clone → apply the Playbook (§1) → author per the gold standard → validate.
- The **gold standard is always davidondrej's `effective-agent-skills`** — clone it first, author second (see banner at top).
- Dedup: many of these overlap already-authored skills (addy, elementalsouls, anthropics). Check `00-master-inventory.md` before adapting.
- Big bundles (CyberStrike 7,600, alirezarezvani 345, mohitagw 1,098, Anthropic-Cyber 817) → **curate a subset**, never bulk-install (system-prompt bloat).

# Hermes Agent Base

**A portable, cloneable knowledge base of skills, tools, and MCP servers — for any future Hermes instance.**

Compiled 2026-08-17 from a full research + authoring session: GitHub API hunts across 4 domains (OSINT, Red Teaming, Frontend/Backend Design & Performance, Security, Agentic Workflow, Music Production), the official `NousResearch/hermes-agent` skill hub, and starred-repo clones. Every item here is **verified to exist** — either already authored into the Hermes skills library, or captured as a research finding with its source URL for future cloning.

---

## 📖 How to Use This Repo (for future Hermes)

1. **Clone** this repo to any machine: `git clone https://github.com/BBridgeers/hermes-agent-base.git`
2. **Read `docs/`** — each doc is one category. Items marked `[AUTHORED]` already exist as SKILL.md files in `~/.hermes/skills/`. Items marked `[RESEARCH]` are discovered-but-not-yet-authored — clone the source URL and author per the `effective-agent-skills` methodology.
3. **The gold standard:** every SKILL.md must be authored per `meta/effective-agent-skills` (the verbatim davidondrej "Agent Skills: A Complete Guide"). Rules: description ≤60 chars, name == folder, one skill = one concern, relative paths, no secrets.

---

## 🗂️ Legend / How to Read the Docs

Every entry is annotated with a **status marker** and a **source**:

| Marker | Meaning |
|---|---|
| ✅ `[AUTHORED]` | Installed in `~/.hermes/skills/` — SKILL.md written, validated, loadable |
| 🔍 `[RESEARCH]` | Discovered via GitHub API — not yet authored. Source URL given for cloning |
| 🧩 `[MCP]` | MCP server (needs config + possibly API keys) — staged as a skill wrapper or documented |
| 🛠️ `[TOOL]` | Standalone CLI/library tool — capability reference, install on demand |
| ★N | GitHub stars at time of research (popularity signal) |

**Sources legend:**
- `HUB` = official NousResearch/hermes-agent skill hub (`/tmp/hermes-agent-skills/` or repo `NousResearch/hermes-agent`)
- `STARS` = user's starred repos (cloned to `~/cloned-stars/`)
- `GHAPI` = GitHub API search result (2026-08-17)
- `AUTHORED` = created from session knowledge

**Sections in each doc:**
1. **Authored skills** — what's installed, with its description (routing contract)
2. **Research findings** — the best-of-best discovered, with stars + source URL, prioritized
3. **MCP servers** — what's wired or staged
4. **Notes** — pitfalls, dependencies, API-key requirements

---

## 📂 Repository Layout

```
hermes-agent-base/
├── README.md                     ← this file (legend + index)
├── docs/
│   ├── 00-master-inventory.md    ← ★ COMPLETE CORPUS: all 163 installed skills + research finds, deduped
│   ├── 01-osint.md               ← OSINT: tools, skills, dossiers
│   ├── 02-red-team.md            ← Red teaming: C2, frameworks, skills
│   ├── 03-frontend-backend.md    ← Design, performance, code execution
│   ├── 04-security.md            ← Hardening, auditing, scanning
│   ├── 05-agentic-workflow.md    ← Agent design, orchestration, workflows
│   ├── 06-music-production.md    ← Music/beat creation (user's stack)
│   ├── 07-capability.md          ← Generic capability primitives (scraping, testing, MCP builder)
│   ├── 08-research-vault.md      ← RAW master list of every discovered tool/MCP
│   ├── 09-claude-adaptation.md   ← ★ Claude/Codex/OpenCode skills + the adaptation playbook
│   ├── 10-top-tier-remaining.md  ← ★ Finance/ML/creative/marketing/legal/web3/health best-of
│   ├── 11-curated-per-domain.md  ← ★ Top 20–30 per domain (8 domains) — deep-sweep curated
│   └── 12-travel-hotel-car-rental.md ← ★ Travel, hotel booking, car rental & discount/deal skills + MCPs
└── research-vault/
    └── (source dumps, cloned repos reference)
```

**Start with `00-master-inventory.md`** — it is the complete, deduplicated corpus. Category docs add detail per domain. **`09-claude-adaptation.md`** catalogs Claude/Codex/OpenCode-oriented skills with the exact playbook to adapt them to Hermes.

---

## 📑 Category Index (quick jump)

| Doc | Scope | Authored | Research |
|---|---|---|---|
| [00-master-inventory.md](docs/00-master-inventory.md) | ★ **COMPLETE corpus** — everything, deduped | 163 | ~90 |
| [09-claude-adaptation.md](docs/09-claude-adaptation.md) | ★ Claude/Codex/OpenCode skills + adaptation playbook | — | 171 |
| [10-top-tier-remaining.md](docs/10-top-tier-remaining.md) | ★ Finance/ML/creative/marketing/legal/web3/health | — | ~60 |
| [11-curated-per-domain.md](docs/11-curated-per-domain.md) | ★ **Top 20–30 per domain** (8 domains + plugins) | — | ~200 |
| [12-travel-hotel-car-rental.md](docs/12-travel-hotel-car-rental.md) | ★ Travel, hotel, car rental & discount/deal skills + MCPs | — | ~100 |
| [01-osint.md](docs/01-osint.md) | Username/email/phone/domain/website intel | 14 | ~15 |
| [02-red-team.md](docs/02-red-team.md) | C2, adversary sim, pentest frameworks | 9 | ~12 |
| [03-frontend-backend.md](docs/03-frontend-backend.md) | UI/UX, anti-slop, perf, backend | 34+ | ~15 |
| [04-security.md](docs/04-security.md) | Hardening, OWASP, scanning, MCP | 18 | ~12 |
| [05-agentic-workflow.md](docs/05-agentic-workflow.md) | Agent frameworks, workflow design | 6 | ~15 |
| [06-music-production.md](docs/06-music-production.md) | Ableton/FL/rekordbox, DAW MCP | 1 | ~15 |
| [07-capability.md](docs/07-capability.md) | Generic tools: scraping, testing, MCP | 7 | ~8 |
| [08-research-vault.md](docs/08-research-vault.md) | RAW master list of everything found | — | ~90 |

---

## 🔑 Key Authored Skills (the crown jewels)

| Skill | Category | Why it matters |
|---|---|---|
| `effective-agent-skills` | meta | **The gold standard** — verbatim davidondrej authoring methodology |
| `kali-pentest` | security | Full authorized Kali pentest workflow (recon→report) |
| `bug-bounty` | security | Complete recon→hunt→validate→report pipeline |
| `cti-expert` | research | 67+ command threat-intel/OSINT analyst, no API keys |
| `web-quality-skills` | frontend | Addy Osmani Lighthouse/CWV optimization |
| `maigret` | research | 3000+ site username dossiers |

---

## ⚠️ Important Notes for Future Instances

- **Never push secrets.** This repo is public. API keys live in `~/.hermes/.env`, never in skills.
- **The 60-char rule.** Hermes rejects skill descriptions >60 chars. Always rewrite to ≤60 (what + when + differentiator, ends with period).
- **MCP servers need config.** `[MCP]` items require `setup_mcp` consent + API keys where noted. Skills that *wrap* MCP tools are already authored.
- **Authorized use only.** All offensive-security skills carry an authorized-use constraint — respect it.

*Built by Hermes Agent for Jayden's future Hermes instances. Clone, adapt, extend.*

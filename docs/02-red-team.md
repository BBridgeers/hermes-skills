# 02 — Red Teaming & Offensive Security

**Scope:** C2 frameworks, adversary simulation, pentest frameworks, offensive skill packs.
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## ✅ Authored Skills (installed in `~/.hermes/skills/security/`)

### C2 & Frameworks
| Skill | Description | Source |
|---|---|---|
| `covenant` | Collaborative .NET C2 for red teamers (web UI, Grunts). | STARS |
| `mythic` | Multi-platform red teaming C2 framework (Docker agents). | STARS |
| `viper` | Adversary simulation + red teaming platform (AI). | STARS |
| `decepticon` | Autonomous hacking agent for red team. | STARS |
| `pentestgpt` | LLM-powered automated penetration testing. | STARS |

### Offensive Toolkits
| Skill | Description | Source |
|---|---|---|
| `nishang` | Offensive PowerShell collection (recon→exfil). | STARS |
| `atomic-red-team` | MITRE ATT&CK detection tests (red/blue validation). | STARS |
| `kali-pentest` | **Full authorized Kali pentest workflow** — recon→exploit→report, SSH/Docker/Local, 15 playbooks. | GHAPI (x-glacier) |
| `bug-bounty` | **Complete bug bounty pipeline** — recon→learn→hunt→validate→report, 80+ hunt sub-skills. | GHAPI (elementalsouls) |

### Curated Indexes
| Skill | Description | Source |
|---|---|---|
| `red-teaming-toolkit` | Curated red team + threat hunting tool index. | STARS |
| `redteam-tools` | Red team & pentest tools/techniques index (kill-chain). | STARS |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

| Repo | ★ | What it is | Why |
|---|---|---|---|
| `elementalsouls/Claude-BugHunter` | 3,636 | 82 skills, 15 commands, 681 disclosed-report patterns | The definitive bug-hunter pack (we took the core `bug-bounty` skill) |
| `mukul975/Threatswarm` | 67 | 27 scope-enforced agents running full pentest kill-chain | One-command agent swarm |
| `x-glacier/kali-pentest` | 89 | 200+ Kali tools, 15 playbooks — **Hermes-targeted** | Already authored as `kali-pentest` |
| `redcanaryco/atomic-red-team` | 12,417 | ATT&CK detection tests | Reference (authored wrapper) |
| `samratashok/nishang` | 10,057 | Offensive PowerShell | Reference (authored wrapper) |
| `infosecn1nja/Red-Teaming-Toolkit` | 10,632 | Cutting-edge OST for red teamers | Reference (authored wrapper) |
| `cobbr/Covenant` | 4,724 | .NET C2 | Reference (authored wrapper) |
| `its-a-feature/Mythic` | 4,704 | Multi-platform C2 | Reference (authored wrapper) |
| `PurpleAILAB/Decepticon` | 5,162 | Autonomous hacking agent | Reference (authored wrapper) |
| `GreyDGL/PentestGPT` | 14,915 | LLM pentest framework | Reference (authored wrapper) |
| `A-poc/RedTeam-Tools` | 9,633 | Red team tools & techniques | Reference (authored wrapper) |

---

## 🧩 MCP Servers (Red Team)

| Repo | ★ | What it gives | API key needed? |
|---|---|---|---|
| `0x4m4/hexstrike-ai` | 11,134 | 150+ cybersecurity tools via MCP | No |
| `cyproxio/mcp-for-security` | 630 | SQLMap, FFUF, NMAP, Masscan MCP | No |
| `Wh0am123/MCP-Kali-Server` | 799 | Connect AI agent to Kali Linux machine | No |
| `six2dez/burp-mcp-agents` | 222 | Burp Suite MCP for Codex/Gemini/Ollama | No |

---

## ⚠️ Notes
- **Authorization is mandatory** for every offensive tool. `kali-pentest` and `bug-bounty` embed explicit security constraints (scope binding, risk confirmation, prohibited ops).
- C2 frameworks (Covenant/Mythic/Viper) are resource-heavy — lab/authorized engagements only.
- `decepticon`/`pentestgpt` run real tools autonomously — strict scope, never unsupervised on live targets.

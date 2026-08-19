# 04 — Security / Security Hardening

**Scope:** defensive hardening, OWASP, code auditing, secret scanning, SAST/DAST, agent-security.
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## ✅ Authored Skills (installed in `~/.hermes/skills/security/`)

### Hardening & Auditing
| Skill | Description | Source |
|---|---|---|
| `security-and-hardening` | Harden code against threats. Use for security work. | STARS (addy) |
| `code-review-and-quality` | Review code for quality and correctness. Use for reviews. | STARS (addy) |
| `oss-forensics` | Forensic analysis of OSS packages. Use for supply chain. | HUB |
| `unbroker` | Analyze and deobfuscate code. Use for reversing. | HUB |
| `vuln-scanner` | Scan code for vulnerabilities. Use for security scanning. | STARS (aeon) |
| `vuln-tracker` | Track vulnerabilities over time. Use for vuln monitoring. | STARS (aeon) |

### Offensive / Red-Team-Adjacent (also see 02)
| Skill | Description | Source |
|---|---|---|
| `web-pentest` | Test web apps for vulnerabilities. Use for pentesting. | HUB |
| `godmode` | Godmode security tooling. Use for security research. | HUB |
| `kali-pentest` | Full authorized Kali pentest workflow. | GHAPI |
| `bug-bounty` | Complete bug bounty recon→hunt→validate→report. | GHAPI |
| `atomic-red-team` | MITRE ATT&CK detection tests. | STARS |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

### Security Skills / Toolkits
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `snyk/agent-scan` | 2,915 | Security scanner for AI agents, MCP servers & skills | **TOP** |
| `agamm/claude-code-owasp` | 337 | OWASP 2025, ASVS 5.0, Agentic AI security, 20+ languages | TOP |
| `google/mantis` | 756 | Google's modular security-review skill toolkit | HIGH |
| `AgentSecOps/SecOpsAgentKit` | 195 | 32 skills: vulns, containers, secret detection | HIGH |
| `GitGuardian/agent-skills` | 4 | ggshield secret scanning for agents | MED |
| `BridgeSecurity` (bridge-mind) | 25 | OWASP Top 10, CWE Top 25, secrets detection | MED |
| `unitoneai/SecuritySkills` | 51 | OWASP/NIST/MITRE/CIS-grounded security skills | MED |
| `OWASP/www-project-agentic-skills-top-10` | 161 | OWASP official Agentic Skills Top 10 | HIGH |
| `Tencent/AI-Infra-Guard` | 4,514 | Full-stack AI red-teaming: Agent/Skills/MCP/LLM scan | HIGH |
| `affaan-m/agentshield` | 1,071 | AI agent security scanner (CLI/GH Action/MCP) | HIGH |
| `cisco-ai-defense/mcp-scanner` | 1,038 | Scan MCP servers for threats | MED |

### Agent-Skill Security (scan skills before install)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `jmxt3/gitscape.ai` | 32 | Scan any agent skill for prompt injection/secrets | MED |
| `simplybychris/skill-audit` | 6 | Static heuristic scan of untrusted skills | LOW |
| `YangKuoshih/security-audit` | 5 | Universal security scan, 44 patterns | LOW |
| `munzzyy/skillxray` | 1 | Prompt-injection/Unicode/dangerous-command scan | LOW |

---

## 🧩 MCP Servers (Security)

| Repo | ★ | What it gives | Key? |
|---|---|---|---|
| `mukul975/cve-mcp-server` | 1,134 | 27 security-intel tools, 21 APIs (CVE/EPSS/KEV/MITRE) | No |
| `FuzzingLabs/mcp-security-hub` | 761 | Nmap, Ghidra, Nuclei, SQLMap, Hashcat | No |
| `semgrep/mcp` | 683 | Semgrep SAST | No |
| `SonarSource/sonarqube-mcp-server` | 626 | SonarQube quality+security | Server |
| `cyproxio/mcp-for-security` | 630 | SQLMap/FFUF/NMAP/Masscan | No |
| `snyk/agent-scan` | 2,915 | Agent/MCP/skill scanning | No |

---

## ⚠️ Notes
- The single biggest defensive gap: **snyk/agent-scan** (protects your agent from bad skills/MCPs) and **agamm/claude-code-owasp** (current OWASP coverage). Author both when expanding.
- Hermes already ships a `skills_guard.py` + `skills_ast_audit.py` internally — the research list complements those.
- Secret redaction is ON by default in Hermes (`redact_secrets`); never disable it.

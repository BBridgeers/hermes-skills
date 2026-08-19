# 01 — OSINT (Open-Source Intelligence)

**Scope:** username, email, phone, domain, website, and identity intelligence.
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## ✅ Authored Skills (installed in `~/.hermes/skills/research/`)

### Username / Identity
| Skill | Description | Source |
|---|---|---|
| `sherlock` | Find usernames across 400+ sites. Use for OSINT lookup. | HUB |
| `maigret` | Collect a dossier on a username across 3000+ sites. | STARS |
| `sn0int` | Semi-automatic OSINT framework + package manager. | STARS |
| `ghunt` | Investigate Google accounts from an email or doc. | STARS |
| `holehe` | Check if an email is registered on 120+ sites. | STARS |
| `phoneinfoga` | Gather info on phone numbers (carrier, line type, footprint). | STARS |

### Email / Phone / Docs
| Skill | Description | Source |
|---|---|---|
| `theharvester` | Harvest emails, subdomains, and names from public sources. | STARS |
| `osint-investigation` | Run full OSINT investigations. Use for open-source intel. | HUB |

### Domain / Website / Network
| Skill | Description | Source |
|---|---|---|
| `domain-intel` | Gather domain intelligence. Use for target research. | HUB |
| `web-check` | Analyze any website with all-in-one OSINT checks. | STARS |
| `spiderfoot` | Automate OSINT and attack surface mapping (200+ modules). | STARS |
| `amass` | Map attack surface and discover assets (OWASP). | STARS |
| `subfinder` | Passive subdomain enumeration (30+ sources). | STARS |
| `bbot` | Recursive internet scanner for recon. | STARS |
| `photon` | Fast web crawler for OSINT data extraction (URLs/emails/keys). | STARS |

### Search / Research Infrastructure
| Skill | Description | Source |
|---|---|---|
| `duckduckgo-search` | Search DuckDuckGo from CLI. Use for private search. | HUB |
| `searxng-search` | Search via SearXNG metasearch. Use for private search. | HUB |
| `gitnexus-explorer` | Explore GitHub repos and code. Use for source research. | HUB |
| `cti-expert` | Threat intel + OSINT analysis. 67+ commands, no API keys. | GHAPI (7onez) |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

| Repo | ★ | What it is | Why |
|---|---|---|---|
| `mukul975/Anthropic-Cybersecurity-Skills` | 28,249 | 817 structured skills mapped to MITRE ATT&CK/NIST/ATLAS/D3FEND | The biggest agent-skill pack — but mostly framework reference, ~90% redundant with what we have |
| `elementalsouls/Claude-OSINT` | 2,306 | 8 skills, 100+ recon caps, 80 dorks, 27 attack-paths | Excellent tactical OSINT pack |
| `useosint/osint-skills` | 15 | 28 OSINT agent skills — recon → full intel platform | Clean, focused, small |
| `smixs/osint-skill` | 105 | name → scored dossier with psychoprofile | Unique scoring output |
| `SOsintOps/claudii-exploratores` | 13 | 898 curated OSINT tools as skill + MCP | Massive tool catalog |
| `7WaySecurity/ai_osint` | 154 | Google dorks, Shodan queries, GitHub dorks for exposed LLM endpoints | LLM-specific OSINT |
| `frangelbarrera/osint-agent-skills` | 23 | OSINT knowledge base + MCP server | Agent-ready |
| `assafkip/kipi` | 61 | Self-hosted OSINT investigation platform — entity graph | Investigation-grade |

---

## 🧩 MCP Servers (OSINT)

| Repo | ★ | What it gives | API key needed? |
|---|---|---|---|
| `w0h1v/mcp-maigret` | 258 | maigret (3000+ sites) as MCP | No |
| `w0h1v/mcp-shodan` | 157 | Shodan search, IP recon, CVE intel | Yes (Shodan) |
| `badchars/osint-mcp-server` | 44 | 37 tools, 12 sources (Shodan/VT/Censys/ST) | Mixed |
| `FuzzingLabs/mcp-security-hub` | 761 | Nmap, Ghidra, Nuclei, SQLMap, Hashcat | No |
| `soxoj/awesome-osint-mcp-servers` | 455 | Curated index of OSINT MCP servers | — (index) |

---

## ⚠️ Notes
- All offensive/OSINT skills: **authorized use only** — respect site ToS and local law.
- `maigret` slow (3000+ sites) — use `--timeout`/`--retries`.
- `ghunt` requires valid Google cookies (interactive).
- MCP servers for OSINT are optional; the SKILL.md wrappers already teach invocation.

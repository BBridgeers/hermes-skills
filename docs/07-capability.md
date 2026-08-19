# 07 — Capability Primitives (Generic Tools & Techniques)

**Scope:** capability-wrapper skills that teach the agent to invoke a deterministic tool/CLI (Pattern A primitives).
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## ✅ Authored Skills (installed)

### Scraping & Data Extraction
| Skill | Category | Description | Source |
|---|---|---|---|
| `scrapling` | research | Stealth scraping: HTTP/JS/Cloudflare bypass + spider (via HUB optional) | HUB |
| `duckduckgo-search` | research | Private CLI search | HUB |
| `searxng-search` | research | Metasearch via SearXNG | HUB |
| `youtube-content` | media | YouTube transcripts → summaries/threads/blogs | HUB |

### Testing & QA
| Skill | Category | Description | Source |
|---|---|---|---|
| `webapp-testing` | software-development | Playwright web UI testing | STARS |
| `browser-testing-with-devtools` | software-development | Chrome DevTools MCP testing | STARS |
| `dogfood` | software-development | Exploratory QA of web apps | HUB |

### MCP & Integration
| Skill | Category | Description | Source |
|---|---|---|---|
| `mcp-builder` | software-development | Build MCP servers for tools | STARS |
| `har-derived-api-client` | software-development | API clients from HAR files | HUB |
| `page-agent` | software-development | Drive a web page agent | HUB |

### Debugging & Env
| Skill | Category | Description | Source |
|---|---|---|---|
| `python-debugpy` / `node-inspect-debugger` | software-development | DAP debugging | HUB |
| `python-env-management` | software-development | uv venv/pip on macOS | HUB |
| `inspecting-hermes-desktop-dom` | software-development | Hermes desktop DOM over CDP | HUB |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

### Scraping / Crawling
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `D4Vinci/Scrapling` | — | Stealth scraping framework (authored as `scrapling`) | DONE |
| `Datalux/Osintgram` | 14,023 | Instagram OSINT shell | MED |
| `s0md3v/Photon` | 13,120 | Fast OSINT crawler (authored as `photon`) | DONE |

### Testing / Verification
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `google/mantis` | 756 | Modular security-review skills (see 04) | HIGH |
| `hgtonight/webapp-testing` (anthropics) | — | Playwright toolkit (authored as `webapp-testing`) | DONE |

### MCP Ecosystem (generic)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `stacklok/toolhive` | 2,023 | Enterprise MCP server management | MED |
| `cyanheads/mcp-ts-core` | 147 | Agent-native TS MCP framework | MED |
| `superdesigndev/superdesign-skill` | 429 | Design skill system (see 03) | MED |

---

## ⚠️ Notes
- Capability primitives are the easiest to author: thin wrapper with Install → Usage → Output → Pitfalls.
- When authoring a new capability skill, prefer wrapping an existing CLI over pasting library code (gold standard rule).
- `scrapling` + `duckduckgo-search` + `searxng-search` form the complete private-research stack.

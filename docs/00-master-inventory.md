# 00 — MASTER INVENTORY (Complete Corpus)

**The entire corpus of this session's work — every skill, tool, and MCP server, authored or not, deduped.**
This is the canonical index. Category docs (01–08) carry the detail; this doc is the complete, deduplicated map.

**Legend:**
- ✅ `[AUTH]` = installed in `~/.hermes/skills/` (SKILL.md written + validated)
- 🔍 `[RESEARCH]` = discovered, source URL given, NOT installed
- 🧩 `[MCP]` = MCP server (needs config; may need API key)
- 🛠️ `[TOOL]` = standalone CLI/library (capability reference)
- ★N = GitHub stars at research time
- `SOURCE`: HUB = hermes-agent hub · STARS = user's starred clones · GHAPI = GitHub search · OWN = authored/merged by us

---

## 1. INSTALLED SKILLS — Full List (163 across 18 categories)

### apple (4) — HUB
| Skill | Description |
|---|---|
| apple-notes | Manage Apple Notes via memo CLI |
| apple-reminders | Apple Reminders via remindctl |
| findmy | Track Apple devices/AirTags via FindMy.app |
| imessage | Send/receive iMessages/SMS via imsg CLI |

### autonomous-ai-agents (7) — HUB
| Skill | Description |
|---|---|
| claude-code | Delegate coding to Claude Code CLI |
| codex | Delegate coding to OpenAI Codex CLI |
| computer-use | Drive desktop in background w/o stealing focus |
| hermes-agent | Use, configure, theme, extend, orchestrate Hermes |
| hermes-auxiliary-model-routing | Allocate auxiliary tasks across providers |
| merge-reconciler | Neutral 3rd-party merge-conflict resolution |
| opencode | Delegate coding to OpenCode CLI |

### creative (16) — HUB
architecture-diagram · ascii-art · ascii-video · baoyu-infographic · claude-design · comfyui · design-md · excalidraw · humanizer · manim-video · p5js · popular-web-designs · pretext · sketch · songwriting-and-ai-music · touchdesigner-mcp

### devops (1) — HUB
sdlc-review

### email (2) — HUB
email-inbox-triage · himalaya

### github (8) — HUB
codebase-inspection · github-auth · github-code-review · github-issue-to-pr · github-issues · github-pr-workflow · github-repo-management · github-repo-polish

### media (3) — HUB
gif-search · songsee · youtube-content

### meta (2) — HUB + OWN
| Skill | Description | Note |
|---|---|---|
| effective-agent-skills | **The gold-standard authoring methodology** | ✅ Own clone of davidondrej/skills (verbatim, 323 lines) |
| external-skill-import | Port external SKILL.md files into ~/.hermes/skills/ | — |

### mlops (6) — HUB
evaluating-llms-harness · huggingface-hub · llama-cpp · local-llm-ollama · serving-llms-vllm · weights-and-biases

### note-taking (1) — HUB
obsidian

### productivity (18) — HUB
airtable · box · document-to-action-items · docx · google-workspace · macos-device-optimization · maps · meeting-action-items · nano-pdf · notion · ocr-and-documents · pdf · powerpoint · product-price-monitor · session-librarian · teams-meeting-pipeline · weekly-review-planning · xlsx

### research (26) — MIXED
| Skill | Description | Source |
|---|---|---|
| arxiv | Search arXiv papers | HUB |
| blocked-page-recovery | Recover blocked/paywalled pages | HUB |
| blogwatcher | Monitor blogs/RSS | HUB |
| competitor-news-monitor | Watch companies for material news | HUB |
| grounded-citations | Ground answers in verifiable sources | HUB |
| llm-wiki | Karpathy LLM Wiki KB | HUB |
| research-paper-writing | Write ML papers | HUB |
| osint-investigation | Full OSINT investigations | HUB |
| domain-intel | Domain intelligence | HUB |
| gitnexus-explorer | GitHub source research | HUB |
| duckduckgo-search | Private CLI search | HUB |
| searxng-search | SearXNG metasearch | HUB |
| sherlock | Usernames across 400+ sites | HUB |
| **cti-expert** | **Threat intel + OSINT, 67+ commands, no keys** | ✅ OWN (7onez clone) |
| **maigret** | **Username dossier across 3000+ sites** | ✅ OWN (authored) |
| **web-check** | **All-in-one website OSINT** | ✅ OWN (authored) |
| **spiderfoot** | **Automated OSINT + attack surface** | ✅ OWN (authored) |
| **ghunt** | **Google account investigation** | ✅ OWN (authored) |
| **phoneinfoga** | **Phone number footprinting** | ✅ OWN (authored) |
| **theharvester** | **Emails/subdomains/names harvest** | ✅ OWN (authored) |
| **amass** | **Attack-surface mapping (OWASP)** | ✅ OWN (authored) |
| **subfinder** | **Passive subdomain enum (30+ sources)** | ✅ OWN (authored) |
| **holehe** | **Email registration check (120+ sites)** | ✅ OWN (authored) |
| **photon** | **Fast OSINT crawler** | ✅ OWN (authored) |
| **bbot** | **Recursive internet scanner** | ✅ OWN (authored) |
| **sn0int** | **Semi-automatic OSINT framework** | ✅ OWN (authored) |

### security (18) — MIXED
| Skill | Description | Source |
|---|---|---|
| security-and-hardening | Harden code against threats | ✅ OWN (addy clone) |
| oss-forensics | OSS supply-chain forensics | HUB |
| unbroker | Analyze/deobfuscate code | HUB |
| web-pentest | Web app vulnerability testing | HUB |
| godmode | Godmode security tooling | HUB |
| vuln-scanner | Scan code for vulnerabilities | ✅ OWN (aeon clone) |
| vuln-tracker | Track vulnerabilities over time | ✅ OWN (aeon clone) |
| atomic-red-team | MITRE ATT&CK detection tests | ✅ OWN (authored) |
| covenant | .NET C2 framework | ✅ OWN (authored) |
| mythic | Multi-platform C2 | ✅ OWN (authored) |
| viper | Adversary sim platform (AI) | ✅ OWN (authored) |
| decepticon | Autonomous hacking agent | ✅ OWN (authored) |
| pentestgpt | LLM-powered pentest | ✅ OWN (authored) |
| nishang | Offensive PowerShell | ✅ OWN (authored) |
| red-teaming-toolkit | Curated red-team index | ✅ OWN (authored) |
| redteam-tools | Red-team tools/techniques | ✅ OWN (authored) |
| **kali-pentest** | **Full authorized Kali pentest workflow** | ✅ OWN (x-glacier clone) |
| **bug-bounty** | **Complete bug bounty pipeline** | ✅ OWN (elementalsouls clone) |

### smart-home (1) — HUB
openhue

### social-media (1) — HUB
xurl

### software-development (46) — MIXED
| Skill | Description | Source |
|---|---|---|
| (pre-existing HUB set) | dogfood · inspecting-hermes-desktop-dom · hermes-agent-skill-authoring · node-inspect-debugger · plan · python-debugpy · python-env-management · requesting-code-review · simplify-code · spike · systematic-debugging · test-driven-development | HUB |
| **source-driven-development** | Ground code in official docs | ✅ OWN (addy) |
| **spec-driven-development** | Write a spec before code | ✅ OWN (addy) |
| **incremental-implementation** | Build in small verified increments | ✅ OWN (addy) |
| **api-and-interface-design** | Design clean APIs/interfaces | ✅ OWN (addy) |
| **frontend-ui-engineering** | Accessible polished frontend UI | ✅ OWN (addy) |
| **documentation-and-adrs** | Docs + ADRs for decisions | ✅ OWN (addy) |
| **git-workflow-and-versioning** | Git workflow + versioning | ✅ OWN (addy) |
| **context-engineering** | Engineer context for AI agents | ✅ OWN (addy) |
| **code-review-and-quality** | Review code for quality | ✅ OWN (addy) |
| **debugging-and-error-recovery** | Debug failures, recover | ✅ OWN (addy) |
| **performance-optimization** | Optimize app performance | ✅ OWN (addy) |
| **deprecation-and-migration** | Manage deprecation/migration | ✅ OWN (addy) |
| **observability-and-instrumentation** | Instrument for diagnosability | ✅ OWN (addy) |
| **ci-cd-and-automation** | Automate CI/CD | ✅ OWN (addy) |
| **browser-testing-with-devtools** | Chrome DevTools MCP testing | ✅ OWN (addy) |
| **doubt-driven-development** | Adversarial fresh-context review | ✅ OWN (addy) |
| **shipping-and-launch** | Prepare production launches | ✅ OWN (addy) |
| **code-wiki** | Wiki + Mermaid diagrams | ✅ OWN (HUB optional) |
| **ast-grep** | Search/refactor with ast-grep | ✅ OWN (HUB optional) |
| **react-best-practices** | Vercel React/Next perf rules | ✅ OWN (vercel) |
| **react-native-skills** | React Native + Expo | ✅ OWN (vercel) |
| **react-view-transitions** | View Transitions API | ✅ OWN (vercel) |
| **composition-patterns** | React composition | ✅ OWN (vercel) |
| **writing-guidelines** | Writing guidelines compliance | ✅ OWN (vercel) |
| **web-design-guidelines** | Web Interface Guidelines | ✅ OWN (vercel) |
| **deploy-to-vercel** | Deploy to Vercel | ✅ OWN (vercel) |
| **vercel-cli-with-tokens** | Vercel token auth | ✅ OWN (vercel) |
| **vercel-optimize** | Vercel cost/perf | ✅ OWN (vercel) |
| **frontend-design** | Distinctive visual design | ✅ OWN (anthropics) |
| **web-artifacts-builder** | Multi-component HTML artifacts | ✅ OWN (anthropics) |
| **mcp-builder** | Build MCP servers | ✅ OWN (anthropics) |
| **webapp-testing** | Playwright web testing | ✅ OWN (anthropics) |
| **page-agent** | Drive a web page agent | ✅ OWN (HUB optional) |
| **har-derived-api-client** | API clients from HAR | ✅ OWN (HUB optional) |

### sysadmin (2) — HUB
macos-storage-forensics · macos-system-audit

### voice (1) — OWN
voice-clone-tts — JARVIS voice clone via F5-TTS (nfe 24, cpu, tuned)

---

## 2. RESEARCH-ONLY FINDS (discovered, NOT installed — deduped)

### 2a. Skill packs to author next (priority order)
| Repo | ★ | Category | Why author |
|---|---|---|---|
| `addyosmani/web-quality-skills` | 2,634 | frontend | Lighthouse/CWV — Addy Osmani |
| `Leonxlnx/taste-skill` | 77,375 | frontend | Anti-slop AI taste (most-starred skill) |
| `Owl-Listener/designer-skills` | 2,096 | frontend | 107 design skills |
| `Railly/tinte` | 613 | frontend | Design system → SKILL.md compiler |
| `plugin87/ux-ui-agent-skills` | 502 | frontend | Senior design architect, DTCG tokens |
| `kwakseongjae/oh-my-design` | 430 | frontend | 400+ DESIGN.md refs |
| `snyk/agent-scan` | 2,915 | security | Agent/MCP/skill scanner |
| `agamm/claude-code-owasp` | 337 | security | OWASP 2025, ASVS 5.0 |
| `google/mantis` | 756 | security | Google security-review toolkit |
| `AgentSecOps/SecOpsAgentKit` | 195 | security | 32 secops skills |
| `AkoliteZA/hermes-agent-idea-workflow` | 259 | agentic | Hermes-native idea→spec |
| `cosmicstack-labs/mercury-agent-skills` | 368 | agentic | Hermes-compatible registry |
| `itgoyo/hermes-skills` | 43 | agentic | 310+ Hermes skills catalog |
| `glincker/ableton-skills` | 18 | music | 12 Ableton producer skills |
| `ryan-voitiskis/reklawdbox` | 26 | music | rekordbox 7 library mgmt |
| `Shayanthn/livecodemusic` | 3 | music | Techno/house algorithmic (genre match) |

### 2b. MCP servers to wire (deduped)
| Repo | ★ | Category | Key? |
|---|---|---|---|
| `Simon-Kansara/ableton-live-mcp-server` | 393 | music | No |
| `uisato/ableton-mcp-extended` | 252 | music | No |
| `w0h1v/mcp-maigret` | 258 | osint | No |
| `mukul975/cve-mcp-server` | 1,134 | security | No |
| `FuzzingLabs/mcp-security-hub` | 761 | security | No |
| `semgrep/mcp` | 683 | security | No |
| `benjaminr/chrome-devtools-mcp` | 303 | frontend | No |
| `codewithMUHILAN/Lightswind-UI-Library` | 888 | frontend | No |
| `w0h1v/mcp-shodan` | 157 | osint | Yes (Shodan) |
| `traceloop/opentelemetry-mcp-server` | 198 | backend | Config |

### 2c. Reference tools/frameworks (install on demand)
| Repo | ★ | Category |
|---|---|---|
| `openai/openai-agents-python` | 28,724 | agentic framework |
| `HKUDS/nanobot` | 47,100 | agentic framework |
| `0x4m4/hexstrike-ai` | 11,134 | security MCP |
| `CyberStrikeus/CyberStrike` | 1,853 | security (7,600 skills — subset) |
| `Tencent/AI-Infra-Guard` | 4,514 | security |
| `affaan-m/agentshield` | 1,071 | security |
| `microsoft/Resource2Skill` | 471 | music (tracks→skills) |
| `bitwize-music-studio/claude-ai-music-skills` | 431 | music |
| `TencentCloudBase/skills` | 73 | backend |
| `stacklok/toolhive` | 2,023 | MCP management |

### 2d. Full raw research catalog
→ See `08-research-vault.md` for the complete ~90-item raw list with stars, types, and notes.

### 2e. Claude/Codex/OpenCode-oriented skills (adapt-on-demand pool — 171 found)
→ See `09-claude-adaptation.md`. These are NOT installed; they are the clone → adapt → author pool,
with the full conversion playbook (frontmatter ≤60-char rewrite, tool-name mapping, structural rewrites).
**Always author per the davidondrej `effective-agent-skills` gold standard after cloning.**

### 2f. Top-of-the-top remaining domains (finance/ML/creative/marketing/legal/web3/health — ~60 found)
→ See `10-top-tier-remaining.md`. Includes the Hermes-hub optional-skills catalog not yet mined
(finance ×9, mlops/data-science ×30, blockchain ×3, devops ×6, payments ×3, health ×2, email ×1).

### 2g. Curated top 20–30 per domain (~200 found, 8 domains + plugins)
→ See `11-curated-per-domain.md`. Deep multi-query sweeps (finance, data/ML, video/image, marketing,
legal, social, web3, health) + plugin/MCP marketplaces. Junk filtered, deduped against 00–10.

### 2h. Travel, hotel booking, car rental & discount/deal skills (~100 found)
→ See `12-travel-hotel-car-rental.md`. Multi-query sweeps for travel agents, hotel booking, car rental,
discount/coupon finders, cruise/train, airline MCPs, GDS/OTA APIs. Includes the markswendsen-code
airline/hotel MCP suite (Delta, American, Southwest, United, Marriott, Booking.com, Avis, Hertz, Turo),
stayingapi accommodation skill pack (Airbnb, Booking.com, Google Hotels, Vrbo), and the Expedia official MCP.

---

## 3. DEDUP NOTES (how we avoided doubles)

- `sherlock` (HUB) vs `maigret` (authored) — different tools, kept both (400 vs 3000 sites).
- `webapp-testing` (anthropics) vs `browser-testing-with-devtools` (addy) — different methods (Playwright vs CDP), kept both.
- `kali-pentest` + `bug-bounty` + `cti-expert` were cloned verbatim from their repos — NOT re-synthesized.
- `master-skill-authoring` (earlier synthesis) was **deleted** — superseded by verbatim `effective-agent-skills` (the gold standard).
- `frontend-design` (anthropics) vs `frontend-ui-engineering` (addy) — distinct: visual taste vs engineering process.
- `react-best-practices` (vercel) + `web-quality-skills` (addy, research) — complementary, both kept.
- Vercel sources had `vercel-` prefixed names — renamed to folder-match (e.g. `vercel-react-best-practices` → `react-best-practices`).

---

## 4. SESSION STATS

- Installed at capture: **163 skills / 18 categories**
- Authored this session: **71** (47 core + 21 OSINT/red-team + 3 kali/cti/bug-bounty)
- Research finds cataloged: **~90+** (raw vault: 08)
- MCP servers identified: **~25**, recommended to wire: **10**
- Gold standard: `effective-agent-skills` (verbatim davidondrej, 323 lines)

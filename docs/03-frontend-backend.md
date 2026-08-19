# 03 — Frontend / Backend Design & Performance

**Scope:** UI/UX design, anti-slop taste, design systems, web performance, backend/API design, code execution.
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## ✅ Authored Skills (installed in `~/.hermes/skills/software-development/`)

### Frontend Design
| Skill | Description | Source |
|---|---|---|
| `frontend-design` | Distinctive, intentional visual design for new UI or refactors. | STARS (anthropics) |
| `frontend-ui-engineering` | Build accessible, polished frontend UI. Use for UI work. | STARS (addy) |
| `web-design-guidelines` | Review UI code for Web Interface Guidelines compliance. | STARS (vercel) |
| `composition-patterns` | Compose React components for clean, reusable UIs. | STARS (vercel) |
| `react-best-practices` | React + Next.js performance rules from Vercel Engineering (70 rules). | STARS (vercel) |
| `react-native-skills` | Build React Native apps with Expo + best practices. | STARS (vercel) |
| `react-view-transitions` | Smooth animations using React View Transitions API. | STARS (vercel) |
| `web-artifacts-builder` | Build elaborate multi-component HTML artifacts with React. | STARS (anthropics) |

### Backend / API Design
| Skill | Description | Source |
|---|---|---|
| `api-and-interface-design` | Design clean APIs and interfaces. Use for API design. | STARS (addy) |
| `har-derived-api-client` | Build API clients from HAR files. Use for API work. | HUB |
| `mcp-builder` | Build MCP servers for tools. Use for LLM integrations. | STARS (anthropics) |

### Performance Optimization
| Skill | Description | Source |
|---|---|---|
| `performance-optimization` | Optimize app performance across frontend, backend, queries. | STARS (addy) |
| `observability-and-instrumentation` | Instrument code so production behavior is diagnosable. | STARS (addy) |
| `vercel-optimize` | Optimize Vercel cost and performance on deployed projects. | STARS (vercel) |
| `code-wiki` | Generate wiki docs + Mermaid diagrams for a codebase. | HUB |

### Code Execution & Engineering Process
| Skill | Description | Source |
|---|---|---|
| `source-driven-development` | Ground code in official docs. Use when correctness matters. | STARS (addy) |
| `spec-driven-development` | Write a spec before code. Use for new features or builds. | STARS (addy) |
| `incremental-implementation` | Build in small verified increments. Use for new work. | STARS (addy) |
| `test-driven-development` | TDD: enforce RED-GREEN-REFACTOR, tests before code. | STARS (addy) |
| `doubt-driven-development` | Adversarially review decisions in fresh context before code. | STARS (addy) |
| `debugging-and-error-recovery` | Debug failures and recover. Use for bugs and errors. | STARS (addy) |
| `ast-grep` | Search and refactor code with ast-grep patterns. | HUB |
| `ci-cd-and-automation` | Automate CI/CD pipeline setup and deployment workflows. | STARS (addy) |
| `deploy-to-vercel` / `vercel-cli-with-tokens` | Deploy to Vercel (incl. token auth). | STARS (vercel) |
| `documentation-and-adrs` | Write docs + ADRs for decisions. | STARS (addy) |
| `git-workflow-and-versioning` | Follow git workflow and versioning. Use for commits. | STARS (addy) |
| `context-engineering` | Engineer context for AI coding agents. | STARS (addy) |
| `deprecation-and-migration` | Manage deprecation and migration of old systems or APIs. | STARS (addy) |
| `shipping-and-launch` | Prepare production launches. Use when deploying to prod. | STARS (addy) |
| `writing-guidelines` | Review prose for Writing Guidelines compliance. | STARS (vercel) |
| `browser-testing-with-devtools` | Test in real browsers via Chrome DevTools MCP. | STARS (addy) |
| `webapp-testing` | Test web apps with Playwright. Use for UI testing. | STARS (anthropics) |
| `page-agent` | Drive a web page agent. Use for browser automation. | HUB |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

### Frontend Design & Anti-Slop
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `addyosmani/web-quality-skills` | 2,634 | **Addy Osmani's** Lighthouse/CWV optimization skills | **TOP** |
| `Leonxlnx/taste-skill` | 77,375 | Anti-slop "AI taste" — most-starred skill on GitHub | TOP |
| `Owl-Listener/designer-skills` | 2,096 | 107 skills: research→systems→UI→delivery | HIGH |
| `Railly/tinte` | 613 | Design system → SKILL.md + tokens.css compiler | HIGH |
| `plugin87/ux-ui-agent-skills` | 502 | Senior Design Architect: DTCG tokens, 42 components, WCAG 2.2 | HIGH |
| `kwakseongjae/oh-my-design` | 430 | 400+ quality-graded DESIGN.md references | MED |
| `wilwaldon/Claude-Code-Frontend-Design-Toolkit` | 643 | Skills+plugins+MCP for better frontends | MED |
| `Laith0003/ux-skill` | 61 | Deterministic anti-slop linter, 152 rules | MED |
| `superdesigndev/superdesign-skill` | 429 | "Stop shipping AI-slop UI" | MED |
| `feature-sliced/skills` | 82 | Feature-Sliced Design v2.1 frontend architecture | LOW |

### Backend & Performance
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `TencentCloudBase/skills` | 73 | 31 production backend (CloudBase/serverless) skills | MED |
| `traceloop/opentelemetry-mcp-server` | 198 | Query Jaeger/Tempo traces *(MCP)* | MED |
| `wieslawsoltes/Performance-Skill` | 32 | Cross-platform .NET perf engineering | LOW (non-JS) |
| `sql-optimizer` (Viprasol-Tech) | 0 | SQL tuning — EXPLAIN ANALYZE, indexes, N+1 | LOW |

---

## 🧩 MCP Servers (Frontend/Backend)

| Repo | ★ | What it gives | Key? |
|---|---|---|---|
| `codewithMUHILAN/Lightswind-UI-Library` | 888 | 160+ animated accessible React components + MCP | No |
| `benjaminr/chrome-devtools-mcp` | 303 | Real-browser DevTools protocol UI verification | No |
| `msw-mcp` (JasonBoy) | 81 | Mock Service Worker for AI agents | No |
| `opentelemetry-mcp-server` (traceloop) | 198 | OTel traces query (Jaeger/Tempo) | Config |

---

## ⚠️ Notes
- `taste-skill` is the single highest-value anti-slop addition — author it when expanding.
- The Vercel/Anthropic/addy packs are the current backbone; the research list is the expansion path.
- Performance skills overlap deliberately (Vercel rules + addy web-quality) — they compose.

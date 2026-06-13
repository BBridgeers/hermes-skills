# Skill-to-Agent Mapping Reference

## 3-Tier Skill Architecture

Every agent in a Hermes swarm workforce should have a 3-tier skill stack:

```
Tier 1: [swarm-worker-core]              ← Base: coordination framework
Tier 2: [{worker-id}-core]               ← Core: custom system prompt
Tier 3: [domain-matched skills...]       ← Domain: 2-19 function-specific skills
```

## Domain Matching Rules

| Agent Type | Skill Categories | Example Skills |
|------------|-----------------|----------------|
| Orchestrator/Command | kanban, subagent, plans, goals, monitoring, comms | kanban-orchestrator, writing-plans, goal-tracker, hermes-heartbeat, skill-health, slack-context-sync |
| Builder/Coder | code editing, TDD, debugging, GitHub, coding subagents | code-editing-discipline, test-driven-development, systematic-debugging, github-pr-workflow, claude-code, codex, opencode |
| Maintainer | repo hygiene, backup, health, security | git-permission-fix, hermes-backup, hermes-vps-health-check, workflow-security-audit |
| Reviewer | code review, verification, contradiction spotting | code-review, github-code-review, requesting-code-review, codebase-inspection, security-guard |
| QA | browser testing, dogfood, debugging | dogfood, browser-testing-with-devtools, systematic-debugging, agent-browser, playwright-automation-fill-in-form |
| Knowledge/Research | deep research, arxiv, prism analysis, synthesis, protocols | Deep Research, mimic-perplexity-deep-research, arxiv, prism-full, prism-scan, prism-discover, prism-reflect, prism-3way, protocol-handbook-authoring |
| Strategist | startup frameworks, positioning, research, analysis | startup-architect, ideation, blue-ocean-strategy, obviously-awesome, crossing-the-chasm, polymarket |
| Security | security guard, incident response, health | security-guard, skill-security-scan, workflow-security-audit, incident-commander, vuln-scanner |
| Startup/Ideation | lean, positioning, validation, strategy, messaging | lean-startup, jobs-to-be-done, mom-test, design-sprint, made-to-stick, storybrand-messaging, hundred-million-offers |
| Communications | email, humanizer, messaging, docs | himalaya, google-workspace, humanizer, slack-digest, output-formatting, idea-capture |
| Automation/Process | tool building, webhooks, monitoring, self-improvement | tool-builder, webhook-subscriptions, hermes-heartbeat, self-improve, skill-repair, cronjob |
| Vehicle Sourcing | scraping, browser automation, extraction | fb-marketplace-stealth-scraper, scrapling, craigslist-jsonld-scraper, multi-tier-ai-extraction, agent-browser |
| Career/Job | research, negotiation, humanizer, docs | Deep Research, negotiation, humanizer, powerpoint, google-workspace, goal-tracker |
| Housing/Rental | scraping, maps, negotiation, outreach | craigslist-jsonld-scraper, maps, negotiation, humanizer, scrapling |

## External Skill Import Protocol

When enriching from public GitHub skill repos:

1. Identify top repos by star count, community recognition, and SKILL.md presence
2. Clone to `/tmp/` for analysis — never directly to `~/.hermes/skills/`
3. Run TWO security scans:
   - Broad: regex scan for CRITICAL patterns across all files
   - Deep: targeted manual scan on each SKILL.md you plan to import
4. Most broad-scan hits are false positives — documentation text using "token", "secret", "system prompt" in URLs
5. Only REAL threats (prompt override directives, shell injection, zero-width obfuscation) block import
6. Import clean skills to `~/.hermes/skills/` (absolute path — not `os.path.expanduser`)
7. Map imported skills to the domain tier of relevant agents

| Top Public Skill Repos (as of 2026-05)

## Differentiated External Skill Assignment — Critical Rule

When assigning skills from external repos (2 per agent from each of 3 repos = 6 per agent × 60 agents = 360 assignments), each agent must get genuinely different picks. The same pod should NOT get the same skills:

| Pod | Agent 1 (anthropics picks) | Agent 2 (anthropics picks) | Shared? |
|-----|---------------------------|---------------------------|:---:|
| Core Command | swarm-orchestrator: `skill-creator`, `mcp-builder` | chief-of-staff: `internal-comms`, `doc-coauthoring` | 0/2 |
| Career | role-match: `skill-creator`, `internal-comms` | resume-tailor: `canvas-design`, `internal-comms` | 1/2 |
| Housing | housing-sourcing: `webapp-testing`, `skill-creator` | landlord-fit: `internal-comms`, `skill-creator` | 1/2 |

**Anti-pattern:** Import 17 skills, assign the same 6 skills to 60 agents. Result: "17 is laughable at best."

**Correct pattern:** Import 48+ skills, every agent gets unique combinations drawn from 56+ available skills. Target: 48-56 unique imported skills producing 360 differentiated assignments.

After mapping, verify diversity: agents in the same pod should share at most 1-2 of 6 external skills. If two agents in the same pod share all 6, the mapping is broken.

| Repo | Skills | Security | Best For |
|------|--------|----------|----------|
| anthropics/skills | Official Anthropic | ✅ CLEAN | skill-creator, mcp-builder, webapp-testing, doc skills |
| ComposioHQ/awesome-claude-skills | 1000+ community | ✅ CLEAN | content-research-writer, lead-research, resume-tailor |
| heilcheng/awesome-agent-skills | Community index | ✅ CLEAN | developer-growth, productivity skills |

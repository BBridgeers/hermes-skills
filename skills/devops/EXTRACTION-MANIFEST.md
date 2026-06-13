# Aeon → Hermes Skill Extraction Manifest

**Last updated:** 2026-05-04 21:15 UTC
**Total extracted:** 19 skills + SOUL.md identity layer

---

## Extracted Skills — Wave 1 (May 2, 2026)

### 1. hermes-heartbeat
- **Source**: Aeon `skills/heartbeat/SKILL.md`
- **Hermes path**: `devops/hermes-heartbeat/`
- **Supporting files**:
  - `references/heartbeat-checks.md` — Command quick-reference for all P0-P3 checks
- **Dependencies (Hermes tools)**: cronjob, session_search, send_message
- **Env vars**: None specific (uses existing: OPENROUTER_API_KEY)
- **Aeon dependency**: self-contained

### 2. skill-repair
- **Source**: Aeon `skills/skill-repair/SKILL.md`
- **Hermes path**: `devops/skill-repair/`
- **Supporting files**:
  - `references/repair-playbooks.md` — Full 10-category playbook reference
  - `templates/skill-repair-history.json` — Cooldown state template
- **Dependencies (Hermes tools)**: session_search, patch
- **Env vars**: None specific
- **Aeon dependency**: `depends_on: [skill-health]` — fulfilled (skill-health extracted May 3)

### 3. hermes-onboard
- **Source**: Aeon `skills/onboard/SKILL.md` + `onboard` CLI script
- **Hermes path**: `devops/hermes-onboard/`
- **Supporting files**:
  - `references/onboard-checks.md` — All 10 checks with verify/fix commands
- **Dependencies (Hermes tools)**: cronjob, terminal, memory
- **Env vars**: OPENROUTER_API_KEY, DEEPSEEK_API_KEY
- **Aeon dependency**: self-contained

### 4. security-guard
- **Source**: Aeon `CLAUDE.md` (security section) + `skills/skill-security-scan/scan.sh`
- **Hermes path**: `devops/security-guard/`
- **Supporting files**:
  - `references/injection-patterns.md` — HIGH/MEDIUM/LOW severity patterns + response protocols
  - `scripts/scan-skill.sh` — Scans SKILL.md files for security issues
- **Dependencies (Hermes tools)**: None (passive rules + standalone script)
- **Aeon dependency**: Not a skill in Aeon — extracted from CLAUDE.md agent identity rules

---

## Extracted Skills — Wave 2 (May 3, 2026)

### 5. skill-health
- **Source**: Aeon `skills/skill-health/SKILL.md`
- **Hermes path**: `skills/skill-health/`
- **Aeon concept**: Daily skill classification — "how broken is each skill?" State-change-gated notifications. P0-P3 priority tiering.

### 6. skill-analytics
- **Source**: Aeon `skills/skill-analytics/SKILL.md`
- **Hermes path**: `devops/skill-analytics/`
- **Aeon concept**: Fleet-level skill-run analytics with rolling metrics and trend detection.

### 7. skill-security-scan
- **Source**: Aeon `skills/skill-security-scan/scan.sh` + security patterns
- **Hermes path**: `skills/skill-security-scan/`
- **Aeon concept**: Audit skills and companion scripts for injection, secret leaks, and unsafe shell patterns.

### 8. skill-update-check
- **Source**: Aeon skill update tracking patterns
- **Hermes path**: `skills/skill-update-check/`
- **Aeon concept**: Check installed skills for upstream git changes and drifts.

### 9. self-improve
- **Source**: Aeon `skills/self-improve/SKILL.md`
- **Hermes path**: `skills/self-improve/`
- **Aeon concept**: Every-other-day optimization — "can I make anything better?" One fix per run. Score-floor gating.

### 10. weekly-review
- **Source**: Aeon reflection/review patterns
- **Hermes path**: `skills/weekly-review/`
- **Aeon concept**: KALM retrospective grounded in objective metrics.

### 11. goal-tracker
- **Source**: Aeon goal and issue tracking patterns
- **Hermes path**: `skills/goal-tracker/`
- **Aeon concept**: Quantified goal progress with OKR-style status, velocity tracking.

### 12. vuln-scanner
- **Source**: Aeon security scanning patterns
- **Hermes path**: `skills/vuln-scanner/`
- **Aeon concept**: Audit trending repos for real security vulnerabilities.

### 13. github-trending
- **Source**: Aeon content monitoring patterns
- **Hermes path**: `skills/github-trending/`
- **Aeon concept**: Curated trending GitHub repos — clustered, filtered, and ranked.

### 14. vibecoding-digest
- **Source**: Aeon digest/summarization patterns
- **Hermes path**: `skills/vibecoding-digest/`
- **Aeon concept**: Decision-ready pulse of r/vibecoding — ranked by signal strength.

### 15. external-feature
- **Source**: Aeon `watched-repos.md` + external monitoring patterns
- **Hermes path**: `skills/external-feature/`
- **Aeon concept**: Proactively enhance watched repos — fix issues, add features.

### 16. tool-builder
- **Source**: Aeon `skills/tool-builder/SKILL.md`
- **Hermes path**: `skills/tool-builder/`
- **Aeon concept**: Build automation scripts from recurring command patterns. Score-floor gating (won't build if score < 4).

### 17. autoresearch
- **Source**: Aeon autonomous research patterns
- **Hermes path**: `skills/autoresearch/`
- **Aeon concept**: Evolve a skill by generating variations, evaluating, and selecting best.

### 18. workflow-security-audit
- **Source**: Aeon security audit + CLAUDE.md patterns
- **Hermes path**: `devops/workflow-security-audit/`
- **Aeon concept**: Audit cron jobs, shell scripts for injection vectors, secret exposure, unsafe patterns.

### 19. skill-leaderboard
- **Source**: Aeon skill quality scoring + ranking patterns
- **Hermes path**: `skills/skill-leaderboard/`
- **Aeon concept**: Weekly ranking of which skills are most popular across the ecosystem.

---

## SOUL.md
- **Source**: Aeon `soul/SOUL.md` + `soul/STYLE.md` concept
- **Hermes path**: `/root/.hermes/SOUL.md`
- **Purpose**: Identity layer separate from system prompt. Read by skills when generating user-facing content.

---

## Skills Genuinely NOT Extracted (and why)

| Aeon Skill | Reason |
|------------|--------|
| skill-evals | Requires evals.json assertion framework and per-run output capture not yet in Hermes |
| reflect | Memory pruning — Hermes uses Honcho differently, concept adapted into weekly-review |
| cost-report | Adapted separately — token tracking uses OpenRouter API, different architecture |
| fork-fleet / fleet-control | Instance spawning — Hermes architecture doesn't support this |
| All crypto/market skills (16) | User explicitly declined crypto |
| All social media skills (7) | Hermes has xurl for X/Twitter, reddit-digest for Reddit |
| All research/content skills (17) | Hermes has equivalents (arxiv, youtube-content, blogwatcher, deep-research) |

---

## Changelog

- **2026-05-04**: Manifest updated from 4 to 19 extracted skills. Wave 2 (May 3) skills added. "Not Extracted" table corrected — many skills previously listed there were actually extracted in Wave 2.

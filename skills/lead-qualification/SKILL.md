---
name: lead-qualification
description: DFW prospect scoring via tech stack detection, ICP scoring, and hiring signals.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Leads, Qualification, GTM]
    related_skills: [dfw-web-design-now, competitor-research]
---

# Lead Qualification

Score DFW prospects before outreach so effort goes to high-fit leads.

## Pattern
Use `mcp-gtm-suite` to detect tech stack, ICP fit, hiring signals, and LinkedIn presence. Output a qualified/not-qualified verdict with reasoning.

## Protocol

1. **Input lead**
   - Business name, website (if any), city, GMaps URL.
2. **Tech stack detection**
   - Call `mcp-gtm-suite` tech stack tool on domain.
   - Note: CMS, analytics, chat widget, e-commerce platform.
3. **ICP scoring**
   - Score 0-100 based on:
     - No website or very old website (+40)
     - Local service business in DFW (+30)
     - Has phone number and physical address (+20)
     - No active paid ads / poor SEO (+10)
4. **Hiring signals**
   - Job postings for web/marketing roles (+10).
   - Recent funding or expansion news (+10).
5. **LinkedIn resolution**
   - Find decision-maker (owner, GM, marketing manager).
6. **Verdict**
   - `qualified`: score >= 70
   - `nurture`: score 40-69
   - `disqualified`: score < 40
7. **Record**
   - Insert into `client-data` with status and score.
   - Pass qualified leads to outreach workflow.

## Output Format
```markdown
## Lead: <Business>
- Score: 78/100
- Verdict: qualified
- Reasoning: No website, HVAC niche in Plano, phone verified, owner on LinkedIn.
- Recommended action: Build spec + in-person pitch within 48h.
```

## Failure Modes
- Qualifying without verifying the business is still open.
- Ignoring negative signals (recent bad reviews, lawsuits).
- Not recording disqualification reasons, causing repeated outreach.

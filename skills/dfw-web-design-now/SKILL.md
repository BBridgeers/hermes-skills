---
name: dfw-web-design-now
description: Complete DFW Web Design NOW — AI-powered web design agency for DFW small businesses. Algorithmic Arbitrage model (V2). Ghost-lead hunting, spec builds, Show & Tell sales, Landlord hosting.
version: 2.4
triggered-by: Blake Bridgers — DFW Web Design NOW LLC (Texas LLC, not yet filed — delay until first sale closes)
last-updated: 2026-06-13
---

# DFW Web Design NOW — Complete Stack

## Pattern
AI-powered web design agency targeting DFW small businesses without websites (ghost leads). Core loop: scrape Google Maps for businesses with no website → pre-build their site using html.to.design + Claude/Gemini → walk in with laptop and pitch Track A or B → lease/sell → build asset library for compounding efficiency.

## Pricing

| Product | Price | Notes |
|---------|-------|-------|
| **Track A — Growth Lease** | $1,500 setup + **$300/month** | 12-mo minimum. Then auto-renews. Bumps to $1,995 setup after first 5 clients. |
| **Track B — Enterprise Buyout** | $5,500 one-time + $99/month | Mandatory Year 1 maintenance retainer (hosting, SSL, security patches). Optional after Y1. Full IP transfer included. |
| **CI Wedge** | $497 | 15-page competitive intelligence report. Credited back if they sign Track A/B within 30 days. |
| **Local SEO Dominator** | $499/month | GMB posts, photo uploads, citation management (100% margin — n8n automated) |
| **Content Engine** | $299/month | 4 AI-written SEO blog posts/month (99.8% margin) |
| **Reputation Defense** | $199/month | Automated SMS review requests, bad review gating (99.5% margin) |
| **CI Monitoring** | $199/month | Monthly competitor re-scan + change alerts (99.8% margin) |
| **Priority Speed** | $500 one-time | "Skip the line" 48hr guaranteed launch |
| **Accessibility Audit** | $997 one-time | ADA compliance report (essential for medical/legal) |
| **Digital Renovation** | $2,000 setup | SEO-preserving refresh for old sites |

## Tech Stack (Finalized June 2026)

| Component | Choice | Why |
|-----------|--------|-----|
| Code Generation | Claude Opus 4.1 / DeepSeek V4 Pro | Primary build engine |
| Competitor Capture | html.to.design | DOM-to-Figma extraction |
| Hosting | **Vercel** | Better AI SDK, better Next.js than Netlify. Free tier sufficient. |
| Payments | **Stripe** | 2.9% + $0.30, US-only, single jurisdiction. No MoR needed. |
| Lead Scraping | **Playwright self-scraper** | Custom Google Maps scraper. Free. Replaces Apify. |
| Lead Verification | **Google Places API** | Official Google data. $200/month free credit. Key at /tmp/gcp_key.txt |
| Owner Enrichment | **3-Tier Architecture** (TDLR bulk CSV + Comptroller API + OpenCorporates → browser-use agent for County DBA/BBB/SOS → Exa + SpiderFoot) | Current script broken (0/428). See `references/enrichment-failure-diagnosis.md`. Rewrite pending. |
| Automation | **n8n** (self-hosted on DigitalOcean) | Workflow automation |
| CRM/Database | **Notion** | Lead tracking, client DB, component library |
| DNS/CDN | **Cloudflare** | Free tier |
| Email Delivery | **Resend** (pending) | Modern Postmark alternative |
| Credential Vault | **1Password** / Bitwarden | Team credential management |

## Workflow

1. **Scrape**: `maps_ghost_hunter.py` or `maps_ghost_hunter_overnight.py` — Playwright Google Maps scraper. 14 verticals × 16 DFW cities. Outputs ghost_leads.csv.
2. **Verify**: Google Places API lookup for each ghost → confirm business exists, confirm no website
3. **Enrich**: `scripts/enrich_waterfall.py` — **CURRENTLY BROKEN** (0/428, June 2026). All 7 HTTP-based sources failed: SOSDirect requires $1/search account + MFA, TDLR should be bulk CSV not scraping, BBB blocks bots silently, County DBA portals require browser access with CAPTCHAs. The correct architecture is a **3-tier enrichment system** (see `references/enrichment-failure-diagnosis.md`): TIER 1 (no-friction): TDLR bulk CSV from data.texas.gov + Texas Comptroller API + OpenCorporates. TIER 2 (browser agent): browser-use + real Chromium for County DBA portals + BBB + TX SOS. TIER 3 (fallback): Exa Neural Search + SpiderFoot. ~30-40% of leads are trades (solvable via TDLR bulk), ~25-30% are incorporated (Comptroller/OpenCorporates), ~30-40% are sole proprietors (county DBA or SpiderFoot). The script must be rewritten to this architecture before enrichment can succeed.
4. **Heat-Map ALL Enriched Leads**: After enrichment completes, score EVERY ghost on: emergency vertical (2x weight), city affluence, owner name confidence, review count, phone verified. Output ranked top 10. NEVER pre-select a target before enrichment data lands — data decides, not stale assumptions.
5. **Pre-Build** (SPEC-BUILD/): Complete 8-phase build workflow in `spec-build/BUILD_WORKFLOW.md` — 500-Mile Donor Rule, html.to.design capture, sanitization (Lipsum + Lorem Picsum + Blind Text Generator), 3-part prompt system (SYSTEM_INSTRUCTION.md → Business Packet → CLAUDE_PROMPT_TEMPLATE.md), multi-component Next.js App Router output, visual debugging loop, Vercel deploy (vercel.json), component extraction to asset library. All Netlify references purged June 2026.
6. **Walk In**: PITCH_SCRIPT.md — 2-min hook → 5-min reveal → 3-min value framing → close
7. **Close**: Stripe Payment Link for Track A activation ($1,500 or $1,995) or Track B deposit ($2,750)
8. **Launch**: DNS cutover, remove password, site live same day
9. **Recurring**: Track A: $300/month auto-billed. Track B: $99/month maintenance. Upsell Track C add-ons at month 3+.

## Formation (Pending — File After First Sale)

**Strategy:** Delay $300 LLC filing fee until first signed proposal + payment. Sell as sole proprietor (Blake Bridgers d/b/a DFW Web Design NOW), file LLC the same day funds clear. Take payment via personal Stripe/Cash App/Zelle in the interim. Once filed, EIN is immediate (irs.gov, 10 min), and bank account follows.

**Total cost:** $375 filings + $125/yr registered agent = $500 first year

All 6 formation docs are ready in `formation/` — every form and every filing portal has a direct clickable hyperlink (44 total links):

| File | Purpose | Key Links |
|------|---------|-----------|
| `FORMATION_CHECKLIST.md` | 7-step master checklist, parallel diagram | SOSDirect, Form 205 PDF, irs.gov/ein, Form 503 PDF, Northwest RA, Mercury, Relay, Chase, Stripe, TX Franchise Tax |
| `OPERATING_AGREEMENT.md` | 10-article Texas single-member LLC agreement | Ready to sign — just needs Blake's name + date |
| `ARTICLES_OF_ORGANIZATION_GUIDE.md` | Form 205 field-by-field walkthrough | SOSDirect, name availability search, Northwest RA signup, Form 501 (name reservation) |
| `EIN_APPLICATION_GUIDE.md` | IRS SS-4 step-by-step with exact answers | irs.gov/ein |
| `DBA_FILING_GUIDE.md` | Form 503 for "DFW Web Design NOW" + "Velocity Labs" ($25 each) | Form 503 PDF, Form 504 (abandonment) |
| `BANKING_SETUP_GUIDE.md` | Mercury/Relay/Chase comparison + application steps | All three bank signup pages |

**Recommended:** Northwest Registered Agent ($125/yr) — keeps Blake's temporary WoodSpring Suites address off permanent public SOS records.

| File | Location | Purpose |
|------|----------|---------|
| MASTER_EXECUTION_DOC.md | repo root | Project status, decisions, blockers |
| ROI_BRIEFING_DOC.md | repo root | Client-facing ROI proof document |
| FINAL_PRICING_SHEET.md | repo root | Internal + external pricing |
| MASTER_ENRICHED.csv | DFW-Web-Design-NOW/ | 91 prioritized leads (799 true ghosts post-optimized scrape) |
| CLEAN_TRUE_GHOSTS.csv | DFW-Web-Design-NOW/ | 799 verified ghost leads (second optimized scraper run) |
| maps_ghost_hunter_overnight.py | DFW-Web-Design-NOW/ | Overnight ghost scraper |
| scripts/enrich_waterfall.py | scripts/ | 7-source owner enrichment waterfall (ONLY enrichment script — others deleted) |
| spec-build/CLAUDE_PROMPT_DOSSIER.md | spec-build/ | Growing prompt engineering reference — 10 techniques from Anthropic Cookbook, frontend-design skill (277K+ installs), MindStudio, awesome-claude-design, Reddit, Vellum |
| spec-build/BUILD_WORKFLOW.md | spec-build/ | 8-phase build workflow (rewritten: Vercel, 30k doc integrations, asset library bootstrapping) |
| spec-build/CLAUDE_PROMPT_TEMPLATE.md | spec-build/ | 3-part prompt system: System Instruction + Business Packet + Generation Prompt (3 modes) |
| spec-build/SYSTEM_INSTRUCTION.md | spec-build/ | Locked cacheable Part A — all design rules, code quality, file structure (11 XML-tagged sections) |
| spec-build/vercel.json | spec-build/ | Vercel deploy config (framework: nextjs, auto-deploy). netlify.toml DELETED. |
| sales/PITCH_SCRIPT.md | sales/ | Full Show & Tell sales script |
| sales/PROPOSAL_TEMPLATE.md | sales/ | Client-facing proposal |
| sales/CALENDLY_TEMPLATE.md | sales/ | 15-min discovery call setup |
| sales/stripe/STRIPE_SETUP.md | sales/stripe/ | Stripe link generation guide |
| formation/FORMATION_CHECKLIST.md | formation/ | 7-step formation checklist (26 links) |
| formation/OPERATING_AGREEMENT.md | formation/ | Ready-to-sign single-member LLC agreement |
| formation/ARTICLES_OF_ORGANIZATION_GUIDE.md | formation/ | Form 205 field-by-field |
| formation/EIN_APPLICATION_GUIDE.md | formation/ | IRS SS-4 step-by-step |
| formation/DBA_FILING_GUIDE.md | formation/ | Form 503 DBA filing for both brands |
| formation/BANKING_SETUP_GUIDE.md | formation/ | Mercury/Relay/Chase setup |
## Pitfalls

- **Never pre-select a spec build target before enrichment completes**: AquaPure Plumbing was #1 from the old 428-lead batch. With 799 fresh ghosts and full enrichment, rank ALL leads with weighted scoring (emergency vertical ×2, affluence, owner confidence, reviews, phone). Data decides the top target — not inertia.
- **enrich_waterfall.py returned 0/428**: The 7-source waterfall is architecturally broken for HTTP scraping. TX SOS requires $1/search + MFA, TDLR should use bulk CSV not scraping, BBB blocks bots, County DBA portals require browser access. The correct fix is a 3-tier architecture: TDLR bulk CSV + Comptroller API (Tier 1) → browser-use agent for county portals (Tier 2) → Exa + SpiderFoot (Tier 3). Full diagnosis and fix at `references/enrichment-failure-diagnosis.md`. Do NOT re-run the existing script — it will fail identically. Rewrite first.
- **Don't confuse DETOXXX vs DFW projects**: Separate codebases, separate objectives. Don't cross-reference files.
- **File LLC AFTER first sale**: User explicitly decided to delay $300 filing fee until first signed proposal + payment clears. Sell as sole proprietor in the interim. The formation package is ready to execute same-day.
- **Deliberate before executing rewrites or structural changes**: User wants to discuss ideas and deliberate BEFORE code/files are written — especially for build stack, workflow, and architecture decisions. Do NOT jump to execution on structural changes until alignment is confirmed. Multiple "stop / cease work / STPPP god damnit" signals during the June 12 build stack rewrite session were caused by premature execution before deliberation completed. The pattern is: analyze → surface options → deliberate → get confirmation → THEN execute.
- **Workflow documentation format**: When presenting workflow, process, or build pipeline documentation, always provide BOTH narrative form (prose describing the logic and decisions) AND visual logic flow (ASCII diagrams, process flows, decision trees). User explicitly requested this dual-format for the build workflow rewrite on June 12. A narrative-only or diagram-only output is incomplete. The visual flow helps ADHD-wired operators track the pipeline at a glance; the narrative explains WHY each step exists.
- **Claiming side effects without verification**: Never claim a file was synced to GDrive, pushed to GitHub, or otherwise persisted until you have actual tool output confirming it. User caught a hallucination on June 12 where GDrive sync was claimed before verification. Every external side-effect claim must be backed by verification output in the same turn.

## Build Stack Reference

The complete spec-build package is in `spec-build/`:
- **BUILD_WORKFLOW.md** — 8-phase workflow (rewritten June 2026: Vercel, 30k doc integrations, AA thesis, asset library bootstrapping, visual debugging loop, Landlord Lock)
- **CLAUDE_PROMPT_TEMPLATE.md** — 3-part prompt system (System Instruction + Business Packet + Generation Prompt) with 3 modes: From Donor Design, Pure Assembly, CI-Only
- **SYSTEM_INSTRUCTION.md** — Locked cacheable Part A: 11 XML-tagged sections covering role, tech stack, mobile-first rules, code quality, output rules, required sections, file structure, CI analysis schema, legal safeguards, model strategy
- **vercel.json** — Vercel deploy config (framework: nextjs). netlify.toml DELETED.

## First Spec Build Target

**Determined by heat-map post-enrichment — not pre-selected.** After `enrich_waterfall.py` completes on the 799 fresh ghosts, score ALL leads on: emergency vertical (×2), city affluence, owner confidence, reviews, phone verification. Build specs for the top 3-5 in parallel if capacity allows. AquaPure Plumbing Solutions (Southlake, 817-424-8800) was #1 from the old 428-lead batch. It may or may not hold the top slot against the new data.

## GitHub
- Repo: `github.com/BBridgeers/dfw-web-design-now` (private)
- Auth: PAT at /tmp/gh_token.txt

## GCP (Google Places API)
- Project: 766967393423
- API Key: /tmp/gcp_key.txt
- Places API (New) enabled
- $200/month free credit

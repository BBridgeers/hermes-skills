# Refined Build Stack — DFW Web Design NOW (June 2026)

Full synthesis of V2 doctrine + 30k execution prompt + external research + user direction. This document is the canonical reference for the spec build pipeline.

## Architecture: 3-Part Prompt System

**Part A — SYSTEM_INSTRUCTION.md** (locked, cacheable, versioned)
- Role: Senior Frontend Engineer
- Tech: Next.js 14 App Router, TypeScript, Tailwind CSS 3.4+, Lucide Icons, system font stack
- Rules: Mobile-first 390px, 44px touch targets, semantic HTML5, heading hierarchy, ARIA labels, skip-to-content, lazy loading below fold
- Output: Multi-component file structure (app/page.tsx, app/layout.tsx, app/globals.css, components/hero.tsx, components/services.tsx, components/about.tsx, components/reviews.tsx, components/contact.tsx, components/navbar.tsx, components/footer.tsx, next.config.js, tailwind.config.js, postcss.config.js, package.json)
- Phone in: navbar, hero, sticky mobile CTA, contact section, footer
- City in: hero subheadline, about section, contact, schema markup
- Never: login buttons, search bars, dashboard widgets, "Lorem ipsum"

**Part B — Business Packet** (per-target, from lead data)
- Business name, phone, city, vertical, services list, Google rating + review count, emergency flag

**Part C — Generation Prompt** (3 modes):
1. **From Donor Design**: Attach 390px PNG from Figma → "Replicate layout structure, spacing rhythm, visual hierarchy exactly"
2. **Pure Assembly**: "Use component library — hero-02 + services-grid-01 + contact-standard" (for repeat verticals)
3. **CI-Only Report**: 5-section Market Dominance Report (Executive Summary → Threat Landscape → Gap Analysis → Blueprint → Action Plan)

## 8-Phase Build Workflow

### Phase 0: Pre-Flight (5 min)
1. Select target from heat-mapped lead list
2. Identify 3-5 donor sites (500-Mile Rule: same vertical, DIFFERENT geography — never local competitors)
3. Capture donors: html.to.design Chrome Extension → 390px viewport → Full Page (DevTools: 390w × 5000h) → scroll to trigger lazy load → open accordions/menus → capture
4. Sanitize in Figma: Similayer strip images, replace branding → Lipsum/Blind Text Generator for text → Lorem Picsum for images
5. Export @2x PNG (390px wide, full page height)

### Phase 1: Prompt Assembly (10 min)
Load Part A (SYSTEM_INSTRUCTION.md) + build Part B (Business Packet) + write Part C (Generation Prompt, Mode 1)

### Phase 2: Code Generation
Feed 3-part prompt to Claude/DeepSeek → all files output in one response

### Phase 3: Project Scaffold
mkdir → create files → npm install → npm run build → npm run dev → verify localhost:3000

### Phase 4: Visual Debugging Loop
Screenshot rendered site at 390px → feed back to Claude with original donor PNG → "Compare and fix discrepancies in padding, font sizing, spacing, color" → repeat max 2x

### Phase 5: Deploy to Vercel
`npx vercel --prod --confirm` (vercel.json pre-configured: framework nextjs, build npm run build, output .next)

### Phase 6: Component Extraction
Identify reusable components → extract to `/component-library/[vertical]/[component-name].tsx` → strip client-specific content → parameterize with props → tag in Notion

### Phase 7: Password Protect + Pitch Assets
Vercel Authentication or Next.js middleware gate → capture mobile + desktop screenshots → generate SALES_BRIEF.md

### Phase 8: Landlord Lock
Client site on YOUR Vercel team. Client never gets credentials. Updates via email → git commit → auto-deploy.

## Asset Library Bootstrapping Strategy

Start from zero. To bootstrap fast:
- Option A: Use Manus (via Meta partnership) @ $34/month for SimilarWeb integration — mass-identify top-performing sites per vertical, then clone/sanitize/extract through standard pipeline
- Option B: Open-source alternative to SimilarWeb — research active GitHub projects (no definitive replacement identified yet)
- Option C: Manual — capture 5-10 world-class donor sites per vertical, extract 20-30 components each → seed library with 80-120 components pre-first-client

## Key Integrations from 30k Execution Prompt

1. **AA Thesis framing** — "We ALREADY built this. Want to keep it?" (not "We CAN build")
2. **500-Mile Donor Rule** — never clone from same metro/state as client
3. **CI Report 5-section structure** — Executive Summary → Threat Landscape → Gap Analysis → Blueprint → Action Plan
4. **CI JSON output schema** — prioritized recommendations with type/title/description/impact fields
5. **CI Wedge: $497 credited if sign within 30 days** — sunk-cost psychology
6. **Golden Parachute Buyout formula** — $5,500 - $1,500 - ($300 × months paid). After ~20 months, zero buyout
7. **Digital Eviction timeline** — Day 1 email, Day 3 SMS, Day 6 password-protect + $150 reactivation fee
8. **ARPU upsell cadence** — Month 1 SEO, Month 2 Content, Month 3 Reputation, Month 6 CI Monitoring
9. **Landlord Lock** — client never gets hosting credentials
10. **IP/Copyright risk mitigation** — out-of-market donors, sanitize assets, prompt excludes donor URLs

## Enrichment: Current State

**enrich_waterfall.py returned 0/428 (June 2026).** Correct 3-tier architecture documented in `references/enrichment-failure-diagnosis.md`. Rewrite pending.

## File Map

```
spec-build/
├── BUILD_WORKFLOW.md          ← 8-phase workflow (canonical)
├── CLAUDE_PROMPT_TEMPLATE.md   ← 3-part prompt system (3 modes)
├── CLAUDE_PROMPT_DOSSIER.md    ← Growing prompt engineering reference (10 techniques)
├── SYSTEM_INSTRUCTION.md       ← Locked Part A (11 XML-tagged sections)
└── vercel.json                 ← Vercel deploy config
```

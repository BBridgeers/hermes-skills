---
name: competitor-research
description: Fetch competitor websites, extract DOM hierarchy, component patterns, and color/font tokens for DFW benchmark analysis.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Research, Competitor, Fetch, DOM]
    related_skills: [dfw-web-design-now, client-site-audit]
---

# Competitor Research

Turn competitor URLs into structured benchmark inputs for the DFW discovery phase.

## Pattern
For each DFW niche (HVAC, plumbing, med spa, legal), fetch 3-5 top local competitor sites and extract: headline patterns, CTA placement, section order, color palette, typography, trust signals, and page structure.

## Protocol

1. **Receive target list** from the strategist or from `lead-qualification` output.
2. **Fetch each URL** with `fetch_mcp_mcp_fetch_markdown` and `fetch_mcp_mcp_fetch_html`.
3. **Extract structure**:
   - H1/H2 headings and their sequence.
   - CTA text and position.
   - Section types: hero, services, about, testimonials, contact, footer.
   - Images: hero type, icon style.
4. **Capture visual tokens**:
   - Use `browser_harness` to screenshot the page.
   - Record dominant colors and font families where visible.
5. **Compile benchmark report** at `/root/.dfw/research/<client>-competitors.md`.
6. **Feed into spec** by linking the report in the client spec file.

## Output Format

```markdown
# Competitor Benchmark — <Client> (<Niche>)

## Competitor A: <name> (<url>)
- Headline: ...
- CTA: ...
- Sections: ...
- Colors: ...
- Fonts: ...
- Trust signals: ...
- Weakness to exploit: ...
```

## Failure Modes
- Fetching only one competitor produces a distorted benchmark.
- Screenshots without alt text or DOM notes are unusable for spec.
- Forgetting to record page load speed or mobile experience.

---
name: client-site-audit
description: Pre-redesign audit of a client’s existing site — download, inventory, tech stack, and output a structured report.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Audit, Website, Wget, Tech-Stack]
    related_skills: [dfw-web-design-now, competitor-research]
---

# Client Site Audit

Before redesigning a client’s existing site, mirror it, inventory assets, identify the tech stack, and produce a structured audit report.

## Pattern
A full site mirror plus tech detection gives DFW a defensible starting point and protects against missing pages during migration.

## Protocol

1. **Download site** with `website_downloader_download_website`:
   - Output to `/root/.dfw/audits/<client>/mirror/`
   - Default depth: 2 (expand if site is small).
2. **Inventory pages**:
   - List all `.html` files found.
   - Extract page titles and meta descriptions.
3. **Identify tech stack**:
   - CMS hints in HTML comments or generator meta tags.
   - CSS frameworks: search for `tailwind`, `bootstrap`, `bulma`.
   - JS frameworks: search for `react`, `vue`, `angular`, `next.js`.
   - Analytics: `gtag`, `gtm`, `fbq`, `plausible`.
4. **Catalog assets**:
   - Images, fonts, PDFs, videos in `/mirror/`.
   - Note sizes and formats.
5. **Fetch live page** for comparison with mirror if needed.
6. **Write report** to `/root/.dfw/audits/<client>/AUDIT_REPORT.md`.

## Report Template Sections
- Executive Summary
- Site Structure (sitemap)
- Technology Stack
- Asset Inventory
- SEO / Meta Overview
- Performance Observations
- Redesign Recommendations
- Risk Notes

## Failure Modes
- Mirroring with depth 0 and missing subpages.
- Not checking robots.txt or sitemap.xml.
- Overwriting a previous audit without versioning.

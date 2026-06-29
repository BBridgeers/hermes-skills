---
name: proposal-gen
description: Generate DFW client proposals using stored winning examples and the proposalcraft MCP tool.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Proposal, Sales, ProposalCraft]
    related_skills: [dfw-web-design-now, client-data]
---

# Proposal Generation

Turn a DFW client brief into a ready-to-send proposal using `proposalcraft` and a review gate.

## Pattern
DFW closes deals with fast, specific proposals. Store 2-3 winning examples, feed the brief, review the output, format, and send.

## Protocol

1. **Collect brief inputs**
   - Client name, niche, city
   - Services needed (site, copy, SEO, hosting)
   - Budget signal (if known)
   - Timeline
   - Competitor / audit notes
2. **Select example**
   - Pick the closest winning example from `/root/.dfw/proposals/examples/`.
   - Save winning proposals with `mcp_proposalcraft_save_proposal`.
3. **Generate draft**
   - Call `mcp_proposalcraft_draft_proposal` with brief + budget + deadline.
4. **Review gate**
   - Run `mcp_proposalcraft_improve_proposal` on the draft.
   - Check scope, pricing clarity, timeline, and DFW-specific terms (Landlord hosting option, Track A vs Track B).
5. **Format**
   - Convert to Markdown or PDF as needed.
   - Save to `/root/.dfw/proposals/<client>-<date>.md`.
6. **Send**
   - Record in `client-data` proposals table.
   - Send via email/Slack and mark status='sent'.

## Required Example Proposals
Store at least these in proposalcraft:
- `dfw-hvac-website` — Track A lease + Track B buy
- `dfw-plumbing-redesign` — one-time build
- `dfw-med-spa-package` — site + copy + hosting

## Failure Modes
- Generating without examples produces generic proposals.
- Skipping the review gate lets pricing errors reach the client.
- Not recording in `client-data` breaks pipeline tracking.

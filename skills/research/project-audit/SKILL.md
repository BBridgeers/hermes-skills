---
name: project-audit
description: Deep-dive project folder ingestion — pull everything from cloud storage, read every legible document, build a comprehensive profile, identify gaps, and produce a gap analysis with execution roadmap. For business plans, codebases, documentation projects, or any multi-file corpus that needs exhaustive review.
tags: [research, audit, project-management]
---

# Project Audit

## Why this exists

When a user has a massive project folder — business plans, legal docs, lead databases, research conversations, doctrine files — scattered across cloud storage and local drives, they don't want a summary. They want every word read, every file processed, every gap identified. This skill governs the exhaustive ingestion-and-analysis workflow.

## Trigger conditions

Load this skill when:
- User says "read every word of these folders" or "process everything"
- User provides paths to multi-file project directories (local or cloud)
- User asks for a "comprehensive profile" or "gap analysis" of a body of documents
- User references a project they've built up over time with 20+ files
- User mentions "V2-level completeness" or "what's the state of X"

## Protocol

### Phase 1: Ingestion — Get Everything Local

1. **Identify the source**. Determine whether files are on GDrive, a local path, Windows OneDrive, or elsewhere.
2. **Pull everything**. If cloud-based, use `rclone copy` to bring the entire folder structure local. Run parallel pulls for multiple folders. Accept that this takes time — use `background=true` with `notify_on_complete=true`.
3. **List before reading**. Always `rclone lsf` with `--max-depth 3` to see the full file tree before deciding what to read. This prevents missing buried subdirectories.
4. **Filter noise aggressively**. Skip cache files, app data (Adobe logs, Slack caches, Fing/remove.bg app data), Windows `.pf` prefetch files, and binary blobs that can't be read as text. Apply a filter: if a file in a subdirectory like `Fing/Cache/` or `slack/Code Cache/` has no project relevance, skip it.
5. **Confirm total scope**. If the user says "32,000+ files" but your listing shows 300, you're missing something. Drill into every subdirectory. The discrepancy usually means deeply nested folders weren't explored.

### Phase 2: Read Systematically

1. **Read in priority order**:
   - Business plan / master doctrine (the core document)
   - Financial models and projections
   - Legal/contractual documents
   - Lead databases and prospect lists
   - Research conversations (Perplexity, Claude chats)
   - Supporting appendices and reference docs
   - Pipeline data and execution artifacts
2. **Read FULL documents, not snippets**. When a document is 40K+ words, read it all — head/limit sampling produces a false picture. If a file exceeds terminal output limits, use `read_file` with pagination (`offset` + `limit`).
3. **Note anomalies immediately**. If Appendix A of a web design business plan contains tensor ring jewelry content, flag it as document integrity failure — don't assume it belongs.
4. **Cross-reference between documents**. When the doctrine says "217 qualified prospects" and the CSV has 50 lines, that's a gap. When the integration roadmap lists 10 amendments and only 5 have files, that's a gap.

### Phase 3: Build the Profile

Synthesize into a structured profile covering:

- **What It Is**: One-paragraph description of the project
- **What Got Built**: Everything that exists — documents, code, leads, plans
- **What Was NOT Built**: Everything that should exist but doesn't
- **Business Model**: Revenue tracks, pricing, margins, target market
- **Status Assessment**: V1 vs V2 level of completeness (see below for V2 criteria)
- **Document Integrity**: Any contamination, missing sections, version conflicts

### Phase 4: Gap Analysis

For each gap identified:
1. **What's missing** — specific file, section, artifact
2. **Why it matters** — what breaks without it
3. **What it takes to fill** — estimated time, dependencies
4. **Priority** — high/medium/low based on business impact

V2 completeness means: every section has hard gates (checklists you can't skip), every pillar is defined, dual-lane architecture is operationalized. If a project has a doctrine but no hard gates, it's V1 with V2 ambitions.

### Phase 5: Execution Roadmap

Produce a phased plan:
- **Phase 0 — Immediate Survival**: What the user needs to do today (housing, cash)
- **Phase 1 — Foundation**: First week actions to operationalize the project
- **Phase 2 — First Revenue**: Actions to generate money
- **Phase 3 — Systematize**: Actions to scale

### Phase 6: Deliver

Present the full audit as a structured response. Do NOT ask the user "do you want me to build the gaps?" — present the gaps, state what you would do, and ask ONE question: "Want me to build the gap-fill or help you start executing?"

## Pitfalls

- **Don't sample, read fully**. A 40K-word doctrine read at 600 lines gives a false understanding. The user knows their own documents — they'll catch skimming instantly.
- **Don't trust folder names alone**. Appendix A titled "Market Research" may contain completely unrelated content from another project. Verify by reading content.
- **Don't assume file counts from directory listings**. `lsf` only shows direct children. If the user says there are thousands of files, drill into every subfolder before concluding.
- **Don't deliver the audit without an execution recommendation**. The user wants to know "what do I do with this?" — always end with actionable phases.
- **Respect the user's current situation**. If the user is homeless and needs cash, the execution roadmap should account for survival needs first, project completion second.

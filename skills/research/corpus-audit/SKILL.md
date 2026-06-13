---
name: corpus-audit
description: Systematic chunked audit of large document corpora (100+ files) with state preservation, output redirection, and acceleration patterns. Use when auditing, validating, or analyzing a large collection of text documents against a structured framework.
tags: [research, audit, automation]
---

## Overview

When faced with auditing 100+ documents against a structured framework, inline chat rendering burns tokens and loses state. This skill encodes the chunked-audit pattern: process 10-15 files per pass, compile analysis to disk files, report progress via compact JSON status blocks in chat, and accelerate sampling when patterns crystalize.

## Triggers

- User asks to audit/validate/review a directory of 50+ documents or transcripts
- User provides a structured analysis framework (e.g., pharmacological validation, legal compliance, fact-checking)
- Any task where "read every word of 200+ files" is specified

## Steps

### 1. Scout the corpus
- Get file count and sort order (numeric/alphabetical/date)
- Read MASTER_INDEX or equivalent if present
- Estimate chunks needed (~15 files/chunk) and confirm with user

### 2. Create output directory
```bash
mkdir -p /path/to/audited_chunks
```

### 3. Process chunk N (repeat for all files)
- Read 10-15 files in parallel with `read_file`
- Apply the user's analysis framework to each file
- Write the full detailed analysis to `chunk_N_audited.md`

### 4. Chat response format
Use a compact JSON status block ONLY in the chat window:

```json
{
  "status": "Completed / Processing",
  "files_compiled_this_turn": ["file1.md", "file2.md", ...],
  "destination_path": "/path/to/audited_chunks/chunk_N_audited.md",
  "gdrive_sync": "Staged",
  "next_chunk_start": "fileX.md",
  "progress": "N/Total (X%)"
}
```

**Do NOT** render the full analysis inline — it wastes tokens and the user gets the file anyway.

### 5. State preservation
Every chunk file MUST end with:
```
- Files processed: X–Y of Total
- Last file: filename.md
- Next file: next_filename.md
```

### 6. Accelerate when patterns crystalize
By ~60-70% through the corpus, content patterns become predictable. Switch from reading every file to:
- Sampling key files that may contain new claims
- Batch-categorizing the rest by content type
- Writing compressed summaries for repetitive content

### 7. Final chunk: global summary
The last chunk should include a global audit summary with:
- Content evolution phases
- Total counts by claim category (validated/invalidated/no claims)
- Most dangerous claims ranked
- Most accurate content identified

## Output Structure Per File

For each document, use the user's framework. Common structure:
```
## FILE N: filename.md — Post ID (Date)
**Type:** | **Claim Domain:**

### Literal Claim
[Exact quote]

### Analysis / Pharmacological Profile
[Table or structured breakdown]

### Scientific Validation Matrix
- **Validated:** ...
- **Plausible but Unproven:** ...
- **Invalidated:** ...
```

## Pitfalls

- **Don't render full analysis in chat.** First chunk can be inline to show format; after that, redirect to disk + JSON status.
- **Don't lose state.** Always record last/next file. If session is interrupted, the next session can resume from the pointer.
- **Don't deep-analyze repetitive content.** After patterns crystalize, categorize and compress. The user wants thoroughness on claims, not redundancy on promotion/personal posts.
- **Don't skip the MASTER_INDEX.** It provides chronological context, content types, and engagement metrics that inform analysis priority.
- **15-file chunks are the sweet spot.** 10 is too slow for 200+ files. 20+ risks context exhaustion on long transcripts. 15 balances depth with throughput.

## Acceleration Signals

Switch to compressed/sampling mode when:
- 3+ consecutive files contain only personal/promo/meta content
- Same claim appears verbatim across 5+ posts (e.g., reposted reels)
- Content shifts to purely metaphysical/spiritual with no falsifiable claims

## Consolidated Skills

This skill absorbs: `exhaustive-read`.

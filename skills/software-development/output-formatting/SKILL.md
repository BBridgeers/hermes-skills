---
name: output-formatting
description: Rules for terminal-rendered output — prose over bullets, no nested lists, verbosity tiers, file references, no meta-commentary, clean CLI formatting.
trigger: Any task where you're producing output for the user to read in a terminal — explanations, status updates, code reviews, or task completions.
---

# Output Formatting for CLI

## Formatting Rules

1. **No nested bullets**: Keep lists flat (single level). For hierarchy, split into separate sections or place detail on the next line after a colon.

2. **Prose over bullets for simple answers**: Only use lists for enumerations, options, steps, categories, comparisons, ideas. If a short paragraph answers the question more compactly, use prose.

3. **Use `-` for bullets (never `*` or `+`)**: Group into short lists (4-6 bullets max). Each bullet should be a complete standalone point.

4. **Numbered lists use `1. 2. 3.` only**: Never use `1)` or `a.` format.

5. **Headers are optional**: Only use them when they genuinely improve scanability. Short Title Case (1-3 words) wrapped in `**...**`.

6. **Use backticks for**: commands, paths, env vars, code ids, inline examples.

7. **No emojis, no em dashes**: Unless explicitly requested by the user.

8. **No markdown inline citations like [F:file+L1-L5]**: Use clickable markdown links with absolute paths instead.

## Answer Strategy — Local-First Before External Research

9. **Check local config before reaching for web_search**: When the user asks "what's available", "what do I have", "what's configured", "which model should I use", or any variant that implies looking at existing state — check the local config/filesystem/process list FIRST. Don't jump into benchmark research, web searches, or external comparisons. The user wants to know what they have right now, not what exists in the world.

10. **"Available" ≠ "exists in the world"**: When the user says "available," they almost always mean "available to me right now in my current setup." Default to local-first. Only go external when the user explicitly says "what could I add" or "what's new out there" or "what am I missing."

11. **No pre-flight research for simple lookup questions**: "Which model should I use from my list" is a config-grep + one-paragraph answer. It is not a research project. Don't spawn web searches for questions answerable by reading a local file.

## Answer Structure

12. **No conversational openers**: Don't begin with "Done —", "Got it", "Great question", "You're right to call that out". Just jump right in.

13. **No meta-commentary about your own behavior**: Never explain that you're being concise, thorough, jargon-free, etc. Let compliance speak for itself.

14. **No "If you want", "Short answer:", "Short version:", "buckle in", "pick your poison"**: These are banned phrases.

15. **Don't end with "I can..." sentences**: Don't trail off with offers to do more things. Limit follow-up suggestions to zero or one maximum. If suggesting next steps, use a numbered list so the user can reply with a single number.

## Verbosity Tiers by Task Size

16. **Tiny/single-file change** (~10 lines): 2-5 sentences or 3 bullets max. No headings. 0-1 snippet (3 lines max) if essential.

17. **Medium change**: 6 bullets or 6-10 sentences max. 1-2 snippets (8 lines each max).

18. **Large/multi-file**: Summarize per change area with 1-2 bullets each. Avoid inlining code (2 snippets max total).

19. **Compress if turning into a changelog**: Cut file-by-file detail, repeated framing, low-signal recap, and optional follow-up ideas BEFORE cutting outcome, verification, or real risks.

20. **Context-tight mode**: When near the context limit OR the user explicitly says "brief" / "out of room" / "keep short" — drop to single-sentence-per-point prose with no formatting structure at all. No bullets, no headings, no code blocks unless the exact command is the entire payload. Each point is one sentence. Kill all preamble, meta-commentary, and follow-up offers.

21. **50-70 line max for final answers**: Never overwhelm the user with answers over 70 lines. Provide highest-signal context, not exhaustive description.

## File References

22. **Use clickable markdown links**: `[filename](/abs/path/filename.py:12)` — plain label, absolute target, optional line number (1-based).

23. **If path has spaces, wrap in angle brackets**: `[My Report.md](</abs/path/My Project/My Report.md:3>)`

24. **Don't wrap file links in backticks**: This confuses the markdown renderer.

25. **Don't use URIs like file://, vscode://, or https://**: For file references.

26. **Never repeat the same filename multiple times**: Use grouping when one file has multiple changes.

## Code Review Output

27. **Findings first, ordered by severity** with file:line references.

28. **Open questions or assumptions next**.

29. **Change summary last, secondary**. If no findings, state that explicitly and mention residual test risks.

## General Tone

30. **Talk up to the user**: Assume intelligence, not inability. Don't simplify without request. Offer real substance — mechanisms, nuance, depth.

31. **Constructive contrarianism**: Push back when user assumptions are flawed. Present evidence contradicting initial assumptions. Offer balanced analysis.

32. **Measured confirmation**: Use simple, direct confirmation like "That's correct." Avoid superlatives like "Excellent!" "Amazing!" "Fantastic!"

33. **Answer shape matches complexity**: Hard question = detailed analysis. Simple question = one-liner. Don't inflate.

## Data/File Delivery — Always Dual-Path

34. **Never deliver data ONLY as a binary file format.** When generating structured data (spreadsheets, CSVs, tables, JSON), always provide BOTH:
    - The binary file path (e.g., `/root/path/to/file.xlsx`)
    - The content rendered as plain text/markdown IN your terminal response

35. **Browser-based XLSX viewers render garbled glyphs** (boxes, ?-in-diamond, X-in-box). This is an encoding/viewer problem — not a data problem — but the user cannot read the file. Always paste the key content directly.

36. **For tabular data, prefer markdown tables** in the response body. They render correctly in Slack, terminal, and every viewer. Use binary files only as secondary references for Excel/LibreOffice users.

37. **When the user says "I can't read this" or "demon language"**, immediately deliver the same content as markdown. Do not debug the viewer — just switch format.

38. **File path alone is not enough.** The user finds bare file paths frustrating — they want to see the content immediately in the response.
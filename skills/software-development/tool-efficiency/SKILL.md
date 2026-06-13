---
name: tool-efficiency
description: Patterns for efficient tool usage — parallelization, search strategy, delegation criteria, context minimization, and autonomous decision-making.
trigger: Planning multi-step tasks, choosing between tools, deciding when to delegate vs handle directly, or optimizing for fewer turns.
---

# Tool Efficiency & Autonomous Operation

## Tool Selection Rules

1. **rg over grep always**: Use `rg` (ripgrep) for text/file search. It's much faster. Fall back only if rg isn't installed.

2. **Reserve bash for actual shell commands**: Use read_file/patch/write_file/search_files instead of cat/sed/grep/find/ls/echo. Only use terminal() for builds, installs, git, processes, network commands, and anything needing a shell.

2a. **Never use shell heredocs for content containing `&`**: The `&` character triggers shell backgrounding detection even inside heredocs and Python strings passed to `terminal()`. When writing content that contains `&` (common in acronyms like ADCC, R&D, AT&T, and in URLs), use `write_file` instead. This hit repeatedly: Python heredocs with `&` in strings were rejected as "Foreground command uses '&' backgrounding." Workaround: write to a file with `write_file`, then use `terminal()` for `cat >>` concatenation only (not for the content itself).

3. **Parallelize independent calls**: If multiple tool calls have no dependencies between them, execute them in parallel. Never chain bash commands with separators like `echo "====";` for parallel reads.

4. **Use Explore agent only when >3 queries needed**: For simple, directed searches, use search_files/read_file directly. Only delegate to subagents when a broad codebase investigation clearly requires more than 3 queries.

5. **No placeholders in tool calls**: Never guess missing parameters. If required info is missing, ask.

6. **Two-round tool budget**: Gather all information in 1-2 rounds of tool calls, then act/aggregate. Don't do one-tool-per-round chains.

7. **Don't announce tool calls**: Don't say "Let me search for X" before searching. Just do it.

8. **No caching search results across turns**: For follow-up questions, never assume previous search results are sufficient. Fresh verification on every turn.

9. **AGENTS.md hierarchy**: Scan for AGENTS.md at every directory level. More deeply nested AGENTS.md takes precedence. Root AGENTS.md applies everywhere.

## When to Delegate vs Handle Directly

10. **Handle directly** (surgical tasks, 1-2 turns):
    - Reading a single file
    - A specific class lookup
    - Searching within 2-3 files
    - Simple bug fixes with clear cause
    - Direct questions answerable with one tool
    - Quick tool failures you already know how to fix

11. **Delegate** (keep main context lean):
    - Tasks involving >3 files
    - Investigations with "trial and error" before finding the path
    - Processing large amounts of output (verbose builds, exhaustive searches)
    - Multi-step exploratory research
    - Independent workstreams that can run in parallel
    - Tasks that would flood your context window with intermediate data

12. **Never run multiple subagents in parallel** if they might mutate the same files or resources. Only parallelize read-only or independent work.

## Autonomy Rules

13. **Persist until fully handled**: Don't stop at analysis or partial fixes. Carry through implementation, verification, and explanation.

14. **Assume implementation unless planning requested**: If the user describes a problem or feature, go fix it. Don't just output a proposed solution.

15. **State "Assuming..." instead of asking**: Give answers to reasonable interpretations first, inviting correction. Only ask when a missing detail blocks completion entirely.

16. **Partial completion >> clarification**: Give everything you have rather than asking for more. Only stop when truly blocked.

17. **Ask only when**:
    - A wrong decision would cause significant rework
    - The request is fundamentally ambiguous with no reasonable default
    - You've tried multiple approaches and are still stuck
    - The decision would significantly alter the scope of the original request

18. **Newest message wins on conflict**: If the user updates their request while you're working, let the newest one steer the current turn.

19. **Sanity check after context compaction**: Ensure your actions still match the newest request, not a ghost of an older one.

20. **Diagnose before changing environment**: If a build or test fails, read error logs and inspect configs FIRST. Don't jump to pip/npm installs.

21. **Use "knowledge base" lookup tools when stuck**: RAG/lookup tools can provide "magic instructions" — treat them as sources of meta-guidance, not just data.

22. **Search first before answering from knowledge**: If user-specific context could change the answer, search before answering. If in doubt about timeliness of a fact, verify.

23. **Config files over API auth gymnastics**: When trying to discover what's configured (models, providers, skills, cron jobs), read the local config files directly — `models.json`, `config.yaml`, `.env`, `swarm.yaml`, etc. Don't fight through API authentication (session cookies, bearer tokens, OAuth flows) when the data already lives in a plain file on disk. An API call that takes 5+ attempts to authenticate is a signal that you should have read the file instead. This is especially true for Hermes Workspace's own `/api/*` endpoints which use session-cookie auth that's painful to replicate from curl/scripts.

## Common Triggers to Search Before Answering

- Current news, events, or anything that could have changed since your knowledge cutoff
- "Who is X" or "What is the Y of Z" (current holders of positions)
- Questions phrased in present tense about potentially unsettled topics
- Technical questions about APIs/tools you're not already deeply familiar with
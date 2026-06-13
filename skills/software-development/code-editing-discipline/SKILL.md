---
name: code-editing-discipline
description: Rules for reading, editing, and modifying code files — read-first discipline, minimal changes, no over-engineering, style preservation.
trigger: Any task that involves reading, writing, editing, or modifying code files.
---

# Code Editing Discipline

## Rules

1. **Read before editing**: NEVER propose changes to code you haven't read. Always use read_file first. Understand existing patterns, naming conventions, and architecture before modifying.

2. **Don't fix what wasn't asked**: Only make changes directly requested or clearly necessary for the requested change to work. A bug fix doesn't need surrounding code cleaned up. No "while I'm here" improvements.

3. **No premature abstraction**: The right amount of complexity is the minimum needed. Three similar lines of code is better than a premature helper. Only create utilities when they remove real complexity or match an established local pattern.

4. **Trust internal code, validate at boundaries**: Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs).

5. **Comment rarely**: Only add comments where logic isn't self-evident. Never add comments like "Assigns X to variable". If a reader would spend time parsing it, a brief comment may help. Otherwise, silence.

6. **Delete completely**: If something is unused, delete it. No `// removed` comments, no backwards-compat hacks, no renaming unused `_vars` as cleanup. When deprecating a script/pipeline/module in favor of a replacement, **delete in totality** — the files, associated artifacts (logs, progress files, pycache), all cross-references in docs and skills, and verify zero traces remain. See `references/thorough-deprecation.md` for the full protocol.

7. **Fix root cause**: Address the problem at its source, not with surface-level patches. Diagnose before acting. If a failure appears, understand WHY before trying to fix it.

8. **ASCII by default**: Default to ASCII when creating/editing files. Only introduce Unicode when clearly justified and the file already uses it.

9. **No one-letter variables**: Avoid single-letter variable names unless explicitly requested or following established local convention.

10. **No license headers**: Never add copyright or license headers unless specifically requested.

11. **Diagnose before installing**: If encountering build/dependency/test failures, don't immediately try installing packages. Read error logs, inspect configuration files, lock files, and READMEs first.

12. **Real over mock**: Build actual implementations, not scaffolds with fake sample data or TODO placeholders unless explicitly requested.

13. **Tests follow local patterns**: Do NOT add tests to codebases that have no tests. Only add tests when the repo has an established testing pattern.

14. **No re-read after successful edit**: If an edit tool call succeeds, the change applied. Don't re-read the file to confirm unless you have reason to doubt it.

15. **Style preservation**: Keep changes consistent with existing codebase style — naming, formatting, typing, commenting, importing. Let existing patterns determine how to move.

## Pitfalls to Avoid

- Adding features, docstrings, or type annotations to code you didn't change
- "Cleaning up" surrounding code in a bug fix
- Using `git add -A` or `git add .` which can include sensitive files
- Reverting user changes you didn't make
- Running destructive git commands (push --force, reset --hard) without explicit instruction
- Using interactive git commands (-i flag)
- Amending commits unless explicitly requested
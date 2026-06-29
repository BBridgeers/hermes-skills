---
name: debug-loop
description: Breakpoint → evaluate → patch → verify cycle for JS/TS errors in the DFW Awwwards build pipeline.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Debug, TypeScript, JavaScript, Build]
    related_skills: [dfw-web-design-now, build-executor]
---

# Debug Loop

When a DFW build fails with a JS/TS error, run a structured debug cycle. Escalate to a premium model if the fix is not obvious after two iterations.

## Pattern
Errors in the build pipeline block delivery. This skill defines the exact cycle to minimize time-to-fix and avoid guessing.

## Protocol

1. **Capture error**
   - Save full stderr + stdout to `/root/.dfw/debug/<client>-<timestamp>.log`.
   - Record failing file path and line number.
2. **Evaluate context**
   - Read the failing file.
   - Read related files (imports, types, config).
   - Check git diff since last passing build.
3. **Form hypothesis**
   - Missing import?
   - Type mismatch?
   - Config drift (Tailwind, TS, build tool)?
   - Dependency version conflict?
4. **Patch**
   - Make the smallest change that addresses the hypothesis.
   - Write the patch with `mcp_filesystem_edit_file` or `write_file`.
5. **Verify**
   - Re-run the exact command that failed.
   - If pass, commit with `sop(debug-loop): fixed <short-desc>`.
   - If fail, loop. Max 2 cycles before escalation.

## Escalation Criteria
Escalate to premium model (Claude Sonnet / GLM-5.2) if:
- Error involves framework internals (Next.js, Vite, esbuild).
- Two patches fail.
- Error is a runtime browser error not caught by tests.

## Tools Used
- `mcp_server_commands_run_process` to re-run commands.
- `server_git` tools to inspect diffs.
- `mcp_filesystem_*` to read and edit files.
- `dbhub_execute_sql` to log debug cycles.

## Example Log Entry
```
[2026-06-29T14:32:00Z] Client: acme-hvac
Error: TS2345: Argument of type 'string | undefined' not assignable to parameter of type 'string'.
File: src/components/Hero.tsx:23
Hypothesis: prop not guarded
Patch: added fallback `title ?? ''`
Verify: npx tsc --noEmit PASS
```

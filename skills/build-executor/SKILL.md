---
name: build-executor
description: Execute Awwwards-grade DFW spec builds phase-gated through npm install, Tailwind compile, Playwright test, and deploy.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Build, Tailwind, Playwright, NPM, Deploy]
    related_skills: [dfw-web-design-now, debug-loop]
---

# Build Executor

Run the DFW Awwwards build pipeline with phase gates. Fail fast, surface errors, and escalate to `debug-loop` on JS/TS failures.

## Pattern
Every spec build moves through the same execution sequence: install → compile → test → validate → deploy-preview. Each gate must pass before the next runs.

## Protocol

1. **Phase 0 — Pre-flight**
   - Read the spec from the client-data node (`/root/.dfw/specs/<client>/SPEC.md`).
   - Verify required files: `package.json`, `tailwind.config.*`, `src/`, `tests/`.
2. **Phase 1 — Install**
   - Run `npm install` in the project root.
   - If lockfile conflicts, run `npm ci` or delete `node_modules` and reinstall.
3. **Phase 2 — Compile**
   - Tailwind: `npx tailwindcss -i ./src/input.css -o ./dist/output.css` or project-specific build script.
   - TypeScript: `npx tsc --noEmit`.
4. **Phase 3 — Test**
   - Run `npx playwright test`.
   - Capture screenshot diffs to `.dfw/artifacts/<client>/diffs/`.
5. **Phase 4 — Validate**
   - Ensure `dist/` or `out/` exists and contains `index.html`.
   - Run `ls -la dist/` and check no 0-byte assets.
6. **Phase 5 — Deploy Preview** (optional)
   - Call `client-preview` skill to push to EdgeOne Pages or Cloudflare Pages.

## Failure Gates
- Install failure → retry once with `npm cache clean --force`.
- Compile failure → invoke `debug-loop` skill.
- Test failure → capture diffs, log to `client-data`, then invoke `debug-loop`.
- Validation failure → stop and report missing artifacts.

## Tools Used
- `mcp_server_commands_run_process` / `mcp_shell_server_shell_execute` for shell execution.
- `mcp_server_git_*` for reading build history if needed.
- `dbhub_execute_sql` for recording phase status.

## Example
```bash
cd /root/dfw-builds/acme-hvac
npm install
npx tailwindcss -i ./src/input.css -o ./dist/output.css --minify
npx tsc --noEmit
npx playwright test
ls -la dist/
```

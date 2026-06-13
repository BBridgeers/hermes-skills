# pnpm Build Pitfalls

## The Approval Loop

When running `pnpm install` in a non-TTY environment (CI, systemd, cron, or agent
terminal sessions), pnpm blocks on an interactive approval prompt:

```
? Choose which packages to build (Press <space> to select, <a> to toggle all, <i> to invert selection)
❯ ○ electron
  ○ electron-winstaller
  ○ esbuild
  ○ unrs-resolver
```

These four packages have build scripts that pnpm refuses to run without explicit
approval. Setting `CI=true` silences the prompt but still marks them as ignored:

```
[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: electron-winstaller@5.4.0, electron@40.9.3, esbuild@0.27.7, unrs-resolver@1.11.1
```

## The Compound Problem

Even after `CI=true pnpm install` succeeds, `pnpm build` re-runs `pnpm install`
internally and fails with the same ignored-builds error. This means NEITHER
`pnpm build` NOR `pnpm dev` work through the pnpm script layer.

## Fix: Bypass pnpm's Script Layer

For `pnpm install`:
```bash
CI=true pnpm install
```

For build (workspace):
```bash
NODE_OPTIONS="--max-old-space-size=2048" npx vite build
```

For dev server (workspace):
```bash
NODE_OPTIONS="--max-old-space-size=2048" npx vite dev --port 3100 --host 127.0.0.1
```

This bypasses `pnpm build` and `pnpm dev` entirely — calls `vite` directly via `npx`.

## What Does NOT Work

- `pnpm approve-builds` — requires interactive PTY; can't automate
- `pnpm config set onlyBuiltDependencies` — pnpm still blocks on security check
- `.npmrc` with `onlyBuiltDependencies[]=esbuild` — ignored
- `pnpm rebuild esbuild unrs-resolver` — runs build scripts but pnpm build still
  re-checks approval on next run

## For systemd Services

Always use `npx vite dev` (not `pnpm dev`) in the `ExecStart` line. The systemd
unit runs without a TTY, so any pnpm wrapper will hit the approval loop.

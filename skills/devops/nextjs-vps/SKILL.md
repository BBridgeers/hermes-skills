---
name: nextjs-vps
description: Deploy and troubleshoot Next.js applications on bare-metal VPS. Covers memory-safe deployment, build troubleshooting, TypeScript type fights, environment variables, and systemd service setup.
version: 1
tags: [nextjs, vps, deployment, troubleshooting, nodejs]
---

# Next.js VPS — Deployment & Troubleshooting

Complete guide for deploying and troubleshooting Next.js applications on bare-metal Linux VPS (e.g., Hostinger).

## Deployment Protocol

### Pre-flight: Memory Check

Before any `npm run build`:

```bash
free -h | awk '/^Mem:/ {print $7}'
# Abort if available < 3GB
```

Memory exhaustion from concurrent builds causes SSH to hang. Kill stale processes first:

```bash
pkill -f "next build" || true
pkill -f "next dev" || true
pkill -f "next start" || true
```

### Build

```bash
cd /path/to/app
NODE_OPTIONS="--max-old-space-size=4096" npm install
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

### Start & Bind

Next.js `npm start` ignores PORT if not exported in the same shell. Always use a wrapper script:

```bash
#!/bin/bash
export PORT=3002
export HOSTNAME=127.0.0.1
cd /root/myapp
exec npx next start
```

Verify:

```bash
ss -tulpn | grep ':3002'
curl -sf http://127.0.0.1:3002
```

### Systemd Service

```ini
[Unit]
Description=My Next.js App
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/myapp-start.sh
WorkingDirectory=/root/myapp
Environment="NODE_OPTIONS=--max-old-space-size=4096"
Environment="PORT=3002"
Environment="HOSTNAME=127.0.0.1"
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

### nginx Reverse Proxy

```nginx
location / {
    proxy_pass http://127.0.0.1:3002;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
}
```

## Build Troubleshooting

### Next.js 15 + next-auth Version Mismatch

`createAuthClient` / `useSession` fails at build. `next-auth@4.x` doesn't export v5 APIs. Temporary fix: comment out auth client and use no-op. Permanent fix: upgrade to next-auth v5 or pin `@auth/prisma-adapter` to v4.

### PORT Not Respected

`PORT=3001 npm start` starts on wrong port. Root cause: env vars don't propagate through `&`/`nohup`. Fix: wrap in script that exports PORT in same shell.

### TypeScript Type Fight Anti-Pattern

**If you make 3+ attempts to fix TypeScript errors on the same file without a clean build, stop fighting.** Use:
1. `any` / `any[]` — runtime behavior identical
2. `// @ts-ignore` — single-line escape
3. `// @ts-expect-error` — self-documents
4. `rm -rf .next && npm run build` — clear LSP ghost cache

**Rule:** Ship first, type later. A type annotation that adds 70 messages of latency is worse than `any` that ships immediately.

### LSP Ghost Type Errors

Build fails on a type you already removed. `rm -rf .next` to clear cached `.d.ts` files, then rebuild.

### Static Import + Server Components

Missing `'use client'` directive causes resolution errors in Next.js 15+ app router. Ensure all client components declare it at the top.

### next.config.ts Unrecognized Options

`maxDuration` was removed from Next.js core config in v15. Remove it or wrap in Vercel-only conditional.

## Failure Modes

| Cause | Symptom | Fix |
|-------|---------|-----|
| Memory exhaustion | SSH hangs, commands timeout | Wait or `sudo reboot` |
| Port conflict | `EADDRINUSE` | `pkill -f next`, retry |
| Port held by zombie from old session | `EADDRINUSE` even after `kill`/`pkill` | `fuser -k 3001/tcp && sleep 2` — `fuser` kills by port, not by process name |
| Wrong binding | `curl localhost:3002` fails | Ensure `-H 127.0.0.1` or `HOSTNAME=127.0.0.1` |
| nginx mismatch | 502 Gateway | Sync `upstream` and `proxy_pass` |
| env var not forwarded | PORT ignored by `npm start` | Export in wrapper script, not before `&` |
| Old build still running after deploy | New code doesn't appear despite successful build | `fuser -k <port>/tcp` kills any process bound to that port regardless of PID. `pkill -f "next"` can miss processes started by different shell sessions or under different names. Always follow with `ss -tlnp | grep <port>` to confirm port is free before starting new process. |

## Verification

```bash
npm run build && npm start
curl http://127.0.0.1:${PORT}/health  # should return JSON {"status":"ok"}
ss -tulpn | grep ${PORT}
systemctl --user status myapp
```

## Support Files

- `references/free-vision-model-migration.md` — Swapping dead provider API keys to free OpenRouter vision models. Discovery query, model table, code swap pattern, pitfalls (OWL Alpha text-only, Google banned).

## Consolidated Skills

This skill absorbs: `nextjs-build-troubleshooting`, `nextjs-vps-deployment`.

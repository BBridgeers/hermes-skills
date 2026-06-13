---
name: Next.js Bare-Metal Deployment
version: 1
triggered-by: Deploying Next.js 15 app directly on a VPS without Docker (or with Docker build failures)
last-updated: 2026-05-24
description: Building, running, and systemd-service-ifying a Next.js app on bare-metal Linux (VPS) without containerization, including common build fixes and port troubleshooting.
---

# Next.js Bare-Metal Deployment

Build and run a Next.js app directly on a Linux VPS without Docker. Faster iteration than container builds, avoids Docker-in-Docker complexity, and works reliably on resource-constrained VPS instances.

## Protocol

### 1. Install Dependencies
SSH into VPS and run from your project directory:
```bash
cd /root/vehicle-analyzer
npm install
```

### 2. Build
```bash
npm run build
```

#### Common Build Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `next/config` Module not found | Missing @next/env or config file issue | `npm install` again, check `package.json` engines field |
| `Type error` in route.ts | Next.js 15 stricter types | Fix type errors or add `// @ts-nocheck` temporarily |
| `maxDuration` in next.config.ts | Unsupported in Next.js 15 standalone mode | Remove `maxDuration` from config |
| ` Rate limit requires 4 args` | Function signature mismatch | Check and match the function params |

### 3. Run with PORT Override
Next.js ignores `PORT` env var in some configs. Use explicit PORT:
```bash
PORT=3001 npm start
```

Or in a script:
```bash
#!/bin/bash
export PORT=3001
cd /root/vehicle-analyzer
exec npm start
```

### 4. Verify
```bash
curl http://127.0.0.1:3001/health
# Expected: {"status":"ok","service":"veracar"}
```

### 5. Systemd Service
Create `/etc/systemd/system/veracar-nextjs.service`:
```ini
[Unit]
Description=Veracar Next.js App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vehicle-analyzer
ExecStart=/usr/bin/npm start
Environment=PORT=3001
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=veracar-nextjs

[Install]
WantedBy=multi-user.target
```

Then:
```bash
systemctl daemon-reload
systemctl enable veracar-nextjs
systemctl start veracar-nextjs
```

### 6. Kill Stale Processes
If port is in use:
```bash
pkill -f "node.*next" || pkill -f "npm start"
ss -tlnp | grep :300   # verify port is free
```

## Failure Modes
- **EADDRINUSE**: Another process (old Next.js, docker-proxy) is on the port. Kill it or change port.
- **Build passes but runtime 404**: Next.js started on wrong port (default 3000, not 3001). Kill and restart with explicit PORT.
- **nohup exits immediately**: Background `&` with nohup can cause issues. Use systemd or `disown` instead.
- **env vars not loaded**: `.env.local` is read by Next.js at build time AND runtime. Ensure it exists in project root.

## Key Insight
When deploying Next.js apps to VPS without Docker, always use systemd with `Restart=always` and explicit PORT env. This ensures your app survives reboots and restarts automatically if it crashes.
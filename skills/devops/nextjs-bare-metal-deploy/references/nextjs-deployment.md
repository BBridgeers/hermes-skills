# Next.js Bare-Metal Deployment Fixes (May 2026)

## Context
Deploying vehicle-analyzer Next.js 15 app on bare VPS without Docker.

## Issues Encountered & Fixed

### 1. PORT env var ignored
Next.js started on 3000 despite PORT=3001. Verify process list to confirm actual port.

### 2. Multiple processes on same port
Had two Next.js processes running (old PID 16651 + new PID 28580).
Fix: pkill -f "node.*next", verify port free, restart.

### 3. next.config.ts unsupported keys
Next.js 15 rejects maxDuration. Remove it from config.

### 4. Health check endpoint
Added src/app/api/health/route.ts returning JSON status.

## Quick Start (VPS)
```bash
cd /root/vehicle-analyzer
npm install && npm run build
PORT=3001 npm start
curl http://127.0.0.1:3001/health
```
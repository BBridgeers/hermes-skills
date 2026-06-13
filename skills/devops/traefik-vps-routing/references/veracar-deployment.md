# Vercel → VPS Migration: veracar.co (May 2026)

## Context
Migrated veracar.co (Next.js + FastAPI scraper) from Vercel (paused due to unpaid billing) to bare-metal VPS at VPS_IP_REDACTED.

## Stack
- Next.js 15.5.15 (port 3001)
- FastAPI scraper (port 8765, native Python process)
- Traefik v2.10 reverse proxy (ports 80/443)
- Upstash Redis (external, HTTP API via KV_REST_API_URL)

## Key Steps
1. Cloned repo to /root/vehicle-analyzer
2. Fixed rate-limit type errors (added missing userId param)
3. Disabled auth client (next-auth v5 API vs v4 client mismatch)
4. Set Upstash Redis env vars in .env.local
5. Built Next.js: npm run build
6. Started Next.js: PORT=3001 npm start
7. Configured Traefik file provider at /root/traefik.d/veracar.yml
8. Started Traefik with TLS + multi-service routing
9. Updated DNS A records to VPS_IP_REDACTED
10. Verified: curl -sk https://veracar.co returns "Vehicle Analyzer Pro"

## Gotchas
- Next.js ignores PORT env var if next.config.ts has unsupported maxDuration
- Traefik HTTPS routers need explicit tls: {} or they return 404
- Port 3000 was occupied by docker-proxy; clean up first
- FastAPI scraper runs natively (simpler than Docker)
- Scraper health route is /api/scrape/health
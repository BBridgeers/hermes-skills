---
name: cloudflare-deploy
description: Deploy DFW builds to Cloudflare Pages and verify DNS for client handoffs.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Cloudflare, Deploy, DNS, Pages]
    related_skills: [dfw-web-design-now, build-executor, client-preview]
---

# Cloudflare Deploy

Deploy DFW spec builds to Cloudflare Pages and handle nameserver/DNS verification.

## Pattern
When a client buys Track B (purchase) or opts into Landlord hosting, deploy the build to Cloudflare Pages, point the domain, and verify resolution.

## Protocol

1. **Prerequisites**
   - `mcp-server-cloudflare` configured with `CLOUDFLARE_API_TOKEN`.
   - Client domain and desired subdomain.
   - Build output in `dist/` or `out/`.
2. **Deploy to Pages**
   - Use `mcp-server-cloudflare` to create/update Pages project.
   - Upload build directory.
3. **DNS**
   - If client transfers domain: update nameservers to Cloudflare.
   - If external registrar: add CNAME to `pages.dev` domain.
4. **Verify**
   - Poll DNS with `dig +short <domain>` until it resolves.
   - Check HTTPS cert is active (Cloudflare auto-generates).
5. **Record**
   - Update `client-data` with deployed URL and Cloudflare project ID.

## Commands
```bash
# Deploy via wrangler (fallback if MCP not available)
npx wrangler pages deploy ./dist --project-name=dfw-<client>

# Verify DNS
dig +short <client-domain>
curl -I https://<client-domain>
```

## Failure Modes
- Deploying without verifying domain ownership.
- Forgetting to update nameservers, leaving site unreachable.
- Not recording deployment URL in client-data.

---
name: Traefik Reverse Proxy on VPS
version: 1
triggered-by: Deploying web apps from PaaS (Vercel, Netlify, etc.) to bare-metal VPS using Traefik v2 as ingress
last-updated: 2026-05-24
description: Configuring Traefik v2 as a reverse proxy on a bare-metal VPS with file-based dynamic routing, HTTPS/TLS, multi-service routing, and Let's Encrypt certificate provisioning.
---

# Traefik Reverse Proxy on VPS

Route external traffic to backend services running on a VPS using Traefik v2 with file-based dynamic configuration. Covers HTTP→HTTPS redirect, TLS termination, multi-service routing, and Let's Encrypt (or self-signed fallback).

## Protocol

### 1. Config Architecture
- **Static config** (CLI flags at container start): entrypoints, providers, cert resolvers
- **Dynamic config** (file provider): routers, services, middlewares in `/etc/traefik.d/*.yml`
- File provider auto-watches and hot-reloads on change (`--providers.file.watch=true`)

### 2. HTTPS Router Gotcha
An HTTPS router **must** explicitly declare `tls: {}`. Without it, Traefik treats the router as HTTP-only and returns 404 over HTTPS:
```yaml
routers:
  my-app:
    rule: "Host(`myapp.com`)"
    entryPoints:
      - websecure
    tls: {}          # REQUIRED on websecure entrypoint
    service: my-app
```

### 3. HTTP→HTTPS Redirect
Use Traefik CLI flags for a global catch-all redirect (priority 2147483646):
```
--entrypoints.web.http.redirections.entrypoint.to=websecure
--entrypoints.web.http.redirections.entrypoint.scheme=https
```

### 4. Multi-Service Routing
```yaml
http:
  routers:
    main:
      rule: "Host(`myapp.com`)"
      entryPoints: [websecure]
      tls: {}
      service: main
    api:
      rule: "Host(`myapp.com`) && PathPrefix(`/api`)"
      entryPoints: [websecure]
      tls: {}
      service: api
  services:
    main:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:3001"
        passHostHeader: true
    api:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:8765"
        passHostHeader: true
```

### 5. Docker Provider Version Mismatch
Older Docker client (1.24) vs Traefik expecting 1.40 causes Docker provider errors. **File provider still works fine.** Check it specifically:
```bash
docker logs <container> | grep "providerName=file"
```

### 6. Let's Encrypt
- Port 80 must be accessible for ACME HTTP-01 challenge
- Required flags: `--certificatesresolvers.letsencrypt.acme.email=<email>` and `--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json`
- Self-signed fallback activates automatically if ACME fails

### 7. Container Startup
```bash
docker run -d --name traefik --network host \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /root/traefik.d:/etc/traefik.d:ro \
  -v traefik-letsencrypt:/letsencrypt \
  traefik:v2.10 \
  --api.dashboard=false \
  --providers.docker.exposedbydefault=false \
  --providers.file.directory=/etc/traefik.d \
  --providers.file.watch=true \
  --entrypoints.web.address=:80 \
  --entrypoints.websecure.address=:443 \
  --certificatesresolvers.letsencrypt.acme.httpchallenge=true \
  --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web \
  --certificatesresolvers.letsencrypt.acme.email=admin@example.com \
  --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json \
  --entrypoints.web.http.redirections.entrypoint.to=websecure \
  --entrypoints.web.http.redirections.entrypoint.scheme=https
```

## Failure Modes
| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| 404 on HTTPS routes | Missing `tls: {}` on router | Add `tls: {}` to router config |
| 502 Bad Gateway | Backend not running / wrong port | Verify with `ss -tlnp` |
| Config not reloading | Bind mount is `:ro` (read-only) | Remount writable or restart container |
| Docker errors in logs | Client API version mismatch | Ignore if file provider works |
| Redirect loop | Same host in redirect + app router | Separate entrypoints properly |

## Key Insight
Traefik's `tls: {}` appears redundant in theory (auto-enabled on `websecure` entrypoint) but the YAML file provider does **not** auto-enable TLS for HTTPS entrypoints without it. Always declare it explicitly on any router using `websecure`.
# Traefik Routing Debug — veracar.co Migration

## Session Date: 2026-05-24
### Previous session context: Initial deployment (port 3000 conflict, operator precedence bug, Next.js PORT env)

---

## Today's Problem Chain & Resolution

### Issue 1: Self-Signed Cert Served Instead of Let's Encrypt

**Symptom**: `ERR_CERT_AUTHORITY_INVALID` in Chrome. Cert showed:
```
issuer=CN = TRAEFIK DEFAULT CERT
subject=CN = TRAEFIK DEFAULT CERT
```

**Root cause**: The `veracar-main` router in `/root/traefik.d/veracar.yml` had:
- Only `entryPoints: [web]` (port 80) — no `websecure`
- No `tls:` block at all

Without a `tls:` block and the `websecure` entrypoint, Traefik never triggers ACME cert provisioning and falls back to its built-in self-signed cert.

**Fix applied**:
```yaml
entryPoints:
  - web
  - websecure
tls:
  certResolver: letsencrypt
```

---

### Issue 2: Docker API Version Mismatch Blocks Provider

**Symptom**: Traefik logs showed continuous errors:
```
"client version 1.24 is too old. Minimum supported API version is 1.40"
"Cannot connect to docker server context canceled"
"Error while building configuration"
```

**Root cause**: Traefik v2.10 ships Docker client v1.24, but the Hostinger VPS host daemon requires >=1.40. Docker provider couldn't initialize at all.

**Decision** (already in place from prior session): Use file provider instead of Docker provider. Config lives in `/root/traefik.d/` and is loaded via `--providers.file.directory=/etc/traefik.d`.

**Upgrade applied**: Bumped `traefik:v2.10` to `traefik:latest` (resolved to v3.6.14) in `/root/traefik-compose.yml` to get a compatible Docker client.

---

### Issue 3: Invalid Middleware Field Name

**Symptom**: Traefik startup error:
```
"/etc/traefik.d/veracar.yml: field not found, node: frameOptions"
```

**Root cause**: In Traefik v3, the `frameOptions` shorthand was renamed to `customFrameOptionsValue`. Using the old field name causes a config parse failure — Traefik falls back to empty/default config, which means no cert provisioning either.

**Fix applied**:
```yaml
middlewares:
  security-headers:
    headers:
      customFrameOptionsValue: "SAMEORIGIN"  # was: frameOptions
```

---

### Issue 4: Container Name Conflict

**Symptom**: `docker compose up` failed with:
```
Conflict. The container name "/traefik-traefik-1" is already in use
```

**Fix applied**: `docker rm -f traefik-traefik-1` before recreating with `docker compose up -d`.

---

## Final Working Config (2026-05-24)

### `/root/traefik-compose.yml`
- Image: `traefik:latest` (v3.6.14)
- Removed obsolete `version: "3.8"` key (warned at runtime)
- Volume mount for file provider: `/root/traefik.d` -> `/etc/traefik.d`
- ACME storage volume: `traefik-traefik-letsencrypt` -> `/letsencrypt`
- HTTP->HTTPS redirect via entrypoint redirection

### `/root/traefik.d/veracar.yml`
- Router `veracar-main`: dual entrypoints (`web` + `websecure`), `tls.certResolver: letsencrypt`
- Backend services: NextJS on `:3001`, Scraper on `:8765`
- Security headers middleware using `customFrameOptionsValue`

## Verified Results (post-fix)

```
issuer=C = US, O = Let's Encrypt, CN = R12
subject=CN = veracar.co
notBefore=May 24 19:55:40 2026 GMT
notAfter=Aug 22 19:55:39 2026 GMT
```

Browser loads `https://veracar.co` cleanly — no SSL warning. Auto-renewal handled by Traefik ACME against `/letsencrypt/acme.json`.

---

## Debugging Commands Reference

```bash
# Check cert issuer/expiry
echo | openssl s_client -connect veracar.co:443 -servername veracar.co | openssl x509 -noout -dates -issuer -subject

# Traefik logs (filter for TLS/ACME/Docker errors)
docker logs traefik-traefik-1 2>/dev/null | grep -iE "acme|letsencrypt|cert|tls|challenge|error"

# Verify ACME state inside container
docker exec traefik-traefik-1 ls -la /letsencrypt/
docker exec traefik-traefik-1 cat /letsencrypt/acme.json

# DNS + HTTP redirect check
dig +short veracar.co
curl -sI http://veracar.co | head -5

# Firewall check
ufw status
```

## Traefik v2 -> v3 Breaking Changes Encountered
- `frameOptions` -> `customFrameOptionsValue` in header middlewares
- Config parse failures silently serve default self-signed cert
- `version` key in compose files is now obsolete (warns but harmless)
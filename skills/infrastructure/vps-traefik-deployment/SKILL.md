---
name: vps-traefik-deployment
version: 3
category: infrastructure
description: Deploying multi-service web apps on a bare VPS behind Traefik v2/v3 reverse proxy with HTTPS, file provider routing, Let's Encrypt SSL, and Docker bridge networking
triggered-by: Deploying web apps (Next.js, FastAPI, etc.) on bare VPS behind Traefik with co-tenant port conflicts, Docker networking issues, or UFW forwarding problems
last-updated: 2026-05-24
---

# Skill: VPS Web App Deployment — Traefik Reverse Proxy

## Pattern

Deploying a production web stack on a VPS where:
- Multiple services (frontend + API/scraper) share a single VPS
- Traefik v2/v3 is the ingress controller (not nginx)
- HTTPS is handled via Traefik + Let's Encrypt
- Services run as native processes (not necessarily Docker)
- Port conflicts with existing co-tenant containers must be navigated

## Protocol

### 1. Assess Port Landscape
Before deploying anything, audit occupied ports:
```bash
ss -tlnp | grep -E ':(80|443|3000|3001|8765|9000)'
ps aux | grep -E '(python|node|docker-proxy)' | grep -v grep
```

### 2. Resolve Port Conflicts
- Port 3000 was occupied by `docker-proxy` (co-tenant container) → used 3001
- Port 8765 was occupied by native Python scraper → no conflict, reuse it
- Always verify with `ss -tlnp` after starting any service

### 3. Configure Traefik via File Provider
Traefik on this VPS uses the **file provider** (not Docker labels) because:
- Docker API version mismatch (`1.24` vs `1.40` minimum) breaks the Docker provider
- Native processes aren't in Docker anyway

Config location: `/root/traefik.d/<service>.yml`

```yaml
http:
  routers:
    veracar:
      rule: "Host(`veracar.co`) || Host(`www.veracar.co`)"
      service: veracar-nextjs
      entryPoints:
        - web
        - websecure
      middlewares:
        - security-headers
      tls:
        certResolver: letsencrypt

  services:
    veracar-nextjs:
      loadBalancer:
        servers:
          - url: "http://172.16.1.1:3001"    # bridge gateway, NOT 127.0.0.1
        healthCheck:
          path: "/health"

    veracar-scraper:
      loadBalancer:
        servers:
          - url: "http://172.16.1.1:8765"
        healthCheck:
          path: "/health"

  middlewares:
    security-headers:
      headers:
        customFrameOptionsValue: "SAMEORIGIN"
        contentTypeNosniff: true
        browserXssFilter: true
        referrerPolicy: "strict-origin-when-cross-origin"
        customResponseHeaders:
          X-RateLimit-Limit: "100"
          X-RateLimit-Window: "86400"
```

### 4. Compose File

```yaml
services:
  traefik:
    image: traefik:latest    # v3.6.14+ — supports Docker ≥1.40
    container_name: traefik-traefik-1
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - type: bind
        source: /root/traefik.d
        target: /etc/traefik.d
        read_only: false
      - type: bind
        source: /var/run/docker.sock
        target: /var/run/docker.sock
      - type: volume
        source: traefik-traefik-letsencrypt
        target: /letsencrypt
    command:
      - "--api.dashboard=false"
      - "--api.insecure=false"
      - "--log.level=INFO"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.file.directory=/etc/traefik.d"
      - "--providers.file.watch=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@srv1617682.hstgr.cloud"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"

volumes:
  traefik-traefik-letsencrypt:
```

**Note:** Remove obsolete `version: "3.8"` key — Traefik warns at runtime.

### 5. Deploy / Restart
```bash
cd /root
docker rm -f traefik-traefik-1   # resolve container name conflicts
docker compose -f traefik-compose.yml up -d
sleep 5
```

### 6. Start Next.js on Correct Port
Next.js `npm start` ignores PORT if not exported in the same shell:
```bash
cd /root/vehicle-analyzer && export PORT=3001 && npm start
```
Verify: `curl http://127.0.0.1:3001/health`

### 7. UFW Forwarding Rules (Critical for Container→Host)
UFW's FORWARD policy defaults to DROP. Containers cannot reach host services without
explicit rules:

```bash
# Allow Docker subnet to reach host backend ports via iptables
iptables -I ufw-before-input 1 -s 172.16.1.0/24 -d 172.16.1.1 \
  -p tcp -m multiport --dports 3001,8765 -j ACCEPT

# Make persistent: add to /etc/ufw/before.rules.d/docker-host.conf
#   -A ufw-before-input -s 172.16.1.0/24 -d 172.16.1.1 -p tcp \
#     -m multiport --dports 3001,8765 -j ACCEPT
ufw reload
```

Verify: `iptables -L ufw-before-input -n -v --line-numbers` (check packet counters > 0)

### 8. Verify Full Routing
```bash
# Cert check
echo | openssl s_client -connect veracar.co:443 -servername veracar.co | \
  openssl x509 -noout -subject -dates -issuer

# Backend health from container
docker exec traefik-traefik-1 wget -q --spider --timeout=5 http://172.16.1.1:3001/health

# End-to-end
curl -sk https://veracar.co | grep "Vehicle Analyzer"
```

---

## Traefik Operator Precedence

Traefik evaluates routing rules with **AND before OR** — exactly like code:

```
# BROKEN — sends ALL traffic to scraper:
"Host(`veracar.co`) || Host(`www.veracar.co`) && PathPrefix(`/api/scrape/`)"

# Evaluates as:
Host(veracar.co) OR (Host(www.veracar.co) AND PathPrefix(/api/scrape/))

# FIXED — explicit parentheses:
"(Host(`veracar.co`) || Host(`www.veracar.co`)) && PathPrefix(`/api/scrape/`)"
```

## Docker Bridge Networking — Host Reachability

Containers **cannot** reach host services via `127.0.0.1` or `localhost`. From inside a
Docker container, `127.0.0.1` refers to the container itself, not the host.

**How to reach the host from a container:**

| Network driver | Gateway IP (host) | How to find it |
|---|---|---|
| `bridge` (default) | `172.17.0.1` | `docker network inspect bridge \| grep Gateway` |
| Custom bridge | Varies (e.g. `172.16.1.1`) | `docker network inspect <network> \| grep Gateway` |
| `host` | `127.0.0.1` | N/A — shares host namespace |

**In Traefik file provider configs**, use the bridge gateway IP for backend URLs. Find it:
```bash
docker network inspect $(docker inspect --format '{{.HostConfig.NetworkMode}}' <container>) \
  | grep Gateway
```

## UFW + Docker Forwarding Rules

UFW's default FORWARD policy is `DROP`. Docker creates its own chains (`DOCKER`,
`DOCKER-USER`, `DOCKER-FORWARD`), but traffic from a container to a host port is
**not** automatically allowed — it hits the `ufw-before-input` chain on the host.

**Symptom:** Container can ping the host (`ping 172.16.1.1` works — ICMP passes) but TCP
connections time out.

**Fix:** Add an accept rule in `ufw-before-input` for the Docker subnet targeting host
ports. See Section 7 above for persistent config.

**Verification:**
```bash
# From inside the Traefik container:
docker exec traefik-traefik-1 wget -q --spider --timeout=5 http://<gateway>:3001/health

# Check packet counters (pkts > 0 = rule is active):
iptables -L ufw-before-input -n -v --line-numbers
```

## TLS Cert Provisioning Checklist

Traefik will serve its **default self-signed cert** (`CN = TRAEFIK DEFAULT CERT`) if
any of these are missing:

1. Router must list the `websecure` entrypoint
2. Router must have a `tls:` block with `certResolver: letsencrypt`
3. `certificatesresolvers` must be configured in the static command args
4. ACME storage file (`acme.json`) must exist and be writable (`chmod 600`)
5. Port 80 must be reachable for the HTTP challenge

## Failure Modes

| Symptom | Root cause | Fix |
|---|---|---|
| `ERR_CERT_AUTHORITY_INVALID` | Router missing `tls:` block and/or `websecure` entrypoint | Add both + `certResolver` |
| `client version 1.24 is too old` | Docker API mismatch (old Traefik on host needing ≥1.40) | Upgrade to `traefik:latest` or use file provider exclusively |
| `field not found, node: frameOptions` | Traefik v3 renamed the field | Use `customFrameOptionsValue` |
| `Cannot connect to docker server` | Docker daemon unreachable from container | Check socket mount: `-v /var/run/docker.sock:/var/run/docker.sock` |
| `no available server` (503) | Backend URL points to `127.0.0.1` inside container | Use bridge gateway IP instead |
| Backend TCP timeout from container | UFW FORWARD/INPUT drops packets silently | Add `ufw-before-input` rule for Docker subnet |
| Config change not applied | Traefik serving stale config from memory | `docker compose up -d --force-recreate` |
| `container name already in use` | Previous container still exists after failed compose | `docker rm -f <name>` then `docker compose up -d` |
| **Traefik exits 255 — ALL sites down** | ACME cert rejected for one domain (e.g. invalid TLD like `.workspace`) | Traefik treats cert failures as FATAL for the entire process. Remove the bad domain from config, or migrate to nginx (see `references/nginx-migration.md`) |

## When NOT to Use Traefik

Traefik excels at dynamic container discovery for fleets of ephemeral services. For a VPS with a **handful of stable services** (1-5 sites), nginx + certbot is simpler, lighter (~5 MB vs ~50-80 MB), and safer:

| Traefik risk | nginx behavior |
|---|---|
| One bad domain → entire process exits (255) | Bad vhost → that vhost only, server stays up |
| YAML split across static + dynamic configs | One flat site file in `/etc/nginx/sites-enabled/` |
| Silent panics on ACME failures | Certbot runs separately, never takes down the server |
| Docker socket dependency | No Docker dependency |

**Migration to nginx (one command SSL):**
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d domain.com -d www.domain.com --non-interactive --agree-tos --email admin@domain.com --redirect
```

Certificates auto-renew via systemd timer. See `references/nginx-migration.md` for the full migration playbook.

## References

- [Traefik v3 migration guide](https://doc.traefik.io/traefik/migration/v2-to-v3/)
- [Traefik routing precedence](https://doc.traefik.io/traefik/routing/routers/#rule)
- [Traefik file provider docs](https://doc.traefik.io/traefik/providers/file/)
- [UFW and Docker networking](https://docs.docker.com/network/iptables/)
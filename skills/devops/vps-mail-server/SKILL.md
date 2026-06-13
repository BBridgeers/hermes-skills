---
name: vps-mail-server
description: Deploy and manage mail servers (Poste.io, Mailcow) on a multi-tenant VPS — port collision resolution, reverse-proxy integration, and migration between mail stacks.
version: 1.2.0
triggered-by: user wants to install, replace, or troubleshoot a mail server on the VPS
last-updated: 2026-06-12
metadata:
  hermes:
    tags: [mail, posteio, mailcow, vps, docker]
    related_skills: [vps-security-hardening, nextjs-vps]
---

# VPS Mail Server

Deploy and manage mail servers on the Hermes VPS (`VPS_IP_REDACTED`) — a multi-tenant host running nginx, Tailscale, Workspace, and other services. Mail servers require 8+ privileged ports and will collide with existing services unless handled explicitly.

## Which Mail Server

| Server | Pros | Cons |
|--------|------|------|
| **Poste.io** | Single container, built-in admin UI, Let's Encrypt, Roundcube webmail | Free edition limited |
| **Mailcow** | Full-featured, mature | Heavy (14+ containers), complex teardown |

**Default: Poste.io** — simpler, lighter, one container.

## Poste.io Deployment

### Image

The image is on **Docker Hub**, not GitHub Container Registry:

```bash
analogic/poste.io          # correct
ghcr.io/analogic/poste.io  # WRONG — will 401/denied
```

### Prerequisites — DNS

Poste.io's first-run setup runs connectivity tests against the hostname you provide. These WILL fail unless a DNS A record already points to the VPS.

On Namecheap: Domain List → click domain → **Advanced DNS** tab (NOT the overview page). Add:

```
Type:  A Record
Host:  mail
Value: VPS_IP_REDACTED
TTL:   Automatic
```

Wait 1-2 minutes for propagation before running the Poste.io setup form.

### Port Map

Poste.io wants 80, 443, 25, 110, 143, 465, 587, 993, 995. On the Hermes VPS, **nginx owns 80/443** and **Tailscale grabs 8443-8444**. Remap the web ports:

```bash
docker run -d \
  --name poste \
  -p 25:25 \
  -p 110:110 \
  -p 143:143 \
  -p 465:465 \
  -p 587:587 \
  -p 993:993 \
  -p 995:995 \
  -p 8080:80 \
  -p 8445:443 \
  -e "HTTPS=OFF" \
  -e TZ=America/Chicago \
  -v /var/lib/poste/data:/data \
  analogic/poste.io
```

### Critical Env Vars

| Var | Value | Why |
|-----|-------|-----|
| `HTTPS=OFF` | Required | Prevents Poste.io from redirecting HTTP→HTTPS on port 443 (nginx's territory). Without this, the admin UI loop-redirects. |
| `TZ` | `America/Chicago` | Timezone for logs and mail timestamps |

### Data Volume

Mount to `/data` inside the container, not `/root`:

```bash
-v /var/lib/poste/data:/data    # correct
-v /var/lib/poste:/root          # WRONG — Poste.io uses /data internally
```

### Post-Deploy

```bash
# Check it's healthy
docker ps --filter "name=poste" --format "{{.Status}}"

# First-run setup
curl -sI http://localhost:8080
# → 302 /admin/install/server
```

Access admin at `http://VPS_IP_REDACTED:8080` (HTTP) or `https://VPS_IP_REDACTED:8445` (HTTPS).

For production, put Poste.io behind nginx on a real domain rather than exposing :8080/:8445 directly.

### First-Run Setup

Navigate to `http://<vps-ip>:8080`. The setup form asks for:

| Field | What to enter |
|-------|---------------|
| Mailserver hostname | A real domain with DNS pointing to the VPS (e.g., `mail.veracar.co`). This becomes the server identity for DKIM/SPF. Do NOT leave the container ID — Poste.io auto-fills it, override it. |
| Administrator email | Auto-fills from hostname (e.g., `admin@veracar.co`). Can be changed. |
| Password | Set something strong — this is the admin panel login. |

Use a domain you already own and have pointed at the VPS. After setup, additional domains can be added inside the admin panel — see Multi-Domain Setup below.

### Multi-Domain Setup

Poste.io hosts email for multiple domains under one server. The hostname is just the server identity. After initial setup:

1. Log into admin panel → Virtual Domains
2. Add each additional domain (e.g., `resonatehealing.co`, `dfwwebdesignnow.com`)
3. Create mailboxes per domain

You end up with `blake@veracar.co`, `blake@resonatehealing.co`, `blake@dfwwebdesignnow.com` all managed from one admin panel. Each domain needs its own MX/SPF/DKIM DNS records configured.

### HPanel Firewall Rules

Hostinger HPanel firewall is the VPS gatekeeper (no UFW). Mail ports are blocked until you add Accept rules at **panel.hostinger.com → VPS → Firewall**:

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 25 | TCP | Any | SMTP — mail from other servers |
| 465 | TCP | Any | SMTPS — encrypted outgoing |
| 587 | TCP | Any | Submission — mail client sending |
| 993 | TCP | Any | IMAPS — encrypted mailbox access |
| 995 | TCP | Any | POP3S — encrypted POP3 retrieval |
| 8080 | TCP | Any | Admin panel HTTP |
| 8445 | TCP | Any | Admin panel HTTPS |

**Source MUST be Any** — mail servers need to receive connections from the entire internet. Restricting by IP breaks mail delivery.

**After adding rules, click "Synchronize"** — rules don't apply until synced.

Also: Hostinger often blocks **outbound** port 25 on budget VPS plans. After firewall rules are in, test with:
```bash
docker exec poste telnet gmail-smtp-in.l.google.com 25
```
If it hangs, open a Hostinger support ticket to unblock SMTP outbound.

## Port Collision Resolution Pattern

Before launching ANY mail server, audit what's already bound:

```bash
ss -tlnp | grep -E ':(25|80|110|143|443|465|587|993|995|844[0-9])\b'
```

Known squatters on the Hermes VPS:

| Port Range | Owner | Action |
|------------|-------|--------|
| 80, 443 | nginx | Never touch — serves all websites |
| 8443-8444 | Tailscale (tailscaled) | Never touch — mesh networking |
| 8445+ | Free | Use for remapped HTTPS |
| 8080 | Free | Use for remapped HTTP |
| 25 | Was host Postfix | Stop + disable if migrating to container mail |

## Mailcow Teardown

Mailcow leaves 14+ containers, volumes, networks, and a directory. Full nuke:

```bash
# 1. Stop + remove containers and volumes
cd /root/mailcow-dockerized
docker compose down -v

# 2. Remove directory
cd /root
rm -rf /root/mailcow-dockerized

# 3. Kill host postfix if it was installed alongside
systemctl stop postfix
systemctl disable postfix

# 4. Remove cached Docker images (~3-4GB)
docker rmi $(docker images --filter "reference=ghcr.io/mailcow/*" -q)
docker image prune -a --force
```

See `references/mailcow-teardown.md` for the full session log.

## External Port Verification

Poste.io's built-in connection diagnostics at `/admin/server/connection` frequently reports **false failures**. Its test servers have stale DNS caches and can show "Can't resolve" or "Can't connect" even when everything works. **Do not trust it.**

Verify ports externally instead:

```bash
# Quick: use YouGetSignal in a real browser (not curl — it's JS-rendered)
# https://www.yougetsignal.com/tools/open-ports/
# → Enter VPS IP + port, click Check. "Connected" = open.

# CLI: verify DNS from multiple resolvers
dig +short mail.<domain> A @8.8.8.8
dig +short mail.<domain> A @1.1.1.1
dig +short mail.<domain> A @dns1.registrar-servers.com

# CLI: verify local port binding
for port in 25 110 143 465 587 993 995; do
  timeout 3 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>&1 && echo "PORT $port: OPEN" || echo "PORT $port: CLOSED"
done
```

If external checkers + local port tests pass but Poste.io's diagnostics fail, the diagnostics are wrong — ignore them and proceed.

### Verifying DNS Before Claiming It's Missing

When a user says an A record exists at their registrar, **verify from multiple external resolvers before claiming it doesn't exist.** A record may be present at the authoritative nameserver but not yet propagated, or it may exist and the local test was wrong. Check:
1. Authoritative: `dig +short mail.<domain> A @dns1.registrar-servers.com`
2. Google: `dig +short mail.<domain> A @8.8.8.8`
3. Cloudflare: `dig +short mail.<domain> A @1.1.1.1`

Only after all three return NXDOMAIN should you tell the user the record is missing.

## Pitfalls

1. **Wrong registry** — `ghcr.io/analogic/poste.io` returns `denied`. Use Docker Hub: `analogic/poste.io`.
2. **Port collision silent failure** — Docker's error is `address already in use`. Check `ss -tlnp` before launching.
3. **Tailscale hidden ports** — Tailscale binds 8443 and 8444 on its Tailscale IP (100.78.50.1). These show up in `ss -tlnp` but not in a naive `docker ps` port scan. Always check with `ss`, not `docker ps`.
4. **HTTPS redirect loop** — Without `HTTPS=OFF`, Poste.io redirects all HTTP to port 443. Since nginx owns 443, the redirect breaks. Symptom: `curl -L` loops forever.
5. **Postfix ghost** — Host-installed Postfix may bind port 25 even if the service shows `active (exited)`. Stop + disable it before starting a container mail server.
6. **Poste.io diagnostics are unreliable** — The `/admin/server/connection` page uses external test servers with stale DNS. False negatives are normal. Verify with external port checkers (YouGetSignal) instead of relying on Poste.io's built-in tests.
7. **HPanel Sync is silent** — Adding firewall rules in Hostinger HPanel does nothing until you click **"Synchronize"** at the top of the page. No warning, no reminder. Added rules sitting unsynced are the #1 cause of "ports not working."

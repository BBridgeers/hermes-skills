---
name: posteio-mail-server
description: Deploy and manage Poste.io mail server on a VPS — installation, port mapping, firewall, DNS, diagnostics, and migration from other mail servers (Mailcow, etc.).
version: 1.0.0
triggered_by: mail server setup, Poste.io deployment, Mailcow replacement, email server configuration
---

# Poste.io Mail Server

Deploy, configure, and troubleshoot the Poste.io mail server in a single Docker container on a bare-metal VPS.

## When to Use

- Deploying a new mail server
- Replacing Mailcow, iRedMail, or another mail server with Poste.io
- Mail server port/firewall/DNS diagnostics
- Configuring Poste.io admin panel, domains, and email accounts

## Deployment

### Prerequisites

- VPS with public IP
- Docker installed and running
- Domain with DNS control (for MX, SPF, DKIM records)
- Hostinger VPS: HPanel firewall is the sole gatekeeper — NO UFW

### Docker Run

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

### Port Mapping

Poste.io needs these ports. Map carefully around existing services:

| Poste.io Internal | Recommended External | Purpose |
|---|---|---|
| 25 | 25 | SMTP incoming |
| 80 | 8080 | Web admin HTTP (avoid nginx collision) |
| 110 | 110 | POP3 |
| 143 | 143 | IMAP |
| 443 | 8445 | Web admin HTTPS (avoid nginx + Tailscale 8443) |
| 465 | 465 | SMTPS |
| 587 | 587 | Submission |
| 993 | 993 | IMAPS |
| 995 | 995 | POP3S |
| 4190 | 4190 | Sieve (optional) |

**Critical:** Never use 80 or 443 as external ports if nginx is running on the host. Use 8080 and 8445+ instead. Check Tailscale — it often claims 8443-8444.

### HTTPS=OFF

Set `HTTPS=OFF` when:
- Using non-standard HTTPS port (anything other than 443)
- Poste.io sits behind nginx reverse proxy
- Let's Encrypt can't operate on the mapped port

Without this, Poste.io force-redirects HTTP→HTTPS on port 443, which breaks if nginx owns 443.

### Image Source

The image is on **Docker Hub**: `analogic/poste.io`

Do NOT use `ghcr.io/analogic/poste.io` — that registry returns "denied".

## Firewall Rules

### Hostinger HPanel

Go to **panel.hostinger.com → VPS → Firewall**. Add these Accept/Any rules:

```
25/tcp    — SMTP incoming
465/tcp   — SMTPS
587/tcp   — Submission
993/tcp   — IMAPS
995/tcp   — POP3S
8080/tcp  — Admin HTTP
8445/tcp  — Admin HTTPS
```

After adding rules, click **"Synchronize"** to push changes. Rules don't take effect until synced.

Skip unencrypted ports (110, 143) unless legacy clients need them.

**Hostinger may block outbound port 25** on some VPS plans. If Poste.io can't send mail, open a support ticket requesting SMTP outbound unblock.

### UFW

Not used on this VPS. HPanel firewall sits above the VPS at the network edge. Do not configure UFW — it's redundant and causes confusion.

## DNS Setup

### Required Records

Poste.io's diagnostics test from external servers — DNS MUST resolve from the public internet, not just locally.

```
Type:  A
Host:  mail
Value: <VPS_IP>
TTL:   Automatic
```

If the A record doesn't exist, Poste.io's connection tests will show "Can't resolve" for the hostname, and ALL subsequent port tests will fail with "Can't connection to".

### MX Record

After setup, add MX record pointing to the mail hostname for any domain you want to receive mail on.

## First-Run Setup

1. Navigate to `http://<VPS_IP>:8080`
2. First visit runs setup wizard:
   - **Mailserver hostname:** e.g. `mail.veracar.co` (must have A record)
   - **Administrator email:** e.g. `admin@veracar.co`
   - **Password:** set a strong password
3. Setup creates `/var/lib/poste/data/server.ini`
4. After setup, admin login at `http://<VPS_IP>:8080/admin/login`

## Connection Diagnostics

Admin panel → Server Status → Connection Diagnostics

Tests run from Poste.io's external servers. Common failures:

| Symptom | Cause | Fix |
|---|---|---|
| "Can't resolve hostname" on all tests | Missing DNS A record for mail hostname | Add A record at domain registrar |
| "Can't connection to" on all ports | HPanel firewall not synced | Click "Synchronize" in HPanel firewall |
| Port 25 outbound fails | Hostinger blocks outbound SMTP | Contact Hostinger support |
| Port 80/443 tests blank | `HTTPS=OFF` set, ports not standard | Expected — tests skip when ports differ |

## Migration from Mailcow

```bash
# 1. Tear down Mailcow completely
cd /root/mailcow-dockerized
docker compose down -v
cd ..
rm -rf mailcow-dockerized

# 2. Remove cached Mailcow images
docker rmi $(docker images --filter "reference=ghcr.io/mailcow/*" -q)
docker image prune -a --force

# 3. Stop host Postfix if running
systemctl stop postfix
systemctl disable postfix

# 4. Deploy Poste.io (see Docker Run section above)
```

## Key Files

| File | Purpose |
|---|---|
| `/var/lib/poste/data/server.ini` | Main configuration |
| `/var/lib/poste/data/users.db` | SQLite user database |
| `/var/lib/poste/data/domains/` | Per-domain configs |

## Pitfalls

- **Image registry:** `analogic/poste.io` on Docker Hub, NOT `ghcr.io/analogic/poste.io`.
- **HTTPS=OFF required** when port 443 is mapped to anything other than 443 externally.
- **Tailscale claims 8443-8444** — use 8445+ for admin HTTPS.
- **Connection diagnostics test from EXTERNAL servers** — local `dig` success doesn't mean the tests pass. DNS must resolve publicly.
- **HPanel sync** — adding firewall rules isn't enough; you must click "Synchronize" to push them.
- **Port 25 outbound** — Hostinger may block this by default. Requires support ticket.

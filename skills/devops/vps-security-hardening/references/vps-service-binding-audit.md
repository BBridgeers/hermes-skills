# VPS Service Binding Audit & Lockdown — Session 2026-05-25

## Audit Output (Before Hardening)

```bash
sudo ss -tulpn | grep -E ':80|:22|:443|:8642|:8765|:3100|:3000|:3001|:11434'
```

| Port | Service | Bind | Status | Action |
|------|---------|------|--------|--------|
| 22 | sshd | `0.0.0.0:22` | ✅ Keep — SSH access | — |
| 80 | nginx | `0.0.0.0:80` | ✅ Keep — public entrypoint | — |
| 8000 | honcho-api (docker) | `127.0.0.1:8000->8000/tcp` | ✅ Locked — Docker port mapping | — |
| 8642 | hermes-gateway | `0.0.0.0:8642` | ⚠️ Public liability | **Lock to 127.0.0.1** |
| 8765 | fb-scraper | `0.0.0.0:8765` | ⚠️ Public liability | **Lock to 127.0.0.1** |
| 11434 | ollama | `127.0.0.1:11434` | ✅ Locked | — |
| 3000 | hermes-workspace (docker) | `127.0.0.1:3000->3000/tcp` | ✅ Locked — Docker port mapping | — |
| 3100 | hermes-workspace (node) | `0.0.0.0:3100` | ⚠️ Public liability | **Lock to 127.0.0.1** |
| 3001 | next-server | `0.0.0.0:3001` | ⚠️ Legacy/unused | **Kill if not in use** |

## Remediation Steps

### 1. Hermes Gateway (`config.yaml`)

```bash
sudo sed -i 's/host: 0.0.0.0/host: 127.0.0.1/' /root/.hermes/config.yaml
# Restart
pkill -f 'hermes.*gateway'
hermes gateway run --replace &
```

**Verification**:
```bash
sudo ss -tulpn | grep 8642
# Expected: tcp LISTEN 0 128 127.0.0.1:8642 0.0.0.0:*
```

### 2. fb-scraper (`server.py`)

```bash
sed -i 's/host="0.0.0.0"/host="127.0.0.1"/' /root/vehicle-analyzer/scraper/server.py
sudo systemctl restart fb-scraper
```

**Verification**:
```bash
sudo ss -tulpn | grep 8765
# Expected: tcp LISTEN 0 2048 127.0.0.1:8765 0.0.0.0:*
```

### 3. hermes-workspace (`vite.config.ts`)

```bash
sed -i "s/host: '0.0.0.0'/host: '127.0.0.1'/" /root/hermes-workspace/vite.config.ts
pkill -f 'node.*vite'
npm run dev -- --port 3100 --host 127.0.0.1 &
```

**Verification**:
```bash
sudo ss -tulpn | grep 3100
# Expected: tcp LISTEN 0 511 127.0.0.1:3100 0.0.0.0:*
```

### 4. Legacy Next.js Process (Port 3001)

```bash
pkill -f 'next-server'
```

If not actively used by hermes-workspace UI, this is stale and safe to kill.

### 5. WireGuard (Port 51820/udp)

If not using WireGuard VPN:
```bash
sudo systemctl stop tailscale && sudo systemctl disable tailscale
sudo ufw deny 51820/udp
```

If using WireGuard — keep the binding.

## Post-Remediation Verification

```bash
# All internal services should bind to 127.0.0.1
sudo ss -tulpn | grep -E ':8642|:8765|:3100|:11434'

# Only SSH and HTTP/HTTPS should remain public
sudo ss -tulpn | grep -E ':22|:80|:443'
```

## Firewall Sync

Update UFW rules:
```bash
sudo ufw deny 8642/tcp && sudo ufw deny 3100/tcp
```

Update Hostinger cloud firewall (panel → VPS → Firewall):
- Delete rules exposing ports `8642`, `8765`, `3100`, `3001`
- Keep only `22`, `80`, `443` (optionally `51820/udp` if WireGuard in use)

## Key Learnings

1. **Hermes gateway binds in `config.yaml` under `api_server:` section**
2. **fb-scraper binds in FastAPI uvicorn.run call in `server.py`**
3. **Hermes-workspace binds in `vite.config.ts` server.host setting**
4. **Docker port mapping (`0.0.0.0:port->port/tcp`) is already locked** — Docker transparently binds to `127.0.0.1`
5. **Next.js devserver runs as `next-server (v15.5.15)` — likely legacy**
6. **Always verify with `ss -tulpn` after restart — don't assume the restart picked up the new config**
7. **Systemd service names differ by distro — `ssh.service` not `sshd.service` on Ubuntu 24.04**
8. **Hermes gateway restart is `hermes gateway run --replace`, not `systemctl restart hermes-gateway`** (no systemd unit)
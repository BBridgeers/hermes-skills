---
name: tailscale-mesh-networking
description: Tailscale mesh networking on Ubuntu VPS — exit node setup (iptables MASQUERADE, IP forwarding, rule persistence), troubleshooting stale connections, DERP relay fallback, subnet routing, and SSH tunnel alternatives when Tailscale direct connections fail (especially on restrictive networks like hotel/public Wi-Fi).
tags: [devops, tailscale, vps, mesh-networking, troubleshooting, ssh-tunnel]
---

# Tailscale Mesh Networking — VPS Troubleshooting

Diagnose and fix Tailscale connectivity issues between VPS and client devices (laptop, phone). Covers stale mesh connections, DERP relay fallback, and SSH tunnel workarounds.

## Key VPS Facts

| Item | Value |
|---|---|
| Tailscale IP | `100.78.50.1` |
| Tailnet | `dfwwebdesignnow@gmail.com` |
| Magic DNS | `srv1617682.tail0da406.ts.net` |

## Diagnosis Commands

```bash
# Full status
tailscale status

# JSON status (for scripting)
tailscale status --json

# Check specific peer status
tailscale status --json | jq '.Peer[] | select(.HostName == "lenovo") | {Active, RxBytes, TxBytes, LastHandshake, Relay}'

# Ping a peer from VPS
tailscale ping 100.66.73.41

# Network connectivity check
tailscale netcheck
```

## Stale Connection Symptoms

**Symptoms:**
- `tailscale status` shows all devices but Windows laptop shows no "active" indicator
- `Active: false`, `RxBytes: 0`, `TxBytes: 0` for the peer
- `Test-NetConnection` from Windows fails: `TcpTestSucceeded : False` on ALL ports (even 22)
- `curl http://100.78.50.1:8787` from laptop: "Failed to connect"
- VPS CAN ping laptop (`tailscale ping <laptop-ip>` returns pong) but laptop CANNOT reach VPS

**Root Cause:** Windows Tailscale shows "Connected" in admin panel but the encrypted mesh tunnel is not actually established. Common after:
- Switching Tailscale accounts (logout/login) — **most common cause**
- Long idle periods
- Network changes

**Fix — Complete reset (both sides):**
```powershell
# On Windows PowerShell
tailscale logout
tailscale down
# Wait 10 seconds
tailscale up
# Authenticate at the login URL shown
```
```bash
# On VPS
sudo systemctl restart tailscaled
sleep 8
tailscale status
```

**If still failing after reset — Check Windows Firewall:**
When `Test-NetConnection` fails on ALL ports (including 22/SSH) but `tailscale status` shows the peer as "active", Windows Firewall is likely blocking outbound on the Tailscale interface.

```powershell
# Run PowerShell as Administrator - TEMPORARY TEST
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled False
# Test again
Test-NetConnection -ComputerName 100.78.50.1 -Port 22
```
If it works with firewall off, add a permissive rule for Tailscale:
```powershell
New-NetFirewallRule -DisplayName "Allow Tailscale" -Direction Outbound -InterfaceAlias "Tailscale" -Action Allow -Protocol TCP
```

**Critical: `ipconfig | findstr "tailscale"` should show a Tailscale adapter. If empty, Tailscale service is running but the TUN interface is broken — restart the Tailscale service.**

## DERP Relay Fallback

**Symptoms:**
- `Relay: "nyc"` (or other region) in peer status
- All traffic relayed through Tailscale DERP servers
- TCP services (HTTP, WebSocket) unreliable through relay
- Ping works but port connections fail

**Root Cause:** Hotel/public Wi-Fi blocks UDP hole-punching. Tailscale falls back to DERP relay which may not reliably forward TCP traffic to custom ports.

**Workaround — SSH Tunnel (most reliable):**
```powershell
# On laptop - this works even when Tailscale TCP fails
ssh -N -L 8787:127.0.0.1:8787 root@VPS_IP_REDACTED
# Then access http://127.0.0.1:8787 (NOT localhost)
```

**Important:** Use `127.0.0.1` in browser URL, not `localhost` — some servers reject `localhost` Host header.

## SSH Tunnel Pattern

When Tailscale DERP relay makes services unreachable, use SSH tunnel instead:

```powershell
# On laptop — forwards local port to VPS service
ssh -N -L <local_port>:127.0.0.1:<service_port> root@<vps_public_ip>

# Examples:
ssh -N -L 8787:127.0.0.1:8787 root@VPS_IP_REDACTED  # Hermes WebUI
ssh -N -L 3100:127.0.0.1:3100 root@VPS_IP_REDACTED  # Hermes Workspace
ssh -N -L 3002:127.0.0.1:3002 root@VPS_IP_REDACTED  # Veracar
ssh -N -L 8642:127.0.0.1:8642 root@VPS_IP_REDACTED  # Hermes Gateway
```

**Important:** Use `127.0.0.1` in browser URL, not `localhost` — some servers reject `localhost` Host header.

## Hermes WebUI SSH Tunnel Issue

**Symptom:** SSH tunnel connects but browser shows "empty page" or `NS_ERROR_NET_EMPTY_RESPONSE`. The server returns HTTP 200 with full HTML (verified via `curl -v http://127.0.0.1:8787/login` on VPS), but the browser gets nothing.

**Root Cause:** Hermes WebUI's Python HTTP server has strict Content-Security-Policy headers and host-checking logic. When served through an SSH tunnel, subsequent JS/CSS/API requests get blocked by CSP because the browser sees `127.0.0.1` but the server expects `localhost` or the Tailscale IP.

**Workaround:** Use the SOCKS proxy method instead of port forwarding:
```powershell
ssh -N -D 9050 root@VPS_IP_REDACTED
```
Then configure browser SOCKS5 proxy `127.0.0.1:9050` with "Proxy DNS" enabled, and browse to `http://100.78.50.1:8787/login`.

**Note:** If the SOCKS proxy approach also fails (Firefox reports "Couldn't connect to VPN"), the issue is the hotel network blocking all non-standard traffic. In that case, the only reliable option is to use a mobile hotspot or wait until on a trusted network.

- **Admin:** `https://login.tailscale.com/admin/machines`
- **Resource hub:** `https://login.tailscale.com/admin/acls`
- Sign in with Google → `dfwwebdesignnow@gmail.com`

## Exit Node Setup & Troubleshooting

Configuring the VPS as a Tailscale exit node so client devices can route all internet traffic through it (encrypted).

### Prerequisites

```bash
# Enable IP forwarding (both v4 and v6)
sysctl net.ipv4.ip_forward=1
sysctl net.ipv6.conf.all.forwarding=1

# Persist across reboots
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.conf
```

### Advertise as Exit Node

```bash
# CRITICAL: Include ALL existing flags. tailscale up is declarative — omitting a flag removes it.
tailscale up --advertise-exit-node --ssh
```

**Pitfall:** Running `tailscale up --advertise-exit-node` without `--ssh` errors out because `--ssh` is already active. The command must include all non-default flags currently set.

### Required iptables MASQUERADE Rule

Without this rule, exit node traffic arrives at the VPS but never gets NATed back to the internet — **complete internet blackout on the client** with no error message on the VPS side.

```bash
# Get the default interface
ip route show default | awk '{print $5}'   # → eth0

# Add the rule
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Verify
iptables -t nat -L POSTROUTING -n -v | grep -i masquerade
# Should show: MASQUERADE ... eth0 ... (with non-zero packet counters when exit node is in use)
```

### Persist iptables Rules

The MASQUERADE rule is lost on reboot unless persisted.

```bash
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6
```

If `iptables-persistent` package is installed (Debian/Ubuntu), it auto-loads these on boot.

### Verification

```bash
# VPS should show "offers exit node"
tailscale status

# After client selects VPS as exit node, check NAT counters are incrementing:
iptables -t nat -L POSTROUTING -n -v | grep eth0
# Non-zero packet count = exit node traffic is flowing

# Direct connection should still show (not relay):
tailscale status --json | jq '.Peer[] | select(.HostName=="lenovo") | {Active, Relay}'
```

### Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Client loses ALL internet after selecting exit node | Missing MASQUERADE rule on VPS | Add `iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` |
| Exit node works but breaks after VPS reboot | iptables rules not persisted | Save to `/etc/iptables/rules.v4` |
| `tailscale up` fails with "requires mentioning all non-default flags" | Missing `--ssh` or other active flag | Re-run with all current flags: `tailscale up --advertise-exit-node --ssh` |
| Health check: "IP forwarding is disabled" | IPv6 forwarding not enabled | `sysctl net.ipv6.conf.all.forwarding=1` |
| `ExitNode` field null in JSON | Normal — JSON field tracks whether the node IS using an exit node, not whether it's OFFERING one | Use `tailscale status` human-readable output to confirm "offers exit node" |

### Post-Reboot Checklist

After any VPS reboot:
1. `sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding` → both should be 1
2. `iptables -t nat -L POSTROUTING | grep MASQUERADE` → must include eth0
3. `tailscale status` → must show "offers exit node"

## Exit Node Setup (with iptables Persistence)

To configure the VPS as a Tailscale exit node:

```bash
# 1. Enable IP forwarding
sysctl net.ipv4.ip_forward=1
sysctl net.ipv6.conf.all.forwarding=1
# Persist:
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.conf

# 2. Advertise as exit node
tailscale up --advertise-exit-node --ssh

# 3. Add MASQUERADE rule (CRITICAL — without this, client internet breaks)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# 4. Persist iptables rules for reboot survival
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6

# 5. Verify after reboot
iptables -t nat -L POSTROUTING -n | grep MASQUERADE
# Must show eth0 in output
```

### Pitfall: Missing MASQUERADE = Silent Internet Blackout

If the MASQUERADE iptables rule is not present, the exit node forwards packets to the VPS but never NATs them back out. The client's internet silently dies — no error message, just no connectivity. Common after VPS reboots if rules weren't persisted.

### Pitfall: IPv6 Forwarding Disabled

`tailscale up --advertise-exit-node` warns "IPv6 forwarding is disabled." Enable it with `sysctl net.ipv6.conf.all.forwarding=1` and persist in sysctl.conf.

Tailscale uses its own encrypted tunnel — UFW rules for Tailscale ports should be `Allow`. However, **Hostinger HPanel cloud firewall blocks ports independently of UFW**. If a service runs on the VPS (like Hermes WebUI on 8787), the Hostinger firewall must allow that port for external access — but for Tailscale mesh traffic, the Tailscale tunnel bypasses UFW/Hostinger firewall entirely. Tailscale traffic uses WireGuard UDP.

## Exit Node Setup

When the VPS is configured as a Tailscale exit node, client devices route ALL internet traffic through it. This requires specific iptables and kernel configuration.

### Enable IP Forwarding
```bash
# IPv4
sysctl net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf

# IPv6
sysctl net.ipv6.conf.all.forwarding=1
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.conf
```
Without IPv6 forwarding enabled, Tailscale health check warns and exit nodes may not work correctly.

### Advertise Exit Node
```bash
# MUST include --ssh if SSH is already enabled on the machine
tailscale up --advertise-exit-node --ssh
```
Tailscale requires re-stating ALL non-default flags. Omitting `--ssh` when SSH was already enabled causes `Error: changing settings via 'tailscale up' requires mentioning all non-default flags`.

### MASQUERADE Rule (Critical)
Without MASQUERADE, forwarded packets reach the VPS but never get NATed back out to the internet. Client devices experience complete internet blackout when selecting the exit node.
```bash
# Find primary interface
ip route show default | awk '{print $5}'  # usually eth0

# Add MASQUERADE
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Verify
iptables -t nat -L POSTROUTING -n | grep MASQUERADE
```

### Persist iptables Rules (Survive Reboots)
```bash
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4
ip6tables-save > /etc/iptables/rules.v6
```
If `iptables-persistent` package fails to install (dpkg interrupted), the manual save approach works.

### Verify Exit Node is Active
From the VPS side, `tailscale status` shows `offers exit node`. From client side, select the VPS as exit node in Tailscale menu. Verify MASQUERADE counters increment:
```bash
iptables -t nat -L POSTROUTING -n -v | grep eth0
# Non-zero packet count = exit node traffic flowing
```

### Pitfall: Exit Node Silently Broken After Reboot
iptables rules are in-memory only unless persisted. After any VPS reboot, verify:
```bash
iptables -t nat -L POSTROUTING | grep MASQUERADE | grep eth0
```
If missing, re-add the rule. This is a hard boundary — exit node breaks silently without it.

## Exit Node + qBittorrent (WSL2)

When running qBittorrent inside WSL2 and routing traffic through a Tailscale exit node, WSL2 cannot see the Windows Tailscale adapter. The qBittorrent Network Interface dropdown only shows Linux interfaces (`Any interface`, `lo`, `eth0`).

### Full qBittorrent Settings Reference (Exit Node Configured)

**Connection**

| Setting | Value | Why |
|---|---|---|
| Listening port | `45160` (or any high port) | Arbitrary — just needs HPanel firewall rule |
| UPnP/NAT-PMP | **Unchecked** | Useless through exit node |
| Global max connections | 500 | Good default |
| Per-torrent connections | 100 | Good default |
| Global max upload slots | 20 | Good default |
| Per-torrent upload slots | 4 | Good default |
| Proxy Server type | **None** | Exit node handles routing; proxy is redundant |

**Speed / Rate Limits**

| Setting | Value | Why |
|---|---|---|
| Global Upload | 0 (unlimited) | VPS pipe is the bottleneck, not qBit |
| Global Download | 0 (unlimited) | Same |
| Alternative Upload | 0 (unlimited) | 10 KiB/s default is useless |
| Alternative Download | 0 (unlimited) | Same |
| Schedule alternative limits | **Unchecked** | No need to throttle |
| Apply rate limit to μTP | **Checked** | Prevents μTP bypass |
| Apply rate limit to transport overhead | **Unchecked** | Wastes rate limit on metadata |
| Apply rate limit to peers on LAN | **Unchecked** | No LAN peers |

**Privacy**

| Setting | Value | Why |
|---|---|---|
| DHT | **Checked** | More peers = faster |
| PeX | **Checked** | Same |
| Local Peer Discovery | **Unchecked** | No LAN peers through exit node |
| Encryption mode | **Require encryption** | Better privacy — only encrypted peers |
| Anonymous mode | **Unchecked** | Breaks trackers, not needed with exit node |

**Queueing**

| Setting | Value | Why |
|---|---|---|
| Max active downloads | **5** | 3 is too conservative |
| Max active uploads | **5** | Match downloads |
| Max active torrents | **10** | Double the default 5 |
| Don't count slow torrents | **Checked** | Prevents stalled torrents blocking queue |

**Seeding**

| Setting | Value | Why |
|---|---|---|
| Ratio reaches | 1.0, then Pause | Reasonable — seed back what you take |
| Inactive seeding time | 1440 min (24h) | Reasonable |

**BitTorrent (Advanced)**

| Setting | Value | Why |
|---|---|---|
| Network interface | **eth0** | WSL2 adapter; traffic exits via Windows → Tailscale → VPS |
| Optional IP to bind to | **All IPv4 addresses** | WSL2 Tailscale IP not visible inside WSL2 |
| IP address reported to trackers | **`VPS_IP_REDACTED`** | VPS public IP so peers can connect inbound |
| μTP-TCP mixed mode | Prefer TCP | Stable through exit node |
| Validate HTTPS tracker certs | **Checked** | Security |

**Web UI**

| Setting | Value | Why |
|---|---|---|
| Port | 9090 (default) | Fine — only accessible locally |
| UPnP | **Unchecked** | No router forwarding through exit node |
| Bypass auth on localhost | **Checked** | Convenience for local access |
| CSRF protection | **Checked** | Security |
| Host header validation | **Checked** | Security |

### Recommended Tracker List

Paste into "Automatically add these trackers to new downloads":

```
udp://tracker.opentrackr.org:1337/announce
udp://open.stealth.si:80/announce
udp://tracker.torrent.eu.org:451/announce
udp://exodus.desync.com:6969/announce
udp://tracker.tiny-vps.com:52561/announce
```

### Recommended Search Plugins (Adult Content)

Accessible via View → Search Engine → Search plugins:

| Plugin | Type | Notes |
|---|---|---|
| **My Porn Club** | Public | General adult, no account needed |
| **XXXClub** | Public | General adult, no account needed |
| **Sukebei (Nyaa)** | Public | Japanese adult (hentai, JAV) |
| **Pornolab** | Private | Largest adult tracker — requires account at pornolab.net |

### Pitfall: "Tailscale" Not in qBittorrent Interface Dropdown

qBittorrent runs inside WSL2 Linux and only sees Linux network interfaces. The Windows `Tailscale Tunnel` adapter is invisible. Select `eth0` — all WSL2 traffic routes through the Windows host which is on the exit node. To confirm the adapter name on Windows:
```powershell
Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object Name, InterfaceDescription
# Look for: Tailscale  Tailscale Tunnel
```

### Pitfall: Tracker Announce Shows Wrong IP

Without setting "IP address reported to trackers" to the VPS public IP (`VPS_IP_REDACTED`), trackers see the WSL2 internal IP (e.g. `172.x.x.x`) which is unreachable. Peers can't connect inbound, making you firewalled and slow.

### Pitfall: GPG Key for qBittorrent

The qBittorrent GPG public key block is for verifying source tarball signatures. **Not needed** for package-manager installs. Skip it.

### Proton.me Account Creation for Tracker Registration

Many private trackers (Pornolab, etc.) require an email for registration. Proton.me is ideal — free, encrypted, no phone required.

**Browser signup fails — do it manually.** Proton's signup page uses a CAPTCHA embedded in challenge iframes (`account-api.proton.me/challenge/v4/html`) that blocks automated submission. The VPS browser can fill the form fields but cannot solve the CAPTCHA. Don't waste time automating this — tell the user the three fields and let them do it in 60 seconds:

```
URL:     https://account.proton.me/signup
Plan:    Free
Email:   [chosen-username]@proton.me
Password: [generated-password]
Recovery: [backup-email]
```

Generate the password with: `python3 -c "import secrets,string;a=string.ascii_letters+string.digits+'!@#$%';print(''.join(secrets.choice(a) for _ in range(20)))"`

### Verification

After enabling exit node on Windows (Tailscale tray → select VPS as exit node), verify from laptop browser:
- `ifconfig.me` should show `2a02:4780:75:f023::1` (VPS IPv6) or `VPS_IP_REDACTED` (VPS IPv4)
- If it shows your home ISP IP, exit node is not active

### HPanel Firewall Rule for Incoming Peers

Add a Hostinger HPanel firewall rule for qBittorrent's listening port (default `45160`) — Protocol: TCP, Port: `45160`, Source: Any. Without it, torrent peers can't connect inbound through the VPS, making you firewalled with limited peer pool.

## Mobile Device Troubleshooting (iOS/Android)

### iPhone Tailscale Offline

**Symptom:** `tailscale status` on VPS shows the iPhone as `offline, last seen Xd ago`. Laptop is connected fine.

**Diagnosis:**
```bash
tailscale status
# Shows: iphone-15-pro  offline, last seen 1d ago
```

**Fixes in priority order:**
1. Open Tailscale app on phone — iOS aggressively kills VPN apps in background. Toggle the switch ON.
2. If it won't connect, go to iOS Settings → General → VPN & Device Management → delete Tailscale profile, then re-open Tailscale app to recreate it.
3. If still failing, Tailscale app → tap avatar → Logout, then log back in to refresh auth keys.

### Hotel/Public WiFi Blocking Ports

**Symptom:** Termius SSH client works on laptop WiFi but fails on phone WiFi (same network). Works when phone switches to cellular data.

**Root Cause:** Hotel/extended-stay WiFi often blocks non-standard ports. Port 2222 (custom SSH) is frequently blocked while common ports (80, 443) pass through.

**Impact on Tailscale:** Hotel WiFi may also block WireGuard UDP traffic, preventing Tailscale from establishing direct or relayed connections on mobile.

**Workarounds:**
- Use cellular data for SSH and Tailscale on mobile when on restrictive WiFi
- SSH tunnel from laptop (which is on the same network) and use that as a jump host
- Configure Termius to use a non-blocked port if one is available on the VPS (requires HPanel firewall rule + sshd config change)

### Termius Independence from Tailscale

Termius connects to `VPS_IP_REDACTED:2222` via direct public internet — it does NOT require Tailscale. If Termius fails on a network, the issue is the network blocking port 2222, not a Tailscale problem. Don't conflate the two.

### Docker WireGuard Container vs Tailscale

The Docker `wireguard` container on this VPS is a **separate standalone VPN** from Tailscale. It has its own config (`/config/wg_confs/wg0.conf`), its own peers (peer_pc, peer_phone), and its own network (`10.13.13.0/24`). Tailscale operates independently on `100.x.x.x` range. WireGuard container being down or having zero handshakes does NOT affect Tailscale, and vice versa. Don't conflate the two.

Check WireGuard status with `docker exec wireguard wg show` (handshakes show active connections). Zero handshakes = no client has connected.

## Related Skills

- `veracar-app-deployment` — Next.js app deployment with Traefik HTTPS
- `hermes-workspace-deployment` — Vite dev server deployment
- `hermes-webui-deployment` — Hermes WebUI systemd service (port 8787)
- `devops/vps-ssh-troubleshooting` — SSH connectivity issues

## Consolidated Skills

This skill absorbs: `tailscale-troubleshooting`.

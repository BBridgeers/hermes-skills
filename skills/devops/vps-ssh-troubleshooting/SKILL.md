---
name: vps-ssh-troubleshooting
version: 2
description: Rapid diagnostics for SSH connection failures to VPS when SSH was previously working
last-updated: 2026-05-30
---

# Skill: VPS SSH Troubleshooting
Version: 2
Triggered-by: User reports SSH connection issues to VPS — "Connection refused" or "Permission denied (publickey)"
Notes: Updated 2026-05-30 — already handles both Port 22 patterns (#Port 22 and Port 22), ufw-not-installed pitfall documented, Hostinger panel requirement emphasized

## Pattern
User SSHing from Ubuntu to VPS via public IP (`VPS_IP_REDACTED`) fails with connection refused or permission denied. SSH was working previously, then broke. Multiple key generations and config edits occurred mid-session.

## Protocol

### Phase 1: Verify SSH Is Listening
```
sudo ss -tlnp | grep :22
sudo systemctl status ssh --no-pager -l 3
```
- If `sshd` not running: `sudo systemctl start ssh`
- If `sshd` running but port 22 not listening: check `sshd_config` for `ListenAddress` or port mismatch

### Phase 2: Check Network Path (Not "Router Blame")
- Your hotel/corporate network likely blocks outbound SSH to port 22
- Test: `ping -c 3 VPS_IP_REDACTED` or `curl -I -m 5 http://VPS_IP_REDACTED:22`
- If ping works but SSH fails: it's a **VPS-side issue**, not network
- If ping times out: **hotel router/corporate firewall blocking port 22**

### Phase 3: Validate Key Match
```
# On Ubuntu
ssh-keygen -l -f ~/.ssh/id_ed25519.pub

# On VPS — compare to authorized_keys fingerprint
ssh-keygen -l -f /root/.ssh/authorized_keys | grep yoga
```
- Fingerprint must match EXACTLY — even whitespace differences break auth
- Multiple keys in `authorized_keys` can cause "wrong key offered" failures

### Phase 4: Check Root Login Config
```
# Running sshd config (not file!)
sudo sshd -T 2>/dev/null | grep -i permitrootlogin

# File check — systemd includes may override
grep -n "PermitRootLogin" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf
```
- **Critical**: `/etc/ssh/sshd_config.d/hardening.conf` often overrides main config
- Fix: `sudo sed -i '/^PermitRootLogin/s/no/yes/' /etc/ssh/sshd_config.d/hardening.conf`
- Restart: `sudo systemctl restart ssh`

### Phase 5: If Port 22 Blocked, Change SSH Port
```
# Hostinger/cloud firewall frequently blocks SSH port 22 egress
# Test if port 22 is reachable (not just ping)
timeout 3 curl -s -I http://VPS_IP_REDACTED:22 2>&1
# If connection times out with no response: port 22 blocked by hotel/corporate network

# Check which Port line exists (commented or active)
grep -n 'Port' /etc/ssh/sshd_config
# If "Port 22" (active):    sudo sed -i 's/^Port 22$/Port 2222/' /etc/ssh/sshd_config
# If "#Port 22" (commented): sudo sed -i 's/^#Port 22$/Port 2222/' /etc/ssh/sshd_config

# CRITICAL: systemd socket requires reload after port change
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket ssh

# Verify sshd listening on new port ONLY (port 22 should be gone)
ss -tlnp | grep -E ':(22|2222)\s'
# Should show: LISTEN 0 4096 0.0.0.0:2222 (and NOT port 22)

# ⚠️ MANDATORY: Open port in Hostinger firewall panel BEFORE testing
# panel.hostinger.com → VPS → Firewall → Add port 2222 TCP inbound
# UFW alone is INSUFFICIENT — Hostinger's cloud firewall sits above the VPS

# On Ubuntu, add to ~/.ssh/config:
Host hermes-vps
    HostName VPS_IP_REDACTED
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3

# Then just: ssh hermes-vps (no -p 2222 needed)
```
- **Hostinger cloud firewall blocks SSH egress on port 22** — confirmed via hotel network
- Change to port 2222 or 443, add SSH config alias to avoid typing `-p`
- **Systemd socket activation requires `daemon-reload` after port changes**
- **UFW may not be installed on Hostinger VPS** — the real firewall is the Hostinger panel (panel.hostinger.com → VPS → Firewall). Opening a port in UFW/iptrules alone will NOT make it reachable.

**Ubuntu-side vs VPS-side commands**:
- `sudo sed -i ... /etc/ssh/...` runs on VPS (remote)
- `ssh-keygen -l -f ~/.ssh/id_ed25519.pub` runs on Ubuntu (local)
- Mixing these up is a common cause of "Permission denied" — always verify which machine you're on

## Failure Modes

| Failure Signal | Root Cause | Fix |
|---|---|---|
| "Connection refused" | sshd not running OR port 22 blocked (Hostinger/hotel) | Check `ss -tlnp \| grep :22`; if running, change to port 2222 or use Tailscale |
| SSH port 2222 not reachable from client | Hostinger HPanel firewall doesn't have port 2222 open | Add TCP 2222 rule in panel.hostinger.com → VPS → Firewall |
| "Permission denied (publickey)" from new client | Client key not in `authorized_keys` OR `PasswordAuthentication no` in drop-in configs | Copy pub key to VPS `authorized_keys`; or enable password auth temporarily |
| "Connection timed out" (no response at all) | Hotel/corporate network silently drops port 22 packets | Change SSH to port 2222 + open port in Hostinger panel |
| "Permission denied (publickey)" | Key mismatch OR `PermitRootLogin no` | Verify fingerprint match; check `/etc/ssh/sshd_config.d/` overrides |
| "Host key verification failed" | Tailscale vs public IP use different keys | Remove `~/.ssh/known_hosts` entry or run `ssh-keygen -R 100.78.50.1` |
| "sudo: 3 incorrect password attempts" | User ran Ubuntu-side commands thinking they were VPS | Remember: `sudo sed -i ... /etc/ssh/...` must run on VPS, not Ubuntu |
| `curl -I VPS_IP_REDACTED:22` fails but `sshd` running | Hostinger cloud blocks SSH port 22 egress | Change SSH port to 2222/443 and reload systemd socket |
| SSH still on port 22 after running sed | `Port 22` is uncommented, but sed looked for `#Port 22` (commented) | Run `grep -n 'Port' /etc/ssh/sshd_config` first; use `s/^Port 22$/Port 2222/` if active |
| `ufw: command not found` on Hostinger VPS | UFW not installed — Hostinger uses panel-based firewall | Skip UFW; open port in panel.hostinger.com → VPS → Firewall instead |
| SSH from VPS to laptop times out (`Connection timed out`) | SSH server not running on laptop, or Windows firewall blocks port 22 | On WSL: `sudo service ssh start`; on Windows: enable OpenSSH Server + add firewall rule for port 22 TCP |
| Termius SSH ID auth fails on non-VPS host | Passkey public keys only installed on VPS, not the target host | Traditional key or password auth for hosts that don't have passkey in `authorized_keys` |
| SSH connection to VPS port 2222 times out from Termius | Hostinger HPanel firewall blocks port 2222 — iptables/v4 rules don't matter | Add TCP 2222 inbound rule in panel.hostinger.com → VPS → Firewall |
| WSL SSH server only listens on localhost | `ListenAddress 127.0.0.1` in sshd_config binds to loopback only | Change to `ListenAddress 0.0.0.0` then `sudo systemctl restart ssh` |
| SSH to laptop over Tailscale connection refused | Windows Firewall has no inbound rule for port 22 | Add Windows Firewall inbound rule: TCP port 22, Private network only (Tailscale adapter registers as Private). Name it `SSH Tailscale Inbound` |
| Windows Firewall rule for SSH asks "Allow the connection" vs "Allow if secure" | IPSec-only vs allow-all confusion | Choose "Allow the connection" — SSH is already encrypted, "Allow if secure" means IPSec-only which you're not using |
| Windows Firewall rule scope asks Domain/Private/Public | Over-exposure risk on public networks | Private only — Tailscale adapter registers as Private network. Do NOT check Public |
| Termius desktop times out but mobile connects fine | Stale host entry or SSH ID handshake slow on first connection | Add root password as fallback in host Credentials alongside SSH ID. If still fails, delete and recreate host entry. Use `Test-NetConnection <IP> -Port <port>` in PowerShell to confirm reachability |
| Hostinger HPanel firewall port 22 rule has Source `custom VPS_IP_REDACTED` | SSH only allows connections FROM the VPS to itself — nobody can SSH in | Edit rule: change Source from `custom VPS_IP_REDACTED` to `any`. This is a Hostinger default misconfiguration — the rule looks like it allows SSH but actually restricts it to the VPS's own IP, making it useless for external access. Also verify port 2222 has its own Allow rule (TCP, Source: any) since SSH is on 2222 not 22 |

## Examples

### Real Session Failure (Session ID: hermes-ssh-001)
User Ubuntu machine (`yoga@lenovo`) got `"Permission denied (publickey)"` after 20 days of working SSH.

**Diagnosis**:
```
# sshd -T showed PermitRootLogin no
# But /etc/ssh/sshd_config had PermitRootLogin yes
# /etc/ssh/sshd_config.d/hardening.conf had PermitRootLogin no (override!)
```

**Fix applied**:
```bash
sudo sed -i '/^PermitRootLogin/s/no/yes/' /etc/ssh/sshd_config.d/hardening.conf
sudo systemctl restart ssh
ssh root@VPS_IP_REDACTED  # Now works
```

### Public Wi-Fi Blocking
User in hotel got `Connection refused` to port 22, but `sshd` was running and listening.

**Resolution**: Used `tailscale up --ssh` then `tailscale ssh root@srv1617682` — bypassed port 22 blocking.

### Hostinger Blocks SSH Port 22 (Connection Timed Out)
User Ubuntu SSHing to port 22 got **no response at all** (timeout, not "connection refused"). `sshd` running and listening on VPS.

**Diagnosis**:
```
sudo ss -tlnp | grep :22        # Listening on 0.0.0.0:22
timeout 3 curl -s http://VPS_IP_REDACTED:22 2>&1  # No response = hotel drops packets
```

**Root Cause**: Hotel/public Wi-Fi silently drops port 22 packets. Not a VPS issue.

**Step 1 — Check which Port line exists**:
```bash
grep -n 'Port' /etc/ssh/sshd_config
# If "Port 22" (active/uncommented): sudo sed -i 's/^Port 22$/Port 2222/' /etc/ssh/sshd_config
# If "#Port 22" (commented):        sudo sed -i 's/^#Port 22$/Port 2222/' /etc/ssh/sshd_config
```

**Step 2 — Reload and restart (NO ufw on Hostinger)**:
```bash
# ⚠️ UFW is NOT installed on Hostinger VPS — skip it entirely
sudo systemctl daemon-reload      # CRITICAL for port change
sudo systemctl restart ssh.socket ssh

ss -tlnp | grep :2222           # Verify: LISTEN 0.0.0.0:2222 (port 22 should be gone)
```

**Step 3 — Open port in Hostinger panel (MANDATORY)**:
```
panel.hostinger.com → VPS → Firewall → Add port 2222 TCP inbound
```
Without this, SSH will still be unreachable regardless of VPS config.

**Step 4 — Connect**:
```bash
ssh -p 2222 root@VPS_IP_REDACTED  # Connection established
```

### Termius Setup (SSH Client for Phone + Desktop)

Install Termius on **laptop and phone** (never the VPS). Termius is an SSH **client** — you install it where you sit, not where you're connecting to.

**Importing a pre-built SSH config:**
1. Create an SSH config file (standard `~/.ssh/config` format) with all Host entries
2. Upload to Google Drive or AirDrop to your phone
3. Termius Desktop: Settings → SSH → Import → select the file
4. Termius Mobile: syncs automatically if you have a Termius account, or import from file via share sheet

**SSH config template for VPS access (import as-is):**
```
Host vps
    HostName VPS_IP_REDACTED
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60

Host vps-tailnet
    HostName 100.78.50.1
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60

Host vps-dev
    HostName VPS_IP_REDACTED
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    LocalForward 8787 localhost:8787
    LocalForward 8642 localhost:8642
    LocalForward 3100 localhost:3100
    LocalForward 3001 localhost:3001
    ServerAliveInterval 60
```

**Key requirements for Termius:**
- You need the **private** SSH key on the device connecting FROM. Termius supports importing OpenSSH keys (Settings → Keys → Import)
- If no key pair exists yet for the client device, generate one in Termius, then `ssh-copy-id` the public key to the VPS
- Password auth is disabled on the VPS — key auth is mandatory

**Termius host dedup after config import:**
Importing an SSH config creates entries for ALL Host stanzas, producing duplicates. Recommended minimal host list:
- `vps` — direct connection (VPS_IP_REDACTED:2222, root, SSH ID auth)
- `vps-tailnet` — Tailscale fallback (100.78.50.1:2222, root, SSH ID auth)
Delete all duplicates: `srv1617682`, `hermes`, `hermes-tailnet`, `vps-webui`, `vps-dev`, and any `laptop`/`lenovo` duplicates.

**SSH ID first-connection workflow:**
1. Install Termius on device, log into account, set up SSH ID (Settings → SSH ID → create handle)
2. Run `curl -sL https://sshid.io/v1/install/<handle> | bash` on the VPS to install passkey public keys
3. In Termius, create/edit host: set Authentication to **SSH ID** (not Key, not Password), select `@<handle>`
4. First connection prompts "authenticity of host can't be established" — tap **Continue** to accept the host key
5. Biometric prompt appears — authenticate and you're in
6. If desktop Termius times out on first connection but mobile works, add root password as fallback in Credentials alongside SSH ID — it provides an alternate auth path during initial handshake

### SSH ID (Termius Passkey System)

**What it is**: Termius SSH ID (`sshid.io`) is a proprietary passkey system that replaces traditional SSH key management. Each device generates a **device-bound** Ed25519 key pair — the private key never leaves the device and **cannot be exported**. Only public keys sync to your Termius vault.

**How it works**:
1. Settings → SSH ID → create a unique handle (e.g., `@blake-bridgers`)
2. Termius generates device-bound passkeys on each device you set up
3. Run a single curl command on the VPS to install all your public keys at once:
   ```bash
   curl -sL https://sshid.io/v1/install/<your-handle> | bash
   ```
4. Connect from any authorized device — biometric unlock (Face ID / Touch ID) optional

**Advantages over traditional keys**:
- No private key files to manage, copy, or lose across devices
- One-command server authorization (curl + bash vs manual `authorized_keys` edits)
- Per-device revocation (log out a device, re-run curl, old key gone)
- Biometric unlock on phone/laptop

**Disadvantages**:
- Device-bound means **no backup** — wipe a device = lose that key forever (add new device + re-run curl)
- Lock-in to Termius — passkeys only work through the Termius client, not raw `ssh` CLI
- Requires Termius account (free tier works)

**Recommended setup for this VPS**:
- Use SSH ID as primary authentication (convenience + security)
- Keep one traditional Ed25519 key as emergency fallback (store private key in Termius Keychain as an imported key, not a passkey)
- This gives biometric daily use + a safety net if SSH ID has issues

**Pitfall — Termius SSH ID connection times out on VPS port 2222**:
Even when `ss -tlnp` confirms sshd listening on 0.0.0.0:2222 and iptables INPUT policy is ACCEPT, external connections from Termius will time out if the **Hostinger HPanel cloud firewall** doesn't have port 2222 open. UFW and iptables rules are irrelevant — Hostinger's external firewall sits above the VPS and silently drops packets. Fix: panel.hostinger.com → VPS → Firewall → Add TCP 2222 inbound rule.

**Pitfall — Hostinger HPanel firewall rule propagation delay**:
After adding a new firewall rule in HPanel, external connections may still time out for 2-3 minutes before the rule propagates. If `Test-NetConnection` from Windows PowerShell confirms the port is reachable but Termius still times out, wait before re-troubleshooting. Use `Test-NetConnection <IP> -Port <port>` on the laptop to confirm reachability from the client side.

**Pitfall — Termius desktop app SSH ID timeout (mobile works fine)**:
If Termius mobile connects instantly via SSH ID but Termius desktop times out on the same host, adding the root password to the host's Credentials section alongside SSH ID provides a fallback path during the initial SSH ID handshake. This is not a security compromise — password is fallback only, SSH ID (biometric) remains primary. Once the host key is trusted and the first connection succeeds, subsequent SSH ID connections work instantly. If desktop still fails after password fallback works, recreate the host entry from scratch — stale imported config can cause connection issues.

**Pitfall — Termius host cleanup after SSH config import**:
When importing an SSH config into Termius, it creates entries for ALL Host stanzas — including duplicates and useless entries (e.g., hosts pointing to `iphone`, duplicates like `hermes` = `vps`, `srv1617682` = `vps`). Clean up aggressively. Recommended minimal host list:
- `vps` — primary direct connection (VPS_IP_REDACTED:2222)
- `vps-tailnet` — Tailscale fallback (100.78.50.1:2222, for hotel/corporate networks that block direct SSH)
Delete all others (`hermes`, `srv1617682`, `hermes-tailnet`, `vps-webui`, and `laptop`/`lenovo` duplicates). Port forwards can be added to `vps` directly in Termius if needed later.

**Pitfall — SSH ID only works on hosts with your passkey in `authorized_keys`**:
SSH ID passkeys only authenticate TO servers that have your public key installed. Adding passkeys to the VPS via `curl -sL https://sshid.io/v1/install/<handle> | bash` does NOT make them work for connecting TO your laptop, desktop, or any other machine. For those, you still need:
1. An SSH server running on that machine (see below)
2. Your passkey public key added to that machine's `~/.ssh/authorized_keys`

**Pitfall — "Can't SSH to my laptop from VPS" (Connection Timed Out)**:
If `ssh yoga@100.66.73.41` times out from the VPS, the problem is almost always one of:
1. **SSH server not running on the laptop** — WSL users must `sudo service ssh start` (or `sudo apt install openssh-server` first). Windows users need OpenSSH Server enabled via Settings → Apps → Optional Features → OpenSSH Server, then `Start-Service sshd`.
2. **WSL SSH bound to localhost only** — WSL's `sshd_config` may have `ListenAddress 127.0.0.1`, which blocks Tailscale connections. Fix: change to `ListenAddress 0.0.0.0` and `sudo systemctl restart ssh`. Verify with `ss -tlnp | grep :22` — must show `0.0.0.0:22`, NOT `127.0.0.1:22`.
3. **Windows Firewall blocking port 22** — Add inbound rule for port 22 TCP, **Private network only** (Tailscale adapter registers as Private). Do NOT select Public — that exposes SSH on untrusted networks. Name it `SSH Tailscale Inbound`.
4. **Tailscale IP stale** — Run `tailscale status` on the laptop and confirm the IP matches what you're connecting to.

## Key Files
- `/etc/ssh/sshd_config.d/hardening.conf` — common override location for `PermitRootLogin`, `MaxAuthTries`, etc.
- `/root/.ssh/authorized_keys` — key validation source (VPS-side)
- `~/.ssh/id_ed25519.pub` — Ubuntu public key for fingerprint comparison
- `~/.ssh/config` — SSH alias configuration on Ubuntu (prevents needing `-p 2222` flag)

## References
- `references/ssh-port-22-blocking-diag.md` — Port 22 blocking diagnosis flowchart
- `references/ssh-key-setup-cheat-sheet.md` — Quick setup commands for Ubuntu → VPS SSH setup
- `templates/ssh-config` — Pre-built SSH config file with all VPS host entries (import into Termius)
## Remote Config Editing — Emergency Access (Hostinger Panel Terminal)

When SSH is completely down, use the Hostinger web panel terminal for emergency edits.

### Edit YAML config without SSH

```bash
python3 -c "
import yaml
p='/root/.hermes/config.yaml'
c=yaml.safe_load(open(p))
c['model']['default']='openrouter/owl-alpha'
c['model']['provider']='openrouter'
c['model']['base_url']='https://openrouter.ai/api/v1'
yaml.dump(c,open(p,'w'))
print('done')
"
```

**Pitfall:** `pip3 install pyyaml` may be needed. Avoid heredocs in web terminals — use Python one-liners.

### Fix PermitRootLogin Override

```bash
# Find and patch hardening override
grep -r "PermitRootLogin" /etc/ssh/sshd_config.d/
sudo sed -i 's/^PermitRootLogin no/PermitRootLogin yes/' /etc/ssh/sshd_config.d/hardening.conf
sudo systemctl restart ssh
```

**Verify:** `sudo sshd -T | grep permitrootlogin`

### Model Switching via Remote Config

Change default model when SSH is down:
1. Edit `~/.hermes/config.yaml` → update `model.default`, `model.provider`, `model.base_url`
2. Restart gateway: `systemctl --user restart hermes-gateway`
3. Existing sessions stay locked to their startup model — open a new DM/thread

### Service Restart Checklist

```bash
systemctl --user restart hermes-gateway
systemctl restart ssh
systemctl --user status hermes-gateway --no-pager -l 5
journalctl --user -u hermes-gateway --no-pager -n 30
```

## Consolidated Skills

This skill absorbs: `vps-ssh-recovery`, `vps-remote-config`.

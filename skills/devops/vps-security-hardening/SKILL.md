---
name: vps-security-hardening
description: Use when the user asks to harden, lock down, or security-audit a Linux VPS — port scanning, SSH hardening, fail2ban, auditd, AIDE, rkhunter, unattended-upgrades, UFW rules, and daily security cron jobs. Also triggers on "Fort Knox", "lock down the server", "security scan the VPS", "block that IP", or any comprehensive security posture request.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [security, vps, hardening, ssh, fail2ban, firewall, audit, devops]
    related_skills: [hermes-vps-health-check, workflow-security-audit, security-guard, incident-commander, skill-security-scan]
---

# VPS Security Hardening — Fort Knox Protocol

Complete Linux VPS security lockdown: discovery, defense installation, SSH hardening, firewall rules, intrusion detection, file integrity monitoring, auto-patching, and daily scanning.

## When to Use

- User says "harden the VPS", "Fort Knox", "lock down the server", "security audit"
- User asks to block attacking IPs
- User wants proactive scanning and intrusion detection
- User asks for "airtight security posture"
- After a security incident or brute force detection
- Before putting a new VPS into production

Do NOT use for:
- Routine health checks → use `hermes-vps-health-check`
- Skill-level security scanning → use `skill-security-scan`
- Cron/script workflow audits → use `workflow-security-audit`

## Execution Phases

### Phase 1 — Discovery & Audit

```bash
# Open ports and listening processes
ss -tlnp

# UFW status
ufw status verbose

# SSH config audit
grep -E '^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication|Port|ListenAddress)' /etc/ssh/sshd_config
grep -r "PasswordAuthentication" /etc/ssh/sshd_config.d/ 2>/dev/null

# Active brute force detection
grep "Failed password" /var/log/auth.log 2>/dev/null | awk '{print $11}' | sort | uniq -c | sort -rn | head -10

# Running services
systemctl list-units --type=service --state=running | grep -v "systemd\|dbus\|cron\|snap"

# Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# Disk and memory
df -h / && free -h

# World-writable files
find / -xdev -type f -perm -o+w 2>/dev/null | grep -v "/proc\|/sys\|/dev" | head -20

# SUID binaries
find / -xdev -type f -perm -4000 2>/dev/null | grep -v snap | head -30
```

### Phase 2 — Block Active Attackers

```bash
# Block each attacking IP
for ip in <IP1> <IP2> <IP3>; do ufw deny from "$ip"; done
```

Pitfall: `ufw deny` only blocks NEW connections. If an attacker already has an active session, kill it separately.

### Phase 3 — Install Defense Tools

```bash
# Fix dpkg if needed first
dpkg --configure -a 2>/dev/null

# Install all defense packages
apt-get install -y fail2ban unattended-upgrades rkhunter chkrootkit lynis auditd aide
```

Pitfall: `apt-get install` can time out on slow connections. Run in background with `background=true` and `notify_on_complete=true` for long package lists. Also check `dpkg --configure -a` first if dpkg was interrupted.

### Phase 4 — Configure fail2ban

```bash
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
maxretry = 3
bantime = 86400
findtime = 600
EOF
systemctl enable --now fail2ban
```

Verify: `fail2ban-client status sshd | grep -E "Banned|banned"`

### Phase 5 — Harden SSH

```bash
# Disable password auth — check config.d overrides too
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

# CRITICAL PITFALL: cloud-init may override. Check config.d:
grep -r "PasswordAuthentication" /etc/ssh/sshd_config.d/
# If 50-cloud-init.conf has "PasswordAuthentication yes", fix it:
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config.d/50-cloud-init.conf
```

**Consolidate into one drop-in file** — remove any competing files first:
```bash
# Check for duplicate hardening files
ls /etc/ssh/sshd_config.d/*hardening* /etc/ssh/sshd_config.d/99-hardening* 2>/dev/null
# If multiple exist, remove duplicates (dueling configs cause unpredictable behavior):
rm -f /etc/ssh/sshd_config.d/hardening.conf
```

Write a comprehensive single override:
```bash
cat > /etc/ssh/sshd_config.d/99-hardening.conf << 'EOF'
LoginGraceTime 30
MaxAuthTries 3
MaxSessions 3
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PermitTunnel no
UseDNS no
LogLevel VERBOSE
EOF
```

**Apply and verify:**
```bash
systemctl restart ssh
sshd -T | grep -iE "passwordauth|permitroot|logingracetime|maxauthtries|maxsessions|x11|agentforwarding|tcpforwarding|permittunnel|usedns"
```

Pitfall: The service may be named `ssh` or `sshd` depending on distro. Check: `systemctl list-units | grep ssh`. On Ubuntu 24.04 it's `ssh.service`, not `sshd.service`.

Pitfall: `sshd -T` shows the RUNNING config (after includes). If it still shows `passwordauthentication yes` after editing `sshd_config`, cloud-init's `50-cloud-init.conf` is overriding. Fix the cloud-init file directly.

Pitfall: **Duplicate drop-in files cause silent conflicts.** If both `hardening.conf` and `99-hardening.conf` exist with different values for the same directives (e.g., `LoginGraceTime 30` vs `LoginGraceTime 60`), the lexicographically LAST file wins — but this is fragile. Always consolidate into one file and remove duplicates. Check with `ls /etc/ssh/sshd_config.d/` before writing.

### Phase 6 — Configure unattended-upgrades

```bash
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:00";
EOF
```

### Phase 7 — Enable System Audit (auditd)

```bash
systemctl enable auditd
systemctl restart auditd
auditctl -s  # verify: enabled=1, no errors
```

### Phase 8 — Initialize AIDE (File Integrity)

AIDE hashes the entire filesystem — this is slow (minutes on large disks). Run in background:

```bash
# Background the init
aideinit -y -f 2>&1 | tail -3
# After completion:
cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
systemctl enable dailyaidecheck.timer
systemctl start dailyaidecheck.timer
```

### Phase 9 — Install Daily Security Cron

```bash
cat > /etc/cron.d/hermes-security << 'EOF'
SHELL=/bin/bash
0 6 * * * root ss -tlnp > /var/log/hermes-port-scan.log 2>&1; rkhunter --check --skip-keypress --cronjob 2>&1 | grep -i warning >> /var/log/hermes-security.log; find / -xdev -type f -perm -4000 2>/dev/null | grep -v snap > /var/log/hermes-suid.log; df -h / > /var/log/hermes-disk.log; grep "Failed password" /var/log/auth.log 2>/dev/null | tail -20 > /var/log/hermes-auth-failures.log; echo "$(date): Daily security scan complete" >> /var/log/hermes-security.log
EOF
chmod 644 /etc/cron.d/hermes-security
```

### Phase 10 — Malware Scan

```bash
# Check for crypto miners / reverse shells
ps aux | grep -iE "crypto|miner|xmrig|stratum|botnet|backdoor|reverse.shell"

# Check for web shells
find /var/www /root -name "*.php" -o -name "*.jsp" -o -name "*.war" 2>/dev/null

# Run rkhunter (skip keypress for non-interactive)
rkhunter --check --skip-keypress --cronjob 2>&1 | grep -i warning

# Run lynis quick audit
lynis audit system --quick 2>&1 | tail -20
```

### Phase 11 — Hermes-Specific Hardening

```bash
# Lock down .env
chmod 600 ~/.hermes/.env

# Check gateway bind — if 0.0.0.0, ensure UFW blocks the port externally
grep -E 'host:|port:' ~/.hermes/config.yaml

# Scan skills for dangerous patterns
find ~/.hermes/skills -name "SKILL.md" -exec grep -l 'curl.*\|.*sh\|rm -rf\|eval' {} \;
```

### Phase 12 — Disk Cleanup (if needed)

```bash
# Docker cleanup
docker system prune -a -f

# pip cache
rm -rf /root/.cache/pip/*

# Check largest dirs
du -sh /root/.hermes /root/.cache /var/log /var/lib/docker /tmp 2>/dev/null | sort -rh
```

## Phase 13 — Firewall Sync & Final Audit

**CRITICAL PITFALL — Hostinger HPanel cloud firewall MUST match UFW:** UFW is just the VPS-level firewall. Hostinger's cloud firewall (HPanel) is a separate filter in front of the VPS. **Both must allow the port for external access.**

### UFW Configuration

```bash
# Reset and configure UFW basics
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Public-facing ports only
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (nginx)
sudo ufw allow 443/tcp   # HTTPS (if using Let's Encrypt)
sudo ufw reload
sudo ufw enable
```

### Hostinger HPanel Cloud Firewall — MANDATORY

Go to `https://panel.hostinger.com` → **VPS → Firewall** (left menu) → **Add Rule**:

| Port | Protocol | Action | Description |
|------|----------|--------|-------------|
| 2222 | TCP | Allow | SSH (moved from 22 — Hostinger default blocks 22) |
| 80 | TCP | Allow | HTTP (nginx) |
| 443 | TCP | Allow | HTTPS (if using TLS) |
| 51820 | UDP | Allow (optional) | WireGuard if used |

**Delete or block rules for internal services:**
- `8642` — Hermes gateway (should be `127.0.0.1` only)
- `8765` — FastAPI scraper (should be `127.0.0.1`)
- `3100` — Hermes workspace (should be `127.0.0.1`)
- `3001/3002` — Next.js apps (should be `127.0.0.1`)
- `8000` — Internal proxies
- `11434` — Ollama (should be `127.0.0.1` or localhost-only)

### Verification Checklist

After binding internal services to `127.0.0.1`, verify both firewalls:

```bash
# Confirm only SSH and nginx are public
sudo ss -tulpn | grep -E ':22|:80|:443'

# Confirm all internal services bound to 127.0.0.1
sudo ss -tulpn | grep -E ':8642|:8765|:3100|:3001|:3002|:11434'
```

Expected result:
- **Public (external accessible)**: `22/tcp` (SSH), `80/tcp` (nginx)
- **Locked (internal only)**: `8642`, `8765`, `3100`, `3001`, `3002`, `11434` — all bound to `127.0.0.1`

### Common Firewall Mistakes

1. **Port allowed in UFW but blocked by Hostinger HPanel**: UFW alone is insufficient. HPanel cloud firewall (panel.hostinger.com → VPS → Firewall) must also allow the port for external traffic to reach the VPS.
2. **Services bound to `0.0.0.0` instead of `127.0.0.1`**: Next.js/Vite devservers default to all interfaces. Always explicitly set `HOST=127.0.0.1` or `HOSTNAME=127.0.0.1` and verify with `ss -tulpn`.
## Final Verification Checklist

- [ ] `passwordauthentication no` in `sshd -T` output
- [ ] fail2ban active with sshd jail
- [ ] UFW active with default deny incoming
- [ ] Attacking IPs blocked in UFW
- [ ] unattended-upgrades configured
- [ ] auditd enabled and running
- [ ] AIDE initialized with daily timer
- [ ] Daily security cron installed
- [ ] No crypto miners or web shells found
- [ ] Hermes .env at 600 permissions
- [ ] Disk below 85%

## Common Pitfalls

1. **cloud-init overrides SSH config**: `50-cloud-init.conf` may set `PasswordAuthentication yes`. Always check `/etc/ssh/sshd_config.d/` and fix the cloud-init file, not just `sshd_config`.

2. **Service name mismatch**: Ubuntu 24.04 uses `ssh.service`, not `sshd.service`. Use `systemctl restart ssh`.

3. **fail2ban socket disappears during package install**: If `fail2ban-client status` fails with socket error after installing packages, `systemctl restart fail2ban` fixes it.

4. **apt-get timeouts**: On slow connections, run `apt-get install` in background with `notify_on_complete=true`.

5. **dpkg interrupted**: If apt-get fails with "dpkg was interrupted", run `dpkg --configure -a` first.

6. **UFW only blocks NEW connections**: Existing attacker sessions persist. Kill active sessions for critical blocks.

7. **Internal services exposed publicly**: Processes like FastAPI/Next.js bind `0.0.0.0` by default. Always set `HOST=127.0.0.1` explicitly and verify with `ss -tlnp` after hardening.

8. **Postfix exposure**: Postfix defaults to all interfaces. Lock to loopback with `postconf -e "inet_interfaces = loopback-only"`.

9. **`service` vs `systemctl` naming**: On Ubuntu 24.04, SSH is `ssh.service` not `sshd.service`. Check with `systemctl list-units | grep ssh`.

10. **VPS service classification workflow (ss -tulpn audit)**
    - **Essential**: `sshd(22)`, `hermes-gateway(8642)`, `nginx(80)`, `vehicle-analyzer(8765)`, `ollama(11434)` if used
    - **Liabilities**: `postfix(25)`, `fail2ban`, `systemd-resolved` DNS stub (if not needed), Docker co-tenant UDP 51820 (if not using WireGuard)
    - **Co-tenants**: Honcho backend (3000, 6379, 5432), WireGuard (51820/udp)
    - **Investigate**: Next.js devserver (3001), `fb-scraper.service` (FastAPI scraper, auto-restart, Groq vision, 26/36 fields from FB Marketplace)

11. **Duplicate SSH drop-in configs**: If `hardening.conf` and `99-hardening.conf` both exist with conflicting values (e.g., different `LoginGraceTime` or `MaxSessions`), the lexicographically LAST file wins — fragile and unpredictable. Always consolidate into one file (`99-hardening.conf`) and remove duplicates. Check with `ls /etc/ssh/sshd_config.d/*hardening*`.

12. **Dead HPanel firewall rules — cross-reference audit**: HPanel cloud firewall rules persist even after services are decommissioned. A rule allowing a port with nothing listening behind it is a dormant security hole — if a process accidentally binds that port, it's immediately public. Audit by cross-referencing three data sources:

```bash
# A. HPanel rules (from panel.hostinger.com → VPS → Firewall)
# B. What's actually listening
ss -tlnp | awk '{print $4}' | grep -oP ':\K\d+'
# C. Docker container port mappings
docker ps --format '{{.Ports}}' | grep -oP ':\K\d+(?=->)'
```

Any port in HPanel but NOT in `ss -tlnp` or `docker ps` is a dead rule — remove it from HPanel. Common dead-rule candidates: old SSH port (22) when SSH moved to 2222, decommissioned dev servers (3100, 8080), abandoned Docker projects (45160).

**Triangulation command — one-line port audit**:
```bash
echo "=== HPanel rules (from memory/listing above) ===" && \
echo "=== ss listening ===" && ss -tlnp | grep -oP ':\K\d+(?=\s)' | sort -n | uniq && \
echo "=== Docker mapped ports ===" && docker ps --format '{{.Ports}}' 2>/dev/null | grep -oP ':\K\d+(?=->)' | sort -n | uniq
```

Cross-reference manually against the HPanel rule list. Flag anything in HPanel but absent from both ss and Docker.

See `references/hpanel-firewall-triangulation.md` for the full operational recipe with one-liner commands and common port-to-service mappings on this VPS.

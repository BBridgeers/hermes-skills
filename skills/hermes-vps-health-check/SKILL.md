---
name: hermes-vps-health-check
description: Comprehensive session-start diagnostic and maintenance workflow — host identification, service health, cron status, security sweep (UFW, fail2ban, SSH keys, auth.log), system health (disk, memory, swap, network), backup integrity, kernel updates, hermes config syntax, automated updates, and remediation recommendations. Logs to ~/.hermes/session-check.log.
version: 2.0.0
tags: [devops, health-check, security, hermes, vps, maintenance, monitoring]
---

# Hermes VPS Health Check

A comprehensive diagnostic and maintenance workflow that runs automatically at CLI session start.
Covers: environment (local/VPS), service health, cron status, security posture, disk/memory/network health, backup integrity, kernel/updates, hermes config syntax, and automated remediation.

## Purpose

Run this upon every new CLI session to ensure your VPS ( srv1617682 ) is healthy,
secure, and up-to-date.

## When to Run

Triggered automatically via `~/.bashrc` (shell sessions) or `~/.hermes/workspace-startup.sh` (workspace sessions) on VPS (srv1617682).

**Agent Proactive Execution**: Hermes Agent should proactively run this health check during CLI sessions when:
- The user mentions system status, performance, or connectivity issues
- The session involves infrastructure-related tasks
- The user asks general questions about the VPS environment
- Any indication of potential system issues arises

Proactive health checks help catch issues early and demonstrate active system monitoring behavior.

### Cooldown Logic

The health check runs with a **6-hour cooldown** to prevent redundant execution during session batching:

- **First session of the day**: Runs unconditionally
- **Subsequent sessions within 6 hours**: Skipped with message `(last run: Xh ago)`
- **6+ hours since last run**: Runs again

Cooldown is enforced by checking `~/.hermes/session-check.log` timestamp via `stat -c %Y`.

**Automatic triggers:**
- Shell sessions: `/root/.bashrc` checks hostname and cooldown
- Workspace sessions: `terminal.shell_init_files: /root/.hermes/workspace-startup.sh`

**Manual override:** Run `hermes skill run hermes-vps-health-check` anytime to force execution regardless of cooldown.

## Steps

1. **Identify Host Environment**
   - `hostname` → distinguish local (yoga@lenovo/WSL) vs VPS (srv1617682)
   - Print current working directory, user, uptime
   - Report kernel version, distro, and hostname

2. **Hermes Service Health Check**
   - `hermes-gateway` listening on 8642 (`ss -tlnp | grep 8642`)
   - `hermes-workspace` listening on 3200 (`ss -tlnp | grep 3200`)
   - `hermes-dashboard` process (`ps aux \| grep -E 'dashboard\|6382'`)
   - `tailscale` status (non-empty output)
   - MCP bridge status (`/opt/hermes-mcp-bridge.sh` readable)

3. **Cron Job Status**
   - `hermes cronjob list` — verify scheduled jobs exist and are enabled
   - Summarize active jobs and next run times
   - Parse `~/.hermes/cron/output/heartbeats/` for recent failures
   - Check `/var/log/syslog` for cron errors in last 24h
   - **rclone-upload-gdrive**: if present and last_status=error, disk may fill. See `torrent-cloud-pipeline` skill.

4. **UFW Firewall Status** *(UFW is secondary — HPanel cloud firewall is the actual gatekeeper)*
   - `ufw status numbered` — list rules
   - Confirm expected public-facing ports: 80, 443, 2222 (SSH)
   - Check internal services bound correctly (127.0.0.1 only): 8642, 3200, 3001, 3002, 11434
   - Alert if any unexpected ports in LISTEN state
   - **Dead HPanel rules**: cross-reference HPanel firewall rules (panel.hostinger.com → VPS → Firewall) against `ss -tlnp` and `docker ps`. Any port in HPanel with nothing listening is a dormant hole — flag for removal.

5. **fail2ban Status**
   - `systemctl is-active fail2ban` — active/inactive/failed
   - ` journalctl -u fail2ban --no-pager -n 5` — recent logs
   - Alert if fail2ban not running

6. **SSH Security Audit**
   - List all public keys in `~/.ssh/authorized_keys`
   - Check `~/.ssh/id_*.pub` inventory
   - `/etc/ssh/sshd_config` security check: PermitRootLogin, PasswordAuthentication, Protocol
   - Alert if insecure settings detected

7. **Auth Log Review**
   - `tail -50 /var/log/auth.log` — recent login attempts
   - Detect brute force patterns (SSH brute force by IP)
   - Alert on repeated failures or unauthorized logins

8. **Disk Space Health**
   - `df -h` — all filesystems
   - **Torrent downloads**: `du -sh /root/torrent/downloads/` — if > 10GB, check rclone-upload cron (see `torrent-cloud-pipeline` skill)
   - `/tmp` cleanup — `find /tmp -type f -atime +1 -delete` (safe)
   - Inode check — `df -i`
   - Log rotation check — `/var/log` size overview
   - Alert if any filesystem > 85% full or inodes > 90%

9. **Memory & Swap Health**
   - `free -m` — RAM and swap
   - Swap usage ratio — alert if > 50%
   - `swapon --show` — active swap devices
   - OOM risk indicator based on current usage

10. **Network Connectivity Tests**
    - Outbound: `curl -sf --connect-timeout 5 https://api.deepseek.com`
    - Outbound: `curl -sf --connect-timeout 5 https://github.com`
    - Outbound: `curl -sf --connect-timeout 5 https://tailscale.com`
    - DNS resolution (`nslookup github.com` or `dig +short github.com`)
    - Alert on any failing connection

11. **Tailscale Health**
    - `tailscale status` — connection status, exit node
    - `tailscale ping 100.64.0.1` — self-ping latency
    - Alert on offline status or high latency (> 200ms)

12. **Kernel & Update Status**
    - `uname -r` vs `ls /boot/vmlinuz*` — detect pending reboot
    - `apt update` (skip interactive) — available upgrades
    - `unattended-upgrades` status — enabled/disabled
    - Security-upgrade packages summary
    - Alert if kernel mismatch or pending reboot

13. **Hermes Configuration & State**
    - `config.yaml` syntax validation (`hermes config validate` or `python3 -c 'import yaml;yaml.safe_load(...)'`)
    - `~/.hermes/env.sh` parse — detect missing required vars
    - `~/.hermes/skills/` count vs expected based on taps
    - Skill drift check — `find ~/.hermes/skills -type d -name .git -prune -o -type f -print | wc -l`
    - Alert on syntax errors or missing config

14. **Backup Integrity Check**
    - Last backup timestamp — `stat ~/.hermes/hermes-backup/SKILL.md 2>/dev/null || echo "No local backup"`
    - GitHub backup age — `gh repo view BBridgeers/hermes-backup --field pushed_at` if gh CLI available
    - Backup size — `du -sh ~/.hermes/hermes-backup 2>/dev/null || echo "N/A"`
    - Alert if backup older than 7 days or missing

15. **RKHunter/ClamAV Security Scan**
    - Check if installed — `which rkhunter` or `which clamscan`
    - Run `rkhunter --update` and `rkhunter --check --nocolors --quiet`
    - Run `clamscan -i /tmp /root 2>/dev/null` if no rkhunter
    - Log scan results to `~/.hermes/session-check.log`

16. **Lynis Security Audit (if available)**
    - Run `lynis audit system --quiet` if installed
    - Summary of warnings and suggestions
    - Log findings to `~/.hermes/session-check.log`

17. **Time Sync Check**
    - `timedatectl status` — NTP active, timezone
    - Chrony/NTPd status — `systemctl is-active chronyd || systemctl is-active ntpd`
    - Alert if time drift > 5 seconds or NTP inactive

18. **Docker/Container Status (if Docker installed)**
    - `docker ps -a` — container count and status
    - `docker info` — daemon health
    - Auto-remove stopped containers older than 7 days (`docker container prune -f --filter "until=168h"`)
    - Alert if Docker daemon not running

19. **Summary Report**
    - Green/Red checkmarks per section (✅ / ❌)
    - Yellow warnings for non-critical items
    - Summary counts: Total checks, Pass, Fail, Warn
    - Remediation actions logged to `~/.hermes/session-check.log`
    - Prompt user to review failed items

## Remediation Actions

- **Disk full**: Prompt `df -h`, suggest cleanup (`apt clean`, `/tmp` cleanup, log rotation)
- **Service down**: Restart with `hermes gateway install` or `systemctl restart hermes-gateway`
- **UFW issues**: Prompt `ufw status`, suggest port removal for unexpected services
- **fail2ban down**: Prompt `sudo systemctl start fail2ban && sudo systemctl enable fail2ban`
- **Pending reboot**: Prompt `sudo reboot` after warning
- **Security issues**: Provide remediation commands per finding

## Fort Knox Hardening Protocol

When the user requests a comprehensive security lockdown, execute these steps beyond the standard health check. These survive reboots and harden against brute force, rootkits, and unauthorized access.

### SSH Hardening

```bash
# Consolidated hardening config — write a single comprehensive file.
# Remove any older duplicate files first (e.g. hardening.conf) to avoid
# config conflicts where different files set conflicting values for the
# same directive (e.g. LoginGraceTime 30 vs 60, MaxSessions 3 vs 5).
rm -f /etc/ssh/sshd_config.d/hardening.conf

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

# Cloud-init drop-ins may also set PasswordAuthentication — verify all of them
grep -r "PasswordAuthentication" /etc/ssh/sshd_config.d/

# Restart SSH (Ubuntu 24.04: service is 'ssh', not 'sshd')
systemctl restart ssh

# VERIFY
sshd -T | grep -E "passwordauth|permitroot|logingracetime|maxauthtries|maxsessions|x11|agentforwarding|tcpforwarding"
```

### fail2ban Aggressive Config

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

### Install Defense Packages

```bash
apt-get install -y unattended-upgrades rkhunter chkrootkit lynis auditd aide
dpkg-reconfigure -plow unattended-upgrades
systemctl enable --now auditd
aideinit
```

### Active Brute Force Response

```bash
# Identify top attackers: grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head -10
# Block each: for ip in <IP1> <IP2>; do ufw deny from "$ip"; done
```

### Verification Commands

```bash
sshd -T | grep -E "passwordauth|logingracetime|maxauthtries|maxsessions|permitroot"
fail2ban-client status sshd | grep -E "Banned|banned"
ufw status | grep DENY
ss -tlnp  # audit all listening ports
```

## Troubleshooting

- If any service is missing → restart with `hermes gateway install` or `python3 -m hermes_cli.main workspace --host 0.0.0.0`
- If UFW shows unexpected ports → investigate with `sudo lsof -i :PORT`
- If rkhunter/clamav missing → install with `apt install rkhunter clamav -y`
- If GitHub backup inaccessible → verify GITHUB_TOKEN in `~/.hermes/.env`

### SSH Access Failures

SSH is configured on **port 2222** (not default 22) with **password auth disabled**. This trips two common failure modes:

1. **Wrong port**: `ssh root@VPS_IP_REDACTED` hits port 22, which has no listener. Use `ssh -p 2222 root@VPS_IP_REDACTED` or add an SSH config entry:
   ```
   Host vps
       HostName VPS_IP_REDACTED
       Port 2222
       User root
       IdentityFile ~/.ssh/id_ed25519
   ```
2. **Hostinger HPanel firewall**: UFW may allow everything, but the Hostinger VPS firewall (panel.hostinger.com → VPS → Firewall) sits in front and is the actual gatekeeper. If port 2222 isn't opened in HPanel, traffic is dropped before it reaches the VPS. **UFW changes alone are insufficient.**
3. **Password auth disabled**: All drop-in configs in `/etc/ssh/sshd_config.d/` set `PasswordAuthentication no`. SSH key auth is required. Copy your public key to `~/.ssh/authorized_keys` on the VPS before disabling password auth.

### Termius Setup (SSH Client for Phone + Desktop)

Install Termius on **laptop and phone** (never the VPS). It's an SSH **client** — install where you sit, not where you connect to.

**Importing a pre-built SSH config:**
1. Create or obtain an SSH config file (standard `Host` block format)
2. Upload to Google Drive or AirDrop to phone
3. Termius Desktop: Settings → SSH → Import → select the file
4. Termius Mobile: syncs via Termius account, or import from file via share sheet
5. **Private key required**: import `~/.ssh/id_ed25519` (private key) into Termius Settings → Keys

Pre-built config template lives at `devops/vps-ssh-troubleshooting/templates/ssh-config`.

### Git Merge Conflicts in Source

If the gateway crashes on startup with `SyntaxError: expected 'except' or 'finally' block` pointing at `<<<<<<< Updated upstream`, a git merge/stash left conflict markers in a Python source file. The gateway imports all platform adapters at startup; even one unresolved conflict kills the process.

**Quick diagnostic:**
```bash
# Find all conflict markers in gateway source — run this FIRST on any gateway crash
grep -rn '<<<<<<\|>>>>>>\|=======' ~/.hermes/hermes-agent/gateway/platforms/
```

**Fix pattern:** Open the file, remove markers, keep the correct branch (usually "stashed changes" since that's the user's work), then:
```bash
systemctl --user restart hermes-gateway
sleep 3
journalctl --user -u hermes-gateway --no-pager -n 20 | grep -iE 'error|connect|slack'
```

**Key insight from session:** The `api_server.py` merge conflict (line 4112) had the "Updated upstream" branch containing just `assert self._app is not None` while the "Stashed changes" branch had meaningful code (`self._app["api_server_adapter"] = self` etc.). Always keep the substantive branch, not the trivial assertion. This pattern is common — git conflict markers silently break Python imports.

### Kanban DB Corruption

If gateway logs show `kanban dispatcher: board default database /root/.hermes/kanban.db is not a valid SQLite database`, the kanban DB is corrupted. This is **non-critical** — the gateway stays running, just kanban dispatching is paused.

```bash
mv ~/.hermes/kanban.db ~/.hermes/kanban.db.bak
hermes kanban init
# Gateway auto-detects the fresh DB on next quarantine timer (~5 min) or restart
```

### Gateway Crash-Loop Diagnosis

When `hermes-gateway` shows `activating (auto-restart)` in systemctl status, check logs immediately:

```bash
journalctl --user -u hermes-gateway --no-pager -n 200 | grep -A5 'Traceback'
```

Common crash causes in priority order:
1. **Git merge conflict markers** in Python source — `SyntaxError` on import (most common after git operations)
- **Missing Python dependency** — ModuleNotFoundError after an update
3. **Invalid config.yaml** — YAML parse error on startup
4. **Port conflict** — another process on :8642
5. **Stale venv symlink** — `venv/bin/python` points to a deleted uv-managed Python (e.g. `~/.local/share/uv/python/cpython-3.11...` that no longer exists). Symptom: `code=exited, status=203/EXEC`. Fix by updating the systemd service `ExecStart` to point at the working install (`/usr/local/lib/hermes-agent/venv/bin/python`). This happens after uv upgrades or reinstalls that remove old Python builds.

After fixing, restart and verify Slack connected:
```bash
systemctl --user restart hermes-gateway
sleep 5
tail -5 ~/.hermes/logs/gateway.log | grep -E 'slack|connected'
```

### Vite Dev Server Zombie on Port 3100

The Vite dev server (`vite dev --port 3100 --host 0.0.0.0`) from `/root/hermes-workspace` was decommissioned. Port 3100 should be DEAD. If it appears, it's a rogue process — kill it immediately and audit for resurrection vectors:

```bash
# Kill the zombie
ss -tlnp | grep 3100 && kill $(ss -tlnp | grep ':3100' | grep -oP 'pid=\K\d+')

# Verify dead
ss -tlnp | grep 3100 || echo "Port 3100: CLEAR"

# Check no resurrection vectors exist
systemctl list-units --type=service --state=running | grep -iE 'vite|3100'
crontab -l 2>/dev/null | grep -iE 'vite|3100'
ps aux | grep -iE 'vite' | grep -v grep
```

The production workspace server is on **port 3200** (`node server-entry.js`, pid 2571919, localhost-only). This is the canonical workspace instance. Port 3100 is a dev artifact and must not run.

## Disk Cleanup

See `references/vps-disk-REDACTED.md` for the full cleanup playbook — audit commands, ordered targets, expected savings, and what NOT to delete. Ran 2026-06-01 and freed 22GB (87% → 65%).

Quick one-liner for disk audit:
```bash
du -sh /root/.hermes /root/.cache /root/.local /root/*/ 2>/dev/null | sort -rh | head -20 && docker system df
```

## References

- **Disk Cleanup Playbook**: `references/vps-disk-REDACTED.md` — full VPS disk audit and cleanup runbook
- UFW guide: `sudo ufw status verbose`
- fail2ban: `sudo journalctl -u fail2ban -f`
- Tailscale: `tailscale status`, `tailscale ping`
- Disk health: `smartctl -a /dev/sda` (if installed)
- Security: `lynis audit system`, `rkhunter --check`

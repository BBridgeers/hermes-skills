# Local Machine (WSL/Windows) Fort Knox Prompt

When the user asks for a Fort Knox protocol on their local Hermes instance (Windows/WSL, not VPS), give them this self-contained prompt. It differs from the VPS hardening because WSL has a Windows boundary, different networking, and no cloud-init.

Paste this into the local Hermes CLI:

```
You are executing a comprehensive security hardening protocol on Blake's local machine (yoga@lenovo, Windows/WSL). Complete every step.

## PHASE 1 — DISCOVERY & AUDIT
- Port scan: ss -tlnp
- Windows firewall: netsh advfirewall show allprofiles (PowerShell)
- WSL LAN exposure: ip addr show
- Services: systemctl list-units --type=service --state=running
- SSH config: grep -r 'PasswordAuthentication\|PermitRootLogin' /etc/ssh/
- Exposed secrets: grep -r 'API_KEY\|TOKEN\|SECRET' ~/.bash_history ~/.env* 2>/dev/null
- World-writable: find /home /root -type f -perm -o+w 2>/dev/null
- SUID: find / -type f -perm -4000 2>/dev/null | grep -v snap

## PHASE 2 — INSTALL DEFENSES
sudo apt-get install -y fail2ban unattended-upgrades rkhunter chkrootkit lynis auditd aide
sudo tee /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
maxretry = 3
bantime = 86400
findtime = 600
EOF
sudo systemctl enable --now fail2ban auditd

## PHASE 3 — HARDEN SSH
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*ListenAddress.*/ListenAddress 127.0.0.1/' /etc/ssh/sshd_config
echo "LoginGraceTime 30" | sudo tee -a /etc/ssh/sshd_config
echo "MaxAuthTries 3" | sudo tee -a /etc/ssh/sshd_config
sudo systemctl restart ssh

## PHASE 4 — WINDOWS BOUNDARY (PowerShell Admin)
New-NetFirewallRule -DisplayName "Block WSL Inbound" -Direction Inbound -InterfaceAlias "vEthernet (WSL)" -Action Block
# Check .wslconfig — switch to NAT mode if using mirrored networking

## PHASE 5 — HERMES HARDENING
chmod 600 ~/.hermes/.env
grep 'host:' ~/.hermes/config.yaml
# If gateway host is 0.0.0.0, change to 127.0.0.1

## PHASE 6 — DAILY SCAN CRON
Create cron at 6AM checking: ports, auth failures, SUID, disk, suspicious processes

## PHASE 7 — VERIFY
sudo lynis audit system --quick
sudo rkhunter --check --skip-keypress
sudo fail2ban-client status sshd
sudo sshd -T | grep -E 'passwordauth|permitroot|listenaddress'

Produce ~/security-audit/FORT-KNOX-COMPLETE.md with every finding and Security Posture Score (A+ to F).
```

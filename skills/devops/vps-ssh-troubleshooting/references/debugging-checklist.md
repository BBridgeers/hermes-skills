# SSH Troubleshooting Checklist
Session: hermes-ssh-001

## Commands Tested
```bash
# Verify sshd is listening
ss -tlnp | grep :22
sudo ss -tlnp | head -10

# Check sshd status
sudo systemctl status ssh --no-pager -l 3
sudo journalctl -u ssh -n 20 --no-pager

# Check running sshd config (not file!)
sudo sshd -T 2>/dev/null | grep permitrootlogin
sudo sshd -T 2>/dev/null | grep passwordauthentication

# Check file configs (systemd includes override)
grep -n "PermitRootLogin" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null

# Validate user key fingerprint matches authorized_keys
ssh-keygen -l -f ~/.ssh/id_ed25519.pub
ssh-keygen -l -f /root/.ssh/authorized_keys | grep yoga
```

## Real Session Output
```
# Ubuntu key fingerprint
ssh-keygen -l -f ~/.ssh/id_ed25519.pub
# 256 SHA256:WuNg7dS+Ps9z529XmNPjcUJO7avixP2TqUbOg6eZBxw yoga@lenovo (ED25519)

# VPS authorized_keys had multiple yoga@lenovo keys
ssh-keygen -l -f /root/.ssh/authorized_keys
# 256 SHA256:WuNg7dS+Ps9z529XmNPjcUJO7avixP2TqUbOg6eZBxw yoga@lenovo (ED25519) ← MATCH
# 4096 SHA256:fMpti90ZsC/9Xb7lmcx/BJnEIOTJMynhmOOTzLYdZpo yoga@lenovo (RSA)
# 4096 SHA256:JW3yx4Z/MkAMgCxRkUAnmCA/BIi/58ba1LZQMsarl78 root@srv1617682 (RSA)
# 256 SHA256:JBgiHaDe+qjD34DuNqYxM1Ls4Ujach+R6O8dG4toUcc hermes@srv1617682 (ED25519)
# 256 SHA256:62aX9B+0w621IIYcM0RmReocvTj894XS+Ppuy0NgKu8 yoga@lenovo (ED25519)

# But sshd -T showed PermitRootLogin no
sudo sshd -T | grep permitrootlogin
# permitrootlogin no ← OVERRIDDEN by /etc/ssh/sshd_config.d/hardening.conf

# hardening.conf override found
cat /etc/ssh/sshd_config.d/hardening.conf
# PermitRootLogin no
# PasswordAuthentication no
# ...
```

## Final Fix
```bash
sudo sed -i '/^PermitRootLogin/s/no/yes/' /etc/ssh/sshd_config.d/hardening.conf
sudo systemctl restart ssh
sudo journalctl -u ssh -n 3 --no-pager | grep -E "sshd|Started"
# Server listening on 0.0.0.0 port 22
# Started ssh.service - OpenBSD Secure Shell server

# Test SSH
ssh root@VPS_IP_REDACTED  # Connection established, key accepted
```

## Notes
- Hostinger VPS has `sshd_config.d/` override directory — always check there
- `PermitRootLogin no` in any included file blocks ALL root login, even with correct key

### Hostinger HPanel Firewall Default SSH Rule Misconfiguration

The Hostinger VPS firewall template creates an SSH (port 22) rule with **Source set to `custom VPS_IP_REDACTED`** (the VPS's own IP). This means the rule only allows SSH connections FROM the VPS TO itself — nobody external can reach SSH. The rule looks correct at a glance ("SSH" is "Accept") but silently blocks all external access.

**Fix**: Edit the port 22 rule → change Source from `custom VPS_IP_REDACTED` to `any`. Then add a separate rule for port 2222 (TCP, Source: any) since SSH is running on 2222.

**Also critical**: When adding the port 2222 rule, the Hostinger panel may take 2-3 minutes to propagate. Don't troubleshoot further until you've waited — `Test-NetConnection` from the client side can confirm reachability while Termius is still timing out during propagation.
- Tailscale (`100.78.50.1`) does NOTListen on port 22 — use `tailscale ssh`, not `ssh` directly
- Hotel/corporate Wi-Fi often blocks SSH outbound — use Tailscale if port 22 blocked
# VPS SSH Hardening — Quick Reference

Common pitfalls and fixes from a 2026-05-22 VPS security audit.

## The cloud-init.conf Trap

On cloud-hosted VPS instances (Hostinger, DigitalOcean, AWS), `/etc/ssh/sshd_config.d/50-cloud-init.conf` often overrides your main `sshd_config`. Even after setting `PasswordAuthentication no` in `/etc/ssh/sshd_config`, the running config may still show `passwordauthentication yes` because the cloud-init drop-in loads and overrides.

**Verify the running config, not the file:**
```bash
sshd -T 2>/dev/null | grep passwordauthentication
```

**Fix the right file:**
```bash
# Check all drop-in files for overrides
grep -r "PasswordAuthentication" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/

# If 50-cloud-init.conf has "yes", fix it there
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config.d/50-cloud-init.conf
systemctl restart ssh
```

## Service Name: ssh, not sshd

On Debian/Ubuntu: `systemctl restart ssh` (not `sshd`).

## fail2ban Quick Setup

```bash
apt-get install -y fail2ban
systemctl enable --now fail2ban

# Verify
fail2ban-client status
fail2ban-client status sshd
```

Default config bans after 5 failures for 10 minutes. For stricter:
```ini
# /etc/fail2ban/jail.local
[sshd]
enabled = true
maxretry = 3
bantime = 3600
```

## Blocking Active Attackers

```bash
# Top brute force IPs
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn | head -10

# Block them
for ip in <IP1> <IP2> <IP3>; do ufw deny from "$ip"; done
```

## Security Checklist

- [ ] `PasswordAuthentication no` in running config (verify with `sshd -T`)
- [ ] fail2ban installed and running with sshd jail
- [ ] UFW active with default deny incoming
- [ ] `PermitRootLogin` either `no` or `prohibit-password` (not `yes` with password auth)
- [ ] All attacker IPs blocked in UFW
- [ ] SSH still accessible via key auth after changes

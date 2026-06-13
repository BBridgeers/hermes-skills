# SSH Key Setup Cheat Sheet

## User Context
- **Ubuntu machine**: `yoga@lenovo` (client)
- **VPS**: `srv1617682` at `VPS_IP_REDACTED` (hosting)
- **Target user**: `root` on VPS

## Generate Key on Ubuntu
```bash
# Generate fresh key (no passphrase for simplicity)
ssh-keygen -t ed25519 -C "yoga@ubuntu"

# Verify public key
cat ~/.ssh/id_ed25519.pub
# Should show: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDOpmyGthKaXrWGAnvCrm6BIh30wvRRUtkmwM7JwjujH yoga@ubuntu
```

## Add Public Key to VPS
```bash
# Method 1: Using ssh-copy-id (recommended)
ssh-copy-id root@VPS_IP_REDACTED

# Method 2: Manual copy
ssh root@VPS_IP_REDACTED "echo 'PASTE_KEY_HERE' >> ~/.ssh/authorized_keys"
```

## Test SSH Connection
```bash
# If SSHD on standard port 22
ssh root@VPS_IP_REDACTED

# If SSHD changed to port 2222 (Hostinger blocks 22)
ssh -p 2222 root@VPS_IP_REDACTED
```

## SSH Config Alias (Avoid Typing Port)
On Ubuntu, add to `~/.ssh/config`:
```
Host hermes-vps VPS_IP_REDACTED
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Then just:
```bash
ssh hermes-vps
# or
ssh VPS_IP_REDACTED
```

## VPS Config Checks

### Is SSHD Running?
```bash
sudo systemctl status ssh --no-pager -l 3
sudo ss -tlnp | grep :2222
```

### Is Root Login Enabled?
```bash
sudo sshd -T 2>/dev/null | grep -i permitrootlogin
# Must say: permitrootlogin yes

# Check overrides
grep -n "PermitRootLogin" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf
```

### Is Port 22 Blocked?
```bash
# On VPS
timeout 3 nc -zv 0.0.0.0 2222  # Should succeed

# From Ubuntu
timeout 3 nc -zv VPS_IP_REDACTED 22  # Likely fails (Hostinger blocks)
timeout 3 nc -zv VPS_IP_REDACTED 2222  # Should succeed
```

### Restore Standard Port 22 (If Needed)
```bash
sudo sed -i 's/^Port 2222$/Port 22/' /etc/ssh/sshd_config
sudo ufw allow 22/tcp
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket ssh
```

Then test from Ubuntu:
```bash
ssh root@VPS_IP_REDACTED
```

## Key Takeaways
1. **Ubuntu generates key**, **VPS stores public key in authorized_keys**
2. **Hostinger blocks SSH egress on port 22** — change to 2222 or use Tailscale
3. **Systemd requires `daemon-reload`** after port changes
4. **SSH config alias** removes need for `-p` flag and `-i` key path
5. **`PermitRootLogin yes` must be in `/etc/ssh/sshd_config.d/hardening.conf`** (override file)
# SSH Port 22 Blocking Diagnostics

**User context**: Ubuntu machine (`yoga@lenovo`) in hotel Wi-Fi trying to SSH to VPS `VPS_IP_REDACTED`.

**Observed behavior**:
```
ping -c 3 VPS_IP_REDACTED      # 3/3 45ms - WORKS
ssh root@VPS_IP_REDACTED       # Connection refused
ssh -p 22 root@VPS_IP_REDACTED # Connection refused
```

**Diagnosis checklist**:

## 1. Is SSHD Running and Listening?
```bash
sudo ss -tlnp | grep :22
sudo systemctl status ssh --no-pager -l 3
```
- If `sshd` not running: `sudo systemctl start ssh`
- If running but port 22 not in `ss` output: configuration issue

## 2. Is Port 22 Reachable From Outside?
```bash
# From Ubuntu, test the actual port (not just ping)
timeout 3 nc -zv VPS_IP_REDACTED 22
# OR
timeout 3 curl -I -m 5 http://VPS_IP_REDACTED:22 2>&1 | head -3
```
- If timeout/connection refused: **port 22 blocked** (hotel router or Hostinger)
- If works: `sshd` issue

## 3. Is The VPS Hosting Provider Blocking Port 22?
Hostinger often blocks SSH egress on port 22 on shared IPs.

**Test with alternative port**:
```bash
# Temporarily change sshd to port 2222
sudo sed -i 's/^#Port 22$/Port 2222/' /etc/ssh/sshd_config
sudo ufw allow 2222/tcp
sudo systemctl daemon-reload
sudo systemctl restart ssh.socket ssh

# Verify
ss -tlnp | grep :2222
```

Then test from Ubuntu:
```bash
ssh -p 2222 root@VPS_IP_REDACTED
```

If this works, Hostinger is blocking port 22.

## 4. Is Hotel/Corporate Network Blocking Port 22?
Public Wi-Fi often blocks port 22 to prevent abuse.

**Workarounds**:
1. Use **cellular hotspot** instead of hotel Wi-Fi
2. Use **Tailscale SSH** (bypasses port restrictions)
3. Use **different port** (2222, 443) on VPS

## 5. Tailscale SSH (Bypasses All Port Blocking)
```bash
# On VPS
tailscale up --ssh
tailscale status

# On Ubuntu
tailscale ssh root@srv1617682
```

Tailscale uses mesh network — no port blocking possible.

---

**Key insight**: `ping` works but `ssh` on port 22 refused = **not a network routing issue**, it's either:
- Hostinger blocking port 22 egress, OR
- Hotel router blocking outbound SSH

The only reliable fix: change SSH port to 2222 or use Tailscale.

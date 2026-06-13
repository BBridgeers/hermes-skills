# UFW Firewall for veracar.co Port 3002

## The Problem

Services bound to `0.0.0.0` still require explicit UFW rules to be accessible from outside the VPS.

## Commands Used This Session

```bash
# Add rule
ufw allow 3002/tcp
ufw status verbose | grep 3002
```

## Why This Fails Without the Rule

- **Inside VPS**: `curl http://127.0.0.1:3002` works (UFW allows loopback by default)
- **Outside VPS**: Browser/external curl returns 502 or timeout because UFW explicitly DENYs the port

## Verification Matrix

| Port | UFW Rule | Test from VPS | Test from External IP |
|------|----------|---------------|----------------------|
| 3002 | DENY     | 200 OK        | 502 / Timeout        |
| 3002 | ALLOW    | 200 OK        | 200 OK               |

## UFW Command Reference

```bash
# List all rules
ufw status verbose

# Allow port
ufw allow 3002/tcp
ufw allow 3100/tcp

# Remove rule (if needed)
ufw delete allow 3002/tcp
```

## Hostinger Cloud Firewall

Hostinger's cloud panel (VPS → Firewall) is separate from UFW. Ensure both are aligned. For now, open port 3002 in UFW is sufficient for external access via direct IP:port.
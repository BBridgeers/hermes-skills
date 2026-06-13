# Tailscale Serve for Hermes Remote Access

Expose Hermes Workspace and Dashboard over Tailscale with automatic TLS.

## Setup

```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up  # authenticate via browser link
```

Enable "Serve" in the Tailscale admin console (https://login.tailscale.com/admin/serve).

```bash
tailscale serve --bg --https=8444 http://127.0.0.1:3100  # Workspace
tailscale serve --bg --https=8443 http://127.0.0.1:9119   # Dashboard
```

Access: `https://MACHINE_NAME.TAILNET.ts.net:8444`

## Port Conflict with Traefik

**Pitfall:** Port 443 is commonly occupied by Traefik or other reverse proxies. Tailscale Serve cannot bind to port 443 if another process already has it. Symptoms: serve starts but HTTPS connections return 404 or timeout.

```bash
# Check what's on port 443
ss -tlnp | grep 443

# If Traefik has it, use alternative ports
tailscale serve --https=443 off  # remove failed binding
tailscale serve --bg --https=8444 http://127.0.0.1:3100
```

## Troubleshooting

- **DNS doesn't resolve**: Client device not on tailnet, or MagicDNS disabled. Try ping MACHINE_NAME from client.
- **Connection timeout**: Tailscale ACLs may block the port. Check https://login.tailscale.com/admin/acls.
- **404 from serve**: Port conflict (see above), or proxy target not running. Verify: `curl http://127.0.0.1:3100`.
- **TLS errors**: First connection after serve starts may take ~30s for certificate issuance.
- **SSH tunnel fallback**: `ssh -L 3100:127.0.0.1:3100 root@VPS_IP` — always works, bypasses Tailscale entirely.

## Verify

```bash
tailscale serve status
ss -tlnp | grep tailscale
curl -sk https://MACHINE_NAME.TAILNET.ts.net:8444 | head -5
```

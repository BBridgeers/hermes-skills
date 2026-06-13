# Tailscale Serve — External Access for Native Hermes Deployments

Use Tailscale Serve to make the Workspace (3100) and Dashboard (9119) accessible
from any Tailscale-connected device (phone, desktop) with automatic HTTPS.

## Setup

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate VPS to your tailnet
tailscale up
# → Visit the auth link in your browser

# Verify
tailscale status
# Should show: <ip>  <hostname>  <account>  linux  -

# Enable Serve on your tailnet (one-time admin action)
# → Visit the URL printed by: tailscale serve --https=443 http://127.0.0.1:3100
# → In Tailscale admin console, enable "HTTPS Certificates" for this node

# Expose services
tailscale serve --bg --https=443 http://127.0.0.1:3100     # Workspace
tailscale serve --bg --https=8443 http://127.0.0.1:9119    # Dashboard
```

## Access URLs

```
https://<hostname>.<tailnet>.ts.net        → Workspace (port 3100)
https://<hostname>.<tailnet>.ts.net:8443   → Dashboard (port 9119)
```

## Important: Serve vs Funnel

- **Serve** (use this): Only Tailscale-connected devices can reach the services.
  Private, encrypted, no public internet exposure.
- **Funnel**: Exposes services to the public internet. DO NOT enable — the
  workspace has terminal access, file control, and agent commands.

## Coexistence with WireGuard

Tailscale uses its own `tailscale0` interface and a random high UDP port.
It does NOT conflict with existing WireGuard Docker containers or host
WireGuard instances on port 51820.

## Persistence

Tailscale is installed as a systemd service (`tailscaled`). Serve config persists
across reboots automatically. Verify with: `tailscale serve status`

## Troubleshooting

- If `tailscale serve` says "Serve is not enabled on your tailnet", visit the
  admin link it provides and enable HTTPS Certificates.
- If workspace loads but models/config don't populate, the dashboard (port 9119)
  may not be running. Check: `ss -tlnp | grep 9119`
- Tailscale auth links expire quickly — if you miss it, run `tailscale up` again.

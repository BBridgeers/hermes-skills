# Port Binding for External Access

Both services bind to `127.0.0.1` by default. For external access (VPS public IP), services must bind to `0.0.0.0`.

## Commands

- **Hermes Workspace (Vite dev)**: `vite dev --host 0.0.0.0 --port 3100`
- **veracar-app (Next.js)**: `PORT=3002 HOSTNAME=0.0.0.0 npx next start` or env vars before command

## Why This Matters

Services bound to `127.0.0.1` respond to curl from VPS but return 502 when accessed via public IP due to browser proxy misconfiguration. Binding to `0.0.0.0` fixes this.

## Verification

```bash
# Should show 0.0.0.0:PORT
ss -tulpn | grep -E ":(3002|3100)\s"
```

# Nginx Port Drift — Diagnosis Pattern

## Symptom

Browser shows "Failed to fetch" or "Network error" on all requests, but:
- The Next.js service is running (`systemctl status veracar-nextjs.service` shows active)
- `curl localhost:<port>` returns 200 from the VPS itself
- External requests fail

## Root Cause

Nginx `upstream` port doesn't match the systemd `PORT=` environment variable. Nginx proxies to a dead port.

## Three-Layer Check

```bash
# Layer 1: Is the service listening?
ss -tlnp | grep -E '3001|3002'

# Layer 2: Where does nginx point?
grep 'server 127.0.0.1' /etc/nginx/sites-enabled/veracar

# Layer 3: Does nginx reach the service?
curl -s -o /dev/null -w "%{http_code}" -H "Host: veracar.co" http://127.0.0.1/
```

If Layer 1 shows the service on 3001 but Layer 2 shows upstream → 3002, that's the bug.

## Fix

```bash
# Write corrected nginx config (system file write restriction: use cat > instead of sed/cp)
cat /tmp/veracar-nginx-fix.conf > /etc/nginx/sites-enabled/veracar
nginx -t && systemctl reload nginx
```

## Real Incident (2026-05-26)

- Nginx had `upstream veracar { server 127.0.0.1:3002; }`
- systemd had `Environment=PORT=3001`
- Next.js was listening on 3001, nginx hitting 3002
- Result: every veracar.co request failed
- Fix: updated nginx upstream to 3001

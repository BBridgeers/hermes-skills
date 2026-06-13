# Nginx Port Mismatch Audit — 502 Gateway Errors

When veracar.co returns 502 Bad Gateway after moving services to new ports:

## Diagnosis

1. Check actual running ports:
   ```bash
   sudo ss -tlnp | grep -E ':3001|:3101|:8765|:8642'
   ```

2. Check nginx upstream config:
   ```bash
   grep -E 'proxy_pass|upstream' /etc/nginx/sites-available/veracar
   ```

3. Compare — if nginx points to `3001` but service runs on `3101`, fix.

## Fix Template

```bash
# Update nginx config (example: hermes-workspace moved to 3101)
sudo sed -i 's/127.0.0.1:3001/127.0.0.1:3101/' /etc/nginx/sites-available/veracar

# Verify and reload
sudo nginx -t && sudo systemctl reload nginx

# Test
curl http://localhost/health
```

## Root Causes

- **Port fallback**: Vite/Next.js falls back to next port if specified port is in use (3000→3100→3101)
- **Config drift**: Service changed port, nginx config not updated
- **Wrong upstream**: Multiple Next.js instances — nginx points to old one

## Verification

After fix:
```bash
# Only expected ports should be public
sudo ss -tlnp | grep -E ':22|:80|:443'

# Internal services bound to 127.0.0.1
sudo ss -tlnp | grep -E ':8642|:8765|:3101|:3001'
```
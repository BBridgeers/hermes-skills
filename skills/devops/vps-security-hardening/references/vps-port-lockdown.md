# VPS Port Lockdown — Binding Internal Services to 127.0.0.1

When auditing `sudo ss -tulpn`, lock down services bound to `0.0.0.0` that should NOT be public:

| Port | Service | Fix | Verify |
|------|---------|-----|--------|
| `8642` | Hermès gateway API | Patch `~/.hermes/config.yaml` → `api_server.host: 127.0.0.1`, restart gateway | `sudo ss -tulpn \| grep :8642` |
| `8765` | FastAPI scraper (fb-scraper) | Patch `scraper/server.py` → `host="127.0.0.1"`, restart service | `sudo ss -tulpn \| grep :8765` |
| `3100` / `3001` | Next.js / Vite devserver | Patch `vite.config.ts` → `host: '127.0.0.1'`, restart devserver | `sudo ss -tulpn \| grep -E ':3100\|:3001'` |
| `11434` | Ollama | Already bound `127.0.0.1` — verify with `ss -tulpn` | — |
| `8000` | Honcho Docker (api/deriver) | Docker port mapping already locks `127.0.0.1:8000` → **no change needed** | — |

## Command Sequence

```bash
# 1. Identify public listeners
sudo ss -tulpn | grep -E ':8642|:8765|:3100|:3001'

# 2. Patch config file (example: hermes gateway)
sed -i 's/host: 0.0.0.0/host: 127.0.0.1/' ~/.hermes/config.yaml

# 3. Patch code file (example: FastAPI scraper)
sed -i 's/host="0.0.0.0"/host="127.0.0.1"/' /root/vehicle-analyzer/scraper/server.py

# 4. Patch vite.config.ts (Next.js)
sed -i "s/host: '0.0.0.0'/host: '127.0.0.1'/" /root/hermes-workspace/vite.config.ts

# 5. Restart affected services
sudo systemctl restart fb-scraper 2>/dev/null || true
pkill -f 'hermes.*gateway'; sleep 2; hermes gateway run --replace
pkill -f 'node.*vite'; sleep 2; cd /root/hermes-workspace && npm run dev -- --host 127.0.0.1

# 6. Verify binding
sudo ss -tulpn | grep -E ':8642|:8765|:3100|:3001'
```

## Expected Result

After lockdown, only these ports remain public:
- `22/tcp` — SSH
- `80/tcp` — nginx (web entrypoint)

Everything else (`8642`, `8765`, `3100`, `3001`, `8000`, `11434`) bound to `127.0.0.1`.

## Pitfalls

1. **Config overrides**: Some services read host from env vars (`API_SERVER_HOST`, `SCRAPER_HOST`). Always check `os.getenv()` in code if the config change doesn't appear.
2. **Multiple FastAPI instances**: The scraper container may have two FastAPI apps — patch both `server.py` and `fb_marketplace.py` if both expose ports.
3. **Version mismatch**: The patched file may be in a `venv` or `dist-packages` folder — use `which python3` + `grep -r '0.0.0.0'` to find the active copy.
4. **Service not managed by systemd**: If `systemctl restart` fails, kill and restart manually: `pkill <service>; sleep 2; <launch-command>`
5. **UFW blocking internal traffic**: If nginx/Traefik can't reach `127.0.0.1` services after binding, check UFW rules — ensure `ufw allow from 127.0.0.1` is not blocked.
6. **Port fallback**: Vite devserver falls back to `3101` if `3100` is in use — always verify with `ss -tulpn`.
7. **Next.js CLI precedence**: Next.js `--host` flag overrides `vite.config.ts` `host` setting — command-line args win.

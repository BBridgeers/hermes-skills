# fb-scraper.service — Service Deployment & Hardening

**Service file**: `/etc/systemd/system/fb-scraper.service`

```ini
[Unit]
Description=FB Marketplace Stealth Scraper API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vehicle-analyzer/scraper
ExecStart=/usr/bin/python3 -u server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=90
TimeoutStopSec=30
Environment=PYTHONUNBUFFERED=1
Environment=GROQ_API_KEY=***
Environment=SCRAPER_PORT=8765

[Install]
WantedBy=multi-user.target
```

**What it does**:
- FastAPI REST server for `veracar.co` to call when scraping Facebook Marketplace
- Runs `scraper/server.py` via systemd
- Auto-restart on failure (`Restart=always`, `RestartSec=10`)
- Exits CLI when browser hangs (uses `scraper.py` headless + `fb_marketplace.py` scraping pipeline)
- Uses Groq `llama-4-scout-17b` (vision) + `llama-3.3-70b` (text enrichment) to extract 26/36 vehicle fields from FB screenshots or URL imports

**Port binding**:
- Current: `0.0.0.0:8765` — public exposure
- Safe: `127.0.0.1:8765` — only accessible from localhost, proxy behind Traefik/nginx

**Server startup line** (server.py:213):
```python
uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
```
→ Change to `host="127.0.0.1"` for hardening.

**Systemd service file**:
- No `EnvironmentFile=` directive — use a wrapper script to load `GROQ_API_KEY` from `~/.hermes/.env`
- Suggest patching to:
  ```ini
  EnvironmentFile=/root/.hermes/.env
  ```

**Health check** (local, pre-hardening):
```bash
curl http://localhost:8765/api/scrape/health
# Expected: {"status":"purring"}
```

**Hardening sequence**:
1. Patch `server.py` line 213: `sed -i 's/host="0.0.0.0"/host="127.0.0.1"/' /root/vehicle-analyzer/scraper/server.py`
2. Add `EnvironmentFile=/root/.hermes/.env` to systemd unit
3. Restart: `sudo systemctl daemon-reload && sudo systemctl restart fb-scraper`
4. Verify binding: `sudo ss -tulpn | grep 8765`
5. Add Traefik rule (or nginx reverse proxy) to `/fb-api/*` → `http://127.0.0.1:8765`
6. Disable public port in Hostinger cloud firewall / UFW

**After hardening**, `veracar.co` (Vercel) → VPS API → nginx → `127.0.0.1:8765` still works.

**If not needed for `veracar.co`**, disable:
```bash
sudo systemctl stop fb-scraper
sudo systemctl disable fb-scraper
```

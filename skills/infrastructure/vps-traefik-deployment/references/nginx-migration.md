# Traefik → Nginx Migration Playbook

## When to migrate

- You have ≤5 public-facing services on the VPS
- Traefik crashed (exit 255) due to a bad domain in config
- You want simpler SSL management without Docker dependency
- Memory is tight (~8 GB RAM shared across services)

## Migration steps (executed 2026-05-26 on srv1617682)

### 1. Remove Traefik
```bash
# Container
docker rm -f traefik-traefik-1

# Volumes and configs
docker volume rm traefik-letsencrypt
rm -rf /docker/traefik /root/traefik.d
```

### 2. Verify nginx is running (it should auto-start)
```bash
systemctl status nginx
ss -tlnp | grep -E ':80|:443'
```

### 3. Configure nginx site
Create `/etc/nginx/sites-enabled/<site>`:
```nginx
upstream backend {
    server 127.0.0.1:3001;
}

server {
    listen 80;
    server_name domain.com www.domain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Add SSL with certbot
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d domain.com -d www.domain.com \
  --non-interactive --agree-tos \
  --email admin@domain.com --redirect
```

### 5. Verify
```bash
curl -sI https://domain.com | head -3
# Should return HTTP/1.1 200 and show nginx in Server header

ss -tlnp | grep -E ':443'
# Should show nginx listening on 443
```

## Key differences from Traefik

| | Traefik | nginx |
|---|---|---|
| SSL | Built-in ACME, tied to process lifecycle | Separate certbot, never takes down server |
| Config location | `/root/traefik.d/*.yml` + compose args | `/etc/nginx/sites-enabled/<site>` |
| Bad domain behavior | Process exits 255 | That vhost only fails, others keep serving |
| Resource usage | ~50-80 MB (Go + Docker socket) | ~5-10 MB (C, event-driven) |
| Docker awareness | Auto-discovers containers | Manual upstream blocks |

## Cert renewal

certbot installs a systemd timer automatically:
```bash
systemctl list-timers | grep certbot
# certbot.service — runs twice daily, renews when <30 days remain
```

# Traefik network_mode: host Configuration

When Traefik uses `network_mode: host`, it shares the host's network namespace — **ports are exposed directly on the VPS, not through Docker port mapping**.

## Key Facts

| Configuration | `network_mode: host` | Standard bridge network |
|--------------|---------------------|------------------------|
| Port binding | Direct on VPS | Docker port mapping |
| `docker port` output | Empty (`{}`) | Shows port mappings |
| External accessibility | Immediately available | Requires `ports:` mapping |
| Firewal requirement | Host firewall (UFW + cloud) | Docker port + host firewall |

## How to Set

When creating Traefik container:

```bash
docker run -d \
  --name traefik-traefik-1 \
  --network host \
  -v /etc/traefik:/etc/traefik:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc/traefik.d:/etc/traefik.d:ro \
  -v /letsencrypt:/letsencrypt:rw \
  traefik:latest \
  --api.dashboard=false \
  --api.insecure=false \
  --providers.docker=true \
  --providers.docker.exposedbydefault=false \
  --providers.file.directory=/etc/traefik.d \
  --providers.file.watch=true \
  --entrypoints.web.address=:80 \
  --entrypoints.websecure.address=:443 \
  --certificatesresolvers.letsencrypt.acme.httpchallenge=true \
  --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web \
  --certificatesresolvers.letsencrypt.acme.email=admin@srv1617682.hstgr.cloud \
  --certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json
```

## Why This Matters

- **`network_mode: host` exposes ports 80 and 443 directly on the VPS**
- No Docker port mapping needed — the container shares the host's network stack
- Traefik listens on `:::80` and `:::443` via `netstat`/`ss`
- External accessibility requires both **UFW** and **Hostinger HPanel firewall** to allow ports 80/443

## Common Failure Modes

### Symptom: Traefik runs but HTTPS not accessible
**Diagnosis**: `docker inspect` shows `"Ports": {}` and `"NetworkMode": "host"` — this is normal, not a bug.

### Symptom: Port 443 shows Connection refused externally
**Diagnosis**: Hostinger HPanel firewall (not UFW) is blocking port 443. Add rule in `panel.hostinger.com → VPS → Firewall`.

### Symptom: Port 80 shows nginx instead of Traefik
**Diagnosis**: nginx is still running. Stop it:
```bash
service nginx stop
systemctl disable nginx  # prevent auto-start on reboot
```

## Verification

```bash
# Check Traefik network mode
docker inspect traefik-traefik-1 --format '{{.HostConfig.NetworkMode}}'
# Expected: host

# Check ports on host
ss -tulpn | grep -E ":(80|443)\s"
# Expected: traefik process listening on both ports

# Check Traefik inside container
docker exec traefik-traefik-1 netstat -tulpn | grep -E ":(80|443)\s"
```

## Migration from root_default Network

If Traefik is currently using `network_mode: root_default`:

```bash
# Stop and remove current container
docker stop traefik-traefik-1
docker rm traefik-traefik-1

# Start new container with network_mode: host
docker run -d \
  --name traefik-traefik-1 \
  --network host \
  -v /etc/traefik:/etc/traefik:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc/traefik.d:/etc/traefik.d:ro \
  -v /letsencrypt:/letsencrypt:rw \
  traefik:latest \
  # ... (same args as above)
```

## Performance Notes

- No NAT overhead — network Mode: host is faster than bridge networking
- No port collision risk — container ports bind directly to host
- **Must stop nginx first** — it conflicts on ports 80/443
# Traefik Dynamic Routing for veracar.co

When routing veracar.co through Traefik (Docker container using `network_mode: host`), create a file-based provider configuration.

## Dynamic Router Config

Save as `/etc/traefik.d/veracar.yml`:

```yaml
http:
  routers:
    veracar:
      rule: "Host(`veracar.co`)"
      service: veracar
      entryPoints: websecure
      tls:
        certResolver: letsencrypt
  services:
    veracar:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:3002"
```

## Apply Configuration

```bash
sudo mkdir -p /etc/traefik.d
cat << 'EOF' | sudo tee /etc/traefik.d/veracar.yml
http:
  routers:
    veracar:
      rule: "Host(`veracar.co`)"
      service: veracar
      entryPoints: websecure
      tls:
        certResolver: letsencrypt
  services:
    veracar:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:3002"
EOF
sudo docker restart traefik-traefik-1
```

## Port Exposure Requirement

**Hostinger HPanel firewall must allow port 443** for HTTPS to work.

Traefik listens on `:::443` and `:::80` via `network_mode: host`, but Docker inspect shows `"Ports": {}` because host networking bypasses port mapping.

Verify Traefik is running in host networking mode:
```bash
docker inspect traefik-traefik-1 --format '{{.HostConfig.NetworkMode}}'
# Expected: host
```

## Verification

After restart:
```bash
# Check Traefik logs for router service
docker logs traefik-traefik-1 | grep -i veracar

# Test HTTP
curl -s -o /dev/null -w "%{http_code}" "http://veracar.co"

# Test HTTPS (requires 443 open in Hostinger HPanel)
curl -s -I "https://veracar.co"
```

## Let's Encrypt Certificate Flow

1. First request to `https://veracar.co` triggers Let's Encrypt challenge
2. Traefik attempts HTTP-01 challenge (requires port 80 open)
3. Certificate stored in `/letsencrypt/acme.json` inside container
4. Subsequent requests use TLS with the issued certificate

If certificate issuance fails:
```bash
# Check ACME status
docker exec traefik-traefik-1 cat /letsencrypt/acme.json

# Manually trigger renewal
docker exec traefik-traefik-1 traefik renews-certificates
```

## Pitfall: Invalid TLD Crashes Traefik (Exit 255)

**Let's Encrypt only issues certificates for domains with recognized public suffixes.** Custom/internal TLDs like `.workspace`, `.local`, `.internal`, `.lan`, `.test`, `.localhost` are NOT recognized by Let's Encrypt's ACME server.

When Traefik has a router with `tls.certResolver: letsencrypt` pointing to an unrecognized TLD:
1. Traefik attempts ACME HTTP-01 challenge
2. Let's Encrypt returns `urn:ietf:params:acme:error:rejectedIdentifier` — "Domain name does not end with a valid public suffix (TLD)"
3. Traefik retries repeatedly (exponential backoff)
4. Eventually Traefik crashes with **exit code 255** (fatal error)
5. Container status shows `Exited (255)`

**Real case (2026-05-26)**: A router for `hermes.workspace` was added to `/root/traefik.d/`. Traefik crashed at 09:32 UTC after failing ACME for this domain. nginx auto-started as fallback at the exact same second.

**Diagnosis**:
```bash
# Check if Traefik is dead
docker ps -a --format '{{.Names}} {{.Status}}' | grep traefik
# → traefik-traefik-1 Exited (255) 8 hours ago

# Check the last error
docker logs traefik-traefik-1 --tail 20 | grep -i "acme\|rejected\|invalid"

# List dynamic configs for invalid domains
ls /root/traefik.d/ && grep -r "Host(" /root/traefik.d/
```

**Fix options** (pick one):
1. **Remove the bad router** — delete the dynamic config file for the invalid domain from `/root/traefik.d/` and restart
2. **Migrate to nginx** — nginx handles this gracefully (no ACME crash). Stop Traefik, start nginx with equivalent config
3. **Use DNS challenge** — switch certResolver to a DNS-based challenge provider instead of HTTP-01

**Recovery**: On the VPS, nginx is configured as a hot standby. If nginx is not running:
```bash
systemctl start nginx
systemctl status nginx
```

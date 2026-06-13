# HPanel Firewall Port Triangulation — Operational Recipe

Quick one-liner to cross-reference HPanel rules against what's actually listening on the VPS. Run this before adding/removing firewall rules.

## Step 1: Audit what's listening

```bash
# Full port-to-service mapping with process names
ss -tlnp | awk 'NR>1{print $4" "$NF}' | sed 's/.*://' | sort -n | while read port proc; do
  pid=$(echo $proc | grep -oP 'pid=\K[0-9]+')
  cmd=$(ps -p $pid -o args --no-headers 2>/dev/null | head -c 60)
  echo "PORT $port → $cmd"
done
```

## Step 2: Cross-reference Docker containers

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

## Step 3: Compare against HPanel rules

Match each HPanel rule against Steps 1+2. Flag categories:
- **DEAD**: HPanel allows but nothing listening → remove
- **PUBLIC exposed but should be internal**: bound to `0.0.0.0` → lock to `127.0.0.1` or restrict source IP
- **Missing from HPanel**: service listening on 0.0.0.0 but no HPanel rule → unreachable from internet

## Step 4: Check for obsolete bind-mount/co-tenant ports

Docker containers with port mappings on `0.0.0.0` even if the HPanel doesn't expose them:
```bash
docker ps --format '{{.Ports}}' | grep -oP '0\.0\.0\.0:\K\d+'
```

## Common patterns on this VPS

| Port | Typical binding | Service |
|------|----------------|---------|
| 80/443 | 0.0.0.0 | nginx (public) |
| 2222 | 0.0.0.0 | SSH (main entry, HPanel-restricted to user IP) |
| 3001 | * | Vehicle Analyzer (veracar.co) |
| 3002 | 0.0.0.0 | Docker hermes-av1-frontend |
| 3100 | 0.0.0.0 | Vite dev server (ZOMBIE — should be dead, verify) |
| 3200 | 127.0.0.1 | Hermes Workspace production server-entry.js |
| 11434 | 0.0.0.0 | Ollama API (HPanel-restricted to user IP) |
| 8642 | 127.0.0.1 | Hermes Gateway |
| 9119 | 127.0.0.1 | Hermes Dashboard |
| 8765 | * | Vehicle Analyzer scraper |

Note: This table is a snapshot from June 11, 2026. Always re-audit with Step 1 — port bindings change.

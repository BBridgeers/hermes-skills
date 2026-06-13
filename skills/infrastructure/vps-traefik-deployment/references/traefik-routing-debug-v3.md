# Traefik Routing Debug — veracar.co (Session 2026-05-24)

## Session Context
Follow-up to initial deployment. User reported SSL certificate error, then "no available server" after cert fix.

## Issue Chain & Resolution

### 1. ERR_CERT_AUTHORITY_INVALID — Self-Signed Cert Served
- Symptom: Chrome warns TRAEFIK DEFAULT CERT as issuer and subject
- Root cause: Router had only entryPoints: [web] and no tls: block
- Fix: Added websecure entrypoint + tls.certResolver: letsencrypt

### 2. Docker Provider Inactive — API Mismatch
- Symptom: Logs: "client version 1.24 is too old. Minimum supported API version is 1.40"
- Root cause: Traefik v2.10 ships Docker client v1.24; host daemon requires >=1.40
- Decision: Keep using file provider. Bumped image to traefik:latest (v3.6.14).

### 3. Config Parse Failure — frameOptions Renamed
- Symptom: "field not found, node: frameOptions"
- Root cause: Traefik v3 renamed frameOptions to customFrameOptionsValue
- Impact: Silent failure — config can't parse, falls back to empty config, no TLS cert
- Fix: customFrameOptionsValue: "SAMEORIGIN"

### 4. No Available Server — Wrong Backend IP
- Symptom: 503 Service Unavailable: no available server
- Root cause: Backend URL http://127.0.0.1:3001 — inside container, 127.0.0.1 is the container itself
- Diagnosis: ping worked, wget timed out -> UFW INPUT dropping TCP from Docker subnet
- Fix: Changed URL to bridge gateway IP http://172.16.1.1:3001 + added iptables rule

### 5. Container Name Conflict
- Symptom: "container name already in use"
- Fix: docker rm -f traefik-traefik-1 before docker compose up -d

## Environment
- Host: Hostinger VPS VPS_IP_REDACTED | Docker bridge: 172.16.1.0/24 gateway 172.16.1.1
- Traefik v3.6.14 | Next.js on :3001 | Scraper on :8765
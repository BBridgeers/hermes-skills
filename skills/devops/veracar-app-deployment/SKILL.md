---
name: veracar-app-deployment
description: Deploy veracar.co vehicle analyzer on bare-metal VPS with proper port binding (0.0.0.0) for external access. Covers Next.js startup flags, environment variable syntax, and verification.
tags: [devops, veracar, nextjs, vps, port-binding]
---

# veracar.co Deployment — VPS Only, External Access

Deploy the vehicle analyzer app (`veracar.co`) on bare metal with public IP accessibility. Unlike the workspace, veracar uses Next.js which requires specific port binding syntax.

## Architecture

> **New**: Analysis Report page at `/analysis/[id]` — see `references/analysis-page-architecture.md` for full page flow, data contract, 14 sections, and navigation wiring.

Veracar uses a two-layer setup:
- **Nginx** (port 80) → reverse proxies to **Next.js** (port 3001)
- **FastAPI Scraper** (port 8765) → proxied by nginx at `/api/scrape`

Next.js binds to `127.0.0.1:3001` for production. Scraper binds to `127.0.0.1:8765` (internal only — accessed via nginx).

**Reverse proxy history**: Traefik (Docker, `network_mode: host`) was previously used but crashed on 2026-05-26 due to an ACME cert failure for `hermes.workspace` (`.workspace` TLD not recognized by Let's Encrypt). nginx auto-started as fallback and is now the permanent reverse proxy. See `references/traefik-dynamic-routing.md` for Traefik config and crash details.

## Nginx Reverse Proxy (Standard Path)

```nginx
upstream veracar { server 127.0.0.1:3001; }
upstream scraper { server 127.0.0.1:8765; }

server {
    listen 80;
    server_name veracar.co www.veracar.co;

    location / {
        proxy_pass http://veracar;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/scrape {
        proxy_pass http://scraper;
        proxy_set_header Host $host;
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

**Critical pitfall**: The nginx `upstream` port MUST match the systemd `Environment=PORT=` value. If they drift (e.g., upstream says 3002 but systemd says 3001), every request fails with "Failed to fetch" / "Network error" — nginx proxies to a dead port. Check both files together when diagnosing connectivity issues:

```bash
grep 'server 127.0.0.1' /etc/nginx/sites-enabled/veracar
grep 'PORT=' /etc/systemd/system/veracar-nextjs.service
```

## Systemd Units

**veracar-nextjs.service** (`/etc/systemd/system/veracar-nextjs.service`):
```ini
[Service]
Type=simple
ExecStart=/usr/bin/npm start
WorkingDirectory=/root/vehicle-analyzer
Environment=PORT=3001
Environment=NODE_ENV=production
EnvironmentFile=-/root/vehicle-analyzer/.env.local
Restart=always
RestartSec=10
```

**veracar-scraper.service** (`/etc/systemd/system/veracar-scraper.service`):
```ini
[Service]
Type=simple
WorkingDirectory=/root/vehicle-analyzer/scraper
EnvironmentFile=/root/vehicle-analyzer/.env.local
Environment=HOST=127.0.0.1
Environment=PORT=8765
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=5
```

Both services use `EnvironmentFile=-/root/vehicle-analyzer/.env.local` to pick up `OPENROUTER_API_KEY` and `GROQ_API_KEY`.

## Firewall

Since both services bind to `127.0.0.1`, no UFW or Hostinger HPanel rules are needed for ports 3001 or 8765 — they're internal-only. Only port 80 (nginx) needs to be open.

Nginx on port 80 requires:
- **Hostinger HPanel** → VPS → Firewall: Port 80, TCP, Allow
- **UFW**: `ufw allow 80/tcp`

## Vision Pipeline

**CURRENT PROVIDER (2026-06-12): Groq key pool** — `meta-llama/llama-4-scout-17b-16e-instruct` via Groq. 3 API keys pooled (`GROQ_API_KEY_POOL` env var, comma-separated). Each endpoint iterates through keys until one succeeds. User provided valid keys after earlier key died.

**Key pool pattern** (used in `/api/extract-listing` and `/api/analyze-photos`):
```typescript
function getGroqKeyPool(): string[] {
    const pool = process.env.GROQ_API_KEY_POOL || process.env.GROQ_API_KEY || '';
    return pool.split(',').map(k => k.trim()).filter(k => k.startsWith('gsk_'));
}
// Then loop: for (const key of keys) { try { fetch Groq with key } catch { next key } }
```

**Fallback history**: OpenRouter free tier was temporarily used when Groq key died (2026-06-12). Switched back to Groq when user provided valid replacement keys. OpenRouter free models (`nvidia/nemotron-3-nano-omni`) may still be viable as secondary fallback but Groq is primary.

**Active free vision models on OpenRouter** (verified 2026-06-12):
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` — ✅ PRIMARY. 30B MoE, vision+audio+video, reasoning. Best for structured JSON extraction from screenshots.
- `nvidia/nemotron-nano-12b-v2-vl:free` — fallback, 12B, vision+video
- `google/gemma-4-31b-it:free` — 31B vision. Skip: user explicitly dislikes Google/Gemini models.
- `nex-agi/nex-n2-pro:free` — 262K context, vision. Untested quality.

**Model discovery**: Query OpenRouter API for current free vision models:
```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import sys,json
for m in json.load(sys.stdin).get('data',[]):
    p = float(str(m.get('pricing',{}).get('prompt','0')).replace('\$','') or 0)
    c = float(str(m.get('pricing',{}).get('completion','0')).replace('\$','') or 0)
    mods = m.get('architecture',{}).get('input_modalities',[]) or []
    if p==0 and c==0 and 'image' in str(mods).lower():
        print(f\"{m['id']} | ctx={m.get('context_length','?')} | mods={mods}\")
"
```

**Required env vars** (in `.env.local`, sourced by systemd `EnvironmentFile=`):
```
OPENROUTER_API_KEY=***  # fallback — free vision models if Groq pool exhausted
GROQ_API_KEY_POOL=*** # PRIMARY — comma-separated Groq keys for vision pipeline
FB_EMAIL=***                # Facebook Marketplace scraper auth
FB_PASSWORD=***            # Facebook Marketplace scraper auth
```

The pipeline flow (both `/api/extract-listing` and `/api/analyze-photos`):
1. OpenRouter free vision models tried SEQUENTIALLY until one returns valid data:
   - `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` → primary, 30B MoE, reasoning
   - `nvidia/nemotron-nano-12b-v2-vl:free` → fallback, 12B, vision+video
   - `nex-agi/nex-n2-pro:free` → last fallback, 262K context
2. Ollama local → last resort (not running on this VPS)

**Sequential fallback pattern** (used in `/api/extract-listing`):
```typescript
const FREE_VISION_MODELS = [
    'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free',
    'nvidia/nemotron-nano-12b-v2-vl:free',
    'nex-agi/nex-n2-pro:free',
];

for (const model of FREE_VISION_MODELS) {
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        // ... same auth/headers for every model
        body: JSON.stringify({ model, messages, ... }),
    });
    if (res.ok) {
        const parsed = JSON.parse(res.choices[0].message.content);
        if (parsed.make || parsed.year) {
            vehicle = parsed;
            break; // stop on first success
        }
    }
}
```
This prevents single-model blind spots — one free model may fail/return garbage while another succeeds.

**OpenRouter API setup** (used in both endpoints):
```typescript
const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ***        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://veracar.co',       // REQUIRED by OpenRouter
        'X-Title': 'veracar.co Vehicle Analyzer',    // REQUIRED by OpenRouter
    },
    body: JSON.stringify({
        model: 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free',
        messages: [...],
        temperature: 0.1,
        max_tokens: 2048,  // extract-listing uses 2048
        // max_tokens: 1024,  // analyze-photos uses 1024
    }),
});
```

**Free model constraint**: User requires ALL API models to be $0. Never select a paid model without explicit approval. Check OpenRouter pricing before pinning a model ID — free tier models can change.

**Critical**: All `JSON.parse` calls on LLM output must use `sanitizeJson()` helper (strips control characters + HTML guard). See `references/json-sanitization-vision-output.md`.

### Master Inspector Protocol

All vision prompts are enriched with the **Master Assessor Inspection Protocol** (`src/lib/master-inspector.ts`), a 17KB knowledge base covering:

- **Structural integrity**: frame/unibody inspection, rust classification (surface/scale/perforation/structural), weld forensics
- **Paint & body**: orange peel, clear coat failure, panel gap tolerances (>2mm variance = suspect), crease vs dent, flood indicators
- **Glass & lighting**: bullseye/star break/edge crack, OEM vs replacement, fogged lenses
- **Tires & wheels**: cupping (suspension), feathering (alignment), dry rot, sidewall bulges, DOT date codes
- **Interior forensics**: bolster collapse, pedal pad wear vs odometer, seat twist, flood indicators
- **Under-hood**: milkshake oil (head gasket), rod knock, timing chain rattle, fresh RTV, stop-leak in coolant
- **Make/model fatal flaws**: 60+ documented pattern failures cross-referenced by make/model with severity and repair cost estimates. See `references/make-model-fatal-flaws.md`.

This protocol is imported by both `/api/extract-listing` and `/api/analyze-photos` as `${MASTER_INSPECTOR_KNOWLEDGE}`.

## Photo-Based Analysis

Veracar supports three photo-based analysis flows:

1. **Photo-only auto-detect**: Upload photos → Run AI Analysis → VERA IDs make/model/year/trim/body/colors from photos via `/api/analyze-photos`, THEN runs full market analysis. No manual make/model entry needed. Condition data (exterior, interior, mechanical, notable damage, overall impression) auto-populates from photos.
2. **Screenshot + photos combined**: Paste listing screenshot while photos are uploaded → all images analyzed together via `/api/extract-listing`, listing data + condition assessment in one call. Photos are appended as `photo0`, `photo1`, ... in FormData.
3. **Condition extraction from photos**: The `analyze-photos` prompt now has a dedicated PART 2 for condition assessment (exterior paint/dents/rust, interior seats/dash/carpets, mechanical engine bay/leaks/rust). These populate the condition text boxes and factor into the vehicle score.

### Key API endpoints for photo analysis:
- `POST /api/analyze-photos` — takes photo files (`photo0`, `photo1`, ...), returns vehicle identity + condition
- `POST /api/extract-listing` — accepts `photo0`, `photo1`, ... alongside screenshot `image`

### Frontend flow for auto-detect:
- `VehicleForm` button disabled check relaxed: allows analysis without make/model when photos present
- `handleRunAnalysis` checks: if `!make || !model` and `photos.length > 0`, calls `/api/analyze-photos` first
- Detected fields populate form before continuing to `/api/chat` for market analysis
- Condition fields from photo analysis map to: `exteriorCondition`, `interiorCondition`, `mechanicalCondition`, `notableDamage`, `overallImpression`

## Environment Variables: systemd ≠ .env.local

**Next.js does NOT automatically read `.env.local` files at runtime** when launched via systemd. The `EnvironmentFile=` directive in the systemd unit is REQUIRED.

**Pitfall**: Adding a new variable to `.env.local` and restarting the service won't work without `EnvironmentFile` in the systemd unit. The service only sees variables explicitly set via `Environment=` or `EnvironmentFile=` in the unit file.

## Verification

## Redis Persistence Architecture

**Hard rule**: ALL persistent state goes through Upstash Redis. Nothing in `localStorage`. Full architecture: `references/redis-persistence-architecture.md`.

## Verification

```bash
# Next.js health
curl -s -o /dev/null -w "%{http_code}" -H "Host: veracar.co" http://127.0.0.1/

# Scraper health
curl -s http://127.0.0.1:8765/api/scrape/health
# → {"status":"purring","sessions_count":2}

# Through nginx
curl -s http://veracar.co/health
# → {"status":"ok","service":"veracar"}

# Vision pipeline test (from vehicle-analyzer dir)
export $(grep -v '^#' .env.local | grep '=' | xargs)
python3 -c "import asyncio, os, sys; sys.path.insert(0,'scraper'); from vision_extractor import _call_openrouter_api; print(asyncio.run(_call_openrouter_api('Say hello as JSON: {\"msg\":\"\"}', '', os.environ['OPENROUTER_API_KEY'])))"
```

## Why Port Drift Happens

The nginx config and systemd unit are edited independently. Common scenarios:
- Someone changes the systemd `PORT=` to avoid a conflict but forgets to update nginx upstream
- A copy-paste of a deployment config from a different environment carries a stale port number
- The service was previously on 3002, migrated to 3001, but nginx was never updated

**Diagnosis pattern**: When the browser shows "Failed to fetch" or "Network error" but the Next.js process is running, check the three-layer chain:
1. `ss -tlnp | grep <port>` — is the service listening?
2. `grep 'server 127.0.0.1' /etc/nginx/sites-enabled/veracar` — does nginx point to the right port?
3. `curl -H "Host: veracar.co" http://127.0.0.1/` — does nginx actually reach the service?

## Git Workflow — Commit & Push After Changes

**Every coding session on vehicle-analyzer MUST end with committed and pushed changes.** Uncommitted work is lost work. The repo lives at `git@github.com:BBridgeers/vehicle-analyzer.git` (branch: `main`).

After any code change (new features, bug fixes, config updates, new scripts):

```bash
cd /root/vehicle-analyzer
git add -A
git status --short   # verify what's staged
git commit -m "<type>: <description>"
git push origin main
```

Commit types: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `perf:`

**Pitfall**: The VPS is the SOLE development environment for vehicle-analyzer. There is no local laptop copy. If the VPS dies or the repo isn't pushed, ALL work is lost. Push after every session.

**Quick audit** — check parity at any time:
```bash
cd /root/vehicle-analyzer && git status --short && echo "---UNPUSHED---" && git log --oneline origin/main..HEAD
```
Empty output = clean and pushed. Anything else = action required.

## VERA Chat Integration (Hermes-Powered)

The app includes VERA CHAT 2.0 — an omniscient in-app debug assistant powered
by Hermes Agent. The chat widget appears on every page as a floating button
(bottom-right). It proxies through `/api/chat` to Hermes's API server on
`127.0.0.1:8642`. See `references/vera-chat-hermes-integration.md` for the
full architecture, debug mode, and forward-producing suggestions.

**⚠️ ALWAYS-ON CONSTRAINT**: VERA must ALWAYS accept input — never gate the
chat behind `hasContext`, never show "Scan a vehicle to activate VERA", never
disable the input or send button based on vehicle state. The only valid disable
condition is `isStreaming` (response in progress). See `references/vera-chat-hermes-integration.md`
for the always-on design rationale and the removed `hasContext` guard.

## Pitfalls

- **EADDRINUSE on deploy**: Old Next.js process holds port 3001. Must `fuser -k 3001/tcp` before starting new build. BUT: build first, verify build succeeds, THEN ask user before killing old process. Never kill the app unprompted.
- **Sequential model fallback is REQUIRED for free vision**: Single free model calls fail silently. Always loop through at least 3 free vision models (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` → `nvidia/nemotron-nano-12b-v2-vl:free` → `nex-agi/nex-n2-pro:free`). One model returning garbage doesn't mean extraction failed — try the next. Use `break` on first success.
- **Stale vehicle data persists on extraction failure**: When extraction returns empty/garbage (no make/model/year/price), the old form data silently persists because setForm only overrides populated fields. Fix: when extraction returns no usable data, explicitly clear the form fields AND set error state. Do NOT throw — that leaves stale data in place. See page.tsx processScreenshot and handleScrape for the clearing pattern.
- **VERA input blocked — always-on constraint**: The chat input must NEVER be disabled based on vehicle state. disabled= should only reference isStreaming. sendMessage must NOT have if (!hasContext) return. VERA works without a vehicle using the omniscient debug prompt.
- **Free models only**: User requires 0-dollar API costs. Never select a paid model without explicit approval.
- **Duplicate drifts silently**: `page.tsx` had an inline `downloadReport()` that diverged from the canonical `generateTextReport()` in `AnalysisResults.tsx`. Insurance showed `$undefined` because page.tsx accessed nested properties (`ins.monthly`) on flat types (`personalMonthly`). **Fix**: Export the canonical function, import in all consumers. Single source of truth prevents this. See `references/analysis-page-architecture.md` for the full data access contract.
- **Do NOT kill the running app without user permission.** The user cursed me out for running `fuser -k 3001/tcp` unprompted. Build first, verify the build succeeds, THEN ask before killing old process. The app going down mid-session breaks the user's workflow and kills VERA (who IS the app). VERA going offline during a debug session is catastrophic. The user's time is precious — an unexpected restart disrupts their active work.
- **Groq key pool > single key**: User may provide multiple Groq keys. Always configure a pool (`GROQ_API_KEY_POOL`) rather than a single key. Iterate through them — one key may be rate-limited while another works.
- **Free models are a fallback, not primary**: The user's Groq keys work for paid models. Only use free OpenRouter models when ALL Groq keys are exhausted. Do NOT switch to free models preemptively — trust the user when they say a key is valid.
- **Trust the user's keys**: When the user says a key is valid, USE it. Don't run validation tests that can't work due to security redaction. Deploy with the key and let runtime errors surface actual issues.
- **Groq key is DEAD? Try the pool first**: Groq keys expire silently. Before switching to OpenRouter free tier, check `GROQ_API_KEY_POOL` env var — multiple keys may be configured. Only fall back to OpenRouter free models when the entire pool is exhausted.
- **FB scraper will fail — don't fight it endlessly.** Facebook Marketplace anti-bot blocks bare Playwright within seconds. When URL scraping returns empty data, tell the user immediately and suggest screenshots (which work via the Groq vision pipeline). Do NOT spend 10+ turns debugging the scraper — the user wants results, not scraper archeology. FB listing data IS available in meta tags (`og:title`, `og:description`) and visible body text even behind the login wall, but the VPS scraper's Playwright gets blocked before reaching extraction logic. Hermes' browser (Browserbase with residential proxies) can see FB content. See `fb-marketplace-stealth-scraper` skill.

## Related Skills

- `hermes-workspace-deployment` — workspace deployment (Vite dev)
- `Next.js Bare-Metal Deployment` — general Next.js deployment patterns

## Consolidated Skills

This skill absorbs: `vercel-carfax-pdf-integration`.

## Support Files

- `references/groq-key-pool-pattern.md` — Multi-key API pool pattern for vision endpoints

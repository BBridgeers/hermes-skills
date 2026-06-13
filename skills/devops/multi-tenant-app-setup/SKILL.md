---
name: multi-tenant-app-setup
description: Build multi-tenant Next.js/Vercel apps with user-scoped Redis KV, JWT/auth middleware, per-user rate limiting, and user isolation. Use when adding user accounts, session isolation, or billing/per-user tracking to a VPS-hosted app.
tags:
  - nextjs
  - vercel
  - redis
  - multi-tenant
  - auth
related_skills:
  - vercel-pdf-extraction
  - devops/hermes-workspace-deployment
  - localstorage-to-redis-migration
---

# Multi-Tenant Next.js App Setup — VPS Hosted

## When to use
- Adding user accounts/session isolation to a VPS-hosted Next.js app
- Need per-user KV (Redis) keys for fleet data, comparison matrices, rate limiting
- Want to transition from single-user to multi-tenant while keeping single-user fallback (HARD_CODED_USER_ID)
- Need per-user rate limiting (not just per-IP)
- Target: VPS hostinger srv1617682 (VPS_IP_REDACTED) or similar bare-metal VPS

## Live Validation Required — Every Modality Tested End-to-End

When building or modifying a vehicle evaluation or fleet management app, YOU MUST LIVE-TEST EVERY INPUT MODALITY and OUTPUT FUNCTION. The user will reject theoretical completion.

### Input Modalities (ALL must be tested live)
| # | Modality | Test Action | Verify Outcome |
|---|----------|-------------|----------------|
| 1 | VIN Entry | Enter `1HGCV1F34LA012345` → Click Decode | Year 2020, Make HONDA, Model Accord, Score 40, 4 recalls |
| 2 | Listing URL | Paste FB Marketplace URL → Click Scrape | Platform auto-detected, fields auto-filled |
| 3 | Quick Reference URL | Paste any URL | UI accepts, no errors |
| 4 | Listing Screenshot | Paste/Ctrl+V image | Vision OCR fallback available |
| 5 | Vehicle Photos | Upload multiple images | Multi-file accepted |
| 6 | CARFAX PDF | Upload PDF | Text extraction + Vision OCR pipeline |

### Output Functions (ALL must be tested live)
| # | Function | Test Action | Verify Outcome |
|---|----------|-------------|----------------|
| 1 | Fleet Save | Click "Save to Fleet" | Appears in Fleet Dashboard with score |
| 2 | Fleet History Reload | Click history item | Form populates with saved data |
| 3 | Comparison Matrix | Click "Comparison Matrix" | Multiple vehicles display with metrics |
| 4 | Market Analytics | Navigate to `/analytics` | Real data shown, filters functional |
| 5 | Market Sweep | Run sweep → Click "Analyze" | Result pre-fills evaluation form |
| 6 | Sweep Export | Click "Export CSV" | File downloads with data |

### Live Validation Checklist
- [ ] VIN decode auto-fills year/make/model/trim/recalls
- [ ] Listing URL auto-detects platform and scrapes
- [ ] Quick Reference URL input works
- [ ] Screenshot paste/crop works (Vision OCR fallback)
- [ ] Vehicle photos multi-upload works
- [ ] CARFAX PDF upload → text/Vision extraction
- [ ] "Save to Fleet" actually saves and appears in dashboard
- [ ] Fleet history item click loads saved vehicle into form
- [ ] Comparison Matrix shows all 3+ vehicles with metrics
- [ ] Analytics shows real data, not static mock
- [ ] Market Sweep runs actual scrape, returns real results
- [ ] Sweep "Analyze" button pre-fills form correctly
- [ ] Export buttons download files with data

### Pitfalls to Hunt For
- **"Save to Fleet" doesn't save** — button clicked, no change visible in fleet
- **History items don't load** — clicks but doesn't populate form fields  
- **Navigation redirects wrong** — sweeps goes to analytics, comparison missing
- **Buttons enabled but do nothing** — UI says ready, no API call, no feedback
- **API calls fail silently** — Network tab shows 200 but no data returned
- **Form clearance after save** — form resets after save instead of showing success

### Your Live Validation Workflow
1. Start on / (root) — verify all input fields visible
2. Test VIN → `1HGCV1F34LA012345` → Click Decode → verify auto-fill
3. Test Listing URL → paste real FB URL → Click Scrape → verify platform detection
4. Test Save to Fleet → Click "Save to Fleet" → Go to Fleet Dashboard → verify vehicle appears
5. Test History Restore → Click history item → verify form populates with saved data
6. Test Comparison Matrix → Navigate to `/comparison` → verify 3+ vehicles display
7. Test Analytics → Navigate to `/analytics` → verify real data, filters functional
8. Test Market Sweep → Run sweep → Click "Analyze" on result → verify form prefill
9. Test Export → Click Export CSV → verify file downloads with data

**LIVE VALIDATION IS MANDATORY. DO NOT PROCEED TO REPORTING WITHOUT IT.**

## Key patterns from this session

### 1. Multi-tenant KV wrapper (`src/lib/kv-user-wrapper.ts`)

```typescript
import { Redis } from '@upstash/redis';

const USER_PREFIX = (uid: string) => `user:${uid}:`;

export function userKv(uid: string, kv: Redis): Redis {
  const prefix = USER_PREFIX(uid);

  const origSet = kv.set.bind(kv);
  const origGet = kv.get.bind(kv);
  const origDel = kv.del.bind(kv);
  const origIncr = kv.incr.bind(kv);
  const origHSet = kv.hset.bind(kv);
  const origHGet = kv.hget.bind(kv);
  const origZAdd = kv.zadd.bind(kv);
  const origZRange = kv.zrange.bind(kv);

  const proxied: any = {
    set: (key: string, val: any, opts?: any) => origSet(prefix + key, val, opts),
    get: (key: string) => origGet(prefix + key),
    del: (key: string) => origDel(prefix + key),
    incr: (key: string) => origIncr(prefix + key),
    hset: (key: string, data: any) => origHSet(prefix + key, data),
    hget: (key: string, field: string) => origHGet(prefix + key, field),
    zadd: (key: string, data: any) => origZAdd(prefix + key, data),
    zrange: (key: string, start: number, end: number) => origZRange(prefix + key, start, end),
    ...kv,
  };
  
  return proxied as any as Redis;
}
```

### 2. User-scoped rate limiting (`src/lib/rate-limit.ts`)

```typescript
import { kv } from './kv';
import { userKv } from './kv-user-wrapper';

const RATELIMIT_USER_PREFIX = (userId: string) => `${userId}:ratelimit:`;

export async function rateLimit(
    key: string,
    maxRequests: number,
    windowSeconds: number,
    userId: string
): Promise<{ allowed: boolean; remaining: number; resetAt: number }> {
    const prefixedKey = `${RATELIMIT_USER_PREFIX(userId)}${key}`;
    const count = await kv.incr(prefixedKey);
    
    if (count === 1) {
        await kv.expire(prefixedKey, windowSeconds);
    }

    const resetAt = Date.now() + (await kv.ttl(prefixedKey)) * 1000;

    if (count > maxRequests) {
        return { allowed: false, remaining: 0, resetAt };
    }

    return { allowed: true, remaining: maxRequests - count, resetAt };
}

// Convenience wrappers
export const EXTRACT_LIMIT = { max: 20, windowSec: 3600 };       // 20/hr
export const CHAT_LIMIT    = { max: 100, windowSec: 86400 };     // 100/day
```

### 3. User ID detection (`src/lib/kv-user-wrapper.ts`)

```typescript
export async function getCurrentUserId(request?: Request): Promise<string> {
    // Check for hardcoded user (VPS local mode)
    const hardcoded = process.env.HARD_CODED_USER_ID;
    if (hardcoded) {
        return hardcoded;
    }

    // Check Authorization header for API tokens
    const authHeader = request.headers.get('authorization');
    if (authHeader && authHeader.startsWith('Bearer ')) {
        const token = authHeader.slice(7);
        if (token.length > 10) {
            return token;  // TODO: Validate against JWT store
        }
    }

    // Fall back to IP-based identification (shared environment)
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 
               request.headers.get('x-real-ip') || 'unknown';
    return ip;
}
```

### 4. Auth middleware (`src/lib/auth-middleware.ts`)

```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function verifyUser(request: NextRequest): Promise<{ userId: string; legal: boolean }> {
    const hardcoded = process.env.HARD_CODED_USER_ID;
    if (hardcoded) {
        return { userId: hardcoded, legal: true };
    }

    const authHeader = request.headers.get('authorization');
    if (authHeader && authHeader.startsWith('Bearer ')) {
        const token = authHeader.slice(7);
        if (token.length > 10) {
            return { userId: token, legal: true };
        }
    }

    const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
    return { userId: ip, legal: true };
}
```

### 5. Updated API routes

```typescript
// /api/fleet/route.ts — before → after

// Before:
const FLEET_KEY = 'vera_fleet_prod';
const fleet = await kv.get(FLEET_KEY);

// After:
const userId = await getCurrentUserId(req);
const fleet = await kv.get(`${userId}:${FLEET_KEY}`);
```

## Dependencies to add

```bash
npm install next-auth @auth/prisma-adapter
```

For user session storage, use Upstash Redis with next-auth (adapter: `@auth/redis-adapter`).

## Environment variables

```
# VPS .env
HARD_CODED_USER_ID=blake
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...

# For next-auth (optional, when full auth is ready)
NEXTAUTH_URL=https://veracar.co
NEXTAUTH_SECRET=change-me
```

## Pitfalls

- **User key collision**: Always prefix with `user:{userId}:` to avoid cross-user data leaks
- **Hardcoded fallback**: `HARD_CODED_USER_ID` must be set for VPS single-user mode, otherwise IP falls back to `unknown`
- **Rate limit key design**: Include user ID AND endpoint AND date string for daily rollover:
  ```typescript
  `${userId}:ratelimit:fleet_create:${new Date().toDateString()}`
  ```
- **No SCAN on Vercel KV**: Upstash KV doesn't support `SCAN` for listing keys — maintain a registry set if you need audit/cleanup
- **redis-cli on VPS not in PATH**: Use `docker exec honcho-redis-1 redis-cli` or add to PATH

## User Preference Note
User explicitly disfavors Google AI models (Gemini). Prefer Groq (free tier) for OCR/vision.

## References
- `references/multi-tenant-kv-wrapper.ts` — User-scoped KV proxy pattern
- `references/rate-limit-upgrade.ts` — Per-user rate limiting implementation
- `references/auth-middleware.ts` — Auth verification patterns
- `references/fleet-route.ts` — Example API route with user isolation
- `references/sessionize-kv-keys.sh` — Script to rename legacy flat keys to user-scoped format
", "file_path": "devops/multi-tenant-app-setup/SKILL.md"}
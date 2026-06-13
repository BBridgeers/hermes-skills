---
name: localstorage-to-redis-migration
description: Migrate Next.js apps from localStorage to Upstash Redis with zero-downtime dual-write pattern. Covers whitelisted KV API route, client helper with localStorage fallback, async function ripple handling, and component update patterns.
triggers:
  - User asks to migrate localStorage to Redis, Upstash, or KV
  - User mentions "store locally" data needs to persist on Vercel
  - User asks about making localStorage data survive across devices/sessions
---

# localStorage → Redis (Upstash) Migration Pattern

Migrate any Next.js App Router app from `localStorage` to Upstash Redis with a **dual-write** strategy: write to both KV and localStorage so the app works before Redis is configured.

## Step 1: Ensure `@upstash/redis` is installed

```bash
cd project && npm ls @upstash/redis || npm install @upstash/redis
```

## Step 2: Create whitelisted KV API route

Create `src/app/api/kv/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { kv } from '@/lib/kv';

const ALLOWED_KEYS = [
  'activeVehicle',
  'activeAnalysis',
  // ... add all keys that need Redis persistence
] as const;

type AllowedKey = (typeof ALLOWED_KEYS)[number];
function isAllowed(key: string): key is AllowedKey {
  return ALLOWED_KEYS.includes(key as AllowedKey);
}

// GET /api/kv?key=vehicle-analyzer-history
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const key = searchParams.get('key');
  if (!key || !isAllowed(key)) {
    return NextResponse.json({ error: `Invalid key. Allowed: ${ALLOWED_KEYS.join(', ')}` }, { status: 400 });
  }
  try {
    const value = await kv.get<string>(key);
    return NextResponse.json({ key, value: value ?? null });
  } catch (e: any) {
    return NextResponse.json({ error: 'KV read failed', detail: e.message }, { status: 500 });
  }
}

// POST /api/kv { key, value }
export async function POST(request: Request) {
  const body = await request.json();
  const { key, value } = body;
  if (!key || !isAllowed(key)) {
    return NextResponse.json({ error: `Invalid key.` }, { status: 400 });
  }
  if (value === undefined || value === null) {
    await kv.del(key);
    return NextResponse.json({ key, action: 'deleted' });
  }
  const serialized = JSON.stringify(value);
  const ttl = (key === 'activeVehicle' || key === 'activeAnalysis') ? 604800 : 2592000;
  await kv.set(key, serialized, { ex: ttl });
  return NextResponse.json({ key, action: 'saved' });
}

// DELETE /api/kv?key=...
export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const key = searchParams.get('key');
  if (!key || !isAllowed(key)) {
    return NextResponse.json({ error: 'Invalid key.' }, { status: 400 });
  }
  await kv.del(key);
  return NextResponse.json({ key, action: 'deleted' });
}
```

**Security**: The `ALLOWED_KEYS` whitelist prevents arbitrary Redis access from the client. Only explicitly listed keys can be read/written.

**TTL**: Active vehicle/analysis data gets 7 days; history/chat gets 30 days.

## Step 3: Create client-side KV helper

Create `src/lib/kv-client.ts`:

```typescript
const KV_API = '/api/kv';

async function kvGet<T>(key: string): Promise<T | null> {
  try {
    const res = await fetch(`${KV_API}?key=${encodeURIComponent(key)}`);
    if (!res.ok) return null;
    const data = await res.json();
    if (data.value === null) return null;
    return JSON.parse(data.value) as T;
  } catch {
    // Fallback to localStorage during SSR or network failures
    if (typeof window !== 'undefined') {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    }
    return null;
  }
}

async function kvSet(key: string, value: unknown): Promise<void> {
  // Dual-write: localStorage for instant access + KV for persistence
  if (typeof window !== 'undefined') {
    if (value === null || value === undefined) {
      localStorage.removeItem(key);
    } else {
      localStorage.setItem(key, JSON.stringify(value));
    }
  }
  try {
    await fetch(KV_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value }),
    });
  } catch { /* silent — localStorage already has data */ }
}

async function kvDelete(key: string): Promise<void> {
  if (typeof window !== 'undefined') localStorage.removeItem(key);
  try {
    await fetch(`${KV_API}?key=${encodeURIComponent(key)}`, { method: 'DELETE' });
  } catch { /* silent */ }
}

export { kvGet, kvSet, kvDelete };
```

**Dual-write pattern**: Every write goes to localStorage AND Redis. If Redis is unreachable, the app works from localStorage. If localStorage is cleared (new device/browser), Redis restores on next load.

## Step 4: Update consuming modules

### Pattern A: React Context (useEffect load, setter save)

Replace:
```typescript
useEffect(() => {
  const stored = localStorage.getItem("activeVehicle");
  if (stored) setState(JSON.parse(stored));
}, []);

const setVehicle = (v) => {
  localStorage.setItem("activeVehicle", JSON.stringify(v));
};
```

With:
```typescript
useEffect(() => {
  async function load() {
    const stored = await kvGet<Vehicle>("activeVehicle");
    if (stored) setState(stored);
    setIsLoaded(true);
  }
  load();
}, []);

const setVehicle = (v) => {
  setState(v);
  kvSet("activeVehicle", v); // fire-and-forget
};
```

### Pattern B: Sync functions becoming async

When a library function like `getHistory()` becomes async, consumers that used it in `useState(() => ...)` or synchronous calls must be updated:

**Before** (ComparisonView.tsx):
```typescript
const [entries] = useState<HistoryEntry[]>(() => getHistory());
```

**After**:
```typescript
const [entries, setEntries] = useState<HistoryEntry[]>([]);
const [loaded, setLoaded] = useState(false);

useEffect(() => {
  getHistory().then(data => { setEntries(data); setLoaded(true); });
}, []);

if (!loaded) return null; // prevent flash
```

### Pattern C: Page-level inline handlers

For quick inline writes (like button `onClick`), use dynamic import to avoid bundling kv-client into every page:

```typescript
onClick={async () => {
  const { kvGet, kvSet } = await import('@/lib/kv-client');
  const alerts = (await kvGet<any[]>('alertTriggers')) || [];
  alerts.push({ name, region });
  await kvSet('alertTriggers', alerts);
}}
```

Dynamic import keeps `kv-client` out of the page bundle until the button is clicked.

## Step 5: Verify migration

```bash
# Search for remaining direct localStorage usage
grep -rn 'localStorage\.\(get\|set\|remove\)Item' src/ --include='*.ts' --include='*.tsx' | grep -v kv-client.ts
```

Only `kv-client.ts` should contain localStorage calls (as intentional fallback). All business modules should use `kvGet`/`kvSet`.

## Pitfalls

- **Upstash Redis won't auto-create from `Redis.fromEnv()` on Vercel** — must set `KV_REST_API_URL` and `KV_REST_API_TOKEN` env vars in Vercel project settings
- **The whitelist MUST include every key** — missed keys silently fail (400 response). Search the entire src dir for `localStorage.getItem(` to build the list
- **Large objects may exceed Redis key size limits** — if a chat session or history grows large, consider splitting into multiple keys
- **Concurrent writes from multiple tabs can race** — the last write wins. For critical data, use Redis transactions or a session lock key

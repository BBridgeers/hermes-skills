# Standalone Page Pattern — veracar.co

Every main app page on veracar.co is a standalone top-level route. This document is the canonical pattern.

## Rule

No parameterized `[id]` routes for main pages. No localStorage-based data passing between routes. All persistence through Upstash Redis.

## GDrive Design Check (BEFORE building)

**Always search Google Drive for design specs before building a new page.** The user keeps design documents like `vehicle_analyzer_lisitng_evaluation_output_design.md` (ID: `1qxoxKdmi-9keS9ahWlY-J_JEL7rwCJ7f`) on GDrive. See `references/gdrive-design-docs.md` for the search/download pattern. Building without the design doc causes rework — the `/analysis` page was initially built as a `[id]` dynamic route with localStorage because the spec wasn't consulted first.

## File Structure

```
src/app/
├── {page}/page.tsx          # client component, fetches from API
├── api/{page}/route.ts      # GET + POST, reads/writes Redis
```

## API Route Template

```typescript
// src/app/api/{resource}/route.ts
import { NextResponse } from 'next/server';
import { kv } from '@/lib/kv';
import { getCurrentUserId } from '@/lib/kv-user-wrapper';

const KEY = '{resource}';

export async function GET(req: Request) {
  const userId = await getCurrentUserId(req);
  const data = await kv.get(`${userId}:${KEY}`) as YourType | null;
  if (!data) return NextResponse.json({ success: false, error: 'Not found' }, { status: 404 });
  return NextResponse.json({ success: true, vehicle: data.vehicle, result: data.result, timestamp: data.timestamp });
}

export async function POST(req: Request) {
  const userId = await getCurrentUserId(req);
  const body = await req.json();
  await kv.set(`${userId}:${KEY}`, { ...body, timestamp: new Date().toISOString() });
  return NextResponse.json({ success: true });
}
```

## Page Template

```typescript
// src/app/{page}/page.tsx
"use client";

export default function Page() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/{resource}')
      .then(r => r.ok ? r.json() : Promise.reject('Not found'))
      .then(j => setData(j))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // loading state → spinner
  // error state → empty state with link to trigger action
  // success state → full page content
}
```

## Page Patterns by Type

### Analysis/Report Pages

Pages that display computed results (like `/analysis`) follow this pattern:
- Data flows: trigger page → POST `/api/{resource}` (Redis) → navigate to `/{resource}` → GET `/api/{resource}` (Redis) → display
- **Decision buttons go IN the top banner**, not at the bottom of the page
- Banner includes: verdict, score, "Why?"/info button, Download button, **and** primary action buttons (Add/Pass/etc.)
- Empty state: "No {Resource} Yet" with link to trigger page

### Fleet/List Pages

Pages that display collections (like `/fleet`) follow this pattern:
- Data source: Redis key `{userId}:fleet`
- Render a list/grid of cards
- Support selection for comparison, delete, etc.

## Navigation

Every new standalone page MUST be added to the sidebar nav of:
- `src/app/page.tsx` (New Evaluation — main entry point)
- `src/app/fleet/page.tsx` (Fleet Dashboard)
- `src/app/analytics/page.tsx` (Market Analytics)

The nav link pattern:
```tsx
<Link href="/{page}" className="flex items-center gap-3 px-3 py-2 text-gray-400 hover:text-gray-200 hover:bg-[#1a1816] rounded-md text-sm font-medium transition-colors">
  <svg>...</svg>
  Page Name
</Link>
```

When the page IS the active page, use `bg-[#1e1c19] text-cyan-400` styling.

## Pitfalls

1. **localStorage in API routes is a hard bug** — server-side code has no `window.localStorage`. The previous `/api/analysis/[id]/route.ts` called `localStorage.getItem()` in a GET handler and failed silently at runtime.

2. **Dynamic `[id]` routes hide pages from navigation** — they're only reachable via `router.push()` with a generated ID, never from the sidebar. Main app pages must be static top-level routes.

3. **Missing nav links** — if a page exists but has no sidebar link, users can only reach it via URL or programmatic navigation. Every page needs nav links on all entry points.

4. **TypeScript cast for `kv.get()`** — Upstash `kv.get()` returns `unknown`. Always cast: `as YourType | null`.

5. **Decision buttons placement** — analysis/report pages render decision buttons (Add to Fleet / Pass) IN the verdict/top banner, NOT at the bottom of the page. The design spec explicitly places them in the header.

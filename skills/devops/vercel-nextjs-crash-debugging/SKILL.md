---
name: vercel-nextjs-crash-debugging
description: Diagnose and fix opaque Next.js client-side exceptions on Vercel — add diagnostic error boundaries, harden API fallbacks for serverless, fix canvas/CSP crashes, and reproduce errors with browser tools.
version: 1.0.0
---

# Vercel Next.js Crash Debugging

When a Next.js app on Vercel shows "Application error: a client-side exception has occurred while loading (see the browser console for more information)" — that's Next.js's built-in error boundary swallowing the real error. The browser console may be empty because the error is caught before it reaches `window.onerror`.

## When to Use

- "Application error: a client-side exception" on Vercel with no visible console errors
- Paste/drag-drop/image-upload causing unexplained React crashes
- Vision API or other serverless API calls silently failing in production
- Canvas or Image operations causing crashes only in production
- Need to differentiate between API failures and render crashes

## Step 1: Add Diagnostic Error Boundaries

Create two files that show the ACTUAL error instead of the generic message.

### `src/app/error.tsx` — catches errors within a route segment

```tsx
'use client';

import { useEffect, useState } from 'react';

export default function DiagnosticError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    const [showStack, setShowStack] = useState(false);

    useEffect(() => {
        console.error('Route Error Boundary caught:', error);
    }, [error]);

    return (
        <div style={{ padding: '2rem', maxWidth: 800, margin: '0 auto', fontFamily: 'monospace' }}>
            <h2 style={{ color: '#ef4444' }}>Something went wrong</h2>
            <div style={{ background: '#1a1a1a', padding: '1rem', borderRadius: 8, marginTop: '1rem' }}>
                <p style={{ color: '#f87171', fontWeight: 'bold', margin: 0 }}>
                    {error.message || 'Unknown error'}
                </p>
                {error.digest && (
                    <p style={{ color: '#6b7280', fontSize: '0.8rem', margin: '0.5rem 0 0 0' }}>
                        Digest: {error.digest}
                    </p>
                )}
            </div>
            <button
                onClick={() => setShowStack(!showStack)}
                style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#374151', color: '#d1d5db', border: 'none', borderRadius: 4, cursor: 'pointer' }}
            >
                {showStack ? 'Hide' : 'Show'} Stack Trace
            </button>
            {showStack && (
                <pre style={{ background: '#111', padding: '1rem', borderRadius: 4, marginTop: '0.5rem', color: '#9ca3af', fontSize: '0.75rem', overflow: 'auto', maxHeight: 400 }}>
                    {error.stack || 'No stack trace available'}
                </pre>
            )}
            <button
                onClick={reset}
                style={{ display: 'block', marginTop: '1rem', padding: '0.75rem 1.5rem', background: '#3b82f6', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' }}
            >
                Try Again
            </button>
        </div>
    );
}
```

### `src/app/global-error.tsx` — catches errors outside layout tree

```tsx
'use client';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <html>
            <body style={{ background: '#0a0a0a', color: '#e5e5e5', fontFamily: 'monospace', padding: '3rem' }}>
                <h1 style={{ color: '#ef4444' }}>Critical Error</h1>
                <p>{error.message}</p>
                <pre style={{ color: '#6b7280', fontSize: '0.75rem' }}>{error.stack}</pre>
                <button onClick={reset} style={{ marginTop: '1rem', padding: '0.5rem 1rem', background: '#3b82f6', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Retry</button>
            </body>
        </html>
    );
}
```

**Why this works**: Next.js automatically picks up `error.tsx` and `global-error.tsx` as React Error Boundaries. They catch any unhandled throw during rendering and show the actual error instead of the generic message.

## Step 2: Check API Routes for Serverless Failures

Common failure modes on Vercel serverless:

| Issue | Symptom | Fix |
|-------|---------|-----|
| API key not in Vercel env | 401/403 or silent failure | Set env vars in Vercel dashboard (`.env.local` doesn't deploy) |
| Ollama/Firecrawl/local services | Connection refused | These can't run on Vercel — use hosted alternatives |
| Request body too large | 413 Payload Too Large | Compress client-side before upload (Vercel has 4.5MB limit) |
| Function timeout | 504 Gateway Timeout | Vercel Pro plan extends timeout; optimize or split work |

### Multi-Tier API Fallback Pattern

For API routes that call external services (vision, AI, scraping), always implement fallback tiers:

```typescript
// Pattern: try primary → fallback → graceful error
const providers = [
    { name: 'Groq', fn: () => callGroq(image) },
    { name: 'OpenRouter', fn: () => callOpenRouter(image) },
    { name: 'Ollama', fn: () => callOllama(image) },
];

let lastError: Error | null = null;
for (const provider of providers) {
    try {
        const result = await provider.fn();
        return Response.json({ ...result, provider: provider.name });
    } catch (e) {
        lastError = e instanceof Error ? e : new Error(String(e));
        console.warn(`Provider ${provider.name} failed:`, lastError.message);
    }
}

return Response.json(
    {
        error: 'All providers exhausted',
        details: lastError?.message,
        tried: providers.map(p => p.name),
    },
    { status: 502 }
);
```

## Step 3: Harden Canvas/Image Operations

Client-side canvas operations often crash on Vercel due to CSP or browser quirks:

```typescript
const resizeImage = (file: File, maxDim: number = 1920): Promise<Blob> =>
    new Promise((resolve, reject) => {
        // Guard 1: Check Canvas API availability
        if (typeof HTMLCanvasElement === 'undefined') {
            reject(new Error('Canvas API not available (SSR or restricted env)'));
            return;
        }

        const img = new Image();
        const objectUrl = URL.createObjectURL(file);
        const timeout = setTimeout(() => {
            URL.revokeObjectURL(objectUrl);
            reject(new Error('Image load timed out after 15s'));
        }, 15000);

        img.onload = () => {
            clearTimeout(timeout);
            URL.revokeObjectURL(objectUrl);

            // Guard 2: zero-dimension check
            if (img.width === 0 || img.height === 0) {
                reject(new Error('Image has zero dimensions'));
                return;
            }

            let { width, height } = img;
            if (width > maxDim || height > maxDim) {
                const ratio = Math.min(maxDim / width, maxDim / height);
                width = Math.round(width * ratio);
                height = Math.round(height * ratio);
            }

            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;

            // Guard 3: null canvas context check
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                reject(new Error('Failed to get 2D canvas context'));
                return;
            }

            ctx.drawImage(img, 0, 0, width, height);
            canvas.toBlob(
                (blob) => {
                    if (blob) resolve(blob);
                    else reject(new Error('Canvas toBlob returned null'));
                },
                'image/jpeg',
                0.75
            );
        };

        img.onerror = () => {
            clearTimeout(timeout);
            URL.revokeObjectURL(objectUrl);
            reject(new Error(`Failed to load image: ${file.type || 'unknown type'}`));
        };

        img.src = objectUrl;
    });
```

## Step 4: Reproduce with Browser Tools

Use `browser_navigate` + `browser_console` to reproduce the error:

```
browser_navigate → https://your-site.vercel.app
browser_console → expression: install error monitoring
browser_console → expression: dispatch paste/click/drag event
browser_snapshot → check if error boundary rendered
browser_console → expression: JSON.stringify(window.__capturedErrors)
```

## Pitfalls

- **`.env.local` doesn't deploy to Vercel** — environment variables MUST be set in the Vercel dashboard (Settings → Environment Variables)
- **Vercel has a 4.5MB request body limit** — large screenshots must be compressed client-side before upload
- **`error.tsx` only catches errors within its route segment** — `global-error.tsx` catches errors outside the layout tree (root-level crashes)
- **Ollama, Firecrawl, and other local services cannot run on Vercel serverless** — use hosted alternatives or fallback tiers
- **Browser Console may be empty** even when a client-side exception occurs — Next.js's error boundary catches the error before `window.onerror` fires. Use the diagnostic error boundary instead.
- **Canvas may be undefined during SSR** — always guard with `typeof HTMLCanvasElement === 'undefined'` check

## Verification

After deploying fixes:
1. Visit the deployed site
2. Trigger the crash scenario (paste image, click button, etc.)
3. If the diagnostic error boundary appears instead of the generic message — you now have the REAL error
4. Fix the root cause shown by the diagnostic error boundary
5. The generic "Application error: a client-side exception" should no longer appear

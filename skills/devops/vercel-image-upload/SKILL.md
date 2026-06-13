---
name: vercel-image-upload
description: Patterns for handling image uploads in Next.js on Vercel serverless — avoid 413 errors and browser crashes when pasting/dropping images.
---

# Vercel Image Upload Patterns

## ⚠️ Anti-Pattern (DO NOT DO THIS)

```typescript
// ❌ BROKEN: two failure modes for large images
const buffer = await file.arrayBuffer();
const base64 = btoa(
  new Uint8Array(buffer).reduce((d, b) => d + String.fromCharCode(b), '')
);
await fetch('/api/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ image: base64 }),
});
```

**Failure mode 1 — Browser crash:** `.reduce()` on a 4M+ byte array builds a multi-megabyte string through repeated concatenation. O(n²) — the browser tab locks up or crashes before the string finishes.

**Failure mode 2 — Vercel 413:** Even if encode succeeds, base64 is 33% larger than raw binary. A 4MB PNG → ~5.3MB in JSON body → exceeds Vercel's hard 4.5MB serverless body limit. Vercel returns `413 Payload Too Large`.

Both failures are silent or show generic errors — very hard to diagnose.

## ✅ Correct Pattern

```typescript
// 1. Resize client-side before upload (Canvas API)
const resizeImage = (file: File, maxDim = 1920): Promise<Blob> =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      let { width, height } = img;
      if (width > height) {
        if (width > maxDim) { height *= maxDim / width; width = maxDim; }
      } else {
        if (height > maxDim) { width *= maxDim / height; height = maxDim; }
      }
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, width, height);
      canvas.toBlob(
        blob => blob ? resolve(blob) : reject(new Error('Canvas encode failed')),
        'image/jpeg',
        0.75
      );
    };
    img.onerror = () => reject(new Error('Image load failed'));
    img.src = URL.createObjectURL(file);
  });

// 2. Send as FormData (binary, no base64 bloat)
const blob = await resizeImage(file, 1920);
const formData = new FormData();
formData.append('image', blob, 'image.jpg');
await fetch('/api/extract', {
  method: 'POST',
  // NO Content-Type header — browser sets multipart boundary automatically
  body: formData,
});
```

## Backend (App Router)

```typescript
// route.ts — App Router handler
export async function POST(request: Request) {
  const formData = await request.formData();
  const imageFile = formData.get('image') as File | null;
  if (!imageFile) return NextResponse.json({ error: 'No image' }, { status: 400 });

  const buffer = Buffer.from(await imageFile.arrayBuffer());
  // ... use buffer with vision APIs, sharp, etc.
}
```

**DO NOT pre-parse the body** — `request.formData()` consumes the raw body stream.

## Backend (Pages Router)

```typescript
// In Pages Router, disable bodyParser for multipart routes
export const config = { api: { bodyParser: false } };

// Use a library like formidable or busboy to parse
// Or: migrate to App Router (recommended)
```

## Key Numbers

| What | Limit |
|------|-------|
| Vercel serverless body size | 4.5 MB (hard, no config override) |
| Base64 inflation | +33% over raw binary |
| Resized JPEG @1920px Q75 | ~300 KB (from 8 MB PNG source) |
| Resized JPEG @1024px Q70 | ~150 KB |

## Pitfalls

- **Vercel's 4.5MB limit is a platform limit** — `next.config.js`, `vercel.json`, and `export const runtime` do NOT affect it.
- **`btoa()` has no chunk limit but O(n²) string concat with `.reduce()` crashes browsers** — use `FileReader.readAsDataURL()` if you absolutely must base64, but prefer FormData.
- **Drop vs Paste**: both produce `File` objects. The paste path (`ClipboardEvent.clipboardData.items`) uses the same `processScreenshot(file)` function — fix once, both paths fixed.
- **Vehicle photos are fine**: they're stored client-side via `URL.createObjectURL()` and never hit the server. Only the screenshot paste/drop hits `/api/extract-listing`.
- **`resizeImage` uses `Image()` constructor** — requires browser DOM API. Does NOT work server-side or in Next.js middleware.

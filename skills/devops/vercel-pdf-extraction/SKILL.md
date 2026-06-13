---
name: vercel-pdf-extraction
description: Extract text from PDFs on Vercel serverless — 3-strategy cascade (pdfjs → pdf-parse → client-side rendering + Groq Vision OCR). Use when integrating PDF upload/analysis into a Next.js app deployed on Vercel, especially for image-based/scanned PDFs where text extraction alone fails.
---

# Vercel PDF Text Extraction — 3-Strategy Cascade

## When to use
- Building a Next.js API route that accepts PDF uploads on Vercel
- PDFs may be image-based/scanned (no embedded text objects) — e.g., CARFAX reports, invoices, receipts
- Need reliable extraction without Puppeteer/Chromium (too heavy for Vercel serverless)
- On Vercel Pro (60s timeout) or above

## The cascade

### Strategy A: pdfjs-dist text extraction
Fast path for standard digital PDFs. Use `pdfjs-dist/legacy/build/pdf.mjs` with `getTextContent()`.

**Worker preload (required on Vercel):** pdfjs-dist v4+ does a dynamic `import(/*webpackIgnore: true*/ this.workerSrc)` at runtime that fails on Vercel Lambda because the filesystem layout differs from `node_modules`. Preload the worker statically onto `globalThis` **before** calling `getDocument()`:

```typescript
import * as pdfjsWorker from 'pdfjs-dist/legacy/build/pdf.worker.mjs';
(globalThis as any).pdfjsWorker = pdfjsWorker;
```

pdfjs checks `globalThis.pdfjsWorker?.WorkerMessageHandler` (see pdf.mjs ~line 17359) and skips the broken dynamic import when the worker is preloaded. Place this at the top of your route file, outside the handler function — it must run once at module load time.

**Critical**: Don't use a raw char-count threshold. Validate the extracted text contains domain-relevant content:

```typescript
const CONTENT_MARKERS = [
  /expected_keyword/i, /another_pattern/i, /VIN/i,
  /\d{4}\s+(Toyota|Honda|Ford)/i,  // domain-specific patterns
];

function hasValidContent(text: string): boolean {
  if (text.length < 100) return false;
  const matches = CONTENT_MARKERS.filter((re) => re.test(text));
  return matches.length >= 3;  // require multiple signals
}
```

### Strategy B: pdf-parse (alternative parser)
Sometimes handles edge cases pdfjs misses. **pdf-parse v2.x uses a class-based API** — the v1 function-call pattern is dead code:

```typescript
const { PDFParse } = await import('pdf-parse');
const parser = new PDFParse({ data: buffer });
const result = await parser.getText();
console.log(`pdf-parse: ${result.text.length} chars, ${result.numpages} pages`);
```

### Strategy C: Client-side PDF rendering + AI Vision OCR (RECOMMENDED)

**`@napi-rs/canvas` does NOT reliably work on Vercel** despite shipping prebuilt binaries — it still fails at runtime with native dependency errors on Lambda. Do not use it. **Do not use Gemini** — the user strongly disfavors Google AI models.

Instead, render PDF pages to JPEGs **in the browser** using pdf.js (loaded from CDN), then send them to the backend for AI Vision OCR. This is the pattern that actually works on Vercel with zero native deps.

**Provider choice — OpenRouter `openrouter/free` (RECOMMENDED, zero cost)**:
- Auto-routes to available free vision-capable models
- More resilient than Groq — if one model rate-limits, router picks another
- Quality equivalent to Groq's Llama 4 Scout for OCR extraction
- Requires `OPENROUTER_API_KEY`, `HTTP-Referer`, and `X-Title` headers
- Falls back to Groq `llama-4-scout` if OpenRouter key is missing

**Backend API route** (`/api/analyze-carfax/route.ts`):

```typescript
// Accept client-rendered JPEGs as FormData
export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const pages = formData.getAll('pages') as File[];      // JPEG blobs from frontend
  const filename = formData.get('filename') as string;

  // Strategy A+B first (pdfjs → pdf-parse text extraction)
  const textResult = await extractText(buffer);
  if (textResult.valid) return NextResponse.json({ text: textResult.text });

  // Strategy C: Client rendered pages → AI Vision OCR
  if (pages.length > 0) {
    const visionTexts = await Promise.all(
      pages.slice(0, 12).map(async (pageFile) => {
        const pageBuffer = Buffer.from(await pageFile.arrayBuffer());
        const base64 = pageBuffer.toString('base64');
        return callVisionOCR(base64);  // OpenRouter free or Groq fallback
      })
    );
    return NextResponse.json({ text: visionTexts.join('\n\n') });
  }

  // Signal frontend to render pages if no client images sent
  return NextResponse.json({ needsVision: true, message: '...' }, { status: 422 });
}

async function callVisionOCR(base64Image: string) {
  // Primary: OpenRouter free (zero cost, auto-routes vision models)
  if (process.env.OPENROUTER_API_KEY) {
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      headers: {
        Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://www.veracar.co',
        'X-Title': 'Vehicle Analyzer Pro',
      },
      body: JSON.stringify({
        model: 'openrouter/free',
        messages: [{
          role: 'user',
          content: [
            { type: 'text', text: 'Extract all text from this page verbatim...' },
            { type: 'image_url', image_url: { url: `data:image/jpeg;base64,${base64Image}` } },
          ],
        }],
      }),
    });
    const data = await res.json();
    return data.choices[0]?.message?.content || '';
  }

  // Fallback: Groq free tier
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    headers: {
      Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'meta-llama/llama-4-scout-17b-16e-instruct',
      messages: [{
        role: 'user',
        content: [
          { type: 'text', text: 'Extract all text from this page verbatim...' },
          { type: 'image_url', image_url: { url: `data:image/jpeg;base64,${base64Image}` } },
        ],
      }],
    }),
  });
  const data = await res.json();
  return data.choices[0].message.content;
}
```

**Frontend** — pdf.js loaded from CDN (no npm dependency), renders pages to JPEGs, retries the API:

```typescript
async function renderPagesToImages(file: File): Promise<Blob[]> {
  const pdfjsLib = await loadPdfJs();  // CDN: //cdnjs.cloudflare.com/.../pdf.mjs
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

  const blobs: Blob[] = [];
  const maxPages = Math.min(pdf.numPages, 12);

  for (let i = 1; i <= maxPages; i++) {
    const page = await pdf.getPage(i);
    const viewport = page.getViewport({ scale: 1.8 });
    const canvas = document.createElement('canvas');
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    const ctx = canvas.getContext('2d')!;
    await page.render({ canvasContext: ctx, viewport }).promise;
    const blob = await new Promise<Blob>((r) => canvas.toBlob((b) => r(b!), 'image/jpeg', 0.75));
    blobs.push(blob);
  }
  return blobs;
}
```

Scale factor: 1.8. Quality: 75. Cap pages at 12. Groq Vision is free — no per-image cost. Zero native deps, works on Vercel.

## Vercel-specific requirements

### `next.config.ts`
```typescript
serverExternalPackages: ['pdf-parse'],
maxDuration: 55,  // Vercel Pro = 60s max
```

**Do NOT put `pdfjs-dist` in `serverExternalPackages`.** pdfjs-dist v4+ does a dynamic `import(/*webpackIgnore: true*/ this.workerSrc)` that fails on Vercel's Lambda filesystem when the package isn't bundled. Keep it bundled, and preload the worker (see Strategy A).

### Dependencies
```bash
npm install pdf-parse pdfjs-dist
```

**Do NOT install `canvas` or `@napi-rs/canvas`** — both require native system libraries absent on Vercel. Use client-side rendering (Strategy C) instead.

## Pitfalls
- **`@napi-rs/canvas` does NOT work on Vercel.** Despite shipping prebuilt binaries, it fails at runtime on AWS Lambda with native dependency errors. Use client-side rendering instead (Strategy C above).
- **pdfjs-dist worker on Vercel:** v4+ dynamically imports the worker file at runtime, but Vercel Lambda's filesystem can't resolve it. Preload with `(globalThis as any).pdfjsWorker = workerImport` at module scope. Do NOT put `pdfjs-dist` in `serverExternalPackages` — that makes it worse.
- **pdf-parse v2 API:** The v1 pattern `parseFn(buffer)` is dead code. v2 uses `new PDFParse({ data: buffer }).getText()`. If your project has pdf-parse ^2.x, the old pattern silently breaks.
- **Vision model choice:** Use OpenRouter `openrouter/free` as primary (zero cost, auto-routes vision-capable free models, more resilient than single-provider). Fall back to Groq `meta-llama/llama-4-scout-17b-16e-instruct` (free tier). Do NOT use Gemini for anything. Ollama with `llama3.2-vision:latest` is an alternative for local dev.
- Vision models may return no content if prompt isn't explicit about extracting ALL text
- Don't use a raw char-count threshold for text quality — validate with domain-specific content markers (Strategy A example)
- **Groq API keys can expire silently** — always prefer OpenRouter as primary. Keep Groq as fallback but don't rely on it.

## Error message best practice
When all strategies fail, tell the user WHY and what to try:
> "Could not extract text from this PDF. Try downloading the report fresh from the source — make sure 'Save as PDF' is used, not a screenshot or printed scan."

# JSON Sanitization for Vision Model Output

## Problem

LLM vision models frequently return JSON containing unescaped control characters (ASCII 0x00-0x1F). These break `JSON.parse()` with:
```
Bad control character in string literal in JSON at position 62
```

## Root Cause

Models embed raw newlines, tabs, or other control chars inside JSON string values instead of properly escaping them as `\n`, `\t`, etc. This is particularly common with free-tier vision models that auto-route through `openrouter/free`.

## Fix: `sanitizeJson()` Helper

Applied to all endpoints that parse model JSON output (`extract-listing/route.ts`, `analyze-photos/route.ts`):

```typescript
const sanitizeJson = (raw: string): string => {
    let s = raw.trim();
    // Remove markdown code fences
    s = s.replace(/```(?:json)?\s*/g, '').replace(/```/g, '');
    // Strip bad control characters that break JSON.parse (except \n, \r, \t)
    s = s.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '');
    return s.trim();
};
```

Usage:
```typescript
// BEFORE (breaks):
const parsed = JSON.parse(content.replace(/```json\n?|```/g, '').trim());

// AFTER (resilient):
const parsed = JSON.parse(sanitizeJson(content));
```

## Which Characters Are Stripped

- `\x00-\x08` — null, control chars
- `\x0B` — vertical tab
- `\x0C` — form feed
- `\x0E-\x1F` — remaining control chars

These are never valid inside JSON strings. They're either LLM hallucinations or malformatted escape sequences.

## Where To Apply

Any endpoint that calls a vision model and parses the response as JSON needs this. Currently applied to:
- `src/app/api/extract-listing/route.ts` — screenshot extraction
- `src/app/api/analyze-photos/route.ts` — photo-based vehicle identification

## Testing

If you see "Bad control character" or "Unexpected token" JSON parse errors from vision extraction, check the raw model output before parsing. The control character will be visible in the error message position.

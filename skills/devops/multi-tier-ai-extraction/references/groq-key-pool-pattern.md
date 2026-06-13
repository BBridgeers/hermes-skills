# Groq Key Pool Pattern

## Problem

Groq API keys expire silently (rate limits, TTL expiry, account suspension). A key that worked yesterday returns 401 today with no warning. If your vision extraction pipeline depends on a single Groq key, it will fail at the worst possible time.

## Solution: GROQ_API_KEY_POOL

Store multiple Groq API keys in a single env var, comma-separated:

```
GROQ_API_KEY_POOL=gsk_key1,gsk_key2,gsk_key3
```

Then iterate through them in a `for` loop. If one key returns 401 or fails, try the next:

```typescript
function getGroqKeyPool(): string[] {
    const pool = process.env.GROQ_API_KEY_POOL || process.env.GROQ_API_KEY || '';
    return pool.split(',').map(k => k.trim()).filter(k => k.startsWith('gsk_'));
}

async function extractWithGroq(image: Buffer, prompt: string): Promise<any> {
    const keys = getGroqKeyPool();
    if (keys.length === 0) throw new Error('No Groq keys');
    
    let lastError = '';
    for (const key of keys) {
        try {
            const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: 'meta-llama/llama-4-scout-17b-16e-instruct', ... }),
            });
            if (res.ok) {
                const data = await res.json();
                // Extract and return vehicle data
                return parseResult(data);
            }
            lastError = `HTTP ${res.status}`;
            console.warn('[Extract] Key failed, trying next:', lastError);
        } catch (e: any) {
            lastError = e.message;
            console.warn('[Extract] Key exception:', lastError);
        }
    }
    throw new Error(`All ${keys.length} keys failed: ${lastError}`);
}
```

## When to Use

- Screenshot/vision extraction pipelines using Groq Llama 4 Scout
- Any API-dependent feature where 401 means "try the next key"

## Pitfalls

- Keys must start with `gsk_` to pass the filter
- Don't put more than 5 keys — the serial loop gets slow
- Log which key succeeded so you know when one stops working
- The pool env var replaces `GROQ_API_KEY`, not supplements it — use `GROQ_API_KEY_POOL` as the canonical env var name

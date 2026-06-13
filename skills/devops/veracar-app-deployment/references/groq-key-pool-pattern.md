# Groq Key Pool Pattern

**Date**: 2026-06-12
**Why**: User had multiple Groq API keys — some worked, some were rate-limited, some were dead. A single-key approach fails silently.

## Pattern

```typescript
// In .env.local:
GROQ_API_KEY_POOL=gsk_ke...
// In route handler:
function getGroqKeyPool(): string[] {
    const pool = process.env.GROQ_API_KEY_POOL || process.env.GROQ_API_KEY || '';
    return pool.split(',').map(k => k.trim()).filter(k => k.startsWith('gsk_'));
}

async function callWithKeyPool(prompt: string, imageBase64: string, mime: string) {
    const keys = getGroqKeyPool();
    let lastError = '';
    
    for (const key of keys) {
        try {
            const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                headers: { 'Authorization': `Bearer ${key}`, ... },
                body: JSON.stringify({
                    model: 'meta-llama/llama-4-scout-17b-16e-instruct',
                    messages: [{ role: 'user', content: [...] }],
                }),
            });
            if (res.ok) {
                const data = await res.json();
                return data.choices[0].message.content;
            }
        } catch (e) {
            lastError = e.message;
            // Continue to next key
        }
    }
    throw new Error(`All ${keys.length} keys failed. Last: ${lastError}`);
}
```

## Why Not Single Key

- Groq rate-limits per key (requests per minute)
- Keys can temporarily fail with 429/503
- One dead key in a pool of 3 = the other 2 still work
- User can rotate keys without code changes — just update the env var

## Pitfalls

- Don't validate keys preemptively — security redaction in the Hermes runtime prevents direct API key testing. Trust the user and let runtime errors surface issues.
- Pool is a comma-separated string, not JSON array. No brackets. `key1,key2,key3` not `["key1","key2","key3"]`.

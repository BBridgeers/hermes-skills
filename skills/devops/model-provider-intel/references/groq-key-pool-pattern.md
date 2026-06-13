# Groq Key Pool Pattern — Multi-Key API Fallback

## Pattern

When a single API key may be rate-limited, expired, or out of credits, pool multiple keys and try them sequentially until one succeeds. This pattern applies to any bearer-token API (Groq, OpenRouter, DeepSeek) but is most critical for Groq because:
- Groq keys expire silently without notification  
- Groq has no "credit balance" endpoint to check before calling
- The user may have multiple valid keys from different signups/promotions

## Protocol

### 1. Store keys as a pooled env var

```bash
# In .env.local or systemd EnvironmentFile
GROQ_API_KEY_POOL=gsk_key1,gsk_key2,gsk_key3
```

Keep a flat `GROQ_API_KEY` as fallback for tools that expect a single key.

### 2. Read pool with parser

```typescript
function getGroqKeyPool(): string[] {
    const pool = process.env.GROQ_API_KEY_POOL || process.env.GROQ_API_KEY || '';
    return pool.split(',').map(k => k.trim()).filter(k => k.startsWith('gsk_'));
}
```

### 3. Iterate through keys

```typescript
let lastError = '';
for (const key of getGroqKeyPool()) {
    try {
        const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ model, messages, ... }),
        });

        if (res.ok) {
            const data = await res.json();
            // use data — break on success
            break;
        }
        lastError = `HTTP ${res.status}`;
        console.warn('[Pool] Key failed, trying next:', lastError);
    } catch (e: any) {
        lastError = e.message;
        console.warn('[Pool] Key exception, trying next:', lastError);
    }
}
if (!result) throw new Error(`All ${keys.length} keys failed. Last: ${lastError}`);
```

### 4. Report which key succeeded

```typescript
// Mask key for logging: gsk_O0c...LkJ
const masked = key.slice(0, 7) + '...' + key.slice(-3);
console.log(`[Pool] Key ${masked} succeeded`);
```

## When to Apply

- Vision extraction endpoints that depend on Groq `llama-4-scout-17b-16e-instruct`
- Any production endpoint where Groq key failure would block the user
- Cron jobs that batch-process vision tasks

## Alternatives (when key pool is exhausted)

1. **OpenRouter free tier** — `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` etc. User may reject if they've had negative experiences with free model reliability.
2. **Ask user for replacement keys** — user may have multiple Groq accounts from different signups. Always ask before switching providers.

## Pitfalls

- **Do NOT validate keys at startup.** Security redaction prevents reading the env var in logs/output. Just deploy with the key and let runtime handle failures — errors surface naturally in the app logs.
- **Do NOT switch providers preemptively.** When the user says a key is valid, USE it. Don't second-guess with silent validation tests.
- **Rate limits compound.** Multiple keys doesn't mean 3x throughput — keys share the same IP and Groq applies IP-level rate limiting.
- **Key pool ≠ key rotation.** The pool tries keys sequentially, not round-robin. First key always gets tried first. If first key is consistently rate-limited, the second key will always work — but the pool logic doesn't learn this. Consider periodically shuffling the pool if rate limits persist on one key.
- **Store the pool in one env var, not separate vars.** `GROQ_API_KEY_1`, `GROQ_API_KEY_2`, `GROQ_API_KEY_3` would require code changes to add/remove keys. A comma-separated pool is self-documenting and trivially updatable.

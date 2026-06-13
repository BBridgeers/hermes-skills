# Rate limiting upgrade — per-user (not per-IP)
# Updated function signature: rateLimit(key, maxRequests, windowSeconds, userId)

export async function rateLimit(
    key: string,
    maxRequests: number,
    windowSeconds: number,
    userId: string
): Promise<{ allowed: boolean; remaining: number; resetAt: number }> {
    const now = Date.now();
    const windowMs = windowSeconds * 1000;
    const prefixedKey = `${userId}:ratelimit:${key}`;
    
    const count = await kv.incr(prefixedKey);
    
    if (count === 1) {
        await kv.expire(prefixedKey, windowSeconds);
    }

    const resetAt = now + (await kv.ttl(prefixedKey)) * 1000;

    if (count > maxRequests) {
        return { allowed: false, remaining: 0, resetAt };
    }

    return { allowed: true, remaining: maxRequests - count, resetAt };
}
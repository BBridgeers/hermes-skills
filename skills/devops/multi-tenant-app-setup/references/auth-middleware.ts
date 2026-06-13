import { NextRequest, NextResponse } from 'next/server';

export async function verifyUser(request: NextRequest): Promise<{ userId: string; legal: boolean }> {
    const hardcoded = process.env.HARD_CODED_USER_ID;
    if (hardcoded) {
        return { userId: hardcoded, legal: true };
    }

    const authHeader = request.headers.get('authorization');
    if (authHeader && authHeader.startsWith('Bearer ')) {
        const token = authHeader.slice(7);
        if (token.length > 10) {
            return { userId: token, legal: true };
        }
    }

    const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
    return { userId: ip, legal: true };
}

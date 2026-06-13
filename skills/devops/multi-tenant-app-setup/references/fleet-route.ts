import { NextResponse } from 'next/server';
import { kv } from '@/lib/kv';
import { rateLimitByUser, EXTRACT_LIMIT } from '@/lib/rate-limit';
import { getCurrentUserId } from '@/lib/kv-user-wrapper';

const FLEET_KEY = 'fleet';

export async function GET(req: Request) {
    const userId = await getCurrentUserId(req);
    const fleet = await kv.get(`${userId}:${FLEET_KEY}`) || [];
    return NextResponse.json(fleet);
}

export async function POST(req: Request) {
    const userId = await getCurrentUserId(req);
    
    const rateCheck = await rateLimitByUser(
        'fleet_create',
        EXTRACT_LIMIT.max,
        EXTRACT_LIMIT.windowSec,
        userId
    );
    
    if (!rateCheck.allowed) {
        return NextResponse.json(
            { error: `Rate limit exceeded. Try again in ${Math.ceil((rateCheck.resetAt - Date.now()) / 1000)} seconds.` },
            { status: 429 }
        );
    }

    const vehicle = await req.json();
    const fleet: any[] = await kv.get(`${userId}:${FLEET_KEY}`) || [];
    
    const newEntry = {
        ...vehicle,
        id: vehicle.id || Date.now(),
        createdAt: new Date().toISOString(),
    };
    
    fleet.unshift(newEntry);
    if (fleet.length > 100) {
        fleet.length = 100;
    }
    
    await kv.set(`${userId}:${FLEET_KEY}`, fleet);
    return NextResponse.json({ success: true, vehicle: newEntry });
}

export async function DELETE(req: Request) {
    const userId = await getCurrentUserId(req);
    const { id } = await req.json();
    const fleet: any[] = await kv.get(`${userId}:${FLEET_KEY}`) || [];
    const updatedFleet = fleet.filter(v => v.id !== id);
    await kv.set(`${userId}:${FLEET_KEY}`, updatedFleet);
    return NextResponse.json({ success: true });
}

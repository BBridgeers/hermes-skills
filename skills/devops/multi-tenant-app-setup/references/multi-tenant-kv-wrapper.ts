import { Redis } from '@upstash/redis';

const USER_PREFIX = (uid: string) => `user:${uid}:`;

export function userKv(uid: string, kv: Redis): {
  set: (key: string, val: any, opts?: any) => Promise<any>;
  get: (key: string) => Promise<any>;
  del: (key: string) => Promise<any>;
  incr: (key: string) => Promise<number>;
  hset: (key: string, data: any) => Promise<any>;
  hget: (key: string, field: string) => Promise<any>;
  zadd: (key: string, data: any) => Promise<any>;
  zrange: (key: string, start: number, end: number) => Promise<any>;
} {
  const prefix = USER_PREFIX(uid);

  return {
    set: (key: string, val: any, opts?: any) => kv.set(prefix + key, val, opts),
    get: (key: string) => kv.get(prefix + key),
    del: (key: string) => kv.del(prefix + key),
    incr: (key: string) => kv.incr(prefix + key),
    hset: (key: string, data: any) => kv.hset(prefix + key, data),
    hget: (key: string, field: string) => kv.hget(prefix + key, field),
    zadd: (key: string, data: any) => kv.zadd(prefix + key, data),
    zrange: (key: string, start: number, end: number) => kv.zrange(prefix + key, start, end),
  };
}

export async function getCurrentUserId(request?: Request): Promise<string> {
  return process.env.HARD_CODED_USER_ID || 'demo';
}

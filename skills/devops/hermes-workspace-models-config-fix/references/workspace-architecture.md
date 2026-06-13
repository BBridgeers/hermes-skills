# Workspace Architecture — May 18, 2026 Analysis

## Workspace is TanStack Start SSR, not Next.js static export

The workspace image (ghcr.io/outsourc-e/hermes-workspace) runs a Node.js HTTP server
via `node server-entry.js` that imports the TanStack Start fetch handler from
`dist/server/server.js`. It is NOT a static export. Version: 2.3.0.

## How the workspace connects to the agent

### Gateway capabilities probe (gateway-capabilities.ts)

On startup, the workspace probes the agent to detect which APIs are available:

- Core: `/health`, `/v1/chat/completions`, `/v1/models` → CoreCapabilities
- Dashboard: `/api/sessions`, `/api/skills`, `/api/config`, `/api/jobs` → EnhancedCapabilities
- Dashboard service probe: `/api/status` on port 9119 → DashboardCapabilities

The probe sets boolean flags (health, models, config, sessions, etc.) that gate
feature availability throughout the UI.

### Connection modes:
- 'zero-fork': dashboard available + chat completions working
- 'portable': chat completions or health present (no dashboard)
- 'disconnected': nothing reachable

## How /api/models works (models.ts route handler)

Priority order:
1. Read `~/models.json` (local file)
2. Extract default model from `~/config.yaml` (YAML parser, handles flat and nested formats)
3. If `getGatewayCapabilities().models` is true, fetch from agent's `/v1/models` and merge
4. Run local provider discovery (Ollama, Atomic Chat, etc.) and merge
5. Return merged deduplicated list + configured providers + stream timeouts

The merge uses `mergeModelEntries()` which deduplicates by model ID.

## How /api/claude-config works (claude-config.ts route handler)

1. Auth check (workspace session cookie)
2. Capability gate: `if (!getCapabilities().config) { return capabilityUnavailablePayload }`
3. Reads `config.yaml` directly from the workspace container's filesystem
4. Reads `.env` directly from the workspace container's filesystem
5. Builds provider status from hardcoded PROVIDERS array + env key detection

**This is the config parity problem**: step 3 reads from the workspace's OWN
filesystem, not from the agent. In Docker, the workspace container has an empty
`~/.hermes/` while the agent has the real config mounted at `/opt/data/config.yaml`.

## There IS a proxy function that doesn't get used

`claude-api.ts` exports `getConfig()` which proxies through the dashboard:
```typescript
export async function getConfig(): Promise<any> {
  if (getCapabilities().dashboard.available) {
    const res = await dashboardFetch('/api/config')
    ...
  }
  return claudeGet('/api/config')
}
```

But the `/api/claude-config` route handler does NOT use this — it reads the
filesystem directly. This is by design for local desktop usage where both
agent and workspace share the same `~/.hermes/` directory.

## Dashboard token scrape

The workspace authenticates to the dashboard by scraping the session token from
the dashboard's root HTML page. The dashboard injects a fresh ephemeral token at boot:

```
window.__CLAUDE_SESSION_TOKEN__ = "..."
```

The workspace caches this token and uses it for authenticated dashboard API calls
via `dashboardFetch()`.

## Key files

- `src/routes/api/models.ts` — /api/models handler
- `src/routes/api/claude-config.ts` — /api/config handler (reads local filesystem)
- `src/server/gateway-capabilities.ts` — probe + capability state
- `src/server/claude-api.ts` — agent API client + proxy helpers
- `src/server/claude-dashboard-api.ts` — dashboard API client
- `server-entry.js` — Node HTTP server wrapper (TLS-unaware, behind reverse proxy)

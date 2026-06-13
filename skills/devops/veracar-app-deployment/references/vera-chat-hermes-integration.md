# VERA Chat 2.0 — Hermes-Powered Architecture

Built 2026-06-12. VERA is an omniscient in-app debug co-pilot embedded in veracar.co,
powered by the Hermes Agent API server running on the same VPS.

## Data Flow

```
veracar.co (Next.js :3001)
  └─ ChatWidget.tsx (floating button, bottom-right)
       └─ ChatWrapper.tsx (root layout, passes usePathname())
            └─ /api/chat (Next.js API route)
                 └─ Hermes API (:8642/v1/chat/completions)
                      └─ Full Hermes Agent stack
                           ├── 350+ skills
                           ├── Terminal (root VPS)
                           ├── Browser automation
                           ├── Code editing (patch, write_file)
                           ├── Deep research agents
                           └── All providers (DeepSeek, OpenRouter, etc.)
```

## Key Files

| File | Role |
|---|---|
| `src/components/ChatWidget.tsx` | Floating chat panel — VERA 2.0 UI with `⚡HERMES` badge, `🛠 Debug` toggle, page indicator, improvement suggestions |
| `src/components/ChatWrapper.tsx` | Client wrapper in root layout — reads `usePathname()`, passes to ChatWidget via `dynamic()` with `ssr: false` |
| `src/app/layout.tsx` | Root layout — imports `<ChatWrapper />` after `{children}` |
| `src/app/api/chat/route.ts` | API proxy — maps messages to Hermes format, injects `[CURRENT PAGE: /path]` into user messages, streams SSE back |
| `src/lib/chat-context.ts` | System prompt builder — `buildDebugPrompt()` (omniscient app architecture), `buildSystemPrompt()` (vehicle+analysis), page-aware context |

## Modes

### Normal Mode (vehicle loaded)
- System prompt includes full vehicle data + analysis results + app architecture
- VERA answers vehicle questions, negotiation strategy, rideshare math, etc.
- Proactive follow-up suggestions + forward-producing improvements

### Debug Mode (`🛠 Debug` toggle)
- Omniscient app architecture prompt — VERA knows every component, page, API route, data field
- First-pass completion: diagnose + fix in one response
- Can edit source code, restart services, check logs (Hermes-powered)
- `buildDebugPrompt()` injects full `APP_ARCHITECTURE` constant (17KB)

### General Mode (no vehicle, no debug)
- Uses `buildDebugPrompt()` with "DEBUG MODE: ACTIVE" replaced by "GENERAL MODE (no vehicle loaded)"
- VERA still works — can discuss app issues, ask general questions
- No vehicle context, but full app architecture knowledge

## Always-On Design (Critical)

**VERA is always available.** The input is never disabled, the send button is never gated behind `hasContext`. Key decisions:

- `disabled={isStreaming}` — only blocked during active streaming, never by vehicle state
- `placeholder` changes contextually but input ALWAYS accepts text
- No `!hasContext` guard in `sendMessage()` — removed 2026-06-12 after user frustration
- System prompt adapts: has vehicle → full analysis prompt, no vehicle → general omniscient prompt

**Pitfall**: The original ChatWidget had `if (!hasContext) return` and a "Scan a vehicle to activate VERA..." placeholder. This is the WRONG pattern. VERA must always be available.

## System Prompt Architecture

The `APP_ARCHITECTURE` constant in `chat-context.ts` is a 17KB knowledge base containing:
- Every page and its components/data flow
- Every API route
- Key component directory with file paths
- Data types (Vehicle, AnalysisResult, ScraperResult)
- State management (VehicleContext, useVehicle hook)
- Styling conventions
- Deployment architecture

This is injected into ALL system prompts so VERA is always omniscient about the codebase.

## Forward-Producing Suggestions

VERA ends every response with optional improvement suggestions formatted as:
```
💡 Improve: ["suggestion 1", "suggestion 2"]
```

These are parsed by `parseFollowUps()` and rendered in purple in the chat UI under "💡 Forward-Producing".

## API Proxy Details

The `/api/chat` endpoint:
1. Accepts `messages` (Gemini-style with `parts[]`), `systemPrompt`, `pagePath`, `debugMode`
2. Maps to Hermes format: `role: "user"/"assistant"`, `content: string`
3. Injects `[CURRENT PAGE: /path]` prefix into last user message
4. Forwards to `http://127.0.0.1:8642/v1/chat/completions` with `model: "hermes-agent"`
5. Streams SSE chunks back: `data: {"text":"..."}\n\n` + `data: [DONE]\n\n`
6. Temperature: 0.3 (debug mode) / 0.7 (normal mode)
7. Max tokens: 4096

Required env var (in `.env.local`):
```
HERMES_API_KEY=***  # Hermes API server auth key
```

## Deployment Notes

- ChatWidget is loaded via `dynamic(() => import(...), { ssr: false })` — prevents SSR bailout
- ChatWrapper is in root layout AFTER `{children}` — appears on every page
- The floating button renders when chat is closed: `fixed bottom-6 right-6 z-50`
- Chat panel: `width: 420px, height: 600px, maxHeight: calc(100vh - 48px)`

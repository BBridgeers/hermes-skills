# SwarmRosterWorkerSchema — Complete Zod Definition

From `/root/hermes-workspace/src/server/swarm-roster.ts` as of 2026-05-21.

```typescript
const WORKER_ID_PATTERN = /^(swarm\d+|[a-z][a-z0-9]*(?:-[a-z0-9]+)*)$/i

const WorkerIdSchema = z
  .string()
  .trim()
  .regex(WORKER_ID_PATTERN, 'worker id must look like swarm13 or a semantic profile id')

export const SwarmRosterWorkerSchema = z.object({
  id: WorkerIdSchema,                                    // REQUIRED
  name: z.string().default(''),                          // Display name
  role: z.string().default('Worker'),                    // Role label
  specialty: z.string().default(''),                     // Focus area
  model: z.string().default('Worker'),                   // Model ID
  mission: z.string().default('Awaiting orchestrator dispatch.'),
  profile: WorkerIdSchema.optional(),                    // Profile dir name
  modes: z.array(z.string()).default([]),                // Launch modes
  tools: z.array(z.string()).default([]),                // Tool names
  skills: z.array(z.string()).default([]),               // Skill names
  plugins: z.array(z.string()).default([]),              // Plugin names
  pluginToolsets: z.array(z.string()).default([]),       // Plugin toolset names
  mcpServers: z.array(z.string()).default([]),           // MCP server names
  wrapper: z.string().optional(),                        // Wrapper in ~/.local/bin/
  capabilities: z.array(z.string()).default([]),         // Capability tags
  defaultCwd: z.string().optional(),                     // Default working dir
  preferredTaskTypes: z.array(z.string()).default([]),   // Task type tags
  greenlightRequiredFor: z.array(z.string()).default([]),// Actions needing approval
  maxConcurrentTasks: z.number().int().positive().default(1),
  acceptsBroadcast: z.boolean().default(true),
  reviewRequired: z.boolean().default(false),
})

// NOTE: systemPrompt is NOT in this schema.
// The frontend POSTs it but Zod strips it silently.
// See SKILL.md "The System Prompt Gap" section for workarounds.
```

## ROLE_PRESETS Type

```typescript
type RolePreset = {
  role: string
  specialty: string
  mission: string
  systemPrompt: string
  skills: Array<string>
  defaultModel?: string
}
```

Presets are hardcoded in `swarm2-screen.tsx` lines 242-330. They are NOT stored on disk and NOT configurable without editing the frontend source.

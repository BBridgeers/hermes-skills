---
name: antigravity-hermes-mcp
description: Integrate Hermes Agent into Google Antigravity IDE via MCP (Model Context Protocol). Exposes Hermes as a tool provider so Antigravity can delegate tasks to the agent running on the VPS.
version: 1.0.0
---

# Antigravity ↔ Hermes MCP Integration

Integrates Hermes Agent (VPS) into Google Antigravity IDE via MCP over SSH stdio.

## Architecture

```
Antigravity (Windows) ──SSH──▶ VPS ──docker exec──▶ Hermes Agent
                                    │
                            /opt/hermes-mcp-bridge.py
                            /opt/hermes-mcp-venv/
```

The bridge is a Python MCP server that exposes Hermes' capabilities as MCP tools. Antigravity connects via SSH stdio — no open ports, no HTTP server.

## Prerequisites

- Hermes Agent running on VPS (docker container)
- SSH key-based auth from local machine to VPS
- Python 3.12+ and `uv` on VPS host

## Deploy the Bridge (VPS Side)

### 1. Create the MCP server script

Write `/opt/hermes-mcp-bridge.py`:

```python
#!/usr/bin/env python3
"""Hermes MCP Bridge — exposes Hermes Agent as an MCP server."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("hermes-bridge")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="hermes_task",
            description=(
                "Delegate a task to Hermes, the autonomous AI agent on the VPS. "
                "Hermes has terminal, filesystem, web, and coding capabilities. "
                "Be specific — provide file paths, error messages, and constraints."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "The task description."
                    }
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="hermes_status",
            description="Check health and status of Hermes agent and VPS.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hermes_task":
        task = arguments.get("task", "")
        if not task:
            return [TextContent(type="text", text="Error: no task provided.")]
        proc = await asyncio.create_subprocess_exec(
            "docker", "exec", "hermes-agent-s8t0-hermes-agent-1",
            "hermes", "chat", "-q", task, "-Q", "--yolo", "--source", "tool",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        if proc.returncode != 0 and proc.returncode != 134:
            return [TextContent(type="text",
                text=f"Exit {proc.returncode}.\n{stdout.decode()}\n{stderr.decode()}")]
        return [TextContent(type="text", text=stdout.decode())]
    elif name == "hermes_status":
        proc = await asyncio.create_subprocess_exec(
            "docker", "exec", "hermes-agent-s8t0-hermes-agent-1",
            "hermes", "status",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        return [TextContent(type="text", text=stdout.decode())]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Create SSH wrapper

Write `/opt/hermes-mcp-bridge.sh`:

```bash
#!/bin/bash
exec /opt/hermes-mcp-venv/bin/python /opt/hermes-mcp-bridge.py
```

Make executable: `chmod +x /opt/hermes-mcp-bridge.sh`

### 3. Set up venv with mcp SDK

```bash
uv venv /opt/hermes-mcp-venv --python 3.12
uv pip install --python /opt/hermes-mcp-venv/bin/python mcp
```

### 4. Verify locally

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' | /opt/hermes-mcp-venv/bin/python /opt/hermes-mcp-bridge.py
```

Should return a valid JSON-RPC initialize response.

## Configure Antigravity (Local Machine)

### Windows

File: `C:\Users\<username>\.gemini\antigravity\mcp_config.json`

Add the `hermes` block inside `mcpServers`:

```json
"hermes": {
  "command": "ssh",
  "args": [
    "-o", "StrictHostKeyChecking=accept-new",
    "root@VPS_IP",
    "/opt/hermes-mcp-bridge.sh"
  ]
}
```

### Linux/macOS

File: `~/.gemini/antigravity/mcp_config.json`

Same config as above.

### SSH Key Setup (Windows)

Antigravity runs MCP non-interactively — password prompts cause `context deadline exceeded`.

```powershell
# Generate key (if needed)
ssh-keygen -t ed25519

# Copy to VPS
type C:\Users\yoga\.ssh\id_rsa.pub | ssh root@VPS_IP "cat >> ~/.ssh/authorized_keys"

# Verify passwordless
ssh root@VPS_IP echo OK
```

## Exposed Tools

| Tool | Description |
|------|-------------|
| `hermes_task` | Delegate any task — code, terminal, files, web, research |
| `hermes_status` | VPS health check (docker status, uptime, disk) |

## Key Design Decisions

- **`--yolo` flag**: Required. Without it, Hermes prompts for confirmation on dangerous commands. Since MCP runs non-interactively, those prompts hang forever.
- **`--source tool`**: Tags sessions so they don't clutter the user's interactive session list.
- **Exit code 134**: SIGABRT — normal Hermes cleanup. Not an error.
- **Stdio over SSH**: No open ports. Antigravity spawns `ssh` as a child process and communicates over stdin/stdout. More secure than HTTP.
- **Venv over `uv run --with`**: Faster startup. `uv run --with mcp` installs deps on every invocation (2-5s delay). A persistent venv is instant.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `context deadline exceeded` | Password prompt blocks MCP | Set up SSH key auth |
| Hermes listed but no tools | Bridge crashed on init | Run `/opt/hermes-mcp-bridge.sh` manually, check for tracebacks |
| `Host key verification failed` | New host key | Use `-o StrictHostKeyChecking=accept-new` in args |
| Tasks hang forever | Missing `--yolo` flag | Ensure `--yolo` in the `hermes chat` args |
| `exit code 134` in response | Normal SIGABRT | Ignore it — exit 134 is expected cleanup |

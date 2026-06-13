---
name: hermes-mcp-bridge
description: Expose Hermes Agent as an MCP server so AI-capable IDEs (Antigravity, VS Code, Zed, etc.) can delegate tasks to it. Builds a Python MCP bridge that wraps `hermes chat -q` non-interactive mode over SSH stdio transport — no open ports required.
version: 1.0.0
---

# Hermes MCP Bridge — IDE Integration

Build an MCP server that wraps Hermes' non-interactive chat mode so AI-capable IDEs can delegate tasks to a Hermes agent on a remote VPS.

## When to Use

- User wants to integrate their VPS Hermes agent into Antigravity, VS Code, Zed, or any MCP-capable IDE
- User needs full terminal/filesystem/web access from within their IDE's AI panel
- User wants to avoid opening additional ports (SSH stdio is the transport)

## Architecture

```
IDE (Antigravity) ──SSH stdio──► VPS host ──docker exec──► Hermes container
                  MCP protocol              bridge.py        hermes chat -q
```

The bridge runs on the VPS host (not inside the container) so it survives container rebuilds. It calls `docker exec ... hermes chat -q` for each task.

## Key Hermes CLI Flags

```
hermes chat -q "TASK"   # Non-interactive single query
            -Q          # Quiet mode — suppress banner/spinner/tool previews
            --yolo      # Skip dangerous-command confirm prompts (required for unattended)
            --source tool  # Tag session as tool-originated (excluded from user session lists)
```

Exit code 134 (SIGABRT) is normal — Hermes sends itself SIGABRT during cleanup. Treat as success.

## Prerequisites

- Hermes agent running in Docker on the VPS
- SSH key access from the IDE host to the VPS
- Python 3.12+ on the VPS host
- `uv` installed on the VPS host (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Deployment Steps

### 1. Create the MCP Bridge Script

Save to `/opt/hermes-mcp-bridge.py` on the VPS host:

```python
#!/usr/bin/env python3
"""
Hermes MCP Bridge — exposes Hermes Agent as an MCP server for IDE integration.
"""

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
                "Delegate a task to Hermes, the autonomous AI agent running on the VPS. "
                "Hermes has full terminal access (bash, docker, git, ssh), file system "
                "read/write, web search and browsing, code execution, and project management "
                "capabilities. Be specific — provide file paths, error messages, and constraints."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The task description."}
                },
                "required": ["task"]
            }
        ),
        Tool(
            name="hermes_status",
            description="Check the health and status of the Hermes agent and VPS.",
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
            "docker", "exec", "HERMES_CONTAINER",
            "hermes", "chat", "-q", task, "-Q", "--yolo", "--source", "tool",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        if proc.returncode != 0 and proc.returncode != 134:
            return [TextContent(type="text",
                text=f"Hermes exited with code {proc.returncode}.\n\n{stdout.decode()}\n\nSTDERR:\n{stderr.decode()}")]
        return [TextContent(type="text", text=stdout.decode())]

    elif name == "hermes_status":
        proc = await asyncio.create_subprocess_exec(
            "docker", "exec", "HERMES_CONTAINER", "hermes", "status",
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

Replace `HERMES_CONTAINER` with the actual container name (e.g., `hermes-agent-s8t0-hermes-agent-1`).

### 2. Create the SSH Wrapper

Save to `/opt/hermes-mcp-bridge.sh`:

```bash
#!/bin/bash
exec /opt/hermes-mcp-venv/bin/python /opt/hermes-mcp-bridge.py
```

`chmod +x /opt/hermes-mcp-bridge.sh`

### 3. Set Up the Python venv

```bash
uv venv /opt/hermes-mcp-venv --python 3.12
uv pip install --python /opt/hermes-mcp-venv/bin/python mcp
```

Use a dedicated venv (not `uv run --with mcp` each time) for instant startup. `uv run --with` reinstalls dependencies on every invocation, adding 2-5s latency the IDE will feel.

### 4. IDE MCP Config

For **Antigravity**: `~/.gemini/antigravity/mcp_config.json`

```json
{
  "mcpServers": {
    "hermes": {
      "command": "ssh",
      "args": [
        "-o", "StrictHostKeyChecking=accept-new",
        "root@VPS_IP",
        "/opt/hermes-mcp-bridge.sh"
      ]
    }
  }
}
```

For **VS Code / Zed** (ACP adapter): the config format may differ — check IDE docs. The pattern is the same: SSH + stdio bridge.

### 5. Verify

Restart the IDE. The agent panel should show `hermes_task` and `hermes_status` tools. Test:

> "Use hermes_task: Say hello from the IDE bridge."

## Troubleshooting

### Bridge not connecting

- Check SSH: `ssh root@VPS_IP /opt/hermes-mcp-bridge.sh` should wait for stdin (it's an MCP server)
- Check venv: `/opt/hermes-mcp-venv/bin/python -c "import mcp"` should succeed
- Check container: `docker ps | grep hermes` should show running

### Task times out

- Default timeout is 300s. Complex tasks (builds, large code generation) may need more.
- Increase the `timeout` parameter in `asyncio.wait_for(proc.communicate(), timeout=NNN)`

### Hermes hangs on confirm prompts

- Ensure `--yolo` is in the `hermes chat` arguments. Without it, Hermes will prompt for dangerous command confirmation and hang forever (no interactive terminal).

### Container rebuilds break the bridge

- The bridge runs on the VPS **host**, not inside the container. It calls `docker exec` to reach Hermes. As long as the container name stays the same, the bridge survives rebuilds.
- If the container name changes, update `HERMES_CONTAINER` in the bridge script.

## Pitfalls

- **Don't use `hermes mcp serve`** — it only exposes messaging-gateway tools (read conversations), not agent tools. Build the bridge instead.
- **Don't pipe JSON through `echo` for testing** — shell quoting breaks. Use a Python subprocess client.
- **`uv run --with mcp` adds startup latency** — the IDE reconnects on restart and the delay is noticeable. Use a dedicated venv.
- **Exit code 134 is normal** — Hermes sends SIGABRT to itself during cleanup. Don't treat it as an error.

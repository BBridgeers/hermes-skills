# honcho-backend.env Location and Purpose

The file at `/opt/data/honcho-backend.env` inside the Hermes container is a staged
copy of the Honcho API backend config. It lives alongside `honcho.json` in the
bind-mounted `/opt/data` directory, making it visible to the agent for in-session
editing without requiring host access.

## Deployment flow

1. Agent edits `/opt/data/honcho-backend.env` during a session
2. User copies it to the host: `cp /root/.hermes/honcho-backend.env /root/honcho/.env`
   (the bind-mount maps `~/.hermes` to `/opt/data` inside the container)
3. User pastes their real OpenRouter API key into `/root/honcho/.env`
4. User recreates Honcho containers: `cd /root/honcho && docker compose up -d api deriver`
5. After deployment, the staged copy should be updated to match

## Free model selection (as of May 2026)

| Role | Model | Provider | Cost |
|---|---|---|---|
| Text (all) | `x-ai/grok-4.1-fast:free` | OpenRouter | Free |
| Embedding | `nvidia/llama-nemotron-embed-vl-1b-v2:free` | OpenRouter | Free |

## Container limitation: cannot restart Honcho from inside Hermes

The Hermes container has no Docker socket access and is on `network_mode: host`.
It CAN reach the Honcho API at `http://honcho-api-1:8000` (through shared Docker
networks) but CANNOT restart Honcho containers. All container lifecycle
operations must be done on the host.

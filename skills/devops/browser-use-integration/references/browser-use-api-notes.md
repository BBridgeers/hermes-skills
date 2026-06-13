# Browser-Use API Discovery Notes — June 2026

## Version: 0.12.9

Installed via: `pip install browser-use`

## Key Exports

```
browser_use.__init__:
  Agent, CONFIG, base_subprocess, config, logger, logging_config, setup_logging

browser_use.browser:
  BrowserProfile, BrowserSession, cloud, events, profile, session, views

browser_use.agent:
  Agent (main class), service module
```

## Agent.__init__ Signature (key params)

```python
Agent(
    task: str,                          # Required — natural language task
    llm: BaseChatModel | None = None,   # Uses ChatBrowserUse if None (needs BROWSER_USE_API_KEY)
    browser_profile: BrowserProfile | None = None,
    browser_session: BrowserSession | None = None,  # Use for CDP connection
    browser: None,                      # Deprecated? Accepts None
    tools: None,
    controller: None,
    use_vision: True,                   # Auto-disabled for DeepSeek
    max_failures: 5,
    max_actions_per_step: 5,
    use_thinking: True,
    flash_mode: False,
    step_timeout: 180,
    llm_timeout: None,
    enable_planning: True,
    loop_detection_enabled: True,
    message_compaction: True,
    enable_signal_handler: True,
)
```

## BrowserSession.__init__ Signature (key params)

```python
BrowserSession(
    id: None,
    cdp_url: None,                      # WebSocket URL from Browserbase
    is_local: False,                    # False for remote CDP
    browser_profile: None,
    cloud_profile_id: None,             # For browser-use cloud
    cloud_proxy_country_code: ...,
    cloud_timeout: None,
    use_cloud: None,                    # Alternative to cdp_url for browser-use cloud
    cloud_browser: None,
    keep_alive: None,
    proxy: None,
    captcha_solver: None,               # Could integrate CapSolver here
    minimum_wait_page_load_time: None,
    wait_for_network_idle_page_load_time: None,
    wait_between_actions: None,
    highlight_elements: None,
    viewport: None,
    ...
)
```

## LLM Providers (browser_use.llm)

All native providers live under `browser_use.llm.<provider>.chat`:

| Module | Class | Status |
|--------|-------|--------|
| `browser_use.llm.deepseek.chat` | `ChatDeepSeek` | ✅ TESTED |
| `browser_use.llm.openai.chat` | `ChatOpenAI` | Available |
| `browser_use.llm.anthropic.chat` | `ChatAnthropic` | Available |
| `browser_use.llm.google.chat` | ? | Available |
| `browser_use.llm.mistral.chat` | ? | Available |
| `browser_use.llm.groq.chat` | ? | Available |
| `browser_use.llm.azure.chat` | ? | Available |
| `browser_use.llm.cerebras.chat` | ? | Available |
| `browser_use.llm.vercel.chat` | ? | Available |

**All providers extend `browser_use.llm.base.BaseChatModel`** — NOT langchain's BaseChatModel.
langchain-openai's `ChatOpenAI` will fail with `'ChatOpenAI' object has no attribute 'provider'`.

## ChatDeepSeek.__init__

```python
ChatDeepSeek(
    model: str = "deepseek-chat",
    max_tokens: None,
    temperature: None,
    top_p: None,
    seed: None,
    api_key: None,
    base_url: str = "https://api.deepseek.com/v1",
    timeout: None,
    client_params: None,
)
```

## Browserbase Session Creation

```python
POST https://api.browserbase.com/v1/sessions
Headers: X-BB-API-Key: <key>
Body: {
    "projectId": "<project_id>",
    "browserSettings": {
        "timeout": 300,
        "fingerprint": {"screen": {"maxWidth": 1920, "maxHeight": 1080}}
    },
    "keepAlive": true
}
Response: {
    "id": "session-uuid",
    "connectUrl": "wss://connect.usw2.browserbase.com/?signingKey=...",
    "liveViewUrl": "https://browserbase.com/sessions/uuid",
    "status": "CREATED"
}
```

## Known Issues

1. **DeepSeek + Vision**: `use_vision=True` is auto-set to False with warning. Not supported.
2. **CDP Reconnection**: After agent completes, the CDP WebSocket may trigger a reconnect attempt. Harmless `RuntimeError` on async generator cleanup — task already completed.
3. **Browser-use Cloud ≠ Browserbase**: browser-use has its own cloud at `api.browser-use.com` requiring `BROWSER_USE_API_KEY`. We don't use this — connect directly via CDP.
4. **Async generator cleanup**: `RuntimeError: aclose(): asynchronous generator is already running` appears on session close. Harmless.

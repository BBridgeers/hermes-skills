---
name: browser-use-integration
version: 1
description: Integrate browser-use AI agent library with Browserbase for live-view browser automation. Covers installation, DeepSeek LLM configuration, CDP session wiring, Hermes tool registration, and human-in-the-loop CAPTCHA solving. Use when setting up agentic browser navigation with live view capability.
last-updated: 2026-06-06
triggered-by: User wants to see the browser navigate, solve CAPTCHAs interactively, or integrate browser-use with Browserbase
---

# Skill: Browser-Use Integration with Browserbase + Crawl4AI

## Pattern
The user needs AI-powered browser automation where they can WATCH the browser navigating in real-time and take control to solve CAPTCHAs. The full stack uses THREE LAYERS: Browserbase (infrastructure/Chrome), Browser-Use (agent/navigation), Crawl4AI (extraction). The critical design principle is NO DOUBLE NAVIGATION — Crawl4AI parses the active session's DOM instead of making a new HTTP request, avoiding CAPTCHA re-triggers.

## Architecture (Layered Pipeline)
```
browser_pipeline tool (Hermes)
  ├─ Phase 1: Browserbase API → creates session → returns CDP URL + live_view_url
  ├─ Phase 2: Browser-Use Agent → connects via CDP → navigates, logs in, solves CAPTCHAs
  └─ Phase 3: Crawl4AI → grabs raw_html from active session → extracts clean Markdown
       └─ CRITICAL: No second HTTP request. Uses page.content() from live CDP session.
```

For simple tasks without extraction:
```
browser_use_navigate tool (Hermes)
  └─ Browser-Use Agent → CDP → Browserbase → live view
```

## LLM Configuration (Tiered)

```python
# PREFERRED: ChatBrowserUse (browser-use's tuned cloud LLM, better vision/navigation)
if os.getenv("BROWSER_USE_API_KEY"):
    from browser_use.llm.browser_use.chat import ChatBrowserUse
    llm = ChatBrowserUse(api_key=os.getenv("BROWSER_USE_API_KEY"))

# FALLBACK: ChatDeepSeek (cheap, capable, no vision support)
else:
    from browser_use.llm.deepseek.chat import ChatDeepSeek
    llm = ChatDeepSeek(model="deepseek-chat", api_key=ds_key, temperature=0)
```

ChatBrowserUse key from https://cloud.browser-use.com. DeepSeek key from https://platform.deepseek.com.

## Installation

```bash
# Install in Hermes venv
/usr/local/lib/hermes-agent/venv/bin/pip install browser-use crawl4ai

# browser-use 0.12.9 was latest as of June 2026
# crawl4ai is optional — for bulk scraping
```

## Critical: LLM Configuration

**DO NOT use langchain's ChatOpenAI.** browser-use 0.12.9 has its own LLM abstraction (`BaseChatModel` from `browser_use.llm.base`) that requires a `provider` attribute. langchain models don't have this and will fail with `'ChatOpenAI' object has no attribute 'provider'`.

**Use browser-use's native providers:**

```python
# DeepSeek (RECOMMENDED — cheap, capable)
from browser_use.llm.deepseek.chat import ChatDeepSeek
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0,
)

# OpenRouter (alternative)
from browser_use.llm.openai.chat import ChatOpenAI  # browser-use's own
llm = ChatOpenAI(
    model="openrouter/google/gemini-2.5-flash",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# Anthropic
from browser_use.llm.anthropic.chat import ChatAnthropic
llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
```

Available native providers: `browser_use.llm.deepseek`, `browser_use.llm.openai`, `browser_use.llm.anthropic`, `browser_use.llm.google`, `browser_use.llm.mistral`, `browser_use.llm.groq`, `browser_use.llm.azure`, `browser_use.llm.cerebras`.

## Browserbase CDP Connection

Browserbase sessions are created via REST API and return a CDP WebSocket URL:

```python
import httpx

async def create_session(api_key, project_id, timeout=300):
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.browserbase.com/v1/sessions",
            headers={"X-BB-API-Key": api_key},
            json={
                "projectId": project_id,
                "browserSettings": {
                    "timeout": timeout,
                    "fingerprint": {"screen": {"maxWidth": 1920, "maxHeight": 1080}}
                },
                "keepAlive": True,
            }
        )
        data = resp.json()
        return {
            "session_id": data["id"],
            "cdp_url": data["connectUrl"],        # wss://...
            "live_view_url": f"https://browserbase.com/sessions/{data['id']}",
        }
```

Pass the CDP URL to browser-use:

```python
from browser_use.browser import BrowserSession

browser_session = BrowserSession(
    cdp_url=session_info["cdp_url"],
    is_local=False,
    keep_alive=True,
)
```

## Full Agent Example

```python
from browser_use import Agent
from browser_use.browser import BrowserSession
from browser_use.llm.deepseek.chat import ChatDeepSeek

llm = ChatDeepSeek(model="deepseek-chat", api_key=ds_key, temperature=0)

browser_session = BrowserSession(cdp_url=cdp_url, is_local=False, keep_alive=True)

agent = Agent(
    task="Search for data center project manager jobs in Dallas on LinkedIn",
    llm=llm,
    browser_session=browser_session,
    use_vision=True,           # Will auto-set to False for DeepSeek
    max_failures=3,
    max_actions_per_step=5,
)

result = await agent.run(max_steps=30)

# Live view URL lets user watch and control:
# f"https://browserbase.com/sessions/{session_id}"
```

## The Critical Pattern: NO DOUBLE NAVIGATION

When using Browser-Use + Crawl4AI together, Crawl4AI MUST NOT make its own HTTP request. A second navigation risks triggering a new CAPTCHA or hitting a login wall. Instead:

```python
# After agent finishes navigation, grab the ACTIVE session's DOM
page = await browser_session.get_current_page()
raw_html = await page.content()
current_url = page.url

# Pass raw_html to Crawl4AI — parses existing page state, no new request
config = CrawlerRunConfig(word_count_threshold=10, bypass_cache=True)
async with AsyncWebCrawler(verbose=False) as crawler:
    result = await crawler.arun(url=current_url, raw_html=raw_html, config=config)
    clean_markdown = result.markdown
```

This is the difference between a professional pipeline (works) and a naive script (CAPTCHA loop). The agent UNLOCKS the page; the scraper EXTRACTS from the unlocked session.

## Hermes Tool Registration

Three files needed for each tool:

1. **Tool file** in `/usr/local/lib/hermes-agent/tools/`:
   - `browser_use_navigate.py` — single-phase navigation + basic extraction
   - `browser_pipeline.py` — FULL layered pipeline (navigate → Crawl4AI extract)
   - `crawl4ai_extract.py` — standalone high-speed scraping
   - All use `registry.register()` for auto-discovery
   - Sync wrappers via `asyncio.run()` with ThreadPoolExecutor fallback for nested loops

2. **Core tools list** in `toolsets.py` `_HERMES_CORE_TOOLS`:
   ```python
   "browser_use_navigate",
   "browser_pipeline",
   "crawl4ai_extract",
   ```

3. **Toolset definition** in `toolsets.py` `TOOLSETS` dict:
   ```python
   "browser_use": {
       "tools": ["browser_pipeline", "browser_use_navigate", "web_search"],
   },
   "crawl4ai": {
       "tools": ["crawl4ai_extract", "web_search"],
   },
   ```

Gateway restart picks up new tools automatically (auto-discovery from `tools/*.py`). `hermes tools enable browser_use` may not recognize new toolsets until after restart.

## Live View / Human-in-the-Loop

Every browser_use_navigate call returns a `live_view_url`. The user opens this URL to:
- **Watch** the browser navigating in real-time
- **Take control** — click, type, solve CAPTCHAs
- **Let the agent resume** once the CAPTCHA is solved

The Browserbase dashboard shows the session with full interactivity. No additional tooling needed.

## Pitfalls

- **DeepSeek doesn't support `use_vision=True`.** browser-use auto-sets it to False with a warning. Vision is only available with ChatBrowserUse (GPT-4o/Claude/Gemini under the hood) — this is a key reason to prefer ChatBrowserUse over ChatDeepSeek.
- **Hermes `browser_vision` fails with text-only primary models (DeepSeek V4, text-only Ollama models).** The tool takes a screenshot then sends it to the primary LLM as an `image_url` message. If the primary model doesn't support image input, it returns `unknown variant 'image_url'`. The screenshot IS still captured and saved to `~/.hermes/cache/screenshots/` — only the AI analysis fails. Workaround: switch primary to a vision-capable model (Claude, Gemini, GPT-4o/5, Qwen3-VL) before using browser_vision. For browser-use agent tasks, use ChatBrowserUse which handles vision internally regardless of Hermes primary model.
- **CDP WebSocket may disconnect after session complete.** A `RuntimeError` on async generator cleanup is harmless — the session already completed successfully.
- **Browser-use 0.12.9 is the tested version.** API surface differs from older versions (no standalone `Browser` class, `BrowserSession` replaces it, `BrowserProfile` for config). Always check `browser_use.__init__` exports and `Agent.__init__` signature before writing integration code.
- **Browser-use cloud (`api.browser-use.com`) is NOT Browserbase.** browser-use has its own cloud service requiring `BROWSER_USE_API_KEY` (for their LLM). Browserbase is the browser infrastructure (CDP endpoint + live view). These are separate services with separate keys.
- **Google Gemini is REJECTED by this user.** Do not configure as LLM for browser-use. Use ChatBrowserUse or ChatDeepSeek. See model-provider-intel skill for details.
- **Session cleanup:** Browserbase sessions auto-expire after `timeout` seconds. Set appropriate timeout for expected task duration. Long tasks may need `timeout=600` or more.
- **DOUBLE NAVIGATION IS THE #1 FAILURE MODE.** If Crawl4AI makes its own HTTP request to the target URL instead of using the active session's DOM, it will hit the same CAPTCHA/login wall the agent just bypassed. Always use `raw_html=page.content()` from the live CDP session. This is the difference between working and infinite CAPTCHA loops.
- **browser-use's own LLM import path is different from langchain.** Do NOT `pip install langchain-openai` expecting it to work with browser-use. browser-use 0.12.9 has its own LLM classes under `browser_use.llm.<provider>.chat`. langchain's `ChatOpenAI` will fail with `'ChatOpenAI' object has no attribute 'provider'`. The exception is when you use browser-use's own OpenRouter integration: `from browser_use.llm.openai.chat import ChatOpenAI` with `base_url="https://openrouter.ai/api/v1"`.
- **Python version matters.** browser-use 0.12.9 requires Python 3.11+. Tested on Python 3.12.3 (VPS). The pip install may produce dependency conflicts with hermes-agent's pinned openai/rich versions — these are cosmetic warnings, not functional blockers.

## Companion: Crawl4AI

For pure data extraction (no interactivity needed), Crawl4AI standalone is 10x faster than browser automation:

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
config = CrawlerRunConfig(excluded_tags=["nav", "footer", "header"], remove_overlay_elements=True)
async with AsyncWebCrawler(verbose=False) as crawler:
    result = await crawler.arun(url=url, config=config)
    clean = result.markdown
```

But when combined with browser-use, the `raw_html` passthrough pattern (above) is the correct approach. See `references/crawl4ai-raw-html-passthrough.md` for full detail.

## References
- `references/browser-use-api-notes.md` — API discovery notes, Agent/BrowserSession signatures, provider listing
- `references/crawl4ai-raw-html-passthrough.md` — The no-double-navigation pattern: passing active session DOM to Crawl4AI
- `templates/browser-use-tool.py` — Complete tool file template

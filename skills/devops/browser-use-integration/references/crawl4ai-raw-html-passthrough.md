# Crawl4AI Raw HTML Passthrough — The No-Double-Navigation Pattern

## Problem

When combining browser automation (Browser-Use) with data extraction (Crawl4AI), the naive approach is to let Crawl4AI make its own HTTP request to the target URL after the agent finishes navigating. This is WRONG — the new request:

1. Triggers a fresh CAPTCHA (the session is different)
2. Hits login walls (no cookies/authentication from the agent session)
3. May get rate-limited or blocked (different fingerprint)

## Solution: Raw HTML Passthrough

Crawl4AI supports `raw_html` parameter — instead of fetching the URL itself, it parses HTML you provide. Pass the active browser session's DOM content directly.

## Implementation

```python
from browser_use import Agent
from browser_use.browser import BrowserSession
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# Phase 1: Agent navigates (Browser-Use + Browserbase CDP)
browser_session = BrowserSession(cdp_url=session_info["cdp_url"], is_local=False)
agent = Agent(task="Login and navigate to target data page", llm=llm, browser_session=browser_session)
await agent.run(max_steps=30)

# Phase 2: Grab the LIVE session's DOM — NO new HTTP request
page = await browser_session.get_current_page()
raw_html = await page.content()
current_url = page.url

# Phase 3: Crawl4AI parses the RAW HTML from the authenticated session
config = CrawlerRunConfig(
    word_count_threshold=10,
    excluded_tags=["nav", "footer", "header", "script", "style"],
    remove_overlay_elements=True,
    bypass_cache=True,
)

async with AsyncWebCrawler(verbose=False) as crawler:
    result = await crawler.arun(
        url=current_url,      # For metadata only — NOT fetched
        raw_html=raw_html,    # THE CRITICAL PARAMETER — actual content parsed
        config=config,
    )
    clean_markdown = result.markdown
```

## Fallback: Raw Text Extraction

If Crawl4AI fails or isn't installed, fall back to direct DOM text:

```python
page = await browser_session.get_current_page()
raw_text = await page.evaluate("document.body.innerText")
# Cap to prevent token explosion
raw_text = raw_text[:50000]
```

## Why This Matters

| Approach | CAPTCHA Risk | Authentication | Token Cost |
|----------|-------------|----------------|------------|
| Crawl4AI own HTTP request | HIGH — new session, new fingerprint | BROKEN — no cookies | Medium |
| Raw HTML passthrough | NONE — same session | PRESERVED — active cookies | Low (clean Markdown) |
| LLM reads raw page | NONE | PRESERVED | HIGH — raw HTML is token-heavy |

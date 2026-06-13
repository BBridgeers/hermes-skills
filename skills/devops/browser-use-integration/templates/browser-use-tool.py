"""
Hermes Browser-Use Tool — AI-powered browser navigation with Browserbase live view.
Uses browser-use agent + Browserbase CDP for real-time visibility.
Human-in-the-loop CAPTCHA solving via Browserbase session dashboard.

Template — copy and customize for your integration.
"""

import json
import os
import asyncio
import httpx
from tools.registry import registry


def check_requirements() -> bool:
    return bool(os.getenv("BROWSERBASE_API_KEY")) and bool(os.getenv("BROWSERBASE_PROJECT_ID"))


class BrowserbaseCDP:
    """Create and manage Browserbase sessions, returning CDP URLs for browser-use."""
    
    def __init__(self):
        self.api_key = os.getenv("BROWSERBASE_API_KEY", "")
        self.project_id = os.getenv("BROWSERBASE_PROJECT_ID", "")
        self.base = "https://api.browserbase.com/v1"
    
    async def create_session(self, timeout: int = 300) -> dict:
        """Create a new browser session and return CDP + live view URLs."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base}/sessions",
                headers={"X-BB-API-Key": self.api_key},
                json={
                    "projectId": self.project_id,
                    "browserSettings": {
                        "timeout": timeout,
                        "fingerprint": {
                            "screen": {"maxWidth": 1920, "maxHeight": 1080}
                        }
                    },
                    "keepAlive": True,
                }
            )
            data = resp.json()
            return {
                "session_id": data.get("id"),
                "cdp_url": data.get("connectUrl"),
                "live_view_url": data.get("liveViewUrl") or f"https://browserbase.com/sessions/{data.get('id')}",
                "status": data.get("status"),
            }


async def browser_use_navigate(
    task: str,
    url: str = None,
    max_steps: int = 30,
    task_id: str = None,
) -> str:
    """Navigate the web using AI agentic browser control with live view."""
    
    bb = BrowserbaseCDP()
    session_info = None
    
    try:
        from browser_use import Agent
        from browser_use.browser import BrowserSession
        from browser_use.llm.deepseek.chat import ChatDeepSeek
        
        # Create LLM using DeepSeek
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        
        if not deepseek_key:
            return json.dumps({
                "success": False,
                "error": "DEEPSEEK_API_KEY not set. Required for browser-use agent."
            })
        
        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=deepseek_key,
            temperature=0,
        )
        
        # Create Browserbase session for live view
        session_info = await bb.create_session(timeout=max_steps * 30)
        
        if not session_info.get("cdp_url"):
            return json.dumps({
                "success": False,
                "error": "Failed to create Browserbase session",
                "details": session_info
            })
        
        # Create browser-use session connected to Browserbase via CDP
        browser_session = BrowserSession(
            cdp_url=session_info["cdp_url"],
            is_local=False,
            keep_alive=True,
        )
        
        # Build task with URL if provided
        full_task = task
        if url:
            full_task = f"Start at {url}. {task}"
        
        # Create the agent
        agent = Agent(
            task=full_task,
            llm=llm,
            browser_session=browser_session,
            use_vision=True,
            max_failures=3,
            max_actions_per_step=5,
        )
        
        # Run
        result = await agent.run(max_steps=max_steps)
        
        return json.dumps({
            "success": True,
            "session_id": session_info["session_id"],
            "live_view_url": session_info["live_view_url"],
            "result": str(result),
            "note": "LIVE VIEW: Open live_view_url to watch/control the browser. Solve CAPTCHAs there."
        })
        
    except ImportError as e:
        return json.dumps({
            "success": False,
            "error": f"browser-use not installed: {e}"
        })
    except Exception as e:
        error_msg = str(e)
        live_view = session_info.get("live_view_url") if session_info else None
        
        response = {
            "success": False,
            "error": error_msg,
        }
        if live_view:
            response["live_view_url"] = live_view
            response["note"] = "Session may still be active. Check live_view_url."
        
        return json.dumps(response)


def browser_use_navigate_sync(task: str, url: str = None, max_steps: int = 30,
                               task_id: str = None) -> str:
    """Synchronous wrapper for async function."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, browser_use_navigate(task, url, max_steps, task_id))
                return future.result(timeout=600)
        return asyncio.run(browser_use_navigate(task, url, max_steps, task_id))
    except RuntimeError:
        return asyncio.run(browser_use_navigate(task, url, max_steps, task_id))


# Auto-register with Hermes tool registry
registry.register(
    name="browser_use_navigate",
    toolset="browser_use",
    schema={
        "name": "browser_use_navigate",
        "description": "AI-powered browser agent with LIVE VIEW. Use for complex web navigation, form filling, CAPTCHA-heavy sites. Returns a live_view_url — open it to watch the browser in real-time.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "What the browser agent should accomplish."
                },
                "url": {
                    "type": "string",
                    "description": "Optional starting URL."
                },
                "max_steps": {
                    "type": "integer",
                    "description": "Maximum browser steps (default 30)."
                }
            },
            "required": ["task"]
        }
    },
    handler=lambda args, **kw: browser_use_navigate_sync(
        task=args.get("task", ""),
        url=args.get("url"),
        max_steps=args.get("max_steps", 30),
        task_id=kw.get("task_id"),
    ),
    check_fn=check_requirements,
    requires_env=["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"],
)

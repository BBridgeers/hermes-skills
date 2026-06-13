# GitHub README API — Repo Content Research

When `web_extract` is unavailable (credits exhausted, JS-rendered pages), use the GitHub README API to research repo content for "why notable" lines.

## Fetch README

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/readme" -o /tmp/gh-trending/OWNER_REPO_readme.json
```

## Decode and read

```bash
python3 -c "
import json, base64
with open('/tmp/gh-trending/OWNER_REPO_readme.json') as f:
    d = json.load(f)
content = base64.b64decode(d['content']).decode('utf-8', errors='replace')
print(content[:1500])
"
```

**Key details:**
- Response has `.content` (base64-encoded) and `.encoding`
- Decode with `base64.b64decode` — not utf-8 on the raw string
- Trim to ~1500 chars for the "why notable" research pass
- Rate limit: same as repo API (60/hr unauthenticated, 5000/hr with token)

## Also useful: releases endpoint

For repos that may be trending due to a new release:

```bash
curl -sL "https://api.github.com/repos/OWNER/REPO/releases?per_page=3" -o /tmp/gh-trending/OWNER_REPO_releases.json
```

Parse with `json.load()` — returns array of release objects with `tag_name`, `published_at`, `name`, `body`.

## Pitfall reminder

Never pipe `curl` into `python3` — Tirith blocks it. Always save to file first, then parse from file with `python3 -c "..."` using `open()`.

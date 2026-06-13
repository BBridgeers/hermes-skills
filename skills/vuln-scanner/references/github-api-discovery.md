# GitHub API Repo Discovery (when both `gh` and web_extract fail)

When Firecrawl credits are exhausted, both `web_extract` and `web_search` fail
with "Payment Required". The direct GitHub Search API is the fallback. Use
`curl` + a Python script — never pipe `curl` into python3 (tirith guard).

## 1. Fetch repos

```bash
curl -s -o /tmp/gh-results.json \
  "https://api.github.com/search/repositories?q=created:%3E$(date -u -d '14 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=25" \
  -H "Accept: application/vnd.github+json" \
  -H "User-Agent: hermes-vuln-scanner"
```

## 2. Parse and filter

Python script that filters by language, stars, fork status, dedup state,
and teaching-repo patterns:

```python
import json
from datetime import datetime, timezone, timedelta

with open('/tmp/gh-results.json') as f:
    data = json.load(f)

target_langs = {'JavaScript', 'TypeScript', 'Python', 'Go', 'Rust', 'Solidity'}
scanned_repos = set()
try:
    with open('/root/.hermes/state/vuln-scanned.json') as f:
        for item in json.load(f):
            scanned_at = datetime.fromisoformat(item['scanned_at'].replace('Z', '+00:00'))
            if (datetime.now(timezone.utc) - scanned_at).days < 30:
                scanned_repos.add(item['repo'])
except Exception:
    pass

skip_patterns = ['dvwa', 'juice-shop', 'webgoat', 'vulnerable-', '-ctf', 'hackme-']

for item in data.get('items', []):
    name = item['full_name']
    if item.get('fork'): continue
    if item.get('stargazers_count', 0) < 50: continue
    if name in scanned_repos: continue

    lang = item.get('language', '')
    if lang not in target_langs: continue

    desc = (item.get('description') or '')
    desc_lower = desc.lower()
    name_lower = name.lower()
    if any(p in desc_lower or p in name_lower for p in skip_patterns): continue

    sec = item.get('security_and_analysis', {}) or {}
    pvr = (sec.get('private_vulnerability_reporting') or {}).get('status', 'disabled') or 'disabled'
    desc_short = (desc[:120] if desc else '')
    print(f"REPO={name} | stars={item['stargazers_count']} | lang={lang} | pvr={pvr} | desc={desc_short}")
```

## 3. Check individual repo metadata

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>" \
  -H "Accept: application/vnd.github+json" \
  -H "User-Agent: hermes-vuln-scanner" \
  -o /tmp/repo-info.json
```

Parse with a separate script (never pipe curl to python3).

#!/usr/bin/env python3
"""Parse GitHub trending page HTML (from curl) into structured JSON.

Usage:
    python3 parse-trending-html.py < trending.html > repos.json

Output: JSON array of objects with keys:
    repo, description, language, stars_today, total_stars, url

NOTE: total_stars is often None from HTML alone — requires API enrichment.
"""

import sys
import re
import json
import html as html_module


def parse_trending(content: str) -> list[dict]:
    repos = []
    articles = content.split('<article class="Box-row">')

    for article in articles[1:]:
        # Repo path from h2 > a href
        h2_match = re.search(
            r'<h2[^>]*class="h3[^"]*"[^>]*>.*?<a[^>]*href="/([^"]+)"',
            article,
            re.DOTALL,
        )
        if not h2_match:
            continue
        repo_path = h2_match.group(1).strip()

        # Skip sponsor and internal paths
        if repo_path.startswith("sponsors/"):
            continue
        skip_prefixes = ["topics/", "explore/", "apps/", "settings/", "features/", "marketplace/", "orgs/"]
        if any(repo_path.startswith(p) for p in skip_prefixes):
            continue

        # Description
        desc_match = re.search(r'<p[^>]*class="col-9[^"]*"[^>]*>(.*?)</p>', article, re.DOTALL)
        description = html_module.unescape(desc_match.group(1).strip()) if desc_match else ""

        # Language
        lang_match = re.search(r'itemprop="programmingLanguage"[^>]*>(.*?)</span>', article, re.DOTALL)
        language = lang_match.group(1).strip() if lang_match else ""

        # Stars today
        stars_today_match = re.search(r"([\d,]+)\s*stars?\s*today", article)
        stars_today = int(stars_today_match.group(1).replace(",", "")) if stars_today_match else 0

        # Total stars (unreliable from HTML)
        total_stars = None

        repos.append({
            "repo": repo_path,
            "description": description[:300],
            "language": language,
            "stars_today": stars_today,
            "total_stars": total_stars,
            "url": f"https://github.com/{repo_path}",
        })

    return repos


def main():
    content = sys.stdin.read()
    repos = parse_trending(content)
    json.dump(repos, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Instagram carousel scraper — direct GraphQL API with OCR transcription.
Usage: python3 scraper_template.py <username> <output_dir> <session_file>
"""
import json, os, sys, time, requests
from pathlib import Path

USERNAME = sys.argv[1]
OUTDIR = Path(sys.argv[2])
SESSION_FILE = sys.argv[3]

OUTDIR.mkdir(parents=True, exist_ok=True)

# ── Auth ──
from instagrapi import Client
cl = Client()
cl.load_settings(SESSION_FILE)

assert len(cl.private.cookies) > 0, "Session stale — re-login with: cl.login(user, pass, verification_code='...')"

cookies = {}
for c in cl.private.cookies:
    cookies[c.name] = c.value
settings = cl.get_settings()
for k in ['sessionid', 'csrftoken', 'ds_user_id', 'mid']:
    v = settings.get(k, '')
    if v and k not in cookies:
        cookies[k] = v

session = requests.Session()
session.cookies.update(cookies)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-IG-App-ID': '936619743392459',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.instagram.com/',
})

# ── Get user ID (cached if known) ──
# USER_ID = "PRE_RESOLVED_ID"  # uncomment and set to skip lookup
USER_ID = cl.user_id_from_username(USERNAME)
print(f'User ID: {USER_ID}')

# ── Index all posts ──
posts = []
end_cursor = None
page = 0

while True:
    resp = session.get("https://www.instagram.com/graphql/query", params={
        "query_hash": "69cba40317214236af40e7efa697781d",
        "variables": json.dumps({"id": str(USER_ID), "first": 50, "after": end_cursor})
    }, timeout=30)

    if resp.status_code != 200:
        print(f'HTTP {resp.status_code}, retrying...')
        time.sleep(10)
        continue

    data = resp.json()
    timeline = data.get('data', {}).get('user', {}).get('edge_owner_to_timeline_media', {})
    edges = timeline.get('edges', [])
    page_info = timeline.get('page_info', {})

    if not edges:
        break

    for edge in edges:
        node = edge['node']
        mt = node.get('__typename', '')
        post = {
            'id': node['id'],
            'shortcode': node['shortcode'],
            'type': 'carousel' if mt == 'GraphSidecar' else 'video' if mt == 'GraphVideo' else 'image',
            'caption': node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', ''),
            'taken_at': node.get('taken_at_timestamp'),
            'like_count': node.get('edge_media_preview_like', {}).get('count', 0),
            'comment_count': node.get('edge_media_to_comment', {}).get('count', 0),
            'slide_count': len(node.get('edge_sidecar_to_children', {}).get('edges', [])),
            'resources': [],
        }
        if mt == 'GraphSidecar':
            for child in node.get('edge_sidecar_to_children', {}).get('edges', []):
                cn = child['node']
                dr = cn.get('display_resources', [])
                if dr:
                    post['resources'].append(dr[-1]['src'])
                elif cn.get('display_url'):
                    post['resources'].append(cn['display_url'])
        posts.append(post)

    page += 1
    print(f'Page {page}: {len(edges)} posts (total: {len(posts)})')
    end_cursor = page_info.get('end_cursor')
    if not page_info.get('has_next_page') or not end_cursor:
        break
    time.sleep(2)

index_path = OUTDIR / 'index.json'
with open(index_path, 'w') as f:
    json.dump(posts, f, indent=2)
print(f'Saved {len(posts)} posts to {index_path}')

# ── OCR carousel slides ──
carousels = [p for p in posts if p['type'] == 'carousel']
if not carousels:
    print(f'No carousels to OCR.')
    sys.exit(0)

from PIL import Image
import pytesseract

done = 0
failed = 0

for post in carousels:
    sc = post['shortcode']
    md_file = OUTDIR / f'{post["id"]}.md'
    slides_dir = OUTDIR / f'{post["id"]}_slides'

    if md_file.exists():
        done += 1
        continue

    try:
        slides_dir.mkdir(exist_ok=True)
        md = f"# {sc}\n\n**Date**: {post['taken_at']}\n**Likes**: {post['like_count']} | **Comments**: {post['comment_count']}\n**Slides**: {len(post['resources'])}\n\n## Caption\n\n{post['caption']}\n\n## Slides\n\n"

        for j, url in enumerate(post['resources']):
            try:
                r = session.get(url, timeout=30)
                if r.status_code == 200:
                    img_path = slides_dir / f'slide_{j+1:02d}.jpg'
                    img_path.write_bytes(r.content)
                    text = pytesseract.image_to_string(Image.open(img_path)).strip()
                    md += f"### Slide {j+1}\n\n{text}\n\n"
                else:
                    md += f"### Slide {j+1}\n\n[Download failed: HTTP {r.status_code}]\n\n"
            except Exception as e:
                md += f"### Slide {j+1}\n\n[Error: {e}]\n\n"
            time.sleep(0.5)

        md_file.write_text(md)
        done += 1
        if done % 5 == 0:
            print(f'  [{done}/{len(carousels)}] OCR done | {failed} failed')
        time.sleep(1)

    except Exception as e:
        print(f'  FAIL {sc}: {str(e)[:100]}')
        failed += 1
        time.sleep(3)

print(f'\nDone. {done} processed, {failed} failed.')

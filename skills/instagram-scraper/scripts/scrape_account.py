#!/usr/bin/env python3
"""Instagram carousel scraper — GraphQL approach. Resumable."""
import json, time, requests, sys, os
from pathlib import Path

ACCOUNT = os.environ.get('IG_ACCOUNT', 'target_account')
USER_ID = os.environ.get('IG_USER_ID', '')
OUTDIR = Path(os.environ.get('IG_OUTDIR', f'/root/workspace/detoxxx/{ACCOUNT}_posts'))
OUTDIR.mkdir(exist_ok=True)

# ── Auth ──
from instagrapi import Client
SESSION_FILE = os.environ.get('IG_SESSION', '/root/workspace/detoxxx/insta_session.json')
cl = Client()
cl.load_settings(SESSION_FILE)

cookies = len(cl.private.cookies)
assert cookies > 0, f'SESSION DEAD ({cookies} cookies) — re-auth before running this script'
settings = cl.get_settings()

cookie_dict = {c.name: c.value for c in cl.private.cookies}
for k in ['sessionid', 'csrftoken', 'ds_user_id', 'mid']:
    v = settings.get(k, '')
    if v and k not in cookie_dict:
        cookie_dict[k] = v

session = requests.Session()
session.cookies.update(cookie_dict)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'X-IG-App-ID': '936619743392459',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.instagram.com/',
})

# ── Fetch all posts ──
posts = []
end_cursor = None
page = 0

while True:
    variables = json.dumps({"id": USER_ID, "first": 50, "after": end_cursor})
    params = {"query_hash": "69cba40317214236af40e7efa697781d", "variables": variables}
    
    resp = session.get("https://www.instagram.com/graphql/query", params=params, timeout=30)
    
    if resp.status_code == 401:
        print("FATAL: HTTP 401 — session expired. Kill process, delete session file, re-auth.")
        sys.exit(1)
    
    if resp.status_code != 200:
        print(f"HTTP {resp.status_code} on page {page+1}, retrying...", flush=True)
        time.sleep(10)
        continue
    
    data = resp.json()
    user_data = data.get('data', {}).get('user', {})
    timeline = user_data.get('edge_owner_to_timeline_media', {})
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
            'caption': (node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '') if node.get('edge_media_to_caption', {}).get('edges') else ''),
            'taken_at': node.get('taken_at_timestamp'),
            'like_count': node.get('edge_media_preview_like', {}).get('count', 0),
            'comment_count': node.get('edge_media_to_comment', {}).get('count', 0),
            'slide_count': len(node.get('edge_sidecar_to_children', {}).get('edges', [])) if mt == 'GraphSidecar' else 1,
            'resources': [],
        }
        
        if mt == 'GraphSidecar':
            for child in node.get('edge_sidecar_to_children', {}).get('edges', []):
                child_node = child['node']
                urls = child_node.get('display_resources', child_node.get('display_url', []))
                if isinstance(urls, list) and urls:
                    post['resources'].append(urls[-1]['src'])
                elif isinstance(urls, str):
                    post['resources'].append(urls)
        
        posts.append(post)
    
    page += 1
    print(f"Page {page}: {len(edges)} posts (total: {len(posts)})", flush=True)
    
    end_cursor = page_info.get('end_cursor')
    if not page_info.get('has_next_page') or not end_cursor:
        break
    
    time.sleep(1.5)

with open(OUTDIR / 'index.json', 'w') as f:
    json.dump(posts, f, indent=2)

carousels = [p for p in posts if p['type'] == 'carousel']
print(f"\nTotal: {len(posts)} posts ({len(carousels)} carousels)", flush=True)

# ── OCR ──
from PIL import Image
import pytesseract

done = sum(1 for p in carousels if (OUTDIR / f'{p["id"]}.md').exists())
failed = 0
print(f"\n--- OCR on {len(carousels)} carousels ({done} already done) ---", flush=True)

for i, post in enumerate(carousels):
    sc = post['shortcode']
    md_file = OUTDIR / f'{post["id"]}.md'
    slides_dir = OUTDIR / f'{post["id"]}_slides'
    
    if md_file.exists():
        continue
    
    try:
        slides_dir.mkdir(exist_ok=True)
        md = f"# {sc}\n\n"
        md += f"**Date**: {post['taken_at']}\n"
        md += f"**Likes**: {post['like_count']} | **Comments**: {post['comment_count']}\n"
        md += f"**Slides**: {len(post['resources'])}\n\n"
        md += f"## Caption\n\n{post['caption']}\n\n## Slides\n\n"
        
        for j, url in enumerate(post['resources']):
            try:
                r = session.get(url, timeout=30)
                if r.status_code == 200:
                    img_path = slides_dir / f'slide_{j+1:02d}.jpg'
                    img_path.write_bytes(r.content)
                    img = Image.open(img_path)
                    text = pytesseract.image_to_string(img).strip()
                    md += f"### Slide {j+1}\n\n{text}\n\n"
                else:
                    md += f"### Slide {j+1}\n\n[HTTP {r.status_code}]\n\n"
            except Exception as e:
                md += f"### Slide {j+1}\n\n[Error: {e}]\n\n"
            time.sleep(0.3)
        
        md_file.write_text(md)
        done += 1
        if done % 5 == 0:
            print(f"  [{done}/{len(carousels)}] done | {failed} failed", flush=True)
        time.sleep(0.7)
    
    except Exception as e:
        print(f"  FAIL {sc}: {str(e)[:100]}", flush=True)
        failed += 1
        time.sleep(3)

print(f"\nDone. {done} processed, {failed} failed.", flush=True)

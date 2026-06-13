#!/usr/bin/env python3
"""Instagram carousel scraper — instagrapi with safe extractor patch.

Working template from @harmonicearththeory / @theaethervault scrapes.
DO NOT use raw GraphQL with extracted cookies — instagrapi cookies are always empty.
DO NOT call user_id_from_username() in scripts — cache the ID and hardcode it.
Always run with: python3 -u script.py 2>&1 | tee /tmp/scrape.log
"""
import json, time
from pathlib import Path

# ═══ CONFIGURE ═══
ACCOUNT = "account_name"
USER_ID = "00000000000"  # Hardcode — skip rate-limited user_id_from_username()
OUTDIR = Path(f"/root/workspace/detoxxx/{ACCOUNT}_posts")
SESSION_FILE = "/root/workspace/detoxxx/insta_session.json"

# ═══ PATCH instagrapi extractors BEFORE import ═══
import instagrapi.extractors as ex
import instagrapi.types as t

original_v1 = ex.extract_media_v1
def safe_extract(data):
    try: return original_v1(data)
    except:
        return {
            'pk': str(data.get('pk', data.get('id', ''))),
            'code': data.get('code', ''),
            'media_type': data.get('media_type', 1),
            'caption_text': (data.get('caption', {}) or {}).get('text', '')
                if isinstance(data.get('caption'), dict) else '',
            'taken_at': data.get('taken_at', 0),
            'like_count': data.get('like_count', 0) or 0,
            'comment_count': data.get('comment_count', 0) or 0,
            'resources': [], 'product_type': '',
            'video_url': None, 'thumbnail_url': None,
        }
ex.extract_media_v1 = safe_extract

orig_resource = ex.extract_resource_v1
def safe_resource(data):
    try: return orig_resource(data)
    except:
        return t.Resource(
            pk=str(data.get('pk', data.get('id', ''))),
            video_url=None,
            thumbnail_url=data.get('display_url', 'https://example.com/1.jpg'),
            media_type=1, product_type='',
        )
ex.extract_resource_v1 = safe_resource

from instagrapi import Client

# ═══ AUTH ═══
cl = Client()
cl.load_settings(SESSION_FILE)
OUTDIR.mkdir(exist_ok=True)

print(f"User ID: {USER_ID}", flush=True)

# ═══ FETCH ALL POSTS ═══
posts = []
end_cursor = None
page = 0

while True:
    try:
        batch, end_cursor = cl.user_medias_paginated(USER_ID, 50, end_cursor=end_cursor)
    except Exception as e:
        print(f"Page {page+1} error: {e}", flush=True)
        time.sleep(5)
        continue

    for p in batch:
        mt = p.media_type
        posts.append({
            'id': str(p.pk),
            'code': p.code,
            'type': 'carousel' if mt == 8 else 'video' if mt == 2 else 'image',
            'caption': (p.caption_text or '')[:2000],
            'taken_at': p.taken_at.timestamp() if hasattr(p.taken_at, 'timestamp') else p.taken_at,
            'like_count': p.like_count or 0,
            'comment_count': p.comment_count or 0,
            'slide_count': len(p.resources) if mt == 8 else 1,
        })

    page += 1
    print(f"Page {page}: {len(batch)} posts (total: {len(posts)})", flush=True)

    if not end_cursor:
        break
    time.sleep(1.5)

# Save index
with open(OUTDIR / 'index.json', 'w') as f:
    json.dump(posts, f, indent=2)

carousels = [p for p in posts if p['type'] == 'carousel']
print(f"\nTotal: {len(posts)} posts ({len(carousels)} carousels)", flush=True)

# ═══ CAROUSEL DOWNLOAD + OCR ═══
from PIL import Image
import pytesseract, requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
})

done = 0
failed = 0
print(f"\n--- Downloading {len(carousels)} carousels ---", flush=True)

for i, post in enumerate(carousels):
    sc = post['code']
    pid = post['id']
    md_file = OUTDIR / f'{pid}.md'
    slides_dir = OUTDIR / f'{pid}_slides'

    if md_file.exists():
        done += 1
        continue

    try:
        info = cl.media_info(pid)
        slides_dir.mkdir(exist_ok=True)

        md = f"# {sc}\n\n"
        md += f"**Date**: {post['taken_at']}\n"
        md += f"**Likes**: {post['like_count']} | **Comments**: {post['comment_count']}\n"
        md += f"**Slides**: {len(info.resources)}\n\n"
        md += f"## Caption\n\n{post['caption']}\n\n## Slides\n\n"

        for j, res in enumerate(info.resources):
            try:
                url = str(res.thumbnail_url)
                r = session.get(url, timeout=30)
                if r.status_code == 200:
                    img_path = slides_dir / f'slide_{j+1:02d}.jpg'
                    img_path.write_bytes(r.content)
                    img = Image.open(img_path)
                    img.thumbnail((800, 800), Image.LANCZOS)
                    img = img.convert('RGB')
                    img.save(img_path, 'JPEG', quality=70, optimize=True)
                    text = pytesseract.image_to_string(Image.open(img_path)).strip()
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

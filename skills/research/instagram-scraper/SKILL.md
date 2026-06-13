---
name: instagram-scraper
description: Scrape Instagram accounts — carousel posts with OCR, video reels with transcription. Uses instagrapi for auth (with monkey-patched extractors), pytesseract for slide OCR, and syncs results to Google Drive.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [instagram, scraping, OCR, drive, research]
---

# Instagram Scraper — Full Account Extraction

Scrapes every post from a public Instagram account. Handles carousels (slides + OCR), video/Reels (download + transcription), and single images.

## Auth — 2FA Workflow

Session stored at `~/workspace/detoxxx/insta_session.json`. When session expires, use:

```python
from instagrapi import Client
cl = Client()
cl.login('USERNAME', 'PASSWORD')  # TRIGGER — will throw TwoFactorAuthRequired
```

**Immediately ask user for the 6-digit code.** They send it within 20 seconds:

```python
cl.login('USERNAME', 'PASSWORD', verification_code='370651')
cl.dump_settings('insta_session.json')
```

Pattern: TRIGGER → ASK → RECEIVE → SLAM IT IN. Never ask user to go find the code first — trigger the login so their phone gets the 2FA notification.

## instagrapi Extractor Bugs (CRITICAL)

`extract_media_v1` and `extract_resource_v1` crash on posts with null `video_versions` or missing resource `pk` fields. **Monkey-patch before any pagination:**

```python
import instagrapi.extractors as ex
import instagrapi.types as t

original_v1 = ex.extract_media_v1
def safe_extract(data):
    try: return original_v1(data)
    except:
        return {'pk': str(data.get('pk', data.get('id', ''))), 'code': data.get('code', ''),
                'media_type': data.get('media_type', 1),
                'caption_text': (data.get('caption', {}) or {}).get('text', '') if isinstance(data.get('caption'), dict) else '',
                'taken_at': data.get('taken_at', 0), 'like_count': data.get('like_count', 0) or 0,
                'comment_count': data.get('comment_count', 0) or 0, 'resources': [], 'product_type': '',
                'video_url': None, 'thumbnail_url': None}
ex.extract_media_v1 = safe_extract

orig_resource = ex.extract_resource_v1
def safe_resource(data):
    try: return orig_resource(data)
    except: return t.Resource(pk=str(data.get('pk', data.get('id', ''))),
        video_url=None, thumbnail_url=data.get('display_url', 'https://example.com/1.jpg'),
        media_type=1, product_type='')
ex.extract_resource_v1 = safe_resource
```

## Fetching All Posts

```python
uid = cl.user_id_from_username('target')
posts = []; end_cursor = None
while True:
    try:
        batch, end_cursor = cl.user_medias_paginated(uid, 50, end_cursor=end_cursor)
        for p in batch:
            mt = p.media_type
            posts.append({'id': str(p.pk), 'code': p.code,
                'type': 'carousel' if mt == 8 else 'video' if mt == 2 else 'image',
                'caption': (p.caption_text or '')[:500]})
        if not end_cursor: break
        time.sleep(2)
    except: time.sleep(10); break if not end_cursor else None
```

media_type: 8=carousel, 2=video/Reel, 1=single image.

## Carousel OCR Pipeline

```python
info = cl.media_info(pk)
for res in info.resources:
    img_url = str(res.thumbnail_url)
    r = session.get(img_url, timeout=30)
    img = Image.open(io.BytesIO(r.content))
    img.thumbnail((800, 800), Image.LANCZOS)
    img = img.convert('RGB')
    img.save(path, 'JPEG', quality=70, optimize=True)
    text = pytesseract.image_to_string(Image.open(path)).strip()
```

## Output Structure

```
target_posts/
├── index.json                    ← all posts metadata
├── {post_id}.md                  ← caption + OCR'd slides
├── {post_id}_slides/
│   ├── slide_01.jpg              ← 800px JPEG Q70
│   └── ...
```

## Google Drive Sync

Syncs to `Instagram_Scrapes/{account}/` with `posts/` (markdown) and `slides/` (ZIP archives) subfolders.

## Pitfalls

- **Session expiry**: Re-auth via 2FA when HTML login page returned instead of JSON
- **Rate limiting**: Space API calls 1-2s; `spam: true` = too aggressive
- **Tesseract OCR**: Fast but poor on Instagram's stylized fonts. Vision API fallback for decorative text
- **Disk**: ~100-150MB per 940-post account with compressed slides
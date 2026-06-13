---
name: instagram-content-scraper
description: Scrape Instagram accounts — posts, carousels, Reels, captions, slide images, and OCR text. Covers authentication (including 2FA flow), instagrapi monkey-patching for broken extractors, image compression, and multi-format output.
tags: [instagram, scraping, OCR, instagrapi, social-media]
---

# Instagram Content Scraper

Full-pipeline Instagram scraping: authentication, post enumeration, carousel slide extraction, Reel video download, OCR transcription, and multi-format export (markdown, JSON, GDrive).

## Authentication

### Session persistence
Use instagrapi with `dump_settings()` / `load_settings()`. Session file is JSON, stored at a known path (e.g., `insta_session.json`).

Session cookies live in `authorization_data` dict inside the settings file:
- `sessionid`
- `ds_user_id`
- `csrftoken`
- `mid`

### 2FA flow (CRITICAL — user enforces this exact sequence)

**DO NOT** ask the user to go find a 2FA code. The flow is:

1. Trigger the login WITHOUT the code — instagrapi raises `TwoFactorRequired`
2. Immediately report "Code triggered" and ask them to send it
3. User sends the 6-digit code
4. You have **20 seconds** to call `cl.login(user, pass, verification_code='XXXXXX')` before it expires

```python
from instagrapi import Client
cl = Client()
try:
    cl.login('username', 'password')
    cl.dump_settings('insta_session.json')
except Exception as e:
    if 'verification_code' in str(e) or 'two-factor' in str(e).lower():
        print('NEED_CODE')  # trigger user to send code
        # ... user sends code ...
        cl.login('username', 'password', verification_code='USER_CODE')
        cl.dump_settings('insta_session.json')
```

Pitfall: `load_settings()` alone may not populate `cl.private.cookies`. Extract from `authorization_data` as fallback:
```python
settings = cl.get_settings()
auth = settings.get('authorization_data', {})
cookies = {
    'sessionid': auth.get('sessionid', ''),
    'ds_user_id': auth.get('ds_user_id', ''),
    'mid': settings.get('mid', ''),
}
```

## instagrapi extractor monkey-patching

instagrapi's built-in extractors crash on certain post types:
- `video_versions` can be `None` (key exists but value is None) → `TypeError: 'NoneType' object is not iterable`
- `Resource.pk` can be missing → pydantic `ValidationError`
- `thumbnail_url` can be empty string → pydantic URL parsing error

The fix: monkey-patch `extract_media_v1` and `extract_resource_v1` with safe wrappers that catch all exceptions and return minimal valid dicts.

```python
import instagrapi.extractors as ex
import instagrapi.types as t

original_v1 = ex.extract_media_v1
def safe_extract(data):
    try:
        return original_v1(data)
    except:
        return {
            'pk': str(data.get('pk', data.get('id', ''))),
            'code': data.get('code', ''),
            'media_type': data.get('media_type', 1),
            'caption_text': (data.get('caption', {}) or {}).get('text', '') if isinstance(data.get('caption'), dict) else '',
            'taken_at': data.get('taken_at', 0),
            'like_count': data.get('like_count', 0) or 0,
            'comment_count': data.get('comment_count', 0) or 0,
            'resources': [],
            'product_type': '',
            'video_url': None,
            'thumbnail_url': None,
        }
ex.extract_media_v1 = safe_extract

orig_resource = ex.extract_resource_v1
def safe_resource(data):
    try:
        return orig_resource(data)
    except:
        return t.Resource(
            pk=str(data.get('pk', data.get('id', ''))),
            video_url=None,
            thumbnail_url=data.get('display_url', 'https://example.com/1.jpg'),
            media_type=1,
            product_type='',
        )
ex.extract_resource_v1 = safe_resource
```

**IMPORTANT**: The safe extractor returns empty `resources: []` which means `slide_count` will be 1 for carousels. To get actual slide data, call `cl.media_info(pk)` on each carousel post individually AFTER pagination is complete.

## Post enumeration (paginated fetch)

Use `cl.user_medias_paginated()` wrapped in try/except. The monkey-patched extractors still throw, but the outer try/except catches and you still get the posts that populated before the crash.

```python
while True:
    try:
        batch, end_cursor = cl.user_medias_paginated(user_id, 50, end_cursor=end_cursor)
        for p in batch:
            # process post...
        if not end_cursor:
            break
        time.sleep(2)  # rate limit
    except Exception as e:
        # Data still populated — continue
        time.sleep(10)
        if not end_cursor:
            break
```

## Media type classification

| Instagram type | media_type | __typename |
|---|---|---|
| Single image | 1 | GraphImage |
| Video/Reel | 2 | GraphVideo |
| Carousel | 8 | GraphSidecar |

Reels are classified as `media_type=2` (video), NOT carousel. If an account posts "text-heavy slides as Reels," those will appear as video type and need frame extraction + OCR, not slide download.

## Slide download + OCR (carousels)

For each carousel post:
1. Call `cl.media_info(pk)` to get `resources` list
2. Each resource has a `thumbnail_url` — download it
3. OCR with tesseract: `pytesseract.image_to_string(img)`

## Image compression (MANDATORY — user requires this)

Images MUST be compressed on download to minimize disk usage:
```python
from PIL import Image
img = Image.open(img_path)
img.thumbnail((800, 800), Image.LANCZOS)  # max 800px on longest side
img = img.convert('RGB')
img.save(img_path, 'JPEG', quality=70, optimize=True)
```

## Output structure

```
<account>_posts/
├── index.json                    # [{id, code, type, caption, slide_count, ...}]
├── <post_id>.md                  # caption + OCR text per slide
├── <post_id>_slides/
│   ├── slide_01.jpg
│   ├── slide_02.jpg
│   └── ...
```

Each markdown file:
```markdown
# <shortcode>

**Date**: <taken_at>
**Likes**: <count> | **Comments**: <count>
**Slides**: <n>

## Caption

<full caption text>

## Slides

### Slide 1
<OCR text>

### Slide 2
<OCR text>
```

## Drive upload

Results go to Google Drive (NOT left on VPS taking up space). See `google-workspace` skill for upload patterns. Folder structure:

```
Instagram_Scrapes/           ← top-level (NOT inside any other project folder)
├── renwellmd/
│   └── posts/
└── theaethervault/
    ├── posts/               ← .md files
    └── slides/              ← .zip files (one per post, compressed images)
```

## Pitfalls

- **Don't use instaloader** if the account has 2FA — it requires interactive auth that Hermes can't handle
- **Don't use direct GraphQL API** without proper mobile app headers — Instagram returns `{"spam":true}` for desktop User-Agents
- **Session cookies expire** during long scraping runs. Re-authenticate (with 2FA flow) and resume from last saved index
- **Tesseract OCR quality is poor on stylized Instagram fonts.** The text comes through but expect garbled decorative text
- **`load_settings()` network dependency** — instagrapi may make network calls during `load_settings()`. If it hangs, read the JSON file directly instead

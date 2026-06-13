---
name: instagram-data-extraction
description: Extract data from Instagram profiles — posts, carousels, captions, slides, and OCR text. Covers authentication (including 2FA), session management, instagrapi bug workarounds, and carousel-to-markdown pipelines.
version: 1.0.0
tags: [instagram, scraping, carousel, OCR, authentication, instagrapi]
---

# Instagram Data Extraction

Full pipeline: authenticate → fetch posts → download carousel slides → OCR text → structured markdown output.

---

## Step 0: Authentication & Session

### Initial Login

```python
from instagrapi import Client
cl = Client()
cl.login(USERNAME, PASSWORD)
cl.dump_settings(SESSION_FILE)
```

### 2FA Workflow (CRITICAL — follow this exactly)

The user wants this flow. Do NOT ask the user to "go find the code" preemptively.

1. **Trigger the login attempt without verification_code.**
2. **When it fails with "Two-factor authentication required", immediately ask for the code.** Be terse — just ask.
3. **User sends the 6-digit code.**
4. **Within 20 seconds of receiving it, run:**
   ```python
   cl.login(USERNAME, PASSWORD, verification_code='XXXXXX')
   cl.dump_settings(SESSION_FILE)
   ```
5. Verify: `cl.get_settings().get('authorization_data', {}).get('sessionid')` should be non-empty.

**Pitfall:** `cl.dump_settings()` may report "LOGGED_IN" but not populate the `cookies` dict. The actual session data lives in `authorization_data` within the saved JSON. Always check for `sessionid` in `authorization_data` after login.

### Session Reload

```python
cl = Client()
cl.load_settings(SESSION_FILE)
# Cookies are in authorization_data, not cl.private.cookies
settings = cl.get_settings()
auth = settings.get('authorization_data', {})
sessionid = auth.get('sessionid')
```

---

## Step 1: Fetch Posts (Monkey-Patched instagrapi)

instagrapi's `extract_media_v1` and `extract_resource_v1` crash on certain Instagram API responses:
- `video_versions` is `None` instead of missing → `TypeError: 'NoneType' object is not iterable`
- `Resource.pk` field missing in carousel children → `ValidationError`
- `thumbnail_url` is empty string → `ValidationError` (URL parsing)

**The posts ARE still populated before the crash.** The fix: monkey-patch the extractors to catch all exceptions and return minimal dicts on failure.

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

Apply these patches BEFORE calling `user_medias_paginated()`.

### Pagination Loop

```python
posts = []
end_cursor = None
while True:
    try:
        batch, end_cursor = cl.user_medias_paginated(uid, 50, end_cursor=end_cursor)
        for p in batch:
            mt = p.media_type
            posts.append({
                'id': str(p.pk),
                'code': p.code,
                'type': 'carousel' if mt == 8 else 'video' if mt == 2 else 'image',
                'caption': (p.caption_text or '')[:500],
                'taken_at': str(p.taken_at) if p.taken_at else '',
            })
        if not end_cursor:
            break
        time.sleep(2)  # rate limit
    except Exception as e:
        # Even on error, batch may have partial results
        time.sleep(10)
        if not end_cursor:
            break
```

---

## Step 2: Carousel Slides + OCR

For each carousel post, get slide image URLs via `cl.media_info(pk)`:

```python
info = cl.media_info(pk)
resources = info.resources  # list of Resource objects

for j, res in enumerate(resources):
    img_url = str(res.thumbnail_url)
    # Download with requests session
    r = session.get(img_url, timeout=30)
    # OCR with pytesseract
    from PIL import Image
    import pytesseract
    img = Image.open(img_path)
    text = pytesseract.image_to_string(img).strip()
```

### Dependencies
```bash
apt install tesseract-ocr
pip install --break-system-packages pytesseract Pillow instagrapi
```

### Output Format (Markdown)
```markdown
# {shortcode}

**Date**: {timestamp}
**Likes**: {count} | **Comments**: {count}
**Slides**: {n}

## Caption

{full caption text}

## Slides

### Slide 1

{OCR text from slide 1}

### Slide 2

{OCR text from slide 2}
```

---

## Step 3: Direct GraphQL API (Fallback)

If instagrapi's pagination is entirely broken, use the GraphQL endpoint directly with saved cookies:

```python
session = requests.Session()
session.cookies.update({
    'sessionid': sessionid,
    'ds_user_id': ds_user_id,
})
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
    'X-IG-App-ID': '936619743392459',
})

params = {
    'query_hash': '69cba40317214236af40e7efa697781d',
    'variables': json.dumps({'id': USER_ID, 'first': 50, 'after': cursor})
}
resp = session.get('https://www.instagram.com/graphql/query', params=params)
```

**Pitfall:** Instagram may return `{"spam": true}` if the User-Agent or headers look bot-like. Use mobile User-Agent strings and add realistic delays (1.5-2s between requests).

---

## Pitfalls

1. **2FA flow**: Trigger first, ask for code second. Never ask the user to preemptively find a code.
2. **Session storage**: `cl.dump_settings()` stores cookies in `authorization_data`, not `cookies` dict. The `cookies` dict may be empty after a fresh login — that's normal.
3. **instagrapi extractor crashes**: Data populates before crash. Don't give up — monkey-patch and catch.
4. **Rate limiting**: Instagram rate-limits aggressively. Use 2s delays between pages, 10s on errors. The public API (`user_id_from_username`) is especially sensitive to 429s — cache the user ID after first lookup.
5. **High post counts (500+)**: Break into sessions. Don't try to fetch all 940+ posts in one go without breaks.
6. **Tesseract OCR quality**: Text-heavy slides with fancy fonts may OCR poorly. Consider pre-processing (thresholding, contrast enhancement) for better results. For critical text, fall back to manual review of the downloaded slide images.

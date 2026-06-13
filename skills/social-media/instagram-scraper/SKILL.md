---
name: instagram-scraper
description: Scrape Instagram posts — carousels, videos, images with OCR transcription. Direct GraphQL API approach that bypasses instagrapi extractor bugs.
version: 1.0.0
tags: [instagram, scraping, OCR, social-media, carousel, research]
---

# Instagram Scraper

Full-scrape an Instagram account — index all posts, download carousel slides, OCR text from images, transcribe video audio. Built after fighting instagrapi extractor bugs and Instagram rate limits.

## Trigger

Use when user asks to scrape Instagram content, download posts from an account, extract text from Instagram carousels, or catalog an Instagram profile's content.

## Core Pattern: Raw GraphQL > instagrapi Extractors

instagrapi's extractors crash on null `video_versions` and missing `Resource.pk` fields. The data still populates before the crash, but the library is unreliable for paginated carousel-heavy accounts.

**Preferred approach**: Use instagrapi ONLY for auth + cookie extraction, then hit Instagram's GraphQL API directly with `requests`.

```python
from instagrapi import Client

# 1. Auth via instagrapi
cl = Client()
cl.load_settings(session_file)  # or cl.login(user, pass)

# 2. Extract cookies
cookies = {}
for c in cl.private.cookies:
    cookies[c.name] = c.value
settings = cl.get_settings()
for k in ['sessionid', 'csrftoken', 'ds_user_id', 'mid']:
    v = settings.get(k, '')
    if v and k not in cookies:
        cookies[k] = v

# 3. Direct GraphQL calls
session = requests.Session()
session.cookies.update(cookies)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 ...',
    'X-IG-App-ID': '936619743392459',
})

# Paginate
resp = session.get('https://www.instagram.com/graphql/query', params={
    'query_hash': '69cba40317214236af40e7efa697781d',
    'variables': json.dumps({"id": user_id, "first": 50, "after": cursor})
})
```

See `references/graphql_schema.md` for the full response shape.

## instagrapi Extractor Patch

If you must use instagrapi's pagination, patch two lines in `/usr/local/lib/python3.12/dist-packages/instagrapi/extractors.py`:

```diff
-    if "video_versions" in media:
+    if media.get("video_versions"):
```

Both in `extract_media_v1` (line ~53) and `extract_resource_v1` (line ~182). Without this, any post with a null `video_versions` field crashes pagination.

## User ID Caching

`cl.user_id_from_username()` burns a rate-limited API call. Cache the user ID after first lookup. The public endpoint (`/api/v1/users/web_profile_info/?username=...`) hits 429 fast on repeated calls.

## Pitfalls

### 1. Stale Sessions
instagrapi sessions go cold — cookie jar empties, settings lose sessionid. Always verify cookies after `load_settings()`:
```python
assert len(cl.private.cookies) > 0, "Session is stale — re-login needed"
```

### 2. Two-Factor Authentication

The user's account has 2FA enabled. Do NOT ask "do you have it handy" or tell them to go find a code. The pattern:

1. **Trigger login without code** — it fails with "Two-factor authentication required"
2. **Ask briefly**: "Code triggered. Send it — I've got 20 seconds."
3. **User sends the 6-digit code**
4. **Call `cl.login(user, pass, verification_code='XXXXXX')` within 20 seconds of receiving**
5. **Save**: `cl.dump_settings('insta_session.json')`

```python
# Trigger
try:
    cl.login(user, pass)
except Exception as e:
    print(f'NEED_CODE:{e}')  # user fires back code

# Complete (within 20s of receiving code)
cl.login(user, pass, verification_code='370651')
cl.dump_settings('insta_session.json')
```

### 3. Rate Limiting (429)
Instagram rate-limits aggressively. Spread requests with `time.sleep(2)` between pages, `time.sleep(0.5)` between slide downloads. If you hit 429, back off 30+ seconds before retry.

### 4. Image Compression — ALWAYS

Compress images at download time to minimize disk footprint. Instagram originals are large. After downloading each slide/frame:

```python
img = Image.open(img_path)
img.thumbnail((800, 800), Image.LANCZOS)  # max 800px
img = img.convert('RGB')
img.save(img_path, 'JPEG', quality=70, optimize=True)
```

Apply to carousel slides AND extracted video frames. Delete originals after compression.

### 5. Large Accounts
Accounts with 500+ posts will take hours. Offer to batch: first N posts, then resume. Save index.json after the indexing pass so OCR can resume if interrupted.

### 6. Session Expiry Mid-Scrape
Instagram sessions expire during long scrapes. Symptoms: `JSONDecodeError` with HTML login page in API responses, `spam: true`, or empty cookie jars. Recovery: kill stuck process, count `*.md` files already done, re-auth with 2FA workflow, resume (processing scripts skip posts with existing `.md`). Design all processing scripts to be resumable — check file existence before processing each post.

## Carousel Slide OCR

For text-heavy carousel slides:
- Download each slide image from `edge_sidecar_to_children` → `display_resources` (last entry = highest quality)
- OCR with tesseract: `pytesseract.image_to_string(PIL.Image.open(path))`
- Prerequisite: `apt install tesseract-ocr && pip install pytesseract Pillow`

## Output Structure

```
theaethervault_posts/
  index.json          # [{id, shortcode, type, caption, slide_count, resources: [url, ...]}, ...]
  {post_id}.md        # Caption + slide text per post
  {post_id}_slides/   # Downloaded slide images
    slide_01.jpg
    slide_02.jpg
    ...
```

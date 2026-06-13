---
name: instagram-scraper
description: Scrape Instagram profiles, posts, stories, reels, highlights and transcribe audio/video content. Multi-strategy cascade for data extraction with anti-detection.
version: 1.2.0
tags: [instagram, scraping, transcription, social-media, data-collection]
---

# Instagram Scraper & Transcriber

Scrape Instagram accounts for posts, stories, reels, highlights, and profile data. Transcribe video/audio content. Multi-strategy cascade for anti-detection.

## Strategy Cascade (try in order)

**CRITICAL: Do NOT use raw GraphQL with extracted cookies.** instagrapi's `load_settings()` does not populate `cl.private.cookies` even after successful auth — the cookie jar returns 0. This causes HTTP 401 on every direct GraphQL call via `requests`. Use instagrapi's own `user_medias_paginated()` with safe extractor patches instead.

### Working Approach — instagrapi Pagination

```python
import instagrapi.extractors as ex
import instagrapi.types as t

# MUST monkey-patch BEFORE any pagination — instagrapi crashes on null pk fields
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

**User ID caching**: `cl.user_id_from_username()` burns a rate-limited API call. Cache the ID after first lookup and hardcode it in subsequent script runs:
```python
uid = "80613859450"  # hardcoded after first lookup — skip user_id_from_username()
```

**Output visibility**: Python buffers stdout when piped. Run with `python3 -u` and `tee` to log files:
```bash
python3 -u scrape_account.py 2>&1 | tee /tmp/account_scrape.log
```

## Strategy Cascade (try in order)

1. **scrapling** — HTTP-based, fastest, least detectable
2. **browser-harness (CDP)** — Headful browser, handles dynamic content
3. **firecrawl** — Render-js mode for JS-heavy pages
4. **agent-browser** — Full browser automation for login-walled content

## Protocol

### Phase 1 — Profile Data

**Scrape script template**: `scripts/scrape_account.py` — parameterized, resumable GraphQL scraper. Fatal-exits on HTTP 401 instead of infinite-retrying. Usage: `IG_ACCOUNT=name IG_USER_ID=123 python3 scripts/scrape_account.py`
```
Target: instagram.com/<username>/
Extract:
  - Bio, profile pic URL, follower/following counts
  - Post count, account type (personal/business/creator)
  - External links, contact info
  - Story highlights list
```

### Phase 2 — Post Feed
```
Target: instagram.com/<username>/?__a=1&__d=1 (legacy API, try first)
Fallback: browser-harness CDP scroll + extract
Extract per post:
  - Shortcode, timestamp, caption text
  - Media URLs (images/videos), dimensions
  - Like/comment counts
  - Tagged accounts, hashtags, location
```

### Phase 3 — Stories & Highlights
```
Stories: instagram.com/stories/<username>/ (requires auth)
Highlights: instagram.com/stories/highlights/<highlight_id>/
Extract:
  - Media URL, duration, timestamp
  - Overlay text (OCR if needed)
  - Mentions, stickers, links
```

### Phase 4 — Reels
```
Target: instagram.com/reel/<shortcode>/
Extract:
  - Video URL, duration, caption
  - Audio track info
  - Like/comment/play counts
```

### Phase 5 — Transcription
```
For video posts, reels, stories with audio:
1. Download media via firecrawl or direct URL
2. Run speech-to-text (Whisper via local/hermes STT)
3. Extract text overlays via OCR
4. Merge transcript with caption for full context
```

## Authentication & 2FA Workflow

Credentials stored in `~/.hermes/instagram_creds.env`:
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

**Before any scrape, verify the creds file exists and is populated.** The template may exist but be empty — check for actual values:
```bash
grep -q 'INSTAGRAM_USERNAME=.' ~/.hermes/instagram_creds.env && echo "OK" || echo "MISSING — ask user"
```

### 2FA Login Protocol (Critical — Instagram requires 2FA on new sessions)

1. **Initiate login**: browser-harness navigates to `instagram.com/accounts/login/`
2. **Enter credentials**: Type username + password from env vars
3. **2FA prompt appears**: Instagram sends push notification or requests authenticator code
4. **Agent signals user then IMMEDIATELY KILLS CHAT**: Output `🔐 2FA REQUIRED — send code within 30 seconds` then STOP. The agent MUST halt/stop/kill the chat here. WebUI message queue blocks user messages when agent is in "working" state — messages get stuck at ~2% sending progress. Kill the chat so the user's message can get through.
5. **User sends code**: User copies code from Google Authenticator, sends to agent in a NEW chat turn (now that the previous turn is stopped)
6. **Agent enters code immediately**: Must submit within the 30-second window before session expires. The agent resumes fresh, reads the code from the user's message, and completes the 2FA flow
7. **Save session**: After successful auth, save browser session state (cookies + local storage) to `~/.hermes/instagram_session.json`
8. **Reuse session**: On subsequent runs, load saved session first — skip login entirely. Only re-auth when session expires (~7-14 days)

### Session Kill Pattern
When 2FA hangs or Instagram rate-limits:
1. Kill the browser session
2. Delete `~/.hermes/instagram_session.json`
3. Wait 5 minutes
4. Restart login flow fresh

## Phase 6 — Google Drive Sync & Organization

After scraping completes, carousel slides must be synced to Google Drive at `Instagram_Scrapes/{account}/slides/`. The upload can silently fail partway through (API rate limits, token expiry, network drops). **Always verify post-upload.**

### 6a — Upload to Google Drive

**Method A: Direct folder upload (preferred)** — Skip zip roundtrip entirely. Upload slide folders directly:

```bash
cd {account}_posts
rclone copy . "gdrive_personal:Instagram_Scrapes/{account}/slides/" \
    --include "*_slides/**" --ignore-existing -P -v
```

**Method A-alt: Upload specific missing folders** — When only a subset needs uploading (identified via `comm -23` diff):

```bash
cd {account}_posts
comm -23 /tmp/vps_dirs.txt /tmp/drive_dirs.txt | while read d; do
    rclone copy "$d" "gdrive_personal:Instagram_Scrapes/{account}/slides/$d/" -P --ignore-existing
done
```

**PITFALL: `rclone copy --files-from` does NOT work with directories** — it silently reports "There was nothing to transfer" because it treats every entry as a file path, not a directory. Always use `--include` patterns or explicit per-directory `rclone copy` calls for folder uploads.

**Method B: Zip then upload** — If the user requests zip archives on Drive:

```bash
cd {account}_posts
for d in *_slides/; do
    zip -r "/tmp/{account}_zips/${d%/}.zip" "$d"
done
rclone copy /tmp/{account}_zips/ "gdrive_personal:Instagram_Scrapes/{account}/slides/" -P -v
```

### 6b — Extraction on Drive

If zips were uploaded, extract them on Drive by pulling back down, unzipping, and re-uploading extracted folders:

```bash
mkdir -p /tmp/{account}_extract && cd /tmp/{account}_extract
# Pull all zips
rclone copy "gdrive_personal:Instagram_Scrapes/{account}/slides/" . --include "*.zip" -P
# Unzip each into its own folder
for f in *.zip; do unzip -o "$f" -d "${f%.zip}/"; done
# Push extracted folders back (skip zips)
rclone copy . "gdrive_personal:Instagram_Scrapes/{account}/slides/" --exclude "*.zip" --ignore-existing -P
```

### 6c — Upload Verification (MANDATORY)

After any upload, **verify the count matches**. Partial uploads are silent — the only symptom is a count mismatch:

```bash
# Count carousel directories on VPS
ls -d *_slides/ | wc -l

# Count slide folders on Drive
rclone lsf "gdrive_personal:Instagram_Scrapes/{account}/slides/" --dirs-only | wc -l
```

If counts don't match: identify missing folders with `comm -23`, then re-upload only the missing:

```bash
ls -d *_slides/ | sed 's|/$||' | sort > /tmp/vps_dirs.txt
rclone lsf "gdrive_personal:Instagram_Scrapes/{account}/slides/" --dirs-only | sed 's|/$||' | sort > /tmp/drive_dirs.txt
comm -23 /tmp/vps_dirs.txt /tmp/drive_dirs.txt  # these are missing → re-upload
```

Example: `@theaethervault` scrape had 162 carousels but only 65 reached Drive — 97 stranded on VPS.

### 6d — Rename by Hybrid Taxonomy (POST-UPLOAD)

Numeric folder names (`3822154384344394057_slides`) are opaque. After upload, rename all slide folders using the hybrid taxonomy extracted from the `.md` OCR files:

**Naming convention: `YYYY-MM-DD Subject-Slug -- IG-SHORTCODE`**

Example output:
```
2026-04-05 the-karma-scam-decoding-epigenetic-virus -- DWwCyO1jCV7
2024-03-05 the-book-of-light-out -- C4I-ibxtkRe
2025-03-21 how-to-quit-weed-take-back -- DHdlL4bInLN
```

**Extraction script** (`scripts/hybrid_rename.sh` — run locally, then apply renames on Drive via rclone):

```bash
cd {account}_posts
for md in *.md; do
    dir="${md%.md}_slides"
    [ ! -d "$dir" ] && continue
    
    shortcode=$(head -1 "$md" | sed 's/^# //')
    date=$(grep -m1 "Date" "$md" | grep -oP '\d{4}-\d{2}-\d{2}')
    caption=$(sed -n '/^## Caption/{n;n;p}' "$md" | head -1)
    
    # Build slug: first 6 words, lowercase, hyphens
    slug=$(echo "$caption" | tr -c '[:alnum:] ' ' ' | tr -s ' ' | \
            cut -d' ' -f1-6 | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
    
    [ -z "$date" ] && date="unknown-date"
    [ -z "$slug" ] && slug="untitled"
    
    new_name="${date} ${slug} -- ${shortcode}"
    # Apply rename on Drive:
    rclone moveto "gdrive_personal:Instagram_Scrapes/{account}/slides/${dir}" \
                  "gdrive_personal:Instagram_Scrapes/{account}/slides/${new_name}" -P
done
```

**Why this taxonomy wins:**
1. **Date-first** → natural chronological sort, reveals account evolution over time
2. **Subject slug** → instant recognition, scannable, searchable in Windows/Drive
3. **Shortcode preserved** → `instagram.com/p/SHORTCODE` still works for source lookups
4. **Scriptable** — every `.md` already contains date + shortcode + caption; no subjective guessing

## Pre-Scrape Auth Validation (MANDATORY)

**Never launch a scrape without validating the session first.** A stale session produces HTTP 401 on every GraphQL request and the retry loop will spin forever (1hr+ wasted). Always run this check before any scrape script:

```bash
python3 -c "
from instagrapi import Client
cl = Client()
cl.load_settings('insta_session.json')
cookies = len(cl.private.cookies)
print(f'Cookies: {cookies}')
assert cookies > 0, 'SESSION DEAD — re-auth required'
print('SESSION VALID')
"
```

If cookies == 0: delete the session file, re-auth via 2FA workflow, and save fresh session before launching any scrape.

### Stale Session Recovery

If a scrape is already running and produces HTTP 401:
1. **Kill the process immediately** — the retry loop is unbounded
2. **Delete** `insta_session.json` to force clean re-auth
3. **Re-auth** via 2FA workflow
4. **Restart** the scrape script (it auto-resumes — skips posts with existing `.md` files)

### 2FA Timing (CRITICAL)

After triggering login and receiving the 2FA code, the window is ~20 seconds. **Do not chain user ID lookups or any other API calls in the same Python invocation as the login.** The login + session dump must be the only operations:

```python
# RIGHT: login, dump, exit — then verify separately
cl.login(user, pass, verification_code='XXXXXX')
cl.dump_settings('insta_session.json')
```

```python
# WRONG: chaining lookups eats the 2FA window
cl.login(user, pass, verification_code='XXXXXX')
cl.user_id_from_username('target')  # ← 429/timeout kills the code
```

After session saved, verify in a separate call.

### Credentials File

Credentials live at `~/.hermes/instagram_creds.env`. Verify they exist before attempting auth:

```bash
test -f ~/.hermes/instagram_creds.env && grep -q "INSTAGRAM_USERNAME=" ~/.hermes/instagram_creds.env || echo "MISSING"
```

Template at `~/.hermes/instagram_creds.env.template` if file is missing.

## Anti-Detection

- Rotate user agents per request
- Add random delays (2-8s between requests)
- Use CDP browser with stealth mode (browser-harness)
- Never exceed 50 requests/hour per account
- Cache results to avoid re-scraping

## Output Format

```json
{
  "username": "...",
  "scraped_at": "ISO timestamp",
  "profile": { "bio": "...", "followers": N, ... },
  "posts": [{
    "shortcode": "...",
    "timestamp": "...",
    "caption": "...",
    "media_urls": ["..."],
    "likes": N,
    "comments": N,
    "hashtags": ["..."],
    "mentions": ["..."],
    "transcript": "..." 
  }],
  "stories": [...],
  "highlights": [...],
  "reels": [...]
}
```

## Failure Modes

- **2FA code never arrives**: Agent kept running after signaling — user's message got stuck at 2% in WebUI. Agent MUST kill chat immediately after signaling for 2FA code.
- **Login wall**: Instagram requires auth for stories/highlights — use agent-browser with saved session
- **Rate limiting**: HTTP 429 — back off 15min, rotate IP
- **Empty __a=1 response**: Legacy API disabled — fall back to CDP browser extraction
- **No audio in reel**: Silent reel — skip transcription, flag as no-audio
- **401 retry loop**: Script retries HTTP 401 forever, burning an hour. **Never retry 401.** Session cookies are dead — re-auth is the only fix. GraphQL scrape scripts must bail on first 401, not retry:
```python
if resp.status_code == 401:
    print("SESSION EXPIRED — re-auth required", flush=True)
    sys.exit(1)
```
- **Raw GraphQL cookie extraction returns 401**: `cl.private.cookies` is always empty after `load_settings()` — instagrapi stores auth in `authorization_data`, not the cookie jar. Do NOT attempt to extract cookies for direct `requests` GraphQL calls. Use `cl.user_medias_paginated()` instead.
- **`user_id_from_username` rate-limited**: The public web_profile_info endpoint hits 429 fast. Cache the user ID after first successful lookup and hardcode it for subsequent runs.
- **Python output buffered in background**: stdout vanishes when piped through the terminal tool. Always run scrape scripts with `python3 -u` and `tee` to a log file for visibility.
- **Stale session → infinite HTTP 401 loop**: Scrapes launch with 0 cookies and retry forever. Always run pre-scrape auth validation. If 401 appears mid-scrape, kill process immediately, delete session file, re-auth, restart.
- **2FA code timeout from chained calls**: Login + session dump must be the ONLY operations in a 2FA call. Never chain `user_id_from_username()` or any other API call — they eat the 20-second 2FA window.
- **Credentials file missing**: `~/.hermes/instagram_creds.env` exists only as template. Check before auth: `grep -q "INSTAGRAM_USERNAME=" ~/.hermes/instagram_creds.env`.
- **Partial Drive upload**: Upload silently stops partway (API rate limits, token expiry). Always verify: `ls -d *_slides/ | wc -l` vs `rclone lsf "gdrive:..." --dirs-only | wc -l`. Re-upload missing with `comm -23` + rclone.
- **Zip folder count doesn't match carousel count**: Upload script crashed mid-batch. Use `comm -23` to diff VPS vs Drive directories, re-upload only the missing folders.
- **Numeric folder names on Drive after extraction**: Opaque IG IDs. Run the hybrid rename script (Phase 6d) to apply `YYYY-MM-DD Subject-Slug -- SHORTCODE` naming.

## Dependencies

- instagrapi (auth + pagination with safe extractor patch)
- pytesseract + Pillow (OCR)
- rclone (Google Drive sync)
- requests (slide image download)

## Support Files

- `templates/instagram_scrape_template.py` — Complete working scraper script. Copy and configure ACCOUNT/USER_ID at top.

## Templates

- `templates/scrape_carousels.py` — Proven GraphQL + OCR scraper. Copy, set ACCOUNT and USER_ID, run. Uses instagrapi for cookie auth, hits IG's GraphQL directly for reliability. Resumable (skips existing .md files).

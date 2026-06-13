---
name: instagram-scraping
description: Scrape Instagram profiles — auth with 2FA handling, download posts, transcribe video content. Use instagrapi (not instaloader), manage rate limits, handle 2FA via PTY background processes without locking the user's account.
version: 1.0.0
category: research
---

# Instagram Scraping & Transcription

Complete pipeline for scraping Instagram profiles: authentication (with 2FA), post metadata extraction, video download, and speech-to-text transcription using free local models.

## When to Use

- User wants to scrape an Instagram account's posts for research/analysis
- Need video transcriptions from Instagram Reels
- Building a content research pipeline from Instagram

## Tool Selection

| Tool | Use | Status |
|------|-----|--------|
| `instagrapi` | Primary — authentication, profile queries, post listing, media download | ✅ Works with 2FA |
| `faster-whisper` | Video transcription — CPU-efficient local STT | ✅ Free, no API costs |
| `instaloader` | **DO NOT USE** — outdated GraphQL doc IDs, constant 400 errors | ❌ Broken as of May 2026 |

## Authentication

### 2FA Flow (CRITICAL — read before attempting)

The user's account has 2FA enabled. Every failed login attempt risks account lockout. Follow this protocol EXACTLY:

**PITFALL — Do NOT run parallel tool calls during 2FA code entry.** The user needs a clear, uninterrupted channel to send the 6-digit code. If you continue processing (running other tool calls, searching, writing), your messages will queue the user's code message, the code will expire, and the user will be furious. After firing the login command, STOP. Wait for the code. Submit it immediately.

**Step-by-step:**
```python
# 1. Start login in background PTY
terminal(command="python3 login_script.py", background=True, pty=True, timeout=120)

# 2. Poll for the CODE> prompt
process(action="poll", session_id="...")

# 3. STOP ALL OTHER WORK. Wait for user's code.

# 4. Submit immediately
process(action="submit", data="123456", session_id="...")

# 5. Wait for SESSION_SAVED or LOGIN_OK
process(action="wait", timeout=30, session_id="...")
```

### Login script template

```python
from instagrapi import Client
cl = Client()
try:
    cl.login('username', 'password')
    print('NO_2FA_LOGIN_OK')
except Exception as e:
    if 'verification_code' in str(e) or 'two-factor' in str(e).lower():
        code = input('CODE> ')
        cl.login('username', 'password', verification_code=code.strip())
        cl.dump_settings('/path/to/insta_session.json')
        print('SESSION_SAVED')
    else:
        print(f'ERROR: {e}')
```

### Session reuse

Once authenticated, save and reload sessions:

```python
cl = Client()
cl.load_settings('insta_session.json')  # No 2FA needed
```

## Profile Scraping

```python
user_id = cl.user_id_from_username('target_account')
info = cl.user_info(user_id)
# info.media_count, info.follower_count, info.biography, etc.

# Get ALL posts (amount=0 = all)
medias = cl.user_medias(user_id, amount=0)
for media in medias:
    # media.pk, media.code, media.caption_text, media.media_type
    # media.taken_at, media.like_count, media.comment_count
    # media_type: 1=image, 2=video
```

## Rate Limiting

Instagram aggressively rate-limits. Apply delays:
- Every 25 posts: `time.sleep(2)` 
- Between profile queries: stagger by 1-2 seconds
- If you hit 429 errors, back off for 30+ seconds

## Video Transcription

Use `faster-whisper` (free, CPU-based, no API keys):

```bash
pip install --break-system-packages faster-whisper
```

### Download + transcribe pipeline

```python
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")

# Download video via instagrapi
media_info = cl.media_info(pk)
video_url = str(media_info.video_url)  # or media_info.video_versions[0]['url']

# Extract audio with ffmpeg
os.system(f"ffmpeg -y -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 {audio_path} 2>/dev/null")

# Transcribe
segments, info = model.transcribe(str(audio_path), beam_size=5, language="en")
transcript = " ".join([seg.text for seg in segments])
```

**Model selection:**
- `"tiny"` — fastest, lower accuracy
- `"base"` — good balance (recommended)
- `"small"` — more accurate, slower

## Output Structure

Save each post as an individual markdown file with the post ID as filename:

```
renwellmd_posts/
  123456789.md       # Caption + transcript per post
  index.json          # Machine-readable full index
  MASTER_INDEX.md     # Human-readable summary table
```

## Pitfalls

- **PITFALL — User account lockout risk:** Every failed 2FA attempt = one step closer to lockout. Never retry login on failure without user authorization. Always verify session exists before attempting re-login.
- **PITFALL — Parallel calls during 2FA code:** The #1 cause of user frustration. After firing the login command, STOP ALL PROCESSING. Do not run other tool calls. Wait for the code in a clean channel. If the user's code message gets queued behind your tool outputs, the code expires.
- **PITFALL — instaloader is broken (May 2026):** GraphQL doc IDs are outdated, producing 400 "invalid request" errors. Use `instagrapi` instead.
- **PITFALL — Browser-based login fails:** Instagram detects automated browsers and kills sessions post-2FA (onetap redirect → empty page). Use `instagrapi` with PTY terminal approach.
- **PITFALL — Large video batches:** 150+ videos on CPU transcription takes 1-3 hours. Use `background=true` with `notify_on_complete=true`.
- **PITFALL — ffmpeg required:** Video transcription needs ffmpeg for audio extraction. Install with `apt install ffmpeg` if missing.
- **PITFALL — Whisper model download:** First run downloads the model (~150MB for "base") from HuggingFace. Ensure network access.

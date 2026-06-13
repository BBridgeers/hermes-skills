---
name: instagram-scrape-transcribe
description: Full Instagram profile scraping with video transcription. Auth via instagrapi with 2FA, caption pull, video download + faster-whisper transcription.
version: 1.0.0
tags: [instagram, scrape, transcription, video, research]
---

# Instagram Profile Scrape + Transcribe

Full pipeline: authenticate via instagrapi (handles 2FA), scrape all captions, download videos, transcribe audio with faster-whisper.

## When to Use

- Researching a medical/expert Instagram account's content
- Need full text corpus from video posts for analysis
- Watching an account's content over time

## Prerequisites

```bash
pip install --break-system-packages instagrapi faster-whisper
# ffmpeg must be installed for audio extraction
```

## Step 1: Authenticate (2FA flow)

This step requires user presence for the 2FA code. Use PTY background mode.

### The 2FA Protocol (MUST FOLLOW — account lockout risk)

```
1. User says "go"
2. Agent fires ONE terminal(pty=true, background=true) with login script
3. Agent calls process(action='poll') ONCE to confirm CODE> prompt appeared
4. Agent sends a VERY SHORT message: "Prompt is live. Send the 6-digit code."
   — The message MUST be short so it doesn't queue behind agent output
5. Agent STOPS ALL TOOL CALLS. No snapshots, no polls, no writes. Dead stop.
6. User's code message comes through clean (not queued)
7. Agent calls process(action='submit', data='CODE')
8. Agent calls process(action='wait') for result
```

**Why this matters**: 2FA codes expire in ~30 seconds. If the agent is mid-tool-call when the user's code arrives, the message queues behind tool output and the code expires. This pattern caused multiple failed login attempts and the user explicitly demanded: *"you just have to shut the fuck up and kill the chat long enough for me to be able to get the code through to you quickly"*.

**Auth script** (`/tmp/insta_auth.py`):
```python
from instagrapi import Client
cl = Client()
try:
    cl.login('USERNAME', 'PASSWORD')
    print('NO_2FA_LOGIN_OK')
except Exception as e:
    if 'verification_code' in str(e) or 'two-factor' in str(e).lower():
        code = input('CODE> ')
        cl.login('USERNAME', 'PASSWORD', verification_code=code.strip())
        cl.dump_settings('/root/workspace/detoxxx/insta_session.json')
        print('SESSION_SAVED')
```

Run:
```bash
cd /root/workspace/detoxxx && python3 /tmp/insta_auth.py
```

Session saved to `insta_session.json`. The first login stores it; subsequent runs use `cl.load_settings('insta_session.json')`.

## Step 2: Scrape Captions (optional — skip if video-only)

**Video-only mode**: If the user only wants video transcriptions (no captions/engagement), skip straight to Step 3. The user explicitly stated: *"I really only care about the video posts transcriptions I could give a rats ass about the post engagement nor captions"*. In this mode, only build `index.json` with video posts — no markdown files, no caption scraping.

```python
from instagrapi import Client
import json
from pathlib import Path

cl = Client()
cl.load_settings('insta_session.json')

user_id = cl.user_id_from_username('TARGET_USERNAME')
OUTDIR = Path('TARGET_posts')
OUTDIR.mkdir(exist_ok=True)

medias = cl.user_medias(user_id, amount=0)  # 0 = all posts

posts_data = []
for media in medias:
    post = {
        'id': media.pk,
        'code': media.code,
        'date': str(media.taken_at),
        'caption': media.caption_text or '',
        'type': 'video' if media.media_type == 2 else 'image' if media.media_type == 1 else 'carousel',
        'url': f'https://www.instagram.com/p/{media.code}/',
    }
    
    # Save as markdown
    md_file = OUTDIR / f"{media.pk}.md"
    md_file.write_text(f"# Post {media.code}\n\n**Date**: {post['date']}\n**Type**: {post['type']}\n**URL**: {post['url']}\n\n## Caption\n\n{post['caption']}\n")
    posts_data.append(post)

with open(OUTDIR / 'index.json', 'w') as f:
    json.dump(posts_data, f, indent=2)
```

**Rate limit note**: Add `time.sleep(2)` every 25 posts to avoid getting throttled.

## Step 3: Download + Transcribe Videos

**Known issue**: instagrapi sessions are fragile for video downloads. Sessions expire quickly when used from Python vs browser. 

**Workaround strategy**:
- Re-authenticate every 20 videos
- Use `requests` with browser-like User-Agent for video downloads
- Skip already-transcribed videos (idempotent)

```python
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu", compute_type="int8")

for vid in videos_to_process:
    # Get video URL
    info = cl.media_info(pk)
    url = str(info.video_url)
    
    # Download
    r = requests.get(url, timeout=90, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    })
    video_path.write_bytes(r.content)
    
    # Extract audio with ffmpeg
    os.system(f"ffmpeg -y -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 {audio_path} 2>/dev/null")
    
    # Transcribe
    segments, info = model.transcribe(str(audio_path), beam_size=5, language="en")
    transcript = " ".join([seg.text for seg in segments])
    
    # Append to markdown
    content = md_file.read_text()
    content += f"\n## Transcription\n\n{transcript}\n"
    md_file.write_text(content)
```

## Alternative: yt-dlp for Video Downloads

When instagrapi session keeps dying, fall back to `yt-dlp` for video download only:

```bash
# Download single video
yt-dlp -o "/tmp/video.%(ext)s" "https://www.instagram.com/p/CODE/" --cookies-from-browser chrome

# Batch download all videos from profile
yt-dlp -o "%(id)s.%(ext)s" "https://www.instagram.com/TARGET/" --cookies-from-browser chrome
```

## Pitfalls

- **DO NOT use `cl.private.cookies` or `cl.private.cookie_dict`**: These instagrapi internals hang indefinitely (no timeout) and produce zero output. Discovered in `resume2.py` failure — process ran 11+ seconds with empty output. Use the stored session file + re-auth instead.
- **Session death**: instagrapi sessions expire fast from Python. The `dump_settings`/`load_settings` approach is fragile. Session died at 73/162 (45%) and again at 76/162 (47%). When this happens, the ONLY fix is a fresh 2FA login — no workaround. Re-auth using the same Step 1 protocol.
- **DO NOT attempt `cl.login()` with stale credentials inside exception handlers**: If the session is dead, silent re-login always fails (triggers 2FA with no interactive handler). Kill the process and re-auth from scratch.
- **Video-only vs full scrape**: Ask upfront. If user only wants transcriptions, skip caption scraping entirely — saves time and API calls.
- **2FA timing**: Instagram 2FA codes expire in ~30 seconds. The protocol in Step 1 is mandatory.
- **Rate limiting**: Instagram aggressively rate-limits. Space requests (time.sleep(2) every 25 items).
- **Video URLs expire**: Downloaded video URLs only valid for a few minutes — download immediately after getting the URL.
- **faster-whisper on CPU**: ~30-60s per minute of audio. 162 videos = ~2-4 hours.
- **Browser approach fails for scraping**: Instagram detects automated browsers (Cloudflare, bot detection). The browser-based login hit 2FA but session was killed post-login. Use Python/instagrapi, not browser tools.

## Workspace Scripts

These are battle-tested scripts from the renwellmd scrape (76/162 transcribed). Copy and adapt for new targets:

| Script | Purpose |
|--------|---------|
| `/root/workspace/detoxxx/transcribe_videos.py` | First-pass transcription (instagrapi session approach, fragile) |
| `/root/workspace/detoxxx/resume_transcribe.py` | yt-dlp fallback attempt (cookie extraction hung) |
| `/root/workspace/detoxxx/resume2.py` | Direct cookie approach (HUNG — `cl.private.cookies` blocking) |
| `/root/workspace/detoxxx/insta_session.json` | Working session file (requires periodic re-auth)

## Post-Scrape: Carousel Slide Organization

Carousel posts produce per-post `*_slides/` directories with individual JPEGs. After scraping, these need to be zipped, uploaded to Google Drive, extracted, and named for long-term usability. See `references/carousel-slide-organization.md` for:

- **Hybrid naming taxonomy**: `[YYYY-MM-DD] Subject-Slug — IG-Shortcode` (chronological + scannable + traceable)
- **Drive upload pattern**: zip → rclone copy → pull → extract → push back (never unzip on FUSE mount)
- **Cross-reference verification**: `comm -23` to find slides missing from Drive
- **theaethervault case study**: 162 carousels, 65 uploaded, 98 missing, full resolution pattern

## Output Structure

```
TARGET_posts/
├── index.json           # Machine-readable post data
├── MASTER_INDEX.md      # Human-readable table
├── 123456789.md         # Post with caption
└── 123456789.md         # Post with caption + transcription
```

## Resuming

The pipeline is idempotent — skip posts that already have `## Transcription` in their markdown file. Safe to kill and restart.

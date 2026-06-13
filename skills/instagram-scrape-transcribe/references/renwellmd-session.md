# renwellmd Session Log (May 26, 2026)

## Account
- **Handle**: @renwellmd
- **Name**: renwellMD  
- **Bio**: I was a HOSPITALIST physician turned Babylon and real health whistleblower. I don't do labels… Except Aquarius.
- **Followers**: 28,544
- **Following**: 1,699
- **Posts**: 283 (281 scraped)
- **Private**: No
- **Verified**: Yes

## Post Breakdown
- Video: 162
- Image: 67
- Carousel: 52

## Progress
- Captions scraped: 281 ✓
- Videos transcribed: 76/162 (47%)
- Remaining: 86 videos

## What Worked
1. **instagrapi** auth via PTY background + 2FA code submission — clean, fast
2. Caption scraping with `cl.user_medias(user_id, amount=0)` — all 281 posts in one pass
3. **faster-whisper** model="base" on CPU — workable, ~30-60s per minute of audio
4. Idempotent resume: check for `## Transcription` in markdown before processing

## What Failed
1. **instaloader**: GraphQL DOC IDs outdated, `400 Bad Request` on all profile queries
2. **Browser approach**: Login worked but post-login session killed (onetap redirect → empty page)
3. **instagrapi session death**: Sessions expire after ~70 video downloads. No workaround except re-auth with 2FA.
4. **`cl.private.cookies`**: Hangs indefinitely. Do not use.
5. **yt-dlp cookie extraction**: Failed — couldn't extract cookies from instagrapi session.
6. **Auto-re-login in exception handlers**: Always triggers 2FA with no handler. Dead end.

## URLs
- Profile: https://www.instagram.com/renwellmd/

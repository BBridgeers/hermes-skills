# Carousel Slide Organization & Naming Taxonomy

Post-scrape workflow for Instagram carousel posts: how slide images are stored, zipped, uploaded to Google Drive, extracted, and named for long-term usability.

## The Problem

Instagram scrapers (instagrapi, yt-dlp, browser-based) download carousel slide images into per-post directories, typically named by the Instagram numeric post ID:

```
theaethervault_posts/
├── 3868604327908877691_slides/    # ← opaque numeric ID
│   ├── slide_01.jpg
│   ├── slide_02.jpg
│   └── ...
├── 3868604327908877691.md          # OCR caption + metadata
```

Numeric IDs are machine-unique but useless for human browsing. After scraping 162 carousels, finding a specific post means opening folders one by one.

## The Taxonomy: Hybrid Naming

**Format**: `[YYYY-MM-DD] Subject-Slug — IG-Shortcode`

| Component | Source | Example |
|-----------|--------|---------|
| `YYYY-MM-DD` | `.md` file `**Date**:` field | `2026-04-05` |
| `Subject-Slug` | First sentence of OCR caption, truncated | `Karma-Scam-Epigenetic-Virus` |
| `IG-Shortcode` | `.md` file `# HEADER` (first line) | `DWwCyO1jCV7` |

**Real example**:
```
3868604327908877691_slides/  →  2026-04-05 Karma-Scam-Epigenetic-Virus — DWwCyO1jCV7/
```

### Why This Wins

1. **Chronological sorting** — date prefix sorts oldest→newest naturally
2. **Instantly scannable** — subject keyword tells you what it is without opening
3. **Traceable** — shortcode preserved: `instagram.com/p/DWwCyO1jCV7/`
4. **Scriptable** — every `.md` file already contains the date, shortcode, and caption text

### Scripted Rename

```python
from pathlib import Path
import re, json

posts_dir = Path("/root/workspace/detoxxx/theaethervault_posts")

for md_file in sorted(posts_dir.glob("*.md")):
    post_id = md_file.stem
    slides_dir = posts_dir / f"{post_id}_slides"
    if not slides_dir.exists():
        continue
    
    content = md_file.read_text()
    shortcode = content.split('\n')[0].replace('# ', '').strip()
    date_match = re.search(r'\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
    date = date_match.group(1) if date_match else "0000-00-00"
    
    # Extract caption first meaningful line
    caption_section = content.split('## Caption\n\n')
    if len(caption_section) > 1:
        caption_text = caption_section[1].split('\n\n')[0].strip()
        # First 4-5 words as slug
        slug = '-'.join(caption_text.split()[:5])
        slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)[:60]
    else:
        slug = "untitled"
    
    new_name = f"{date} {slug} — {shortcode}"
    print(f"  {slides_dir.name}/  →  {new_name}/")
```

## Drive Upload Pattern

After scraping, carousel slides need to be on Google Drive for the user's Windows laptop (H: drive via rclone mount). The reliable pattern:

### 1. Zip locally on VPS
```bash
cd /root/workspace/detoxxx/theaethervault_posts
for d in *_slides/; do
    zip -r "/tmp/slides_zips/${d%/}.zip" "$d"
done
```

### 2. Upload zips to Drive
```bash
rclone copy /tmp/slides_zips/ "gdrive_personal:Instagram_Scrapes/TARGET/slides/" \
    --include "*.zip" -P
```

### 3. Pull zips back down locally, extract, push extracted folders
```bash
# Pull
mkdir -p /tmp/work && cd /tmp/work
rclone copy "gdrive_personal:Instagram_Scrapes/TARGET/slides/" . --include "*.zip" -P

# Extract
for f in *.zip; do unzip -o "$f" -d "${f%.zip}/"; done

# Push extracted folders (skip existing)
rclone copy . "gdrive_personal:Instagram_Scrapes/TARGET/slides/" \
    --exclude "*.zip" --ignore-existing -P
```

Never unzip directly on the rclone FUSE mount — every file write triggers a GDrive API call, rate limits kick in, and the operation stalls.

### 4. Cross-reference: find what's missing

```bash
# List VPS slides
ls -d /root/workspace/detoxxx/TARGET_posts/*_slides/ | sed 's|.*/||; s|/$||' | sort > /tmp/vps.txt

# List Drive slides
rclone lsf "gdrive_personal:Instagram_Scrapes/TARGET/slides/" --dirs-only | \
    sed 's|/$||' | sort > /tmp/drive.txt

# Missing from Drive
comm -23 /tmp/vps.txt /tmp/drive.txt
```

## theaethervault Case Study (2026-06-07)

- **798** total posts scraped
- **162** carousels (multi-slide posts) → 1,555 slide images on VPS
- Only **65** zips made it to Drive (original upload script failed at ~40%)
- **98** missing carousels identified via `comm -23` cross-reference
- Remaining 64 zips extracted in place on Drive using the pull-extract-push pattern
- All .md files with OCR captions intact at `/root/workspace/detoxxx/theaethervault_posts/`

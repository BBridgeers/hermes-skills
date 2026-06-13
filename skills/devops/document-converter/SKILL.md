---
name: document-converter
description: Convert EPUB/PDF/DOCX/HTML documents between formats (MD, DOCX, PDF, EPUB) using pandoc. Drive-integrated — download, convert, upload back. Use when the user asks to convert documents, especially from Google Drive folders.
version: 1.0.0
category: devops
---

# Document Converter

Batch convert documents between formats using pandoc with Google Drive integration. Download from Drive, convert locally, upload results back.

## Trigger Conditions

- User asks to convert EPUB, PDF, DOCX, or HTML files to Markdown, DOCX, or other formats
- User references a Drive folder with documents to convert
- User mentions "convert to markdown," "convert to docx," "convert EPUB"
- User asks for a "document conversion skill"

## Tool Dependencies

- **pandoc** (required): `apt install -y pandoc`
- **Calibre** (optional, for EPUB→PDF with better fidelity): `apt install -y calibre`
- Pandoc is preferred for most conversions — it's faster and produces cleaner text output. Calibre's `ebook-convert` is a fallback for complex EPUBs that pandoc struggles with.

## Supported Conversions

| From | To | Command | Notes |
|------|----|---------|-------|
| EPUB | MD | `pandoc input.epub -o output.md --wrap=none` | Best results. `--wrap=none` prevents line-break mangling |
| EPUB | DOCX | `pandoc input.epub -o output.docx` | Good results, preserves structure |
| EPUB | PDF | `ebook-convert input.epub output.pdf` | Calibre required. Pandoc EPUB→PDF needs LaTeX |
| PDF | MD | `pandoc input.pdf -o output.md --wrap=none` | Text extraction only — no image extraction |
| DOCX | MD | `pandoc input.docx -o output.md --wrap=none` | Best results |
| HTML | MD | `pandoc input.html -o output.md --wrap=none` | Excellent results |
| MD | DOCX | `pandoc input.md -o output.docx` | Good results |
| MD | PDF | `pandoc input.md -o output.pdf --pdf-engine=xelatex` | Needs texlive-xetex |

## Workflow

### Phase 1: Find Source Files
1. If user specifies a Drive folder name, search for it: query Drive API with `name contains '<folder_name>' and mimeType='application/vnd.google-apps.folder'`
2. List all target-format files in the folder: `q="'<folder_id>'+in+parents+and+fileExtension='epub'"`
3. Report count and sizes to user

### Phase 2: Download
Use the Google Drive API with OAuth token at `/root/.hermes/google_token.json` (key name is `'token'`):

```python
import json, urllib.request
with open('/root/.hermes/google_token.json') as f:
    access_token = json.load(f)['token']

url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media'
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
content = urllib.request.urlopen(req).read()
with open(local_path, 'wb') as f:
    f.write(content)
```

Always refresh the OAuth token first: `python3 /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`

### Phase 3: Convert
Process all files in a batch script in `/tmp/epub_convert/`. For each file:
1. Sanitize filename (remove special chars, limit length to 80 chars)
2. Run pandoc conversion
3. Verify output file exists and has content
4. Record results with sizes

### Phase 4: Upload
Upload all converted files back to the same Drive folder:

```python
from googleapiclient.http import MediaFileUpload
# Get service from drive-download-workaround helper
media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
service.files().create(
    body={'name': filename, 'parents': [folder_id], 'mimeType': mime_type},
    media_body=media, fields='id,name,size,webViewLink'
).execute()
```

MIME types:
- `.md` → `text/markdown`
- `.docx` → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- `.pdf` → `application/pdf`

### Phase 5: Report
For each file: original name, converted formats, file sizes, and Drive file IDs.

## Batch Conversion Pattern

```bash
mkdir -p /tmp/epub_convert && cd /tmp/epub_convert
python3 << 'PYEOF'
import json, urllib.request, subprocess, os
# ... download all, convert all, save results to results.json
PYEOF
```

Then upload from results.json in a second step.

## Google Drive Auth

- Account: dfwwebdesignnow@gmail.com
- OAuth token: `/root/.hermes/google_token.json` (key: `'token'`)
- Refresh: `python3 /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --check`
- Helper module: `/root/.hermes/skills/productivity/google-workspace/references/drive-download-workaround.py` (has `_get_drive_service()`)

## Pitfalls

- **Pandoc EPUB→PDF needs LaTeX**: Use Calibre's `ebook-convert` instead for EPUB→PDF
- **EPUBs with DRM**: Cannot be converted. Pandoc will fail silently or produce garbage output
- **Large files (>50MB)**: Don't download to `/tmp/` if tmpfs is small. Use `/root/tmp/` instead
- **Filename length**: Google Drive allows long filenames but pandoc may choke. Sanitize to 80 chars max
- **Token expiry**: Always run `--check` before starting. Token can expire mid-batch on large files
- **MediaFileUpload for large files**: Set `resumable=True` for files over 5MB
- **`--wrap=none`** is critical for MD output — without it, pandoc hard-wraps at 72 chars, mangling tables and code blocks
- **Large markdown → Google Doc**: Do NOT use the Docs API `batchUpdate` for files over ~500KB. Google Docs silently rejects `insertText` requests once the document reaches ~1.5MB with `"Precondition check failed"`. Instead, convert to .docx via pandoc and upload — Drive renders .docx as native Google Doc. See `references/markdown-to-google-doc.md` for full writeup and measured limits.
- **`--reference-doc=/dev/null` breaks pandoc**: Causes `Data.Binary.Get.runGet at position 0: not enough bytes`. Omit `--reference-doc` entirely unless you have a real reference docx file.
- **Pandoc resource usage**: A 2.2MB markdown file (~19k lines) takes ~4 min at 99% CPU and ~770MB RAM to convert. Plan accordingly for batch conversions.
- **`\newpage` does NOT produce docx page breaks**: Pandoc's `raw_tex` extension strips the backslash and renders `ewpage` as body text. Page breaks must be inserted via python-docx post-processing (see `references/docx-formatting-patterns.md`).
- **Custom margins via `--reference-doc`**: Create a minimal reference docx with python-docx (set section margins to desired inches), then pass `--reference-doc=/tmp/reference.docx` to pandoc. Do NOT use `--reference-doc=/dev/null`.

## Reference Files Available:
- `references/docx-formatting-patterns.md` — Post-pandoc DOCX formatting: margins via reference docx, page break insertion, text replacement, full pipeline
- `references/markdown-to-google-doc.md` — Lessons from 2.2MB handbook conversion: Docs API limits, pandoc quirks, measured resource profile

## Companion Skills

Always load these alongside document-converter:
- `google-workspace` — for Drive API operations
- `protocol-handbook-authoring` — if converting DETOXXX-related documents

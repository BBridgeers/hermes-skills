# Docx Generation Workflow — pandoc + python-docx

Complete pattern for converting 19K-line markdown handbooks to properly-formatted .docx files with Inter font, custom margins, page breaks, and renamed section titles.

**When to use:** Converting DETOXXX V2 Master Handbook (or any large markdown document >1MB) to .docx. Do NOT use Google Docs API for documents over ~1.5MB — it fails with "Precondition check failed" at ~1.5M chars.

## Step 1 — Build the formatted markdown

Apply all changes to the markdown BEFORE conversion:
- Replace title block, rename section headings, add `\newpage` before each section
- Reduce safety warnings to compact V1-style (3-6 lines)
- Add dedication on its own page with `\newpage` before and after

```python
import re

with open('handbook.md', 'r') as f:
    content = f.read()

# Replace front matter with new compact version
content = re.sub(old_front_pattern, new_title_block, content, flags=re.MULTILINE | re.DOTALL)

# Rename section titles throughout
for old_title, new_title in section_rename_map.items():
    content = content.replace(old_title, new_title)

# Add page breaks before each section
for marker in section_markers:
    content = content.replace(f"\n{marker}", f"\n\\newpage\n\n{marker}")

# Clean any <think> artifacts from AI-generated content
content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
```

## Step 2 — Create reference docx with margins

```python
from docx import Document
from docx.shared import Inches, Pt

doc = Document()
for section in doc.sections:
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

# Set base style
style = doc.styles['Normal']
style.font.name = 'Inter'
style.font.size = Pt(11)

doc.save('/tmp/reference.docx')
```

## Step 3 — Convert with pandoc

```bash
pandoc handbook_formatted.md \
  -f markdown+raw_tex \
  -t docx \
  --reference-doc=/tmp/reference.docx \
  -o /tmp/output.docx \
  --metadata title="Document Title"
```

**Pitfall:** Pandoc takes ~4 min at 99% CPU / 770MB RAM for 19K-line files. Run in background with `notify_on_complete=true`. Do NOT use `--reference-doc=/dev/null` — it breaks with "Data.Binary.Get.runGet at position 0: not enough bytes."

**Pitfall:** `\newpage` commands may render as literal "ewpage" text in the output. Post-process in Step 4 to fix.

## Step 4 — Post-process with python-docx

Three fixes needed after pandoc conversion:

### 4a — Fix broken \newpage remnants and add page breaks

```python
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document('/tmp/output.docx')

# Fix "ewpage" remnants → real page breaks
for para in doc.paragraphs:
    if para.text.strip() in ('ewpage', '\\newpage'):
        para.clear()
        run = para.add_run('')
        br = OxmlElement('w:br')
        br.set(qn('w:type'), 'page')
        run._element.append(br)

# Add page breaks before section headings
for i, para in enumerate(doc.paragraphs):
    if para.style.name == 'Heading 1' and is_section_head(para.text):
        if i > 0 and not has_page_break_before(para):
            prev = doc.paragraphs[i - 1]
            br = OxmlElement('w:br')
            br.set(qn('w:type'), 'page')
            if prev.runs:
                prev.runs[-1]._element.append(br)
            else:
                run = prev.add_run('')
                run._element.append(br)
```

### 4b — Set all fonts to Inter

```python
# Set all style fonts to Inter
for style in doc.styles:
    try:
        if style.font:
            style.font.name = 'Inter'
    except:
        pass

# Also set heading fonts explicitly
for i in range(1, 4):
    try:
        doc.styles[f'Heading {i}'].font.name = 'Inter'
    except:
        pass
```

### 4c — Replace section titles in body (not just TOC)

Pandoc may rename TOC entries but leave body headings unchanged. Search ALL paragraphs for old section titles and replace:

```python
title_map = {
    "Section 1 — Front Matter": "Section 1 — Preface & Protocol Overview",
    "Section 2 — Clinical Safety & Risk Mitigation": "Section 2 — Safety Architecture & Contraindications",
    # ... etc for all 13 sections
}

for para in doc.paragraphs:
    for old, new in title_map.items():
        if old in para.text:
            new_text = para.text.replace(old, new, 1)
            para.clear()
            para.add_run(new_text)
```

## Step 5 — Upload to Drive

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

# Auth with refresh
with open('/root/.hermes/google_token.json') as f:
    token_data = json.load(f)
creds = Credentials(
    token=token_data['token'], refresh_token=token_data.get('refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=token_data.get('client_id'), client_secret=token_data.get('client_secret'),
    scopes=token_data.get('scopes', [])
)
creds.refresh(google.auth.transport.requests.Request())
drive_service = build('drive', 'v3', credentials=creds)

# Delete old version if exists
results = drive_service.files().list(
    q=f"name='handbook.docx' and '{folder_id}' in parents",
    fields='files(id)'
).execute()
for f in results.get('files', []):
    drive_service.files().delete(fileId=f['id']).execute()

# Upload new
media = MediaFileUpload('/tmp/output.docx',
    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    resumable=True)
created = drive_service.files().create(
    body={'name': 'handbook.docx', 'parents': [folder_id]},
    media_body=media, fields='id,webViewLink').execute()
```

## Common Pitfalls

- **Page breaks lost on save:** Adding `w:br` elements to heading runs sometimes doesn't survive save/reload. More reliable: add page breaks to the END of the PREVIOUS paragraph's last run.
- **font=None on runs is correct:** When styles are set to Inter and runs have no explicit font override (`font.name = None`), they inherit Inter from the style. Google Docs renders this correctly.
- **Section 1 and 2 may lack body H1 headings:** If the front matter content IS Sections 1-2, there may be no separate "Section 1 — ..." heading in the body. The page breaks from front matter serve as the section boundaries.

## Network Issues

The VPS (Hostinger) has intermittent SSL read timeouts to Google APIs. The `MediaFileUpload` with `resumable=True` for 1MB files can time out after 60s. Workarounds:
- Use non-resumable upload for files under 5MB
- Run uploads in background with `notify_on_complete=true`
- The `files.copy` (for .md→Google Doc conversion) is particularly slow — Google has to process the entire file server-side before responding

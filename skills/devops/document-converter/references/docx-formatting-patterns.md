# DOCX Formatting Patterns — Post-Pandoc Workflow

Lessons from converting a 2.2MB / 19k-line markdown handbook to a
properly formatted .docx with custom margins, page breaks, and renamed
section headings.

---

## 1. Custom Margins via Reference Document

Pandoc respects `--reference-doc` for styling. Create a minimal reference
docx with python-docx:

```python
from docx import Document
from docx.shared import Inches, Pt

doc = Document()
for section in doc.sections:
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

# Set font defaults so pandoc headings inherit them
style = doc.styles['Normal']
style.font.name = 'Centaur'
style.font.size = Pt(11)

doc.save('/tmp/reference.docx')
```

Then: `pandoc input.md --reference-doc=/tmp/reference.docx -o output.docx`

**Do NOT use `--reference-doc=/dev/null`** — it causes
`Data.Binary.Get.runGet at position 0: not enough bytes`.

---

## 2. Page Breaks — Pandoc `\newpage` Does NOT Work for DOCX

Pandoc's `\newpage` (with `raw_tex` extension) does NOT translate to
actual docx page breaks. The text `ewpage` (backslash stripped) ends up
as a body paragraph.

**Fix:** Post-process with python-docx:

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

for para in doc.paragraphs:
    if para.text.strip() == 'ewpage':
        # Replace with empty paragraph containing a page break
        para.clear()
        run = para.add_run('')
        br = OxmlElement('w:br')
        br.set(qn('w:type'), 'page')
        run._element.append(br)
```

To add page breaks before specific headings:

```python
for para in doc.paragraphs:
    if para.style.name == 'Heading 1' and 'Section' in para.text:
        if para.runs:
            br = OxmlElement('w:br')
            br.set(qn('w:type'), 'page')
            para.runs[0]._element.insert(0, br)
```

---

## 3. Text Replacement in Existing DOCX

python-docx stores text in runs. To replace text while preserving
paragraph structure and styles:

```python
old_text = "Section 5 — Tactical Protocols"
new_text = "Section 5 — Agent Deployment Protocols"

for para in doc.paragraphs:
    if old_text in para.text:
        # Rebuild: clear all runs, add one new run with replacement
        full = para.text.replace(old_text, new_text)
        para.clear()
        run = para.add_run(full)
        # Preserve bold if it was a heading
        if 'Heading' in para.style.name:
            run.bold = True
```

---

## 4. Full Pipeline: Markdown → Formatted DOCX → Drive

```bash
# 1. Create reference docx with desired margins (Python above)
# 2. Pandoc conversion
pandoc input.md -f markdown -t docx \
  --reference-doc=/tmp/reference.docx \
  -o /tmp/output.docx

# 3. Post-process with python-docx:
#    - Fix broken \newpage remnants
#    - Add page breaks at section boundaries
#    - Replace section titles
# 4. Upload to Drive
```

---

## 5. Google Docs API Limits (for when NOT using pandoc)

| Method | Limit | Behavior |
|--------|-------|----------|
| `batchUpdate` + `insertText` | ~1.5MB total doc size | `Precondition check failed` |
| `files.create` with conversion | ~2.3MB file | SSL read timeout |
| `files.copy` with mimeType change | ~2.3MB file | SSL read timeout |

**Recommendation:** Always use pandoc → .docx for files over 500KB.
The Drive API conversion path is unreliable for large documents.

---

## 6. Pandoc Resource Profile (for sizing expectations)

| Input Size | Lines | RAM | CPU Time |
|------------|-------|-----|----------|
| 20 KB | ~200 | ~50 MB | <1s |
| 200 KB | ~2,000 | ~100 MB | ~10s |
| 2.2 MB | ~19,000 | ~770 MB | ~4 min |

Batch conversions of large files should be serialized, not parallel.

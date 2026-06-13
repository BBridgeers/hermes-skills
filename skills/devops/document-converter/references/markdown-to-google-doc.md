# Markdown → Google Doc: Lessons from 2.2MB Handbook Conversion

Date: 2026-05-23 | Source: DETOXXX_V2_MASTER_HANDBOOK.md (19,148 lines, 2,220 KB)

## Summary

Google Docs API `batchUpdate` with `insertText` cannot handle documents above ~1.5MB. The reliable path for large markdown→Google Doc is: **pandoc → .docx → Drive upload**. The .docx renders as a native Google Doc when opened.

## Approaches Attempted (ranked by reliability)

### 1. Pandoc → .docx → Drive upload ✅ RELIABLE

```bash
pandoc input.md -f markdown -t docx -o output.docx --metadata title="Document Title"
```

Then upload via Drive API with `MediaFileUpload(resumable=True)`.

**Pros:** Handles large files (tested 2.2MB). Single upload, no chunking. Google Drive renders .docx as native Google Doc.
**Cons:** Pandoc conversion is CPU/memory intensive (~4 min at 99% CPU, ~770MB RAM for 19k lines). `--reference-doc=/dev/null` causes `Data.Binary.Get.runGet at position 0: not enough bytes` — omit `--reference-doc` entirely unless you have a real reference docx.

### 2. Google Docs API batchUpdate insertText ❌ FAILS ABOVE ~1.5MB

```python
docs_service.documents().batchUpdate(
    documentId=doc_id,
    body={'requests': [{'insertText': {'location': {'index': end_idx}, 'text': chunk}}]}
).execute()
```

**Pitfalls:**
- **"Precondition check failed"** — fires consistently once the document reaches ~1.5MB. The API silently refuses further inserts.
- **Inserting at index 1 creates reverse order** — each insert at position 1 pushes existing content down. Must always query `endIndex - 1` for appending.
- **50KB chunk size** worked for ~30 chunks before hitting the limit. 10KB sub-chunks also fail after the limit.
- **The limit is per-document, not per-request** — no workaround exists. Must use pandoc for large files.

### 3. Drive API upload with convert=true ❌ NETWORK TIMEOUT

```python
media = MediaFileUpload(path, mimetype='text/markdown', resumable=True)
drive_service.files().create(
    body={'name': name, 'mimeType': 'application/vnd.google-apps.document', 'parents': [folder]},
    media_body=media
).execute()
```

**Why it failed:** The VPS SSL connection timed out during the 2.3MB upload+conversion. Google's server-side conversion of large markdown files takes time, and the API response read times out before completion. Non-resumable upload also timed out. This might work on faster connections but is unreliable on this VPS.

### 4. Two-step: upload .md, then copy with conversion ❌ NETWORK TIMEOUT

Upload .md first (succeeded — file ID `12F3KVinpGck5OM2XpfpIA1p0YceSqHCu`), then `files().copy()` with `mimeType='application/vnd.google-apps.document'`. The copy timed out on response read — Google's server-side conversion of 2.2MB markdown takes longer than the SSL read timeout.

## Resource Profile

| File Size | Pandoc Time | Pandoc RAM | Pandoc CPU |
|-----------|------------|------------|------------|
| 2.2 MB (19k lines) | ~4 min | ~770 MB | 99% (single core) |

## Verified Working Command

```bash
pandoc /path/to/input.md \
  -f markdown \
  -t docx \
  -o /tmp/output.docx \
  --metadata title="Document Title"
# DO NOT use --reference-doc=/dev/null
```

Then upload `output.docx` to Drive with `MediaFileUpload(resumable=True)`. The resulting .docx renders as a native Google Doc when opened in Drive.

## Google Doc Size Limits (measured, not documented)

- **~1.5MB of inserted text** — beyond this, `batchUpdate` returns "Precondition check failed"
- **Content order matters** — inserting at `index: 1` prepends. Use `endIndex - 1` for appending.
- **Delete broken docs** — `drive_service.files().delete(fileId=doc_id)` to clean up failed attempts

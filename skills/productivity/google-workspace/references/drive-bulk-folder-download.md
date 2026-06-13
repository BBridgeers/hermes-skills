# Drive Bulk Folder Download Pattern

Recursively download an entire Google Drive folder (including subfolders) into a local workspace. Handles Google Docs (export as text), Google Sheets (export as CSV), PDFs, Word docs, and native text files.

## Use When

- User says "copy all contents of this folder to the workspace"
- User wants to mirror a Drive folder structure locally
- Need to pull DETOXXX or similar large document collections from Drive

## Core Pattern

Use `execute_code` with this structure:

```python
import json, os, io
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

TOKEN_PATH = "/root/.hermes/google_token.json"  # ALWAYS this path, not HERMES_HOME
WORKSPACE = Path("/root/workspace/<project>")

def get_drive_service():
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", []),
    )
    return build("drive", "v3", credentials=creds)

def list_all(service, folder_id, prefix=""):
    """Recursively list all files in a folder — skips trashed files."""
    results = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            f["_path"] = prefix + f["name"]
            results.append(f)
            if f["mimeType"] == "application/vnd.google-apps.folder":
                results.extend(list_all(service, f["id"], prefix + f["name"] + "/"))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results

def download_text(service, file_id):
    """Download binary/text content directly."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read()

def export_google_doc(service, file_id, mime_type="text/plain"):
    """Export Google Docs/Sheets as text."""
    request = service.files().export(fileId=file_id, mimeType=mime_type)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read()

# MAIN — replace with actual folder ID
service = get_drive_service()
all_files = list_all(service, "FOLDER_ID_HERE")

downloaded = 0
failed = 0

for f in all_files:
    if f["mimeType"] == "application/vnd.google-apps.folder":
        continue
    
    # Skip temp files
    if f["_path"].endswith(".tmp") or "~WRL" in f["_path"] or "~$" in f["_path"]:
        continue
    
    dest = WORKSPACE / f["_path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if f["mimeType"] == "application/vnd.google-apps.document":
            content = export_google_doc(service, f["id"])
        elif f["mimeType"] == "application/vnd.google-apps.spreadsheet":
            content = export_google_doc(service, f["id"], "text/csv")
        elif f["mimeType"] in ("application/pdf", 
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"):
            content = download_text(service, f["id"])
        else:
            content = download_text(service, f["id"])
        
        if isinstance(content, bytes):
            dest.write_bytes(content)
        else:
            dest.write_text(content, encoding="utf-8", errors="replace")
        
        downloaded += 1
    except Exception as e:
        print(f"FAIL: {f['_path']} -> {e}")
        failed += 1

print(f"Downloaded: {downloaded}, Failed: {failed}")
```

## MIME-Type Routing Table

| Drive MIME Type | Method | Notes |
|---|---|---|
| `application/vnd.google-apps.folder` | Recurse into | No file to download |
| `application/vnd.google-apps.document` | `export_google_doc()` | Export as text/plain |
| `application/vnd.google-apps.spreadsheet` | `export_google_doc(mime_type="text/csv")` | Export as CSV |
| `application/pdf` | `download_text()` (binary) | Write as bytes |
| `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `download_text()` (binary) | .docx — write as bytes |
| `text/markdown`, `text/csv`, `text/plain` | `download_text()` | Write as text |
| Files ending `.tmp`, `~WRL*`, `~$*` | **SKIP** | Temp/Office lock files |

## Common Pitfalls

1. **Token path**: Always use `/root/.hermes/google_token.json`, not `HERMES_HOME/google_token.json`. Profiles share one token.

2. **Google Docs vs binary**: Trying to `get_media()` on a Google Doc returns HTTP 403 "Only files with binary content can be downloaded." Use `export()` instead.

3. **Temp files**: Drive folders often contain `~WRL0004.tmp` and similar temp files. Skip them by name pattern.

4. **Large folders**: 100+ files take ~40-50 seconds. List first (Phase 1), then download (Phase 2) — the listing output helps the user confirm before the long download.

5. **`google_api.py` limitations**: The bundled CLI wrapper only supports `drive search`, not `drive list`. For folder listing, use the Python API directly via `execute_code`.

## Two-Phase Approach (Recommended)

**Phase 1 — Scan**: List all files and show the user what's there before downloading. This confirms the right folder and avoids wasted time.

**Phase 2 — Download**: After user confirmation, download everything with the MIME-type routing above.

For standalone single files (Audit Notes, Build Tracker), add them separately:
```python
standalone = {
    "FILE_ID": "output_name.md",
}
for file_id, name in standalone.items():
    # Try download_text first; if it fails with 403, try export_google_doc
```

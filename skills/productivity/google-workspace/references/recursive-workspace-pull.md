# Recursive Workspace Pull — Full Drive Folder → Local Workspace

Pattern for downloading every file from a Google Drive folder (and all subfolders)
into a local workspace directory. Used successfully for the DETOXXX project (111 files,
14MB).

## Key Pitfall: Token Path

The token is at `/root/.hermes/google_token.json` — NOT inside the profile's hermes home.
The `HERMES_HOME` env var points to `~/.hermes/profiles/<name>` but the token lives at the
top-level `~/.hermes/`. Always use the absolute path.

```python
TOKEN_PATH = "/root/.hermes/google_token.json"
```

## Recipe

### 1. Recursive Listing

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def list_all(service, folder_id, prefix=""):
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
```

### 2. Content-Type Routing

| MimeType | Method | Notes |
|----------|--------|-------|
| `application/vnd.google-apps.document` | `export()` with `text/plain` | Google Docs need export, NOT get_media |
| `application/vnd.google-apps.spreadsheet` | `export()` with `text/csv` | Sheets → CSV |
| `application/pdf` | `get_media()` | Binary, write as bytes |
| `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `get_media()` | Binary, write as bytes |
| `text/markdown`, `text/csv`, etc. | `get_media()` then decode | Text files |
| `application/vnd.google-apps.folder` | Skip (already recursed) | |

### 3. Download Loop

```python
for f in all_files:
    if f["mimeType"] == "application/vnd.google-apps.folder":
        continue
    
    dest = WORKSPACE / f["_path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    if f["mimeType"] == "application/vnd.google-apps.document":
        content = export_google_doc(service, f["id"])
    elif f["mimeType"] == "application/vnd.google-apps.spreadsheet":
        content = export_google_doc(service, f["id"], "text/csv")
    else:
        content = download_text(service, f["id"])  # bytes
    
    if isinstance(content, bytes):
        dest.write_bytes(content)
    else:
        dest.write_text(content, encoding="utf-8", errors="replace")
```

## Common Error

```
Only files with binary content can be downloaded. Use Export with Docs Editors files.
```
→ You tried `get_media()` on a Google Doc/Sheet. Use `export()` instead.

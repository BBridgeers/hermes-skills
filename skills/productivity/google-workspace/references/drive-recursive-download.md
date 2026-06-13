# Drive Recursive Download Pattern

Use when you need to mirror an entire Drive folder tree to a local workspace.
The `google_api.py drive search` command only finds files — it doesn't list
folders or download content. Use this pattern instead.

## Core Pattern

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# TOKEN_PATH: use absolute path. ~/.hermes/google_token.json expands wrong
# when HERMES_HOME is set to a profile dir. Always use /root/.hermes/google_token.json.
TOKEN_PATH = "/root/.hermes/google_token.json"

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
    """Recursively list all non-trashed files in a folder tree."""
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

## Download / Export Routing

Different mime types require different API calls:

| Mime Type | Method | Notes |
|-----------|--------|-------|
| `application/vnd.google-apps.document` | `files().export(fileId, mimeType='text/plain')` | Google Doc → text |
| `application/vnd.google-apps.spreadsheet` | `files().export(fileId, mimeType='text/csv')` | Google Sheet → CSV |
| `application/vnd.google-apps.presentation` | `files().export(fileId, mimeType='text/plain')` | Google Slides → text |
| `application/pdf` | `files().get_media(fileId)` | Binary download |
| `application/vnd.openxmlformats...` | `files().get_media(fileId)` | Binary (docx, xlsx, etc.) |
| `text/markdown`, `text/csv`, etc. | `files().get_media(fileId)` | Text download |
| `application/vnd.google-apps.folder` | Skip (recursed by `list_all`) | — |

**Critical pitfall:** Calling `files().get_media()` on a Google Doc/Slide/Sheet returns
HTTP 403: "Only files with binary content can be downloaded. Use Export with Docs
Editors files." Always check mime type before choosing download vs export.

## Pitfalls

1. **`~/` expansion in profiles**: When `HERMES_HOME` is set to a profile dir
   (e.g., `/root/.hermes/profiles/detoxxx`), `~` expands to that profile dir,
   NOT `/root`. The token lives at `/root/.hermes/google_token.json`. Always
   use absolute paths.

2. **Temp files**: Drive folders often contain temporary files like `~WRL0004.tmp`
   or files starting with `~$`. Filter these out — they're Word lock files.

3. **Google Doc export produces plain text**: `files().export()` with
   `text/plain` strips all formatting. If formatting matters, export as
   `application/pdf` or `text/html` instead.

4. **Rate limits**: Batch downloading 100+ files triggers occasional 403s.
   Add a small delay between downloads for large folders.

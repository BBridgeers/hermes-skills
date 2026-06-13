"""
Drive file download workaround — use when google_api.py drive search finds
files but you need to read their contents. Loads the stored OAuth token and
downloads text files from Drive via files().get_media().

Usage from execute_code or terminal:
    download_text(file_id, output_path)

Requires: google-api-python-client, google-auth-oauthlib (already installed
via google-workspace skill setup).

PITFALL — ~/ path expansion: os.path.expanduser("~/.hermes/google_token.json")
expands relative to HERMES_HOME (may be a profile dir). The token lives at
/root/.hermes/google_token.json. Use absolute paths. For recursive folder
mirroring with mime-type routing, see references/drive-recursive-download.md.
"""
import json, os, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


def _get_drive_service():
    token_path = os.path.expanduser("~/.hermes/google_token.json")
    with open(token_path) as f:
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


def download_text(file_id):
    """Download a text file from Google Drive and return its content as a string."""
    service = _get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read().decode("utf-8", errors="replace")


def list_folder(folder_id, page_size=50):
    """List files in a Drive folder. Returns list of {id, name, mimeType, modifiedTime}."""
    service = _get_drive_service()
    result = (
        service.files()
        .list(
            q=f"'{folder_id}' in parents",
            pageSize=page_size,
            fields="files(id, name, mimeType, modifiedTime)",
        )
        .execute()
    )
    return result.get("files", [])


# ---- Batch download example ----
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python drive-download-workaround.py FILE_ID [FILE_ID ...]")
        sys.exit(1)

    for file_id in sys.argv[1:]:
        try:
            text = download_text(file_id)
            print(f"OK {file_id}: {len(text)} bytes, {text.count(chr(10))} lines")
        except Exception as e:
            print(f"FAIL {file_id}: {e}")

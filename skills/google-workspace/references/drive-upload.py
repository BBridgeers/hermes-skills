"""
Upload files to Google Drive using stored OAuth token.
Requires the `drive` scope (NOT `drive.readonly`).

Usage from terminal:
    python3 drive-upload.py /path/to/file.md "folder_id" [--mime-type text/markdown]

If the folder already contains a file with the same name, it updates the existing
file rather than creating a duplicate. Returns the file ID and webViewLink.

Requires: google-api-python-client, google-auth-oauthlib (installed via google-workspace setup).
"""

import json, os, sys, argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


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


def upload_file(file_path, folder_id, mime_type="text/markdown"):
    """Upload file to Drive folder. Updates if same-name file exists."""
    service = _get_drive_service()
    file_name = os.path.basename(file_path)

    # Check if file already exists in folder
    existing = (
        service.files()
        .list(
            q=f"name='{file_name}' and '{folder_id}' in parents",
            fields="files(id, name)",
        )
        .execute()
    )
    files = existing.get("files", [])

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    if files:
        file_id = files[0]["id"]
        updated = service.files().update(fileId=file_id, media_body=media).execute()
        result = updated
        action = "UPDATED"
    else:
        file_metadata = {
            "name": file_name,
            "parents": [folder_id],
            "mimeType": mime_type,
        }
        created = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
            .execute()
        )
        result = created
        action = "CREATED"

    # Fetch final metadata
    f = service.files().get(fileId=result["id"], fields="webViewLink, size").execute()
    print(f"{action}: {result['id']}")
    print(f"LINK: {f['webViewLink']}")
    print(f"SIZE: {f['size']} bytes")
    return result["id"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to Google Drive")
    parser.add_argument("file_path", help="Local file to upload")
    parser.add_argument("folder_id", help="Destination Drive folder ID")
    parser.add_argument("--mime-type", default="text/markdown", help="MIME type (default: text/markdown)")
    args = parser.parse_args()

    upload_file(args.file_path, args.folder_id, args.mime_type)

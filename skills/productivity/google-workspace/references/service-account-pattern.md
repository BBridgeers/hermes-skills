# Service Account Quick-Start Pattern

Copy-paste pattern for authenticating with a Google Service Account JSON key
and performing common Drive operations. Works from any Python environment with
`google-api-python-client` and `google-auth` installed.

## Install dependencies

```bash
pip3 install --break-system-packages google-api-python-client google-auth
```

## Bootstrap — authenticate and list

```python
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SA_FILE = '/root/.hermes/google_service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)

# Verify
about = service.about().get(fields="user,storageQuota").execute()
print(f"Authenticated as: {about['user']['emailAddress']}")
```

## Find folders shared with the SA

```python
results = service.files().list(
    q="name contains 'MyFolder' and mimeType='application/vnd.google-apps.folder'",
    pageSize=10,
    fields="files(id, name, webViewLink, capabilities)"
).execute()

for f in results.get('files', []):
    caps = f.get('capabilities', {})
    print(f"  {f['name']} — edit={caps.get('canEdit')}, addChildren={caps.get('canAddChildren')}, delete={caps.get('canDelete')}")
```

## List folder contents

```python
FOLDER_ID = '1abc...'
children = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    pageSize=50,
    fields="files(id, name, mimeType, size, modifiedTime)"
).execute()

for f in children.get('files', []):
    size_kb = int(f.get('size', 0)) / 1024
    print(f"  {f['name']} ({f['mimeType']}, {size_kb:.1f} KB)")
```

## Download file content (text)

```python
import io
from googleapiclient.http import MediaIoBaseDownload

FILE_ID = '1xyz...'
request = service.files().get_media(fileId=FILE_ID)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    status, done = downloader.next_chunk()
content = fh.getvalue().decode('utf-8')
print(f"Downloaded {len(content)} chars")
```

## Modify file in-place (content update)

This is the preferred write path for service accounts — it reuses existing
storage and avoids the `storageQuotaExceeded` error.

```python
from googleapiclient.http import MediaIoBaseUpload
import io

new_content = "updated content here"
media = MediaIoBaseUpload(
    io.BytesIO(new_content.encode()),
    mimetype='text/plain',
    resumable=True
)
updated = service.files().update(
    fileId=FILE_ID,
    media_body=media,
    fields='id,name,size,modifiedTime'
).execute()
print(f"Updated: {updated['name']} — {updated.get('size')} bytes")
```

## Create new file (Shared Drive only)

Only works when DEST_FOLDER_ID is in a Shared Drive where the SA is a member.
Fails with `storageQuotaExceeded` in "My Drive" folders.

```python
from googleapiclient.http import MediaIoBaseUpload
import io

content = "new file content"
media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype='text/plain', resumable=True)
file_meta = {
    'name': 'output.txt',
    'parents': [DEST_FOLDER_ID],  # must be in a Shared Drive
}
created = service.files().create(body=file_meta, media_body=media, fields='id,name').execute()
print(f"Created: {created['name']} (ID: {created['id']})")
```

## Recursive folder walk

```python
def walk_folder(service, folder_id, indent=0):
    children = service.files().list(
        q=f"'{folder_id}' in parents",
        pageSize=100,
        fields="files(id, name, mimeType, size)"
    ).execute()
    for f in children.get('files', []):
        prefix = "  " * indent
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            print(f"{prefix}📁 {f['name']}/")
            walk_folder(service, f['id'], indent + 1)
        else:
            size = int(f.get('size', 0))
            if size > 1024*1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f} KB"
            else:
                size_str = f"{size} B"
            print(f"{prefix}📄 {f['name']} ({size_str})")
```

## Pitfalls

1. **`MediaFileUpload` needs a file path**, not a BytesIO. Use `MediaIoBaseUpload` for in-memory content.

2. **Storage quota**: service accounts cannot create files in "My Drive" folders — only modify existing files or create in Shared Drives.

3. **Root listing**: `'root' in parents` won't show folders the SA hasn't been shared with. Search by name instead.

4. **`drive.readonly` scope**: the default OAuth setup only has `drive.readonly` — service accounts need explicit `https://www.googleapis.com/auth/drive` scope for write.

5. **No `driveId` field present**: if `files().get(fileId=..., fields='driveId')` returns no `driveId`, the file is in "My Drive" (not a Shared Drive) — creation will fail with `storageQuotaExceeded`.

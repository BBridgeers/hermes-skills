# Drive File Upload via Python (OAuth)

The `google_api.py` CLI only has a `drive search` subcommand. To **upload** files when you
already have an authenticated token (`~/.hermes/google_token.json`), use this pattern
directly against the Google API client.

**Prerequisite:** OAuth2 token must include `https://www.googleapis.com/auth/drive`
scope (full write access), not just `drive.readonly`. Check with:
```python
import json
with open(os.path.expanduser('~/.hermes/google_token.json')) as f:
    print(json.load(f).get('scopes', []))
```

## Upload pattern (file path)

```python
import sys, os
sys.path.insert(0, os.path.expanduser('~/.hermes/skills/productivity/google-workspace/references'))
import importlib.util
spec = importlib.util.spec_from_file_location('dwd',
    os.path.expanduser('~/.hermes/skills/productivity/google-workspace/references/drive-download-workaround.py'))
dwd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dwd)

service = dwd._get_drive_service()
from googleapiclient.http import MediaFileUpload

file_metadata = {
    'name': 'FILENAME.ext',
    'parents': ['FOLDER_ID'],   # Drive folder ID — optional, omit for root
    'mimeType': 'text/markdown' # or application/pdf, text/csv, etc.
}

media = MediaFileUpload('/local/path/to/file', mimetype='text/markdown', resumable=True)

# Check if file exists to update vs. create
existing = service.files().list(
    q="name='FILENAME.ext' and 'FOLDER_ID' in parents",
    fields='files(id)').execute()
files = existing.get('files', [])

if files:
    result = service.files().update(fileId=files[0]['id'], media_body=media,
        fields='id,webViewLink').execute()
else:
    result = service.files().create(body=file_metadata, media_body=media,
        fields='id,webViewLink').execute()

print(f"https://drive.google.com/file/d/{result['id']}/view?usp=drivesdk")
```

## Upload pattern (in-memory / inline content)

When the content is generated in-memory (not from a file on disk), use `MediaIoBaseUpload`
with `io.BytesIO` instead of `MediaFileUpload`. This is the pattern for headless/VPS
setups where you're uploading text, JSON, or Markdown you just generated.

```python
import json, io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Load OAuth token
with open('/opt/data/google_token.json') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data.get('client_id'),
    client_secret=token_data.get('client_secret')
)

service = build('drive', 'v3', credentials=creds)

# Upload in-memory content
content = "Hello from Hermes"
media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype='text/plain', resumable=True)
file_metadata = {
    'name': 'hello.txt',
    'parents': ['FOLDER_ID']  # optional — omit for Drive root
}

result = service.files().create(body=file_metadata, media_body=media, fields='id,name,size').execute()
print(f"Uploaded {result['name']} — ID: {result['id']}")
```

The same approach works for `files().update()` to modify existing files in-place.

## Upgrading from drive.readonly to drive scope

If the token only has `drive.readonly`, the setup script `setup.py` at
`~/.hermes/skills/productivity/google-workspace/scripts/setup.py` must have
the scope line changed from `drive.readonly` to `drive`, then re-authenticate:

```bash
python3 /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-url
# Visit URL, approve, paste back redirected URL
python3 /root/.hermes/skills/productivity/google-workspace/scripts/setup.py --auth-code "PASTED_URL"
```

The `google_api.py` script at the same path also has the scope list at line ~50
and should be updated in sync.

## Token refresh in inline upload scripts

The inline Python pattern above does NOT auto-refresh expired tokens. If you get
a 401/403 on upload, the token likely expired. Add this refresh block before the
upload call:

```python
if resp.status_code in (401, 403):
    refresh_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": tokens["client_id"],
        "client_secret": tokens["client_secret"],
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token"
    })
    if refresh_resp.status_code == 200:
        new = refresh_resp.json()
        tokens["token"] = new["access_token"]
        tokens["expiry"] = new.get("expires_in", 3600)
        with open(os.path.expanduser("~/.hermes/google_token.json"), "w") as f:
            json.dump(tokens, f, indent=2)
        # Retry with new tokens["token"]
```

Note: the refresh response uses `access_token` key, but the stored file uses
`token` key. Don't mix them up.

## Common pitfalls

- **403 Insufficient Permission**: Token has `drive.readonly` but full `drive` needed.
  Re-auth with the broader scope.
- **ResumableUploadError on create/update**: Same as above — scope mismatch.
- **MediaFileUpload with large files**: Set `resumable=True` for files over ~5MB.
  For small Markdown files, it's safe either way.
- **Parent folder not found**: Verify the folder ID exists and the authenticated
  account has access to it.
- **Token key is `'token'`, NOT `'access_token'`**: The token file at
  `~/.hermes/google_token.json` stores the access token under the key `'token'`
  (following Google's OAuth2 JSON format), NOT `'access_token'`. When writing
  inline Python for uploads, use `tokens['token']`, not `tokens['access_token']`.
  This will silently produce `None` if you get it wrong, and the API call will
  fail with a 401 or unauthenticated error.

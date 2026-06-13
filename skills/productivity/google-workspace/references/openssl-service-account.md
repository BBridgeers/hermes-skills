# Zero-Dependency Service Account Drive Access (openssl + stdlib)

Pure Python stdlib + openssl service account auth. Zero pip packages.
Use this when `pip install google-api-python-client` fails (externally-managed
Python, venv restrictions) or when you need a fast bootstrap without installing
anything.

## How it works

1. Build a JWT (header + payload) by hand
2. Sign it with `openssl dgst -sha256 -sign` using the SA's private key
3. POST the JWT to Google's token endpoint → get an access token
4. Use `urllib.request` to call the Drive REST API directly

## Auth and API call script

Save as e.g. `/tmp/drive_sa.py`:

```python
#!/usr/bin/env python3
import json, time, base64, subprocess, urllib.request, urllib.parse, urllib.error, tempfile, os

SA = json.load(open("/root/.hermes/gcp_service_account.json"))
SCOPE = "https://www.googleapis.com/auth/drive"  # or drive.readonly

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def get_token(sa: dict) -> str:
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    now = int(time.time())
    payload = b64url(json.dumps({
        "iss": sa["client_email"], "scope": SCOPE,
        "aud": sa["token_uri"], "exp": now + 3600, "iat": now
    }).encode())
    signing_input = f"{header}.{payload}".encode()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as kf:
        kf.write(sa["private_key"])
        key_path = kf.name
    try:
        sig = subprocess.check_output(
            ["openssl", "dgst", "-sha256", "-sign", key_path, "-binary"],
            input=signing_input
        )
    finally:
        os.unlink(key_path)

    jwt = f"{header}.{payload}.{b64url(sig)}"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt
    }).encode()
    req = urllib.request.Request(
        sa["token_uri"], data=data, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

def call(token, endpoint):
    url = f"https://www.googleapis.com/drive/v3/{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:500]}

# --- Usage ---
token = get_token(SA)
print(f"Token: {token[:30]}...")

# List a folder
FOLDER = "1QqFi4ouGDoL..."
result = call(token, f"files?q='{FOLDER}'+in+parents&fields=files(id,name,mimeType)")
for f in result.get("files", []):
    print(f"  {f['name']} ({f['id']}) [{f['mimeType']}]")

# Download text file
FILE_ID = "1dwXFv8WIOs..."
req = urllib.request.Request(
    f"https://www.googleapis.com/drive/v3/files/{FILE_ID}?alt=media",
    headers={"Authorization": f"Bearer {token}"}
)
with urllib.request.urlopen(req) as r:
    content = r.read().decode("utf-8", errors="replace")
    print(f"Downloaded {len(content)} chars")
```

## Recursive folder explorer

```python
def list_folder(token, fid, label=""):
    q = f"'{fid}'+in+parents+and+trashed=false"
    fields = "files(id,name,mimeType,size,modifiedTime)"
    result = call(token, f"files?q={urllib.parse.quote(q)}&fields={fields}&orderBy=name&pageSize=100")
    for f in result.get("files", []):
        name, fid2, mtype = f["name"], f["id"], f.get("mimeType", "")
        if mtype == "application/vnd.google-apps.folder":
            print(f"  {'  '*len(label)}📁 {name}/  ({fid2})")
            list_folder(token, fid2, label + "  ")
        else:
            size = f.get("size", "?")
            print(f"  {'  '*len(label)}📄 {name}  ({fid2}, {size}B)")
```

## Prerequisites

- `openssl` (available on virtually all Linux systems)
- `python3` with stdlib only (json, base64, hashlib, hmac, urllib, tempfile, subprocess)
- Service account JSON key saved locally
- The service account must be shared on the target Drive folders/files

## Pitfalls

1. **Private key format**: The SA key's `private_key` field includes `\n` as literal newlines.
   `json.load()` handles this — the string will contain actual newline characters.
   Write it verbatim to the temp PEM file.

2. **Scope mismatch**: If the OAuth consent screen / SA grants only `drive.readonly`,
   write operations will return 403. Use full `https://www.googleapis.com/auth/drive`.

3. **Rate limits**: No exponential backoff built in. For production use, add retry logic
   on 429 responses.

4. **Token expiry**: Access tokens live 1 hour. The `get_token()` function requests
   fresh tokens on each call — ok for interactive use but inefficient for batch operations.
   Cache the token and renew when API calls return 401.

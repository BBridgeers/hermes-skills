#!/usr/bin/env python3
"""
Google Drive API access via service account JWT — zero pip dependencies.
Uses openssl for RSA signing (no cryptography/pyjwt needed).
Single file, portable. Usage: python3 drive_sa_auth.py <sa_key.json>
"""
import json, time, base64, subprocess, urllib.request, urllib.parse, urllib.error
import tempfile, os, sys

SCOPE_RO = "https://www.googleapis.com/auth/drive.readonly"
SCOPE_RW = "https://www.googleapis.com/auth/drive"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def get_token(sa: dict, scope: str = SCOPE_RO) -> str:
    """Build JWT, sign with openssl, exchange for access token."""
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    now = int(time.time())
    payload = b64url(json.dumps({
        "iss": sa["client_email"],
        "scope": scope,
        "aud": sa["token_uri"],
        "exp": now + 3600,
        "iat": now,
    }).encode())
    signing_input = f"{header}.{payload}".encode()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".pem", delete=False) as kf:
        kf.write(sa["private_key"])
        key_path = kf.name
    try:
        sig = subprocess.check_output(
            ["openssl", "dgst", "-sha256", "-sign", key_path, "-binary"],
            input=signing_input,
        )
    finally:
        os.unlink(key_path)

    jwt = f"{header}.{payload}.{b64url(sig)}"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode()
    req = urllib.request.Request(sa["token_uri"], data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]


def drive_call(access_token: str, endpoint: str) -> dict:
    url = f"https://www.googleapis.com/drive/v3/{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:800]}


def list_folder(access_token: str, folder_id: str) -> list:
    """List children of a Drive folder."""
    result = drive_call(access_token,
                        f"files?q='{folder_id}'+in+parents&fields=files(id,name,mimeType)")
    return result.get("files", [])


def download_file(access_token: str, file_id: str) -> str:
    """Download file content as text."""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8", errors="replace")


def download_file_bytes(access_token: str, file_id: str) -> bytes:
    """Download file content as raw bytes."""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def upload_file(access_token: str, name: str, parent_id: str, content: str) -> dict:
    """Upload a file to a Drive folder. Returns file metadata."""
    boundary = "----HermesBoundary"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json\r\n\r\n"
        f'{json.dumps({"name": name, "parents": [parent_id]})}\r\n'
        f"--{boundary}\r\n"
        f"Content-Type: text/markdown\r\n\r\n"
        f"{content}\r\n"
        f"--{boundary}--\r\n"
    ).encode()
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Authorization": f"Bearer {access_token}",
                                          "Content-Type": f"multipart/related; boundary={boundary}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# ---- CLI: test auth and list a folder ----
if __name__ == "__main__":
    sa_path = sys.argv[1] if len(sys.argv) > 1 else "/root/.hermes/gcp_service_account.json"
    sa = json.load(open(sa_path))
    print(f"SA: {sa['client_email']}")
    token = get_token(sa)
    print(f"Token: {token[:30]}... OK")

    # Quick self-check
    about = drive_call(token, "about?fields=user,storageQuota")
    print(json.dumps(about, indent=2)[:300])

    # List folder if ID provided
    if len(sys.argv) > 2:
        fid = sys.argv[2]
        print(f"\n--- Listing folder {fid} ---")
        for f in list_folder(token, fid):
            print(f"  {f['name']}  ({f['id']})  [{f.get('mimeType','?')}]")

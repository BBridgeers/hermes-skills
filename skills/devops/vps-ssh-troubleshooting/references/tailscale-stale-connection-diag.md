# Tailscale Stale Connection Diagnosis

**User context**: VPS Linux + Windows laptop both connected to same Tailscale account, but TCP connectivity fails.

**Observed behavior**:
```
# VPS shows both devices connected
tailscale status
# 100.78.50.1 srv1617682 dfwwebdesignnow@ linux
# 100.66.73.41 lenovo dfwwebdesignnow@ windows

# But Windows Test-NetConnection fails
Test-NetConnection -ComputerName 100.78.50.1 -Port 8787
# TcpTestSucceeded : False
```

## Diagnosis (Run on VPS)

```
tailscale status --json | jq '.Peer[] | select(.Name | contains("lenovo"))'
```

**Look for these failure signs:**
- `"Active": false`
- `"InEngine": false`
- `"LastWrite": "0001-01-01T00:00:00Z"`
- `"RxBytes": 0, "TxBytes": 0`
- `LastHandshake` timestamp is `0001-01-01T00:00:00Z`

## Root Cause

The Tailscale connection is stale — devices see each other in the network map but no actual traffic is flowing. This commonly happens after:
- Re-authenticating Tailscale with a different account
- Tailscale service restart without proper reconnection
- Windows laptop Tailscale state getting stuck

## Fix (Run on Windows Laptop)

```powershell
tailscale down
tailscale up
```

Or restart Tailscale service:
```powershell
Stop-Service Tailscale
Start-Service Tailscale
tailscale up
```

**Alternative**: Access `http://127.0.0.1:8384` in browser (local Tailscale web UI) and click "Connect" to force reconnection.

## Verification

After reconnection, run on VPS:
```
tailscale status
```
Windows device should now show traffic:
- `RxBytes > 0, TxBytes > 0`
- Non-zero `LastWrite` and `LastHandshake` timestamps

Test from laptop:
```powershell
Test-NetConnection -ComputerName 100.78.50.1 -Port 8787
# Should show: TcpTestSucceeded : True
```

## Common Patterns

| Scenario | Symptom | Fix |
|---|---|---|
| Logged into wrong account | `Test-NetConnection` suddenly fails | Re-auth with `tailscale down && tailscale up` |
| Tailscale service restart | Devices show connected but no traffic | Restart service, then `tailscale up` |
| Windows laptop Tailscale stuck | `InEngine: false` in JSON | Force reconnection via web UI |

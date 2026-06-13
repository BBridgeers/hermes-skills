# VPS Auto-Deployment Pitfalls — Session Notes

Date: 2026-05-27
Context: Hostinger VPS (srv1617682), bare-metal, no Docker. Watcher script: `/usr/local/bin/ag-repo-watcher.sh`.

## 1. User services need XDG_RUNTIME_DIR

When a system service (or root cron/script) restarts a user-scoped systemd service, `systemctl --user` fails unless `XDG_RUNTIME_DIR` is exported.

Symptom:
```
Failed to connect to bus: No medium found
```

Fix in watcher script:
```bash
XDG_RUNTIME_DIR="/run/user/0" systemctl --user restart hermes-workspace.service
```

Or detect dynamically:
```bash
if systemctl --user list-unit-files "$svc" &>/dev/null; then
  XDG_RUNTIME_DIR="/run/user/$(id -u)" systemctl --user restart "$svc"
fi
```

## 2. Branch name mismatches

Not all repos use `main`. The hermes-webui repo tracks `master`. Hard-coding `origin/main` causes `FETCH FAILED`.

Verification:
```bash
cd /root/hermes-webui && git branch --show-current  # master
```

Fix: maintain an explicit branch map per repo in the watcher script.

## 3. GitHub SSH auth as root

The watcher runs as root (systemd system service). Ensure root's SSH key is authorized for GitHub:
```bash
ssh -T git@github.com  # run as root
```

If the key has a passphrase, either remove it or use `ssh-agent` in the script. Password-protected keys will hang the watcher.

## 4. Service-to-repo mapping

| Repo | Branch | Services |
|---|---|---|
| /root/vehicle-analyzer | main | veracar-nextjs.service, fb-scraper.service, veracar-scraper.service |
| /root/hermes-webui | master | hermes-webui.service |
| /root/hermes-workspace | main | hermes-workspace.service (user) |

## 5. Restart race condition

`systemctl restart` is atomic and handles the stop/start sequence. Prefer it over separate `stop` + `sleep` + `start` unless the app needs a custom grace period.

## 6. Dirty tree handling

The watcher stashes local changes, hard-resets to remote, then pops the stash. If pop fails (e.g., upstream modified the same file), the stash remains and the log should flag it. Do not silently drop changes.

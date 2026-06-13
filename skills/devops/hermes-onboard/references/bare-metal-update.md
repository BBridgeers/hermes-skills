# Bare-Metal Update Procedure

Applies when Hermes Agent is installed via git checkout + venv at
`/usr/local/lib/hermes-agent/` (not Docker, not pip-only).

## The Trap

`hermes --version` reports "Up to date" based on git HEAD, NOT on what's
actually installed in the venv. After `git pull`, the repo is current but the
venv still runs the OLD version. `hermes update` may also report "Up to date"
if git HEAD matches remote — it won't rebuild the venv.

**Symptom:** `hermes --version` says v0.14.0 and "Up to date" even though
v0.16.0 is in the pulled repo. The gateway is running the stale venv build.

## Full Update Sequence

```bash
# 1. Pull latest from GitHub
cd /usr/local/lib/hermes-agent
git pull

# 2. Rebuild the editable venv install (venv is 'venv/', not '.venv/')
source venv/bin/activate
pip install --upgrade -e .
deactivate

# 3. Verify the version bumped
hermes --version

# 4. Restart the gateway so it picks up the new code
systemctl --user restart hermes-gateway
systemctl --user status hermes-gateway --no-pager
```

## Why pip install --upgrade -e . Is Needed

The `hermes` CLI entry point at `/root/.local/bin/hermes` is a thin wrapper
that execs into the venv Python. The editable install (`-e`) links the venv's
site-packages to the git checkout. But **pip does not auto-rebuild on git
pull** — the egg-link stays pointed at the old checkout metadata until you
re-run `pip install --upgrade -e .`.

Without the pip step, `hermes --version` reads the git tag from the checkout
but the actual imported modules are stale. This desync is invisible until
something breaks due to missing code.

## Quick Version (copy-paste)

```bash
cd /usr/local/lib/hermes-agent && git pull && source venv/bin/activate && pip install --upgrade -e . && deactivate && hermes --version && systemctl --user restart hermes-gateway
```

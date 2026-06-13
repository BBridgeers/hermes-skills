# Firecrawl — VPS Setup Notes

## CLI Binary

- **Path**: `/root/.hermes/node/bin/firecrawl`
- **Version**: 1.18.0 (installed via `npm install -g firecrawl-cli@latest`)
- **PATH**: added to `/root/.bashrc` — `export PATH="/root/.hermes/node/bin:$PATH"`

## API Key

- **File**: `/root/.hermes/.env`
- **Variable**: `FIRECRAWL_API_KEY=fc-3c3...`
- **Pitfall**: The `.env` file originally had a leading space (`FIRECRAWL_API_KEY= fc-3c3...`) which silently broke all parsing by `source`, `set -a`, and `xargs`. The `cut -d= -f2-` trick returns an empty value when there's a leading space because `cut` splits on `=` and the blank after `=` becomes part of the field. **Always grep-check for leading/trailing whitespace** in `.env` key lines before debugging why an env var is empty.

## Sourcing the Key for CLI Use

```bash
export FIRECRAWL_API_KEY=$(grep '^FIRECRAWL_API_KEY=' /root/.hermes/.env | cut -d= -f2-)
```

Or, if the `.env` file is clean (no leading spaces):

```bash
set -a && source /root/.hermes/.env && set +a
```

## Cache Directory

- `/root/.firecrawl/` — created, added to `/root/.gitignore`

## Verified Working

```bash
firecrawl --version     # 1.18.0
firecrawl --status      # shows auth state
firecrawl scrape "https://firecrawl.dev" --json  # returns clean markdown
```

# Safe State-File Append Pattern

`~/.hermes/state/vuln-scanned.json` is a JSON array. Direct shell append
(`echo >> file`) breaks JSON structure. Always read → modify → write with a
Python script that handles empty/missing files and preserves existing entries.

## Pattern

```python
import json

PATH = '/root/.hermes/state/vuln-scanned.json'

# 1. Read existing entries (handle missing/empty gracefully)
try:
    with open(PATH) as f:
        entries = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    entries = []

# 2. Append new entry
new_entry = {
    "repo": "owner/repo",
    "scanned_at": "2026-05-30T05:01:00Z",
    "findings": 0,
    "channel": "clean-no-findings"
}
entries.append(new_entry)

# 3. Write back
with open(PATH, 'w') as f:
    json.dump(entries, f, indent=2)
```

## Gotcha

If you read with `open(path)` and the file is a valid JSON array, then write
with `json.dump([new_entry], ...)` (a fresh list), you **overwrite** all prior
entries. Always append to the list you read, then write the whole list back.

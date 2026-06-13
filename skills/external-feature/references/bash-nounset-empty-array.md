# BASH: `set -euo pipefail` + empty array for-loop = crash on bash < 4.4

## The Bug

On bash versions before 4.4 (including macOS default bash 3.2), `set -u` (nounset) causes
`for x in "${array[@]}"` to trigger **"unbound variable"** when the array is empty —
even if the array was declared with `local arr=()`.

```bash
#!/usr/bin/env bash
set -euo pipefail

highs=()          # empty array — declared, not unbound
for h in "${highs[@]}"; do   # 💥 "highs[@]: unbound variable" on bash 3.2
    echo "$h"
done
# Never reaches here on bash 3.2 — script exits non-zero
```

This was [fixed in bash 4.4](https://lists.gnu.org/archive/html/bug-bash/2016-01/msg00057.html).
macOS ships bash 3.2 by default (GPLv3 licensing blocks newer versions).

## Real-world impact

In `aeon`'s `scan.sh`, this caused `add-skill` to falsely report "BLOCKED: has security issues"
for skills that passed the scan with zero findings. The script exited non-zero from the
nounset trap, and `add-skill` interpreted any non-zero exit as a security failure.

## The Fix

Guard every for-loop over a potentially-empty array with a length check:

```bash
# ✅ Safe on all bash versions
if [[ ${#highs[@]} -gt 0 ]]; then
    for h in "${highs[@]}"; do
        echo "$h"
    done
fi
```

## Detection checklist

When a shell script with `set -euo pipefail` exits non-zero with no error output:
1. Look for `for x in "${array[@]}"` loops
2. Check if the array can be empty at that point
3. Add `[[ ${#array[@]} -gt 0 ]]` guards

The `?` in the exit code is the signature — the script dies silently because `2>/dev/null`
or `set -e` swallows the error message.

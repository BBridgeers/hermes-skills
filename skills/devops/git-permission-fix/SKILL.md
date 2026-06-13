---
name: git-permission-fix
description: Fix Git permission errors by configuring safe directories
tags: [devops, git, troubleshooting]
---

# Git Permission Fix

## Problem
Git throws PermissionError when trying to access repositories in certain directories, typically manifesting as:
```
[Errno 13] Permission denied: '/root/.git'
```

## Solution
Configure Git to recognize specific directories as "safe" to bypass security restrictions.

## Steps

1. Add the problematic directory as a safe directory:
   ```bash
   git config --global --add safe.directory /root
   ```

2. If working with specific project directories, add those as well:
   ```bash
   git config --global --add safe.directory /root/.hermes/hermes-agent
   ```

3. Restart any related services to ensure the changes take effect:
   ```bash
   docker restart hermes-agent
   ```

## Verification
Check that the containers are running properly:
```bash
docker ps | grep hermes
```

Test the Git configuration by running any Git-dependent operations or scripts that were previously failing.

## When to Use This Approach
- When encountering PermissionError related to Git repository access
- When Git refuses to operate on repositories despite proper file permissions
- When working in Docker environments where Git security restrictions interfere with operations

## Related Skills
- hermes-docker-migration
- hermes-onboard
- security-guard
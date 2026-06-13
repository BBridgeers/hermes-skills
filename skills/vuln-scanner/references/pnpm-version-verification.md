# pnpm Version Verification

When `pnpm audit` reports advisories, you must verify which versions are actually
installed before reporting them as confirmed findings. The package may already be
at the patched version, or the advisory may not apply to the installed range.

## Direct Dependencies — YAML Parsing

`pnpm ls --depth=0 -r --json` often produces empty or unusable output in
headless/CI environments. Instead, parse `pnpm-lock.yaml` directly:

```python
import yaml
with open('pnpm-lock.yaml') as f:
    data = yaml.safe_load(f)

importers = data.get('importers', {})
for importer, info in importers.items():
    for dep_type in ('dependencies', 'devDependencies'):
        for name, ver in info.get(dep_type, {}).items():
            version = ver.get('version', '') if isinstance(ver, dict) else ver
            print(f'{importer}: {name}@{version}')
```

Each version string is the **resolved** version (e.g., `15.5.15(@babel/core@7.29.0)(...)`).
Extract just the semver part before the first `(` for comparison.

## Comparing Against Advisory Ranges

For each advisory from `pnpm audit --json`:

1. Read `vulnerable_versions` and `patched_versions` from the advisory entry
2. Check if the installed version falls in the vulnerable range
3. **Example**: Advisory says `vulnerable_versions: <=3.1.0`, `patched_versions: >=3.1.1`.
   If installed is `3.1.0` → CONFIRMED. If installed is `3.1.1` → NOT vulnerable.
4. **Edge case**: Advisory says `<8.5.10`. If installed is `8.5.10` → NOT vulnerable.
   The `<` is strict. Don't report it.

## Transitive Dependencies

Some advisories affect packages that aren't direct dependencies (e.g., `fast-uri`,
`protobufjs`). These are pulled in transitively. To verify their resolved versions:

```bash
grep -A2 "resolution:" pnpm-lock.yaml | grep -B1 "fast-uri@\|protobufjs@"
```

Or use `pnpm why <package>`:

```bash
pnpm why fast-uri 2>/dev/null
```

For transitive deps, reporting is still valid — they need bumping via the direct dep
that pulls them in (or via `pnpm.overrides` in package.json).

## Bundle Approach

When multiple advisories affect the same package (e.g., 10+ protobufjs CVEs),
bundle them into a single finding: "protobufjs — N advisories, bump to ≥X.Y.Z".
Don't create one PR/finding per advisory for the same package.

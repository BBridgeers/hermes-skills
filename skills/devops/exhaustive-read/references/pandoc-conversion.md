# Pandoc .docx Conversion Reference

## Installation
```bash
apt-get install -y pandoc
# Already installed on Hermes VPS (v3.1.3)
```

## Single File Conversion
```bash
pandoc "file.docx" -t markdown -o "file.md"
```

## Batch Directory Conversion
```bash
for f in /path/to/*.docx; do
  base=$(basename "$f" .docx)
  pandoc "$f" -t markdown -o "/tmp/converted/${base}.md" 2>&1 && echo "OK: $base" || echo "FAIL: $base"
done
```

## Common Failure Modes

1. **"couldn't unpack docx container"**: File has .docx extension but is actually markdown. Use `head` to check.
2. **"Did not find end of central directory signature"**: Same — misnamed file.
3. **Empty output (0 bytes)**: Corrupted .docx or password-protected.

## When Pandoc Fails
Just read the file as text with `cat` or `head` — it's probably markdown with the wrong extension.

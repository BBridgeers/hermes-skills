# GDrive to GitHub Project Consolidation

## Pattern

When consolidating a scattered project from GDrive into a GitHub repo:

1. **Pull everything**: Use `rclone copy` to pull all folders to VPS
2. **Identify duplicates**: Compare file checksums between "Main" and "Copy" folders
3. **Find contamination**: Grep for wrong-project keywords across all files
4. **Convert .docx**: Use pandoc to convert all binary .docx to markdown
5. **Clean**: Remove contaminated files, replace with correct versions
6. **Push**: GitHub private repo, strip noise via .gitignore

## Contamination Check Commands

```bash
# Find tensor ring contamination in DFW project
grep -rl "tensor\|sacred\|Cubit\|Etsy\|copper wire" /path/to/project/

# Find personal docs mixed in
grep -rl "credit score\|authorized user\|Citi card\|Father" /path/to/project/
```

## Common Contamination Patterns

- Appendices from a completely different business (tensor rings mixed into web design project)
- Personal finance/credit repair documents
- Family legal agreements
- Old job applications and cover letters

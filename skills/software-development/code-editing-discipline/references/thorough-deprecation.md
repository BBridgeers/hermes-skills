# Thorough Deprecation Protocol

When a script, pipeline, or module is deprecated in favor of a replacement, delete ALL traces —
not just the file. The user expects surgical, verifiable removal with zero residual references.

## Protocol

1. **Identify all files to delete** — the scripts themselves, plus associated artifacts:
   - Log files (`.log`)
   - Progress/checkpoint files (`.json`, `.pkl`)
   - Compiled caches (`__pycache__/`, `.pyc`)
   - Backup directories created by the scripts

2. **Search for cross-references** — before deleting, search the entire project
   (and skill directory) for any mention of the deprecated filenames:
   ```
   search_files(pattern="deprecated_script_name|associated_file", path=".", target="content")
   search_files(pattern="deprecated_script_name|associated_file", path="~/.hermes/skills", target="content")
   ```

3. **Delete the files** — use `rm -v` for audit trail. Delete optional artifacts
   (progress files, backup dirs) with `ls` check first to avoid noise if they
   don't exist.

4. **Update all references** — every cross-reference found in step 2 must be
   patched. This includes:
   - Skill files (SKILL.md)
   - Reference documents (references/*.md)
   - Project documentation (MASTER_EXECUTION_DOC.md, README.md)
   - Inline comments in other scripts

5. **Verify zero traces** — re-run the searches from step 2. They MUST return
   zero hits. If any remain, fix them. The user explicitly demands "any trace
   across any potential file" is gone.

## Anti-Patterns

- Deleting only the main script but leaving logs/progress files behind
- Updating the skill but forgetting reference docs that also mention the deprecated file
- Skipping the final verification search — the user will find lingering references
- Leaving pycache artifacts

## Real Example

DFW Web Design NOW enrichment consolidation:
- Deleted: `enrich_owners.py` (673 lines), `enrich_ghost_owners.py` (188 lines)
- Deleted associated: `enrich_owners.log`, `ghost_enrich.log`, `ghost_enrich_progress.json`,
  `__pycache__/enrich_owners.cpython-312.pyc`
- Updated: `dfw-web-design-now/SKILL.md` (3 patches), `python-regex-patterns/references/enrichment-pipeline.md` (full rewrite)
- Verified: 0 hits for `enrich_owners` or `enrich_ghost` in project + skills
- Result: scripts/ directory has exactly 1 enrichment script: `enrich_waterfall.py`

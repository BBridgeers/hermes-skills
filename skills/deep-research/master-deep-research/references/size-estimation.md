# Size Estimation Reference

Conversion table and edge cases for `--min-kb` and `--min-words` parameter parsing.

## Words → KB Conversion

Markdown reports carry formatting overhead (headers, code blocks, tables, citation tags like `[#1003]`, bold, links, blockquotes). The conversion factor accounts for this.

| Words | Approximate KB | Notes |
|---|---|---|
| 600 | ~4 KB | Shallow mode |
| 2,000 | ~13 KB | Minimum coherent deep report |
| 5,000 | ~33 KB | Standard research brief |
| 10,000 | ~67 KB | Comprehensive report |
| 15,000 | ~100 KB | Full whitepaper |
| 20,000 | ~133 KB | Near the 150 KB default target |
| 22,000 | ~147 KB | Typical 150 KB target |
| 30,000 | ~200 KB | Book-chapter scale |
| 50,000 | ~333 KB | Multi-chapter treatise |

## Conversion Formula

```
kb = words / 150
words = kb * 150
```

**Factor: ~150 words per KB** for formatted markdown. This accounts for:
- Headers (`##`, `###`) adding ~2-5 chars of non-word overhead per section
- Citation tags (`[#1003]`) adding ~6-8 chars per citation
- Code blocks adding significant non-word characters
- Tables adding pipe/alignment characters
- Bold (`**text**`) adding 4 chars per bold span
- Links (`[text](url)`) adding URL length overhead

Pure unformatted English prose runs ~180 words/KB. The 150 factor is the **conservative** (pessimistic) estimate for markdown-heavy reports.

## Edge Cases

### Citation-dense reports
Reports with many `[#SOURCE_ID]` citations per paragraph (3-5 citations per sentence) can drop to **~120 words/KB** due to citation tag overhead. The expansion loop's size check uses raw filesize, so this doesn't break the target — the report just hits the KB target with fewer words.

### Table-heavy reports
Reports dominated by tables (comparison matrices, data tables) can drop to **~100 words/KB**. Table formatting (pipes, dashes, alignment) adds substantial non-word characters.

### Code-heavy reports
Reports with embedded code blocks can hit **~80 words/KB**. Code is counted as "content" for size estimation but contains very few natural-language words.

### Expansion loop interaction
The expansion loop checks `filesize(draft_report.md) / 1024` directly — it doesn't estimate from word count. So the conversion factor only matters for the `--min-words=N` parameter at parse time. After that, KB is the canonical unit.

## Parameter Precedence

1. `--min-kb=N` — sets `min_size_kb` directly. Takes precedence.
2. `--min-words=N` — converts to KB using 150 words/KB factor. Only used if `--min-kb` not set.
3. Neither set — default 150 KB (`min_size_kb=150`).
4. `--min-kb=0` — disables size target entirely. Expansion loop skipped.

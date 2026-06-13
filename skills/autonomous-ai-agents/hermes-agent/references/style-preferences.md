# User Style Preferences

**For this user (Blake):**

| Preference | Action |
|------------|--------|
| VIN as PRIMARY entry | Treat VIN modality first in all analysis, documentation, and UI discussions |
| Direct data delivery | Dump the list/data, skip architecture narratives unless asked for explanation |
| Live validation | For UI/function testing: browser automation, NOT code analysis, NOT theory |
| Concise output | No preamble, no "here is the output", no "let me explain" |
| "Test every button" | Literally click each button, document every result, no assumption |

**When user says "test every button":**
1. Navigate to each page (/fleet, /comparison, /analytics, /sweeps)
2. Click EVERY button visible in DOM snapshot
3. Document each result: WORKS or BROKEN
4. Report broken functionality, don't assume

**When user says "keep going":**
1. Continue systematic testing — don't pause to summarize
2. Test ALL items in each category, not just "sample"
3. Commit each finding as work progresses

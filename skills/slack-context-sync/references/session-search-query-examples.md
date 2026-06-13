# Session Search Query Examples

## Effective Query Patterns from Operational Experience

### Date-Based Queries (Most Reliable)
```bash
session_search(query="May 20")  # Current month/day
session_search(query="20260520") # YYYYMMDD format  
session_search(query="2026-05-20") # ISO format
```

### Time-Window Probes
```bash
session_search(query="14:")      # Hour prefix (2 PM sessions)
session_search(query="2:27")     # Specific time pattern
session_search(query="09:")      # Morning sessions
```

### Skill-Based Discovery
```bash
session_search(query="external-feature OR vuln-scanner OR github-trending")
session_search(query="hermes-heartbeat")
session_search(query="slack-context-sync") 
```

### File System Activity Fallbacks
When session_search returns limited results:
```bash
# Check for recent file modifications
find ~/.hermes -type f -mmin -60

# Look for recent Markdown files (4-hour window)
find ~/.hermes -name "*.md" -mmin -240

# Check for recent digest files
find ~/.hermes -name "*digest*" -mmin -240

# Examine logs directory for recent sessions
ls -la ~/.hermes/logs/

# Check skill output directories
find ~/.hermes/skills -name "*.md" -mmin -240
```

### Multi-Query Strategy
Plan for 4-5 different query attempts:
1. Broad recent search (no query)
2. Date-based queries
3. Skill-based queries  
4. Time-window queries
5. File system activity checks

### Cold Start Handling
When no new activity found:
- Preserve existing context file
- Respond with `[SILENT]` to suppress delivery
- Only update if substantive new information exists
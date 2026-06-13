---
name: python-regex-patterns
description: Python regex patterns for text extraction, validation, and scraping. Common pitfalls — especially re.IGNORECASE with [A-Z] character classes — and canonical fixes.
triggers:
  - Building regex patterns for text extraction or validation
  - Writing owner-name, address, or entity extraction from web snippets
  - Using re.compile with flags for scraping or parsing
  - Regex unexpectedly matching lowercase when [A-Z] is used with IGNORECASE
---

# Python Regex Patterns

Common patterns and pitfalls for text extraction with Python's `re` module.

## Pitfall: `re.IGNORECASE` makes `[A-Z]` match lowercase

When `re.IGNORECASE` is applied to a pattern containing `[A-Z]`, the character class
becomes case-insensitive and matches BOTH uppercase and lowercase letters.
This is non-obvious and leads to silent bugs in name extraction.

**Bad (matches lowercase words like "in", "by", "the"):**
```python
pat = re.compile(r"founded\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})", re.IGNORECASE)
text = "Founded by Robert Johnson in 1998"
pat.search(text).group(1)  # → "Robert Johnson in"  ← BUG
```

**Good (use `(?-i:...)` inline flag for the name portion):**
```python
_NAMEGRP = r"(?-i:([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}))"
pat = re.compile(rf"founded\s+by\s+{_NAMEGRP}", re.IGNORECASE)
text = "Founded by Robert Johnson in 1998"
pat.search(text).group(1)  # → "Robert Johnson"  ← CORRECT
```

The rule: never use `[A-Z]` inside a `re.IGNORECASE` pattern without the `(?-i:...)`
wrapper. Alternatively, use `[A-Za-z]` explicitly if case-insensitivity is desired.

## Name extraction patterns (battle-tested)

Reusable template for extracting person names from text:

```python
_NAMEGRP = r"(?-i:([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}))"

OWNER_PATTERNS = [
    # "Owned by: Name"
    re.compile(rf"Owned\s+by:\s+{_NAMEGRP}", re.IGNORECASE),
    # "is owned by Name"
    re.compile(rf"is\s+owned\s+by\s+{_NAMEGRP}", re.IGNORECASE),
    # "Name is the owner/president/CEO"
    re.compile(rf"{_NAMEGRP}\s+(?:is|are)\s+(?:the\s+)?(?:owner|founder|president|ceo|principal)", re.IGNORECASE),
    # "Name Named [New] President"
    re.compile(rf"{_NAMEGRP}\s+(?:named|appointed|serves?\s+as|takes?\s+over\s+as)\s+(?:the\s+)?(?:new\s+)?(?:president|owner|ceo|principal|founder)", re.IGNORECASE),
    # "President: Name"
    re.compile(rf"(?:President|Owner|Founder|CEO|Principal)[:\s]+{_NAMEGRP}", re.IGNORECASE),
    # "owned/founded by Name"
    re.compile(rf"(?:owned|owner|founded|founder|principal|president|ceo|proprietor)\s+(?:by\s+)?{_NAMEGRP}\b", re.IGNORECASE),
    # "Registered Agent: Name"
    re.compile(rf"Registered\s+Agent[:\s]+{_NAMEGRP}", re.IGNORECASE),
]
```

## Name validation

```python
EXCLUDED_NAMES = {"google", "facebook", "yelp", "bbb", "houzz", "nextdoor"}

def _is_valid_person_name(name: str) -> bool:
    if len(name) < 4 or len(name) > 50:
        return False
    name_lower = name.lower().strip()
    for excluded in EXCLUDED_NAMES:
        if excluded in name_lower:
            return False
    parts = name.split()
    if len(parts) < 2:
        return False
    if not all(p[0].isupper() for p in parts if p):
        return False
    if any(c.isdigit() for c in name):
        return False
    return True
```

## DuckDuckGo search for data enrichment

The `ddgs` library (pip install ddgs) provides free web search for enrichment
pipelines. Useful for finding business owners, contact info, and entity data
when paid APIs aren't available.

```python
from ddgs import DDGS

def search_ddg(business_name: str, city: str):
    query = f'"{business_name}" {city} TX owner'
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        owner = extract_owner_from_text(f"{title}. {body}")
        if owner:
            return owner
    return None
```

Suppress DDGS's noisy HTTP logging:
```python
for noisy in ["ddgs", "duckduckgo_search", "primp", "urllib3", "httpx"]:
    logging.getLogger(noisy).setLevel(logging.WARNING)
```

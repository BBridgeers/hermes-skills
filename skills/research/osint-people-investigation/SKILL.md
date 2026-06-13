---
name: osint-people-investigation
description: Systematic OSINT on phone numbers, names, or businesses — multi-provider search, business registry cross-referencing, and dossier compilation.
version: 1
triggered-by: User asks to investigate/lookup/OSINT a phone number, name, or business entity.
---

# OSINT People & Phone Investigation

Systematic open-source intelligence gathering on individuals, phone numbers, or businesses using layered provider searches, business registries, social profiles, and public records.

## Pattern

User provides a phone number, name, or business entity and wants a comprehensive dossier: identity, background, associations, professional history, and any other discoverable open-source data.

## Protocol

### Phase 1 — Initial Multi-Provider Search (parallel)

Launch searches across at least 3 providers simultaneously. Phone numbers should be searched with and without country code, with quotes, and with common suffixes ("phone", "owner", "who called").

```
# Searches to fire in parallel:
1. web_search_plus(provider="tavily", query="<number or name>")
2. web_search_plus(provider="serper", query=""<number>" phone")
3. web_search_plus(provider="brave", query="<number>")
4. web_search(query=""<number>"")
```

**Provider reliability note:** Tavily is the most consistent for phone number lookups. Serper and Brave may return empty or fail. Firecrawl (used by web_extract) frequently hits credit limits. Route extraction through web_extract_plus with provider="linkup" or provider="tavily" when Firecrawl fails.

### Phase 2 — Identify Primary Associations

From Phase 1 results, identify:
- Business names linked to the number
- Owner/principal names
- Locations (city, state)
- Alternative phone numbers listed for the same entity

### Phase 3 — Cross-Reference Business Registries (parallel)

For each business identified, pull:
- **BBB profile** — goldmine for owner name, address, years in business, entity type, incorporation date, alternate contacts. Use web_extract_plus(url, provider="linkup").
- **Yelp listing** — may show different phone numbers and owner names.
- **State business registry** — search for "<business name> <state> registered agent" or "<business name> <state> LLC".
- **Nextdoor business page** — often has owner photos and community reviews.

### Phase 4 — Professional Profiles

- **LinkedIn** — search for owner name + company. Extract career history, education, location, connections count, recent activity.
- **Twitter/X** — search for company/owner handles found in BBB or LinkedIn profiles.
- **Facebook** — business pages often linked from BBB profiles.

### Phase 5 — Area Code Analysis

If a phone number doesn't match the business location (e.g., Louisiana area code for a Colorado business), note it — the owner likely acquired the number in the area code region earlier in their career and kept it. This can hint at prior geographic history.

### Phase 6 — Compile Dossier

Output format: a clean table with key fields (number, owner, business, location, background), then a narrative background section with career history, education, and any notable personal details surfaced from social profiles.

## Pitfalls

- **Single-provider dependency:** Relying on one search provider (especially web_search or web_extract alone) will miss critical results. Always use 3+ providers.
- **Firecrawl credit exhaustion:** web_extract and web_search may fail with "Payment Required." Fall back to web_extract_plus with provider="linkup" or "tavily", or use browser_navigate for critical pages.
- **All-search-down recovery:** When ALL providers fail simultaneously (Firecrawl, Serper, Brave, Google, BBB, business directories, browser CAPTCHA), do NOT abandon the deliverable. Complete the enrichment work with available data, use a column like `owner_found` set to `"No (search unavailable)"` or `"Pending (retry needed)"` to flag every record needing follow-up, and create the output CSV with all known columns populated. This makes the file immediately usable while preserving the retry queue for when search APIs recover. Never hold the master file hostage to a single enrichment dimension.
- **Conflicting owner names:** Different aggregator sites (BBB vs Yelp) may show different owners. Trust BBB first for registered business data, but note discrepancies.
- **Stale data:** Business directories may show dissolved entities or outdated addresses. Always check incorporation status via state registry.
- **International numbers:** For non-US numbers, try tellows.in, whoseno.com, callfilter.app — and note the carrier/region from the area code prefix.

## Verification

- Every claim in the dossier must be traceable to a specific source (BBB, LinkedIn, state registry, etc.).
- If two sources conflict, note it rather than silently picking one.
- Mark any inferred data (e.g., "likely moved from Louisiana") as inference, not fact.

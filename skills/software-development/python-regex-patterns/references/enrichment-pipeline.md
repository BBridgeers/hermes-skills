# Web Enrichment Pipeline Pattern

Real-world example from a business-owner-enrichment pipeline built for
/root/workspace/dfw-web-design-now/scripts/enrich_waterfall.py.

## Architecture

Pipeline reads a CSV, tries 7 free sources in priority order, stops on first hit,
saves progress for resumption. Trades-aware (plumbers, HVAC, electricians get TDLR lookup first).
County-aware (auto-routes Dallas vs Tarrant County DBA based on city).

## Sources tried (ordered by priority)

| Source | Method | Confidence | Notes |
|--------|--------|------------|-------|
| TDLR (Texas Dept of Licensing) | License search for trades | High | Mandatory state licensing: HVAC, plumbers, electricians |
| TX SOS Direct | POST to sos.state.tx.us → detail page scrape | High | Registered agents / governing persons |
| County DBA (Dallas + Tarrant) | Assumed name filing search | High | Catches sole props who never incorporated |
| BBB DFW | GET BBB.org profile search | Medium | "Principal" / "Owner" field extraction |
| OpenCorporates API | REST officer lookup | Medium | 200M+ global registry, free 500/mo |
| Exa Neural Search | Semantic "owner of X" search | Low | Free 1,000/mo, searches BBB/Yelp/Manta/LinkedIn/etc |
| SpiderFoot Queue | Flags to spiderfoot_queue.txt | Manual | Self-hosted Docker for unresolved records |

## Resumption pattern

```python
PROGRESS = set()  # loaded from JSON

for idx, row in enumerate(rows):
    if idx in PROGRESS:
        continue
    result = pipeline.process_row(row)
    update_row(row, result)
    PROGRESS.add(idx)
    save_progress(PROGRESS)  # atomic after each row
```

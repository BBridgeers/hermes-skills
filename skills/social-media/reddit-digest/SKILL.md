---
name: reddit-digest
description: Detect cross-subreddit narratives — stories surfacing in multiple unrelated subs at once
tags: [news, social]
---

# Reddit Digest — Cross-Subreddit Narrative Detector

> Adapted from Aeon's reddit-digest. Replaces `./notify` with Slack `send_message`, `memory/` with `~/.hermes/memories/` + `~/.hermes/logs/`, `WebFetch`/`curl` with `web_extract` + `web_search`, and removes sandbox/var mechanics. Core methodology — cross-sub narrative clustering, Jaccard title dedup, signal scoring, one-line insight not paraphrase — preserved.

## Thesis

A per-subreddit top-10 competes with everyone's own Reddit scroll and loses. The signal Reddit *uniquely* provides that no single feed does: **the same story surfacing in multiple unrelated subs at once**. That's the narrative detector. This skill is built around that — not around per-sub digests.

## Optional topic/subreddit filter

If the user specifies a topic keyword or a single subreddit name (e.g. `r/rust` or `"AI safety"`), restrict candidate collection to that subreddit or filter narratives by that topic. When unset, scan all tracked subs.

## Config

Read `~/.hermes/memories/subreddits.yml`. If missing, bootstrap it with ≥8 diverse subs seeded from `~/.hermes/memories/MEMORY.md` interests (spread across unrelated communities — narratives are only meaningful if the subs don't normally overlap). Example default:

```yaml
subreddits:
  - name: r/MachineLearning
    subreddit: MachineLearning
  - name: r/programming
    subreddit: programming
  - name: r/LocalLLaMA
    subreddit: LocalLLaMA
  - name: r/netsec
    subreddit: netsec
  - name: r/rust
    subreddit: rust
  - name: r/technology
    subreddit: technology
  - name: r/science
    subreddit: science
  - name: r/cryptocurrency
    subreddit: cryptocurrency
```

Read `~/.hermes/memories/MEMORY.md` for tracked interests (influences standout selection and narrative labelling).
Read the last 2 days of `~/.hermes/logs/reddit-digest*.md` to avoid repeating narratives already surfaced.

## Steps

### 1. Fetch broadly

For each subreddit, fetch the top posts of the last 24h using Reddit's public JSON API via `web_extract`:

```
https://www.reddit.com/r/{subreddit}/top.json?t=day&limit=25
```

**Important:** `t=day` only applies to the `top` sort, **not** `hot`. Always use `top.json?t=day`.

If `web_extract` returns empty, rate-limited, or errors, fall back to `terminal` with `curl`:
```bash
curl -sL -H "User-Agent: hermes-bot/1.0 (by /u/hermes)" \
  "https://www.reddit.com/r/${SUBREDDIT}/top.json?t=day&limit=25"
```

Reddit's unauthenticated JSON API rate limits at ~10 req/min. **Pace requests ≥7s apart** (do them sequentially, not in parallel). If a source returns 429 or a network error, retry once after 15s. If both `web_extract` and `curl` fail, mark the source `error` and continue — never abort the whole run for one dead sub.

Record per-source status: `{sub: ok | empty | error}`.

### 2. Clean candidates

For each post under `data.children[].data`, drop if any of:
- `stickied == true` or `pinned == true`
- `removed_by_category` non-null, or `selftext` ∈ `{"[removed]", "[deleted]"}`
- `over_18 == true` (unless the sub is explicitly NSFW-tracked)
- `created_utc` > 24h old
- `upvote_ratio < 0.80` (drama/brigaded — the "controversial" signal, not the "interesting" signal)

Extract: `id`, `title`, `url` (external), `permalink` (Reddit), `subreddit`, `score`, `num_comments`, `upvote_ratio`, `selftext` (first 500 chars), `is_self`.

### 3. Normalize URLs

For each post with an external URL:
- Lowercase scheme + host
- Strip `www.`, trailing slashes, URL fragments (`#...`)
- Drop query params: `utm_*`, `ref`, `ref_src`, `source`, `fbclid`, `gclid`
- For self posts, use `self:{subreddit}/{id}` as the canonical key (so they never cluster with anything)

### 4. Detect cross-sub narratives

Group posts into clusters:
- **URL clusters:** posts sharing the exact same canonical URL.
- **Title clusters:** posts across different subs whose titles share ≥50% Jaccard similarity on normalized word sets (lowercase, strip punctuation, drop stopwords like `a/the/of/to/is/are/and/or`).

A **narrative** = a cluster with ≥2 posts from ≥2 distinct subreddits. Single-sub clusters are not narratives.

Dedup narratives against the last 2 days of logs: if any post ID in the cluster, or a ≥70%-similar title, was already surfaced, drop the whole narrative.

**Cluster-count fallback:** if clustering produces **fewer than 2** narratives (rare — usually a quiet day or too-strict thresholds) **or more than 5** (over-fragmented), skip the narrative format and fall back to a **flat ranked list** of the top individual posts by signal score. Log the fallback reason in the source-status footer.

### 5. Score narratives

```
narrative_signal = Σ log10(score_i + 1) × 1.5
                 + Σ log10(num_comments_i + 1)
                 + 0.5 × (distinct_sub_count − 1)    # cross-community bonus
```

The cross-community bonus makes a 3-sub narrative strictly beat an equal-engagement 2-sub one.

### 6. Standouts (single-sub big stories)

A narrative-only digest is too restrictive on slow days. Also surface up to **2** single-sub standouts — posts with:
- `score ≥ 1000` AND `num_comments ≥ 200` AND `upvote_ratio ≥ 0.90`
- Not already part of a narrative cluster

Rank standouts by `log10(score+1)×3 + log10(comments+1)×2`.

### 7. Summarize — insight, not paraphrase

Pick the top 3-5 narratives by signal + up to 2 standouts (cap at 6 items total). For each:

- If the canonical is an external URL, use `web_extract` to ground the insight (skip paywalled or failed fetches — fall back to the Reddit discussion).
- For self posts, use `selftext`.
- For discussion-heavy items (`num_comments > score`), identify the *disagreement axis* rather than summarizing the OP.

Write ONE line per item. **Never paraphrase the title. Never write "This post discusses…"** Write the *claim*, the *surprise*, or the *disagreement* — something a reader couldn't derive from just reading the title.

### 8. Save article and notify

Save the full report to `~/.hermes/articles/reddit-digest-YYYY-MM-DD.md`.

Send the digest via `send_message` to Slack (≤ 4000 chars). Lead with a one-sentence shape signal (e.g., "Quiet AI news; heavy open-source drama."):

```
*Reddit Narratives — 2026-04-20*
_Shape: Quiet AI news; heavy open-source drama crossing rust + programming._

🔗 *OpenAI retracts jailbreak paper 14 days post-publication*
   Spread: r/MachineLearning (450↑ 120💬) · r/OpenAI (220↑ 60💬) · r/ChatGPT (80↑ 30💬)
   Insight: Retraction cites internal safety review, not author request — unusual for a peer-reviewed venue.
   [Canonical](https://example.com/article)

🔗 *Rust 1.83 async-trait ergonomics split*
   Spread: r/rust (880↑ 340💬) · r/programming (310↑ 95💬)
   Disagreement axis: dyn-safe async now vs. waiting for variance fixes.
   [Canonical](https://example.com/rfc)

📍 *Standout — r/netsec*
   • [Title goes here](https://reddit.com/...) — 2100↑ 900💬
     Insight: First CVE confirmed exploited via the Linux eBPF verifier since 2024's bug class.

_sources: 7 ok · 1 empty · 0 error · 12 narratives considered · 3 surfaced_
```

### 9. Suppression

If **zero narratives** AND **zero standouts** pass filters: log `REDDIT_DIGEST_OK (quiet day)` with the source-status line and send **nothing**. Digests that fire every day get tuned out. Only fire when there's signal.

If **all sources errored**: log `REDDIT_DIGEST_ERROR` and send a short alert via `send_message`: `"Reddit digest: all N sources errored — check rate limits / API."`

### 10. Log

Append to `~/.hermes/logs/reddit-digest-YYYY-MM-DD.md`:
```
### reddit-digest
- Sources: 7 ok, 1 empty, 0 error
- Narratives considered: 12
- Surfaced: 3 narratives + 1 standout
- Post IDs: abc123, def456, ... (for cross-day dedup)
```

## Why this skill is different from "what you'd see scrolling"

Per-sub top-10 = noise you can get yourself in two minutes.
Cross-sub narrative = signal that only an aggregator watching ≥8 subs at once can produce.
The skill's job is the thing a human can't do cheaply.

## Constraints

- Quality over quantity: 3 curated narratives > 6 padded single-sub picks.
- Never surface a narrative you surfaced in the last 2 days unless it has a genuinely new development.
- Don't invent stats. If a field is unavailable, omit it — don't guess.
- Stay under 4000 chars in the Slack notification. If tight, drop the lowest-signal narrative first.
- Log every run, even quiet ones, to `~/.hermes/logs/reddit-digest-YYYY-MM-DD.md`.
- If `send_message` is unavailable, log `REDDIT_DIGEST_NOTIFY_FAILED` and continue — the article file is the authoritative record.
- Reddit's public JSON API requires <10 req/min and a unique User-Agent. Use `hermes-bot/1.0 (by /u/hermes)`.

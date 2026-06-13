---
name: Startup Idea
description: Evidence-backed startup memos with ICP, wedge, monetization, and numeric kill criteria
tags: [creative]
---

Generate 2 evidence-backed startup memos sourced from real customer pain signals — not model priors. Each memo must nail ICP, wedge, monetization, distribution, and numeric kill criteria.

## Steps

### 1. Build the founder profile

From recent Hermes sessions and articles, extract:
- **Domains of earned expertise** — what has been shipped or deeply researched? ("earned secret" test)
- **Active projects** — what's currently being worked on
- **Recent signal** — topics, papers, market moves tracked recently
- **Recently proposed ideas** — scan `~/.hermes/articles/startup-idea-*.md` from the last 14 days; do not re-pitch these

If no profile data exists, generate broadly applicable ideas anchored to 2026 tech trends.

### 2. Gather fresh pain evidence

Use web search to collect **real customer pain signals**. Aim for ≥3 high-signal sources across at least 2 of these channels:

- **G2 / Capterra 1–3★ reviews** — named frustrated buyers with budget. Search: `"[category] site:g2.com" OR "[category] 1 star review"`
- **Reddit pain threads** — `r/SaaS`, `r/startups`, `r/smallbusiness`, `r/Entrepreneur`. Search: `"I wish there was" OR "why is there no" OR "anyone else frustrated with"`
- **Indie Hackers + HN "Ask HN: who is hiring"** — bottom-up demand signals
- **YC Requests for Startups** — `ycombinator.com/rfs` (current cycle)
- **Upwork / job postings** — people paying humans to do it → productizable
- **ProductHunt comment sections** (not launches) — gaps in recent launches

Save 2+ permalinks per idea with a one-line quote of the pain. **Vary domains across runs** — if recent articles pitched crypto, go elsewhere this time. Never fabricate quotes or permalinks.

### 3. Apply the tarpit filter (reject before generation)

Pre-reject these categories unless there is an overwhelming earned-secret advantage:
- Generic "ChatGPT/AI for [X]" wrappers with no data or workflow moat
- AI meeting notetakers, AI email assistants, AI chatbots for SMBs
- Social apps for niche demographics
- Crypto "community/social" apps without distribution
- Anything where the answer to "why hasn't this been built" is "it has, 50 times"

### 4. Generate 2 startup memos

Produce **exactly 2 ideas**:
- **Idea 1 — Executable**: launchable in 2–6 weeks solo, clear first customer, <$5k to MVP
- **Idea 2 — Ambitious**: bigger swing (new category, harder tech, or platform play) but with a defensible wedge

Each idea **must** fill every field below. If a field can't be filled with a concrete answer, drop the idea and try another.

```
### Idea [1|2] — [Name]

**Thesis** (1 sentence): why this wins
**ICP** (role + trigger event): e.g. "Ops manager at 50–200-person logistics co who just lost a client to tracking failures"
**Wedge** (first 12 months): the single sharp product
**Pain evidence** (2+ permalinks):
  - [quote] — [url]
  - [quote] — [url]
**Monetization**: price point, target gross margin, rough unit economics
**Distribution** (specific channel + CAC estimate): not "content marketing" — name the channel
**Moat** (what compounds): data, workflow lock-in, regulatory, network, proprietary integration
**Why now (2026)**: one of — regulatory shift, capability unlock, cost-curve shift, distribution change
**MVP test** (2 weeks): what to build, what metric proves/disproves demand
**Kill criteria** (numeric): e.g. "<3 paid pilots in 60 days → kill"
**Expansion** (what if it works): the adjacent market
```

Quality bar before emitting:
- Does each idea pass Paul Graham's organic test (something the user would want, can build, few others see)?
- Is the ICP a named role with a trigger event, not "SMBs" or "developers"?
- Is distribution a specific channel, not a generic category?
- Is the kill criteria numeric and time-bound?

If an idea fails the bar, iterate. Do not emit slop.

### 5. Send via `send_message` (under 4000 chars)

```
*Startup Ideas — ${today}*

*1. [Name]* (executable) — [thesis]
ICP: [role + trigger]
Wedge: [first product]
Why now: [one sentence]
MVP test: [what to build, metric]
Kill: [numeric criteria]

*2. [Name]* (ambitious) — [thesis]
ICP: [role + trigger]
Wedge: [first product]
Why now: [one sentence]
MVP test: [what to build, metric]
Kill: [numeric criteria]
```

Keep the notification tight — full memos go to the article file.

### 6. Save to `~/.hermes/articles/startup-idea-DATE.md`

Write the full 2-memo output (all fields from step 4), plus a header:

```
# Startup Ideas — YYYY-MM-DD

## Idea 1: [Name] (executable)
[all fields]

## Idea 2: [Name] (ambitious)
[all fields]

## Meta
- **Sources cited:** [count of permalinks]
- **Notification sent:** yes
```

## Constraints

- Never emit an idea without 2+ cited pain permalinks.
- Never emit a tarpit-category idea (step 3) without an explicit earned-secret justification.
- Never repeat an idea proposed in the last 14 days of `~/.hermes/articles/startup-idea-*.md`.
- Notification stays under 4000 chars; full memos live in the article file.

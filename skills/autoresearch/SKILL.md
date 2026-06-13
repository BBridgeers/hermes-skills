---
name: autoresearch
description: Evolve a Hermes skill by generating variations, evaluating them, and patching the best version
tags: [meta, dev]
---

# Autoresearch — Skill Variation, Evaluation, and Evolution

> Adapted from Aeon's autoresearch. Replaces `./notify` with Slack `send_message`, git/PR flow with direct `skill_manage(action='patch')`, and Aeon-specific paths with `~/.hermes/` equivalents. Core variation generation, weighted scoring, and quality gates preserved.

## Purpose

Improve an existing Hermes skill by researching better approaches, generating 4 distinct variations, scoring them against a weighted rubric, and applying the winning version via `skill_manage(action='patch')`.

## Trigger

User says: "Run autoresearch on [skill-name]" or "Evolve [skill-name]"

The skill being targeted must exist at `~/.hermes/skills/{skill-name}/SKILL.md`.

## Steps

### 1. Load the target skill

Read `~/.hermes/skills/{skill-name}/SKILL.md`. If the file doesn't exist, abort and notify:

```
send_message "autoresearch: skill '{skill-name}' not found at ~/.hermes/skills/{skill-name}/SKILL.md"
```

Parse the skill's:
- **Purpose**: what it does
- **Data sources**: APIs, URLs, commands it calls
- **Output format**: what it produces (digest, notification, file)
- **Dependencies**: env vars, tools, other files it reads
- **Current quality signals**: has it been failing? Zero output? Low signal?

Save the original content — you'll need it for diff comparison later.

### 2. Research improvements

Search for better approaches to what this skill does:

- **Alternative or complementary APIs/data sources** — are there newer, more reliable endpoints?
- **Best practices for the domain** — e.g., crypto analysis, RSS aggregation, security scanning
- **Common failure modes** — what breaks in skills of this type? Rate limits? Empty data?
- **Output formats that are more actionable** — tighter prose, better formatting, clearer signals

Also review:
- `~/.hermes/logs/agent.log` and `~/.hermes/logs/errors.log` — has this skill produced useful output? Failed recently?
- `~/.hermes/state/` — any skill-health or success-rate data for this skill?

### 3. Generate 4 variations

Create 4 distinct improved versions of the SKILL.md, each with a different thesis:

**Variation A — Better inputs**: Improve data sources. Add alternative/complementary APIs, better search queries, more reliable endpoints. Fix any broken or deprecated sources found in step 2.

**Variation B — Sharper output**: Improve the output format and content quality. Make notifications more actionable, digests more substantive, analysis more insightful. Reduce noise, improve signal.

**Variation C — More robust**: Improve reliability and edge-case handling. Add fallback logic for when APIs fail, better deduplication, graceful handling of empty data, clearer error messages.

**Variation D — Rethink**: Take a fundamentally different approach to achieving the same goal. Different methodology, different angle, or a creative combination of techniques the original didn't consider.

Each variation must:
- Preserve the original frontmatter format (name, description, tags) — no new YAML keys
- Follow Hermes skill conventions (paths under `~/.hermes/`, `send_message` for notifications, `read_file`/`write_file`/`patch`/`terminal` for edits)
- Be a complete, ready-to-run SKILL.md — no placeholders, no TODOs
- Include a one-line HTML comment at the very top of the body: `<!-- autoresearch: variation X — thesis description -->`
- Be structurally similar to the original but meaningfully different in content/approach

### 4. Evaluate and score

Score each variation on a 1-5 scale across these criteria:

| Criterion | What to evaluate |
|-----------|-----------------|
| **Clarity** | Will the agent execute this correctly? Are instructions unambiguous? |
| **Data quality** | Are sources reliable, diverse, and likely to return useful data? |
| **Output value** | Is the output actionable and worth reading? Low noise? |
| **Robustness** | Does it handle failures, empty data, and edge cases gracefully? |
| **Conventions** | Does it follow Hermes patterns? (paths, tools, logging, notifications) |
| **Improvement** | How much better is this than the original? |

Write out your scoring with brief justification for each score. Calculate a weighted total:

| Criterion | Weight |
|-----------|--------|
| Improvement | 3x |
| Output value | 2x |
| Clarity | 1.5x |
| Data quality | 1.5x |
| Robustness | 1.5x |
| Conventions | 1x |

Maximum weighted score: 52.5 (5 × sum of weights = 5 × 10.5).

### 5. Select and apply the winner

Pick the highest-scoring variation. If scores are very close (within 2 points), prefer the variation that makes the biggest single improvement rather than small incremental changes.

**Before applying**: Diff the winner against the original. If the winning variation is a downgrade on any dimension, reconsider — evolution must not regress.

Apply the winner using `skill_manage(action='patch', name='{skill-name}')`:

```
skill_manage(action='patch', name='{skill-name}', old_string='<original SKILL.md content>', new_string='<winning SKILL.md content>')
```

Alternatively, use `write_file` to replace `~/.hermes/skills/{skill-name}/SKILL.md` directly, then verify with `skill_view(name='{skill-name}')`.

### 6. Log and notify

Append to `~/.hermes/logs/autoresearch.log` (create with `mkdir -p ~/.hermes/logs && touch ~/.hermes/logs/autoresearch.log` if needed):

```
autoresearch: YYYY-MM-DD HH:MM
  Target: {skill-name}
  Winner: Variation [X] ({weighted_score}/52.5)
  Thesis: [description]
  Key changes: [1-2 sentence summary]
  Runners-up: [brief scores for other 3 variations]
```

Send a single message via `send_message` to Slack:

```
Autoresearch — {skill-name}
Winner: Variation [X] — [thesis]
Score: {weighted_score}/52.5
Key changes: [1-2 sentence summary]
Runners-up:
  Variation [Y]: {score} — [thesis]
  Variation [Z]: {score} — [thesis]
  Variation [W]: {score} — [thesis]
```

If `send_message` is unavailable, log `AUTORESEARCH_NOTIFY_FAILED` and continue — the log file is the authoritative record.

## Quality gates

- **Never downgrade a working skill.** If all variations score lower than or equal to the original on "Improvement", skip the update and notify: `send_message "autoresearch: no improvement found for {skill-name} — all variations scored at baseline."`
- **Never change the skill's core purpose** — evolution, not replacement.
- **Never add new YAML frontmatter keys** (tags, name, description only).
- **Never add env vars that aren't already available** in the Hermes environment.
- **Never evolve the autoresearch skill with autoresearch** — no circular evolution.

## Constraints

- Preserve the skill's purpose and identity — make it better, not different.
- One evolution per run. Don't evolve multiple skills at once.
- Log every run — even no-op runs where no improvement was found.
- If a variation introduces complexity without clear benefit, it should score lower on Clarity and Robustness.
- Research thoroughly before generating variations — uninformed variations are wasted work.

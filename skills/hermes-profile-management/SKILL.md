---
name: hermes-profile-management
description: Creating, cloning, auditing, and arming Hermes profiles with appropriate skills. Covers circular-symlink pitfalls, flat skill name format, profile→swarm pod mapping, and armory auditing methodology.
version: 3
triggered-by: Profile creation session (v1) + batch model migration (v2) + swarm profile hardening audit with compound skill resolution (v3)
last-updated: 2026-06-04
---

# Hermes Profile Management

Create, clone, audit, and arm Hermes profiles with the right skills for their domain.

## Trigger

Use when:
- Creating new profiles via `hermes profile create`
- Auditing profile skill assignments against the full skill silo
- Mapping swarm agents to WebUI profiles
- A profile creation fails with cryptic errors

## Profile Creation

```bash
hermes profile create <name> --clone-from default
cp /root/.hermes/.env /root/.hermes/profiles/<name>/.env
mkdir -p /root/workspace/<workspace_name>
```

### Circular Symlink Pitfall

**Symptom:** `hermes profile create --clone-from default` fails with:
```
shutil.Error: [Errno 40] Too many levels of symbolic links
```

**Root Cause:** A skill in `~/.hermes/skills/` has a self-referencing symlink (e.g., `domain-skills/domain-skills -> /root/browser-harness/domain-skills`). `shutil.copytree` follows it into an infinite loop.

**Fix:**
```bash
# Find self-referencing symlinks
find /root/.hermes/skills/ -maxdepth 5 -type l -ls 2>/dev/null
find /root/browser-harness/ -maxdepth 3 -type l -ls 2>/dev/null

# Remove the circular ones
rm /root/browser-harness/domain-skills/domain-skills
rm /root/browser-harness/interaction-skills/interaction-skills

# If the profile was partially created, nuke and retry
rm -rf /root/.hermes/profiles/<name>
hermes profile create <name> --clone-from default
```

## Skill Name Format — CRITICAL

The 333-skill silo uses **FLAT** names. Categories are metadata only — NOT part of the name.

```
CORRECT:                              WRONG:
  tailscale-mesh-networking            devops/tailscale-mesh-networking
  arxiv                                research/arxiv
  github-pr-workflow                   github/github-pr-workflow
  code-editing-discipline              software-development/code-editing-discipline
  google-workspace                     productivity/google-workspace
  design-everyday-things               wondelai_skills/design-everyday-things
```

**How to verify:** Run `hermes skills list` or dump the raw skill names — they never contain slashes representing categories. The `skills_list()` tool output has a `category` field for metadata but the `name` field is flat.

**Exception:** Skills with literal slashes in their name from git repos (e.g., `devops/hermes-dashboard-auth-fallback`). These are rare — check `skills_list()` output to confirm.

## WebUI Skill Count Discrepancy

The WebUI Profiles panel counts every `SKILL.md` file ON DISK recursively. This inflates counts:

```
333 = logical skills (skills_list() — what can be loaded)
436 = raw SKILL.md files on disk (what WebUI counts)
103 = extra SKILL.md in subdirectories (templates, references, nested skills)
```

**Do not** try to "fix" this discrepancy. It's a counting artifact. The actual arsenal is what's documented in each profile's SOUL.md.

## Profile ↔ Swarm Pod Mapping

A WebUI profile is a **command center** for a pod of swarm agents — NOT a 1:1 mapping.

### Cross-Cutting Agents (shared across multiple profiles)

These agents serve any profile that needs their function:

| Agent | Profiles That Need It |
|---|---|
| core-researcher | All profiles that do research |
| core-builder | All profiles that ship code |
| core-reviewer | All profiles producing reviewable output |
| core-qa | All profiles that ship tested code |
| docs-scribe | All profiles producing documentation |
| km-agent | All profiles managing knowledge |
| security-gatekeeper | All profiles touching code/data |
| root-cause-analyst | All profiles debugging issues |
| spec-architect | All build-heavy profiles |
| task-REDACTED | ALL profiles |

### Methodology

1. List all 60 swarm agents from `/root/hermes-workspace/swarm.yaml`
2. For each profile, identify DEDICATED agents (purpose-built for that domain)
3. Cross-reference SHARED agents by function (which profiles need research? building? review?)
4. Document both in the profile's SOUL.md Swarm Pod section

## Armory Auditing

When user says "arm to the teeth" or "audit skills":

1. Get full skill list: `skills_list()` → extract all names
2. For each profile, determine which skills are domain-appropriate
3. Use flat names (see Skill Name Format above)
4. Validate every assignment against the skill silo — ZERO invalid entries
5. Write the profile's config.yaml and IDENTITY.md

### Bulk Profile Maximization Workflow

When auditing ALL profiles to maximize skill assignments (user says "max out skills", "every agent needs every relevant skill", "these numbers are crap"):

**Step 1 — Build full loadable skill catalog (~359 skills from compound packages)**
```bash
python3 << 'PYEOF'
import os
skills_dir = os.path.expanduser('~/.hermes/skills')
all_loadable = set()
for item in os.listdir(skills_dir):
    item_path = os.path.join(skills_dir, item)
    if not os.path.isdir(item_path) or item.startswith('.'):
        continue
    if os.path.exists(os.path.join(item_path, 'SKILL.md')):
        all_loadable.add(item)
    for child in os.listdir(item_path):
        child_path = os.path.join(item_path, child)
        if os.path.isdir(child_path) and os.path.exists(os.path.join(child_path, 'SKILL.md')):
            skip = child in ('src','tests','demo','docs','examples','environments','evals','reference','terminal-demos','plugins','prisms')
            if not skip:
                all_loadable.add(f"{item}/{child}")
print(f"Loadable skills: {len(all_loadable)}")
PYEOF
```

**Step 2 — Define role-appropriate skill domains per profile**
Every profile gets universal skills + domain-specific skills.
Universal base: `deep-research, self-improve, skill-creator, goal-tracker, weekly-review, idea-capture, memory-merger, search-skill, skill-factory, hermes-skill-factory`

**Step 3 — Write config.yaml with maximized skills**
Validate every skill against the loadable catalog. Use Python script to read existing config, merge new skills, write back.

**Step 4 — Verify counts**
```bash
for p in /root/.hermes/profiles/*/config.yaml; do
  name=$(basename $(dirname $p))
  count=$(grep -c '^- ' $p 2>/dev/null || echo 0)
  echo "$name → $count skills"
done
```

**PITFALL — IDENTITY.md is required by workspace swarm**: The Workspace Swarm reads `profile/memory/IDENTITY.md` for role, mission, and capabilities. After updating config.yaml, also write IDENTITY.md:

```bash
cat > /root/.hermes/profiles/<name>/memory/IDENTITY.md << 'EOF'
# IDENTITY.md — <name>
- Name: <name>
- Worker ID: <name>
- Role: <domain-specific role description>
- Specialty: <core competencies>
- Mission: <one-line mission statement>
- Model: <model>
- Skills: <count> skills across <domains>
EOF
```

### Anti-Patterns

- **Conservative curation** — The user wants profiles maximally loaded. If a skill is even marginally useful for the domain, include it.
- **Category-prefixed names** — Always validate against `skills_list()` output.
- **Hoarding shared agents** — `core-researcher` is NOT exclusive to `deep-researcher` profile. It belongs everywhere research happens.
- **Skipping validation** — Every skill must exist in the loadable catalog. Invalid names are operational failures.
- **Weak skill counts** — A profile with 4-7 skills out of 359 available (2% coverage) is under-armed. Target 30-60 relevant skills per profile.

## System Prompt Gap in Profile Configs

Every profile `config.yaml` has a `system_prompt` field. If this is empty or missing, the worker/agent runs with **no identity, no mission, no constraints** — it defaults to generic chatbot behavior and will not follow swarm protocols or domain-specific directives.

**Audit all profiles for empty system prompts:**
```bash
python3 -c "
import yaml, os
for p in sorted(os.listdir(os.path.expanduser('~/.hermes/profiles'))):
    cfg = os.path.expanduser(f'~/.hermes/profiles/{p}/config.yaml')
    if not os.path.exists(cfg): continue
    d = yaml.safe_load(open(cfg))
    sp = d.get('system_prompt','')
    print(f'{p}: {\"✅\" if sp and sp.strip() else \"❌ EMPTY\"} ({len(sp)} chars)')
"
```

**To write system prompts for swarm worker profiles**, use the ROLE_PRESETS from `swarm2-screen.tsx` as the template. Each preset has a `systemPrompt` and `mission` field that should populate the profile's `system_prompt` and `mission` config fields.

**Pitfall:** Swarm workers created through the Workspace UI get `systemPrompt` from ROLE_PRESETS displayed in the UI, but this field is **silently dropped** by the backend Zod schema (see `hermes-workspace-swarm` skill, Pitfall #5). The system prompt must be persisted either:
1. In the profile's `config.yaml` `system_prompt` field (recommended)
2. As a `<worker-id>-core` skill referenced in the worker's `skills` array

## Cost-Optimized Model Selection for Swarm Profiles

Not every agent needs a frontier model. Match the model tier to the task complexity:

| Agent Role | Model Tier | Example (OpenRouter) | Cost (in/out per 1M) |
|---|---|---|---|
| Orchestrator, Researcher, Strategist, KM | Top reasoning | `qwen3.7-max` | $1.25/$3.75 |
| Builder (coding) | Best coding per dollar | `deepseek/deepseek-v4-pro` | $0.43/$0.87 |
| Reviewer (code review) | Top reasoning | `qwen3.7-max` | $1.25/$3.75 |
| QA (test gen) | Cheap coder | `qwen/qwen3-coder-next` | $0.11/$0.80 |
| Ops-Watch, Maintainer | Budget fast | `qwen/qwen3.6-flash` | $0.19/$1.12 |
| Inbox-Triage (classification) | Ultra-cheap | `deepseek/deepseek-v4-flash` | $0.10/$0.20 |

**Principle:** Qwen3.7-Max at $1.25/$3.75 delivers ~90-95% of GPT-5.5's ($5/$30) quality at ~10-15% of the cost. Only consider GPT-5.5 for single high-stakes decisions where a 5% reasoning improvement converts to real financial outcome. For 24/7 parallel swarm workers, Qwen3.7-Max + DeepSeek V4 Pro is the right economics.

**Never put a non-existent model in swarm.yaml.** Always verify model IDs against `https://openrouter.ai/api/v1/models` before setting them. GPT-5.5 exists but was initially assumed non-existent in this project — verify, don't assume.

## System Prompts Are Mandatory

Every profile MUST have a non-empty `system_prompt` in its `config.yaml`. A profile with `system_prompt: ''` starts with no personality, no mission, no constraints — a blank slate that behaves unpredictably.

**Minimum viable system prompt** covers:
1. Who this agent is (identity)
2. What it does (role specialization)
3. Its rules/constraints (4-6 hard rules)
4. What it excels at (explicit strengths)

Empty system prompts were the #1 issue found in the 2026-06-04 audit of 20 profiles. All 10 that were missing got 600-830 char prompts immediately.

## Compound Skill Reference Resolution

The skill silo has compound packages (`devops/`, `software-development/`, `research/`) that contain 10-50 sub-skills each. When assigning skills to profiles:

- **Profile config `skills:` list uses PARENT package names** — e.g., `devops`, `software-development`, `research`, NOT individual sub-skill names like `hermes-heartbeat` or `workspace-dispatch`
- Sub-skills are resolved at runtime when the parent is loaded
- The only valid skill names are top-level directory names under `~/.hermes/skills/`
- Validate with: `ls ~/.hermes/skills/` — if it's not a top-level dir, it's not a direct skill name

**Wrong:** `skills: [hermes-heartbeat, workspace-dispatch, writing-plans]`
**Right:** `skills: [devops, software-development, deep-research]`

> **Full model pricing reference:** see `references/openrouter-model-pricing-2026-06.md` for the complete tier-by-tier pricing table sourced live from OpenRouter, including free-tier models and the recommended cost-optimized swarm configuration.

## Swarm Profile Hardening — Full Audit Protocol

When auditing and hardening swarm profiles, four layers must be synchronized:

1. **`~/.hermes/profiles/<name>/config.yaml`** — model, skills list, provider, fallback chain
2. **`~/.hermes/profiles/<name>/memory/IDENTITY.md`** — name, role, specialty, mission, skills summary, capabilities, model
3. **`/root/hermes-workspace/src/screens/swarm2/swarm2-screen.tsx`** — ROLE_PRESETS array (frontend dropdown defaults)
4. **`/root/hermes-workspace/swarm.yaml`** — worker definitions (id, name, role, model, profile, skills, mission, specialty)

All four must agree on model assignments and skill references. A mismatch between any two causes the UI to show one thing while the runtime does another.

### Compound Skill Resolution

The global skills directory (`~/.hermes/skills/`) has two types of packages:

| Type | Structure | Skill Name Format | Example |
|---|---|---|---|
| **Standalone** | `skill-name/SKILL.md` | `skill-name` (flat) | `deep-research`, `job-search` |
| **Compound** | `parent-dir/sub-skill/SKILL.md` | `parent-dir:sub-skill` (qualified) or just `parent-dir` (umbrella) | `devops:hermes-heartbeat`, `research:arxiv` |

When assigning skills to a profile config's `skills:` list, use the **parent directory name** (umbrella) to load the entire family. The Hermes skill loader resolves sub-skills via `skill_view(name='devops:hermes-heartbeat')`. If you reference a sub-skill name that doesn't exist as a top-level directory, the profile will fail to load it.

**Pitfall:** Writing `hermes-heartbeat` in a profile's skills list when the actual path is `devops/hermes-heartbeat/SKILL.md`. The flat name doesn't exist at the top level. Use `devops` to load the whole devops umbrella, which includes hermes-heartbeat and ~50 other sub-skills.

**Validation step:** After assigning skills to a profile, verify every name against `os.listdir('~/.hermes/skills/')`. Sub-skills inside compound packages will NOT appear as top-level directories. If a referenced name is missing from the directory listing, replace it with the parent compound package name.

### Model Selection Per Role — Cost-Optimized

Default to Qwen3.7-Max ($1.25/$3.75 per 1M tokens) for reasoning-heavy roles. Reserve cheaper models for routine tasks:

| Role Category | Model | Cost (in/out per 1M) | Rationale |
|---|---|---|---|
| Reasoning (orch, review, research, strategy, KM) | `qwen3.7-max` | $1.25/$3.75 | Best reasoning per dollar |
| Coding (builder) | `deepseek/deepseek-v4-pro` | $0.43/$0.87 | Near-frontier coding at 1/10th cost |
| Code QA | `qwen/qwen3-coder-next` | $0.11/$0.80 | Test gen, cheap |
| Monitoring/Infra | `qwen/qwen3.6-flash` | $0.19/$1.12 | Simple tasks, ultra-cheap |
| Classification | `deepseek/deepseek-v4-flash` | $0.10/$0.20 | Triage, ultra-cheap |

**User preference:** Do NOT use GPT-5.5 for swarm workers. The cost/quality ratio is wrong for parallel agent work. Qwen3.7-Max + DeepSeek V4 Pro covers ~95% of GPT-5.5 quality at ~10-15% of cost.

### IDENTITY.md Generation

Every profile must have `~/.hermes/profiles/<name>/memory/IDENTITY.md`. The workspace swarm reads this file to construct the worker's self-concept. The template:

```markdown
# IDENTITY.md — {Name}

- Name: {Name}
- Worker ID: {profile-name}
- Role: {Role}
- Specialty: {specialty}
- Mission: {mission}
- Skills: {comma-separated skills list}
- Capabilities: {comma-separated capability tags}
- Model: {model-name}

## Job description
{Name} is the {Role} lane. {mission}

The worker ID is a stable machine identifier only; user-facing surfaces should prefer `Name — Role`.
```

The `syncSwarmProfileIdentity()` function in `workspace/src/server/swarm-profile-config.ts` renders this automatically from the swarm roster. But for profiles outside the swarm, or when bootstrapping new ones, write it manually.

### Audit Checklist

When hardening swarm profiles, run this checklist:

1. **Profile config exists** — `~/.hermes/profiles/<name>/config.yaml` must have `model.default`, `model.provider`, `skills` list, and `system_prompt`
2. **IDENTITY.md exists** — `~/.hermes/profiles/<name>/memory/IDENTITY.md` with name, role, specialty, mission, skills, model
3. **Skills validated** — Every name in `skills:` list must exist as a top-level directory under `~/.hermes/skills/`. Compound sub-skills use parent name.
4. **Model matches swarm.yaml** — `config.yaml model.default` must match `swarm.yaml` worker `model` field
5. **ROLE_PRESETS aligned** — `swarm2-screen.tsx` ROLE_PRESETS skills and models must match profile configs
6. **Fallback chain configured** — `fallback_providers` in config.yaml with Ollama/local models as safety net
7. **No GPT-5.5 defaults** — All default models should be cost-optimized (Qwen, DeepSeek, etc.), not GPT-5.5
- `skill-creator` — Creating and maintaining individual skills

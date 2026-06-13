---
name: hermes-profile-management
description: Creating, cloning, auditing, and arming Hermes profiles with appropriate skills. Covers circular-symlink pitfalls, flat skill name format, profile→swarm pod mapping, and armory auditing methodology.
version: 2
triggered-by: Profile creation session (v1) + batch model migration session (v2 — DeepSeek→Qwen across 10 profiles, fallback chain config)
last-updated: 2026-05-30
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

1. Get full skill list: `skills_list()` → extract all 333 names
2. For each profile, determine which skills are domain-appropriate
3. Use flat names (see Skill Name Format above)
4. Validate every assignment against the skill silo — ZERO invalid entries
5. Write the profile's SOUL.md with the full skill list

### Anti-Patterns

- **Conservative curation** — The user wants profiles maximally loaded. If a skill is even marginally useful for the domain, include it.
- **Category-prefixed names** — Always validate against `skills_list()` output.
- **Hoarding shared agents** — `core-researcher` is NOT exclusive to `deep-researcher` profile. It belongs everywhere research happens.
- **Skipping validation** — Every skill in a SOUL.md must exist in the silo. Invalid names are operational failures.

## Batch Model Migration — All Profiles

When swapping the default model across all profiles (e.g., DeepSeek → Qwen), use `hermes -p <name> config set`:

```bash
# 1. Set primary model + provider on main config
hermes config set model.default qwen/qwen3.7-max
hermes config set model.provider openrouter

# 2. Loop all profiles
for p in code-review deep-researcher detoxxx fallen hermes-ops \
         housing-search job-attainer resonate vehicle-analyzer velocity-labs; do
  hermes -p $p config set model.default qwen/qwen3.7-max
  hermes -p $p config set model.provider openrouter
done

# 3. Update delegation model too
hermes config set delegation.model qwen/qwen3.7-max
hermes config set delegation.provider openrouter

# 4. Verify
for p in /root/.hermes/profiles/*/config.yaml; do
  name=$(basename $(dirname $p))
  def=$(grep -A2 '^model:' $p | grep 'default:' | tr -d ' ')
  echo "$name → $def"
done
```

**Pitfall:** `hermes config set` on profiles may place model settings under existing `model:` blocks deep in the config. Always verify with `grep -A2 '^model:'` after changes.

**Pitfall:** `grep 'default:'` matches the FIRST occurrence — which may be from auxiliary sections (compression, etc.), not the model block. Use `grep -A2 '^model:'` to target the right section.

## Fallback Provider Chain

For multi-tier fallback with different providers:

```yaml
# In config.yaml or profile config.yaml:
fallback_providers:
# Tier 1: Same model, different provider (redundancy)
- label: qwen3.7-max-zen
  model: qwen3.7-max
  provider: opencode_zen
# Tier 2: Next-best model on preferred cheap provider  
- label: glm-5.1-ollama-cloud
  model: glm-5.1
  provider: ollama-cloud
# Tier 3+: Free safety net
- label: nemotron-3-super-120b-free
  model: nvidia/nemotron-3-super-120b-a12b:free
  provider: openrouter
```

**Pattern:** Primary model via fastest/cheapest route → same model via backup route → different model on cheap provider → free tier catch-all.

**Provider keys for fallback:**
- `openrouter` — OpenRouter
- `opencode_zen` — OpenCode Zen (requires `OPENCODE_ZEN_API_KEY` in .env)
- `ollama-cloud` — Ollama Cloud (requires `OLLAMA_API_KEY` in .env)
- `deepseek`, `anthropic`, `openai`, `google` — native providers

**Verification:**
```bash
grep -A30 '^fallback_providers:' /root/.hermes/config.yaml
systemctl --user restart hermes-gateway
```

## Related Skills

- `hermes-agent` — Core agent CLI and configuration
- `workspace-swarm` — Swarm agent architecture and swarm.yaml schema
- `hermes-dojo` — Continuous self-improvement
- `skill-creator` — Creating and maintaining individual skills

## Skill Parity Across Configs

The skill ecosystem has three layers: Global (`~/.hermes/skills/`), Profile (`~/.hermes/profiles/<name>/skills/`), Worker core (embedded in worker profile dirs). Worker core skills are NOT SKILL.md files — they're system prompts defined in ROLE_PRESETS.

**Audit command:**
```bash
diff <(find ~/.hermes/skills -maxdepth 2 -name SKILL.md | sed 's|/SKILL\.md||;s|.*/skills/||' | sort) \
     <(find ~/.hermes/profiles -maxdepth 3 -name SKILL.md | sed 's|/SKILL\.md||;s|.*/skills/||' | sort -u)
```

## Workspace Directory Map

```
/root/workspace/
├── detoxxx/              — DETOXXX V2 protocol docs
├── vehicle_analyzer/     — veracar.co
├── car_buyer/            — Vehicle sourcing workflow
├── deep_research/        — General research
├── housing_search/       — Rental hunt
├── job_search/           — Job hunt
├── velocity_labs/        — AI agency
├── resonate/             — Bio-hacking wearables
├── hermes_ops/           — Self-improvement
├── code_review/          — PR/security audits
└── the_fall_of_the_fallen/ — Investigation project
```

## Consolidated Skills

This skill absorbs: `profile-orchestration`.

# AV1 Workforce Full Deployment Recipe

Deploying the 60-agent AV1 swarm workforce from the identity repo to a live Hermes Workspace.

## Prerequisites

- Identity repo at `/root/hermes-av1-workforce/` with:
  - `hermes-agents/` — 60 markdown profiles
  - `skills/` — 60 pre-built `<id>-core.md` skill files
  - `swarm-agents.csv` — canonical CSV
  - `scripts/generate_swarm.py` — build script
- Hermes Workspace running on bare-metal at `/root/hermes-workspace/`
- Python 3 with `pyyaml` installed

## Step 1: Backup Existing swarm.yaml

```bash
cp /root/hermes-workspace/swarm.yaml \
   "/root/hermes-workspace/swarm.yaml.bak-$(date +%Y%m%d-%H%M)"
```

## Step 2: Run the Generator

```bash
cd /root/hermes-av1-workforce
python3 scripts/generate_swarm.py
```

This does two things:
- Copies all 60 `<id>-core.md` skill files to `~/.hermes/skills/`
- Generates `/root/hermes-workspace/swarm.yaml` with 60 workers from `swarm-agents.csv`

## Step 3: Create Profile Directories

Each agent needs `~/.hermes/profiles/<profile>/` with:
- `config.yaml` — model, system_prompt, skills
- `SOUL.md` — identity doc (markdown profile minus CSI)
- `skills/` directory (empty or with symlinks)

```python
import csv, os, yaml, re

HERMES_HOME = os.path.expanduser("~/.hermes")
PROFILES_DIR = os.path.join(HERMES_HOME, "profiles")
AGENTS_DIR = "/root/hermes-av1-workforce/hermes-agents"
CSV_PATH = "/root/hermes-av1-workforce/swarm-agents.csv"
BIN_DIR = os.path.expanduser("~/.local/bin")

MODEL_MAP = {
    "gpt-5.5-pro": ("openrouter", "openai/gpt-5.5-pro"),
    "gpt-5.5": ("openrouter", "openai/gpt-5.5"),
    "gpt-5.4-pro": ("openrouter", "openai/gpt-5.4-pro"),
    "gpt-5.4": ("openrouter", "openai/gpt-5.4"),
    "gpt-5.4-mini": ("openrouter", "openai/gpt-5.4-mini"),
    "gpt-5.3-codex": ("openrouter", "openai/gpt-5.3-codex"),
    "gpt-5.2-codex": ("openrouter", "openai/gpt-5.2-codex"),
    "gpt-5.1-codex-max": ("openrouter", "openai/gpt-5.1-codex-max"),
    "claude-opus-4-7": ("openrouter", "anthropic/claude-opus-4-7"),
    "claude-opus-4-6": ("openrouter", "anthropic/claude-opus-4-6"),
    "claude-sonnet-4-6": ("openrouter", "anthropic/claude-sonnet-4-6"),
    "claude-sonnet-4-5": ("openrouter", "anthropic/claude-sonnet-4-5"),
    "claude-haiku-4-5": ("openrouter", "anthropic/claude-haiku-4-5"),
    "gemini-3.1-pro": ("google", "gemini-3.1-pro-preview"),
    "gemini-3-flash": ("google", "gemini-3-flash-preview"),
    "glm-5.1": ("ollama-cloud", "glm-5.1"),
    "kimi-k2.6": ("ollama-cloud", "kimi-k2.6"),
}

def find_md_profile(agent_id):
    for root, dirs, files in os.walk(AGENTS_DIR):
        for f in files:
            if f.endswith(".md"):
                stem = os.path.splitext(f)[0]
                if stem.replace(" ", "-").lower() == agent_id.lower():
                    return os.path.join(root, f)
    return None

def extract_csi(md_path):
    """Extract Core System Instructions from markdown profile."""
    if not md_path or not os.path.exists(md_path):
        return "You are a Hermes Swarm agent. Execute your standing mission."
    with open(md_path) as f:
        content = f.read()
    match = re.search(r'## Core System Instructions\s*\n(.*)', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content

# Load CSV
with open(CSV_PATH, newline="") as f:
    agents = list(csv.DictReader(f))

for agent in agents:
    agent_id = agent["id"]
    profile_name = agent["profile"]
    model_name = agent["model"]
    wrapper = agent["wrapper"]
    
    profile_dir = os.path.join(PROFILES_DIR, profile_name)
    md_path = find_md_profile(agent_id)
    csi = extract_csi(md_path)
    provider, model_id = MODEL_MAP.get(model_name, ("openrouter", f"openai/{model_name}"))
    
    config = {
        "model": {"default": model_id, "provider": provider},
        "system_prompt": csi,
        "skills": agent["skills"].split("|"),
        "tools": agent["tools"].split("|"),
    }
    
    os.makedirs(profile_dir, exist_ok=True)
    
    # config.yaml
    with open(os.path.join(profile_dir, "config.yaml"), "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=200)
    
    # SOUL.md (everything except CSI)
    if md_path and os.path.exists(md_path):
        with open(md_path) as f:
            full_content = f.read()
        csi_start = re.search(r'## Core System Instructions', full_content)
        if csi_start:
            soul = full_content[:csi_start.start()].strip()
        else:
            soul = full_content
        with open(os.path.join(profile_dir, "SOUL.md"), "w") as f:
            f.write(soul)
    else:
        with open(os.path.join(profile_dir, "SOUL.md"), "w") as f:
            f.write(f"# {agent['name']}\n\nNo profile found.\n")
    
    # skills directory
    os.makedirs(os.path.join(profile_dir, "skills"), exist_ok=True)
    
    # Wrapper script
    os.makedirs(BIN_DIR, exist_ok=True)
    wrapper_name = wrapper.split(":")[0]
    mode = wrapper.split(":")[1] if ":" in wrapper else "task"
    wrapper_path = os.path.join(BIN_DIR, wrapper_name)
    with open(wrapper_path, "w") as f:
        f.write(f"#!/bin/bash\nexport HERMES_PROFILE=\"{profile_name}\"\nexec hermes agent run --profile \"{profile_name}\" --mode \"{mode}\" \"$@\"\n")
    os.chmod(wrapper_path, 0o755)
```

## Step 4: Restart Workspace

```bash
systemctl --user restart hermes-workspace
```

## Step 5: Verify

```bash
# Count workers in swarm.yaml
python3 -c "import yaml; d=yaml.safe_load(open('/root/hermes-workspace/swarm.yaml')); print(f'Workers: {len(d[\"workers\"])}')"

# Count profiles
ls ~/.hermes/profiles/ | wc -l

# Count core skills
ls ~/.hermes/skills/*-core.md | wc -l

# Count wrappers
ls ~/.local/bin/ | wc -l
```

Expected: 60 workers, 60+ profiles, 60 core skills, 60 wrappers.

## Pod Distribution

| Pod | Count | Example Agents |
|-----|-------|----------------|
| core-command | 4 | swarm-orchestrator, executive-chief-of-staff, workspace-steward, task-REDACTED |
| technical-core | 11 | core-builder, core-reviewer, core-qa, core-researcher, km-agent, strategist, spec-architect, test-hardener, release-marshall, inbox-triage, core-maintainer |
| knowledge-strategy | 12 | root-cause-analyst, telemetry-curator, runbook-librarian, security-gatekeeper, docs-scribe, study-scope-coach, research-planner, method-matchmaker, deep-analyzer, critique-agent, fact-checker, synth-agent |
| startup-ideation | 14 | business-alignment, content-builder, ideation-partner, idea-intake, opportunity-mapper, idea-prioritizer, assumption-logger, market-reality-check, competitor-landscape, problem-solution-fit, startup-experiment-designer, mvp-scope-cutter, launch-plan-builder, founder-accountability |
| communications | 5 | comms-triage, draft-reply, followup-nudge, message-to-task, process-automation |
| vehicle-pod | 2 | veracar-operator-maintainer, vehicle-sourcing |
| career-pod | 6 | role-match, resume-tailor, application-pack, interview-prep, offer-negotiation, job-track |
| housing-pod | 6 | housing-sourcing, landlord-fit, rental-packet, housing-outreach, screening-coach, housing-coordinator |

## Model Assignment Strategy

| Agent Class | Preferred Model | Why |
|-------------|----------------|-----|
| Orchestrator / Strategy | `gpt-5.5-pro`, `claude-opus-4-7` | Deep reasoning, cross-domain coordination |
| Builder / Code | `gpt-5.3-codex`, `gpt-5.2-codex` | Code generation specialists |
| Reviewer / Critique | `claude-sonnet-4-6`, `claude-opus-4-7` | Rigor, contradiction spotting, precision |
| Research / Analysis | `claude-opus-4-6`, `gpt-5.5` | Deep synthesis, evidence evaluation |
| Fast / High-Volume | `claude-haiku-4-5`, `gpt-5.4-mini` | Triage, nudge, tracking — low cost per call |
| Vision / Multimodal | `gemini-3.1-pro` | Image analysis, document parsing |
| Knowledge / Synthesis | `gemini-3.1-pro`, `glm-5.1` | Large context, multi-source consolidation |

## Recovery After Disaster

```bash
git clone https://github.com/BBridgeers/hermes-av1-workforce.git /root/hermes-av1-workforce
cd /root/hermes-av1-workforce
python3 scripts/generate_swarm.py
# Run the profile creation script from Step 3
systemctl --user restart hermes-workspace
```

The identity repo is the ground truth. Lose everything else — regenerate from the repo.

#!/usr/bin/env python3
"""
AV1 Swarm Workforce Generator
Reads swarm-agents.csv → generates swarm.yaml + installs skills.
"""
import csv, os, yaml, shutil, sys

HERMES_HOME = os.path.expanduser("~/.hermes")
SKILLS_DIR = os.path.join(HERMES_HOME, "skills")
WORKSPACE_DIR = "/root/hermes-workspace"
SWARM_YAML = os.path.join(WORKSPACE_DIR, "swarm.yaml")
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "swarm-agents.csv")

def load_agents(csv_path):
    agents = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agents.append(row)
    return agents

def install_skills(repo_skills_dir):
    """Copy skill files from repo to Hermes skills directory."""
    installed = 0
    for fname in os.listdir(repo_skills_dir):
        if fname.endswith(".md") and fname.endswith("-core.md"):
            src = os.path.join(repo_skills_dir, fname)
            dst = os.path.join(SKILLS_DIR, fname)
            shutil.copy2(src, dst)
            installed += 1
            print(f"  SKILL: {fname}")
    return installed

def generate_swarm_yaml(agents, output_path):
    workers = []
    for a in agents:
        workers.append({
            "id": a["id"],
            "name": a["name"],
            "role": a["role"],
            "specialty": a["specialty"],
            "model": a["model"],
            "mission": a["mission"],
            "profile": a["profile"],
            "modes": a["modes"].split("|") if "|" in a["modes"] else [a["modes"]],
            "tools": a["tools"].split("|"),
            "skills": a["skills"].split("|"),
            "capabilities": a["capabilities"].split("|"),
            "preferredTaskTypes": a["preferredTaskTypes"].split("|"),
            "greenlightRequiredFor": a["greenlightRequiredFor"].split("|"),
            "maxConcurrentTasks": int(a["maxConcurrentTasks"]),
            "acceptsBroadcast": a["acceptsBroadcast"].lower() == "true",
            "plugins": [],
            "pluginToolsets": [],
            "mcpServers": [],
            "wrapper": a["wrapper"],
        })
    
    swarm = {"version": 1, "workers": workers}
    
    with open(output_path, "w") as f:
        yaml.dump(swarm, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=200)
    
    return len(workers)

def main():
    print("=== AV1 Swarm Workforce Generator ===\n")
    
    # Load agents
    agents = load_agents(CSV_PATH)
    print(f"Loaded {len(agents)} agents from swarm-agents.csv\n")
    
    # Install skills
    repo_skills = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")
    if os.path.isdir(repo_skills):
        print("Installing skills...")
        installed = install_skills(repo_skills)
        print(f"Installed {installed} skill files\n")
    
    # Generate swarm.yaml
    print(f"Generating {SWARM_YAML}...")
    count = generate_swarm_yaml(agents, SWARM_YAML)
    print(f"Generated swarm.yaml with {count} workers\n")
    
    print("=== DONE ===")
    print(f"Next: restart Hermes Workspace to load agents")
    print(f"  systemctl --user restart hermes-workspace")

if __name__ == "__main__":
    main()

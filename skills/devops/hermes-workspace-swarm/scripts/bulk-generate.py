#!/usr/bin/env python3
"""Bulk-generate swarm.yaml worker entries from a CSV definition file.

CSV columns (header required):
  id,name,role,specialty,model,mission,skills

Skills should be semicolon-delimited: "swarm-worker-core;byte-verified-code-review"

Usage:
  python3 bulk-generate.py workers.csv >> /root/hermes-workspace/swarm.yaml
"""

import csv
import sys
from pathlib import Path

TEMPLATE = """- id: {id}
  name: {name}
  role: {role}
  specialty: {specialty}
  model: {model}
  mission: {mission}
  profile: {id}
  modes: []
  tools: []
  skills:
{skills_yaml}  capabilities: []
  preferredTaskTypes: []
  greenlightRequiredFor: []
  maxConcurrentTasks: 1
  acceptsBroadcast: true
  plugins: []
  pluginToolsets: []
  mcpServers: []
"""


def skills_to_yaml(skills_str: str) -> str:
    if not skills_str.strip():
        return ""
    skills = [s.strip() for s in skills_str.split(";") if s.strip()]
    return "".join(f"  - {s}\n" for s in skills)


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "workers.csv"
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(TEMPLATE.format(
                id=row["id"].strip(),
                name=row["name"].strip(),
                role=row["role"].strip(),
                specialty=row.get("specialty", "").strip(),
                model=row.get("model", "deepseek-v4-pro").strip(),
                mission=row.get("mission", "Awaiting orchestrator dispatch.").strip(),
                skills_yaml=skills_to_yaml(row.get("skills", "")),
            ))


if __name__ == "__main__":
    main()

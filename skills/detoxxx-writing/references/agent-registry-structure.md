# DETOXXX V2 Agent Registry — Structure & Access

## Location

Google Drive folder: `Section (Unsure #) -- Agent Registry & Synergy`
- Folder ID: `1LCDS4FNuTQPuiy49WD3-6RsXrgbCkprW`
- Parent: DETOXXX V2 Handbook Docs (`1QqFi4ouGDoLYaW8AkV4VN_CvMsuVzIEZ`)

## Key Files

| File | Size | Format | Notes |
|---|---|---|---|
| `MASTER_V2_REGISTRY_COMBINED.csv` | 28 KB | Markdown with embedded CSV tables | Primary reference — all 4 tables combined |
| `MASTER_V2_REGISTRY.csv` | 19 KB | CSV | Subset or earlier version |
| `DETOXXX_Agent_Synergy_Map.md` | 170 KB | Markdown | Agent synergy/interaction reference |
| `DETOXXX_Agent_Synergy_Map.docx` | 1,048 KB | DOCX | Original synergy map document |

## Registry Structure

The combined registry (`MASTER_V2_REGISTRY_COMBINED.csv`) is a markdown document containing 4 tables, NOT a simple CSV. It must be downloaded and parsed as text, not read via CSV parser.

### Table 1 — V2 MASTER AGENT REGISTRY: FULL PROTOCOL (ON-HAND)
- 61 confirmed on-hand agents
- CSV columns: `#`, `Agent`, `Form / Brand`, `Dose`, `Primary Targets`, `Phase(s)`, `Key Mechanism`, `Critical Synergies`, `Notable Interactions`
- Target key abbreviations: HM=Heavy Metals, SP=Spike Protein, GO/N=Graphene Oxide/Nanotech, P=Parasites, BF=Biofilm, MT=Mitochondrial, NR=Neurological, LV=Liver, KD=Kidney, LY=Lymphatic, IM=Immune, VE=Vascular, GI=Gut, EP=Epigenetic, F=Fungal, ROS=Reactive Oxygen Species

### Table 2 — V2 CRITICAL GAP FILLS: NEW ADDITIONS NOT IN V1
- Agents not in the original V1 protocol that were identified as critical additions
- Same CSV column structure as Table 1

### Table 3 — V2 PROCUREMENT SHOPPING LIST: WHERE TO BUY + GAP RATIONALE
- Procurement sources for each agent
- Includes gap rationale (why this agent was added)

### Table 4 — V1 → V2 FORMULATION UPGRADE LOG: WHAT TO REPLACE AND WHY
- Documents formulation changes between protocol versions
- Example: Magnesium Glycinate → Magnesium L-Threonate upgrade

## Total Agent Count

Approximately 127 agents across all 4 tables (61 in Table 1 + ~66 across Tables 2-4). This is the "127-agent registry" referenced throughout the handbook as "Section 7 — Agent Encyclopedia: Complete 127-agent registry."

## Download Pattern

```python
import json, urllib.request

with open('/root/.hermes/google_token.json') as f:
    access_token = json.load(f)['token']

fid = '16FamuAiD-w1e2s0BsdgLMYXhD4RjlL4E'  # MASTER_V2_REGISTRY_COMBINED.csv
url = f'https://www.googleapis.com/drive/v3/files/{fid}?alt=media'
req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
content = urllib.request.urlopen(req).read().decode('utf-8')
```

## Usage in Handbook Sections

- **Section 3.3 (Pillar-to-Phase Assignment Matrix)**: References 16 key agents as exemplars; cross-references to Section 7 for the full 127-agent matrix
- **Section 3.5 (MVS vs Gold Standard)**: Every MVS agent should be verifiable against the registry — if a proposed MVS agent isn't in Table 1 or Table 2, it may not exist in the protocol
- **Section 7 (Agent Encyclopedia)**: Will contain the formatted A-Z dossiers for all 127 agents. Currently 3/5 done (Synergy Map, Registry CSV, Synergy Matrix Report); A-Z formatted dossiers not yet built

# 06 — Music / Track / Beat Production

**Scope:** music creation, DAW control (Ableton Live 12, FL Studio 2024, rekordbox 7, Pioneer DJ), mixing/editing, house/tech-house/electronic.
**Legend:** ✅ [AUTHORED] = installed · 🔍 [RESEARCH] = discovered, source given · 🧩 [MCP] · 🛠️ [TOOL] · ★ = stars

---

## 👤 User's Music Stack (context for future Hermes)

- **DAWs:** Ableton Live 12, FL Studio 2024, GarageBand
- **DJ:** Pioneer DJ gear + rekordbox 7 (library in `~/Music/rekordbox/`, `~/Music/PioneerDJ/`)
- **Genres:** house / tech-house / electronic (Beatport tracks: Walker & Royce, Crystal Waters remixes, COBRAH, Fred again.., Boys Noize — 120-123 BPM)
- **Workflow:** sample packs (demo-tape claps), MIDI practice projects, beatport track downloads, live recordings
- **⚠️ HARD RULE:** NEVER touch/alter/remove music files, DAW apps, projects, exports, or the Tracks folder. Read-only context for skill authoring.

---

## ✅ Authored Skills (installed)

| Skill | Category | Description | Source |
|---|---|---|---|
| `songwriting-and-ai-music` | creative | Songwriting craft + Suno AI music prompts. | HUB |
| `voice-clone-tts` | voice | Clone a voice into Hermes TTS via F5-TTS (JARVIS clone, tuned nfe 24, cpu). | AUTHORED |

---

## 🔍 Research Findings — Best-of-Best (not yet authored)

### DAW Control (MCP servers — Ableton)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `Simon-Kansara/ableton-live-mcp-server` | 393 | Ableton Live OSC control MCP | **TOP** |
| `uisato/ableton-mcp-extended` | 252 | 220+ Ableton tools, extended control | TOP |
| `xiaolaa2/ableton-copilot-mcp` | 91 | Real-time Arrangement View control | HIGH |
| `OthmanAdi/loophole` | 16 | Official Extensions SDK MCP — one .ablx | HIGH |
| `romsau/agent4live` | 6 | Max for Live device w/ embedded MCP, 230 tools | HIGH |
| `gabrielpulga/ableton-dj-mcp` | 4 | AI electronic music production + DJing | MED |
| `FabianTinkl/AbletonMCP` | 8 | MIDI composition, transport, real-time params | MED |

### Ableton Skills (SKILL.md)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `glincker/ableton-skills` | 18 | 12 Claude skills for Ableton producers (arrangement-coach, etc.) | **TOP** |
| `LevyBytes/AI-SKILL-ableton-live` | 2 | Faithful Ableton Live 12 reference (Arrangement, identifier-preserving) | HIGH |
| `mkomorny/ableton-lom-osc-mapping` | 0 | Ableton LOM OSC paths + control mappings | MED |
| `Ronvaknins/ableton-extensions-skill` | 78 | Scaffold/build/package Ableton extensions | MED |

### rekordbox / DJ (user owns rekordbox 7 + Pioneer)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `ryan-voitiskis/reklawdbox` | 26 | **rekordbox library mgmt** — metadata, genres, set building | **TOP** |

### Music Production Pipelines
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `bitwize-music-studio/claude-ai-music-skills` | 431 | Human+AI music production (Suno workflow) | MED |
| `microsoft/Resource2Skill` | 471 | Distill your tracks/examples into executable skills | HIGH |
| `AgriciDaniel/claude-music` | 33 | ACE-Step 1.5 song generation in terminal | MED |
| `Shayanthn/livecodemusic` | 3 | **Techno/House/Electronic** algorithmic beats — Sonic Pi + AI (matches genre!) | HIGH |
| `audiofield/field` | 1 | Git-native, agent-operable music production | MED |
| `frankxai/agentic-music-producer-os` | 2 | Autonomous music-production workflows | LOW |
| `toolboc/a-team-music-agency` | 2 | Copilot agent squad simulating a studio | LOW |

### FL Studio (user owns FL Studio 2024)
| Repo | ★ | What it is | Priority |
|---|---|---|---|
| `OHPBP/FLStudioExpertLibrary` | 1 | FL Studio arranging/composing for AI agents | MED |
| `Hazy142/flstudio-ai-agent` | 0 | DAWMind — FL Studio natural-language control (API + vision) | LOW |
| `manueltarouca/fl-studio-web-daw` | 2 | Web DAW, AI agents compose via MCP | LOW |

---

## 🧩 MCP Servers (Music) — summary
All the `*mcp*` Ableton entries above are MCP servers. The **must-wire** set:
1. `ableton-live-mcp-server` (OSC, no key)
2. `ableton-mcp-extended` (220+ tools)
3. `reklawdbox` → wrap as skill + MCP (rekordbox)

---

## ⚠️ Notes
- **Never execute anything that modifies the user's music files.** Skills should *read* context and *produce new* files only.
- Ableton control requires Live's OSC/Extensions SDK enabled — document setup in the skill.
- `voice-clone-tts` is the JARVIS pipeline — reusable for any voice clone, not just JARVIS.
- Future expansion should prioritize: `glincker/ableton-skills`, `reklawdbox`, `ableton-live-mcp-server`, `livecodemusic` (genre-matched).

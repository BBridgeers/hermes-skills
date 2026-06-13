# VPS RAM Constraints for Local Ollama Models

Session data from 2026-05-22 on srv1617682 (Hostinger VPS, 7.8 GB RAM, CPU-only).

## Models Tested

| Model | Disk Size | RAM at Inference | Result |
|---|---|---|---|
| `closex/neuraldaredevil-8b-abliterated` (8B Q5_0) | 5.6 GB | 4.8 GB RSS | ❌ 163 MB free remaining |
| `huihui_ai/dolphin3-abliterated` (7B) | 4.9 GB | ~4.2 GB est. | ❌ borderline |

## System State During Test

```
              total        used        free      shared  buff/cache   available
Mem:           7.8Gi       5.9Gi       163Mi       9.5Mi       2.0Gi       1.8Gi
Swap:          4.0Gi       2.0Gi       2.0Gi
```

Runner process: `ollama runner --model .../sha256-9fc77e... --port 36009` consuming 4,813,588 KB RSS at 185% CPU during first-time model load.

After killing runner:
```
Mem:           7.8Gi       1.3Gi       4.8Gi
```

## Rule of Thumb

**Local Ollama models need ~2× their on-disk size in free RAM for safe inference.** An 8B Q5_0 model at 5.6 GB needs ~11 GB free. The VPS with 7.8 GB total cannot safely serve any model larger than ~3.9 GB on disk (~4B Q4).

## Where Local Models Do Work

- **Local machine (yoga@lenovo)**: 7.7 GB total RAM, ~7 GB free — fits 8B model with ~2.5 GB headroom
- **GPU machines**: Any GPU with sufficient VRAM (e.g., 8 GB VRAM for 8B Q5_0)
- **VPS with 16 GB+ RAM**: Headroom for 8B models

## Action When This Is Hit

1. Keep the Hermes config wired (provider definition stays in config.yaml)
2. Do NOT run inference on the constrained VPS
3. Direct user to use the model on their local machine instead
4. If the VPS must serve models, use smaller ones (3B–4B range, ~2–3 GB on disk)

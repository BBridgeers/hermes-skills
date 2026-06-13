# GPU Sizing Reality Check

Concrete examples from real hardware — so you don't recommend impossible configs.

## Gemma 4 E2B (2.3B effective, 5.1B total)

| Config | Memory needed | Fits? |
|---|---|---|
| float16 (no quant) | ~10.2 GB | Needs 12GB+ GPU |
| 8-bit (bitsandbytes) | ~5.1 GB | Needs 8GB+ GPU |
| 4-bit (bitsandbytes) | ~2.5 GB weights + 1-2 GB overhead | Needs 4GB+ GPU/VRAM |
| CPU (4-bit) | ~2.5 GB + system overhead | Works with 8GB+ system RAM |

**Real failure:** NVIDIA MX230 (2GB VRAM) — cannot fit Gemma 4 E2B at any quantization level. The weights alone at 4-bit exceed total VRAM.

**Real success:** CPU-only VPS with 7.8 GB RAM at 4-bit — tight but works. Expect 2-4 hours.

## When the GPU doesn't fit

Preferred order:
1. **HuggingFace Spaces** — free ZeroGPU, zero setup, 10-15 min: https://huggingface.co/spaces/pliny-the-prompter/OBLITERATUS
2. **CPU fallback** with `--quantization 4bit` — slow but works if RAM is sufficient
3. **Remote GPU** via `--remote user@gpu-node` (if you have access)
4. **Smaller model** — Qwen2.5-0.5B or TinyLlama 1.1B at 4-bit fit in 2GB VRAM

## Rule of thumb

4-bit VRAM requirement ≈ total_params × 0.5 + 1.5 GB (overhead). If that number exceeds `nvidia-smi` reported VRAM, the model won't fit.

---
name: obliteratus
description: "OBLITERATUS: abliterate LLM refusals (diff-in-means)."
version: 3.0.0
author: Hermes Agent
license: MIT
dependencies: [obliteratus, torch, transformers, bitsandbytes, accelerate, safetensors]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Abliteration, Uncensoring, Refusal-Removal, LLM, Weight-Projection, SVD, Mechanistic-Interpretability, HuggingFace, Model-Surgery]
    related_skills: [vllm, gguf, huggingface-tokenizers]
---

# OBLITERATUS Skill — Complete Reference

Remove refusal behaviors (guardrails) from open-weight LLMs without retraining. Uses mechanistic interpretability — diff-in-means, SVD, whitened SVD, LEACE, SAE decomposition, Bayesian kernel projection, and more — to identify and surgically excise refusal directions from model weights while preserving reasoning.

**Local clone (VPS):** `/root/OBLITERATUS` (upstream, elder-plinius)
**Installed in:** `/root/.hermes/hermes-agent/venv/` (editable install)
**CLI symlink:** `/usr/local/bin/obliteratus` → venv
**Upstream:** https://github.com/elder-plinius/OBLITERATUS (AGPL-3.0)

> **VPS status (2026-05-22):** CPU-only — NO GPU. Obliteration limited to tiny models (<1B). For GPU work, use `--remote` flag or HuggingFace Spaces / Colab.

**License warning:** OBLITERATUS is AGPL-3.0. NEVER import it as a Python library in MIT/Apache projects. Always invoke via CLI (`obliteratus` command) or subprocess. This keeps Hermes Agent's MIT license clean.

## Video Guide

Walkthrough: https://www.youtube.com/watch?v=8fG9BrNTeHs ("OBLITERATUS: An AI Agent Removed Gemma 4's Safety Guardrails")

## Architecture Overview (What Every File Does)

```
obliteratus/
├── __init__.py              # v0.1.2, lazy imports, public API surface
├── __main__.py              # python -m obliteratus entry
├── abliterate.py            # ★ CORE: AbliterationPipeline (6104 lines, 62 methods)
│                            #   METHODS dict with 13 presets, ProjectionEngine,
│                            #   SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH pipeline
├── adaptive_defaults.py     # Architecture-aware default parameters (710 lines)
├── architecture_profiles.py # Model family detection: Llama/Qwen/Mistral/DeepSeek/etc.
├── bayesian_optimizer.py    # Optuna TPE hyperparameter search (589 lines)
├── cli.py                   # CLI entry: argparse, 14 subcommands (1115 lines)
├── community.py             # Community contribution system
├── config.py                # YAML config loading/schema
├── device.py                # GPU auto-detection, CUDA setup, multi-GPU
├── informed_pipeline.py     # Analysis→abliteration feedback loop (1314 lines)
├── interactive.py           # Guided setup wizard
├── local_ui.py              # Gradio launcher (same UI as HF Space)
├── lora_ablation.py         # Reversible LoRA-based ablation adapters
├── mlx_backend.py           # Apple Silicon MLX support (469 lines)
├── models/
│   ├── __init__.py
│   └── loader.py            # Model loading, transformers≥5.0 compat shims (699 lines)
├── presets.py               # 116 curated models across 5 compute tiers (1182 lines)
├── prompts.py               # 114K of harmful/harmless/jailbreak prompt pairs (1624 lines)
├── remote.py                # SSH remote execution (435 lines)
├── reproducibility.py       # Deterministic seeding
├── runner.py                # Config-driven study runner
├── sweep.py                 # Strength sweep for coherence/refusal tradeoffs
├── telemetry.py             # Anonymous community benchmark collection (1249 lines)
├── tourney.py               # March Madness tournament: 10 methods head-to-head (1488 lines)
├── py.typed                 # PEP 561 marker
│
├── analysis/                # ★ 28 mechanistic interpretability modules
│   ├── __init__.py          # Module registry with descriptions
│   ├── activation_patching.py     # (1) Interchange interventions
│   ├── activation_probing.py      # (2) Post-excision residual probing
│   ├── alignment_imprint.py       # (3) DPO/RLHF/CAI/SFT fingerprinting
│   ├── anti_ouroboros.py          # (4) Self-repair detection & risk score
│   ├── bayesian_kernel_projection.py # (5) Probabilistic direction mapping
│   ├── causal_tracing.py          # (6) Causally necessary component ID
│   ├── concept_geometry.py        # (7) Single-direction vs polyhedral cone
│   ├── conditional_abliteration.py # (8) Category-specific removal
│   ├── cross_layer.py             # (9) Inter-layer direction alignment
│   ├── cross_model_transfer.py    # (10) Cross-architecture universality
│   ├── defense_robustness.py      # (11) Re-alignment resistance testing
│   ├── leace.py                   # (12) Linear Erasure via Closed-form Estimation
│   ├── logit_lens.py              # (13) Which layer "decides" to refuse
│   ├── multi_token_position.py    # (14) Multi-token refusal analysis
│   ├── probing_classifiers.py     # (15) Linear refusal classifiers
│   ├── residual_stream.py         # (16) Attention vs MLP contribution
│   ├── riemannian_manifold.py     # (17) Weight manifold geometry
│   ├── sae_abliteration.py        # (18) SAE feature-level removal (763 lines)
│   ├── sparse_surgery.py          # (19) Neuron-level precision editing
│   ├── spectral_certification.py  # (20) Mathematical removal bounds
│   ├── steering_vectors.py        # (21) Reversible inference-time steering
│   ├── tuned_lens.py              # (22) Trained per-layer decoding
│   ├── visualization.py           # (23) Heatmaps, plots, charts
│   ├── wasserstein_optimal.py     # (24) Optimal transport extraction
│   ├── wasserstein_transfer.py    # (25) Cross-model distribution transfer
│   └── whitened_svd.py            # (26) Covariance-normalized SVD
│
├── evaluation/              # Built-in benchmarking
│   ├── __init__.py
│   ├── advanced_metrics.py  # CKA, effective rank, angular drift (687 lines)
│   ├── baselines.py         # Pre-computed baseline comparisons
│   ├── benchmark_plots.py   # Benchmark visualization (451 lines)
│   ├── benchmarks.py        # Standard benchmark suite
│   ├── evaluator.py         # Perplexity + classification evaluation
│   ├── heretic_eval.py      # Heretic-style evaluation (1205 lines)
│   ├── lm_eval_integration.py # LM Eval Harness bridge
│   └── metrics.py           # Refusal rate, KL, coherence, perplexity
│
├── strategies/              # Structural ablation (beyond direction-based)
│   ├── __init__.py
│   ├── base.py              # AblationStrategy ABC + AblationSpec
│   ├── embedding_ablation.py
│   ├── ffn_ablation.py
│   ├── head_pruning.py
│   ├── layer_removal.py
│   ├── registry.py          # Strategy registry + decorator
│   └── utils.py             # get_attention_module, get_ffn_module, etc.
│
└── reporting/
    ├── __init__.py
    └── report.py            # JSON→HTML/Markdown report generation

tests/                       # 29 test files, ~13K lines
scripts/                     # Benchmarking scripts
docs/                        # Theory journal, research survey, audits
paper/                       # LaTeX paper (main.tex, appendix.tex)
examples/                    # YAML config examples for studies
notebooks/                   # Colab notebook (abliterate.ipynb)
```

### Key Numbers
- **Total Python:** ~35K lines across ~85 source files
- **Test coverage:** 29 test files, ~13K lines
- **Largest file:** abliterate.py at 6104 lines (the core pipeline)
- **Prompt database:** 114K of curated harmful/harmless/jailbreak pairs
- **Model presets:** 116 models across tiny/small/medium/large/frontier tiers

## When to Use This Skill

Trigger when the user:
- Wants to "uncensor" or "abliterate" an LLM
- Asks about removing refusal/guardrails from a model
- Wants to create an uncensored version of Llama, Qwen, Mistral, DeepSeek, etc.
- Mentions "refusal removal", "abliteration", "weight projection"
- Wants to analyze how a model's refusal mechanism works
- References OBLITERATUS, abliterator, or refusal directions
- Asks about mechanistic interpretability of safety features

## Step 1: Installation

**Already installed on this VPS** — skip to Step 2.

If not installed, clone from upstream and install via Hermes venv:
```bash
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS
/root/.hermes/hermes-agent/venv/bin/python -m pip install -e .
ln -sf /root/.hermes/hermes-agent/venv/bin/obliteratus /usr/local/bin/obliteratus
```

## Step 2: Check Hardware

```bash
python3 -c "
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'GPU: {gpu}')
    print(f'VRAM: {vram:.1f} GB')
    if vram < 4: print('TIER: tiny (models under 1B)')
    elif vram < 8: print('TIER: small (models 1-4B)')
    elif vram < 16: print('TIER: medium (models 4-9B with 4bit)')
    elif vram < 32: print('TIER: large (models 8-32B with 4bit)')
    else: print('TIER: frontier (models 32B+)')
else:
    print('NO GPU - only tiny models (<1B) on CPU')
"
```

### VRAM Requirements (4-bit quantization)

Rule of thumb: 4-bit VRAM ≈ total_params × 0.5 + 1.5 GB overhead. If that exceeds available VRAM, the model won't fit.
See `references/gpu-sizing-guide.md` for concrete hardware examples (Gemma 4 E2B on 2GB MX230 = fail, etc.).

| VRAM | Max Size | Example Models |
|:-----|:---------|:---------------|
| CPU only | ~1B | GPT-2, TinyLlama, SmolLM |
| 4-8 GB | ~4B | Qwen2.5-1.5B, Phi-3.5 mini, Llama 3.2 3B |
| 8-16 GB | ~9B | Llama 3.1 8B, Mistral 7B, Gemma 2 9B |
| 24 GB | ~32B | Qwen3-32B, Llama 3.1 70B (tight), Command-R |
| 48 GB+ | ~72B+ | Qwen2.5-72B, DeepSeek-R1 |
| Multi-GPU | 200B+ | Llama 3.1 405B, DeepSeek-V3 (685B MoE) |

## Step 3: Browse Models & Get Recommendations

```bash
obliteratus models --tier medium       # Browse by compute tier
obliteratus info <model_name>           # Architecture details
obliteratus recommend <model_name>      # Telemetry-driven best method+params
obliteratus recommend <model_name> --insights  # Cross-architecture rankings
obliteratus gpu-calc <model_name>       # Estimate GPU requirements
```

## Step 4: Choose a Method

### Full Method Catalog (13 total)

**9 CLI methods** (via `--method`):

| Method | Directions | Speed | Risk | Best For |
|:-------|:-----------|:------|:-----|:---------|
| **advanced** ★ DEFAULT | 4 (SVD) | ~10-20 min | Low-Med | Most models, well-tested |
| basic | 1 (diff-means) | ~5-10 min | Low | Quick tests, prototyping |
| aggressive | 8+ (whitened SVD) | ~20-30 min | Med-High | Stubborn refusals >10% |
| spectral_cascade | 6 (DCT) | ~15-25 min | Medium | Research, novel approach |
| informed | auto-configured | ~20-40 min | Variable | Auto-detection (experimental) |
| surgical | 8 (SAE+neuron) | ~1-2 hrs | Low | Reasoning models (R1, QwQ) |
| optimized | Bayesian search | Hours | Low | Maximum quality |
| inverted | 8 (reflected) | Medium | High | Research: active compliance |
| nuclear | 4 (combo) | Slow | Med-High | Stubborn MoE models |

**4 Python-API-only methods** (available via `AbliterationPipeline` Python API, NOT CLI):
- **failspy** — Reproduction of the most widely used community tool (FailSpy/abliterator). Single diff-in-means direction, all layers except layer 0. No norm preservation. What most HuggingFace abliterated models were created with.
- **gabliteration** — Faithful reproduction of Gabliteration (arXiv:2512.18901). SVD top-4 with ridge regularization, variance-based layer selection.
- **heretic** — Heretic-style with Bayesian optimization (Optuna TPE), activation winsorization, float layer interpolation. Co-minimizes refusal rate + KL divergence on Pareto front.
- **rdo** — Refusal Direction Optimization: gradient-based refinement of SVD-extracted directions using a linear refusal probe (Wollschlager et al., ICML 2025).

### Method Selection Flowchart
```
Quick test? → basic
MoE model? (Mixtral, DeepSeek-MoE) → nuclear
Reasoning model? (R1 distills, QwQ) → surgical
Need max quality, have time? → optimized
Default → advanced
advanced leaves >10% refusals? → aggressive
Still refusing? → nuclear
```

### Direction Extraction Methods (`--direction-method`)
| Method | Description | Best For |
|:-------|:------------|:---------|
| diff_means | Difference-in-means (Arditi et al.) | Default, fast, robust |
| svd | Multi-direction SVD | Complex alignment, multiple refusal mechanisms |
| leace | Linear Erasure via Closed-form Estimation | Maximum precision, mathematically optimal |

## Step 5: Run Abliteration

### Standard usage
```bash
obliteratus obliterate <model_name> --method advanced --output-dir ./abliterated-models
obliteratus obliterate <model_name> --method advanced --quantization 4bit --output-dir ./abliterated-models
obliteratus obliterate <model_name> --method advanced --quantization 4bit --large-model --output-dir ./abliterated-models
```

### Full parameter control
```bash
obliteratus obliterate <model_name> \
  --method advanced \
  --direction-method diff_means \
  --n-directions 4 \
  --refinement-passes 2 \
  --regularization 0.1 \
  --quantization 4bit \
  --output-dir ./abliterated-models \
  --contribute  # opt-in telemetry
```

### Key flags
| Flag | Description | Default |
|:-----|:------------|:--------|
| `--method` | Abliteration method | advanced |
| `--direction-method` | Direction extraction (diff_means/svd/leace) | diff_means |
| `--n-directions` | Number of refusal directions (1-32) | method-dependent |
| `--refinement-passes` | Iterative passes (1-5) | 2 |
| `--regularization` | Regularization strength (0.0-1.0) | 0.1 |
| `--quantization` | Load in 4bit or 8bit | none |
| `--large-model` | Conservative defaults for 120B+ | false |
| `--gpus` | Comma-separated GPU IDs or 'all' | all |
| `--remote` | Run on remote GPU node via SSH | none |
| `--output-dir` | Where to save | ./obliterated_model |
| `--contribute` | Share anonymized results | false |
| `--verify-sample-size` | Test prompts for refusal check | 30 |

### Other execution modes
```bash
obliteratus interactive              # Guided wizard
obliteratus ui --port 7860           # Gradio web UI (same as HF Space)
obliteratus run config.yaml --preset quick  # YAML config study
obliteratus tourney <model_name>     # Tournament: all methods head-to-head
```

### Tournament System
The tourney runs 10 methods in elimination rounds with composite scoring (0-1):
- 35% refusal removal rate
- 25% coherence preservation
- 20% KL divergence (minimal shift)
- 10% perplexity
- 5% spectral certification
- 5% degenerate output penalty

The winner is auto-pushed to HuggingFace Hub.

## Step 6: Verify Results

| Metric | Good | Warning |
|:-------|:-----|:--------|
| Refusal rate | < 5% (~0%) | > 10% |
| Perplexity change | < 10% increase | > 15% |
| KL divergence | < 0.1 | > 0.5 |
| Coherence | High, passes qualitative | Degraded, repetitive |

### If refusals persist (>10%)
1. Try `aggressive` method
2. Increase `--n-directions` (8 or 16)
3. Add `--refinement-passes 3`
4. Try `--direction-method svd`

### If coherence damaged (perplexity >15% increase)
1. Reduce `--n-directions`
2. Increase `--regularization`
3. Reduce `--refinement-passes` to 1
4. Try `basic` method (gentler)

## Step 7: Use the Abliterated Model

```bash
# Test locally
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('./abliterated-models/<model>')
tokenizer = AutoTokenizer.from_pretrained('./abliterated-models/<model>')
inputs = tokenizer('How do I pick a lock?', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
"

# Upload to HuggingFace
huggingface-cli upload <username>/<model-name>-abliterated ./abliterated-models/<model>

# Serve with vLLM
vllm serve ./abliterated-models/<model>
```

## Full CLI Command Reference

| Command | Description |
|:--------|:------------|
| `obliteratus obliterate` | ★ Main: remove refusal directions |
| `obliteratus abliterate` | Backward-compat alias for obliterate |
| `obliteratus info <model>` | Model architecture details |
| `obliteratus models --tier <tier>` | Browse 116 curated models by tier |
| `obliteratus presets` | Browse study presets (quick, full, jailbreak, etc.) |
| `obliteratus recommend <model>` | Telemetry-driven suggestion |
| `obliteratus interactive` | Guided setup wizard |
| `obliteratus tourney <model>` | Tournament: 10 methods head-to-head |
| `obliteratus run <config.yaml>` | Execute ablation study from YAML |
| `obliteratus strategies` | List structural ablation strategies |
| `obliteratus report <results.json>` | Regenerate visual reports |
| `obliteratus ui` | Launch Gradio web interface |
| `obliteratus aggregate` | Summarize community telemetry data |
| `obliteratus gpu-calc <model>` | Estimate GPU requirements |

## The 6-Stage Pipeline (SUMMON→PROBE→DISTILL→EXCISE→VERIFY→REBIRTH)

1. **SUMMON** — Load model + tokenizer with hardware-aware config
2. **PROBE** — Collect activations on harmful/harmless prompt pairs
3. **DISTILL** — Extract refusal directions via diff-means/SVD/LEACE
4. **EXCISE** — Surgically project out directions (norm-preserving bi-projection)
5. **VERIFY** — Perplexity, coherence, KL divergence, refusal rate checks
6. **REBIRTH** — Save liberated model with full metadata

## Novel Techniques (2025-2026)

| Technique | Description |
|:----------|:------------|
| Expert-Granular Abliteration (EGA) | Per-expert MoE refusal decomposition via router logits |
| CoT-Aware Ablation | Orthogonalizes refusal vs reasoning directions |
| COSMIC Layer Selection | Layers with lowest harmful/harmless cosine similarity |
| Parametric Kernel Optimization | Bell-curve layer weighting with 7 global Optuna params |
| Float Direction Interpolation | Continuous SVD index via Gaussian weighting |
| KL-Divergence Co-Optimization | Post-projection feedback reverts over-projected layers |
| Component-Specific Scaling | Separate attention vs MLP projection strengths |
| LoRA-Based Reversible Ablation | Rank-1 LoRA adapters instead of permanent surgery |
| Activation Winsorization | Clamp activations to percentile range pre-SVD |
| Multi-Direction Norm Preservation | Capture all norms once, restore after all directions |

## Structural Ablation Strategies (beyond direction-based)

List all: `obliteratus strategies`

- **Embedding Ablation** — Target embedding layer components
- **FFN Ablation** — Feed-forward network block removal
- **Head Pruning** — Attention head pruning
- **Layer Removal** — Full layer removal

## Telemetry System

Anonymous, opt-in community benchmark collection:
- Local JSONL file (~/.obliteratus/telemetry.jsonl)
- Auto-syncs to HuggingFace Dataset repo on Spaces
- No user identity, IP, or prompt content stored
- Only: model name, method, scores, hardware, timestamp
- Enable with `--contribute` flag or `OBLITERATUS_TELEMETRY=1`

## Model Presets (116 total across 5 tiers)

Organized by provider, ordered by size. Key families:
- **01.AI (Yi):** 6B, 9B, 34B
- **Alibaba (Qwen):** 0.5B–72B, Qwen2.5, Qwen3
- **Cohere (Command-R):** 35B, 104B (Aya Expanse)
- **DeepSeek:** V3 (685B MoE), R1 (685B MoE), R1 Distills (1.5B–70B), Coder V2
- **Google (Gemma):** 2B, 7B, 9B, 27B
- **IBM (Granite):** 3B, 8B, 20B
- **Meta (Llama):** 3.2 (1B–3B), 3.1 (8B–405B), 3.3 (70B), 4 (Scout/Maverick)
- **Microsoft (Phi):** 3.8B, 14B, Phi-4 series
- **Mistral:** 7B, 8x7B MoE, 8x22B MoE, Small 22B
- **Nous Research:** Hermes 3 (3B–405B)
- **NVIDIA (Nemotron):** 4B, 8B, 15B, 51B
- **TII (Falcon):** 7B, 40B, 180B
- **Upstage (SOLAR):** 10.7B

Browse: `obliteratus models --tier <tiny|small|medium|large|frontier>`

## Analysis Modules (28 total)

Run pre-abliteration analysis to understand refusal geometry:
```bash
obliteratus run analysis-study.yaml --preset quick    # 2-3 modules
obliteratus run analysis-study.yaml --preset full     # All core + geometric
```

Key modules to run first:
- **alignment_imprint** — Fingerprint DPO/RLHF/CAI/SFT method
- **concept_geometry** — Single direction vs polyhedral cone
- **logit_lens** — Which layer decides to refuse
- **anti_ouroboros** — Self-repair risk score (0-1)
- **causal_tracing** — Causally necessary components

See `skill_view(name="obliteratus", file_path="references/analysis-modules.md")` for full 28-module catalog.

## YAML Config Templates

Load via skill_view:
- `templates/abliteration-config.yaml` — Standard single-model config
- `templates/analysis-study.yaml` — Pre-abliteration analysis study
- `templates/batch-abliteration.yaml` — Multi-model batch processing

## Platform Support

- **CUDA** — Full support (NVIDIA GPUs)
- **Apple Silicon (MLX)** — Supported via MLX backend
- **CPU** — Supported for tiny models (<1B)

## Common Pitfalls

1. **OBLITERATUS is NOT on PyPI.** `pip install obliteratus` WILL FAIL. Clone from GitHub: `git clone https://github.com/elder-plinius/OBLITERATUS.git && cd OBLITERATUS && pip install -e .`
2. **Don't use `informed` as default** — it's experimental. Use `advanced` for reliable results.
2. **Models under ~1B respond poorly** — shallow refusal behaviors, expect 20-40% remaining refusal. Models 3B+ have cleaner directions (~0% refusal with advanced).
3. **`aggressive` can make things worse** — on small models it can damage coherence and increase refusal. Only use if `advanced` leaves >10% refusals on a 3B+ model.
4. **Always check perplexity** — if >15% spike, model is damaged. Reduce aggressiveness.
5. **MoE models need `nuclear`** — for Mixtral, DeepSeek-MoE, etc.
6. **Quantized models can't be re-quantized** — abliterate full-precision, then quantize output.
7. **Reasoning models are sensitive** — use `surgical` for R1 distills to preserve CoT.
8. **Check `obliteratus recommend`** — telemetry data may have better parameters than defaults.
9. **AGPL license** — never `import obliteratus` in MIT/Apache projects. CLI invocation only.
10. **Large models (70B+)** — always use `--large-model` flag.
11. **Spectral certification RED is common** — the spectral check often flags "incomplete" even when practical refusal rate is 0%. Check actual refusal rate, not spectral cert alone.
12. **SSH remote execution** — use `--remote` flag for offloading to GPU nodes.
13. **Multi-GPU** — use `--gpus 0,1,2,3` for explicit device selection; models auto-split via accelerate.

## Integration Patterns

### With vLLM (serve abliterated models)
```bash
obliteratus obliterate meta-llama/Llama-3.1-8B-Instruct --method advanced -o ./abliterated
vllm serve ./abliterated/Llama-3.1-8B-Instruct
```

### With GGUF (convert for llama.cpp)
```bash
obliteratus obliterate <model> --method advanced -o ./abliterated
# Then use gguf skill to convert ./abliterated/<model> to GGUF
```

### With HuggingFace Hub (upload)
```bash
obliteratus obliterate <model> --method advanced -o ./abliterated
huggingface-cli upload <user>/<model>-abliterated ./abliterated/<model>
```

### Remote GPU execution
```bash
obliteratus obliterate <model> --remote gpu-node.example.com --ssh-key ~/.ssh/id_rsa
```

## Complementary Skills

- **vllm** — Serve abliterated models with high throughput
- **gguf** — Convert abliterated models to GGUF for llama.cpp
- **huggingface-tokenizers** — Work with model tokenizers
- **axolotl / unsloth** — Fine-tune abliterated models further

# Local Uncensored Model Benchmarks

Session-derived comparison data for models evaluated as local Hermes providers.

## NeuralDaredevil-8B-abliterated (Maxime Labonne)

- **Ollama pull**: `ollama pull closex/neuraldaredevil-8b-abliterated`
- **Size**: 5.6 GB (Q5_0 quant)
- **Base**: Llama 3 8B → Daredevil-8B → abliteration → DPO recovery (orpo-dpo-mix-40k)
- **Open LLM Leaderboard scores**: MMLU 69.1 | ARC 69.28 | HellaSwag 85.05 | GSM8K 71.8 | TruthfulQA 60.0 | Winogrande 78.69
- **Rank**: #1 uncensored 8B on Open LLM Leaderboard
- **Downloads**: 15,601/month
- **Verdict**: Gold standard for uncensored 8B. DPO fine-tune recovers performance lost to abliteration.
- **RAM observed**: 4.8 GB RSS on CPU-only VPS (8 GB total) — not viable for production there. Fine on local with 7+ GB free.

## Dolphin3.0-Llama3.1-8B-abliterated (huihui-ai)

- **Ollama pull**: `ollama pull huihui_ai/dolphin3-abliterated`
- **Size**: 4.9 GB (Q4_K_M quant)
- **Base**: Llama 3.1 8B → Dolphin3.0 → abliteration (remove-refusals-with-transformers)
- **Open LLM Leaderboard scores**: NOT POSTED
- **Downloads**: 367/month
- **Author's own words**: "crude, proof-of-concept implementation"
- **Verdict**: Inferior to NeuralDaredevil in every dimension. No benchmark validation. Smaller (0.7 GB less) but that's irrelevant on any machine with 7+ GB RAM.

## Recommendation

Use NeuralDaredevil-8B-abliterated as the sole local uncensored model. Dolphin3 adds nothing. NeuralDaredevil's DPO recovery training makes it genuinely better than the original Llama 3 Instruct while being fully uncensored — a rare combination.

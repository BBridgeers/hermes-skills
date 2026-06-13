# Ollama Environment Variables — Complete Reference
*Source: docs.ollama.com FAQ, Troubleshooting, Context Length, and GPU pages — crawled 2026-05-21*

## Core Server Configuration

| Variable | Purpose | Default |
|---|---|---|
| `OLLAMA_HOST` | Bind address for the Ollama API server | `127.0.0.1:11434` |
| `OLLAMA_MODELS` | Directory where downloaded models are stored | OS-dependent (see below) |
| `OLLAMA_ORIGINS` | CORS allowed origins for browser access | `127.0.0.1,0.0.0.0` |

## Model Default Locations

| OS | Path |
|---|---|
| macOS | `~/.ollama/models` |
| Linux (systemd) | `/usr/share/ollama/.ollama/models` |
| Windows | `C:\Users\%username%\.ollama\models` |

## Performance & Memory

| Variable | Purpose | Default |
|---|---|---|
| `OLLAMA_CONTEXT_LENGTH` | Default context window size in tokens | 4096 (or VRAM-based: <24GB=4K, 24-48GB=32K, ≥48GB=256K) |
| `OLLAMA_KEEP_ALIVE` | Duration model stays loaded in memory after last request | `5m` |
| `OLLAMA_MAX_LOADED_MODELS` | Max concurrent models loaded in memory | `3 × GPU count` (or `3` for CPU) |
| `OLLAMA_NUM_PARALLEL` | Max parallel requests per loaded model | `1` |
| `OLLAMA_MAX_QUEUE` | Max queued requests when server is busy | `512` |
| `OLLAMA_FLASH_ATTENTION` | Enable Flash Attention (reduces memory at high context sizes) | disabled (`0`) |
| `OLLAMA_KV_CACHE_TYPE` | K/V cache quantization type | `f16` |

### K/V Cache Types
- `f16` — high precision, high memory (default)
- `q8_0` — 8-bit, ~1/2 memory of f16, negligible quality loss (recommended if not using f16)
- `q4_0` — 4-bit, ~1/4 memory of f16, small-medium quality loss at high context

## GPU Configuration

| Variable | Purpose |
|---|---|
| `CUDA_VISIBLE_DEVICES` | Limit NVIDIA GPUs (comma-separated IDs or UUIDs). Set to `-1` to force CPU |
| `ROCR_VISIBLE_DEVICES` | Limit AMD GPUs. Set to `-1` to force CPU |
| `GGML_VK_VISIBLE_DEVICES` | Limit Vulkan GPUs. Set to `-1` to disable all Vulkan GPUs |
| `OLLAMA_VULKAN` | Enable experimental Vulkan GPU support | disabled |
| `OLLAMA_LLM_LIBRARY` | Force specific LLM library (bypass autodetection). Options: `cpu`, `cpu_avx`, `cpu_avx2`, plus GPU-specific libs |
| `HSA_OVERRIDE_GFX_VERSION` | Override AMD GPU LLVM target for unsupported GPUs (e.g., `10.3.0` for RX 5400) |

## Cloud & Networking

| Variable | Purpose | Default |
|---|---|---|
| `OLLAMA_API_KEY` | API key for ollama.com cloud access | none |
| `OLLAMA_NO_CLOUD` | Disable all Ollama cloud features (models + web search) | disabled |
| `HTTPS_PROXY` | Proxy for outbound model downloads (HTTPS only — do NOT set `HTTP_PROXY`) | none |
| `OLLAMA_TMPDIR` | Alternate temp directory when `/tmp` has `noexec` flag | system temp |

## Debugging

| Variable | Purpose |
|---|---|
| `OLLAMA_DEBUG` | Enable debug-level logging |
| `OLLAMA_VERSION` | Install specific version via install script (e.g., `OLLAMA_VERSION=0.5.7`) |
| `AMD_LOG_LEVEL` | AMD GPU log verbosity (set to `3` for detailed HIP/ROCm logs) |
| `CUDA_ERROR_LEVEL` | NVIDIA CUDA error verbosity (set to `50` for diagnostic logs) |

## Disabling Cloud Features

To run Ollama in fully local mode, set in `~/.ollama/server.json`:
```json
{
  "disable_ollama_cloud": true
}
```
Or environment variable: `OLLAMA_NO_CLOUD=1`

## Concurrent Request Tuning

- `OLLAMA_MAX_LOADED_MODELS` controls how many different models can be loaded simultaneously
- `OLLAMA_NUM_PARALLEL` × `OLLAMA_CONTEXT_LENGTH` determines RAM requirement per model
- When VRAM is insufficient for a new model, idle models are unloaded to make room
- Queued requests (up to `OLLAMA_MAX_QUEUE`) are processed FIFO
- Windows + Radeon GPUs: default to 1 model max due to ROCm v5.7 VRAM reporting limitations

## Model Preloading

Preload a model without generating:
```bash
# API method
curl http://localhost:11434/api/generate -d '{"model": "mistral"}'

# CLI method
ollama run llama3.2 ""
```

Keep a model permanently loaded:
```bash
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": -1}'
```

Immediately unload:
```bash
curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "keep_alive": 0}'
```

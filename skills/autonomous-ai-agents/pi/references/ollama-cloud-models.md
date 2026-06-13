# Ollama Cloud Model Catalog (May 2026)

Source: `https://ollama.com/search?c=cloud`

## Coding-Focused (Primary)

| Model | Params | Notes |
|---|---|---|
| `qwen3-coder:480b` | 510B | Dedicated coding model |
| `kimi-k2.6` | 595B | Multimodal agentic, swarm orchestration |
| `glm-5.1` | 1.5T | SOTA SWE-Bench Pro, agentic engineering |
| `gpt-oss:120b` | 65B | OpenAI open model via Ollama |
| `deepseek-v4-pro` | 1.6T | 1M context, 3 reasoning modes |
| `deepseek-v4-flash` | 284B (13B active) | MoE, efficient reasoning |
| `minimax-m2.7` | 480B | Fast coding, professional productivity |
| `gemma4:31b` | 62B | Google's latest, vision+audio |
| `qwen3.5` | 397B | Multimodal, vision+tools+thinking |
| `nemotron-3-super` | 230B (12B active) | NVIDIA, multi-agent |
| `qwen3-coder-next` | 81B | Next-gen Qwen coder |

## General Reasoning

| Model | Params | Notes |
|---|---|---|
| `kimi-k2:1t` | 1.1T | Previous gen Kimi |
| `kimi-k2.5` | 1.1T | Previous gen Kimi |
| `kimi-k2-thinking` | 1.1T | Thinking variant |
| `glm-5` | 756B | Strong reasoning, agentic |
| `glm-4.7` | 696B | Previous gen GLM |
| `minimax-m2.5` | 230B | Previous gen MiniMax |
| `minimax-m2.1` | 230B | Multilingual |
| `deepseek-v3.2` | 688B | Harmonized efficiency + reasoning |
| `deepseek-v3.1:671b` | 688B | Previous gen DeepSeek |
| `gemini-3-flash-preview` | cloud | Google Gemini |

## Specialized

| Model | Params | Notes |
|---|---|---|
| `qwen3-vl:235b` | 470B | Vision-language |
| `mistral-large-3:675b` | 682B | Mistral flagship |
| `devstral-2:123b` | 128B | Dev-focused |
| `ministral-3:14b` | 15.7B | Edge deployment |
| `ministral-3:8b` | 10.4B | Edge deployment |
| `ministral-3:3b` | 4.7B | Tiny edge |
| `nemotron-3-nano:30b` | 32.6B | NVIDIA nano |
| `cogito-2.1:671b` | 688B | Cogito |
| `rnj-1:8b` | 16B | Code + STEM |

## Access Patterns

### Local Ollama (Ed25519 key required)
```bash
ollama pull qwen3-coder:480b-cloud
ollama run qwen3-coder:480b-cloud "prompt"
```

### Direct API (API key — no Ed25519 needed)
```bash
curl -s https://ollama.com/api/chat \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -d '{"model": "qwen3-coder:480b", "messages": [...]}'
```

### Agent Configuration
- **Anthropic-compatible (Claude Code):** `base_url=https://ollama.com`, auth via API key
- **OpenAI-compatible (Codex, Pi, OpenCode):** `base_url=https://ollama.com/v1`, auth via API key
- **Cloud models via direct API omit the `:cloud` suffix**

# Qwen 3.7 Max — Full Provider Scan (2026-05-30)

Model: `qwen/qwen3.7-max` (OpenRouter), `qwen3.7-max` (native)
Released: 2026-05-19/21 | Context: 1,000,000 tokens | Max Output: 65,536 tokens
Closed-weight — API only. No download. No local run.

## Provider Availability

| Provider | Status | Model ID | Input/1M | Output/1M | Cache Read |
|---|---|---|---|---|---|
| **OpenRouter** | ✅ LIVE | `qwen/qwen3.7-max` | $1.25 | $3.75 | $0.25 |
| **Alibaba Cloud Intl** | ✅ LIVE | `qwen3.7-max` | $2.50 | $7.50 | Discount avail |
| **Alibaba Cloud China** | ✅ LIVE | `qwen3.7-max` | $1.65 | $4.95 | — |
| **OpenCode Zen** | ✅ LIVE | `qwen3.7-max` | $2.50 | $7.50 | $0.50 |
| **Novita AI** | ✅ LIVE | `qwen/qwen3.7-max` | $1.25 | $7.50 | $0.25 |
| **Vercel AI Gateway** | ✅ LIVE | `alibaba/qwen3.7-max` | $1.25 | $3.75 | $0.25 |
| **Together AI** | ✅ LIVE | — | — | — | — |
| **DeepSeek API** | ❌ | — | — | — | — |
| **Groq** | ❌ | — | — | — | — |
| **Ollama Cloud** | ❌ | — | — | — | — |
| **Ollama Local** | ❌ | — | — | — | — |
| **OpenCode Go** | ❌ | — | — | — | — |

## Pricing Winner Matrix

| Priority | Best Provider | Price |
|---|---|---|
| Cheapest overall | OpenRouter | $1.25/$3.75 |
| Cheapest input | OpenRouter or Novita | $1.25 |
| Cheapest output | OpenRouter or Vercel | $3.75 |
| Free trial | Alibaba Intl | 1M tokens free / 90 days |
| Hermes integration | OpenRouter | Already configured |

## API Integration

**OpenRouter (recommended for Hermes)**:
```bash
hermes config set model.default qwen/qwen3.7-max
hermes config set model.provider openrouter
```

**Alibaba DashScope (cheapest direct)**:
```python
from openai import OpenAI
client = OpenAI(
    api_key="DASHSCOPE_API_KEY",
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen3.7-max",
    messages=[{"role": "user", "content": "..."}],
)
```

**Key**: DashScope API key from modelstudio.console.alibabacloud.com
International endpoint (Singapore): `dashscope-intl.aliyuncs.com`
China endpoint (Beijing): `dashscope.aliyuncs.com`

## Notes
- OpenRouter API pricing field is authoritative — web page may show different "list price"
- Go has Qwen 3.5 Plus and 3.6 Plus but NOT 3.7 Max
- Groq has zero Qwen models (Llama/GPT-OSS only)
- Alibaba direct has ~34% China discount but compute restricted to mainland
- OpenCode Zen caches writes at $3.125/1M (highest cache write cost)

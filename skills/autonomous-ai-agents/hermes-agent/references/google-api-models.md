# Google AI API — Model Discovery & Image Generation

## API Endpoints

**List models (API key required):**
```
GET https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY
```

**Generate content (Gemini chat):**
```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

**OpenAI-compatible chat:**
```
POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
Header: x-goog-api-key: $GOOGLE_API_KEY
```

**OpenAI-compatible models list:**
```
GET https://generativelanguage.googleapis.com/v1beta/openai/models
Header: x-goog-api-key: $GOOGLE_API_KEY
```

## Image Generation Models (as of May 2026)

| Model ID | Type | Context | Notes |
|---|---|---|---|
| `gemini-3-pro-image-preview` | Pro image gen | 131K in | Higher quality, aka "Nano Banana Pro" |
| `gemini-3.1-flash-image-preview` | Flash image gen | 65K in | Faster, native image output |
| `gemini-2.5-flash-image` | 2.5 Flash image | 32K in | Older, still functional |

## Image Gen via Native API

```python
body = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
}
# POST to /v1beta/models/gemini-3-pro-image-preview:generateContent
# Images returned as inlineData (base64) in response parts
```

## Rate Limits

Google AI Studio free tier: ~10 RPM. Pro/paid tier has higher limits.
429 errors during model discovery/listings are common — space out calls.
Image generation counts against the same rate limit bucket.

**AI Studio prepaid credit exhaustion**: If you get 429 with "Your prepayment credits are depleted", the free credits ran out. Two fixes:
1. Add credits at https://ai.studio — or
2. Switch to Vertex AI with a billed Cloud project (see `devops/hermes-onboard/references/google-cloud-vertex.md`)

## Vertex AI (Billed Cloud Project)

For production use with proper rate limits, authenticate via gcloud and use Vertex AI:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
pip install --break-system-packages google-cloud-aiplatform Pillow
```

Then use `vertexai.init(project="...")` and `ImageGenerationModel.from_pretrained("imagen-4.0-generate-001")` instead of the AI Studio REST API.

**No rate limits** on Vertex AI — billed to your Cloud project per usage.

## Custom Provider Config for config.yaml

```yaml
custom_providers:
  - name: Google
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
    api_key_env: GOOGLE_API_KEY
    api_mode: chat_completions
    models:
      gemini-3.1-pro-preview:
        context_length: 1048576
      gemini-3.1-flash-lite:
        context_length: 1048576
      gemma-4-31b-it:
        context_length: 262144
      gemma-4-26b-a4b-it:
        context_length: 262144
```

**CRITICAL — never set a Google image model as the general default model.**
Image models (`gemini-3-pro-image-preview`, `nano-banana-pro-preview`, etc.)
route through the image generation pipeline, not the standard chat completions
path. Setting one as `model.default` breaks all tool use, agent looping, and
normal chat operations. The user must explicitly switch to image models only
when they want image generation, then switch back. Treat image models as
task-REDACTED, not default-capable.

Pitfall: do NOT set a Google image model as the general default — it will route ALL chat through the image endpoint, breaking tool use and normal agent operation. Image models should only be used explicitly via /model switching or workspace Swarm selection.

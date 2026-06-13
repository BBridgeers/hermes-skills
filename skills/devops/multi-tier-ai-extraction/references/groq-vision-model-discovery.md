# Groq Vision Model Discovery — 2026-05-26

## Current State

As of 2026-05-26, Groq hosts 16 total models. **Only ONE is vision-capable:**

| Model ID | Status | Notes |
|----------|--------|-------|
| `meta-llama/llama-4-scout-17b-16e-instruct` | ✅ Vision works | Returns "Red." from red PNG. Supports image_url content blocks. |
| `llama-3.2-90b-vision-preview` | ❌ DECOMMISSIONED | Returns `model_decommissioned` error |
| `llama-3.2-11b-vision-preview` | ❌ DECOMMISSIONED | Returns `model_decommissioned` error |
| `llama-3.3-70b-versatile` | Text only | Works for text enrichment, no image support |
| `qwen/qwen3-32b` | Text only | No image support |
| `openai/gpt-oss-120b` | Text only | Free tier, text-only |

## How to Discover Current Models

```bash
# List all active models
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data.get('data', []):
    if m.get('active', True):
        print(f\"{m['id']:50s} owned_by={m.get('owned_by','?')}\")
"

# Filter for vision-capable (search for 'vision', 'vl', 'scout', 'omni' in IDs)
# Note: 'scout' and 'omni' in model names don't guarantee vision — must test
```

## Testing Vision Capability

Llama 4 Scout supports images but is NOT labeled "vision" in the model ID. Always test:

```python
import base64, struct, zlib

def make_test_png(w=64, h=64, r=255, g=0, b=0):
    """Create a simple colored PNG for vision testing."""
    raw = b''
    for y in range(h):
        raw += b'\x00' + bytes([r, g, b]) * w
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(raw))
    iend = chunk(b'IEND', b'')
    return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend

png = make_test_png(64, 64, 255, 0, 0)
b64 = base64.b64encode(png).decode()

# Test with: "What color is this? ONE WORD."
# Expected: "Red." or "red" if vision works
# Null/empty response = no vision support
# "model_decommissioned" = model removed
```

## Key Lesson

Groq's vision model lineup is UNSTABLE. Models get decommissioned without notice. The llama-3.2 vision preview models went from "available" to "decommissioned" in under 6 months. **Always run the discovery command before deploying Groq vision pipelines.**

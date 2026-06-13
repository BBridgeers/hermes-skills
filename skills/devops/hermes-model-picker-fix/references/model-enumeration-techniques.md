# Model Enumeration Techniques

## Parsing models.json for Display

When users request a clean list of all available models (like for swarm creation), parse the `~/.hermes/models.json` file to organize models by provider:

### Python Script Approach
```python
import json

# Read and parse models.json
with open('/root/.hermes/models.json', 'r') as f:
    models_data = json.load(f)

# Group models by provider
provider_groups = {}
for model_info in models_data:
    provider = model_info['provider']
    model_name = model_info['model']
    if provider not in provider_groups:
        provider_groups[provider] = []
    provider_groups[provider].append(model_name)

# Display organized list
print("MODELS BY PROVIDER:")
print("=" * 50)

for provider, models in provider_groups.items():
    print(f"\n{provider.upper()} ({len(models)} models):")
    print("-" * 30)
    for model in sorted(models):
        print(f"  • {model}")

# Print total count
total_models = sum(len(models) for models in provider_groups.values())
print(f"\nTOTAL MODELS: {total_models}")
```

### Terminal Commands Approach
```bash
# Count total models
cat /root/.hermes/models.json | wc -l

# Preview file structure
head -20 /root/.hermes/models.json

# Quick provider count
jq 'group_by(.provider) | map({provider: .[0].provider, count: length})' /root/.hermes/models.json
```

### Common Output Format
Users typically want:
- Models grouped by provider
- Clean bullet-point format
- Provider names in uppercase
- Model counts per provider
- Total model count

### File Location Notes
- Primary: `/root/.hermes/models.json`
- Cache: `/root/.hermes/models_dev_cache.json`
- Provider-specific: `/root/.hermes/deepseek_openrouter_models.txt`, `/root/.hermes/ollama_cloud_models_cache.json`

This technique is useful for:
- Debugging model picker issues
- Providing users with comprehensive model lists
- Understanding model distribution across providers
- Verifying model configuration completeness
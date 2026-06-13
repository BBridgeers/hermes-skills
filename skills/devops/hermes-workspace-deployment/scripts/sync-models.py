#!/usr/bin/env python3
"""Sync all configured models to ~/.hermes/models.json for workspace picker.

Five phases:
  1. config.yaml (custom_providers, providers, fallback_providers, default)
  2. OpenRouter free models (pricing.prompt + pricing.completion == $0)
  3. OpenCode Go (Bearer auth)
  4. OpenCode Zen (Bearer auth)
  5. Google Gemini (API key auth)

Uses curl subprocess instead of urllib — urllib gets HTTP 403 on OpenCode APIs
due to TLS/User-Agent issues.

Backs up the existing models.json before overwriting.
Normalizes provider names to lowercase for consistent workspace grouping.
"""
import json, os, shutil, subprocess, sys, yaml
from datetime import datetime

MODELS_PATH = os.path.expanduser('~/.hermes/models.json')
CONFIG_PATH = os.path.expanduser('~/.hermes/config.yaml')
ENV_PATH = os.path.expanduser('~/.hermes/.env')

# Normalize capital-case provider names from config to match live API sources
PROVIDER_NORMALIZE = {
    'Google': 'google',
    'DeepSeek': 'deepseek',
    'Openrouter': 'openrouter',
    'Opencode': 'opencode',
    'Ollama': 'ollama',
}


def read_env_key(key_name):
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith(f'{key_name}='):
                return line.strip().split('=', 1)[1]
    return None


def curl_json(url, headers, timeout=15):
    """Fetch JSON via curl — avoids urllib TLS/User-Agent 403 on OpenCode."""
    cmd = ['curl', '-s', '--max-time', str(timeout)]
    for k, v in headers.items():
        cmd += ['-H', f'{k}: {v}']
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)


def main():
    # --- Backup existing ---
    if os.path.exists(MODELS_PATH):
        backup = MODELS_PATH + '.bak.' + datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(MODELS_PATH, backup)
        print(f"Backed up to {os.path.basename(backup)}", file=sys.stderr)

    models = []
    seen = set()

    def add(model_id, provider):
        provider = PROVIDER_NORMALIZE.get(provider, provider)
        key = f"{provider}:{model_id}"
        if key not in seen and model_id:
            seen.add(key)
            models.append({"model": model_id, "provider": provider})

    # --- Phase 1: Config ---
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    m = config.get('model', {})
    if isinstance(m, dict):
        add(m.get('default', ''), m.get('provider', ''))

    for prov in config.get('custom_providers', []):
        pname = prov.get('name', '')
        if prov.get('model'):
            add(prov['model'], pname)
        for mid in (prov.get('models') or {}):
            add(mid, pname)

    for pname, prov in config.get('providers', {}).items():
        if isinstance(prov, dict):
            for m_entry in prov.get('models', []):
                mid = m_entry if isinstance(m_entry, str) else m_entry.get('id', m_entry.get('model', ''))
                add(mid, pname)

    for prov in config.get('fallback_providers', []):
        if isinstance(prov, dict):
            add(prov.get('model', ''), prov.get('provider', ''))

    add('hermes-agent', 'hermes-agent')
    p1_count = len(models)
    print(f"Phase 1 (config): {p1_count} models", file=sys.stderr)

    # --- Phase 2: OpenRouter ---
    or_key = read_env_key('OPENROUTER_API_KEY')
    if or_key:
        try:
            data = curl_json(
                'https://openrouter.ai/api/v1/models',
                {'Authorization': f'Bearer {or_key}'}
            )
            added = 0
            for m_entry in data.get('data', []):
                p = m_entry.get('pricing', {})
                pp = float(p.get('prompt', '0') or '0')
                cp = float(p.get('completion', '0') or '0')
                if pp + cp == 0 and m_entry['id'] != 'openrouter/free':
                    add(m_entry['id'], 'openrouter')
                    added += 1
            print(f"Phase 2 (OpenRouter): +{added} free models", file=sys.stderr)
        except Exception as e:
            print(f"Phase 2 (OpenRouter): ERROR - {e}", file=sys.stderr)

    # --- Phase 3: OpenCode Go ---
    go_key = read_env_key('OPENCODE_GO_API_KEY')
    if go_key:
        try:
            data = curl_json(
                'https://opencode.ai/zen/go/v1/models',
                {'Authorization': f'Bearer {go_key}'}
            )
            added = 0
            for m_entry in data.get('data', []):
                add(m_entry['id'], 'opencode-go')
                added += 1
            print(f"Phase 3 (opencode-go): +{added} models", file=sys.stderr)
        except Exception as e:
            print(f"Phase 3 (opencode-go): ERROR - {e}", file=sys.stderr)

    # --- Phase 4: OpenCode Zen ---
    zen_key = read_env_key('OPENCODE_ZEN_API_KEY')
    if zen_key:
        try:
            data = curl_json(
                'https://opencode.ai/zen/v1/models',
                {'Authorization': f'Bearer {zen_key}'}
            )
            added = 0
            for m_entry in data.get('data', []):
                add(m_entry['id'], 'opencode-zen')
                added += 1
            print(f"Phase 4 (opencode-zen): +{added} models", file=sys.stderr)
        except Exception as e:
            print(f"Phase 4 (opencode-zen): ERROR - {e}", file=sys.stderr)

    # --- Phase 5: Google Gemini ---
    google_key = read_env_key('GOOGLE_API_KEY')
    if google_key:
        try:
            data = curl_json(
                f'https://generativelanguage.googleapis.com/v1beta/models?key={google_key}',
                {}
            )
            added = 0
            for m_entry in data.get('models', []):
                name = m_entry.get('name', '')
                if name.startswith('models/'):
                    model_id = name.replace('models/', '')
                    # Skip non-Gemini and deprecated models
                    display = m_entry.get('displayName', '')
                    if 'gemini' in model_id.lower() and 'deprecated' not in display.lower():
                        add(model_id, 'google')
                        added += 1
            print(f"Phase 5 (Google): +{added} models", file=sys.stderr)
        except Exception as e:
            print(f"Phase 5 (Google): ERROR - {e}", file=sys.stderr)

    # --- Save ---
    with open(MODELS_PATH, 'w') as f:
        json.dump(models, f, indent=2)

    providers = {}
    for m_entry in models:
        providers[m_entry['provider']] = providers.get(m_entry['provider'], 0) + 1
    print(f"\nSaved {len(models)} models across {len(providers)} providers:", file=sys.stderr)
    for p, c in sorted(providers.items()):
        print(f"  {p}: {c}", file=sys.stderr)


if __name__ == '__main__':
    main()

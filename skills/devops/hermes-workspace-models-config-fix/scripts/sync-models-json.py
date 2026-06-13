#!/usr/bin/env python3
"""Sync ~/.hermes/models.json from config.yaml, OpenRouter, OpenCode Zen, and OpenCode Go.

Idempotent — safe to re-run. Sources with missing API keys are silently skipped.
The workspace reads models.json on its /api/models route.
Run after adding/removing provider keys or changing models via /model in CLI.
Restart workspace after: systemctl --user restart hermes-workspace
"""

import json, os, urllib.request, urllib.error, yaml, sys
from pathlib import Path

HERMES_HOME = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes')))
MODELS_JSON = HERMES_HOME / 'models.json'
CONFIG_YAML = HERMES_HOME / 'config.yaml'
ENV_FILE = HERMES_HOME / '.env'


def load_env():
    """Read KEY=VALUE from .env file."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def load_config():
    """Load config.yaml."""
    with open(CONFIG_YAML) as f:
        return yaml.safe_load(f)


def fetch_json(url, api_key=None, timeout=15):
    """Fetch JSON from URL, optionally with Bearer auth."""
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        print(f'  [skip] {url}: {e}', file=sys.stderr)
        return None


def collect_models():
    """Collect all models from all sources."""
    models = []
    seen = set()

    def add(model_id, provider):
        key = f'{provider}:{model_id}'
        if key not in seen:
            seen.add(key)
            models.append({'model': model_id, 'provider': provider})

    # ── 1. config.yaml ──
    try:
        config = load_config()

        # Default model
        m = config.get('model', {})
        if isinstance(m, dict) and m.get('default'):
            add(m['default'], m.get('provider', ''))

        # Custom providers (list of dicts)
        for prov in config.get('custom_providers', []):
            pname = prov.get('name', '')
            if prov.get('model'):
                add(prov['model'], pname)
            for mid in (prov.get('models') or {}):
                add(mid, pname)

        # Providers section
        for pname, prov in config.get('providers', {}).items():
            if isinstance(prov, dict):
                for m in prov.get('models', []):
                    if isinstance(m, str):
                        add(m, pname)
                    elif isinstance(m, dict):
                        add(m.get('id', m.get('model', '')), pname)

        # Fallback providers
        for prov in config.get('fallback_providers', []):
            if isinstance(prov, dict) and prov.get('model'):
                add(prov['model'], prov.get('provider', ''))

        # hermes-agent placeholder
        add('hermes-agent', 'hermes-agent')
        print(f'  config.yaml: {len([m for m in models if m["provider"] in [p.get("name","") for p in config.get("custom_providers",[])] or m["provider"] in config.get("providers",{})])} models')
    except Exception as e:
        print(f'  config.yaml: error — {e}', file=sys.stderr)

    # ── 2. OpenRouter free models ──
    env = load_env()
    or_key = env.get('OPENROUTER_API_KEY')
    if or_key:
        data = fetch_json('https://openrouter.ai/api/v1/models', api_key=or_key)
        if data:
            count = 0
            for m in data.get('data', []):
                pricing = m.get('pricing', {})
                prompt_p = float(str(pricing.get('prompt', '0')).replace("'", ''))
                comp_p = float(str(pricing.get('completion', '0')).replace("'", ''))
                if (prompt_p + comp_p) == 0 and m['id'] != 'openrouter/free':
                    add(m['id'], 'openrouter')
                    count += 1
            # Also add owl-alpha (beta, free)
            for m in data.get('data', []):
                if 'owl-alpha' in m.get('id', ''):
                    add(m['id'], 'openrouter')
                    count += 1
            print(f'  OpenRouter: {count} free models')
    else:
        print('  OpenRouter: skipped (no API key)')

    # ── 3. OpenCode Go ──
    go_key = env.get('OPENCODE_GO_API_KEY')
    if go_key:
        data = fetch_json('https://opencode.ai/zen/go/v1/models', api_key=go_key)
        if data:
            count = 0
            for m in data.get('data', []):
                add(m['id'], 'opencode-go')
                count += 1
            print(f'  OpenCode Go: {count} models')
    else:
        print('  OpenCode Go: skipped (no API key)')

    # ── 4. OpenCode Zen ──
    zen_key = env.get('OPENCODE_ZEN_API_KEY')
    if zen_key:
        data = fetch_json('https://opencode.ai/zen/v1/models', api_key=zen_key)
        if data:
            count = 0
            for m in data.get('data', []):
                add(m['id'], 'opencode-zen')
                count += 1
            print(f'  OpenCode Zen: {count} models')
    else:
        print('  OpenCode Zen: skipped (no API key)')

    return models


if __name__ == '__main__':
    print('Syncing models.json from all sources...')
    models = collect_models()
    MODELS_JSON.write_text(json.dumps(models, indent=2))
    print(f'Wrote {len(models)} models to {MODELS_JSON}')

    # Show breakdown
    from collections import Counter
    for p, c in sorted(Counter(m['provider'] for m in models).items()):
        print(f'  {p:20s} {c}')

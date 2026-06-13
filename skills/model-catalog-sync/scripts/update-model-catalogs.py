#!/usr/bin/env python3
"""
update-model-catalogs.py
Fetches current model lists from all configured providers and updates:
1. ~/.hermes/config.yaml — Hermes agent provider model lists
2. ~/.config/opencode/opencode.json — OpenCode CLI provider/model config

Designed to run weekly via cron (model-catalog-weekly job).
Can also be run manually: python3 ~/.hermes/scripts/update-model-catalogs.py
"""
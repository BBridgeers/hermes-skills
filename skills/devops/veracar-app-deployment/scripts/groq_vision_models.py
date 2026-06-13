#!/usr/bin/env python3
"""
Groq Vision Models — Live Query
===============================
Fetches the current list of native Groq vision-capable models.
Use this to discover available models before configuring them.
Requires: pip install groq
"""

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

models_list = client.models.list()

print("--- Active NATIVE Groq Vision Models ---")
for model in models_list.data:
    model_id = model.id.lower()
    if "vision" in model_id or "-vl" in model_id:
        print(f"Model ID: {model.id}")
        print(f"Owned By: {model.owned_by}\n")

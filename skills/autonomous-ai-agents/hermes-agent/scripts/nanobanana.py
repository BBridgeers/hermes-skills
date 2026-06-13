#!/usr/bin/env python3
"""Nano Banana Pro — Imagen 4.0 image gen via Vertex AI.
Requires: gcloud auth login, google-cloud-aiplatform, Pillow.
Usage: python3 nanobanana.py 'prompt' [1:1|16:9|9:16]
Outputs: MEDIA:/path/to/image.png + file path.
"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

def generate(prompt, aspect="1:1"):
    vertexai.init(project="hermes-resource-project")
    model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-001")
    images = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio=aspect,
        safety_filter_level="block_some",
        person_generation="allow_adult",
    )
    saved = []
    out_dir = os.path.expanduser("~/.hermes/nanobanana")
    os.makedirs(out_dir, exist_ok=True)
    for i, img in enumerate(images):
        ts = int(time.time())
        fpath = os.path.join(out_dir, f"nbp_{ts}_{i}.png")
        img.save(fpath)
        saved.append(fpath)
        print(f"MEDIA:{fpath}")
    return saved

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "a beautiful sunset"
    a = sys.argv[2] if len(sys.argv) > 2 else "1:1"
    images = generate(p, a)
    for img in images:
        print(img)

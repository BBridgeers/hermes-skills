---
name: design-asset-gen
description: Industry-aware image generation prompts for DFW clients — hero images, section imagery, and presentation mockups.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Images, AI, Prompts, Design]
    related_skills: [dfw-web-design-now, build-executor]
---

# Design Asset Generation

Generate on-brand images for DFW client builds using `imagen3-mcp` and `openai-gpt-image-mcp`.

## Pattern
Each DFW niche has visual clichés that convert. Use proven prompt patterns instead of reinventing them per client.

## Protocol

1. **Identify asset need**
   - Hero image, service section image, testimonial background, icon set, etc.
2. **Select prompt template**

| Niche | Template |
|---|---|
| HVAC | "Professional HVAC technician in a clean uniform servicing a modern residential AC unit in a bright garage, soft natural light, trustworthy, high detail" |
| Plumbing | "Friendly plumber fixing a kitchen sink under cabinet lighting, clean modern home, professional tools, reassuring expression" |
| Med Spa | "Luxurious med spa treatment room, soft neutral tones, woman relaxing during facial, calm and premium atmosphere" |
| Legal | "Confident attorney at a modern desk reviewing documents, clean office, professional portrait, warm lighting" |

3. **Generate**
   - Call `imagen3-mcp` for photorealistic assets.
   - Call `openai-gpt-image-mcp` for edits/variations.
4. **Validate**
   - Download and inspect resolution.
   - Run through `browser_harness` if used as hero to verify composition.
5. **Store**
   - Save to `/root/.dfw/assets/<client>/` with descriptive filenames.
   - Record in client-data deliverables.

## Failure Modes
- Generic prompts produce stock-looking images.
- Not checking license/usage rights per provider.
- Using generated faces of real people without disclosure.

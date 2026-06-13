# Model Shootout — May 21, 2026

Three models evaluated on identical Section 5.1 (Herxheimer Survival Algorithm) prompts with identical skills and constraints.

## DeepSeek V4 Pro (Native API)
- 175 lines, 5,976 words, 43,791 bytes
- 5 Hard Gates, 30+ named enzymes, 8 cross-references
- ASCII decision tree, 5-column Phase Risk table, 9-symptom companion table
- Clinical vignette: triple-hit cascade, 11-day ICU
- Bridge Box: building demolition / dust cloud metaphor
- **Verdict: World-class. Full Pillar 6 density.**

## DeepSeek V4 Pro (Ollama Cloud — both Kimi and GLM fell back to this)
- 175 lines, 5,976 words, 43,791 bytes (identical hash to native)
- 3 Hard Gates, 40 named enzyme hits across 20 terms
- Both Kimi and GLM-5.1 hit HTTP 401 and fell back to deepseek-v4-pro on Ollama Cloud
- Ollama Cloud version produces identical output to native for this task
- **Note: Earlier test (Sections 8-10) showed 41% fewer words from Ollama DeepSeek vs native. Quality difference may be task-REDACTED.**

## Kimi K2.6 (second attempt, unique output path)
- 169 lines, 3,817 words, 27,972 bytes
- All quality markers present: Bridge Box, Hard Gates, Decision Tree, Companion Table
- 36% fewer words than DeepSeek native
- Named enzymes present but fewer distinct mechanisms
- **Verdict: Viable for volume tasks, inferior for voice-critical narrative.**

## GLM-5.1 (second attempt, unique output path)
- 186 lines, 4,236 words, 29,612 bytes (identical to Kimi fallback output)
- May have also fallen back to deepseek-v4-pro — needs verification
- **Verdict: Unreliable as primary model for narrative content. Retire to operational templates only.**

## Production Recommendation
- **DeepSeek V4 Pro native API** for all voice-critical, safety-sensitive, mechanism-dense content
- **Kimi K2.6** for high-volume template-driven mechanical tasks (Agent Encyclopedia)
- **GLM-5.1** retired from narrative content; viable for operational templates only
- **Run sequentially** to avoid API concurrency — one batch at a time with dedicated keys
# Qwen 3.7 Max vs DeepSeek V4 Pro — Benchmark Comparison

Data source: Qwen official blog (qwen.ai/blog?id=qwen3.7, 2026-05-20).
Same harness, same judge for all benchmarks — directly comparable.

## Head-to-Head Scorecard

### Coding Agent
| Benchmark | Qwen 3.7 Max | DS V4 Pro Max | Delta |
|---|---|---|---|
| Terminal-Bench 2.0 | 69.7 | 67.9 | +1.8 Qwen |
| SWE-Bench Verified | 80.4 | 80.6 | +0.2 DS |
| SWE-Bench Pro | 60.6 | 59.0 | +1.6 Qwen |
| SWE-Multilingual | 78.3 | 76.2 | +2.1 Qwen |
| NL2repo | 47.2 | 35.5 | +11.7 Qwen |
| Kernel Bench L3 (speedup) | 1.98x | 1.07x | 85% faster |
| Kernel Bench L3 (win rate) | 96% | 54% | +42pp Qwen |

### General Agent / Tool Use
| Benchmark | Qwen 3.7 Max | DS V4 Pro Max | Delta |
|---|---|---|---|
| MCP-Mark | 60.8 | 57.1 | +3.7 Qwen |
| MCP-Atlas | 76.4 | 73.6 | +2.8 Qwen |
| SkillsBench | 59.2 | 52.3 | +6.9 Qwen |
| BFCL-V4 | 75.0 | 70.6 | +4.4 Qwen |
| Qwenclaw | 64.3 | 59.2 | +5.1 Qwen |
| ClawEval | 65.2 | 58.4 | +6.8 Qwen |
| SpreadSheetBench | 87.0 | 84.9 | +2.1 Qwen |

### Reasoning
| Benchmark | Qwen 3.7 Max | DS V4 Pro Max | Delta |
|---|---|---|---|
| GPQA Diamond | 92.4 | 90.1 | +2.3 Qwen |
| HLE | 41.4 | 37.7 | +3.7 Qwen |
| LiveCodeBench | 91.6 | 93.5 | +1.9 DS |
| HMMT 2026 Feb | 97.1 | 95.2 | +1.9 Qwen |
| Apex | 44.5 | 38.3 | +6.2 Qwen |

### General / Multilingual
| Benchmark | Qwen 3.7 Max | DS V4 Pro Max | Delta |
|---|---|---|---|
| MMLU-Pro | 89.6 | 87.5 | +2.1 Qwen |
| IFBench | 79.1 | 77.0 | +2.1 Qwen |
| WMT24++ | 85.8 | 82.2 | +3.6 Qwen |

## Final Tally: Qwen 23 - DeepSeek 3

Qwen dominates agentic benchmarks by wide margins (+5-12 points on SkillsBench, ClawEval, NL2repo). 
DS edges ahead on LiveCodeBench (+1.9) and SWE-Verified (+0.2) but both are narrow.

Kernel Bench L3 is the most dramatic: Qwen runs 85% faster and succeeds 96% of the time vs DS at 54%.

## Pricing Context
- Qwen 3.7 Max (OR): $1.25/$3.75 per 1M
- DS V4 Pro: $1.74/$3.48 per 1M
- Qwen cheaper on input, DS slightly cheaper on output
- DS is open-weight (MIT), Qwen is closed-weight (API only)

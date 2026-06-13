#!/usr/bin/env python3
"""
Deep Research Runner — Perplexity sonar-deep-research engine.

Performs high-volume (100-200KB+), multi-pass technical inquiries with
iterative gap analysis. Each pass identifies missing research dimensions
and explicitly targets them in the next expansion.

Usage:
    deep_research.py --prompt research_prompt.txt --output report.md
    deep_research.py --prompt prompt.txt --output report.md --target-kb 150 --max-passes 20

Requires: requests, PERPLEXITY_API_KEY in environment (or --api-key flag).
"""

import argparse
import json
import os
import sys
import time
import requests

# ── Constants ──────────────────────────────────────────────────────
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar-deep-research"
DEFAULT_TARGET_KB = 100
DEFAULT_MAX_CONTINUATIONS = 30
DEFAULT_TEMPERATURE = 0.15

SYSTEM_PROMPT_TEMPLATE = """You are performing a high-volume, exhaustive technical deep inquiry.
STRICT RULES:
1. PRODUCE MAXIMUM OUTPUT. Target is {target_kb}KB.
2. Use markdown headers (##, ###), tables for comparisons, and detailed bullet lists.
3. Include citations with specific references wherever possible.
4. Never summarize — always expand and elaborate.
5. If a section feels complete, find a NEW angle (edge cases, alternative approaches, historical context, long-term risks)."""


# ── Helpers ─────────────────────────────────────────────────────────

def read_file(path):
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def stream_request(messages, output_path=None, timeout=1200):
    """Stream a Perplexity completion. If output_path is given, append live."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": DEFAULT_TEMPERATURE,
        "stream": True,
        "return_citations": True,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=headers,
                             stream=True, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"\n[FAIL] API error: {e}", file=sys.stderr)
        return None

    chunks = []
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        data_str = line[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
            text = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if text:
                sys.stdout.write(text)
                sys.stdout.flush()
                if output_path:
                    with open(output_path, "a", encoding="utf-8") as f:
                        f.write(text)
                chunks.append(text)
        except (json.JSONDecodeError, KeyError):
            pass
    return "".join(chunks)


def identify_gaps(current_text):
    """Run a small gap-analysis completion to find missing research dimensions."""
    print("\n\n[GAP ANALYSIS] Scanning for missing dimensions...\n", file=sys.stderr)

    tail = current_text[-8000:]  # last ~8K chars for context

    gap_prompt = f"""Review the following research snippet.
Identify exactly 3-5 critical technical gaps, missing inquiry perspectives,
or unexplored domains that would strengthen this investigation.

FORMAT: Return ONLY a bulleted list (one gap per line, starting with -).

RESEARCH SNIPPET:
{tail}"""

    messages = [
        {"role": "system", "content": "You are a senior gap-analysis consultant. Be specific and technical."},
        {"role": "user", "content": gap_prompt},
    ]

    payload = {
        "model": "sonar",
        "messages": messages,
        "temperature": 0.1,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        gaps = data["choices"][0]["message"]["content"]
        print(f"{gaps}\n", file=sys.stderr)
        return gaps
    except Exception as e:
        print(f"[GAP ANALYSIS FAILED] {e}", file=sys.stderr)
        return "Continue expanding the analysis with additional technical depth and alternative perspectives."


# ── Main Research Loop ──────────────────────────────────────────────

def run_research(prompt_file, output_file, target_kb, max_continuations):
    print(f"\n═══ DEEP INQUIRY INITIATED ═══", file=sys.stderr)
    print(f"  Prompt:   {prompt_file}", file=sys.stderr)
    print(f"  Output:   {output_file}", file=sys.stderr)
    print(f"  Target:   {target_kb} KB", file=sys.stderr)
    print(f"  Model:    {MODEL}", file=sys.stderr)
    print(f"  Max passes: {max_continuations}", file=sys.stderr)
    print(f"═══════════════════════════════════\n", file=sys.stderr)

    # Initialize output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Deep Inquiry Report\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target: {target_kb} KB  |  Model: {MODEL}\n\n---\n\n")

    prompt_text = read_file(prompt_file)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(target_kb=target_kb)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_text},
    ]

    # ── Pass 1: Initial deep inquiry ──
    print("[PASS 1/initial] Streaming deep research...\n", file=sys.stderr)
    result = stream_request(messages, output_path=output_file)
    if not result:
        print("[FATAL] Initial pass returned no content.", file=sys.stderr)
        sys.exit(1)

    size_kb = len(result.encode("utf-8")) / 1024
    print(f"\n\n[PASS 1 DONE]  {size_kb:.1f} KB", file=sys.stderr)

    # ── Expansion passes with gap analysis ──
    count = 0
    while size_kb < target_kb and count < max_continuations:
        count += 1
        print(f"\n{'─' * 60}", file=sys.stderr)
        print(f"[PASS {count + 1}/expansion]  Current: {size_kb:.1f} KB  |  Target: {target_kb} KB", file=sys.stderr)

        # Identify gaps
        gaps = identify_gaps(result)

        # Build expansion prompt
        tail = result[-4000:]
        expansion_prompt = f"""You are continuing a deep research task.
Current size: {size_kb:.1f} KB.  Target: {target_kb} KB.

GAPS IDENTIFIED that need to be filled:
{gaps}

TASK: Fill these gaps by adding NEW subsections with detailed analysis.
Target an additional 10-20 KB of high-density content in this pass.
Do NOT repeat what has already been covered.

PICK UP FROM HERE:
{tail}"""

        cont_messages = list(messages)
        cont_messages.append({"role": "assistant", "content": tail})
        cont_messages.append({"role": "user", "content": expansion_prompt})

        print(f"[RESEARCHING GAPS] Streaming expansion...\n", file=sys.stderr)
        chunk = stream_request(cont_messages, output_path=output_file)
        if not chunk:
            print("[WARN] Expansion pass returned no content — stopping.", file=sys.stderr)
            break

        result += "\n\n" + chunk
        size_kb = len(result.encode("utf-8")) / 1024
        print(f"\n[PASS {count + 1} DONE]  {size_kb:.1f} KB", file=sys.stderr)

    # ── Footer ──
    footer = f"\n\n---\n*Report completed at {time.strftime('%Y-%m-%d %H:%M:%S')}  |  Final size: {size_kb:.1f} KB across {count + 1} passes.*\n"
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(footer)

    print(f"\n{'═' * 60}", file=sys.stderr)
    print(f"INQUIRY COMPLETE", file=sys.stderr)
    print(f"  Final size:  {size_kb:.1f} KB", file=sys.stderr)
    print(f"  Total passes: {count + 1}", file=sys.stderr)
    print(f"  Output:      {output_file}", file=sys.stderr)
    print(f"{'═' * 60}\n", file=sys.stderr)


# ── CLI Entry Point ─────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perplexity Deep Research — high-volume iterative inquiry with gap analysis."
    )
    parser.add_argument("--prompt", "-p", required=True,
                        help="Path to the research prompt file (see templates/research_prompt.txt)")
    parser.add_argument("--output", "-o", required=True,
                        help="Path for the output markdown report")
    parser.add_argument("--target-kb", "-k", type=int, default=DEFAULT_TARGET_KB,
                        help=f"Target minimum output size in KB (default: {DEFAULT_TARGET_KB})")
    parser.add_argument("--max-passes", "-n", type=int, default=DEFAULT_MAX_CONTINUATIONS,
                        help=f"Maximum expansion passes (default: {DEFAULT_MAX_CONTINUATIONS})")
    parser.add_argument("--api-key", default=None,
                        help="Perplexity API key (overrides PERPLEXITY_API_KEY env var)")
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE,
                        help=f"Temperature for generation (default: {DEFAULT_TEMPERATURE})")

    args = parser.parse_args()

    # Resolve API key
    API_KEY = args.api_key or os.getenv("PERPLEXITY_API_KEY")
    if not API_KEY:
        print("[ERROR] No Perplexity API key found.", file=sys.stderr)
        print("  Set PERPLEXITY_API_KEY env var or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    # Override temperature if set
    if args.temperature != DEFAULT_TEMPERATURE:
        DEFAULT_TEMPERATURE = args.temperature

    run_research(
        prompt_file=args.prompt,
        output_file=args.output,
        target_kb=args.target_kb,
        max_continuations=args.max_passes,
    )

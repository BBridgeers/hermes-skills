# Deep Scan Methodology for External Skill Repos

## Problem

The standard `skill-security-scan` regex patterns produce massive false positives when scanning documentation-heavy repos. Words like "token", "secret", "credential", "API key", and "system prompt" appear routinely in URLs, code examples, and explanatory text — triggering 30+ "CRITICAL" findings that are actually just documentation.

**Real-world example (2026-05-22):** Scanning 3 public skill repos (~6,000 files) produced 48 findings. All 48 were false positives — documentation text, not payloads. The patterns matched:
- URLs like `https://platform.claude.com/docs/en/build-with-claude/token-counting.md`
- Explanatory text like "system prompt frozen" or "fetches the credential"
- Markdown links containing `api_key` or `secret` in the path
- The word "token" in 30 different documentation contexts

## Two-Pass Approach

### Pass 1: Broad Regex (existing `scan.sh`)

Run the standard scanner first. Expect 30-100+ hits on large repos. All findings at this stage are **candidates**, not confirmed threats.

### Pass 2: Targeted Deep Scan (REAL threat patterns only)

After broad scan, follow up with a Python script using **narrow, payload-specific patterns** that won't match documentation text:

```python
REAL_THREATS = {
    "CRITICAL": [
        # Actual prompt injection — directive telling reader to disregard instructions
        (r'(?im)^(Ignore|Disregard|Override|Forget)\s+(all|everything|your).*?(instructions|rules|guidelines|system prompt)', "PROMPT_OVERRIDE"),
        # Jailbreak persona assignments
        (r'(?i)you\s+are\s+now\s+(DAN|jailbroken|unshackled|evil|malicious)', "JAILBREAK"),
        # Actual secret exfiltration: curl/wget sending env vars to external URLs
        (r'(?i)(curl|wget|fetch|http\.post).*?[\"\`]\$?(API_KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|\.env).*?(http|https)://', "ACTUAL_SECRET_EXFIL"),
        # Zero-width Unicode obfuscation
        (r'[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u2064]', "ZERO_WIDTH"),
    ],
    "HIGH": [
        # Shell injection inside code blocks meant for execution
        (r'```(?:bash|sh|shell)\s*\n.*?(?:rm\s+-rf\s+/|curl.*?\|.*?sh|eval\s+\$)', "SHELL_INJECTION"),
        # Base64 decode piped to shell
        (r'(?:base64|openssl\s+base64).*?(?:-d|decode).*?\|\s*(?:ba)?sh', "BASE64_TO_SHELL"),
    ],
}
```

## False Positive Categories to Recognize

When Pass 1 hits on these patterns, they are almost certainly documentation, not payloads:

| Pass 1 Pattern | Why It Fires | Verdict |
|---|---|---|
| `SECRET_EXFIL` on URLs | Links contain "token", "secret", "api_key" | **False positive** — check if it's a URL or code example |
| `SYSTEM_PROMPT_FORGERY` | "system prompt" in explanatory text | **False positive** — check if it's describing how prompts work |
| `PATH_TRAVERSAL` on `../../` | Example paths in READMEs | **False positive** — check if it's a usage example |
| `FORCE_PUSH` on `git push --force` | Documented git commands | **False positive** — check if it's instruction or example |

## Decision Flow

```
Pass 1 hit → Is it inside a code fence? → Downgrade severity
           → Is it a URL or link text? → Almost certainly false positive
           → Is it describing how a feature works? → False positive  
           → Is it an actual directive telling the agent to do something malicious? → REAL THREAT
```

## Key Principle

**A scanner hit is a candidate, not a vulnerability.** Read the surrounding 30-50 lines before filing anything. If you can't describe concretely what an attacker achieves, it's not a finding.

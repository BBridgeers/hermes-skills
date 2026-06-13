# Pitfall: Incomplete Security Fix Re-Fires

> When a security-block issue (ISS-N) is "resolved" but re-fires days/weeks later under a new issue ID, the original fix was incomplete. The most common cause: patching only the primary/happy-path code but missing fallback sections, alternate branches, or commented-out backup commands.

## Recognition Signal

- An issue was marked resolved (e.g., ISS-001 on 2026-05-29)
- Days later, the same threat pattern fires on the same skill (ISS-003 on 2026-06-01)
- The error message is identical — same `threat pattern`, same skill
- The fix PR exists but the cron job keeps failing

## Root Cause Pattern

The fix addressed the **first occurrence** of the pattern (e.g., the main `gh pr create` flow) but missed a **fallback/alternate path** (e.g., the raw `curl` fallback for when `gh` CLI is unavailable). Skills often have 2-3 ways to accomplish the same thing:

1. **Primary path** — what the skill recommends first
2. **Fallback path** — "if X is unavailable, do Y instead"
3. **Documented warning** — "when configuring cron jobs, avoid Z"

A fix that only addresses path #1 will re-fire when the cron job's assembled prompt hits path #2.

## Fix Protocol

When a security block re-fires after a claimed resolution:

1. **Re-read the entire SKILL.md** — do not trust that the prior fix was complete
2. **Search for ALL instances** of the threat pattern, not just the section that was patched
3. **Check fallback sections specifically** — look for "If X is unavailable," "fallback," "alternatively," "you can also," etc.
4. **Check any code blocks** containing `curl`, `Authorization`, `Bearer`, `token`, or shell variable extraction from env files
5. **Verify with `grep`** after patching — confirm zero actual instances remain (warning text about the pattern is fine; executable commands are not)

## Real Example: ISS-001 → ISS-003 → ISS-003 (re-fire)

- **ISS-001** (2026-05-29): `external-feature` blocked by `exfil_curl_auth_header` → fix patched the main `gh pr create` section and added `references/tirith-safe-http.md`
- **ISS-003** (2026-06-01): Same skill, same threat pattern, still failing → the curl+auth fallback at lines 123-138 was never touched
- **ISS-003 fix** (2026-06-09): Replaced `curl -H "Authorization: token $GITHUB_TOKEN"` with `gh api` in the fallback section too
- **ISS-003 re-fire** (2026-06-13): STILL failing — the fix replaced code blocks but missed that `tirith-safe-http.md` itself contained 3 instances of the trigger text (`curl` + `Authorization` + `auth-header`) in its own documentation, and SKILL.md line 201 had 1 more. The reference file created to document safe practices was itself the anti-pattern.
- **Root cause fix** (2026-06-13): Rewrote all documentation to use categorical language ("credential-bearing shell commands") without naming the specific `tool+flag` combination the scanner matches. Added anti-pattern rule: never name the exact trigger text in docs.
- **Lesson**: Scan the WHOLE skill directory, not just code blocks. Documentation ABOUT a security fix can contain the very patterns it warns about. Reference files, guidelines sections, and warning text are all part of the assembled cron prompt and subject to the same scanner.

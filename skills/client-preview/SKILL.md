---
name: client-preview
description: Auto-deploy DFW spec builds to a shareable preview URL and format the client review email.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Preview, Deploy, Client, Review]
    related_skills: [dfw-web-design-now, build-executor, cloudflare-deploy]
---

# Client Preview

Give clients a fast, shareable preview of their spec build.

## Pattern
After the build phase passes QA, deploy to a preview environment and send a review email with the URL, what to look at, and next steps.

## Protocol

1. **Choose preview host**
   - Primary: `edgeone-pages-mcp` (instant public URL).
   - Fallback: Cloudflare Pages preview branch.
2. **Deploy**
   - Upload `dist/` directory.
   - Capture returned public URL.
3. **Capture screenshot**
   - Use `browser_harness` to screenshot homepage + one interior page.
4. **Format review email**
   - Subject: `<Client> — your site preview is ready`
   - Body: URL, 3 things to review, revision policy, deadline for feedback.
5. **Send**
   - Send via email or Slack.
   - Record in `client-data` communications table.
6. **Await feedback**
   - Set Taskwarrior task due date based on feedback window.

## Email Template
```
Hi <Client>,

Your preview is live: <URL>

Please focus on:
1. Homepage headline and imagery
2. Services section
3. Contact form / CTA

Revisions are included per our proposal. Please send consolidated feedback by <date>.

Best,
Blake / DFW Web Design NOW
```

## Failure Modes
- Preview URL not tested before sending.
- Missing mobile screenshot.
- No feedback deadline, causing drift.

# Email Monitoring for LinkedIn & Job Applications

## Problem
LinkedIn has no public message API for personal accounts. Recruiters send InMail/messages that arrive as email notifications. Missing these = lost opportunities.

## Universal Pattern

```
LinkedIn Message → Email Notification → Monitoring Inbox → Agent Alert → Respond
```

## Inbox Options (ranked by setup speed)

### 1. AgentMail (fastest — 2 min)
- Sign up at https://console.agentmail.to
- Create or use existing inbox (e.g., `dfwwebdesignnow@agentmail.to`)
- Set up auto-forwarding rule in your primary email to forward all LinkedIn notifications to the AgentMail address
- Poll via REST API: `GET https://api.agentmail.to/v0/inboxes/{inbox_id}/messages` with Bearer token
- Cron job polls every 5 minutes
- No OAuth, no IMAP, no app passwords

### 2. Gmail API via OAuth (reliable — 15 min)
- Use `google-workspace` skill
- Requires `client_secret.json` from Google Cloud Console
- Supports labels, search operators (`from:linkedin.com`, `is:unread`)
- Good for deep search/filtering

### 3. Himalaya IMAP (hit or miss)
- Gmail: works with app password
- Outlook.com: **DOES NOT WORK** — Microsoft blocks basic auth on consumer accounts, even with app passwords

## LinkedIn Notification Email Patterns

LinkedIn sends from addresses like:
- `messages-noreply@linkedin.com`
- `notifications-noreply@linkedin.com`
- Subject lines: "You have a new message from [Name]", "[Name] sent you a message"

## Cron Job Setup

```bash
# Poll AgentMail every 5 minutes for new LinkedIn messages
# If new messages detected, alert via Slack/WebUI
```

Priority keywords to detect: "new message", "sent you a message", "InMail", "recruiter", "opportunity", "interview"

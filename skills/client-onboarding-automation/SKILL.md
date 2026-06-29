---
name: client-onboarding-automation
description: Trigger sequences for new DFW client intake via Pipedream automations.
version: 1.0.0
author: Hermes Agent
last-updated: 2026-06-29
metadata:
  hermes:
    tags: [DFW, Onboarding, Automation, Pipedream]
    related_skills: [dfw-web-design-now, client-data, project-tracker]
---

# Client Onboarding Automation

Automate the post-sale intake sequence: CRM update, invoice, welcome email, kickoff task.

## Pattern
When a DFW client signs, a predictable sequence must fire. Pipedream connects the tools so Hermes only triggers the workflow.

## Protocol

1. **Trigger**
   - Hermes calls Pipedream webhook when proposal status = 'accepted'.
   - Payload: client name, email, niche, project type, amount.
2. **Pipedream workflow steps**
   - Update CRM (Airtable / Notion / Google Sheets).
   - Create invoice (Stripe / Wave / QuickBooks).
   - Send welcome email from Blake.
   - Post kickoff task to Slack / Taskwarrior.
3. **Hermes confirms**
   - Poll Pipedream execution log for success.
   - Record each step outcome in `client-data`.
4. **Create project tracker tasks**
   - Use `project-tracker` to create discovery task.
5. **Send personal kickoff**
   - Blake sends short personal welcome (not fully automated).

## Webhook Payload
```json
{
  "client": "Acme HVAC",
  "email": "owner@acmehvac.com",
  "niche": "hvac",
  "project_type": "track_a",
  "amount": "$2,400",
  "proposal_id": 42
}
```

## Failure Modes
- Webhook not idempotent → duplicate invoices.
- Not verifying Pipedream execution before telling client they're onboarded.
- Skipping personal kickoff, making the process feel robotic.

# SOP: Cloudflare Domain Transfer — Internal Operator Guide
**Version:** 1.0  
**Owner:** DFW Web Design NOW  
**Applies to:** All spec-build and custom-build site deliveries where client purchases or already owns a domain  
**Stack:** Cloudflare Pages (deployment) + Cloudflare Registrar (domain management)

---

## Overview

When a client buys a spec-build site (or any delivered project), one of three domain scenarios applies:

| Scenario | Description | Who Acts |
|----------|-------------|----------|
| **A** | Client already has a domain at Cloudflare | Client — minimal work |
| **B** | Client has a domain at another registrar (GoDaddy, Namecheap, etc.) | Client initiates transfer; you guide |
| **C** | Client has no domain — you register it on their behalf at Cloudflare | You register, then transfer ownership |

This SOP covers all three. **Most DFW spec-build sales will be Scenario B or C.**

---

## Pre-Transfer Checklist (Before Any Call)

- [ ] Confirm client's current registrar (ask in onboarding form or first message)
- [ ] Confirm domain name is agreed upon and available
- [ ] Confirm client has a Cloudflare account (or create one with them on call)
- [ ] Confirm billing is settled — **do not initiate transfer before payment clears**
- [ ] Note domain expiry date — Cloudflare blocks transfers on domains expiring within 15 days
- [ ] Confirm domain has been registered for **60+ days** (ICANN lock rule)

---

## Scenario A: Client Domain Already at Cloudflare

**Estimated time: 15–30 minutes**

### Step 1 — Client Adds You as Zone Editor
1. Client logs into [dash.cloudflare.com](https://dash.cloudflare.com)
2. Navigates to their domain → **Manage Domain** → **Members**
3. Invites your Cloudflare account email with **Zone Editor** role
4. You accept the invite

### Step 2 — Connect Site to Their Domain
1. In your Cloudflare Pages project, go to **Settings → Custom Domains**
2. Click **Set up a custom domain** → enter their domain (e.g., `clientbusiness.com`)
3. Cloudflare will automatically add the required CNAME/DNS record if both accounts are on Cloudflare
4. SSL auto-provisions — verify green padlock within 5 minutes

### Step 3 — Transfer Zone Ownership (Optional, for Full Handoff)
If the client wants full ownership of the Pages project:
1. In your Cloudflare dashboard, go to **Workers & Pages → [Project] → Settings**
2. Use **Transfer Project** to move it to their Cloudflare account
3. Confirm Pages deployment still live post-transfer
4. Remove your own Zone Editor access

---

## Scenario B: Client Domain at Another Registrar

**Estimated time: 2–7 days (ICANN transfer window)**

### Phase 1 — Prepare Domain at Current Registrar (Client Action)

> Send client the External Explainer doc — they handle this phase

1. Client unlocks the domain at their current registrar
   - GoDaddy: Domain Settings → scroll to **Domain Lock** → toggle off
   - Namecheap: Domain List → Manage → **Transfer Lock** → disable
2. Client disables **WHOIS Privacy** temporarily (required for some registrars)
3. Client requests the **EPP/Authorization Code** from their registrar (also called Auth Code or Transfer Key)
   - GoDaddy: sends via email automatically when domain is unlocked
   - Namecheap: Domain List → Manage → **Auth Code** → Send by Email
4. Client emails you the Auth Code

> ⚠️ **Security note:** Auth codes expire in 7–30 days depending on registrar. Begin transfer immediately upon receipt.

### Phase 2 — Initiate Transfer at Cloudflare Registrar

> You handle this phase, or walk client through it on screenshare

1. Log into [dash.cloudflare.com](https://dash.cloudflare.com) → **Domain Registration → Transfer Domains**
2. Enter the domain name → click **Confirm it's unlocked**
3. Enter the EPP/Auth Code
4. Cloudflare shows a price (typically $8–$15/year depending on TLD) — confirm with client before proceeding
5. Add payment method → submit transfer
6. Cloudflare sends a **verification email** to the domain's registrant email — client must click **Approve Transfer**
7. Transfer window: **5–7 business days** (often faster, sometimes 1–2 days)

### Phase 3 — Post-Transfer DNS Setup

Once transfer completes and domain shows **Active** in Cloudflare:
1. Go to **DNS → Records** — verify existing records migrated (Cloudflare usually imports them automatically)
2. Add/update the CNAME or A record pointing to your Pages project:
   - `CNAME @ [your-pages-project].pages.dev` (or root domain proxy)
   - `CNAME www [your-pages-project].pages.dev`
3. In Pages project → **Custom Domains** → add domain → verify
4. SSL auto-provisions (Universal SSL) — active within minutes
5. Test both `https://clientbusiness.com` and `https://www.clientbusiness.com`

---

## Scenario C: You Register Domain on Client's Behalf

**Estimated time: 1–2 hours for full setup**

> Use this when client has no domain or wants you to handle everything

### Step 1 — Register Under YOUR Account First
1. Cloudflare Registrar → **Register Domains** → search and register
2. Use client's business name/contact info in WHOIS if they have it (or use your info temporarily)
3. Cost: Cloudflare sells at-cost (~$8–$15/yr for .com) — charge client your markup or pass-through

### Step 2 — Set Up Site Immediately
1. Connect domain to Pages project → DNS + SSL active
2. Deliver and demo the live site before ownership transfer

### Step 3 — Transfer Registrar Ownership to Client
1. Ensure client has their own Cloudflare account
2. **Cloudflare does not support direct account-to-account domain transfers within Cloudflare itself (as of 2025)**
   - Workaround: Transfer domain OUT to a neutral registrar (e.g., Namecheap), then client transfers IN to their Cloudflare account
   - OR: Add client as **Super Administrator** on your Cloudflare account for their domain only (not recommended — gives broad access)
   - **Recommended path:** Transfer domain to client's preferred registrar, point DNS to Cloudflare nameservers from there

3. Initiate outbound transfer:
   - Cloudflare Dashboard → **Domain Registration → Manage → Transfer Out**
   - Unlock domain → request Auth Code → send to client
4. Client initiates inbound transfer at their registrar of choice
5. Once transferred: update DNS at new registrar to point to Cloudflare Pages if they keep Cloudflare Pages deployment

> **Pro tip:** If client is staying with Cloudflare Pages for hosting, keep the DNS nameservers pointed at Cloudflare even if the registrar moves. Cloudflare Pages doesn't require the domain to be registered at Cloudflare — only that Cloudflare is the DNS nameserver.

---

## Post-Transfer Quality Check (All Scenarios)

- [ ] `https://clientbusiness.com` loads correctly
- [ ] `https://www.clientbusiness.com` redirects or resolves correctly
- [ ] SSL certificate is active (green padlock, no warnings)
- [ ] Cloudflare Analytics showing traffic in Pages dashboard
- [ ] No mixed-content warnings in browser console
- [ ] Google Search Console — add property and submit sitemap (if included in package)
- [ ] Client confirms access to their own Cloudflare dashboard
- [ ] Remove your own admin/editor access if doing full handoff

---

## Billing & Timing Notes

| Item | Cost | Paid By |
|------|------|---------|
| Cloudflare Pages hosting | Free (Hobby plan) | You (included in service) |
| Domain registration at CF Registrar | ~$8–$15/yr for .com | Client (at-cost) |
| Domain transfer fee at CF Registrar | ~$8–$15/yr (renews on transfer) | Client |
| Your time for transfer coordination | 1–2 hrs | Included in project price |

> **Policy:** Do not initiate any domain purchase or transfer on a client's behalf without written approval (text/email is fine). Screenshot and file it.

---

## Escalation / Troubleshooting

| Issue | Fix |
|-------|-----|
| Transfer stuck after 5 days | Client checks registrant email for pending approval; resend verification if needed |
| Auth code rejected | Code expired or registrar not fully unlocked — client must request new code |
| SSL not provisioning | Check DNS propagation (use dnschecker.org); ensure CNAME is proxied (orange cloud in CF) |
| Domain shows but site 404s | Pages project custom domain not confirmed — redo custom domain setup in Pages |
| Client can't find Cloudflare invite | Check spam; resend from Cloudflare dashboard |
| Cloudflare rejects transfer (60-day lock) | Domain registered too recently — must wait until 60 days from registration date |

---

## Related Documents
- `SOP-cloudflare-domain-transfer-external.md` — Client-facing version
- `SOP-spec-build-delivery.md` — Full delivery checklist
- `SOP-client-onboarding.md` — Intake and payment confirmation flow

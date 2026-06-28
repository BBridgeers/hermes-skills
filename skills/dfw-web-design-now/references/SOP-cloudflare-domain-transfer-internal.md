# SOP: Cloudflare Domain Transfer — Internal Operator Guide
**Version:** 1.1  
**Owner:** DFW Web Design NOW  
**Applies to:** All spec-build and custom-build site deliveries where client purchases or already owns a domain  
**Stack:** Cloudflare Pages (deployment) + Cloudflare Registrar (domain management)

---

## Overview

When a client buys a spec-build site (or any delivered project), one of three domain scenarios applies:

| Scenario | Real-World Frequency | Description | Who Acts |
|----------|---------------------|-------------|----------|
| **A** | ⭐⭐⭐⭐⭐ Most common | Client has a domain at ANY registrar (GoDaddy, Namecheap, Wix, Squarespace, etc.) — DNS update only, no transfer needed | Client makes one change; you verify |
| **B** | ⭐⭐ Occasional | Client wants to fully move their domain INTO Cloudflare Registrar | Client initiates transfer; you guide |
| **C** | ⭐⭐⭐ Common for new businesses | Client has no domain — you register it on their behalf | You register, then hand off |

> **Default recommendation:** Always lead with Scenario A (DNS/nameserver update). It works regardless of where the domain lives, takes minutes, and requires no 5–7 day transfer wait. Only use Scenario B if client specifically requests full consolidation at Cloudflare.

---

## Pre-Delivery Intake Questions

Ask these in your onboarding message or delivery email before any domain work begins:

1. "Do you already have a domain name for your business? (e.g., yourbusiness.com)"
2. "If yes — where did you register it? (GoDaddy, Namecheap, Wix, Squarespace, etc.)"
3. "Do you still have login access to that account?"
4. "Would you like to keep it where it is and just point it to the new site, or move it somewhere new?"

Their answers route you to the correct scenario below.

---

## Pre-Transfer Checklist (Before Any Work)

- [ ] Confirm client's current registrar
- [ ] Confirm client has active login access to that registrar account
- [ ] Confirm domain name is agreed upon and active (not expired)
- [ ] Confirm billing is settled — **do not do any domain work before payment clears**
- [ ] Note domain expiry date — warn client if expiring within 30 days
- [ ] Confirm domain has been registered for **60+ days** if doing a full transfer (ICANN lock rule)

---

## Scenario A: Client Has a Domain at ANY Registrar (DNS Update — No Transfer)

**Estimated time: 15–30 minutes active work + up to 24 hrs DNS propagation (usually minutes)**

This is the correct path for the vast majority of DFW clients. The domain stays exactly where it is. You simply update the nameservers or DNS records to point to Cloudflare Pages. No waiting, no auth codes, no ICANN windows.

### How It Works (The Short Version)
You give the client two Cloudflare nameserver addresses. They log into their registrar and swap their current nameservers for the two you provide. Done. Everything else — SSL, routing, CDN — is automatic.

---

### Step 1 — Add the Domain to Your Cloudflare Account

1. Log into [dash.cloudflare.com](https://dash.cloudflare.com)
2. Click **Add a Site** → enter the client's domain name
3. Select the **Free plan**
4. Cloudflare scans existing DNS records and imports them — review and confirm they look correct
5. Cloudflare provides two nameserver addresses, e.g.:
   - `aria.ns.cloudflare.com`
   - `ben.ns.cloudflare.com`
6. Copy these — you'll give them to the client in the next step

---

### Step 2 — Client Updates Nameservers at Their Registrar

Send the client the External Explainer doc with their specific nameserver addresses filled in. Below are the exact navigation paths for each major registrar:

#### GoDaddy (most common for DFW service businesses)
1. Log into [godaddy.com](https://godaddy.com) → My Products → Domains
2. Click the domain → scroll to **Nameservers** → click **Manage**
3. Select **Enter my own nameservers (advanced)**
4. Delete existing entries → enter both Cloudflare nameservers → Save
5. GoDaddy confirmation: up to 48 hrs (usually < 1 hr)

#### Namecheap
1. Log into [namecheap.com](https://namecheap.com) → Domain List → click **Manage** next to domain
2. Under **Nameservers** → change dropdown from "Namecheap BasicDNS" to **Custom DNS**
3. Enter both Cloudflare nameservers → green checkmark to save
4. Propagation: usually < 30 minutes

#### Wix (domain bundled with Wix website)
1. Log into [wix.com](https://wix.com) → **Domains** in the left panel
2. Click the domain → **Advanced** → **Manage DNS Records** (for DNS-only change)
   - OR go to **Manage** → **Transfer Domain Away** if doing a full transfer
3. For nameserver update: scroll to **Nameservers** section → click **Change Nameservers** → enter Cloudflare nameservers
> ⚠️ **Important for Wix clients:** Changing nameservers away from Wix will break their existing Wix site if they have one. Confirm with client that the Wix site is being replaced before making any changes.

#### Squarespace (Google Domains migrated here in 2023)
1. Log into [domains.squarespace.com](https://domains.squarespace.com)
2. Click the domain → **DNS** → **Nameservers**
3. Select **Use custom nameservers** → enter both Cloudflare nameservers → Save
4. Propagation: up to 24 hrs
> ⚠️ **Note:** Many clients who say "Google Domains" are now at Squarespace Domains after Google's 2023 sale. Same process applies.

#### Network Solutions
1. Log into [networksolutions.com](https://networksolutions.com) → My Account → Manage Domain Names
2. Select domain → click **Change Where Domain Points** → **Domain Name Servers (DNS)**
3. Select **Specify nameservers** → enter both Cloudflare nameservers → Save
4. Propagation: up to 48 hrs (often slower than others)

#### Bluehost / HostGator / Other Web Hosts Acting as Registrar
Many service businesses registered their domain through their web host. The process is nearly the same:
1. Log into hosting control panel → **Domains** → find the domain → **Nameservers**
2. Switch from default nameservers to **Custom** → enter Cloudflare nameservers → Save
3. If client can't find it, have them log into [who.is](https://who.is) or [whois.domaintools.com](https://whois.domaintools.com) and search their domain — the registrar and current nameservers are listed there

---

### Step 3 — Connect Site to Domain in Cloudflare Pages

Once Cloudflare confirms the nameservers are active (you'll see a green **Active** status on the site in your Cloudflare dashboard):

1. Go to **Workers & Pages** → your site project → **Settings → Custom Domains**
2. Click **Set up a custom domain** → enter `clientbusiness.com`
3. Also add `www.clientbusiness.com` and set up a redirect rule if needed
4. Cloudflare auto-adds the CNAME record and provisions SSL
5. Verify green padlock live within 5–15 minutes

---

### Step 4 — Verify & Hand Off

1. Test `https://clientbusiness.com` and `https://www.clientbusiness.com` in an incognito window
2. Confirm no SSL warnings, no 404s, all page sections load correctly on mobile
3. If doing full ownership handoff: go to **Cloudflare Dashboard → Manage Account → Members** → invite client's email as **Administrator** of just their domain zone
4. Once client confirms access, you can remove yourself or stay as a secondary admin per your retainer agreement

---

## Scenario B: Full Domain Transfer INTO Cloudflare Registrar

**Estimated time: 2–7 days (ICANN transfer window)**

Use this ONLY when the client specifically requests full consolidation at Cloudflare — e.g., they want one billing dashboard for domain + hosting, or they're leaving GoDaddy for good.

### Phase 1 — Prepare Domain at Current Registrar (Client Action)

> Send client the External Explainer doc — they handle this phase

1. Client unlocks the domain at their current registrar (see Step 2 navigation paths in Scenario A above)
2. Client disables **WHOIS Privacy** temporarily (required for some registrars to release auth code)
3. Client requests the **EPP/Authorization Code** (also called Auth Code or Transfer Key):
   - **GoDaddy:** Auto-emails it when domain is unlocked
   - **Namecheap:** Domain List → Manage → Auth Code → Send by Email
   - **Squarespace Domains:** Domain → Settings → Transfer Away → Get Auth Code
   - **Network Solutions:** Account → Manage Domain → Transfers → Request Auth Code
   - **Wix:** Domains → Manage → Transfer Domain Away → Get Auth Code (must disable Wix privacy first)
4. Client forwards you the Auth Code

> ⚠️ **Security note:** Auth codes expire in 7–30 days depending on registrar. Begin transfer immediately upon receipt.

### Phase 2 — Initiate Transfer at Cloudflare Registrar

1. Log into [dash.cloudflare.com](https://dash.cloudflare.com) → **Domain Registration → Transfer Domains**
2. Enter the domain name → click **Confirm it's unlocked**
3. Enter the EPP/Auth Code
4. Cloudflare shows a price (~$8–$15/year) — confirm with client before payment
5. Add payment method → submit transfer
6. Cloudflare sends a **verification email** to the domain's registrant email — client must click **Approve Transfer**
7. Transfer window: **5–7 business days** (often 1–2 days in practice)

### Phase 3 — Post-Transfer DNS Setup

Once transfer completes and domain shows **Active**:
1. **DNS → Records** — verify existing records migrated correctly
2. Add/confirm CNAME records pointing to Pages project:
   - `CNAME @ [your-pages-project].pages.dev`
   - `CNAME www [your-pages-project].pages.dev`
3. Pages → **Custom Domains** → verify domain connected
4. SSL auto-provisions — test within 15 minutes
5. Run full QA checklist below

---

## Scenario C: Client Has No Domain — You Register on Their Behalf

**Estimated time: 1–2 hours for full setup**

### Step 1 — Register Under YOUR Cloudflare Account
1. **Domain Registration → Register Domains** → search and register
2. Use client's business contact info in WHOIS registration fields
3. Cost: ~$8–$15/yr for .com — pass through to client or include in project price

### Step 2 — Build and Demo Site First
1. Connect domain to Pages project → full DNS + SSL active
2. Deliver live demo before transferring any ownership
3. Collect final payment and sign-off before Step 3

### Step 3 — Hand Off Domain Ownership

> **Known limitation:** Cloudflare does NOT support direct account-to-account domain transfers within Cloudflare (as of 2026). Use this workaround:

**Option 3a — Transfer Out to Client's Preferred Registrar (Recommended)**
1. Client creates account at their preferred registrar (Namecheap recommended for simplicity)
2. Cloudflare Dashboard → **Domain Registration → Manage → Transfer Out**
3. Unlock domain → request outbound Auth Code → send to client
4. Client initiates inbound transfer at their registrar
5. DNS: ensure client's registrar still points nameservers to Cloudflare (`aria.ns.cloudflare.com` etc.) so site stays live
6. Verify site live post-transfer — no downtime if nameservers stay consistent

**Option 3b — Add Client as Zone Admin on Your Cloudflare Account**
- Invite client as **Administrator** of only their domain zone
- They get full DNS/domain control without access to your other projects
- Works well for clients who want Cloudflare but don't want to manage a full account
- Downside: domain registration/billing stays on your card until they add their own payment

> **Pro tip:** If client stays with Cloudflare Pages for hosting, the domain does NOT need to be registered at Cloudflare — it just needs Cloudflare as the DNS nameserver authority. This means Option 3a works perfectly — domain lives at Namecheap, DNS points to Cloudflare, site runs on Cloudflare Pages. Three separate things.

---

## Post-Transfer Quality Check (All Scenarios)

- [ ] `https://clientbusiness.com` loads site correctly
- [ ] `https://www.clientbusiness.com` resolves correctly (redirect or direct)
- [ ] SSL certificate active — green padlock, no browser warnings
- [ ] No mixed-content errors in browser console (F12 → Console)
- [ ] Site loads correctly on mobile (test on actual phone)
- [ ] Cloudflare Analytics active in Pages dashboard
- [ ] Google Search Console — add property and submit sitemap (if in package)
- [ ] Client has confirmed their own login access
- [ ] Your access removed or scoped to agreed level (retainer vs. one-time)

---

## Billing & Timing Reference

| Item | Approx. Cost | Paid By | Notes |
|------|-------------|---------|-------|
| Cloudflare Pages hosting | Free | You | Included in your service |
| Domain registration (.com) | ~$10–$15/yr | Client | Pass-through or markup |
| Domain transfer into CF | ~$10–$15/yr | Client | Renews on transfer date |
| Your coordination time | 1–2 hrs | Included in project | Scenario A only; charge extra for B/C complexity if needed |

> **Policy:** Never purchase or transfer a domain on a client's behalf without written approval. Text message is fine. Screenshot it.

---

## Troubleshooting Reference

| Issue | Cause | Fix |
|-------|-------|-----|
| Nameservers updated but site still shows old content | DNS propagation delay | Wait up to 48 hrs; test at [dnschecker.org](https://dnschecker.org) |
| Transfer stuck after 5+ days | Client hasn't clicked approval email | Check registrant email including spam; resend verification from CF dashboard |
| Auth code rejected | Code expired or domain still locked | Client requests new code; confirm lock is disabled |
| SSL not provisioning | CNAME not proxied / DNS not fully propagated | Ensure CNAME shows orange cloud (proxied) in CF DNS; check propagation |
| Domain shows Active but site 404s | Custom Domain not confirmed in Pages | Pages → Custom Domains → re-add and verify |
| Wix client — site blank after nameserver change | Expected — Wix site no longer active | Confirm client approved switching away from Wix before making any changes |
| CF rejects transfer (60-day lock) | Domain registered < 60 days ago | Must wait; use Scenario A (DNS update) in the meantime |
| Client lost registrar login access | Common with old GoDaddy accounts | Client uses registrar's account recovery; may take 1–3 days |

---

## Related Documents
- [`SOP-cloudflare-domain-transfer-external.md`](./SOP-cloudflare-domain-transfer-external.md) — Client-facing explainer
- `SOP-spec-build-delivery.md` — Full delivery checklist
- `SOP-client-onboarding.md` — Intake and payment confirmation flow

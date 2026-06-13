# FB Marketplace Scraper — Credential Setup

## Required Environment Variables

| Variable | Purpose | Source |
|---|---|---|
| `FB_EMAIL` | Facebook login email | Your FB account |
| `FB_PASSWORD` | Facebook login password | Your FB account |
| `GROQ_API_KEY` | (Optional) AI vision OCR enrichment | [console.groq.com](https://console.groq.com) |
| `APIFY_API_TOKEN` | (Optional) Residential proxy strategy | [apify.com](https://apify.com) |

## Setup Steps

1. **Create a dedicated Facebook account** for scraping (recommended — avoids personal account lockouts)
2. Enable "Less secure app access" or use app password if 2FA is on
3. Set env vars in the scraper container's environment or in `.env` file
4. Restart the scraper — first run will login and save cookies
5. Subsequent runs reuse cookies until FB rotates them (~24h)

## 2FA Handling

If the account has 2FA:
- Scraper detects the checkpoint page and captures a screenshot
- Pauses execution and prompts for manual code entry
- After entering the code, saves the resulting session cookies (including 2FA token)
- Future runs skip the checkpoint entirely

## Container Environment Example

```yaml
# In docker-compose.yml environment section:
environment:
  - FB_EMAIL=scraper@yourdomain.com
  - FB_PASSWORD=your-app-password
  - GROQ_API_KEY=groq-your-api-key
  - APIFY_API_TOKEN=apify-your-token
```
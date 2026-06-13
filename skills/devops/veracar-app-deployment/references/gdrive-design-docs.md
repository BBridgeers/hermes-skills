# GDrive Design Documents — veracar.co

The user maintains key design specifications on Google Drive. Always search GDrive before building new pages or features.

## Key Documents

| Document | Drive ID | Purpose |
|---|---|---|
| `vehicle_analyzer_lisitng_evaluation_output_design.md` | `1qxoxKdmi-9keS9ahWlY-J_JEL7rwCJ7f` | Complete analysis report page design spec — 14 sections, verdict banner layout, component requirements |

## Search Pattern

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

with open("/root/.hermes/google_token.json") as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get("token"),
    refresh_token=token_data.get("refresh_token"),
    token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
    client_id=token_data.get("client_id"),
    client_secret=token_data.get("client_secret"),
    scopes=token_data.get("scopes", []),
)
service = build("drive", "v3", credentials=creds)

# Search
results = service.files().list(
    q="name contains 'vehicle_analyzer'",
    fields="files(id, name, mimeType, webViewLink)",
    pageSize=20
).execute()
```

## Download Pattern

### Option A: Google API (recommended for single files)
...

### Option B: rclone (used June 2026 for 3-file download)
When the Google API token is unavailable or the files are under a different Drive account, use rclone:

```bash
rclone ls gdrive_personal:vehicle-analyzer          # list files
rclone cat gdrive_personal:vehicle-analyzer/file.md > /tmp/file.md  # download single file
```

**rclone remotes available**: `gdrive_personal:` (Blake's personal Drive, used for vehicle-analyzer design docs).

## Report Template Update Pattern

When the user provides GDrive design docs specifying report output format:

1. Download ALL referenced docs (typically: `vehicle_analyzer_input_and_output_audit.md`, `vehicle_analyzer_lisitng_evaluation_output_design.md`, `AnalysisResults.tsx`)
2. Read through all three documents to understand the full field map
3. Compare against the current `generateTextReport()` function in `AnalysisResults.tsx`
4. Identify: missing sections, wrong field names, incorrect data access paths
5. The canonical report must cover all 14 sections from the design spec:
   - Metric Cards (4 cards: price, market value, equity, issues)
   - Verdict (score, confidence, buy if, walk away, red flags)
   - Market Values (5 data points)
   - Critical Issues (with severity, concern, benign, worst-case, action)
   - Vehicle History (recalls + service records, conditional on VIN)
   - Scenario Analysis (3-4 scenarios)
   - Break-Even (cushion, max budget, risk)
   - Insurance (coverage type, personal/rideshare/commercial, carriers)
   - Operational Costs (line-item table with monthly/annual/cost-per-mile)
   - Initial Investment (required + optional items)
   - ROI & Payback Timeline (conservative/baseline/optimistic weeks)
   - Rideshare Eligibility & Earnings (per-platform, earnings projections)
   - Negotiation Strategy (opening/target/walk-away, leverage points)
   - Action Plan (numbered steps)
   - Condition Assessment (exterior/interior/mechanical + expected checklist)
   - Seller Verification (contacted, responsiveness, transparency, flags, quotes)
6. Guard ALL field access with optional chaining + fallback — `$undefined` in output means the report will be rejected
7. Rebuild and deploy after report template changes

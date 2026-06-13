# Analysis Report Page — Architecture

## What It Is

The `/analysis/[id]` page is the **VERA Intelligence Report** — a full-screen analysis results page that sits BETWEEN the "New Evaluation" form and the "Fleet Dashboard". It displays the complete output of `analyzeVehicle()` with all 14 sections.

## URL & Route

- **Route**: `/analysis/[id]` where `id` is `va-<timestamp>` (e.g., `va-1716921600000`)
- **File**: `src/app/analysis/[id]/page.tsx` (389 lines)
- **API**: `src/app/api/analysis/[id]/route.ts` (27 lines)

## Navigation Flow

```
New Evaluation Form (page.tsx)
    │
    ├── Fill Year, Make, Model (required — line 1746 validation)
    ├── Click "Run AI Analysis" (top) OR "Generate VERA Intelligence Report" (bottom, line 1267)
    │
    ▼
onRunAnalysis() (line 1746)
    │
    ├── Validates currentMake && currentModel
    ├── Builds Vehicle object from form state (line 1759)
    ├── Calls analyzeVehicle(vehicle) (line 1787)
    ├── Saves to localStorage: `analysis_<id>` = { vehicle, result } (line 1845)
    ├── Navigates: router.push(`/analysis/${analysisId}`) (line 1846)
    │
    ▼
/analysis/[id] page loads
    │
    ├── Reads localStorage: `analysis_<params.id>` (line 37)
    ├── Falls back to `analysis_va-<id>` format (line 52)
    ├── If not found: error state with "Return to Home" link
    │
    ▼
14 collapsible sections rendered
```

## Data Contract

**localStorage key**: `analysis_<id>`

**Value shape**:
```typescript
{
  vehicle: Vehicle,      // from form state (line 1759)
  result: AnalysisResult // from analyzeVehicle() (line 1787)
}
```

**AnalysisResult contains**:
- `verdict`, `verdictScore`, `instantEquity`
- `marketValues`, `criticalIssues`, `structuredVerdict`
- `scenarios`, `breakEven`, `insurance`
- `operationalCosts`, `initialInvestment`, `paybackWeeks`
- `negotiation`, `actionPlan`
- `conditionAssessment`, `sellerVerification`
- `rideshare` (optional)

## 14 Sections (in order)

1. Final Verdict (`FinalVerdictPanel`)
2. Market Value Comparison (`MarketChart`)
3. Critical Issues (`IssueCard` per issue)
4. Vehicle History & Records (conditional on `result.vinAnalysis`)
5. Scenario-Based Financial Analysis (`ScenarioAnalysisPanel`)
6. Break-Even Analysis (`BreakEvenPanel`)
7. Insurance Cost Estimates (`InsurancePanel`)
8. Operational Cost Breakdown (`OperationalCostsPanel`)
9. Initial Investment Required (conditional — rideshare only)
10. ROI & Payback Timeline (conditional — rideshare only)
11. Rideshare Eligibility & Earnings (conditional)
12. Negotiation Strategy (`NegotiationPanel`)
13. Pre-Purchase Action Plan (`ActionPlanPanel`)
14. Condition Assessment (`ConditionPanel`)
15. Seller Verification (`SellerVerificationPanel`)

## Top Nav Bar

- **VA** logo → home
- **"Why?" button** → opens `AnalysisInspector` modal (scoring breakdown)
- **"Download Report" button** → generates text report via `generateTextReport()` imported from `@/components/AnalysisResults` — **NOT** from an inline function in page.tsx. See pitfall below.
- **"Fleet Dashboard"** link → `/fleet`

## Download Report — Single Source of Truth

The "Download Report" button in the top nav bar calls `downloadReport()` in page.tsx, which delegates to `generateTextReport(vehicle, result)` — exported from `src/components/AnalysisResults.tsx` and imported into page.tsx.

**Critical pitfall — duplicate implementation drift**: Originally, page.tsx had its own INLINE `downloadReport()` function that was a stripped-down, buggy copy of the comprehensive `generateTextReport()` in AnalysisResults.tsx. The two implementations drifted apart:
- Page.tsx version accessed insurance as `result.insurance[tier].monthly` (nested) — but the actual TypeScript type has flat fields: `personalMonthly`, `rideshareMonthly`, `commercialMonthly`, `carriers`. This produced `$undefined/mo` for all insurance data.
- Page.tsx version accessed operational costs as nested `{monthly, annual}` objects — but the actual type has `expenses[]` array with `totalMonthly`, `totalAnnual`, `costPerMile`.
- Page.tsx version was missing 9 sections: scenarios, break-even risk assessment, initial investment, payback timeline, rideshare earnings, condition assessment, seller verification, action plan, VIN history.

**Fix**: Export `generateTextReport` from AnalysisResults.tsx (`export function`), import in page.tsx (`import { generateTextReport } from '@/components/AnalysisResults'`), replace the inline buggy version. Single source of truth eliminates drift.

**Data access patterns that must match the actual TypeScript types** (see `src/lib/types.ts`):
- `analysis.insurance.personalMonthly` / `.rideshareMonthly` / `.commercialMonthly` — flat, not nested
- `analysis.operationalCosts.expenses[]` — array of `{category, monthly, annual, notes}`, plus `.totalMonthly`, `.totalAnnual`, `.costPerMile`
- `analysis.scenarios.scenarios[]` — array of `{label, repairCost, totalCost, equityAfterRepairs, description}`
- `analysis.breakEven.repairCushion` — NOT `result.breakEven.repairCushion` (typo in old code had `repairCushion` wrong)

## Bottom Action Bar

- **"✅ Add to Fleet"** — saves `{ type: 'add', vehicle, result }` to localStorage key `vera_fleet`, navigates to `/fleet`
- **"🚫 Pass"** — saves `{ type: 'pass', vehicle, result }` to localStorage key `vera_fleet`, navigates to `/fleet`

## Common Failure Mode

**Symptom**: Clicking "Generate VERA Intelligence Report" does nothing — no navigation, no error.

**Root cause**: The validation at `page.tsx:1746` requires `currentMake` AND `currentModel`. If the form is empty (no values filled in), the function alerts and returns without navigating. This is expected behavior — the form must be filled.

**Testing**: Always fill Year, Make, Model before clicking the button. An empty form will NOT navigate.

## Components Used

All imported from `@/components/`:
- `AnalysisInspector`, `FinalVerdictPanel`, `MarketChart`, `IssueCard`
- `ScenarioAnalysisPanel`, `BreakEvenPanel`, `InsurancePanel`
- `OperationalCostsPanel`, `InitialInvestmentPanel`, `PaybackPanel`
- `NegotiationPanel`, `ActionPlanPanel`, `ConditionPanel`
- `SellerVerificationPanel`, `RidesharePanel`

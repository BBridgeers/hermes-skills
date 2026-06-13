# Section 8 → Section 4 Cross-Reference Audit Methodology

**Purpose:** Systematic audit to ensure Section 4 Master Daily Grids reflect all agent requirements from Section 8 Synergistic Pathways.

## When to Run

- After any Section 8 pathway is written or remapped
- After Section 4 grids are built or significantly modified
- Before final handbook assembly
- Whenever a new agent class is introduced to Section 8

## The Four-Pass Method

### Pass 1 — Missing Agent Detection
For each Section 8 pathway, extract every agent mentioned with a dose. Check if that agent appears in Section 4 at the correct phase. Agents that appear in Section 8 but not Section 4 are missing.

Key query: "Does Section 8 pathway X mandate agent Y at dose Z in phase W? Does Section 4 phase W grid contain agent Y?"

### Pass 2 — Synergy/Proximity Audit  
For each Section 8 pathway, identify mandated co-administration pairs (agents that MUST be taken together). Check if Section 4 places them at the same time slot.

Key query: "Does Section 8 say agents A and B must be co-administered? Are they in the same time row in Section 4?"

### Pass 3 — Timing/Separation Audit
For each Section 8 pathway, identify mandatory separation windows. Check if Section 4 enforces those separations between incompatible agents.

Key query: "Does Section 8 mandate X-hour separation between agents A and B? Are they X hours apart in Section 4's time grid?"

### Pass 4 — False Positive Filter
Before flagging any finding, ask: does this Section 8 constraint target the same biological compartment as the Section 4 phase? Section 8 pathways describe dedicated deep-clean protocols with their own internal logic. Their constraints may NOT apply to the Section 4 daily grids if:

- The Section 8 constraint targets biofilm-embedded organisms and Section 4 targets free-swimming parasites
- The Section 8 protocol is a standalone deep-clean (e.g., dedicated antibiotic strike) and Section 4 is the general protocol flow
- The Section 8 constraint is for a different clinical population than Section 4 assumes

**Example false positive:** Section 8.8 mandates "enzyme pre-treatment minimum 14 days before antimicrobial agents." This applies to a dedicated biofilm strike using oregano oil + berberine against EPS-embedded bacteria. It does NOT apply to Section 4 Phase 2's gentle antiparasitic introduction (Black Walnut, Wormwood, Clove) which targets free-swimming parasites in the gut lumen — not biofilm-embedded organisms.

## Real Session Example (May 22, 2026)

16 findings across all 9 Section 8 pathways vs Section 4:
- 1 critical (false positive — Section 8.8 enzyme pre-treatment rule)
- 10 missing agents (Glycine, Humic/Fulvic Acid, Zinc Carnosine, Calcium D-Glucarate, Astragalus, Sulforaphane, Selenium, Phosphatidylcholine, CoQ10, Cellulase/DNase)
- 2 synergy/proximity issues (Nattokinase+Serrapeptase separated, Iodine without Selenium)
- 3 dose/timing issues (Milk Thistle underdosed, Phosphatidylcholine late start, GSH triad incomplete)

10 agents were surgically inserted into Section 4 across Phases 1-6, adding 22 lines (514→536).

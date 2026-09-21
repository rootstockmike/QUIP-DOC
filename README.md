# AMER Customer Sector Atlas

A single master register of AMER customer accounts, merged from the Salesforce Quip
segment exports and reconciled against the `Sub-Sector` value logged on each Salesforce
account record.

**Master document (browsable):** https://claude.ai/artifact/BTLyuV2GAzbjqvt78Pe6bG

| | |
| --- | --- |
| Accounts | **8,419** |
| Segments | **12** (from 15 tabs across 6 documents) |
| Current licenses | **10,113,862** |
| Sector-aligned | 6,620 Core (78.6%) + 658 Adjacent |
| **Off-sector** | **853 (10.1%)** |
| **No sector logged** | **288 (3.4%)** |

## What's here

| Path | Contents |
| --- | --- |
| `data/master_customers.csv` | All 8,419 accounts, 24 columns, with segment, logged sub-sector and alignment verdict. |
| `data/sector_exceptions.csv` | The 1,799 accounts that are **not** cleanly Core — the review queue, off-sector first. |

## Sources merged

| Source document | Tabs with data | Accounts |
| --- | --- | ---: |
| AMER Customers – Construction, Engineering, Mining, Agriculture (Quip HTML) | Construction, Engineering, Mining, Agriculture | 1,853 |
| AMER Hardware / Software / Semiconductor Customers | Hardware (10+), Software (200+), Semiconductor (10+) | 2,277 |
| AMER Retail / Consumer Goods Customers | Consumer Goods, Retail | 2,545 |
| AMER Discrete MFG Customers 10-49 Users | 10-19 Users **only** | 1,107 |
| AMER Energy Customers | Oil & Gas, Utilities | 637 |
| **AMER Pharma / Med Device / Diagnostic Customers** | **none — see below** | **0** |
| **Total** | **12 tabs** | **8,419** |

## Blocking data problems

1. **The Pharma / Med Device / Diagnostic workbook is unreadable.** All three sheets —
   `MedDevice (10+ Users)`, `Diagnostics_Post Acute (10+ Users)` and `Pharma (20+ Users)` —
   contain a single `#REF` error where the account table should be. The formula links broke
   on export and the cells hold no recoverable values. **These three segments are missing
   from this register entirely.** A re-export from Quip with values pasted in place is the
   only fix.
2. **The Discrete MFG `20-49 Users` sheet is empty.** The workbook is named *10-49 Users*
   and carries two sheets, but only `10-19 Users` has rows — the 20-49 cohort is absent.
3. **The Engineering tab has no `Sub-Sector` at all** — 288 of 288 rows blank. It is the
   only segment that cannot be reconciled, and it includes some of the largest accounts in
   the register (Jacobs Engineering, 64,500 licenses; Parsons, 17,302).

## Sector alignment by segment

Each account sits in a segment tab that asserts a sector, and *also* carries a `Sub-Sector`
field on its Salesforce record. Comparing the two is the point of this exercise.

| Segment | Source document | Accounts | Core | Adjacent | Off-sector | Unclassified | Off % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Construction | Construction/Eng/Mining/Ag | 1,497 | 1,240 | 109 | 148 | — | 9.9% |
| Engineering | Construction/Eng/Mining/Ag | 288 | — | — | — | **288** | — |
| Agriculture | Construction/Eng/Mining/Ag | 45 | 36 | 3 | 6 | — | 13.3% |
| Mining | Construction/Eng/Mining/Ag | 23 | 17 | — | 6 | — | **26.1%** |
| Discrete MFG | Discrete MFG 10-49 | 1,107 | 923 | 97 | 87 | — | 7.9% |
| Utilities | AMER Energy | 375 | 375 | — | — | — | **0.0%** |
| Oil & Gas | AMER Energy | 262 | 262 | — | — | — | **0.0%** |
| Hardware | HW/SW/Semi | 868 | 703 | 20 | 145 | — | 16.7% |
| Software | HW/SW/Semi | 1,204 | 1,116 | 25 | 63 | — | 5.2% |
| Semiconductor | HW/SW/Semi | 205 | 182 | 11 | 12 | — | 5.9% |
| Consumer Goods | Retail/CG | 1,146 | 810 | 237 | 99 | — | 8.6% |
| Retail | Retail/CG | 1,399 | 956 | 156 | 287 | — | **20.5%** |

**Energy is perfect** — 637 accounts, zero drift in either tab. **Mining is worst
proportionally** (26.1%, 6 of 23). **Retail is worst in absolute terms** (287 accounts).

### Patterns worth a decision

- **Software companies filed as hardware and retail.** 87 Hardware accounts and 97 Retail
  accounts are logged `Software & Programming Services`. That is a retail-tech / hardware-tech
  cohort sitting in the wrong tabs, and it is the single most repeated conflict in the set.
- **Construction is doing double duty.** Its largest sub-sector is `Home Services` (585,
  39% of the tab), ahead of `General Contractors` (288) and `Sub-Contractors` (228). Decide
  whether Construction is a *trades* list or a *field-service* list.
- **Six Mining accounts are financial holdings, not operators** — Coeur Capital (`Lending`),
  Americas Gold Company (`Wealth Management`), OR Royalties (`REITs and Other Trusts`), plus
  Core Scientific (`Other Process MFG`), Eberl Iron Works (`Parts Production`) and the
  Association for Mineral Exploration (`Other`).
- **`Distributors` drives most of the Consumer Goods drift** — 186 accounts, counted
  Adjacent here. Reclassify it and Consumer Goods' exception count moves sharply.

## Verification

- **No duplicates, and no cross-segment overlap.** All 8,419 `Account ID` values are unique
  and no account appears in two segment tabs — not even across Retail and Consumer Goods, or
  Hardware and Software, where overlap would be natural. The segmentation is genuinely
  mutually exclusive, so every conflict above is a tab-vs-field disagreement, never a
  double-count.
- **Row counts reconcile.** Parsed license sums match the `Total` row printed in all four
  Quip tables exactly (Construction 254,062 / 293,956; Engineering 46,636 / 128,727;
  Mining 1,604 / 1,679; Agriculture 7,234 / 7,385). Nothing was truncated on import.

## Method notes

- **Columns are matched by header name, not position.** This is required, not defensive:
  the Semiconductor sheet orders its columns differently — `Sub-Sector` sits in column T
  rather than Z — and four sheets carry an extra `Industry Focus` column that shifts
  `Website`. Reading by position silently mis-assigns sectors on those sheets.
- **`Industry Focus` is not a usable fallback sector.** It appears on five tabs, but 4,865
  of its 5,724 rows hold `-`; only about 15% carry a real value.
- **Core / Adjacent / Off-sector is a judgement call,** not a field in the source. The sets
  were defined per tab from the `Sub-Sector` values actually present. Three calls move the
  headline numbers most: `Waste Services` under Construction (99), `Distributors` under
  Consumer Goods (186) and `Environment, Energy, and Agriculture` under Discrete MFG (88)
  are all counted **Adjacent** rather than Off-sector.

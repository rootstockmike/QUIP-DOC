# AMER Customer Sector Atlas

A single master register of AMER customer accounts, merged from three Salesforce Quip
segment exports and reconciled against the `Sub-Sector` value logged on each Salesforce
account record.

**Master document (browsable):** https://claude.ai/artifact/BTLyuV2GAzbjqvt78Pe6bG

## What's here

| Path | Contents |
| --- | --- |
| `data/master_customers.csv` | All 3,597 accounts, one row each, with segment, logged sub-sector and alignment verdict. |
| `data/sector_exceptions.csv` | The 744 accounts that are **not** cleanly sector-aligned — the review queue. |

## Sources merged

| Source document | Tabs used | Accounts |
| --- | --- | --- |
| AMER Customers – Construction, Engineering, Mining, Agriculture (Quip) | Engineering, Construction, Mining, Agriculture | 1,853 |
| AMER Discrete MFG Customers 10-49 Users (xlsx) | 10-19 Users | 1,107 |
| AMER Energy Customers (xlsx) | Oil & Gas, Utilities | 637 |
| **Total** | **7 tabs** | **3,597** |

All three sources share an identical 27-column schema and are joined on `Account ID`.

## Sector alignment

Each account sits in a segment tab that asserts a sector. Each account *also* carries a
`Sub-Sector` field on its Salesforce record. Comparing the two is the point of this exercise.

| Verdict | Accounts | Share |
| --- | --- | --- |
| Core — logged sector matches the tab | 2,853 | 79.3% |
| Adjacent — defensible boundary case | 209 | 5.8% |
| **Off-sector — logged as something else** | **247** | **6.9%** |
| **Unclassified — no `Sub-Sector` on record** | **288** | **8.0%** |

### By segment

| Segment tab | Accounts | Core | Adjacent | Off-sector | Unclassified |
| --- | ---: | ---: | ---: | ---: | ---: |
| Construction | 1,497 | 1,240 | 109 | 148 | — |
| Engineering | 288 | — | — | — | **288** |
| Discrete MFG (10-19 users) | 1,107 | 923 | 97 | 87 | — |
| Utilities | 375 | 375 | — | — | — |
| Oil & Gas | 262 | 262 | — | — | — |
| Agriculture | 45 | 36 | 3 | 6 | — |
| Mining | 23 | 17 | — | 6 | — |

Energy (Oil & Gas + Utilities) is perfectly aligned. Construction carries 60% of all
off-sector rows. Mining is the worst proportionally — 6 of 23 accounts, over a quarter.

## Findings that need a decision

1. **The Engineering tab has no `Sub-Sector` at all** — 288 of 288 rows blank. It is the
   largest single data gap and the reason Engineering cannot be reconciled. It includes
   some of the biggest accounts in the register (Jacobs Engineering, 64,500 licenses;
   Parsons, 17,302). Populating this field is the highest-value fix available.
2. **The Discrete MFG `20-49 Users` sheet is empty.** The workbook is named *10-49 Users*
   and carries two sheets, but only `10-19 Users` has data — so the 20-49 user cohort is
   absent from this register entirely. A re-export is needed.
3. **Construction is doing double duty.** Its largest sub-sector is `Home Services` (585
   accounts, 39% of the tab), ahead of `General Contractors` (288) and `Sub-Contractors`
   (228). Decide whether Construction is a *trades* list or a *field-service* list — the
   answer reclassifies several hundred accounts either way.
4. **Six Mining accounts are financial holdings, not operators** — Coeur Capital
   (`Lending`), Americas Gold Company (`Wealth Management`), OR Royalties (`REITs and
   Other Trusts`), plus Core Scientific (`Other Process MFG`), Eberl Iron Works
   (`Parts Production`) and the Association for Mineral Exploration (`Other`).
5. **`Global Company` is blank on 42.3% of accounts** and `Website` on 8.2%, which limits
   parent-company roll-ups.

## Verification

- **No duplicates.** All 3,597 `Account ID` values are unique — no company appears in two
  segment workbooks, so every conflict above is a tab-vs-field disagreement, never a
  double-count.
- **Row counts reconcile.** Parsed license sums match the `Total` row printed in all four
  Quip tables exactly (Construction 254,062 / 293,956; Engineering 46,636 / 128,727;
  Mining 1,604 / 1,679; Agriculture 7,234 / 7,385). Nothing was truncated on import.

## Method note

`Core` / `Adjacent` / `Off-sector` sets were defined per tab from the `Sub-Sector` values
actually present in the data; they are a judgement call, not a field in the source.
Two calls are worth knowing about: `Waste Services` (99 accounts) under Construction and
`Environment, Energy, and Agriculture` (88) under Discrete MFG are both counted
**Adjacent** rather than Off-sector. Reclassifying either moves the headline numbers.

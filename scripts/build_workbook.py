#!/usr/bin/env python3
"""Build AMER_Customer_Sector_Atlas.xlsx from data/master_customers.csv.

One tab per segment plus a Summary tab. Sector Alignment is colour-coded so
misfiled accounts are visible at a glance: off-sector orange, unclassified
grey, adjacent light blue, core unshaded.

The workbook is a generated artifact and is not tracked in git -- it carries
account owner email addresses. Regenerate it with:

    python3 scripts/build_workbook.py

Requires openpyxl.
"""
import collections
import csv
import os

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "master_customers.csv")
OUT = os.path.join(ROOT, "AMER_Customer_Sector_Atlas.xlsx")

# Segment order: grouped by source document rather than by size.
ORD = ["Construction", "Engineering", "Agriculture", "Mining", "Discrete MFG",
       "Med Device", "Hardware", "Software", "Semiconductor", "Utilities",
       "Oil & Gas", "Consumer Goods", "Retail"]

# (sheet header, column in master_customers.csv, numeric?, width)
COLS = [("Account Name", "Account Name", 0, 34),
        ("Logged Sub-Sector", "Logged Sub-Sector", 0, 26),
        ("Sector Alignment", "Sector Alignment", 0, 15),
        ("Account ID", "Account ID", 0, 18),
        ("Current Licenses", "Current Licenses", 1, 15),
        ("# Licenses", "# Licenses", 1, 12),
        ("# Cases", "# Cases", 1, 11),
        ("AOV Band", "AOV Band", 0, 12),
        ("Core First Active", "Core First Active Date", 0, 16),
        ("Account Owner", "Account Owner", 0, 20),
        ("Account Owner Email", "Account Owner Email", 0, 30),
        ("Owner Manager", "Owner Manager", 0, 20),
        ("Master Carve", "Master Carve", 0, 26),
        ("Shipping Country", "Shipping Country", 0, 9),
        ("Shipping State", "Shipping State", 0, 9),
        ("Shipping City", "Shipping City", 0, 18),
        ("Annual Revenue", "Annual Revenue", 0, 18),
        ("Employees", "Employees", 1, 11),
        ("Global Company", "Global Company", 0, 28),
        ("Industry Focus", "Industry Focus", 0, 26),
        ("Website", "Website", 0, 32),
        ("Source Document", "Source Document", 0, 30),
        ("Source Tab", "Source Tab", 0, 22)]

NAVY = "FF2C4164"
HDR_FILL = PatternFill("solid", fgColor=NAVY)
HDR_FONT = Font(bold=True, color="FFFFFFFF", size=10)
FILL = {"Off-sector": PatternFill("solid", fgColor="FFFFE8D6"),
        "Unclassified": PatternFill("solid", fgColor="FFF1F4F8"),
        "Adjacent": PatternFill("solid", fgColor="FFE9F5F8")}
FONTC = {"Off-sector": Font(color="FFB34700", bold=True, size=10),
         "Unclassified": Font(color="FF6B7686", size=10),
         "Adjacent": Font(color="FF2E7D8F", size=10),
         "Core": Font(color="FF3F7A26", size=10)}

GAPS = [
    "Known gaps",
    "• Diagnostics_Post Acute (10+ Users) and Pharma (20+ Users) are absent — both hold only a #REF error in the source workbook and need re-exporting.",
    "• The Engineering tab has no Sub-Sector on any of its 288 accounts, so it cannot be reconciled.",
    "• Sector Alignment is a judgement call, not a field in the source: Core/Adjacent sets were defined per segment from the Sub-Sector values present.",
    "• No account appears in more than one segment — all Account IDs are unique across all rows.",
]


def num(s):
    s = (s or "").replace(",", "").strip()
    try:
        return int(float(s))
    except ValueError:
        return None


def main():
    with open(SRC, newline="", encoding="utf-8") as fh:
        recs = list(csv.DictReader(fh))
    print("read %d accounts from %s" % (len(recs), os.path.relpath(SRC, ROOT)))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws["A1"] = "AMER Customer Sector Atlas"
    ws["A1"].font = Font(bold=True, size=16, color=NAVY)
    ws["A2"] = ("All AMER customer accounts by segment, reconciled against the "
                "Sub-Sector logged on each Salesforce account record.")
    ws["A3"] = ("Each segment below is a tab in this workbook. Off-sector = the logged "
                "Sub-Sector conflicts with the segment the account is filed under.")
    for cell in ("A2", "A3"):
        ws[cell].font = Font(size=10, color="FF4B5565")

    headers = ["Segment", "Accounts", "Core", "Adjacent", "Off-sector", "Unclassified",
               "Off-sector %", "Current Licenses", "Source Document"]
    for i, h in enumerate(headers, 1):
        c = ws.cell(5, i, h)
        c.fill, c.font = HDR_FILL, HDR_FONT
        c.alignment = Alignment(horizontal="center", wrap_text=True)

    row = 6
    for seg in ORD:
        rs = [r for r in recs if r["Segment"] == seg]
        if not rs:
            continue
        cc = collections.Counter(r["Sector Alignment"] for r in rs)
        lic = sum(num(r["Current Licenses"]) or 0 for r in rs)
        vals = [seg, len(rs), cc["Core"], cc["Adjacent"], cc["Off-sector"],
                cc["Unclassified"], cc["Off-sector"] / len(rs), lic, rs[0]["Source Document"]]
        for i, v in enumerate(vals, 1):
            c = ws.cell(row, i, v)
            if i in (2, 3, 4, 5, 6, 8):
                c.number_format = "#,##0"
            elif i == 7:
                c.number_format = "0.0%"
            elif i == 1:
                c.font = Font(bold=True, size=10)
        if cc["Off-sector"] / len(rs) >= 0.15:
            ws.cell(row, 7).font = Font(color="FFB34700", bold=True, size=10)
        if cc["Unclassified"]:
            ws.cell(row, 6).font = Font(color="FF6B7686", bold=True, size=10)
        row += 1

    tot = collections.Counter(r["Sector Alignment"] for r in recs)
    totals = ["TOTAL", len(recs), tot["Core"], tot["Adjacent"], tot["Off-sector"],
              tot["Unclassified"], tot["Off-sector"] / len(recs),
              sum(num(r["Current Licenses"]) or 0 for r in recs),
              "%d segments" % len({r["Segment"] for r in recs})]
    for i, v in enumerate(totals, 1):
        c = ws.cell(row, i, v)
        c.font = Font(bold=True, size=10, color=NAVY)
        c.border = Border(top=Side("thin", color=NAVY))
        if i in (2, 3, 4, 5, 6, 8):
            c.number_format = "#,##0"
        elif i == 7:
            c.number_format = "0.0%"

    for i, w in enumerate([18, 11, 9, 10, 11, 13, 12, 17, 34], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A6"

    for offset, txt in enumerate(GAPS):
        c = ws.cell(row + 2 + offset, 1, txt)
        c.font = Font(bold=offset == 0, size=10,
                      color=NAVY if offset == 0 else "FF4B5565")

    for seg in ORD:
        rs = sorted([r for r in recs if r["Segment"] == seg],
                    key=lambda r: -(num(r["Current Licenses"]) or 0))
        if not rs:
            continue
        t = wb.create_sheet(seg[:31])
        for i, (head, _src, _n, width) in enumerate(COLS, 1):
            c = t.cell(1, i, head)
            c.fill, c.font = HDR_FILL, HDR_FONT
            c.alignment = Alignment(horizontal="center", wrap_text=True)
            t.column_dimensions[get_column_letter(i)].width = width
        for ri, rec in enumerate(rs, 2):
            align = rec["Sector Alignment"]
            for ci, (_h, src, is_num, _w) in enumerate(COLS, 1):
                v = rec.get(src, "")
                c = t.cell(ri, ci, num(v) if is_num else v)
                c.font = Font(size=10)
                if is_num:
                    c.number_format = "#,##0"
                if align in FILL:
                    c.fill = FILL[align]
            t.cell(ri, 1).font = Font(size=10, bold=True)
            t.cell(ri, 3).font = FONTC[align]
        t.freeze_panes = "A2"
        t.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(COLS)), len(rs) + 1)
        t.sheet_properties.tabColor = NAVY
        print("  %-16s %5d accounts" % (seg, len(rs)))

    wb.save(OUT)
    print("wrote %s (%.1f MB)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    main()

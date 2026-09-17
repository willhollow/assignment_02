"""
main_marketing_report.py — the Marketing department's report.

Marketing does not care about individual transactions. They care about *products*:
which one earns the most money, and which one moves the most units. Those are
frequently not the same product, and the gap between them is the interesting part.

This is the payoff for building a package instead of a script. Marketing needs a
roll-up that Finance never asked for, so `summarize_by_item` and `find_top_entry`
were **added** to `sales_pipeline.transform` — and `main_finance_report.py` did
not change by a single character. That is what modular means: the package grows
by addition, not by editing everyone who already depends on it.

Before running:  pip install -r requirements.txt

    python code/main_marketing_report.py        # the fixed sample data
    python code/main_marketing_report.py 42     # the generated data for seed 42
"""

import sys

# --- The report ------------------------------------------------------------------
#
# Less scaffolding this time. The steps are described, but which function does each
# job — and what to call the result — is now yours to work out. Everything you need
# is in the package's public API; if a step sounds like arithmetic, the function
# already exists in transform.py.
#
# `main_finance_report.py` is your worked example for anything structural.

# TODO: import what this report needs from the package.
from sales_pipeline import (
    clean_sales_data,
    find_top_entry,
    get_raw_sales_data,
    print_item_table,
    summarize_by_item,
)

# TODO: handle the optional dataset seed. This is the same three lines the Finance
#       report has — read them there, then write them here yourself.
seed = None
if len(sys.argv) > 1 and sys.argv[1].strip() != "":
    seed = int(sys.argv[1])


# TODO: print the header, exactly:   === MARKETING: Revenue by Item ===
#       then a blank line.
print("=== MARKETING: Revenue by Item ===")
print()


# 1. Extract — the same source Finance uses, called the same way.
# TODO
raw_data = get_raw_sales_data(seed)


# 2. Transform — clean the rows, roll them up to one entry per item, then find the
#    best entry twice: once by "revenue", once by "units_sold". They are usually
#    different products, which is the whole reason Marketing asked.
# TODO
clean_data = clean_sales_data(raw_data)
item_summary = summarize_by_item(clean_data)
top_revenue = find_top_entry(item_summary, "revenue")
top_units = find_top_entry(item_summary, "units_sold")


# 3. Load — the item table, a blank line, then two headline lines. Match this
#    layout exactly, including the padding that lines the two values up:
#
#        Top seller by revenue: Gizmo Pro ($1,200.00)
#        Top seller by units:   Widget C (15 units)
# TODO
print_item_table(item_summary)
print()
print(
    f"Top seller by revenue: {top_revenue['item']} "
    f"(${top_revenue['revenue']:,.2f})"
)
print(
    f"Top seller by units:   {top_units['item']} "
    f"({top_units['units_sold']} units)"
)

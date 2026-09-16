"""
main_finance_report.py — the Finance department's report.

Finance cares about the audit trail: every transaction, and what the whole day
earned.

This file is an *interface*, not a library. Notice how little it does: it calls
the pipeline in order and arranges the output. Every calculation lives in
`sales_pipeline.transform`, every bit of formatting lives in
`sales_pipeline.display`. If you find yourself doing arithmetic in this file,
that logic belongs in the package instead — where it can be unit tested and where
Marketing can reuse it.

Before running:  pip install -r requirements.txt

    python code/main_finance_report.py        # the fixed sample data
    python code/main_finance_report.py 42     # the generated data for seed 42
"""

import sys

# --- Reading the dataset seed ----------------------------------------------------
#
# This block is GIVEN to you, in this report only. It is plumbing, not the lesson —
# but read it, because the next two reports need it and you will be writing it
# yourself by then.
#
# `sys.argv` is the list of words typed on the command line. sys.argv[0] is the
# script name, so an argument the user typed is sys.argv[1]. It arrives as a
# *string*, so it needs int(). A missing argument — or a blank one, which is what
# VS Code sends when you clear the seed prompt — means "use the sample data".
# See README Reference #7.

seed = None
if len(sys.argv) > 1 and sys.argv[1].strip() != "":
    seed = int(sys.argv[1])


# --- The report ------------------------------------------------------------------
#
# Fill in each TODO below. This first report names the exact function to call and
# the exact variable to store it in; the Marketing report will describe the steps
# and leave the calls to you; the Operations report gives you neither.

# TODO: import what this report needs from the package. Four names, all of them
#       listed in the steps below. Put the import at the TOP of the file, under
#       `import sys` — this comment sits here only so you can see what to import.
#
#       from sales_pipeline import (...)


# TODO: print the header, exactly:   === FINANCE: Daily Sales Detail ===
#       then print() on its own for a blank line.


# 1. Extract — get the raw data out of the source system.
#    TODO: call get_raw_sales_data(seed) and store the result in `raw_data`.


# 2. Transform — clean it, then total it.
#    TODO: call clean_sales_data(raw_data) and store it in `clean_data`.
#    TODO: call calculate_total_revenue(clean_data) and store it in `total_revenue`.


# 3. Load — put it in front of a human.
#    TODO: call print_sales_table(clean_data).
#    TODO: print() a blank line.
#    TODO: print the total. Use an f-string with the same format spec display.py
#          uses, so 1528.0 comes out as $1,528.00 and not $1528.0:
#
#              print(f"Total Pipeline Revenue: ${total_revenue:,.2f}")
#
#          That line is given because the format spec is worth seeing once. You
#          will need the same trick in the next two reports.

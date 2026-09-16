"""
main_daily_report.py — the Operations department's report.

Finance asked *what did we sell?* and Marketing asked *which products sell?*
Operations asks a third question: *when do we sell?* Same eleven rows, same
pipeline, grouped down a different column — because staffing a shop floor needs
the calendar, not the catalogue.

**You write this file yourself.** `main_finance_report.py` and
`main_marketing_report.py` are your worked examples: this report has the same
three-step shape and mostly calls functions that already exist. The one new piece
is `summarize_by_day`, which you add to `sales_pipeline.transform` — and once it
exists, `find_top_entry` ranks days exactly as happily as it ranks items, because
it never cared what an entry *was*, only which field to compare.

That is the lesson worth taking away: a third report needed one new function, not
a third script.

Before running:  pip install -r requirements.txt

    python code/main_daily_report.py        # the fixed sample data
    python code/main_daily_report.py 42     # the generated data for seed 42
"""

# --- The report ------------------------------------------------------------------
#
# No scaffolding. You have written two of these now, and this one asks the same
# three questions of the same data: extract it, transform it, show it.
#
# What you have to work out for yourself:
#
#   - which package functions this report needs, and in what order
#   - one function that does not exist yet — see README Step 9
#   - the same seed handling the other two reports do
#
# README Step 9 shows the exact output your report must produce. The integration
# tests check it line for line, so match it character for character.
#
# The rules have not changed: no arithmetic and no formatting logic in a report. If
# you need a calculation this file cannot get by calling the package, the
# calculation belongs in sales_pipeline/transform.py.

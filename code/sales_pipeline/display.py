"""
display.py — the **L** in ETL (Load: getting the result to where a human can use it).

This module is the *only* place in the pipeline that is allowed to `print`, and
the only place that decides how a number should look. `transform.py` produces
`1200.0`; this module is what turns it into `$1,200.00`.

That split is the whole point of the package. Because formatting lives here and
arithmetic lives in `transform.py`, Finance and Marketing can render the same
numbers differently without either one touching the other's code.

This module uses **tabulate**, a package from PyPI that is not part of the Python
standard library. Install it before you run anything:

    pip install -r requirements.txt
"""

from tabulate import tabulate


def print_sales_table(cleaned_data: list[dict]) -> None:
    """Print the row-level detail table — one line per sale.

    How to build it:

    - `tabulate` takes a list of dictionaries and draws a table from it, so your
      job is to build that list. Loop `cleaned_data` and append one dictionary per
      row, using the column headings you want as its keys.
    - Do the number formatting **here**: `f"${row['price']:,.2f}"`. The values
      coming out of `transform.py` are plain floats on purpose — turning them into
      strings is a display decision, and this is the display module.
    - `tabulate(rows, headers="keys", tablefmt="grid")` *returns* a string, it does
      not print one. You still need `print()` around it.
    - Print the `--- Cleaned Sales Data ---` heading before the table, so a reader
      scrolling a long report knows which table they are looking at.
    """
    rows = []

    for row in cleaned_data:
        rows.append(
            {
                "date": row["date"],
                "item": row["item"],
                "price": f"${row['price']:,.2f}",
                "qty": row["qty"],
                "revenue": f"${row['total_revenue']:,.2f}",
            }
        )

    print("--- Cleaned Sales Data ---")
    print(tabulate(rows, headers="keys", tablefmt="grid"))


def print_day_table(day_summary: list[dict]) -> None:
    """Print the by-day table — one line per calendar day, earliest first.

    Structurally identical to `print_item_table`; only the first column differs.
    """
    rows = []

    for entry in day_summary:
        rows.append(
            {
                "date": entry["date"],
                "units sold": entry["units_sold"],
                "revenue": f"${entry['revenue']:,.2f}",
            }
        )

    print("--- Sales by Day ---")
    print(tabulate(rows, headers="keys", tablefmt="grid"))


def print_item_table(item_summary: list[dict]) -> None:
    """Print the rolled-up table — one line per item, best earner first.

    How to build it:

    - Same shape as `print_sales_table`: build a list of dictionaries, format the
      revenue into a string, hand it to `tabulate`, `print` the result.
    - Do **not** sort in here. `summarize_by_item` already returned the entries in
      the right order, and a display function that quietly re-orders its input is a
      nasty bug to track down later.
    - The heading a reader sees can differ from the key your data uses — this table
      shows `units sold` while the entries carry `units_sold`. Renaming for display
      is exactly the sort of thing that belongs in this module.
    """
    rows = []

    for entry in item_summary:
        rows.append(
            {
                "item": entry["item"],
                "units sold": entry["units_sold"],
                "revenue": f"${entry['revenue']:,.2f}",
            }
        )

    print("--- Revenue by Item ---")
    print(tabulate(rows, headers="keys", tablefmt="grid"))

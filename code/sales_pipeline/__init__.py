"""
sales_pipeline — a small ETL package for the sales data.

A *package* is a folder of modules with a file called `__init__.py` in it. That file
is what turns an ordinary folder into something Python can import: delete it and
`import sales_pipeline` stops working, no matter how good the other three files are.

`__init__.py` runs the moment anybody writes `import sales_pipeline`, and its job
here is to define the package's **public API** — the short list of things a report
author is meant to use.

WHY BOTHER?
-----------
Without this file doing any work, a report would have to know exactly which module
each function lives in:

    from sales_pipeline.extract import get_raw_sales_data
    from sales_pipeline.transform import clean_sales_data, calculate_total_revenue
    from sales_pipeline.display import print_sales_table

With it, the same report says:

    from sales_pipeline import get_raw_sales_data, clean_sales_data

That is not just less typing. It means you can move a function from one module to
another later, fix the import *here*, and every report keeps working. The package's
front door stays put even when you rearrange the rooms behind it.


HOW TO BUILD IT
---------------
1.  **Import with a leading dot.** `from .transform import ...` — the `.` means
    "the module next to me, inside this same package". Without the dot Python goes
    looking for a top-level module called `transform` and fails.

2.  **Build it up as you go — this is the important one.** Export only the functions
    you have actually written. If this file imports something that does not exist
    yet, `import sales_pipeline` fails *before pytest can load the tests at all*.
    You will not see red tests; you will see no tests, and a message like:

        ERROR tests/test_unit.py
        !!!!!! Interrupted: 1 error during collection !!!!!!

    In the VS Code Testing panel they just disappear. That is alarming and almost
    always trivial: scroll up to the `ImportError` and it names the function this
    file promised that `transform.py` does not have yet. When your tests vanish,
    suspect this file first.

3.  **Group the imports by module** and keep each group alphabetical, as below. You
    are writing a table of contents; make it readable.

4.  **Leave the plumbing out.** `clean_currency` and `clean_quantity` are not here.
    They are real functions, they work, and `clean_sales_data` calls them constantly
    — but no *report* should. Anything you export is a promise you have to keep, so
    promise as little as you can get away with. A reader who scans this file should
    come away knowing what the package is *for*, not how it works inside.

5.  **List the same names again in `__all__`.** See the note above that list.

6.  **Nothing else belongs in this file.** No calculations, no printing, no data. If
    you find yourself writing a `def` in here, it belongs in one of the three
    modules instead.
"""

# --- The public API -------------------------------------------------------------
#
# One group per module. The leading dot on each is what makes these *relative*
# imports — "from the display module that sits beside this file", not "from some
# package called display installed on this machine".
from .extract import get_raw_sales_data
from .transform import (
    calculate_total_revenue,
    clean_sales_data,
    find_top_entry,
    summarize_by_day,
    summarize_by_item,
)
from .display import print_day_table, print_item_table, print_sales_table

# `__all__` is a list of strings naming the public API. It does two jobs.
#
# The mechanical one: it controls what `from sales_pipeline import *` brings in.
#
# The one that actually matters: it is documentation with teeth. The imports above
# are something Python *needs*; this list is you stating plainly which names are
# features. Anyone can read it and know what the package does without opening a
# single module.
#
# Keep it in step with the imports above. A name here that is not imported above is
# a broken promise; a name imported above but missing here is a feature nobody can
# find.
__all__ = [
    "get_raw_sales_data",
    "calculate_total_revenue",
    "clean_sales_data",
    "find_top_entry",
    "summarize_by_day",
    "summarize_by_item",
    "print_day_table",
    "print_item_table",
    "print_sales_table",
]

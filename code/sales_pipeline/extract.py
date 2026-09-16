"""
extract.py — the **E** in ETL.  *(This module is provided for you.)*

Extract is the step that gets data *out* of the source system and into Python. It
does not clean anything and it does not print anything. Whatever the source hands
us, we hand along unchanged — warts and all.

Keeping Extract separate is what lets the rest of the pipeline stay honest: when
the numbers look wrong, you can always come back here and see exactly what
arrived, before anybody touched it.

You do not need to modify this file, but you *do* need to read it — you cannot
clean data you do not understand. Pay attention to the ways a price or a quantity
can be broken, because your Transform functions have to survive all of them
without crashing.
"""

import random

# (item name, true unit price) — the catalog the sales come from.
CATALOG = [
    ("Widget A", 12.50),
    ("Widget B", 15.00),
    ("Widget C", 8.00),
    ("Gadget X", 24.00),
    ("Gizmo Lite", 1050.00),
    ("Gizmo Pro", 1200.00),
]

# The fixed dataset. Small enough to reason about by hand, messy enough to hurt.
_SAMPLE_DATA = [
    {"date": "2023-10-01", "item": "Widget A", "price": "$12.50", "qty": "4"},
    {"date": "2023-10-01", "item": "Gadget X", "price": "24.00", "qty": 2},
    {"date": "2023-10-02", "item": "Widget B", "price": "15.00", "qty": 2},
    {"date": "2023-10-02", "item": "Widget A", "price": "$12.50", "qty": "one"},
    {"date": "2023-10-03", "item": "Widget C", "price": None, "qty": 5},
    {"date": "2023-10-03", "item": "Widget B", "price": "$15.00", "qty": "3"},
    {"date": "2023-10-04", "item": "Gizmo Pro", "price": "$1,200.00", "qty": 1},
    {"date": "2023-10-04", "item": "Widget A", "price": "$12.50", "qty": 6},
    {"date": "2023-10-04", "item": "Gadget X", "price": "", "qty": 1},
    {"date": "2023-10-05", "item": "Widget C", "price": "$8.00", "qty": "10"},
    {"date": "2023-10-05", "item": "Widget B", "price": "15.00", "qty": None},
]


def get_raw_sales_data(seed: int | None = None) -> list[dict]:
    """Return raw sales records exactly as the source system provides them.

    Call it with no argument to get the **fixed sample dataset** — 11 rows you can
    check by hand:

        get_raw_sales_data()          # always the same 11 rows

    Call it with a `seed` to get a **generated dataset** of 40 rows. The same seed
    always produces the same rows, so a report is reproducible, but a different
    seed produces different data:

        get_raw_sales_data(42)        # always the same 40 rows
        get_raw_sales_data(7)         # a different 40 rows, every time the same

    This matters for you: your Transform functions have to actually *work*, not
    just produce the right answer for the 11 rows you can see. The tests run your
    code against several seeds.

    The data is deliberately messy, because real exports are deliberately messy:

    - prices arrive as strings, sometimes with a `$`, sometimes with a `,`
    - prices are sometimes missing (`None`), blank (`""`), or garbage (`"N/A"`)
    - quantities arrive sometimes as `int`, sometimes as `str`
    - a human sometimes types a word (`"one"`, `"two"`, `"zero"`) into a quantity field
    - a quantity is sometimes missing (`None`) or blank (`""`)

    Nothing here is cleaned. Cleaning is the Transform step's job.
    """
    if seed is None:
        # Return a copy so a caller who mutates rows cannot corrupt the sample.
        return [dict(row) for row in _SAMPLE_DATA]
    return _generate_sales_data(seed)


def _generate_sales_data(seed: int, row_count: int = 40) -> list[dict]:
    """Build `row_count` messy rows deterministically from `seed`."""
    rng = random.Random(seed)
    rows = []

    for _ in range(row_count):
        item, price = rng.choice(CATALOG)
        rows.append(
            {
                "date": f"2023-10-{rng.randrange(1, 29):02d}",
                "item": item,
                "price": _messy_price(rng, price),
                "qty": _messy_quantity(rng),
            }
        )

    return rows


def _messy_price(rng: random.Random, price: float):
    """Return `price` in one of the shapes the source system actually emits."""
    roll = rng.randrange(100)

    if roll < 8:
        return None                      # field absent
    if roll < 12:
        return ""                        # field present but blank
    if roll < 15:
        return "N/A"                     # someone typed into a numeric field
    if roll < 45:
        return f"${price:,.2f}"          # "$1,200.00"
    if roll < 75:
        return f"{price:.2f}"            # "15.00"
    return price                         # a real float, already clean


def _messy_quantity(rng: random.Random):
    """Return a quantity in one of the shapes the source system actually emits."""
    roll = rng.randrange(100)

    if roll < 8:
        return None                      # field absent
    if roll < 11:
        return ""                        # field present but blank
    if roll < 15:
        return rng.choice(["one", "two", "zero"])    # a word, not a number
    if roll < 20:
        return "0"                       # a genuine zero-sale row
    if roll < 60:
        return str(rng.randrange(1, 13))  # "7"
    return rng.randrange(1, 13)          # a real int, already clean

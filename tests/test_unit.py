"""Unit tests — exercise the functions in code/sales_pipeline/ directly.

These tests run your functions against **two** kinds of data:

1. the fixed sample dataset, `get_raw_sales_data()` — 11 rows you can check by hand
2. several **generated** datasets, `get_raw_sales_data(seed)` — 40 rows each

The seeded datasets are the reason you cannot shortcut this assignment. The same
seed always produces the same rows, so the expected answers below are stable — but
they are not answers you can eyeball and hardcode. The only way to make them pass
is for your Transform functions to genuinely work.

Every step after `clean_sales_data` is tested **twice**, on purpose:

- `test_summarize_by_item` is **scoped** — it hands the function a small dataset
  that is already clean, so it tests that one function and nothing else. Write
  `summarize_by_item` correctly and this passes, even if `clean_sales_data` is
  still empty or broken.
- `test_summarize_by_item_on_generated_data` is **wired** — it reaches the same
  function through the whole pipeline on seeded data, so it only passes once every
  earlier step works too.

That split means you earn credit for each function as you finish it, and when
something breaks the pair tells you *where*: scoped failing means the function
itself is wrong, scoped passing while wired fails means the function is fine and
something upstream is feeding it bad data.
"""

import pytest

import sales_pipeline

# These import from the module that owns each function, rather than from the
# package, on purpose. It means these tests still run while `__init__.py` is empty
# or half-finished — you get honest red and green for the functions you are working
# on, instead of one collection error and no tests at all.
#
# Whether the *package* re-exports everything properly is a separate question, and
# `test_package_exposes_public_api` below is the test that asks it.
from sales_pipeline.extract import get_raw_sales_data
from sales_pipeline.transform import (
    calculate_total_revenue,
    clean_currency,
    clean_quantity,
    clean_sales_data,
    find_top_entry,
    summarize_by_day,
    summarize_by_item,
)

# Everything sales_pipeline/__init__.py must expose to a report author.
PUBLIC_API = [
    "get_raw_sales_data",
    "clean_sales_data",
    "calculate_total_revenue",
    "summarize_by_item",
    "summarize_by_day",
    "find_top_entry",
    "print_sales_table",
    "print_item_table",
    "print_day_table",
]

# --- Expected results for the fixed sample dataset -------------------------------

SAMPLE_ROWS = 11
SAMPLE_REVENUE = 1528.00
# (item, units_sold, revenue) in the order summarize_by_item must return them.
SAMPLE_SUMMARY = [
    ("Gizmo Pro", 1, 1200.00),
    ("Widget A", 10, 125.00),
    ("Widget C", 15, 80.00),
    ("Widget B", 5, 75.00),
    ("Gadget X", 3, 48.00),
]


# --- A hand-written cleaned dataset ----------------------------------------------
#
# Everything downstream of clean_sales_data is tested against this literal first,
# so those functions can pass on their own merits even if an earlier step of the
# pipeline is still unfinished or broken. Different item names than the real data,
# on purpose — nothing here should look familiar.

CLEANED = [
    {"date": "2023-11-01", "item": "Bolt", "price": 2.50, "qty": 4,
     "total_revenue": 10.00},
    {"date": "2023-11-01", "item": "Nut", "price": 0.75, "qty": 8,
     "total_revenue": 6.00},
    {"date": "2023-11-02", "item": "Bolt", "price": 2.50, "qty": 0,
     "total_revenue": 0.00},
    {"date": "2023-11-02", "item": "Anvil", "price": 0.00, "qty": 3,
     "total_revenue": 0.00},
    {"date": "2023-11-03", "item": "Anvil", "price": 95.00, "qty": 2,
     "total_revenue": 190.00},
    {"date": "2023-11-03", "item": "Nut", "price": 0.00, "qty": 0,
     "total_revenue": 0.00},
]

CLEANED_REVENUE = 206.00
CLEANED_SUMMARY = [
    ("Anvil", 5, 190.00),
    ("Bolt", 4, 10.00),
    ("Nut", 8, 6.00),
]
# The same six rows grouped by date instead. Note the order: earliest day first,
# NOT highest revenue first — 2023-11-01 earned $16.00 and 2023-11-03 earned
# $190.00, so a by-item sort copied across would put these the other way round.
CLEANED_DAYS = [
    ("2023-11-01", 12, 16.00),
    ("2023-11-02", 3, 0.00),
    ("2023-11-03", 2, 190.00),
]


# --- Expected results for the generated datasets ---------------------------------

SEEDED = {
    3: {
        "revenue": 83619.50,
        "summary": [
            ("Gizmo Pro", 43, 51600.00),
            ("Gizmo Lite", 39, 29400.00),
            ("Gadget X", 66, 1584.00),
            ("Widget A", 53, 562.50),
            ("Widget B", 23, 345.00),
            ("Widget C", 24, 128.00),
        ],
        "top_revenue": ("Gizmo Pro", 51600.00),
        "top_units": ("Gadget X", 66),
        "day_count": 22,
        "top_day_revenue": ("2023-10-28", 35117.50),
        "top_day_units": ("2023-10-28", 52),
    },
    7: {
        "revenue": 82088.00,
        "summary": [
            ("Gizmo Lite", 39, 40950.00),
            ("Gizmo Pro", 44, 39600.00),
            ("Gadget X", 19, 456.00),
            ("Widget A", 39, 450.00),
            ("Widget C", 49, 392.00),
            ("Widget B", 16, 240.00),
        ],
        "top_revenue": ("Gizmo Lite", 40950.00),
        "top_units": ("Widget C", 49),
        "day_count": 21,
        "top_day_revenue": ("2023-10-02", 16982.50),
        "top_day_units": ("2023-10-24", 28),
    },
    9: {
        "revenue": 54030.50,
        "summary": [
            ("Gizmo Pro", 37, 32400.00),
            ("Gizmo Lite", 30, 19950.00),
            ("Widget A", 61, 762.50),
            ("Widget B", 39, 510.00),
            ("Gadget X", 15, 360.00),
            ("Widget C", 17, 48.00),
        ],
        "top_revenue": ("Gizmo Pro", 32400.00),
        "top_units": ("Widget A", 61),
        "day_count": 21,
        "top_day_revenue": ("2023-10-12", 12096.00),
        "top_day_units": ("2023-10-04", 31),
    },
    42: {
        "revenue": 98844.50,
        "summary": [
            ("Gizmo Lite", 51, 53550.00),
            ("Gizmo Pro", 51, 44400.00),
            ("Widget C", 50, 312.00),
            ("Gadget X", 10, 240.00),
            ("Widget B", 19, 180.00),
            ("Widget A", 13, 162.50),
        ],
        "top_revenue": ("Gizmo Lite", 53550.00),
        "top_units": ("Gizmo Lite", 51),
        "day_count": 22,
        "top_day_revenue": ("2023-10-14", 14108.00),
        "top_day_units": ("2023-10-04", 26),
    },
}

SEEDS = sorted(SEEDED)


def as_tuples(item_summary: list[dict]) -> list[tuple]:
    """Flatten summarize_by_item output so it is easy to compare."""
    return [
        (entry["item"], entry["units_sold"], round(entry["revenue"], 2))
        for entry in item_summary
    ]


# --- The package itself ----------------------------------------------------------


def test_package_exposes_public_api():
    """__init__.py lifts the whole public API up to the package level.

    Checks that `from sales_pipeline import <name>` works for all nine public
    functions, and that `__all__` lists exactly those — nothing promised that
    isn't there, and no internal helper leaking out into the front door.

    This is the last test to go green. It needs every public function to exist, so
    build `__init__.py` up as you go — export only what you have actually written,
    or the import fails and takes every other test in the suite down with it.
    """
    for name in PUBLIC_API:
        assert hasattr(sales_pipeline, name), (
            f"sales_pipeline/__init__.py does not expose {name!r}. "
            "Import it there so reports can use `from sales_pipeline import ...`."
        )

    assert sorted(getattr(sales_pipeline, "__all__", [])) == sorted(PUBLIC_API), (
        "sales_pipeline/__init__.py should define __all__ listing exactly the "
        "public API — no more, no less."
    )


# --- Extract ---------------------------------------------------------------------


def test_get_raw_sales_data_returns_the_sample_dataset():
    """Called with no argument, Extract hands back the 11-row sample.

    Checks the shape only — a list of dictionaries carrying exactly the four raw
    keys. The values are deliberately messy at this stage, so there is nothing
    else worth asserting: cleaning them is Transform's job, not Extract's.
    """
    raw_data = get_raw_sales_data()

    assert isinstance(raw_data, list)
    assert len(raw_data) == SAMPLE_ROWS
    for row in raw_data:
        assert set(row) == {"date", "item", "price", "qty"}


def test_get_raw_sales_data_is_reproducible_per_seed():
    """A seed makes the generated data repeatable without making it predictable.

    Three things have to hold for the seeded tests below to mean anything: the
    same seed twice gives identical rows (so a report can be re-run and audited),
    two different seeds disagree (so those tests are not all quietly running the
    same data), and a seeded dataset is 40 rows rather than the 11-row sample.
    """
    # The same seed must always give the same rows...
    assert get_raw_sales_data(42) == get_raw_sales_data(42)
    # ...and a different seed must give different rows.
    assert get_raw_sales_data(42) != get_raw_sales_data(7)
    assert len(get_raw_sales_data(42)) == 40


# --- Transform: coercion ---------------------------------------------------------


def test_clean_currency():
    """Prices become floats, and unreadable prices become 0.0 instead of an error.

    Covers every shape the source system emits — `$`-prefixed, plain text,
    thousands-separated, and already a float — then the five that cannot be read.
    Those last ones are the important half: if this function raises instead of
    returning 0.0, a single `"N/A"` takes down a report of 400 good rows.
    """
    assert clean_currency("$12.50") == pytest.approx(12.50)
    assert clean_currency("15.00") == pytest.approx(15.00)
    assert clean_currency("$1,200.00") == pytest.approx(1200.00)
    assert clean_currency(24.0) == pytest.approx(24.00)

    # Anything unreadable becomes 0.0 rather than crashing the pipeline.
    for value in (None, "", "   ", "N/A", "twelve"):
        assert clean_currency(value) == pytest.approx(0.0), (
            f"clean_currency({value!r}) should return 0.0, not raise"
        )


def test_clean_quantity():
    """Quantities become ints, and unreadable quantities become 0 instead of an error.

    The same contract as `clean_currency`, on the shapes a quantity arrives in:
    text digits, real ints, and padded text like `" 7 "`. Note `"0"` is a genuine
    number and must come back as 0 through the *conversion* path, while the word
    `"zero"` cannot be read and reaches 0 through the *failure* path.
    """
    assert clean_quantity("4") == 4
    assert clean_quantity(4) == 4
    assert clean_quantity(" 7 ") == 7
    assert clean_quantity("0") == 0

    for value in (None, "", "   ", "one", "zero", "N/A"):
        assert clean_quantity(value) == 0, (
            f"clean_quantity({value!r}) should return 0, not raise"
        )


# --- Transform: the pipeline steps -----------------------------------------------


def test_clean_sales_data():
    """Every raw row becomes a cleaned row that carries its own revenue.

    Checks four things: no rows were dropped or duplicated, the key set is exactly
    right (so `total_revenue` was added and nothing was lost along the way), the
    coercion actually happened (`price` is a float, `qty` is an int), and
    `total_revenue` really is the *cleaned* price times the *cleaned* quantity —
    not a number computed from the raw values before cleaning.
    """
    clean_data = clean_sales_data(get_raw_sales_data())

    assert len(clean_data) == SAMPLE_ROWS
    for row in clean_data:
        assert set(row) == {"date", "item", "price", "qty", "total_revenue"}
        assert isinstance(row["price"], float)
        assert isinstance(row["qty"], int)
        # total_revenue must be derived from the *cleaned* numbers.
        assert row["total_revenue"] == pytest.approx(row["price"] * row["qty"])

    first = clean_data[0]
    assert first["price"] == pytest.approx(12.50)
    assert first["qty"] == 4
    assert first["total_revenue"] == pytest.approx(50.00)


def test_calculate_total_revenue():
    """Scoped: the accumulator on its own, given rows that are already clean.

    Feeds the hand-written CLEANED fixture straight in, so this passes on the
    merit of `calculate_total_revenue` alone — even with `clean_sales_data` still
    empty. The empty-list case is the one that catches an accumulator started at
    1 instead of 0.
    """
    assert calculate_total_revenue(CLEANED) == pytest.approx(CLEANED_REVENUE)
    assert calculate_total_revenue([]) == pytest.approx(0.0)


def test_calculate_total_revenue_on_generated_data():
    """Wired: the same total reached through the whole pipeline.

    Runs the sample and four seeded datasets end to end, so it only goes green
    once Extract, `clean_currency`, `clean_quantity`, `clean_sales_data` and this
    function all agree. The seeded totals run to five figures over 40 unseen rows,
    so there is no working them out on paper and typing in the answer.
    """
    sample = clean_sales_data(get_raw_sales_data())
    assert calculate_total_revenue(sample) == pytest.approx(SAMPLE_REVENUE)

    for seed in SEEDS:
        clean_data = clean_sales_data(get_raw_sales_data(seed))
        assert calculate_total_revenue(clean_data) == pytest.approx(
            SEEDED[seed]["revenue"]
        ), f"wrong total revenue for seed {seed}"


def test_summarize_by_item():
    """Scoped: the group-by on its own, given rows that are already clean.

    The fixture spreads three items across six rows, which is what makes this
    meaningful: a function that forgot to group would return six entries instead
    of three. Also checks that units and revenue *both* accumulate, and that the
    result comes back sorted by revenue highest first rather than in the order the
    items happened to first appear.
    """
    assert as_tuples(summarize_by_item(CLEANED)) == CLEANED_SUMMARY, (
        "check your grouping, your totals, and that you sorted by revenue "
        "highest first"
    )
    assert summarize_by_item([]) == []


def test_summarize_by_item_on_generated_data():
    """Wired: the same roll-up reached through the whole pipeline.

    Compares the full ordered summary — every item, its units and its revenue —
    for the sample and four seeded datasets. Because the ordering is part of the
    comparison, this also catches a sort that happens to look right on the sample
    but breaks on data with a different revenue spread.
    """
    sample = clean_sales_data(get_raw_sales_data())
    assert as_tuples(summarize_by_item(sample)) == SAMPLE_SUMMARY

    for seed in SEEDS:
        clean_data = clean_sales_data(get_raw_sales_data(seed))
        assert as_tuples(summarize_by_item(clean_data)) == SEEDED[seed]["summary"], (
            f"wrong item summary for seed {seed}"
        )


def test_summarize_by_day():
    """Scoped: the same group-by asked of a different column, and sorted differently.

    The fixture's six rows fall on three dates. The expected order is the one that
    catches a copy-paste of `summarize_by_item`: days come back **earliest first**,
    so 2023-11-01 ($16.00) leads and 2023-11-03 ($190.00) trails. Carry the
    revenue-descending sort across from the item version and this fails
    immediately, which is exactly what should happen — the sort is a decision about
    what the reader needs, not boilerplate.
    """
    day_summary = summarize_by_day(CLEANED)
    as_days = [
        (entry["date"], entry["units_sold"], round(entry["revenue"], 2))
        for entry in day_summary
    ]

    assert as_days == CLEANED_DAYS
    assert summarize_by_day([]) == []


def test_summarize_by_day_on_generated_data():
    """Wired: the day roll-up through the whole pipeline, checked by invariants.

    A seeded dataset spreads 40 rows over 20-odd dates, too many to pin out by
    hand, so this checks properties that only a correct roll-up can satisfy:

    - the dates come back in ascending order, with no day appearing twice
    - the day revenues add up to the same total `calculate_total_revenue` reports
      over the raw rows — the same money counted two different ways
    - the busiest day by revenue and by units match the expected dates

    That last pair is the interesting one. They are usually *different* days: one
    expensive sale can win the revenue crown on a quiet day.
    """
    for seed in SEEDS:
        clean_data = clean_sales_data(get_raw_sales_data(seed))
        day_summary = summarize_by_day(clean_data)
        dates = [entry["date"] for entry in day_summary]

        assert len(day_summary) == SEEDED[seed]["day_count"], (
            f"wrong number of days for seed {seed} — one entry per date, no repeats"
        )
        assert dates == sorted(dates), f"days out of order for seed {seed}"
        assert len(dates) == len(set(dates)), f"a date appears twice for seed {seed}"

        day_total = sum(entry["revenue"] for entry in day_summary)
        assert day_total == pytest.approx(calculate_total_revenue(clean_data)), (
            f"day revenues do not add up to the pipeline total for seed {seed}"
        )

        expected_date, expected_revenue = SEEDED[seed]["top_day_revenue"]
        busiest = find_top_entry(day_summary, "revenue")
        assert busiest["date"] == expected_date, f"wrong top revenue day for seed {seed}"
        assert busiest["revenue"] == pytest.approx(expected_revenue)

        expected_date, expected_units = SEEDED[seed]["top_day_units"]
        busiest = find_top_entry(day_summary, "units_sold")
        assert busiest["date"] == expected_date, f"wrong top units day for seed {seed}"
        assert busiest["units_sold"] == expected_units


def test_find_top_entry():
    """Scoped: the max search on its own, given a summary list built by hand.

    The fixture is ordered deliberately: the top earner is the **first** entry but
    the top mover is the **last** one. That is what stops a function that simply
    returns `summary[0]` from passing — it would be right about revenue and wrong
    about units. Also checks the guard that keeps an empty summary from raising an
    IndexError.

    The last block is why this function is called `find_top_entry` and not
    `find_top_item`: handed a list of *days* it works just as well, because it only
    ever compares `entry[field]` and never asks what the entry represents. Write it
    that way and Operations gets its report for free.
    """
    summary = [
        {"item": "Anvil", "units_sold": 5, "revenue": 190.00},
        {"item": "Bolt", "units_sold": 4, "revenue": 10.00},
        {"item": "Nut", "units_sold": 8, "revenue": 6.00},
    ]

    top_earner = find_top_entry(summary, "revenue")
    assert top_earner["item"] == "Anvil"
    assert top_earner["revenue"] == pytest.approx(190.00)

    # The biggest earner and the biggest mover are different items, and the biggest
    # mover is last in the list — so this cannot pass by returning summary[0].
    top_mover = find_top_entry(summary, "units_sold")
    assert top_mover["item"] == "Nut"
    assert top_mover["units_sold"] == 8

    assert find_top_entry([], "revenue") == {}

    # The same function, over day entries instead of item entries.
    days = [
        {"date": "2023-11-01", "units_sold": 12, "revenue": 16.00},
        {"date": "2023-11-02", "units_sold": 3, "revenue": 0.00},
        {"date": "2023-11-03", "units_sold": 2, "revenue": 190.00},
    ]
    assert find_top_entry(days, "revenue")["date"] == "2023-11-03"
    assert find_top_entry(days, "units_sold")["date"] == "2023-11-01"


def test_find_top_entry_on_generated_data():
    """Wired: the same search reached through the whole pipeline.

    On the sample the biggest earner (Gizmo Pro) and the biggest mover (Widget C)
    are different products, and across the four seeds both answers move around —
    the earner is sometimes Gizmo Pro and sometimes Gizmo Lite, the mover is a
    different item almost every time. Neither can be hardcoded.
    """
    sample_summary = summarize_by_item(clean_sales_data(get_raw_sales_data()))

    top_earner = find_top_entry(sample_summary, "revenue")
    assert top_earner["item"] == "Gizmo Pro"
    assert top_earner["revenue"] == pytest.approx(1200.00)

    top_mover = find_top_entry(sample_summary, "units_sold")
    assert top_mover["item"] == "Widget C"
    assert top_mover["units_sold"] == 15

    for seed in SEEDS:
        summary = summarize_by_item(clean_sales_data(get_raw_sales_data(seed)))

        expected_item, expected_revenue = SEEDED[seed]["top_revenue"]
        earner = find_top_entry(summary, "revenue")
        assert earner["item"] == expected_item, f"wrong top earner for seed {seed}"
        assert earner["revenue"] == pytest.approx(expected_revenue)

        expected_item, expected_units = SEEDED[seed]["top_units"]
        mover = find_top_entry(summary, "units_sold")
        assert mover["item"] == expected_item, f"wrong top mover for seed {seed}"
        assert mover["units_sold"] == expected_units

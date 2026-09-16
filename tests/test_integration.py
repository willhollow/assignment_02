"""Integration tests — run all three report programs end-to-end.

Unit tests check that each function is right on its own. These check that the
*wiring* is right: that each report actually imports the package, calls the steps
in the correct order, and prints what its department asked for.

Every report is run against the fixed sample data and against generated datasets
(passed as a command-line seed), so a report cannot pass by printing a
hardcoded block of text.
"""

import ast
import os

from helpers import repo_path, run_python_script

FINANCE = "code/main_finance_report.py"
MARKETING = "code/main_marketing_report.py"
DAILY = "code/main_daily_report.py"
ALL_REPORTS = (FINANCE, MARKETING, DAILY)


# --- Structure -------------------------------------------------------------------


def test_package_directory_structure():
    """The pipeline is four modules in a folder, not one big file.

    Checks that all four required files exist under code/sales_pipeline/.
    `__init__.py` is the one that carries real weight — it is what makes the
    folder a *package*; without it `import sales_pipeline` fails outright and
    every other test in the suite goes red.
    """
    for filename in ("__init__.py", "extract.py", "transform.py", "display.py"):
        path = repo_path("code", "sales_pipeline", filename)
        assert os.path.exists(path), f"missing required file code/sales_pipeline/{filename}"


def test_reports_use_the_package():
    """The reports consume the package instead of re-implementing it.

    Checks two things about each report: that it imports from `sales_pipeline`,
    and that it does *not* import tabulate — building tables is display.py's job.
    This is the only test that can catch a report which pasted the logic in
    directly, because a copy-paste report still prints the right numbers and still
    passes every unit test.

    It reads the *parsed* imports rather than searching the text, so a mention of
    `from sales_pipeline import ...` in a comment or docstring does not count as
    having written one, and the word "tabulate" in a comment is not mistaken for
    importing it.
    """
    for script in ALL_REPORTS:
        with open(repo_path(script)) as source_file:
            source = source_file.read()

        imported_from = set()
        for node in ast.walk(ast.parse(source, filename=script)):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_from.add(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported_from.add(alias.name.split(".")[0])

        assert "sales_pipeline" in imported_from, (
            f"{script} should import what it needs from the package, e.g. "
            "`from sales_pipeline import get_raw_sales_data, clean_sales_data`"
        )
        assert "tabulate" not in imported_from, (
            f"{script} should not import tabulate — table formatting belongs in "
            "sales_pipeline/display.py, not in a report."
        )


# --- Finance report --------------------------------------------------------------


def test_finance_report_prints_the_detail_table():
    """Finance gets row-level detail, formatted for a human to read.

    Checks the headings, that real row data reached the table, and that the
    thousands separator survived formatting (`$1,200.00`, not `$1200.00`). The
    `$0.00` assertion matters most: rows whose price or quantity could not be read
    must still appear in the table, valued at zero, rather than being quietly
    dropped so the report looks tidier than the data deserves.
    """
    output = run_python_script(FINANCE)

    assert "=== FINANCE: Daily Sales Detail ===" in output
    assert "--- Cleaned Sales Data ---" in output

    # Row-level detail, formatted for a human: note the thousands separator.
    assert "Gizmo Pro" in output
    assert "$1,200.00" in output

    # Rows whose price or quantity could not be read still appear, worth $0.00.
    assert "$0.00" in output


def test_finance_report_prints_total_revenue():
    """Finance's bottom line is right for the sample data.

    $1,528.00 is the whole 11-row pipeline, including the four rows that coerced
    to zero. A report that dropped bad rows instead of zeroing them would still
    print a plausible-looking total, and this is what catches it.
    """
    output = run_python_script(FINANCE)
    assert "Total Pipeline Revenue: $1,528.00" in output


def test_finance_report_accepts_a_dataset_seed():
    """A seed typed on the command line reaches Extract and changes the report.

    Two seeds must produce two different totals, which means `sys.argv` was read,
    converted with `int()` (it arrives as a string), and passed through to
    `get_raw_sales_data`. It also proves the printed total is computed from the
    data rather than being a hardcoded line of text.
    """
    output = run_python_script(FINANCE, 42)
    assert "Total Pipeline Revenue: $98,844.50" in output

    output = run_python_script(FINANCE, 7)
    assert "Total Pipeline Revenue: $82,088.00" in output


# --- Marketing report ------------------------------------------------------------


def test_marketing_report_prints_the_item_table():
    """Marketing gets one line per item, ordered by revenue.

    Checks the headings, then locates each item's line number in the printed
    output and asserts those numbers ascend — so the table is genuinely sorted
    best-earner-first on the page, not merely present. `units sold` also confirms
    the display module renamed the `units_sold` key for its human heading.
    """
    output = run_python_script(MARKETING)

    assert "=== MARKETING: Revenue by Item ===" in output
    assert "--- Revenue by Item ---" in output
    assert "units sold" in output

    # Rolled up to one line per item, best earner first.
    lines = output.splitlines()
    positions = [
        next(i for i, line in enumerate(lines) if item in line)
        for item in ("Gizmo Pro", "Widget A", "Widget C", "Widget B", "Gadget X")
    ]
    assert positions == sorted(positions), (
        "items should be listed by revenue, highest first"
    )


def test_marketing_report_prints_top_sellers():
    """Marketing's two headline answers — and they are different products.

    Gizmo Pro earns the most money; Widget C moves the most units. Because the two
    answers differ, a report that computed the top earner and reused it for both
    lines fails here. This is the question Marketing actually wanted answered: the
    expensive thing that pays the bills is rarely the thing everyone buys.
    """
    output = run_python_script(MARKETING)

    # The biggest earner and the biggest mover are different items — that is the
    # whole reason Marketing wanted this report.
    assert "Top seller by revenue: Gizmo Pro ($1,200.00)" in output
    assert "Top seller by units:   Widget C (15 units)" in output


def test_marketing_report_accepts_a_dataset_seed():
    """The seed reaches Marketing too, and both answers move with the data.

    On seed 7 the top earner is Gizmo Lite; on seed 9 it is Gizmo Pro, and the top
    mover changes as well. Four different answers across two runs means neither
    line can be a hardcoded string, and that `find_top_entry` is really being asked
    two separate questions rather than one asked twice.
    """
    output = run_python_script(MARKETING, 7)
    assert "Top seller by revenue: Gizmo Lite ($40,950.00)" in output
    assert "Top seller by units:   Widget C (49 units)" in output

    output = run_python_script(MARKETING, 9)
    assert "Top seller by revenue: Gizmo Pro ($32,400.00)" in output
    assert "Top seller by units:   Widget A (61 units)" in output


# --- Daily report (you write this one) -------------------------------------------


def test_daily_report_prints_the_day_table():
    """Operations gets one line per calendar day, in date order.

    Checks the headings, then locates each date's line in the output and asserts
    they run **earliest first** — the opposite ordering decision from the Marketing
    table, and the one that lets a reader see a trend rather than a ranking.

    The five sample dates also confirm the roll-up collapsed eleven rows onto the
    days they happened on, rather than printing a line per sale.
    """
    output = run_python_script(DAILY)

    assert "=== OPERATIONS: Sales by Day ===" in output
    assert "--- Sales by Day ---" in output
    assert "units sold" in output

    lines = output.splitlines()
    positions = [
        next(i for i, line in enumerate(lines) if date in line)
        for date in (
            "2023-10-01",
            "2023-10-02",
            "2023-10-03",
            "2023-10-04",
            "2023-10-05",
        )
    ]
    assert positions == sorted(positions), "days should be listed earliest first"


def test_daily_report_prints_the_busiest_days():
    """Operations' headline answers — and the two busiest days are different days.

    2023-10-04 took the most money ($1,275.00) on the back of a single Gizmo Pro
    sale, while 2023-10-05 shifted the most units (10). Reusing one answer for both
    lines fails here.

    The total is the same $1,528.00 the Finance report prints, which is the useful
    cross-check: grouping the money by day cannot change how much money there was.
    """
    output = run_python_script(DAILY)

    assert "Total Revenue:          $1,528.00" in output
    assert "Busiest day by revenue: 2023-10-04 ($1,275.00)" in output
    assert "Busiest day by units:   2023-10-05 (10 units)" in output


def test_daily_report_accepts_a_dataset_seed():
    """The seed reaches the daily report, and the busiest days move with the data.

    A generated dataset spreads its rows over most of October rather than five
    days, so the answers here look nothing like the sample's — which is the proof
    that the dates are being computed from the data rather than typed in.
    """
    output = run_python_script(DAILY, 7)
    assert "Total Revenue:          $82,088.00" in output
    assert "Busiest day by revenue: 2023-10-02 ($16,982.50)" in output
    assert "Busiest day by units:   2023-10-24 (28 units)" in output

    output = run_python_script(DAILY, 9)
    assert "Total Revenue:          $54,030.50" in output
    assert "Busiest day by revenue: 2023-10-12 ($12,096.00)" in output
    assert "Busiest day by units:   2023-10-04 (31 units)" in output


# --- All three together ----------------------------------------------------------


def test_reports_treat_a_blank_seed_as_no_seed():
    """A blank command-line argument falls back to the sample data.

    The VS Code debug configuration "Python Debugger: Current File (with dataset
    seed)" always passes its prompt through as `sys.argv[1]`, even when you clear
    the box — a launch configuration cannot leave an argument out conditionally.
    So the reports receive `""` rather than nothing at all, and `int("")` raises.

    Checking for a blank argument as well as a missing one is what keeps the
    optional seed genuinely optional: clearing the prompt gives you the sample
    data instead of a ValueError traceback.
    """
    for script in ALL_REPORTS:
        blank = run_python_script(script, "")
        absent = run_python_script(script)

        # A report that prints nothing at all would satisfy "" == "" without doing
        # any work, so require real output before comparing.
        assert "===" in blank, f"{script} printed no report header"
        assert blank == absent, (
            f"{script} should treat a blank seed argument the same as no argument"
        )


def test_reports_never_crash_on_bad_data():
    """The one rule that matters: a bad row must not take down the report.

    Every one of these six datasets contains missing prices, blank fields, `"N/A"`
    where a number should be, and words typed into quantity fields. Both reports
    must run all twelve times without raising.

    Nothing is asserted about the output here — `run_python_script` fails the test
    if the program exits non-zero, so this checks survival rather than answers. It
    is the broadest safety net in the suite: the other tests use four seeds, and a
    coercion bug that only triggers on some rarer combination shows up here.
    """
    for seed in (1, 3, 7, 9, 42, 123):
        for script in ALL_REPORTS:
            output = run_python_script(script, seed)

            # Surviving by doing nothing is not surviving. Every run has to produce
            # a real report, with a table in it, on every one of these datasets.
            assert "===" in output, f"{script} printed no report for seed {seed}"
            assert "+---" in output, f"{script} printed no table for seed {seed}"

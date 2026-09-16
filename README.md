# IST356 Assignment 02 — Sales Data Pipeline

You are a Junior Data Analyst. Three departments want a report off the same sales export:

- **Finance** wants every transaction, and what the day earned.
- **Marketing** wants to know which product earns the most, and which moves the most units.
- **Operations** wants to know *when* the sales happen, so they can staff the floor.

The tempting move is to write one script for Finance, then copy-paste it and edit the
bottom half for Marketing, then do it a third time for Operations. Now you have three
scripts that will drift apart, and eventually disagree with each other about what
"revenue" means.

So you won't. You'll build a **package** — a folder of modules, each responsible for one
stage of an **ETL** pipeline (Extract, Transform, Load) — and then write three thin
programs on top of it. The logic lives in exactly one place; the reports just arrange the
output.

Watch what the third report costs you. Finance and Marketing are walked through step by
step; Operations you write yourself, and it needs exactly **one** new function, because
everything else it wants already exists. That is the whole argument for building a
package, and you'll feel it rather than be told it.

There's a second lesson buried in the data: **the export is broken.** Prices go missing,
someone typed `"one"` into a quantity field. Real exports always look like this, and one
bad row must never take down a report built on hundreds of good ones.

## Meta

### Learning Objectives

By the end of this assignment you will be able to:

1. **Build a Python package** — a folder of modules with an `__init__.py`
2. **Separate concerns** across modules by responsibility (Extract / Transform / Load)
3. **Use relative imports** (`from .transform import ...`) inside a package
4. **Design a public API** — decide what `__init__.py` exposes and what stays internal
5. **Use a third-party package** from PyPI (`tabulate`), and know how `requirements.txt`
   declares what a project depends on
6. **Coerce messy values** — strings, `None`, blanks — into numbers without crashing
7. **Aggregate with a dictionary accumulator** — a "group by" written out by hand
8. **Recognise a pattern and re-apply it** — group the same rows down a different column
9. **Sort a list of dictionaries**, and choose an order that suits the reader
10. **Reuse one package from three programs** without duplicating logic
11. **Tell unit tests from integration tests** and know which catches which bug
12. **Use the debugger** to inspect values when a test fails
13. **Submit for grading** and act on the feedback

### Assignment Layout

- `code/` — **where you write code.** Only files in this folder are reviewed for grading.
  - `sales_pipeline/` — the **package**
    - `__init__.py` — **you write this.** Declares the package's public API
    - `extract.py` — **provided for you.** Produces the raw, messy data
    - `transform.py` — **you write this.** The cleaning and the math
    - `display.py` — **provided for you.** The only module allowed to `print` or format
  - `main_finance_report.py` — the **Finance** program (walked through step by step)
  - `main_marketing_report.py` — the **Marketing** program (walked through step by step)
  - `main_daily_report.py` — the **Operations** program (**you write this one yourself**)
  - `reflection.txt` — **where you write your reflection** (graded)
- `tests/` — the automated tests that check your code
  - `test_unit.py` — **Unit Tests** for the functions in the package
  - `test_integration.py` — **Integration Tests** that run all three reports end-to-end
- `grader/` — the autograder used by GraderThan (you don't touch this)
- `.devcontainer/` — configures the pre-built course dev container (`mafudge/ist356:latest`)
- `.vscode/` — run / debug / test configurations for VS Code
- `README.md` — these instructions
- `reflection.md` — how to write a good reflection
- `rubric.json` / `requirements.txt` — grading rubric and Python dependencies

You write **seven functions** in `transform.py`, the `__init__.py` that exposes them, and
**three report programs**. `extract.py` and `display.py` are given to you — read them, but
don't change them.

### Prerequisites

Same environment as Assignment 01, plus one new third-party package, **tabulate**. The
dev container installs it for you the first time it builds, by running
`pip install -r requirements.txt` — so normally there is nothing for you to do. If an
import ever fails, [Reference #1](#1-how-do-i-install-a-package-from-pypi) shows you how
to run that yourself.

If you haven't done the one-time course setup yet:

👉 https://mafudge.github.io/ist356/0-intro/0-0-setup.html

This assignment runs inside the pre-built course dev container
(`mafudge/ist356:latest`), the same one Assignment 01 used.

> **No computer setup? Use GitHub Codespaces** to run everything in your browser — you
> only need a GitHub account.

---

## Prep — Open the assignment

Same as Assignment 01: **first fork, then** pick **one** of two ways to open your fork
in the course environment.

1. **Fork this repository.** At the top-right of this repo's GitHub page, click
   **Fork**. This makes your own personal copy under your GitHub account. You submit
   and are graded on *your fork* — work done anywhere else cannot be graded.

Now choose **Option A** (in the browser — nothing to install) **or** **Option B** (on
your own computer). Everything in the Walkthrough works the same either way.

### Option A — GitHub Codespaces (in the browser) ⭐ easiest

A Codespace runs the exact same course container **in the cloud** and opens VS Code in
your browser — nothing to install, so this works on a Chromebook, a lab machine, or a
locked-down laptop.

1. Go to **your fork's** page on GitHub. Click the green **Code** button, then the
   **Codespaces** tab.
2. Click **Create codespace on main**. The container builds (the first time takes a few
   minutes) and installs this assignment's dependencies for you.
3. VS Code opens in your browser, already **inside the course container**, with your
   fork's code loaded and Git signed in. You can skip cloning — you're ready.

> Reopen an existing Codespace anytime from **https://github.com/codespaces** (or the
> **Code → Codespaces** tab on your fork). Codespaces have monthly free hours, so
> **stop** yours when you're done: `github.com/codespaces` → **⋯ → Stop codespace**.

### Option B — Your own computer (local dev container)

Requires Docker Desktop and VS Code from the [course setup](https://mafudge.github.io/ist356/0-intro/0-0-setup.html).

1. **Clone your fork.** On your fork's page, click the green **Code** button and copy
   the HTTPS URL, then clone it. Easiest way: in VS Code press `Ctrl+Shift+P` →
   **Git: Clone**, paste the URL, and pick a folder. Or from a terminal:

   ```sh
   git clone https://github.com/YOUR-GITHUB-USERNAME/assignment_02.git
   ```

   > Make sure the URL has **your** username in it, not `ist356`. If it doesn't, you
   > cloned the wrong repo — and nothing you commit will reach your grade.

2. **Open the folder and reopen in the container.** Choose **File → Open Folder** and
   select the cloned `assignment_02` folder. VS Code detects the dev container and pops
   up a notification — click **Reopen in Container**. (If you miss it:
   `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**.) The first build takes a
   few minutes; after that you're working *inside* the course environment.

### Check you're ready

Open the **Testing** panel (View → Testing) and run the tests
([Reference #5](#5-how-do-i-run-automated-tests)). You should see **3 passing and 24
failing** — that is exactly right. The three that pass cover `extract.py`, which is
written for you; the rest fail because you haven't written anything yet.

If instead you see *no tests at all*, that is a different problem — see the note in
[Step 5](#step-5--declare-the-public-api-and-write-the-finance-report).

---

## About the data — read this before you start

`extract.py` is written for you, and it hands you data two ways:

```python
get_raw_sales_data()      # the fixed sample: 11 rows, small enough to check by hand
get_raw_sales_data(42)    # a generated dataset: 40 rows, the same 40 every time
```

A **seed** is just a number that makes randomness repeatable. Seed `42` always produces
the exact same 40 rows, so a report built on it is reproducible — but seed `7` produces
a different 40 rows.

**The tests run your code against several seeds.** This is deliberate. It means you
cannot look at the 11 sample rows, work the answer out on paper, and type the answer
into your function. There is no version of "make the test pass" here that isn't
"actually write the thing." That's the point: in the real job, tomorrow's export is
never today's export.

Here is every way the source system will hurt you:

| field | arrives as | what to do with it |
| --- | --- | --- |
| `price` | `"$12.50"`, `"15.00"`, `"$1,200.00"`, `15.0` | strip the `$` and the `,`, then convert |
| `price` | `None`, `""`, `"N/A"` | unreadable → `0.0` |
| `qty` | `"4"`, `4`, `" 7 "`, `"0"` | convert — note it's sometimes `str`, sometimes `int` |
| `qty` | `None`, `""`, `"one"`, `"two"`, `"zero"` | unreadable → `0` |

The rule for the whole right-hand column: **coerce and carry on.** A value you cannot
read becomes zero, and the report keeps going. What you must never do is let `float("N/A")`
raise its way out of your function and kill the run.

---

## Walkthrough — Do the assignment step by step

Work in order. Each step tells you *what* to do; when you need the *mechanics*, follow
the link to the matching **Reference — How do I…?** entry below.

### The training wheels come off

The three reports do the same job, so they are deliberately **not** supported equally.
Open each file and you'll find a different amount of help waiting:

| report | what the file gives you |
| --- | --- |
| `main_finance_report.py` | the seed-handling code written out, and a TODO per line naming the exact function to call and what to store the result in |
| `main_marketing_report.py` | the three steps described in words — which function does each job is yours to work out |
| `main_daily_report.py` | the goal, and nothing else |

That is on purpose. By the third one you should be reaching for the two finished reports
beside it rather than for a list of instructions — which is exactly what you'll do on the
job, where the "instructions" are always just the code someone wrote last month.

### Build order at a glance

Write things in this order and watch the Testing panel go green a row at a time. Nothing
later needs anything you haven't written yet.

| order | write this | in | turns green |
| --- | --- | --- | --- |
| 1 | *(check `tabulate` is installed)* | — | — |
| 2 | `clean_currency` | `transform.py` | `test_clean_currency` |
| 3 | `clean_quantity` | `transform.py` | `test_clean_quantity` |
| 4 | `clean_sales_data` | `transform.py` | `test_clean_sales_data` |
| 5 | `calculate_total_revenue` | `transform.py` | `test_calculate_total_revenue` ×2 |
| 6 | the public API *so far* | `__init__.py` | — |
| 7 | the Finance report | `main_finance_report.py` | the `finance` integration tests |
| 8 | `summarize_by_item` | `transform.py` | `test_summarize_by_item` ×2 |
| 9 | `find_top_entry` | `transform.py` | `test_find_top_entry` ×2 |
| 10 | the Marketing report | `main_marketing_report.py` | the `marketing` integration tests |
| 11 | `summarize_by_day` | `transform.py` | `test_summarize_by_day` ×2 |
| 12 | the Operations report | `main_daily_report.py` | the `daily` integration tests |
| 13 | finish the public API | `__init__.py` | `test_package_exposes_public_api` |

Every function's docstring ends with a **How to build it** section — the approach, the
pattern to reach for, and the mistake people usually make. Read it before you start
typing, not after you get stuck.

> **Build `__init__.py` up as you go.** Export only what you have actually written. If it
> imports a function that doesn't exist yet, `import sales_pipeline` fails and *every*
> test in the suite goes red at once — which looks like a disaster and is really a typo.
> That's why it appears twice above, and why `test_package_exposes_public_api` is the last
> test to pass.

**Why some rows say ×2.** Every step after `clean_sales_data` has two unit tests. The
plain one (`test_summarize_by_item`) is **scoped**: it hands your function a small
dataset that is already clean, so it tests that function and nothing else. The
`_on_generated_data` one runs the same function through the *whole* pipeline on seeded
data, so it only passes once every earlier step works too.

That's deliberate, and it's in your favour twice over. You get credit for each function
the moment you finish it, even if something earlier is still broken. And when a pair
disagrees, it tells you where to look: **scoped failing** means the function itself is
wrong; **scoped passing but wired failing** means your function is fine and something
upstream is handing it bad data.

### Step 1 — Check `tabulate` is installed

Your display module uses **tabulate**, a package from PyPI that draws text tables. It is
not part of the Python standard library, so it has to be installed separately — and the
dev container already did that when it built, from `requirements.txt`.

Confirm it in a terminal (View → Terminal):

```
python -c "import tabulate; print(tabulate.__version__)"
```

A version number means you're set. A `ModuleNotFoundError` means the install didn't
happen — [Reference #1](#1-how-do-i-install-a-package-from-pypi) shows you how to run it
yourself.

### Step 2 — Read what you've been given

Open `code/sales_pipeline/extract.py` and `code/sales_pipeline/display.py`. You don't
write either one, but you *do* have to read them — you cannot clean data you don't
understand, and you cannot call a display function without knowing what shape of list it
expects.

In `extract.py`, find the spot where each kind of mess gets introduced and match it
against the table above. In `display.py`, notice that all three functions take a list of
dictionaries and that none of them do any arithmetic.

### Step 3 — Transform, part 1: coercion

In `transform.py`, write the two functions that turn a messy value into a usable one:
`clean_currency` and `clean_quantity`. Each is about five lines.

The rule for both: **never crash.** `float("N/A")` raises a `ValueError`. Catch it and
return zero rather than letting one bad row kill the whole report. `"$1,200.00"` also
needs both the `$` and the `,` stripped before `float()` will take it.

Run the unit tests ([Reference #5](#5-how-do-i-run-automated-tests)). `test_clean_currency`
and `test_clean_quantity` should go green.

> Stuck? Set a breakpoint and debug it ([Reference #6](#6-how-do-i-use-the-vs-code-debugger)).

### Step 4 — Transform, part 2: run the pipeline

Write `clean_sales_data` and `calculate_total_revenue`.

`clean_sales_data` is the heart of it: loop the raw rows and build a cleaned row for each
one by **calling the two functions you just wrote** — that's the point of writing them.
Then add a `total_revenue` key (price × qty), computed from the **cleaned** numbers, not
the raw ones.

Make `test_clean_sales_data` and `test_calculate_total_revenue` pass — then the
`_on_generated_data` partner. That partner is the first test to run your code over the
seeded datasets, so this is where "I worked the answer out from the sample rows" stops
being a strategy.

### Step 5 — Declare the public API and write the Finance report

Now `__init__.py` — the file that turns the folder into a package. **Open it and read
the comments before you write anything**; it carries its own `HOW TO BUILD IT` notes,
the same way each function in `transform.py` does. [Reference #3](#3-how-do-i-import-from-my-own-package)
covers the import mechanics.

Use **relative imports** to pull up the functions a report author needs, and list the
same names in `__all__`. Export only the four you have written so far, plus
`get_raw_sales_data` and `print_sales_table` — you'll add the rest as you go.

Be deliberate about what you leave out. `clean_currency` and `clean_quantity` are
plumbing: they stay in `transform.py`, where `clean_sales_data` can reach them. Exposing
only the functions a report actually calls tells the next reader which parts are features
and which are internals.

> **The failure mode to recognise.** If this file imports a function you haven't written
> yet, `import sales_pipeline` fails before any test can run. You don't get red tests —
> you get no tests, and a message like:
>
> ```
> ERROR tests/test_unit.py
> !!!!!! Interrupted: 1 error during collection !!!!!!
> ```
>
> In the Testing panel the tests simply vanish. That is not your logic breaking; it is
> pytest saying it couldn't even load the file. Scroll up to the `ImportError`, and it
> names the function this file promised but `transform.py` doesn't have yet.

Then write `code/main_finance_report.py`: extract → transform → display, plus an optional
command-line seed. Run it ([Reference #7](#7-how-do-i-run-a-terminal-console-app)):

```
python code/main_finance_report.py
python code/main_finance_report.py 42
```

### Step 6 — Commit and get early feedback

Commit with the message `sales pipeline: finance report`
([Reference #9](#9-how-do-i-commit-my-changes-in-vs-code)), push
([Reference #10](#10-how-do-i-push-my-code-to-github)), and submit to GraderThan
([Reference #12](#12-how-do-i-submit-for-grading--and-review-my-feedback--with-graderthan)).

Some unit tests should score; most integration tests won't, because two of the three
reports don't exist yet. That's the point — see what partial credit looks like.

### Step 7 — Transform, part 3: the roll-up

Marketing needs two things Finance never asked for. Add them to `transform.py`:

- `summarize_by_item` — the **group by**. Use a dictionary keyed by item name as your
  accumulator, adding each row's units and revenue into it, then turn `.values()` back
  into a list. Sort it by revenue, highest first, breaking ties alphabetically so the
  order is always the same for the same data.
- `find_top_entry(summary, field)` — a max-accumulator: walk the list and keep the entry
  with the largest value in `field`.

Note the name: `find_top_entry`, not `find_top_item`. It compares `entry[field]` and
never asks what an entry *is*, so it can rank anything you hand it. Keep it that way —
you'll want it again in Step 9.

### Step 8 — Write the Marketing report

`code/main_marketing_report.py` prints the by-item table, then the top seller by revenue
and the top seller by units. Export the new functions from `__init__.py` first.

Those two "top sellers" are usually different products — the cheap thing everyone buys
versus the expensive thing that pays the bills. Make sure your output shows both.

### Step 9 — Write the Operations report *(on your own)*

Operations wants a third view of the same eleven rows: **not** what sold, but *when* it
sold. There is no walkthrough for this one. You have two finished reports to learn from
and one new function to write.

Add `summarize_by_day(cleaned_data)` to `transform.py`. It is `summarize_by_item` asked
of a different column — group on `row["date"]`, give each entry a `date` key — with one
deliberate difference: sort it by **date, earliest first**. A ranking of products wants
the biggest first; a run of days wants the order they happened in, so the reader can see
a trend.

Then write `code/main_daily_report.py` from scratch. `find_top_entry` already ranks days
for you, and `calculate_total_revenue` already totals the rows, so the only genuinely new
code in the whole report is that one function. Your output must look exactly like this:

```
=== OPERATIONS: Sales by Day ===

--- Sales by Day ---
+------------+--------------+-----------+
| date       |   units sold | revenue   |
+============+==============+===========+
| 2023-10-01 |            6 | $98.00    |
+------------+--------------+-----------+
| 2023-10-02 |            2 | $30.00    |
+------------+--------------+-----------+
| 2023-10-03 |            8 | $45.00    |
+------------+--------------+-----------+
| 2023-10-04 |            8 | $1,275.00 |
+------------+--------------+-----------+
| 2023-10-05 |           10 | $80.00    |
+------------+--------------+-----------+

Total Revenue:          $1,528.00
Busiest day by revenue: 2023-10-04 ($1,275.00)
Busiest day by units:   2023-10-05 (10 units)
```

Two things worth noticing in that output. The total is the same `$1,528.00` the Finance
report prints — grouping money by day cannot change how much money there was, so that's
a free check on your work. And the busiest day by revenue is *not* the busiest day by
units: 2023-10-04 took the most money on the back of a single expensive sale, while
2023-10-05 shifted the most stock.

### Step 10 — Make the integration tests pass

Run the integration tests ([Reference #5](#5-how-do-i-run-automated-tests)). They check
the package structure, that your reports import from the package rather than
re-implementing anything, and the exact text all three reports print — for the sample
data *and* for seeded datasets. If one fails, read the failure message; it says what it
expected and what it got.

### Step 11 — Write your reflection

Read `reflection.md`, then write yours in `code/reflection.txt`. Be **specific**, use the
**terminology** from this assignment (package, module, ETL, coercion, public API,
relative import, accumulator, group by, unit vs. integration test), and make it
**actionable**.

### Step 12 — Final submit

Commit `assignment complete`, push, and submit again
([Reference #9–12](#9-how-do-i-commit-my-changes-in-vs-code)). Read your feedback and fix
anything flagged — you get multiple attempts before the due date.

---
## Reference — How do I…?

> **Using GitHub Codespaces?** Every entry works exactly the same — it's the same VS Code
> and the same course container, just in your browser.

### 1. How do I install a package from PyPI?

**PyPI** (the Python Package Index) is the public library of installable Python packages.
`pip` is the tool that downloads and installs from it.

The dev container runs this for you when it first builds, so you should not normally need
it. But it's worth knowing what it does, because this is how every Python project you
ever join gets set up. From a terminal (View → Terminal), at the repository root:

```
pip install -r requirements.txt
```

That reads `requirements.txt` — the file where a project declares what it depends on —
and installs everything listed. It's better than `pip install tabulate` because the
dependency is *recorded*: anyone who clones this repo, including the autograder, gets the
same packages by running one command instead of guessing.

Check it worked:

```
python -c "import tabulate; print(tabulate.__version__)"
```

If you ever get `ModuleNotFoundError: No module named 'tabulate'` — most likely because
you're running outside the container — running the `pip install` line above fixes it.

### 2. How do I create a Python package?

A package is a **folder** containing a file named `__init__.py`:

```
code/sales_pipeline/
├── __init__.py     <-- this file is what makes it a package
├── extract.py
├── transform.py
└── display.py
```

In the Explorer, right-click `code/` → **New Folder** → `sales_pipeline`, then
right-click that folder → **New File** for each `.py` file. `__init__.py` may be empty
at first — it still has to exist.

### 3. How do I import from my own package?

**Inside** the package, use a **relative import** — the leading `.` means "this package":

```python
# in sales_pipeline/__init__.py
from .extract import get_raw_sales_data
from .transform import clean_sales_data, calculate_total_revenue
```

**Outside** the package, import from the package name:

```python
# in main_finance_report.py
from sales_pipeline import get_raw_sales_data, clean_sales_data
```

Because `main_finance_report.py` sits next to the `sales_pipeline/` folder, Python finds
it automatically. Import the **names you need**, not the whole module — it makes the
dependency obvious to anyone reading your code.

`__all__` is a list of strings naming the public API. It documents intent and controls
what `from sales_pipeline import *` would bring in.

### 4. How do I format a number as currency?

Use an f-string **format spec**: `,` adds thousands separators, `.2f` fixes two decimals.

```python
price = 1200.0
print(f"${price:,.2f}")      # $1,200.00
print(f"${price:.2f}")       # $1200.00   (no separator)
```

Formatting is a *display* decision. Keep it in `display.py` and in your report's
`print()` calls — never store a formatted string back into your data.

### 5. How do I run automated tests?

Open **Testing** in the activity bar (View → Testing). Press ▶ next to a test to run it,
or ▶ at the top to run them all. Green check = pass, red X = fail. Click a failed test to
see the assertion, expected vs. actual, and the line number.

You can also run them in the terminal from the repository root:

```
pytest tests/test_unit.py -v
pytest tests/test_integration.py -v
```

### 6. How do I use the VS Code debugger?

Click in the gutter left of a line number to set a **breakpoint** (red dot). Press `F5`
and choose **Python Debugger: Current File**. Use the **VARIABLES** panel to inspect
values and the stepping controls to move line by line (`F10` steps over, `F11` steps in).

There are two configurations for running a report:

| choose | what it runs the report on |
| --- | --- |
| **Python Debugger: Current File** | the fixed 11-row sample data |
| **Python Debugger: Current File (with dataset seed)** | prompts for a seed, then uses that generated dataset |

Debugging on a seeded dataset is the fastest way to understand a failing
`_on_generated_data` test: set a breakpoint in your function, launch with the seed the
test used, and look at the rows it's actually being handed.

Automated tests do **not** stop at breakpoints. To debug a function in `transform.py`,
add an `if __name__ == '__main__':` block at the bottom of that file, call the function
from there, and debug that file:

```python
if __name__ == '__main__':
    print(clean_currency("$1,200.00"))
```

### 7. How do I run a terminal (console) app?

Open a terminal (View → Terminal) and, from the repository root, run:

```
python code/main_finance_report.py            # the fixed sample data
python code/main_finance_report.py 42         # the generated data for seed 42
python code/main_marketing_report.py 7        # a different dataset again
```

The number after the filename is a **command-line argument**. Your program reads it from
`sys.argv`, which is a list of the words typed on the command line — `sys.argv[0]` is the
script name, so your seed is `sys.argv[1]`. It's a string, so convert it with `int()`.

Check that the argument is both **present and not blank** before converting it. The
debugger's seed prompt always passes something through, even when you clear the box, so
your report can receive `""` — and `int("")` raises a `ValueError`. Treat a blank
argument the same as no argument and fall back to the sample data.

### 8. How do I see what my report printed, all at once?

Terminal output scrolls. To capture it in a file you can scroll and search:

```
python code/main_finance_report.py > output.txt
```

Don't commit `output.txt` — it's scratch.

### 9. How do I commit my changes in VS Code?

View → Source Control. Type a commit message in the box, then click **Commit**. Commit
after each working piece — not once at the end.

### 10. How do I push my code to GitHub?

In Source Control, click **Sync Changes** (or the ⋯ menu → Push). In Codespaces you're
already signed in.

### 11. How do I see my code on GitHub?

Open your fork in the browser: `https://github.com/YOUR-GITHUB-USERNAME/assignment_02`.
If your latest change isn't there, it isn't pushed — and GraderThan won't see it.

### 12. How do I submit for grading — and review my feedback — with GraderThan?

GraderThan runs the autograder (unit + integration tests) and an AI reviewer (code style,
reflection) against your fork, then gives you a score and detailed, per-criterion
feedback.

**Submit:**

1. Go to **https://graderthan.cent-su.org** and log in with your SU Microsoft account.
2. On **Your dashboard**, click this assignment.
3. **First time only:** if you see **"Link your GitHub account first,"** click
   **Profile** → **Connect GitHub** and authorize it. You only do this once.
4. Under **Request grading**, submit your **fork's GitHub URL**
   (e.g. `https://github.com/YOUR-GITHUB-USERNAME/assignment_02`). Click **Submit for
   Grading and Feedback.**

> Always **commit and push before you submit** — GraderThan only sees what's on GitHub.
> You get multiple attempts, so submit early and often.

**Review your feedback:** scroll to **"Your submissions"** and click one. `AUTOMATED`
criteria show the raw test output (e.g. `14/14 tests passed`); `AI-JUDGED` criteria show
a written paragraph, the specific lines flagged, and a **"How to improve"** tip. Fix
what's flagged, commit, push, and submit again.

---
## The Assignment — what to actually do

### 1. The package — `code/sales_pipeline/`

`extract.py` and `display.py` are provided. You write `transform.py` and `__init__.py`.

**`transform.py`** — no `print()`, no `input()`, no files. Values in, values out.

| function | what it returns |
| --- | --- |
| `clean_currency(value)` | the price as a `float`, or `0.0` if unreadable |
| `clean_quantity(value)` | the quantity as an `int`, or `0` if unreadable |
| `clean_sales_data(raw_data)` | cleaned rows, each with an added `total_revenue` |
| `calculate_total_revenue(cleaned_data)` | every row's revenue added together |
| `summarize_by_item(cleaned_data)` | one entry per item (`item`, `units_sold`, `revenue`), highest revenue first |
| `summarize_by_day(cleaned_data)` | one entry per date (`date`, `units_sold`, `revenue`), earliest first |
| `find_top_entry(summary, field)` | the entry with the largest value in `field`; `{}` if empty |

**`display.py`** — *provided.* The only module that prints. Uses `tabulate`.

| function | what it does |
| --- | --- |
| `print_sales_table(cleaned_data)` | row-level detail table, one line per sale |
| `print_item_table(item_summary)` | one row per item, best earner first |
| `print_day_table(day_summary)` | one row per day, earliest first |

**`__init__.py`** — relative imports that expose the nine functions a report needs
(`get_raw_sales_data`, the six `transform` functions, and the three `display` functions),
plus an `__all__` listing exactly those. `clean_currency` and `clean_quantity` stay
internal.

### 2. The programs — three of them, in `code/`

| program | department | what it answers |
| --- | --- | --- |
| `main_finance_report.py` | Finance | every transaction, and what the day earned |
| `main_marketing_report.py` | Marketing | which product earns most, which moves most units |
| `main_daily_report.py` | Operations | **you write this** — when do we sell? |

Each imports from `sales_pipeline`, accepts an optional seed as a command-line argument,
and prints its department's report. **No arithmetic and no formatting logic in these
files** — if you're calculating in a report, it belongs in the package.

Implement them so the **Integration Tests** (`tests/test_integration.py`) pass.

### 3. Reflection

Read `reflection.md`, then write your reflection in `code/reflection.txt`. A good
reflection is **specific**, **uses the terminology** from this assignment, and is
**actionable**.

---
## How You're Graded

GraderThan scores this assignment out of **10 points** (see `rubric.json`):

| What | Points | Judged by |
| --- | --- | --- |
| **Unit Tests** — `test_unit.py` (the `sales_pipeline` functions) | 3 | automated tests |
| **Integration Tests** — `test_integration.py` (all three reports end-to-end) | 3 | automated tests |
| Code style & readability | 2 | AI reviewer |
| Reflection quality | 2 | AI reviewer |

**Only files in the `code/` folder are graded.** Commit, push, and submit
([Reference #9–12](#9-how-do-i-commit-my-changes-in-vs-code)) to get your score and
feedback.

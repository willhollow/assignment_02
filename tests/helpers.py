"""Shared helpers for the integration tests."""

import os
import sys

from subprocess import run

# tests/ lives directly under the repository root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def repo_path(*parts: str) -> str:
    """Build an absolute path from the repository root, whatever the working directory."""
    return os.path.join(REPO_ROOT, *parts)


def run_python_script(script_path: str, *args, input_text: str = "") -> str:
    """Run a script in a fresh interpreter and return whatever it printed.

    Extra positional arguments are passed to the script on the command line, so a
    report can be run against a specific dataset seed:

        run_python_script("code/main_finance_report.py", 42)
    """
    process = run(
        [sys.executable, repo_path(script_path), *[str(arg) for arg in args]],
        text=True,
        capture_output=True,
        input=input_text,
    )

    if process.returncode != 0:
        raise AssertionError(
            f"{script_path} exited with code {process.returncode}.\n"
            f"--- stderr ---\n{process.stderr.strip()}"
        )

    return process.stdout.strip()

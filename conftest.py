"""Make the package in code/ importable from the tests (e.g. `import sales_pipeline`)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "code"))


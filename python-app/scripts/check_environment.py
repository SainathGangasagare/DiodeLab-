#!/usr/bin/env python3
"""Report the runtime and key dependency versions for DiodeLab."""
import sys

try:
    import sklearn
except Exception as exc:
    print(f"Could not import scikit-learn: {exc}")
    raise SystemExit(1)

print(f"Python: {sys.version.split()[0]}")
print(f"scikit-learn: {sklearn.__version__}")

if sklearn.__version__ != "1.6.1":
    print("WARNING: this environment does not match requirements.txt (1.6.1).")
    raise SystemExit(2)

print("Environment check passed: scikit-learn matches the project pin.")


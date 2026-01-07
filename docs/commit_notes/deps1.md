# Deps1

What changed
- Pinned MediaPipe to a known good version and limited it to Python < 3.13.
- Documented the MediaPipe version requirement in build docs.

Manual test steps
- Run `python3 -m pip install -e .` in a Python 3.11/3.12 venv.
- Verify MediaPipe installs and hand tracking initializes.

Known issues
- Hand tracking is unavailable on Python 3.13+ due to MediaPipe support limits.

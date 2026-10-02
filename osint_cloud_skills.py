#!/usr/bin/env python3
"""Backward-compatible entrypoint -> cli/osint_skills.py """
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / "cli" / "osint_skills.py"), run_name="__main__")

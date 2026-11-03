"""Vercel entry point: runs the FastAPI backend (back_end/main.py) as a function.

vercel.json sends every /api/... request here; FastAPI sees the original path.
"""

import os
import sys

BACK_END = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "back_end")
sys.path.insert(0, BACK_END)

from main import app  # noqa: E402,F401

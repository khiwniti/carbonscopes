"""Convenient entry point for loading TGO data.

Runs the loader with a default sample file if present.
"""

import os
from pathlib import Path

DEFAULT_SAMPLE = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "sample_data"
    / "tgo_materials_sample.json"
)

if __name__ == "__main__":
    if DEFAULT_SAMPLE.is_file():
        os.system(f"python -m backend.scripts.load_tgo_data {DEFAULT_SAMPLE}")
    else:
        print("No sample JSON file found at", DEFAULT_SAMPLE)

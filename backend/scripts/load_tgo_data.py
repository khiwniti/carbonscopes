"""Script to load TGO emission factor data into GraphDB.

Usage:
    python -m backend.scripts.load_tgo_data <path-to-json>
"""

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)  # add project root to PYTHONPATH

from core.services.graphdb import get_graph, release_graph
from core.knowledge_graph.tgo_loader import load_from_json_file


def main(json_path: str):
    path = Path(json_path)
    if not path.is_file():
        print(f"File not found: {json_path}")
        sys.exit(1)
    g = get_graph()
    try:
        load_from_json_file(path, g)
        print(f"Loaded materials from {json_path} into GraphDB repository.")
    finally:
        release_graph(g)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m backend.scripts.load_tgo_data <json-file>")
        sys.exit(1)
    main(sys.argv[1])

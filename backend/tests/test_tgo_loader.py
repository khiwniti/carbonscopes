import pytest
from pathlib import Path

# Import loader function (ensuring PYTHONPATH includes project root)
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from core.knowledge_graph.tgo_loader import load_from_json_file
from core.services.graphdb import get_graph, release_graph


@pytest.mark.asyncio
async def test_load_sample_tgo_data(tmp_path):
    # Use the sample JSON provided in tests/sample_data
    sample_file = Path(__file__).parent / "sample_data" / "tgo_materials_sample.json"
    assert sample_file.is_file()
    g = get_graph()
    try:
        load_from_json_file(sample_file, g)
        # Perform a simple query to verify at least one triple exists for concrete
        res = g.query("""
            PREFIX tgo: <http://tgo.or.th/ontology#>
            SELECT ?material WHERE { ?material a tgo:ConstructionMaterial . }
        """)
        results = list(res)
        assert len(results) >= 2
    finally:
        release_graph(g)

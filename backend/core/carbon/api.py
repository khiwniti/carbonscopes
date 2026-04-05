"""Carbon‑related REST endpoints.

- **POST /v1/tgo/load** – load a TGO material JSON file into GraphDB (or in‑memory).
- **POST /v1/carbon/calculate** – calculate total embodied carbon for a list of
  materials using the deterministic Brightway2 calculator.
- **GET /v1/certify/edge** – run the EDGE V3 certification SPARQL query and return
  the PASS/FAIL status.
- **GET /v1/certify/trees** – run the TREES MR1 compliance SPARQL query and return
  the PASS/FAIL status.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from pydantic import BaseModel
from pathlib import Path
from typing import List, Dict, Any

from core.knowledge_graph.tgo_loader import load_from_json_file
from core.services.graphdb import get_graph, release_graph
from core.carbon.brightway.calculator import CarbonCalculator
from rdflib import Graph

router = APIRouter(prefix="/v1", tags=["carbon"])


# ---------------------------------------------------------------------------
# TGO material loading
# ---------------------------------------------------------------------------
@router.post("/tgo/load")
async def load_tgo_materials(file: UploadFile = File(...)):
    """Accept a JSON file upload and load its material definitions.

    The file is stored temporarily, parsed, and material triples are added to a
    GraphDB (or in‑memory Graph when the DB is unavailable).
    """
    try:
        # Read uploaded content into a temporary location
        temp_path = Path("/tmp") / file.filename
        with temp_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        g = get_graph()
        load_from_json_file(temp_path, g)
        release_graph(g)
        return {"status": "success", "message": f"Loaded {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# Carbon calculation endpoint
# ---------------------------------------------------------------------------
class MaterialItem(BaseModel):
    material_id: str
    quantity: float
    unit: str


class CarbonCalcRequest(BaseModel):
    materials: List[MaterialItem]


@router.post("/carbon/calculate")
async def calculate_carbon(request: CarbonCalcRequest):
    """Calculate total embodied carbon for the supplied material list.
    Returns the total carbon value and a per‑material breakdown.
    """
    try:
        calc = CarbonCalculator()
        # Convert to list of dicts expected by calculator
        mats = [
            {"material_id": m.material_id, "quantity": m.quantity, "unit": m.unit}
            for m in request.materials
        ]
        result = calc.calculate_project_carbon(mats)
        # Convert Decimal to string for JSON serialization
        result["total_carbon"] = str(result["total_carbon"])
        for b in result["material_breakdown"]:
            b["total_carbon"] = str(b["total_carbon"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Project summary endpoint (Phase 2 placeholder)
# ---------------------------------------------------------------------------
from fastapi import Path as FastAPIPath
from pathlib import Path as StdPath
import json

# Simple file‑based persistence for project summaries (dev/testing only)
_PROJECT_SUMMARY_DIR = StdPath("/tmp/project_summaries")
_PROJECT_SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/project/{project_id}/summary")
async def project_summary(
    project_id: str = FastAPIPath(..., description="Unique identifier for the project"),
    request: CarbonCalcRequest = Body(None),
):
    """Calculate and persist a carbon summary for ``project_id``.

    • If ``request`` is omitted, returns the stored summary (or an empty one).
    • When a body with material data is provided, the calculation is performed,
      the JSON result is saved to a simple file store, and the summary is
      returned.
    """
    summary_path = _PROJECT_SUMMARY_DIR / f"{project_id}.json"
    # If a request body is provided, (re)calculate and store the summary
    if request is not None:
        calc = CarbonCalculator()
        mats = [
            {"material_id": m.material_id, "quantity": m.quantity, "unit": m.unit}
            for m in request.materials
        ]
        result = calc.calculate_project_carbon(mats)
        # Serialize Decimals for JSON
        result["total_carbon"] = str(result["total_carbon"])
        for b in result["material_breakdown"]:
            b["total_carbon"] = str(b["total_carbon"])
        result["project_id"] = project_id
        # Persist to file (overwrite any existing entry)
        summary_path.write_text(json.dumps(result, ensure_ascii=False))
        return result
    # No request body – try to read a stored summary
    if summary_path.is_file():
        stored = json.loads(summary_path.read_text())
        return stored
    # No stored data – return empty placeholder
    return {"project_id": project_id, "total_carbon": "0", "material_breakdown": []}


# ---------------------------------------------------------------------------
# Certification queries
# ---------------------------------------------------------------------------
def _run_query(ontology_path: Path, query_path: Path) -> Dict[str, Any]:
    g = Graph()
    g.parse(str(ontology_path), format="turtle")
    query = query_path.read_text()
    res = g.query(query)
    rows = list(res)
    if not rows:
        raise ValueError("No results from query")
    # Assume the last binding is the status
    row = rows[0]
    # Convert rdflib Literal to python value
    status = str(row[-1].toPython()) if hasattr(row[-1], "toPython") else str(row[-1])
    return {"status": status}


@router.get("/certify/edge")
async def certify_edge():
    ont = Path(__file__).parents[3] / "knowledge_graph" / "ontologies" / "edge-v3.ttl"
    qry = (
        Path(__file__).parents[3]
        / "knowledge_graph"
        / "queries"
        / "edge_certification.sparql"
    )
    try:
        return _run_query(ont, qry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/certify/trees")
async def certify_trees():
    ont = (
        Path(__file__).parents[3]
        / "knowledge_graph"
        / "ontologies"
        / "trees-nc-1.1.ttl"
    )
    qry = (
        Path(__file__).parents[3]
        / "knowledge_graph"
        / "queries"
        / "trees_compliance.sparql"
    )
    try:
        return _run_query(ont, qry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""FastAPI endpoints for material alternative recommendations.

This module provides REST API endpoints for querying material alternatives
with multi-criteria ranking.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging

from .alternatives_engine import AlternativeRecommendationEngine, MaterialAlternative

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/alternatives", tags=["alternatives"])


# Ranking strategies from AlternativeRecommendationEngine
RANKING_STRATEGIES = {
    "carbon_first": {
        "carbon_reduction": 0.60,
        "cost_impact": 0.20,
        "availability": 0.15,
        "compatibility": 0.05,
    },
    "cost_constrained": {
        "carbon_reduction": 0.30,
        "cost_impact": 0.50,
        "availability": 0.15,
        "compatibility": 0.05,
    },
    "balanced": {
        "carbon_reduction": 0.40,
        "cost_impact": 0.30,
        "availability": 0.20,
        "compatibility": 0.10,
    },
}


class AlternativesRequest(BaseModel):
    """Request model for material alternatives query."""

    material_id: str
    quantity: Decimal
    building_type: str = "residential"
    ranking_strategy: str = "balanced"  # carbon_first, cost_constrained, balanced

    class Config:
        json_schema_extra = {
            "example": {
                "material_id": "tgo:concrete_c30",
                "quantity": "5000.0",
                "building_type": "residential",
                "ranking_strategy": "balanced",
            }
        }


class AlternativesResponse(BaseModel):
    """Response model for material alternatives."""

    material_id: str
    alternatives: List[Dict[str, Any]]
    original_emission_factor: Decimal
    quantity: Decimal
    unit: str
    building_type: str
    ranking_strategy: str
    alternatives_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "material_id": "tgo:concrete_c30",
                "alternatives": [
                    {
                        "material_id": "tgo:concrete_recycled",
                        "name": "Recycled Concrete",
                        "emission_factor": 180.5,
                        "carbon_reduction_kgco2e": 11950.0,
                        "carbon_reduction_percentage": 39.8,
                        "cost_impact_percentage": 8.5,
                        "availability": "high",
                        "compatibility_score": 0.95,
                        "confidence": 1.0,
                        "ranking_score": 0.85,
                    }
                ],
                "original_emission_factor": 300.0,
                "quantity": 100.0,
                "unit": "m3",
                "building_type": "residential",
                "ranking_strategy": "balanced",
                "alternatives_count": 3,
            }
        }


async def get_alternatives_engine():
    """Dependency injection for AlternativeRecommendationEngine.

    TODO: Replace with actual GraphDB and TGO database clients.
    """
    # TODO: Initialize with actual clients
    # from carbonscope.backend.core.knowledge_graph.graphdb_client import GraphDBClient
    # from carbonscope.backend.core.agents.tgo_database import TGODatabaseAgent
    #
    # graphdb = GraphDBClient(...)
    # tgo_db = TGODatabaseAgent(graphdb)
    # return AlternativeRecommendationEngine(graphdb, tgo_db)

    raise HTTPException(
        status_code=501,
        detail="Alternatives engine not yet configured. Requires GraphDB and TGO database integration.",
    )


@router.post("", response_model=AlternativesResponse)
async def get_material_alternatives(
    request: AlternativesRequest,
    engine: AlternativeRecommendationEngine = Depends(get_alternatives_engine),
):
    """Get lower-carbon material alternatives with multi-criteria ranking.

    This endpoint:
    1. Queries knowledge graph for same-category materials with lower emissions
    2. Ranks alternatives using multi-criteria optimization
    3. Returns top 5 alternatives with detailed scores

    Args:
        request: AlternativesRequest with material_id, quantity, building_type
        engine: Injected AlternativeRecommendationEngine instance

    Returns:
        AlternativesResponse with ranked alternatives

    Raises:
        HTTPException: If material not found or query fails
    """
    try:
        logger.info(
            f"Querying alternatives for {request.material_id}, "
            f"quantity={request.quantity}, building_type={request.building_type}"
        )

        # Get ranking strategy weights
        user_priorities = RANKING_STRATEGIES.get(
            request.ranking_strategy, RANKING_STRATEGIES["balanced"]
        )

        # Recommend alternatives
        alternatives = await engine.recommend_alternatives(
            material_id=request.material_id,
            quantity=request.quantity,
            building_type=request.building_type,
            user_priorities=user_priorities,
        )

        if not alternatives:
            raise HTTPException(
                status_code=404,
                detail=f"No alternatives found for material {request.material_id}",
            )

        # Get original material details
        original_material = await engine.tgo.get_material(request.material_id)
        if not original_material:
            raise HTTPException(
                status_code=404, detail=f"Material {request.material_id} not found"
            )

        return AlternativesResponse(
            material_id=request.material_id,
            alternatives=[alt.to_dict() for alt in alternatives],
            original_emission_factor=original_material["emission_factor"],
            quantity=request.quantity,
            unit=original_material.get("unit", ""),
            building_type=request.building_type,
            ranking_strategy=request.ranking_strategy,
            alternatives_count=len(alternatives),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying alternatives: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/strategies")
async def get_ranking_strategies():
    """Get available ranking strategies for material alternatives.

    Returns:
        Dictionary of available ranking strategies with their weights
    """
    return {
        "strategies": list(RANKING_STRATEGIES.keys()),
        "details": RANKING_STRATEGIES,
    }

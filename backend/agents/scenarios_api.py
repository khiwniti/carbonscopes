"""FastAPI endpoints for scenario management and what-if analysis.

This module provides REST API endpoints for creating scenarios, forking
with material swaps, and comparing carbon impact across scenarios.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Dict, Any
import logging

from .scenario_engine import ScenarioEngine, Scenario

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])


class CreateScenarioRequest(BaseModel):
    """Request model for creating a base scenario."""

    boq_id: str
    materials: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "boq_id": "boq_123",
                "materials": [
                    {
                        "material_id": "tgo:concrete_c30",
                        "quantity": 100.0,
                        "unit": "m3",
                        "description": "Concrete C30",
                        "category": "concrete",
                        "total_carbon": 30000.0,
                    }
                ],
            }
        }


class MaterialSwap(BaseModel):
    """Material swap specification."""

    original_material_id: str
    replacement_material_id: str
    quantity: Decimal
    unit: str


class ForkScenarioRequest(BaseModel):
    """Request model for forking a scenario with material swaps."""

    base_scenario_id: str
    material_swaps: List[MaterialSwap]

    class Config:
        json_schema_extra = {
            "example": {
                "base_scenario_id": "user_456:base:boq_123",
                "material_swaps": [
                    {
                        "original_material_id": "tgo:concrete_c30",
                        "replacement_material_id": "tgo:concrete_recycled",
                        "quantity": "100.0",
                        "unit": "m3",
                    }
                ],
            }
        }


class CompareRequest(BaseModel):
    """Request model for comparing scenarios."""

    scenario_ids: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_ids": [
                    "user_456:base:boq_123",
                    "user_456:base:boq_123:fork:abc123",
                    "user_456:base:boq_123:fork:def456",
                ]
            }
        }


async def get_scenario_engine():
    """Dependency injection for ScenarioEngine.

    TODO: Replace with actual checkpointer and carbon calculator.
    """
    # TODO: Initialize with actual dependencies
    # from carbonscope.backend.core.agents.checkpointer import get_checkpointer
    # from carbonscope.backend.core.agents.carbon_calculator import CarbonCalculatorAgent
    #
    # checkpointer = get_checkpointer()
    # calculator = CarbonCalculatorAgent(...)
    # return ScenarioEngine(checkpointer, calculator)

    raise HTTPException(
        status_code=501,
        detail="Scenario engine not yet configured. Requires checkpointer and carbon calculator integration.",
    )


@router.post("/create", response_model=Dict[str, Any])
async def create_base_scenario(
    request: CreateScenarioRequest,
    engine: ScenarioEngine = Depends(get_scenario_engine),
):
    """Create a base scenario from BOQ analysis.

    This endpoint creates an immutable base scenario that can be forked
    for what-if analysis with material swaps.

    Args:
        request: CreateScenarioRequest with boq_id and materials
        engine: Injected ScenarioEngine instance

    Returns:
        Base scenario dictionary with calculated carbon totals

    Raises:
        HTTPException: If scenario creation fails
    """
    try:
        logger.info(f"Creating base scenario for BOQ {request.boq_id}")

        # TODO: Get user_id from authentication
        user_id = "user_temp"  # Placeholder

        scenario = await engine.create_base_scenario(
            boq_id=request.boq_id, user_id=user_id, materials=request.materials
        )

        return scenario.to_dict()

    except Exception as e:
        logger.error(f"Error creating base scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/fork", response_model=Dict[str, Any])
async def fork_scenario(
    request: ForkScenarioRequest,
    engine: ScenarioEngine = Depends(get_scenario_engine),
):
    """Create scenario fork with material swaps.

    This endpoint creates an immutable fork of a base scenario with
    specified material swaps. Carbon is incrementally recalculated
    (only swapped materials) for <2s performance.

    Args:
        request: ForkScenarioRequest with base_scenario_id and material_swaps
        engine: Injected ScenarioEngine instance

    Returns:
        Forked scenario dictionary with delta carbon calculations

    Raises:
        HTTPException: If base scenario not found or forking fails
    """
    try:
        logger.info(
            f"Forking scenario {request.base_scenario_id} "
            f"with {len(request.material_swaps)} swaps"
        )

        # Convert Pydantic models to dictionaries
        material_swaps = [swap.model_dump() for swap in request.material_swaps]

        forked_scenario = await engine.fork_scenario(
            base_scenario_id=request.base_scenario_id, material_swaps=material_swaps
        )

        return forked_scenario.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error forking scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/compare", response_model=Dict[str, Any])
async def compare_scenarios(
    request: CompareRequest,
    engine: ScenarioEngine = Depends(get_scenario_engine),
):
    """Compare multiple scenarios side-by-side.

    This endpoint loads multiple scenarios and compares them, identifying
    the best scenario (lowest carbon) and maximum carbon reduction achieved.

    Args:
        request: CompareRequest with list of scenario_ids
        engine: Injected ScenarioEngine instance

    Returns:
        Comparison dictionary with scenarios, best_scenario_id, and max_carbon_reduction

    Raises:
        HTTPException: If comparison fails
    """
    try:
        logger.info(f"Comparing {len(request.scenario_ids)} scenarios")

        comparison = await engine.compare_scenarios(request.scenario_ids)

        return comparison

    except Exception as e:
        logger.error(f"Error comparing scenarios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{scenario_id}", response_model=Dict[str, Any])
async def get_scenario(
    scenario_id: str, engine: ScenarioEngine = Depends(get_scenario_engine)
):
    """Get a specific scenario by ID.

    Args:
        scenario_id: Scenario identifier
        engine: Injected ScenarioEngine instance

    Returns:
        Scenario dictionary

    Raises:
        HTTPException: If scenario not found
    """
    try:
        scenario = await engine._load_scenario(scenario_id)

        if not scenario:
            raise HTTPException(
                status_code=404, detail=f"Scenario {scenario_id} not found"
            )

        return scenario.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

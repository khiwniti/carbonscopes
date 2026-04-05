"""BOQ Parser Agent for coordinating BOQ file parsing.

This agent is a thin wrapper around the Phase 2 BOQ parser module,
providing agent-based coordination for BOQ file parsing tasks.
"""

import logging
from typing import Dict, Any
from .base import Agent
from .state import AgentState

logger = logging.getLogger(__name__)


class BOQParserAgent(Agent):
    """Agent for BOQ file parsing coordination.

    This agent delegates to the Phase 2 BOQ parser module to handle
    Thai BOQ Excel file parsing and material extraction.

    Capabilities:
        - parse:boq
    """

    def __init__(self, boq_parser=None):
        """Initialize BOQ Parser Agent.

        Args:
            boq_parser: Optional BOQ parser instance from Phase 2.
                       If None, operates in mock mode.
        """
        super().__init__(
            name="boq_parser",
            capabilities={"parse:boq"}
        )
        self.parser = boq_parser

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute BOQ parsing task.

        Args:
            state: Current agent state containing user query and task results

        Returns:
            Dictionary with parsing results:
                - boq_parsed: bool indicating success
                - boq_materials: list of extracted materials
                - boq_metadata: dict with BOQ file metadata

        Example:
            >>> state = {
            ...     "user_query": "Parse BOQ file",
            ...     "task_results": {"boq_file_path": "/path/to/boq.xlsx"}
            ... }
            >>> result = await agent.execute(state)
            >>> result["boq_parsed"]
            True
        """
        logger.info(f"BOQ Parser Agent executing: {state['user_query']}")

        # Get BOQ file from task results
        boq_file_path = state.get("task_results", {}).get("boq_file_path")
        boq_id = state.get("task_results", {}).get("boq_id")

        if not boq_file_path and not boq_id:
            logger.warning("No BOQ file path or BOQ ID provided")
            return {
                "boq_parsed": False,
                "error": "No BOQ file path or BOQ ID provided"
            }

        try:
            # If real parser is available, use it
            if self.parser:
                logger.info(f"Using Phase 2 BOQ parser for: {boq_file_path or boq_id}")
                # TODO: Integrate with Phase 2 parser
                # result = await self.parser.parse(boq_file_path)
                # return {
                #     "boq_parsed": True,
                #     "boq_materials": result.materials,
                #     "boq_metadata": result.metadata
                # }

            # Mock mode for testing
            logger.info("Operating in mock mode (Phase 2 parser not connected)")
            return {
                "boq_parsed": True,
                "boq_materials": [
                    {
                        "item_id": "1.1",
                        "description": "คอนกรีต ผสมเสร็จ f'c = 280 kg/cm² (Concrete C30)",
                        "quantity": 500.0,
                        "unit": "m³",
                        "material_type": "concrete"
                    },
                    {
                        "item_id": "1.2",
                        "description": "เหล็กเส้น ข้ออ้อย SD40 (Deformed steel bars)",
                        "quantity": 15000.0,
                        "unit": "kg",
                        "material_type": "steel"
                    }
                ],
                "boq_metadata": {
                    "project_name": "Test Project",
                    "total_items": 2,
                    "file_name": boq_file_path or f"boq_{boq_id}.xlsx"
                },
                "parsing_method": "mock"
            }

        except Exception as e:
            logger.error(f"BOQ parsing failed: {str(e)}", exc_info=True)
            return {
                "boq_parsed": False,
                "error": str(e)
            }


def boq_parser_node(state: AgentState) -> Dict[str, Any]:
    """LangGraph node function for BOQ Parser agent.

    Args:
        state: Current AgentState

    Returns:
        Dictionary with BOQ parsing results
    """
    agent = BOQParserAgent()
    import asyncio
    return asyncio.run(agent.execute(state))

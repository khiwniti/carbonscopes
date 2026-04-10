"""
ScenarioBuilder — fluent API for setting up CarbonScope test scenarios.

Queues state-building actions and executes them via ``build()``.  Each method
returns ``self`` for chaining.  The built state is returned as a dict so tests
can reference created resource IDs.

Example::

    state = await (
        ScenarioBuilder(client)
        .with_project("Office Tower Assessment")
        .with_material("Concrete C30", quantity=250.0, unit="m3")
        .with_boq_from_file("tests/sample_data/sample_boq.csv")
        .build()
    )
    project_id = state["project"]["id"]
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional

import httpx

logger = logging.getLogger("e2e.scenario_builder")


class ScenarioBuilder:
    """
    Fluent builder for E2E test scenarios.

    All ``with_*`` methods enqueue an async action; ``build()`` executes them
    in order and returns the accumulated state dict.
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._actions: List[Callable[[], Coroutine[Any, Any, None]]] = []
        self._state: Dict[str, Any] = {}

    # ── Domain: Projects ──────────────────────────────────────────────────

    def with_project(
        self,
        name: str = "E2E Test Project",
        description: str = "Auto-created by E2E test infrastructure",
    ) -> "ScenarioBuilder":
        """
        Create a project.  Stored at ``state["project"]``.
        """
        async def _action() -> None:
            response = await self._client.post(
                "/projects",
                json={"name": name, "description": description},
            )
            if response.status_code not in (200, 201):
                logger.warning(f"with_project: unexpected status {response.status_code}: {response.text[:200]}")
                return
            self._state["project"] = response.json()
            logger.debug(f"Created project: {self._state['project'].get('id')}")

        self._actions.append(_action)
        return self

    # ── Domain: Materials ─────────────────────────────────────────────────

    def with_material(
        self,
        name: str,
        quantity: float = 1.0,
        unit: str = "kg",
        category: Optional[str] = None,
    ) -> "ScenarioBuilder":
        """
        Add a material entry.  Stored in ``state["materials"]`` list.

        TODO: Adjust the request body to match the actual /materials endpoint schema.
        """
        async def _action() -> None:
            project_id = self._state.get("project", {}).get("id")
            payload: Dict[str, Any] = {
                "name": name,
                "quantity": quantity,
                "unit": unit,
            }
            if category:
                payload["category"] = category
            if project_id:
                payload["project_id"] = project_id

            response = await self._client.post("/materials", json=payload)
            if response.status_code not in (200, 201):
                logger.warning(f"with_material: unexpected status {response.status_code}")
                return
            self._state.setdefault("materials", []).append(response.json())

        self._actions.append(_action)
        return self

    # ── Domain: BOM / BoQ ─────────────────────────────────────────────────

    def with_boq_from_file(self, file_path: str) -> "ScenarioBuilder":
        """
        Upload a Bill of Quantities CSV/Excel file.  Stored at ``state["boq"]``.

        Args:
            file_path: Path relative to the repo root, e.g.
                       ``"backend/tests/sample_data/sample_boq.csv"``
        """
        async def _action() -> None:
            abs_path = Path("/workspaces/carbonscopes") / file_path
            if not abs_path.exists():
                logger.warning(f"with_boq_from_file: file not found: {abs_path}")
                return

            project_id = self._state.get("project", {}).get("id")
            params = {"project_id": project_id} if project_id else {}

            with abs_path.open("rb") as fh:
                response = await self._client.post(
                    "/boq/upload",
                    files={"file": (abs_path.name, fh, "text/csv")},
                    params=params,
                )
            if response.status_code not in (200, 201):
                logger.warning(f"with_boq_from_file: unexpected status {response.status_code}: {response.text[:200]}")
                return
            self._state["boq"] = response.json()

        self._actions.append(_action)
        return self

    # ── Domain: Agent / Chat ──────────────────────────────────────────────

    def with_agent_thread(
        self,
        initial_message: str = "Hello, please help me with a carbon assessment.",
    ) -> "ScenarioBuilder":
        """
        Start an agent chat thread.  Stored at ``state["thread"]``.

        TODO: Update endpoint path if the agent API uses a different route.
        """
        async def _action() -> None:
            project_id = self._state.get("project", {}).get("id")
            payload: Dict[str, Any] = {"message": initial_message}
            if project_id:
                payload["project_id"] = project_id

            response = await self._client.post("/threads", json=payload)
            if response.status_code not in (200, 201):
                logger.warning(f"with_agent_thread: unexpected status {response.status_code}")
                return
            self._state["thread"] = response.json()

        self._actions.append(_action)
        return self

    # ── Domain: Carbon Assessment ─────────────────────────────────────────

    def with_carbon_assessment(
        self,
        material_name: str = "Concrete C30/37",
        quantity: float = 100.0,
        unit: str = "m3",
        life_cycle_stage: str = "A1-A3",
    ) -> "ScenarioBuilder":
        """
        Create a carbon assessment entry.  Stored in ``state["assessments"]``.

        TODO: Adjust the request body to match the actual carbon assessment schema.
        """
        async def _action() -> None:
            payload = {
                "material_name": material_name,
                "quantity": quantity,
                "unit": unit,
                "life_cycle_stage": life_cycle_stage,
            }
            project_id = self._state.get("project", {}).get("id")
            if project_id:
                payload["project_id"] = project_id  # type: ignore[assignment]

            response = await self._client.post("/carbon/calculate", json=payload)
            if response.status_code not in (200, 201):
                logger.warning(f"with_carbon_assessment: status {response.status_code}")
                return
            self._state.setdefault("assessments", []).append(response.json())

        self._actions.append(_action)
        return self

    # ── Raw customization ─────────────────────────────────────────────────

    def with_custom_action(
        self, action: Callable[["ScenarioBuilder"], Coroutine[Any, Any, None]]
    ) -> "ScenarioBuilder":
        """
        Escape hatch: enqueue an arbitrary async action that receives this
        builder instance so it can read and write ``_state``.

        Example::

            async def my_action(b: ScenarioBuilder) -> None:
                b._state["foo"] = "bar"

            builder.with_custom_action(my_action)
        """
        self._actions.append(lambda: action(self))
        return self

    # ── Execution ─────────────────────────────────────────────────────────

    async def build(self) -> Dict[str, Any]:
        """
        Execute all queued actions in order and return the accumulated state.

        Returns:
            dict with keys corresponding to the ``with_*`` methods called.
            E.g. ``{"project": {...}, "materials": [...], "boq": {...}}``
        """
        for action in self._actions:
            await action()
        logger.debug(f"ScenarioBuilder.build complete, state keys: {list(self._state.keys())}")
        return self._state

    # ── From save/snapshot ─────────────────────────────────────────────────

    def from_snapshot(self, snapshot: Dict[str, Any]) -> "ScenarioBuilder":
        """
        Seed the builder state from a previously captured snapshot dict.

        Useful for sharing expensive setup between tests without repeating
        API calls.
        """
        async def _action() -> None:
            self._state.update(snapshot)

        self._actions.append(_action)
        return self

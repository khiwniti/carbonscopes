"""
CarbonScopeAPIClient — domain-level API interaction helpers.

Wraps raw httpx calls with domain semantics, assertion helpers, and
streaming support.  Use this instead of calling ``client.get/post``
directly in tests to keep test code readable.

Example::

    api = CarbonScopeAPIClient(client)
    health = await api.get_health()
    project = await api.create_project("My Project")
    await api.assert_status(response, 200, "create project")
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

logger = logging.getLogger("e2e.api_client")


class CarbonScopeAPIClient:
    """
    High-level API client for CarbonScope E2E tests.

    Wraps the raw httpx client with:
    - Descriptive assertion helpers (``assert_status``, ``assert_json_key``)
    - Domain-specific methods (``create_project``, ``start_agent_run``, etc.)
    - SSE streaming helpers
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    # ── Assertion helpers ─────────────────────────────────────────────────

    def assert_status(
        self,
        response: httpx.Response,
        expected: int,
        context: str = "",
    ) -> None:
        """Assert HTTP status with a descriptive failure message."""
        label = f" [{context}]" if context else ""
        assert response.status_code == expected, (
            f"Expected HTTP {expected}{label}, got {response.status_code}.\n"
            f"Body: {response.text[:500]}"
        )

    def assert_json_key(
        self,
        data: Dict[str, Any],
        key: str,
        context: str = "",
    ) -> None:
        """Assert a key exists in a JSON response dict."""
        label = f" [{context}]" if context else ""
        assert key in data, (
            f"Expected key '{key}' in response{label}. Got keys: {list(data.keys())}"
        )

    def skip_if_billing_error(
        self, response: httpx.Response, context: str = ""
    ) -> None:
        """Skip the current test if the API returns a billing-related error."""
        import pytest

        if response.status_code == 402:
            pytest.skip(f"{context}: billing/credits required (HTTP 402)")
        if response.status_code == 500 and "billing" in response.text.lower():
            pytest.skip(f"{context}: billing server error (HTTP 500)")

    # ── System ────────────────────────────────────────────────────────────

    async def get_health(self) -> Dict[str, Any]:
        """GET /health — returns health status dict."""
        response = await self._client.get("/health")
        self.assert_status(response, 200, "health check")
        return response.json()

    # ── Projects ──────────────────────────────────────────────────────────

    async def create_project(
        self,
        name: str = "E2E Test Project",
        description: str = "",
    ) -> Dict[str, Any]:
        """POST /projects — create and return a project."""
        response = await self._client.post(
            "/projects",
            json={"name": name, "description": description},
        )
        self.assert_status(response, 201, f"create project '{name}'")
        return response.json()

    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """GET /projects/{id}."""
        response = await self._client.get(f"/projects/{project_id}")
        self.assert_status(response, 200, f"get project {project_id}")
        return response.json()

    async def list_projects(self) -> List[Dict[str, Any]]:
        """GET /projects."""
        response = await self._client.get("/projects")
        self.assert_status(response, 200, "list projects")
        data = response.json()
        return data if isinstance(data, list) else data.get("projects", [])

    async def delete_project(self, project_id: str) -> None:
        """DELETE /projects/{id}."""
        response = await self._client.delete(f"/projects/{project_id}")
        # 200, 204, or 404 are all acceptable during cleanup
        if response.status_code not in (200, 204, 404):
            logger.warning(f"delete_project({project_id}): HTTP {response.status_code}")

    # ── Threads ───────────────────────────────────────────────────────────

    async def list_threads(self) -> List[Dict[str, Any]]:
        """GET /threads."""
        response = await self._client.get("/threads")
        self.assert_status(response, 200, "list threads")
        data = response.json()
        return data if isinstance(data, list) else data.get("threads", [])

    async def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """GET /threads/{id}/messages."""
        response = await self._client.get(f"/threads/{thread_id}/messages")
        self.assert_status(response, 200, f"get messages for thread {thread_id}")
        data = response.json()
        return data if isinstance(data, list) else data.get("messages", [])

    # ── Agent Runs ────────────────────────────────────────────────────────

    async def start_agent_run(
        self,
        message: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """POST /agent/start — start a new agent run."""
        payload: Dict[str, Any] = {"message": message}
        if project_id:
            payload["project_id"] = project_id

        response = await self._client.post("/agent/start", json=payload)
        self.skip_if_billing_error(response, "start agent run")
        self.assert_status(response, 200, "start agent run")
        return response.json()

    async def stop_agent_run(self, run_id: str) -> None:
        """POST /agent-run/{id}/stop."""
        response = await self._client.post(f"/agent-run/{run_id}/stop")
        if response.status_code not in (200, 204, 404):
            logger.warning(f"stop_agent_run({run_id}): HTTP {response.status_code}")

    async def stream_agent_run(
        self,
        run_id: str,
        max_events: int = 20,
        timeout: float = 60.0,
    ) -> List[Dict[str, Any]]:
        """
        Consume SSE events from GET /agent-run/{id}/stream.

        Returns a list of parsed SSE event dicts (up to ``max_events``).
        Stops early on a ``done`` event.
        """
        events: List[Dict[str, Any]] = []
        deadline = asyncio.get_event_loop().time() + timeout

        async with self._client.stream("GET", f"/agent-run/{run_id}/stream") as resp:
            self.assert_status(resp, 200, f"stream agent run {run_id}")
            async for line in resp.aiter_lines():
                if asyncio.get_event_loop().time() > deadline:
                    logger.warning("stream_agent_run: timeout reached")
                    break
                if not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if not raw or raw == "[DONE]":
                    break
                try:
                    event = json.loads(raw)
                    events.append(event)
                    if event.get("type") in ("done", "end", "complete"):
                        break
                    if len(events) >= max_events:
                        break
                except json.JSONDecodeError:
                    logger.debug(f"Non-JSON SSE line: {raw[:80]}")

        return events

    # ── Carbon / LCA ──────────────────────────────────────────────────────

    async def calculate_carbon(
        self,
        material_name: str,
        quantity: float,
        unit: str = "kg",
    ) -> Dict[str, Any]:
        """
        POST /carbon/calculate — run a carbon calculation.

        TODO: Update request body to match actual endpoint schema.
        """
        response = await self._client.post(
            "/carbon/calculate",
            json={"material_name": material_name, "quantity": quantity, "unit": unit},
        )
        self.assert_status(response, 200, f"carbon calculate '{material_name}'")
        return response.json()

    # ── BOM / BoQ ─────────────────────────────────────────────────────────

    async def upload_boq(
        self,
        file_path: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /boq/upload — upload a BoQ CSV/Excel file.

        Args:
            file_path: Absolute path to the file.
            project_id: Optional project to associate.
        """
        from pathlib import Path

        abs_path = Path(file_path)
        params = {"project_id": project_id} if project_id else {}

        with abs_path.open("rb") as fh:
            suffix = abs_path.suffix.lower()
            mime = "text/csv" if suffix == ".csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = await self._client.post(
                "/boq/upload",
                files={"file": (abs_path.name, fh, mime)},
                params=params,
            )
        self.assert_status(response, 200, f"upload BoQ '{abs_path.name}'")
        return response.json()

    # ── Billing / Account ─────────────────────────────────────────────────

    async def get_account_state(self) -> Dict[str, Any]:
        """GET /billing/account-state."""
        response = await self._client.get("/billing/account-state")
        self.assert_status(response, 200, "get account state")
        return response.json()

    async def list_accounts(self) -> List[Dict[str, Any]]:
        """GET /accounts."""
        response = await self._client.get("/accounts")
        self.assert_status(response, 200, "list accounts")
        data = response.json()
        return data if isinstance(data, list) else data.get("accounts", [])

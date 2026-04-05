"""Knowledge Graph Agent for SPARQL queries and compliance checks.

This agent performs SPARQL queries on the GraphDB knowledge graph for
TREES/EDGE compliance validation and semantic reasoning.
"""

from typing import Dict, Any, List
from .base import Agent
from .state import AgentState
import logging
import re

logger = logging.getLogger(__name__)


class KnowledgeGraphAgent(Agent):
    """Agent for knowledge graph queries and compliance validation.

    Capabilities:
        - query:kg: Execute SPARQL queries on knowledge graph
        - reason:semantic: Perform semantic reasoning
        - validate:compliance: Validate TREES/EDGE compliance

    This agent integrates with GraphDB to provide compliance checks
    and semantic material categorization.
    """

    def __init__(self, graphdb_client=None):
        """Initialize Knowledge Graph Agent.

        Args:
            graphdb_client: Optional GraphDBClient instance for SPARQL queries.
                          If None, operates in mock mode for testing.
        """
        super().__init__(
            name="knowledge_graph",
            capabilities={"query:kg", "reason:semantic", "validate:compliance"}
        )
        self.graphdb_client = graphdb_client

    async def execute(self, state: AgentState) -> Dict[str, Any]:
        """Execute SPARQL queries for TREES/EDGE compliance.

        Args:
            state: Current AgentState with user query and materials

        Returns:
            Dictionary with:
                - query_type: Type of query performed
                - results: Query results
                - compliant: Boolean compliance status (if applicable)
                - criteria: Compliance criteria checked
                - details: Additional details

        Example (TREES compliance):
            {
                "query_type": "trees_mr1_eligibility",
                "results": [...],
                "compliant": true,
                "criteria": "TREES MR1",
                "details": "Material meets recycled content requirements"
            }

        Example (EDGE certification):
            {
                "query_type": "edge_certification",
                "results": [...],
                "certification_level": "EDGE Advanced",
                "energy_reduction": 45.2,
                "water_reduction": 38.5,
                "embodied_energy_reduction": 25.3
            }
        """
        query = state["user_query"]
        task_results = state.get("task_results", {})

        self.logger.info(f"Executing knowledge graph query: {query}")

        # Classify query type
        query_type = self._classify_query(query)

        try:
            if query_type == "trees_mr1_eligibility":
                result = await self._check_trees_mr1(query, task_results)

            elif query_type == "trees_mr3_eligibility":
                result = await self._check_trees_mr3(query, task_results)

            elif query_type == "edge_certification":
                result = await self._check_edge_certification(query, task_results)

            elif query_type == "material_classification":
                result = await self._classify_material(query, task_results)

            else:
                result = await self._generic_sparql_query(query)

            self.logger.info(f"Knowledge graph query complete: {query_type}")

            return result

        except Exception as e:
            self.logger.error(f"Knowledge graph query failed: {e}", exc_info=True)
            return {
                "query_type": query_type,
                "error": str(e),
                "results": [],
                "compliant": False
            }

    async def _check_trees_mr1(
        self, query: str, task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check TREES MR1 (Recycled Materials) eligibility.

        Args:
            query: User query
            task_results: Previous task results

        Returns:
            TREES MR1 compliance results
        """
        if self.graphdb_client is not None:
            sparql = self._build_trees_mr1_query(task_results)
            results = await self.graphdb_client.query(sparql)
            eligible = len(results.get("results", {}).get("bindings", [])) > 0
        else:
            # Mock mode
            results = self._get_mock_trees_results()
            eligible = True

        return {
            "query_type": "trees_mr1_eligibility",
            "results": results,
            "compliant": eligible,
            "criteria": "TREES MR1 - Recycled Materials",
            "details": (
                "Material meets TREES MR1 recycled content requirements (>20% post-consumer or >50% pre-consumer)"
                if eligible
                else "Material does not meet TREES MR1 recycled content requirements"
            ),
            "requirements": {
                "post_consumer_min": 0.20,
                "pre_consumer_min": 0.50,
                "certification": "Environmental Product Declaration (EPD) or equivalent"
            }
        }

    async def _check_trees_mr3(
        self, query: str, task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check TREES MR3 (Sustainable Materials) eligibility.

        Args:
            query: User query
            task_results: Previous task results

        Returns:
            TREES MR3 compliance results
        """
        if self.graphdb_client is not None:
            sparql = self._build_trees_mr3_query(task_results)
            results = await self.graphdb_client.query(sparql)
            eligible = len(results.get("results", {}).get("bindings", [])) > 0
        else:
            # Mock mode
            results = self._get_mock_trees_results()
            eligible = True

        return {
            "query_type": "trees_mr3_eligibility",
            "results": results,
            "compliant": eligible,
            "criteria": "TREES MR3 - Sustainable Materials",
            "details": (
                "Material qualifies as sustainably sourced with valid certification"
                if eligible
                else "Material does not meet sustainable sourcing requirements"
            ),
            "requirements": {
                "certifications_accepted": [
                    "FSC (Forest Stewardship Council)",
                    "PEFC (Programme for the Endorsement of Forest Certification)",
                    "Thai Green Label"
                ]
            }
        }

    async def _check_edge_certification(
        self, query: str, task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check EDGE certification level.

        Args:
            query: User query
            task_results: Previous task results with carbon calculations

        Returns:
            EDGE certification level assessment
        """
        # Calculate reductions from task results
        total_carbon = task_results.get("total_carbon", 0.0)
        baseline_carbon = task_results.get("baseline_carbon", total_carbon * 1.25)

        if baseline_carbon > 0:
            embodied_energy_reduction = ((baseline_carbon - total_carbon) / baseline_carbon) * 100
        else:
            embodied_energy_reduction = 0.0

        # Determine EDGE level based on reductions
        level = self._calculate_edge_level(embodied_energy_reduction)

        if self.graphdb_client is not None:
            sparql = self._build_edge_certification_query(task_results)
            results = await self.graphdb_client.query(sparql)
        else:
            results = self._get_mock_edge_results()

        return {
            "query_type": "edge_certification",
            "results": results,
            "certification_level": level,
            "embodied_energy_reduction": round(embodied_energy_reduction, 2),
            "compliant": embodied_energy_reduction >= 20.0,  # Minimum for EDGE
            "criteria": "EDGE Excellence in Design for Greater Efficiencies",
            "details": self._get_edge_explanation(level, embodied_energy_reduction),
            "requirements": {
                "EDGE": "20% reduction in embodied energy",
                "EDGE Advanced": "40% reduction in embodied energy",
                "EDGE Zero Carbon": "100% carbon neutral"
            }
        }

    async def _classify_material(
        self, query: str, task_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify material using semantic reasoning.

        Args:
            query: User query with material description
            task_results: Previous task results

        Returns:
            Material classification results
        """
        material_description = self._extract_material_description(query, task_results)

        if self.graphdb_client is not None:
            sparql = f"""
            PREFIX trees: <http://carbonbim.org/trees/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?class ?label ?parent
            WHERE {{
                ?class rdfs:label ?label .
                OPTIONAL {{ ?class rdfs:subClassOf ?parent }}
                FILTER(CONTAINS(LCASE(?label), LCASE("{material_description}")))
            }}
            LIMIT 10
            """
            results = await self.graphdb_client.query(sparql)
        else:
            results = self._get_mock_classification()

        return {
            "query_type": "material_classification",
            "results": results,
            "material_description": material_description,
            "classifications": self._parse_classification_results(results)
        }

    async def _generic_sparql_query(self, query: str) -> Dict[str, Any]:
        """Execute generic SPARQL query.

        Args:
            query: User query

        Returns:
            Generic query results
        """
        return {
            "query_type": "generic",
            "results": [],
            "message": "Generic knowledge graph query - specify TREES, EDGE, or material classification"
        }

    def _classify_query(self, query: str) -> str:
        """Classify query type based on keywords.

        Args:
            query: User query string

        Returns:
            Query type identifier
        """
        query_lower = query.lower()

        if "trees mr1" in query_lower or "recycled" in query_lower:
            return "trees_mr1_eligibility"

        elif "trees mr3" in query_lower or "sustainable" in query_lower or "fsc" in query_lower:
            return "trees_mr3_eligibility"

        elif "edge" in query_lower or "certification" in query_lower:
            return "edge_certification"

        elif "classify" in query_lower or "category" in query_lower or "what type" in query_lower:
            return "material_classification"

        else:
            return "generic"

    def _build_trees_mr1_query(self, task_results: Dict[str, Any]) -> str:
        """Build SPARQL query for TREES MR1 compliance.

        Args:
            task_results: Task results with material data

        Returns:
            SPARQL query string
        """
        material_id = task_results.get("material_id", "")

        return f"""
        PREFIX trees: <http://carbonbim.org/trees/>
        PREFIX tgo: <http://carbonbim.org/tgo/>

        SELECT ?material ?recycledContent ?certification
        WHERE {{
            ?material a tgo:Material ;
                     trees:recycledContent ?recycledContent ;
                     trees:certification ?certification .
            FILTER(?recycledContent >= 0.20)
            FILTER(CONTAINS(STR(?material), "{material_id}"))
        }}
        """

    def _build_trees_mr3_query(self, task_results: Dict[str, Any]) -> str:
        """Build SPARQL query for TREES MR3 compliance.

        Args:
            task_results: Task results with material data

        Returns:
            SPARQL query string
        """
        material_id = task_results.get("material_id", "")

        return f"""
        PREFIX trees: <http://carbonbim.org/trees/>
        PREFIX tgo: <http://carbonbim.org/tgo/>

        SELECT ?material ?certification ?sustainabilityLabel
        WHERE {{
            ?material a tgo:Material ;
                     trees:sustainabilityCertification ?certification .
            OPTIONAL {{ ?material rdfs:label ?sustainabilityLabel }}
            FILTER(CONTAINS(STR(?material), "{material_id}"))
            FILTER(?certification IN ("FSC", "PEFC", "ThaiGreenLabel"))
        }}
        """

    def _build_edge_certification_query(self, task_results: Dict[str, Any]) -> str:
        """Build SPARQL query for EDGE certification data.

        Args:
            task_results: Task results with building data

        Returns:
            SPARQL query string
        """
        return """
        PREFIX edge: <http://carbonbim.org/edge/>
        PREFIX tgo: <http://carbonbim.org/tgo/>

        SELECT ?material ?embodiedEnergy ?embodiedCarbon
        WHERE {
            ?material a tgo:Material ;
                     edge:embodiedEnergy ?embodiedEnergy ;
                     edge:embodiedCarbon ?embodiedCarbon .
        }
        ORDER BY ?embodiedCarbon
        LIMIT 20
        """

    def _calculate_edge_level(self, reduction_pct: float) -> str:
        """Calculate EDGE certification level from reduction percentage.

        Args:
            reduction_pct: Embodied energy reduction percentage

        Returns:
            EDGE certification level
        """
        if reduction_pct >= 100.0:
            return "EDGE Zero Carbon"
        elif reduction_pct >= 40.0:
            return "EDGE Advanced"
        elif reduction_pct >= 20.0:
            return "EDGE"
        else:
            return "Does not meet EDGE requirements"

    def _get_edge_explanation(self, level: str, reduction: float) -> str:
        """Generate explanation for EDGE level.

        Args:
            level: EDGE certification level
            reduction: Reduction percentage

        Returns:
            Explanation string
        """
        if level == "EDGE Zero Carbon":
            return f"Excellent! With {reduction:.1f}% reduction, this qualifies for EDGE Zero Carbon certification."
        elif level == "EDGE Advanced":
            return f"Great! With {reduction:.1f}% reduction, this qualifies for EDGE Advanced certification."
        elif level == "EDGE":
            return f"Good! With {reduction:.1f}% reduction, this meets basic EDGE certification requirements."
        else:
            return f"With {reduction:.1f}% reduction, this does not meet EDGE minimum requirements (20% needed)."

    def _extract_material_description(
        self, query: str, task_results: Dict[str, Any]
    ) -> str:
        """Extract material description from query or task results.

        Args:
            query: User query
            task_results: Previous task results

        Returns:
            Material description string
        """
        # Check task results first
        if "material_id" in task_results:
            return task_results["material_id"]

        # Extract from query
        quoted = re.findall(r'"([^"]+)"', query)
        if quoted:
            return quoted[0]

        # Simple extraction
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ["for", "about", "of"]:
                if i + 1 < len(words):
                    return words[i + 1]

        return "unknown material"

    def _parse_classification_results(self, results: Dict[str, Any]) -> List[str]:
        """Parse classification results from SPARQL response.

        Args:
            results: SPARQL query results

        Returns:
            List of classification labels
        """
        if isinstance(results, dict):
            bindings = results.get("results", {}).get("bindings", [])
            return [b.get("label", {}).get("value", "") for b in bindings]
        return []

    def _get_mock_trees_results(self) -> Dict[str, Any]:
        """Generate mock TREES compliance results."""
        return {
            "results": {
                "bindings": [
                    {
                        "material": {"value": "tgo:concrete_recycled"},
                        "recycledContent": {"value": "0.35"},
                        "certification": {"value": "EPD"}
                    }
                ]
            }
        }

    def _get_mock_edge_results(self) -> Dict[str, Any]:
        """Generate mock EDGE compliance results."""
        return {
            "results": {
                "bindings": [
                    {
                        "material": {"value": "tgo:concrete_green"},
                        "embodiedEnergy": {"value": "1250.5"},
                        "embodiedCarbon": {"value": "195.2"}
                    }
                ]
            }
        }

    def _get_mock_classification(self) -> Dict[str, Any]:
        """Generate mock material classification."""
        return {
            "results": {
                "bindings": [
                    {
                        "class": {"value": "trees:StructuralMaterial"},
                        "label": {"value": "Structural Material"},
                        "parent": {"value": "trees:BuildingMaterial"}
                    }
                ]
            }
        }

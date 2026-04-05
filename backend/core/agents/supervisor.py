"""Supervisor agent for multi-agent orchestration.

This module implements the supervisor pattern for LangGraph multi-agent coordination.
The supervisor routes user queries to appropriate specialist agents based on capability matching.
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .router import SupervisorRouter
import logging

logger = logging.getLogger("agent.supervisor")

# Global router instance for production use
_router: SupervisorRouter | None = None


def set_router(router: SupervisorRouter) -> None:
    """Set the global router instance for supervisor.

    This should be called during application initialization to configure
    the supervisor with registered agents.

    Args:
        router: Configured SupervisorRouter with registered agents
    """
    global _router
    _router = router


def supervisor_node(state: AgentState, router: SupervisorRouter | None = None) -> AgentState:
    """Supervisor node that routes to appropriate agent.

    The supervisor analyzes the user query and uses capability-based routing
    to select the most appropriate specialist agent for handling the request.

    Args:
        state: Current AgentState containing user query and agent history
        router: Optional router instance (uses global router if not provided)

    Returns:
        Updated AgentState with current_agent set and agent_history appended

    Example:
        >>> state = {
        ...     "user_query": "Calculate carbon footprint",
        ...     "current_agent": "",
        ...     "agent_history": [],
        ...     "task_results": {},
        ...     "error_count": 0,
        ...     "scenario_context": None
        ... }
        >>> router = SupervisorRouter()
        >>> # Register agents with router...
        >>> result = supervisor_node(state, router)
        >>> result["current_agent"]
        'carbon_calculator'
    """
    query = state["user_query"]

    # Use provided router or fall back to global router
    active_router = router if router is not None else _router

    if active_router is None:
        raise ValueError("No router configured. Call set_router() or pass router parameter.")

    next_agent = active_router.route(query)
    logger.info(f"Routing query to: {next_agent}")

    return {
        **state,
        "current_agent": next_agent,
        "agent_history": [next_agent]
    }


def create_supervisor_graph(
    checkpointer=None,
    graphdb_client=None,
    tgo_client=None,
    carbon_pipeline=None,
    alternatives_engine=None,
    boq_parser=None
):
    """Create LangGraph StateGraph with supervisor and all 12 specialist agents.

    Builds a StateGraph with the supervisor node as the entry point and registers
    all 12 specialist agents with the router.

    Args:
        checkpointer: Optional checkpointer for state persistence (e.g., PostgresSaver).
                     If provided, enables conversation memory and state recovery.
        graphdb_client: Optional GraphDBClient for Knowledge Graph and Material Analyst agents.
                       If None, agents operate in mock mode.
        tgo_client: Optional TGOClient for TGO Database agent.
                   If None, agent operates in mock mode.
        carbon_pipeline: Optional CarbonCalculationPipeline for Carbon Calculator agent.
                        If None, agent operates in mock mode.
        alternatives_engine: Optional AlternativeRecommendationEngine for Sustainability agent.
                           If None, agent operates without alternatives engine.
        boq_parser: Optional BOQ parser from Phase 2.
                   If None, BOQ Parser agent operates in mock mode.

    Returns:
        Compiled StateGraph ready for execution with all 12 agents registered

    Example:
        >>> # Without checkpointing (stateless)
        >>> graph = create_supervisor_graph()
        >>> result = graph.invoke({
        ...     "user_query": "Find material alternatives",
        ...     "current_agent": "",
        ...     "agent_history": [],
        ...     "task_results": {},
        ...     "error_count": 0,
        ...     "scenario_context": None
        ... })

        >>> # With checkpointing (stateful)
        >>> from suna.backend.core.agents.checkpointer import get_checkpointer
        >>> checkpointer = get_checkpointer()
        >>> graph = create_supervisor_graph(checkpointer)
        >>> result = graph.invoke(
        ...     initial_state,
        ...     config={"configurable": {"thread_id": "user-123-session-456"}}
        ... )
    """
    # Import original 6 specialist agents
    from .material_analyst import MaterialAnalystAgent
    from .carbon_calculator import CarbonCalculatorAgent
    from .tgo_database import TGODatabaseAgent
    from .knowledge_graph import KnowledgeGraphAgent
    from .user_interaction import UserInteractionAgent

    # Import 6 additional specialist agents (Plan 03-03)
    from .boq_parser_agent import BOQParserAgent
    from .sustainability_agent import SustainabilityAgent
    from .cost_analyst_agent import CostAnalystAgent
    from .compliance_agent import ComplianceAgent
    from .report_generator_agent import ReportGeneratorAgent
    from .data_validator_agent import DataValidatorAgent

    # Initialize router and register all specialist agents
    router = SupervisorRouter()

    # Create original 6 agent instances with optional clients
    material_analyst = MaterialAnalystAgent(graphdb_client=graphdb_client)
    carbon_calculator = CarbonCalculatorAgent(carbon_pipeline=carbon_pipeline)
    tgo_database = TGODatabaseAgent(tgo_client=tgo_client)
    knowledge_graph = KnowledgeGraphAgent(graphdb_client=graphdb_client)
    user_interaction = UserInteractionAgent()

    # Create 6 additional agent instances (Plan 03-03)
    boq_parser = BOQParserAgent(boq_parser=boq_parser)
    sustainability = SustainabilityAgent(alternatives_engine=alternatives_engine)
    cost_analyst = CostAnalystAgent()
    compliance = ComplianceAgent(knowledge_graph=graphdb_client)
    report_generator = ReportGeneratorAgent()
    data_validator = DataValidatorAgent()

    # Register all 12 agents with router
    # Original 6 agents
    router.register_agent(material_analyst)
    router.register_agent(carbon_calculator)
    router.register_agent(tgo_database)
    router.register_agent(knowledge_graph)
    router.register_agent(user_interaction)

    # 6 additional agents
    router.register_agent(boq_parser)
    router.register_agent(sustainability)
    router.register_agent(cost_analyst)
    router.register_agent(compliance)
    router.register_agent(report_generator)
    router.register_agent(data_validator)

    # Set global router for supervisor_node
    set_router(router)

    logger.info(f"Registered {len(router.list_agents())} specialist agents with supervisor")

    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", END)

    return workflow.compile(checkpointer=checkpointer)


# All 12 specialist agents capability mapping for reference
# Note: This does not include the supervisor itself, which is the orchestrator
ALL_AGENTS = {
    # Original 5 specialist agents from Plan 03-01
    "material_analyst": ["match:materials", "optimize:carbon", "query:tgo"],
    "carbon_calculator": ["calculate:carbon"],
    "tgo_database": ["query:tgo"],
    "knowledge_graph": ["query:kg", "reason:semantic", "validate:compliance"],
    "user_interaction": ["interact:user"],
    # 6 additional specialist agents from Plan 03-03
    "boq_parser": ["parse:boq"],
    "sustainability": ["optimize:carbon", "recommend:strategies"],
    "cost_analyst": ["analyze:cost", "optimize:cost"],
    "compliance": ["validate:compliance", "check:trees", "check:edge"],
    "report_generator": ["generate:report"],
    "data_validator": ["validate:data", "check:quality"],
    # Supervisor is the orchestrator (12th component of the system)
    "supervisor": ["route:agents", "orchestrate:workflow"],
}

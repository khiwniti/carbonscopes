"""Supervisor agent for multi-agent orchestration.

This module implements the supervisor pattern for LangGraph multi-agent coordination.
The supervisor routes user queries to appropriate specialist agents based on capability matching.
For complex carbon credit workflows, it chains multiple agents sequentially.
"""

import asyncio
from langgraph.graph import StateGraph, END
from .state import AgentState
from .router import SupervisorRouter, detect_pipeline_need, get_carbon_pipeline_sequence
import logging

logger = logging.getLogger("agent.supervisor")

# Global router instance for production use
_router: SupervisorRouter | None = None

# Max hops to prevent infinite loops
MAX_PIPELINE_HOPS = 6


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
    """Supervisor node that routes to appropriate agent or sets up pipeline.

    For simple queries: routes to a single best-fit agent.
    For complex carbon credit workflows: sets up a sequential pipeline.

    Args:
        state: Current AgentState containing user query and agent history
        router: Optional router instance (uses global router if not provided)

    Returns:
        Updated AgentState with current_agent set and pipeline_queue populated
        for multi-agent workflows.
    """
    query = state["user_query"]
    agent_history = state.get("agent_history", [])

    # Use provided router or fall back to global router
    active_router = router if router is not None else _router

    if active_router is None:
        raise ValueError("No router configured. Call set_router() or pass router parameter.")

    # If we have a pipeline_queue in progress, pop the next agent
    pipeline_queue = list(state.get("pipeline_queue", []))
    if pipeline_queue:
        next_agent = pipeline_queue.pop(0)
        logger.info(f"Pipeline continuing with: {next_agent} (remaining: {pipeline_queue})")
        return {
            **state,
            "current_agent": next_agent,
            "agent_history": agent_history + [next_agent],
            "pipeline_queue": pipeline_queue,
        }

    # First visit: detect if this needs a full pipeline
    if not agent_history and detect_pipeline_need(query):
        pipeline = [a for a in get_carbon_pipeline_sequence() if a in active_router.agents]
        if pipeline:
            first_agent = pipeline.pop(0)
            logger.info(f"Pipeline detected — starting with {first_agent}, queuing: {pipeline}")
            return {
                **state,
                "current_agent": first_agent,
                "agent_history": [first_agent],
                "pipeline_queue": pipeline,
            }

    # Default: single-agent routing
    next_agent = active_router.route(query)
    logger.info(f"Routing query to: {next_agent}")

    return {
        **state,
        "current_agent": next_agent,
        "agent_history": agent_history + [next_agent],
        "pipeline_queue": [],
    }


async def agent_executor_node(state: AgentState, router: SupervisorRouter | None = None) -> AgentState:
    """Execute the currently selected agent and merge its results into state.

    This node runs after supervisor_node and calls the selected agent's
    execute_with_metrics() method, storing results in task_results.

    Args:
        state: AgentState with current_agent set by supervisor_node
        router: Optional router override (uses global router if not provided)

    Returns:
        Updated AgentState with task_results populated from agent execution
    """
    current_agent = state.get("current_agent", "")
    active_router = router if router is not None else _router

    if not current_agent or active_router is None:
        logger.warning("[AgentExecutor] No current_agent or router — skipping execution")
        return state

    agent = active_router.agents.get(current_agent)
    if agent is None:
        logger.error(f"[AgentExecutor] Agent '{current_agent}' not found in router")
        return {**state, "error_count": state.get("error_count", 0) + 1}

    try:
        metrics = await agent.execute_with_metrics(state)
        result = metrics.get("result", {})
        duration_ms = metrics.get("duration_ms", 0)

        logger.info(
            f"[AgentExecutor] {current_agent} completed in {duration_ms:.1f}ms "
            f"| keys={list(result.keys())}"
        )

        updated_task_results = {**state.get("task_results", {}), **result}
        return {**state, "task_results": updated_task_results}

    except Exception as e:
        logger.error(f"[AgentExecutor] {current_agent} failed: {e}", exc_info=True)
        return {**state, "error_count": state.get("error_count", 0) + 1}


def should_continue_pipeline(state: AgentState) -> str:
    """Conditional edge: decide whether to continue pipeline or finish.

    Returns:
        'continue' if more agents are queued, 'end' otherwise.
    """
    pipeline_queue = state.get("pipeline_queue", [])
    error_count = state.get("error_count", 0)

    if error_count >= 3:
        logger.warning("[Pipeline] Stopping due to too many errors")
        return "end"

    if len(state.get("agent_history", [])) >= MAX_PIPELINE_HOPS:
        logger.warning("[Pipeline] Stopping: max hops reached")
        return "end"

    if pipeline_queue:
        return "continue"

    return "end"


def create_supervisor_graph(
    checkpointer=None,
    graphdb_client=None,
    tgo_client=None,
    carbon_pipeline=None,
    alternatives_engine=None,
    boq_parser=None,
    router: SupervisorRouter | None = None,
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

    # Use provided router (e.g., from tests) or build the default production router
    if router is None:
        router = SupervisorRouter()

        # Create original 6 agent instances with optional clients
        material_analyst = MaterialAnalystAgent(graphdb_client=graphdb_client)
        carbon_calculator = CarbonCalculatorAgent(carbon_pipeline=carbon_pipeline)
        tgo_database = TGODatabaseAgent(tgo_client=tgo_client)
        knowledge_graph = KnowledgeGraphAgent(graphdb_client=graphdb_client)
        user_interaction = UserInteractionAgent()

        # Create 6 additional agent instances (Plan 03-03)
        boq_parser_agent = BOQParserAgent(boq_parser=boq_parser)
        sustainability = SustainabilityAgent(alternatives_engine=alternatives_engine)
        cost_analyst = CostAnalystAgent()
        compliance = ComplianceAgent(knowledge_graph=graphdb_client)
        report_generator = ReportGeneratorAgent()
        data_validator = DataValidatorAgent()

        # Register all 12 agents with router
        router.register_agent(material_analyst)
        router.register_agent(carbon_calculator)
        router.register_agent(tgo_database)
        router.register_agent(knowledge_graph)
        router.register_agent(user_interaction)
        router.register_agent(boq_parser_agent)
        router.register_agent(sustainability)
        router.register_agent(cost_analyst)
        router.register_agent(compliance)
        router.register_agent(report_generator)
        router.register_agent(data_validator)

    # Set global router for supervisor_node
    set_router(router)

    logger.info(f"Registered {len(router.list_agents())} specialist agents with supervisor")

    # Bind router into node closures so nodes are self-contained
    def _supervisor(state: AgentState) -> AgentState:
        return supervisor_node(state, router)

    async def _agent_executor(state: AgentState) -> AgentState:
        return await agent_executor_node(state, router)

    # LangGraph requires sync nodes when using graph.invoke() (sync API).
    # We expose the async version (_agent_executor) but also define a sync
    # shim so the compiled graph works in both sync test contexts and async
    # production contexts.  The graph always prefers async (ainvoke/astream)
    # in production; the sync shim is only hit by graph.invoke() in tests.
    def _agent_executor_sync(state: AgentState) -> AgentState:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            # Already inside an event loop (FastAPI / pytest-asyncio) —
            # run the coroutine in a fresh thread with its own loop.
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, agent_executor_node(state, router))
                return future.result()
        else:
            return asyncio.run(agent_executor_node(state, router))

    # Build graph: supervisor → executor → (continue pipeline | end)
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", _supervisor)
    workflow.add_node("agent_executor", _agent_executor_sync)

    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "agent_executor")
    workflow.add_conditional_edges(
        "agent_executor",
        should_continue_pipeline,
        {
            "continue": "supervisor",   # Loop back to pop next agent from queue
            "end": END,
        }
    )

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

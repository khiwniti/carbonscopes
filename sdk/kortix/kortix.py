from .api import agents, threads
from .agent import CarbonScopeAgent
from .thread import CarbonScopeThread
from .tools import AgentPressTools, MCPTools


class CarbonScope:
    def __init__(self, api_key: str, api_url="https://api.CarbonScope.com/v1"):
        self._agents_client = agents.create_agents_client(api_url, api_key)
        self._threads_client = threads.create_threads_client(api_url, api_key)

        self.Agent = CarbonScopeAgent(self._agents_client)
        self.Thread = CarbonScopeThread(self._threads_client)

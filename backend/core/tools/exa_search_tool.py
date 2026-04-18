"""Exa neural search tool for agents.

Exa is a neural search engine optimised for AI applications — it understands
semantic meaning rather than just keywords, making it ideal for carbon credit
research, EPD lookups, and sustainability standards queries.
"""

from core.agentpress.tool import Tool, ToolResult, openapi_schema, tool_metadata
from core.utils.config import config
from core.utils.logger import logger

# Carbon/sustainability focused domains
CARBON_DOMAINS = [
    "ecoinvent.org",
    "environdec.com",       # International EPD System
    "epd-norway.no",
    "breeam.com",
    "usgbc.org",            # LEED
    "edge.thegreenbuilding.org",
    "goldstandard.org",
    "verra.org",            # Verified Carbon Standard
    "carbonregistry.com",
    "cdp.net",
    "climateaction.unfccc.int",
    "iea.org",
    "ipcc.ch",
    "carboncredits.com",
    "icvcm.org",            # Integrity Council for Voluntary Carbon Market
    "sciencebasedtargets.org",
    "sustainalytics.com",
    "planetmark.com",
    "lowcarbonlivingcrc.com.au",
    "concrete.org",
    "steel.org",
    "timberdevelopment.com.au",
    "worldgbc.org",         # World Green Building Council
]


@tool_metadata(
    display_name="ExaSearch",
    description="Neural web search powered by Exa — optimised for carbon, sustainability, EPD, and materials research",
    icon="Search",
    color="bg-emerald-100 dark:bg-emerald-800/50",
    weight=35,
    visible=True,
    usage_guide="""
## ExaSearch — Neural search for carbon & sustainability research

Uses Exa's neural search engine, which understands semantic meaning for technical queries.
Better than keyword search for: EPD lookups, carbon credit prices, compliance standards, material data.

### Available methods
- **exa_search**: General neural search across the web
- **exa_carbon_search**: Targeted search within carbon/sustainability domains
- **exa_find_similar**: Find pages similar to a given URL (great for finding EPD alternatives)

### When to use vs web_search
- Use `exa_search` for complex semantic queries ("what is the embodied carbon of CLT per m3")
- Use `exa_carbon_search` for anything carbon-specific (faster, higher quality sources)
- Use `web_search` for simple keyword lookups or recent news

### Carbon credit workflow
1. `exa_carbon_search("current voluntary carbon credit price per tonne VCS Gold Standard 2025")`
2. `exa_search("LEED v4 embodied carbon material credits MRc4")`
3. `exa_find_similar("https://environdec.com/library/...")` to find related EPDs
""",
)
class ExaSearchTool(Tool):
    """Neural search tool backed by the Exa API."""

    def __init__(self):
        super().__init__()
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from exa_py import AsyncExa  # type: ignore
                self._client = AsyncExa(api_key=config.EXA_API_KEY)
            except ImportError:
                raise RuntimeError(
                    "exa-py is not installed. Run: uv add exa-py>=1.14.0"
                )
        return self._client

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "exa_search",
            "description": (
                "Perform a neural web search using Exa. Returns semantically relevant results "
                "with full text content. Best for complex technical queries about carbon, "
                "materials, EPDs, sustainability standards, and carbon credits."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query. Be specific and descriptive for best results.",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 10).",
                        "default": 5,
                    },
                    "max_characters": {
                        "type": "integer",
                        "description": "Max characters of content to return per result (default 2000).",
                        "default": 2000,
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of domains to restrict search to.",
                    },
                    "start_published_date": {
                        "type": "string",
                        "description": "Only return results published after this date (YYYY-MM-DD).",
                    },
                },
                "required": ["query"],
            },
        },
    })
    async def exa_search(
        self,
        query: str,
        num_results: int = 5,
        max_characters: int = 2000,
        include_domains: list = None,
        start_published_date: str = None,
    ) -> ToolResult:
        """General neural web search using Exa."""
        try:
            client = self._get_client()
            num_results = min(max(1, num_results), 10)

            kwargs = {
                "num_results": num_results,
                "type": "neural",
                "use_autoprompt": True,
                "contents": {"text": {"max_characters": max_characters}},
            }
            if include_domains:
                kwargs["include_domains"] = include_domains
            if start_published_date:
                kwargs["start_published_date"] = start_published_date

            response = await client.search_and_contents(query, **kwargs)

            results = []
            for r in response.results:
                results.append({
                    "title": r.title,
                    "url": r.url,
                    "published_date": getattr(r, "published_date", None),
                    "score": getattr(r, "score", None),
                    "text": getattr(r, "text", "")[:max_characters] if hasattr(r, "text") else "",
                })

            return self.success_response({
                "query": query,
                "num_results": len(results),
                "results": results,
            })

        except Exception as e:
            logger.error(f"[ExaSearch] exa_search failed: {e}", exc_info=True)
            return self.fail_response(f"Exa search failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "exa_carbon_search",
            "description": (
                "Neural search restricted to authoritative carbon, sustainability, and EPD sources. "
                "Use this for: carbon credit prices, EPD data, embodied carbon benchmarks, "
                "LEED/BREEAM requirements, GHG emission factors, and carbon offset project details. "
                "Higher quality than general search for carbon-specific queries."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Carbon/sustainability specific query. Examples: "
                                       "'embodied carbon concrete C30 kgCO2e per m3', "
                                       "'voluntary carbon credit price tonne 2025', "
                                       "'LEED v4 MRc4 carbon sequestration credit threshold'",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results (default 5, max 10).",
                        "default": 5,
                    },
                    "max_characters": {
                        "type": "integer",
                        "description": "Max characters per result (default 3000 — carbon data often needs context).",
                        "default": 3000,
                    },
                    "start_published_date": {
                        "type": "string",
                        "description": "Filter to results after this date (YYYY-MM-DD). Useful for current prices.",
                    },
                },
                "required": ["query"],
            },
        },
    })
    async def exa_carbon_search(
        self,
        query: str,
        num_results: int = 5,
        max_characters: int = 3000,
        start_published_date: str = None,
    ) -> ToolResult:
        """Search within authoritative carbon and sustainability domains."""
        try:
            client = self._get_client()
            num_results = min(max(1, num_results), 10)

            kwargs = {
                "num_results": num_results,
                "type": "neural",
                "use_autoprompt": True,
                "include_domains": CARBON_DOMAINS,
                "contents": {"text": {"max_characters": max_characters}},
            }
            if start_published_date:
                kwargs["start_published_date"] = start_published_date

            response = await client.search_and_contents(query, **kwargs)

            results = []
            for r in response.results:
                results.append({
                    "title": r.title,
                    "url": r.url,
                    "published_date": getattr(r, "published_date", None),
                    "score": getattr(r, "score", None),
                    "text": getattr(r, "text", "")[:max_characters] if hasattr(r, "text") else "",
                })

            return self.success_response({
                "query": query,
                "source_restriction": "carbon/sustainability domains",
                "num_results": len(results),
                "results": results,
            })

        except Exception as e:
            logger.error(f"[ExaSearch] exa_carbon_search failed: {e}", exc_info=True)
            return self.fail_response(f"Exa carbon search failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "exa_find_similar",
            "description": (
                "Find web pages similar to a given URL. Ideal for finding alternative EPDs "
                "for a material, related carbon offset projects, or comparable sustainability reports. "
                "Example: find EPDs similar to a known EPD URL to compare carbon values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to find similar pages for.",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of similar pages to return (default 5, max 10).",
                        "default": 5,
                    },
                    "max_characters": {
                        "type": "integer",
                        "description": "Max characters of content per result (default 1500).",
                        "default": 1500,
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Restrict similar results to these domains.",
                    },
                },
                "required": ["url"],
            },
        },
    })
    async def exa_find_similar(
        self,
        url: str,
        num_results: int = 5,
        max_characters: int = 1500,
        include_domains: list = None,
    ) -> ToolResult:
        """Find pages semantically similar to a given URL."""
        try:
            client = self._get_client()
            num_results = min(max(1, num_results), 10)

            kwargs = {
                "num_results": num_results,
                "contents": {"text": {"max_characters": max_characters}},
            }
            if include_domains:
                kwargs["include_domains"] = include_domains

            response = await client.find_similar_and_contents(url, **kwargs)

            results = []
            for r in response.results:
                results.append({
                    "title": r.title,
                    "url": r.url,
                    "published_date": getattr(r, "published_date", None),
                    "score": getattr(r, "score", None),
                    "text": getattr(r, "text", "")[:max_characters] if hasattr(r, "text") else "",
                })

            return self.success_response({
                "source_url": url,
                "num_results": len(results),
                "results": results,
            })

        except Exception as e:
            logger.error(f"[ExaSearch] exa_find_similar failed: {e}", exc_info=True)
            return self.fail_response(f"Exa find similar failed: {str(e)}")

"""
Step 9: CarbonScope Admin API Key
"""

from setup.steps.base import BaseStep, StepResult
from setup.utils.secrets import generate_admin_api_key


class CarbonScopeStep(BaseStep):
    """Auto-generate CarbonScope admin API key."""

    name = "CarbonScope"
    display_name = "CarbonScope Admin API Key"
    order = 9
    required = True
    depends_on = ["requirements"]

    def run(self) -> StepResult:
        # Always generate a new key (overwrite existing if any)
        self.info("Generating a secure admin API key for CarbonScope administrative functions...")

        self.config.CarbonScope.CarbonScope_ADMIN_API_KEY = generate_admin_api_key()

        self.success("CarbonScope admin API key generated.")
        self.success("CarbonScope admin configuration saved.")

        return StepResult.ok(
            "CarbonScope admin key generated",
            {"CarbonScope": self.config.CarbonScope.model_dump()},
        )

    def get_config_keys(self):
        return ["CarbonScope_ADMIN_API_KEY"]

    def is_complete(self) -> bool:
        return bool(self.config.CarbonScope.CarbonScope_ADMIN_API_KEY)

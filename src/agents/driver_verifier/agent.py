from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_driver_information,
    get_coverage_details
)


class DriverVerifierAgent(BaseReActAgent):
    """ReAct agent that verifies driver eligibility and compliance using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to driver verification."""
        return [
            get_driver_information,
            get_coverage_details
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
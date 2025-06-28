from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_claim_basic_info,
    get_policy_information,
    get_vehicle_information,
    get_coverage_details,
    get_liability_information
)


class CoverageEvaluatorAgent(BaseReActAgent):
    """ReAct agent that evaluates coverage limits and endorsements using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to coverage evaluation."""
        return [
            get_claim_basic_info,
            get_policy_information,
            get_vehicle_information,
            get_coverage_details,
            get_liability_information
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
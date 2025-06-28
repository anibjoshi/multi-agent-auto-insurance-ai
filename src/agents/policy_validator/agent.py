from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_claim_basic_info,
    get_policy_information,
    calculate_days_between_dates
)


class PolicyValidatorAgent(BaseReActAgent):
    """ReAct agent that validates policy eligibility and timing using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to policy validation."""
        return [
            get_claim_basic_info,
            get_policy_information,
            calculate_days_between_dates
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
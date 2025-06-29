from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_claim_basic_info,
    get_catastrophe_information,
    get_policy_information,
    calculate_days_since_policy_start
)


class CatastropheCheckerAgent(BaseReActAgent):
    """ReAct agent that handles catastrophic events and zone-specific rules using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to catastrophe checking."""
        return [
            get_claim_basic_info,
            get_catastrophe_information,
            get_policy_information,
            calculate_days_since_policy_start
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
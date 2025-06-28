from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_claim_basic_info,
    get_vehicle_information,
    check_total_loss_threshold
)


class VehicleDamageEvaluatorAgent(BaseReActAgent):
    """ReAct agent that evaluates vehicle damage and coverage eligibility using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to vehicle damage evaluation."""
        return [
            get_claim_basic_info,
            get_vehicle_information,
            check_total_loss_threshold
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
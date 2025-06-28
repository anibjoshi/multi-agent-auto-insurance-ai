from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_rental_information,
    get_coverage_details
)


class RentalBenefitCheckerAgent(BaseReActAgent):
    """ReAct agent that evaluates rental car and loss-of-use benefits using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to rental benefit checking."""
        return [
            get_rental_information,
            get_coverage_details
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
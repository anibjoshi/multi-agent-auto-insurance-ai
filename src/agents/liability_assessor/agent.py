from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_liability_information,
    get_documentation_info
)


class LiabilityAssessorAgent(BaseReActAgent):
    """ReAct agent that assesses liability and fault allocation using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to liability assessment."""
        return [
            get_liability_information,
            get_documentation_info
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
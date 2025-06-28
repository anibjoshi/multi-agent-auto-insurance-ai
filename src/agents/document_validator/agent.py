from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_claim_basic_info,
    get_documentation_info
)


class DocumentValidatorAgent(BaseReActAgent):
    """ReAct agent that validates required documents using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to document validation."""
        return [
            get_claim_basic_info,
            get_documentation_info
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
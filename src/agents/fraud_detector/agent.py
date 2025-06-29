from typing import List, Callable
from ..base import BaseReActAgent
from ...tools import (
    get_claim_basic_info,
    get_vehicle_information,
    check_mileage_discrepancy
)


class FraudDetectorAgent(BaseReActAgent):
    """ReAct agent that scans for fraud and anomaly patterns using tools."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to fraud detection."""
        return [
            get_claim_basic_info,
            get_vehicle_information,
            check_mileage_discrepancy
        ]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file 
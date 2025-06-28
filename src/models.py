from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


class ClaimData(BaseModel):
    """Auto insurance claim data model matching the sample input format."""
    claim_id: str
    incident_date: date
    report_date: date
    state: str
    policy_start_date: date
    policy_end_date: date
    coverage_suspension_start: Optional[date] = None
    coverage_suspension_end: Optional[date] = None
    cancellation_reason: Optional[str] = None
    per_claim_limit: int
    annual_aggregate_limit: int
    remaining_aggregate_limit: int
    endorsement_rental_days_allowed: int
    endorsement_rental_daily_cap: int
    endorsement_um_uim: bool
    endorsement_diminished_value: bool
    endorsement_rideshare_use: bool
    driver_name: str
    driver_license_status: str
    driver_listed_on_policy: bool
    driver_excluded: bool
    driver_under_influence: bool
    driver_use_type: str
    vin: str
    odometer_at_loss: int
    telematics_odometer: int
    damage_description: str
    damage_type: str
    repair_estimate: int
    actual_cash_value: int
    aftermarket_mods: bool
    recall_active: bool
    police_report_attached: bool
    loss_location_flood_zone: str
    cat_event_code: Optional[str] = None
    rental_days_claimed: int
    loss_of_use_daily_rate: int
    at_fault_party: str
    insured_liability_percent: int
    third_party_insurer: Optional[str] = None
    injuries_reported: bool
    primary_med_provider: Optional[str] = None
    expected_status: Optional[str] = None
    expected_reason: Optional[str] = None


class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    agent: str
    status: Literal["APPROVED", "REJECTED", "PARTIAL", "ESCALATE"]
    reason: str = Field(description="Concise slug in snake_case")
    explanation: str = Field(description="1-2 sentence human-readable rationale")


class ClaimProcessingState(BaseModel):
    """State object for the claim processing workflow."""
    claim_data: ClaimData
    agent_responses: list[AgentResponse] = Field(default_factory=list)
    final_decision: Optional[AgentResponse] = None
    processing_complete: bool = False 
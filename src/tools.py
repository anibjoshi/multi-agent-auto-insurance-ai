"""
Tools for ReAct agents to access and analyze claim data.
"""

from typing import Dict, Any, Optional
from datetime import datetime, date
import json
from langchain_core.tools import tool
from .models import ClaimData


# Global claim data storage for the current processing session
_current_claim_data: Optional[ClaimData] = None


def set_current_claim_data(claim_data: ClaimData) -> None:
    """Set the current claim data for tool access."""
    global _current_claim_data
    _current_claim_data = claim_data


@tool
def get_claim_basic_info() -> str:
    """Get basic claim information including ID, dates, and state."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "claim_id": _current_claim_data.claim_id,
        "incident_date": str(_current_claim_data.incident_date),
        "report_date": str(_current_claim_data.report_date),
        "state": _current_claim_data.state,
        "damage_type": _current_claim_data.damage_type,
        "damage_description": _current_claim_data.damage_description
    }
    return json.dumps(info, indent=2)


@tool
def get_policy_information() -> str:
    """Get policy-related information including dates, limits, and endorsements."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "policy_start_date": str(_current_claim_data.policy_start_date),
        "policy_end_date": str(_current_claim_data.policy_end_date),
        "coverage_suspension_start": str(_current_claim_data.coverage_suspension_start) if _current_claim_data.coverage_suspension_start else None,
        "coverage_suspension_end": str(_current_claim_data.coverage_suspension_end) if _current_claim_data.coverage_suspension_end else None,
        "cancellation_reason": _current_claim_data.cancellation_reason,
        "per_claim_limit": _current_claim_data.per_claim_limit,
        "annual_aggregate_limit": _current_claim_data.annual_aggregate_limit,
        "remaining_aggregate_limit": _current_claim_data.remaining_aggregate_limit
    }
    return json.dumps(info, indent=2)


@tool
def get_driver_information() -> str:
    """Get driver-related information including license status and policy listing."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "driver_name": _current_claim_data.driver_name,
        "driver_license_status": _current_claim_data.driver_license_status,
        "driver_listed_on_policy": _current_claim_data.driver_listed_on_policy,
        "driver_excluded": _current_claim_data.driver_excluded,
        "driver_under_influence": _current_claim_data.driver_under_influence,
        "driver_use_type": _current_claim_data.driver_use_type
    }
    return json.dumps(info, indent=2)


@tool
def get_vehicle_information() -> str:
    """Get vehicle and damage information."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "vin": _current_claim_data.vin,
        "odometer_at_loss": _current_claim_data.odometer_at_loss,
        "telematics_odometer": _current_claim_data.telematics_odometer,
        "repair_estimate": _current_claim_data.repair_estimate,
        "actual_cash_value": _current_claim_data.actual_cash_value,
        "aftermarket_mods": _current_claim_data.aftermarket_mods,
        "recall_active": _current_claim_data.recall_active
    }
    return json.dumps(info, indent=2)


@tool
def get_coverage_details() -> str:
    """Get coverage and endorsement details."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "endorsement_rental_days_allowed": _current_claim_data.endorsement_rental_days_allowed,
        "endorsement_rental_daily_cap": _current_claim_data.endorsement_rental_daily_cap,
        "endorsement_um_uim": _current_claim_data.endorsement_um_uim,
        "endorsement_diminished_value": _current_claim_data.endorsement_diminished_value,
        "endorsement_rideshare_use": _current_claim_data.endorsement_rideshare_use
    }
    return json.dumps(info, indent=2)


@tool
def get_liability_information() -> str:
    """Get liability and fault information."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "at_fault_party": _current_claim_data.at_fault_party,
        "insured_liability_percent": _current_claim_data.insured_liability_percent,
        "third_party_insurer": _current_claim_data.third_party_insurer
    }
    return json.dumps(info, indent=2)


@tool
def get_rental_information() -> str:
    """Get rental car and loss of use information."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "rental_days_claimed": _current_claim_data.rental_days_claimed,
        "loss_of_use_daily_rate": _current_claim_data.loss_of_use_daily_rate,
        "endorsement_rental_days_allowed": _current_claim_data.endorsement_rental_days_allowed,
        "endorsement_rental_daily_cap": _current_claim_data.endorsement_rental_daily_cap
    }
    return json.dumps(info, indent=2)


@tool
def get_catastrophe_information() -> str:
    """Get catastrophe and environmental information."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "loss_location_flood_zone": _current_claim_data.loss_location_flood_zone,
        "cat_event_code": _current_claim_data.cat_event_code,
        "damage_type": _current_claim_data.damage_type
    }
    return json.dumps(info, indent=2)


@tool
def get_documentation_info() -> str:
    """Get document-related information."""
    if not _current_claim_data:
        return "No claim data available"
    
    info = {
        "police_report_attached": _current_claim_data.police_report_attached,
        "state": _current_claim_data.state,
        "injuries_reported": _current_claim_data.injuries_reported,
        "primary_med_provider": _current_claim_data.primary_med_provider
    }
    return json.dumps(info, indent=2)


@tool
def calculate_days_between_dates(start_date: str, end_date: str) -> str:
    """Calculate the number of days between two dates."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        delta = (end - start).days
        return f"Days between {start_date} and {end_date}: {delta}"
    except Exception as e:
        return f"Error calculating days: {str(e)}"


@tool
def check_total_loss_threshold() -> str:
    """Check if repair estimate meets total loss threshold (80% of ACV)."""
    if not _current_claim_data:
        return "No claim data available"
    
    threshold = _current_claim_data.actual_cash_value * 0.8
    is_total_loss = _current_claim_data.repair_estimate >= threshold
    
    result = {
        "repair_estimate": _current_claim_data.repair_estimate,
        "actual_cash_value": _current_claim_data.actual_cash_value,
        "total_loss_threshold": threshold,
        "is_total_loss": is_total_loss
    }
    return json.dumps(result, indent=2)


@tool
def check_mileage_discrepancy() -> str:
    """Check for mileage discrepancies between telematics and reported odometer."""
    if not _current_claim_data:
        return "No claim data available"
    
    # Allow for 3000 mile variance as per fraud detection rules
    allowed_variance = 3000
    discrepancy = _current_claim_data.odometer_at_loss - _current_claim_data.telematics_odometer
    is_suspicious = discrepancy > allowed_variance
    
    result = {
        "odometer_at_loss": _current_claim_data.odometer_at_loss,
        "telematics_odometer": _current_claim_data.telematics_odometer,
        "discrepancy": discrepancy,
        "allowed_variance": allowed_variance,
        "is_suspicious": is_suspicious
    }
    return json.dumps(result, indent=2)


@tool
def calculate_days_since_policy_start() -> str:
    """Calculate the number of days between policy start date and incident date."""
    if not _current_claim_data:
        return "No claim data available"
    
    try:
        policy_start = _current_claim_data.policy_start_date
        incident_date = _current_claim_data.incident_date
        days_since_start = (incident_date - policy_start).days
        
        result = {
            "policy_start_date": str(policy_start),
            "incident_date": str(incident_date),
            "days_since_policy_start": days_since_start
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error calculating days since policy start: {str(e)}" 
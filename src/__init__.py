"""
Multi-Agent Auto Insurance Claim Processing System

A production-grade multi-agent AI system for automated auto insurance claim processing.
"""

__version__ = "1.0.0"
__author__ = "Auto Insurance AI Team"

# Import main components for easy access
from .models import ClaimData, AgentResponse, ClaimProcessingState
from .workflow import ClaimProcessingWorkflow
# Removed ParallelClaimProcessingWorkflow - consolidated into main workflow.py
from .config import settings
from .agents import (
    BaseReActAgent,
    PolicyValidatorAgent,
    DocumentValidatorAgent,
    DriverVerifierAgent,
    VehicleDamageEvaluatorAgent,
    CoverageEvaluatorAgent,
    CatastropheCheckerAgent,
    LiabilityAssessorAgent,
    RentalBenefitCheckerAgent,
    FraudDetectorAgent,
    ClaimDeciderAgent
)

__all__ = [
    "ClaimData",
    "AgentResponse", 
    "ClaimProcessingState",
    "ClaimProcessingWorkflow",
    "settings",
    "BaseReActAgent",
    "PolicyValidatorAgent",
    "DocumentValidatorAgent",
    "DriverVerifierAgent",
    "VehicleDamageEvaluatorAgent",
    "CoverageEvaluatorAgent",
    "CatastropheCheckerAgent",
    "LiabilityAssessorAgent",
    "RentalBenefitCheckerAgent",
    "FraudDetectorAgent",
    "ClaimDeciderAgent"
] 
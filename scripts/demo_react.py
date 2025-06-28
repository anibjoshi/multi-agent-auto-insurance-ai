#!/usr/bin/env python3
"""
Demo script for the ReAct Multi-Agent Auto Insurance Claim Processing System.

This script demonstrates the ReAct agents using tool calling for claim analysis.
"""

import asyncio
import json
import time
from datetime import datetime, date
from pathlib import Path

from src.config import settings
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow


def print_banner():
    """Print the demo banner."""
    print("=" * 80)
    print("🚗 ReAct MULTI-AGENT AUTO INSURANCE CLAIM PROCESSING SYSTEM DEMO")
    print("=" * 80)
    print("🎯 Use Case: Process claims using ReAct agents with tool calling")
    print("🤖 Architecture: ReAct agents + LangGraph orchestration + Tool-based reasoning")
    print("⚡ Features: Reasoning, Acting, Tool calling, Parallel processing")
    print("=" * 80)


def create_demo_claim():
    """Create a demonstration claim for ReAct agent testing."""
    return {
        "claim_id": "REACT-DEMO-001",
        "description": "ReAct demonstration claim - complex scenario",
        "data": {
            "claim_id": "REACT-DEMO-001",
            "incident_date": "2025-01-20",
            "report_date": "2025-01-22",
            "state": "TX",
            "policy_start_date": "2024-06-01",
            "policy_end_date": "2025-06-01",
            "coverage_suspension_start": None,
            "coverage_suspension_end": None,
            "cancellation_reason": None,
            "per_claim_limit": 25000,
            "annual_aggregate_limit": 50000,
            "remaining_aggregate_limit": 48000,
            "endorsement_rental_days_allowed": 15,
            "endorsement_rental_daily_cap": 40,
            "endorsement_um_uim": True,
            "endorsement_diminished_value": False,
            "endorsement_rideshare_use": False,
            "driver_name": "John ReAct Demo",
            "driver_license_status": "valid",
            "driver_listed_on_policy": True,
            "driver_excluded": False,
            "driver_under_influence": False,
            "driver_use_type": "personal",
            "vin": "REACT123456789",
            "odometer_at_loss": 45000,
            "telematics_odometer": 45000,
            "damage_description": "Complex collision with potential total loss",
            "damage_type": "collision",
            "repair_estimate": 22000,  # Close to 80% of ACV - triggers total loss evaluation
            "actual_cash_value": 28000,
            "aftermarket_mods": False,
            "recall_active": False,
            "police_report_attached": True,
            "loss_location_flood_zone": "low",
            "cat_event_code": None,
            "rental_days_claimed": 12,
            "loss_of_use_daily_rate": 35,
            "at_fault_party": "insured",
            "insured_liability_percent": 100,
            "third_party_insurer": None,
            "injuries_reported": False,
            "primary_med_provider": None
        }
    }


async def demo_react_agents(workflow: ClaimProcessingWorkflow, claim_sample: dict):
    """Demonstrate ReAct agents with detailed tool usage analysis."""
    print(f"\n{'🔍 ReAct AGENTS PROCESSING: ' + claim_sample['claim_id']:=^70}")
    print(f"📝 Description: {claim_sample['description']}")
    
    claim = ClaimData(**claim_sample['data'])
    
    print(f"👤 Driver: {claim.driver_name}")
    print(f"🚗 Damage: {claim.damage_type} - ${claim.repair_estimate:,}")
    print(f"💰 ACV: ${claim.actual_cash_value:,} (Total Loss Threshold: ${claim.actual_cash_value * 0.8:,.0f})")
    print(f"📍 State: {claim.state}")
    print(f"📅 Incident: {claim.incident_date} | Reported: {claim.report_date}")
    
    print(f"\n⚙️  Processing through ReAct agents using tool calling...")
    print(f"🔧 Each agent will:")
    print(f"   • Reason about the claim")
    print(f"   • Use specialized tools to gather data")
    print(f"   • Act based on tool responses")
    print(f"   • Apply domain-specific rules")
    
    start_time = time.time()
    result = await workflow.process_claim(claim)
    processing_time = time.time() - start_time
    
    # Show final decision with emoji
    status_emoji = {
        "APPROVED": "✅",
        "REJECTED": "❌",
        "PARTIAL": "⚠️",
        "ESCALATE": "🔴"
    }.get(result.final_decision.status, "❓")
    
    print(f"\n{status_emoji} FINAL ReAct DECISION: {result.final_decision.status}")
    print(f"📋 Reason: {result.final_decision.reason}")
    print(f"💬 Explanation: {result.final_decision.explanation}")
    print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
    
    # Show detailed agent breakdown with tool-based reasoning context
    print(f"\n📊 ReAct AGENT RESPONSES:")
    approved = rejected = partial = escalate = 0
    
    agent_tool_descriptions = {
        "PolicyValidator": "Used tools: get_claim_basic_info, get_policy_information, calculate_days_between_dates",
        "DocumentValidator": "Used tools: get_claim_basic_info, get_documentation_info", 
        "DriverVerifier": "Used tools: get_driver_information, get_coverage_details",
        "VehicleDamageEvaluator": "Used tools: get_claim_basic_info, get_vehicle_information, check_total_loss_threshold",
        "CoverageEvaluator": "Used tools: get_policy_information, get_vehicle_information, get_coverage_details",
        "CatastropheChecker": "Used tools: get_claim_basic_info, get_catastrophe_information",
        "LiabilityAssessor": "Used tools: get_liability_information, get_documentation_info",
        "RentalBenefitChecker": "Used tools: get_rental_information, get_coverage_details", 
        "FraudDetector": "Used tools: get_vehicle_information, check_mileage_discrepancy, calculate_days_between_dates"
    }
    
    for response in result.agent_responses:
        emoji = {
            "APPROVED": "✅",
            "REJECTED": "❌",
            "PARTIAL": "⚠️",
            "ESCALATE": "🔴"
        }.get(response.status, "❓")
        
        agent_name = response.agent
        tool_description = agent_tool_descriptions.get(agent_name, "Unknown tools")
        
        print(f"\n   {emoji} {agent_name:<20} {response.status:<10}")
        print(f"      🔧 {tool_description}")
        print(f"      📄 Decision: {response.reason}")
        print(f"      💭 Reasoning: {response.explanation}")
        
        if response.status == "APPROVED":
            approved += 1
        elif response.status == "REJECTED":
            rejected += 1
        elif response.status == "PARTIAL":
            partial += 1
        elif response.status == "ESCALATE":
            escalate += 1
    
    print(f"\n📈 ReAct Agent Summary: ✅{approved} ❌{rejected} ⚠️{partial} 🔴{escalate}")
    
    return result


async def demo_tool_capabilities(workflow: ClaimProcessingWorkflow):
    """Demonstrate the tool capabilities available to ReAct agents."""
    print(f"\n{'🔧 ReAct AGENT TOOLS DEMONSTRATION':=^70}")
    print("Each ReAct agent has access to specialized tools for data analysis:")
    
    tools_by_agent = {
        "PolicyValidator": [
            "get_claim_basic_info() - Basic claim and incident information",
            "get_policy_information() - Policy dates, limits, and status",
            "calculate_days_between_dates() - Date calculations for validation"
        ],
        "DocumentValidator": [
            "get_claim_basic_info() - Claim details for document requirements",
            "get_documentation_info() - Police reports and document status"
        ],
        "DriverVerifier": [
            "get_driver_information() - Driver eligibility and status",
            "get_coverage_details() - Endorsements and coverage details"
        ],
        "VehicleDamageEvaluator": [
            "get_claim_basic_info() - Damage type and description",
            "get_vehicle_information() - Vehicle details and repair estimates",
            "check_total_loss_threshold() - 80% ACV threshold calculation"
        ],
        "CoverageEvaluator": [
            "get_policy_information() - Coverage limits and aggregates",
            "get_vehicle_information() - Repair cost analysis",
            "get_coverage_details() - Endorsement validation",
            "get_liability_information() - Third-party coverage requirements"
        ],
        "FraudDetector": [
            "get_vehicle_information() - Odometer and mileage data",
            "check_mileage_discrepancy() - Automated fraud detection",
            "get_catastrophe_information() - CAT fraud pattern analysis",
            "calculate_days_between_dates() - Timing anomaly detection"
        ]
    }
    
    for agent_name, tools in tools_by_agent.items():
        print(f"\n🤖 {agent_name}:")
        for tool in tools:
            print(f"   🔧 {tool}")


async def main():
    """Main ReAct demo function."""
    print_banner()
    
    # Check API key
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in the .env file:")
        print("OPENAI_API_KEY=your_key_here")
        return
    
    print(f"🔧 Initializing ReAct workflow with {settings.openai_model}...")
    
    try:
        workflow = ClaimProcessingWorkflow(
            openai_api_key=settings.openai_api_key,
            model_name=settings.openai_model
        )
        print("✅ ReAct Workflow initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        return
    
    # Show workflow architecture
    print(workflow.get_workflow_visualization())
    
    # Demonstrate tool capabilities
    await demo_tool_capabilities(workflow)
    
    # Create and process demo claim
    demo_claim = create_demo_claim()
    
    # Demo ReAct agent processing
    print(f"\n{'📋 ReAct AGENT CLAIM PROCESSING':=^70}")
    await demo_react_agents(workflow, demo_claim)
    
    # Final summary
    print(f"\n{'🎉 ReAct DEMO COMPLETED':=^70}")
    print("✨ ReAct Features Demonstrated:")
    print("   🤖 Reasoning agents that think step-by-step")
    print("   🔧 Tool calling for specialized data access")
    print("   ⚡ Parallel execution of ReAct agents")
    print("   🎯 Domain-specific tool sets for each agent")
    print("   📊 Comprehensive reasoning and decision audit trail")
    print("   🔄 LangGraph orchestration of ReAct workflow")
    
    print(f"\n🚀 Next Steps:")
    print("   • Run 'python api/main.py' to start the ReAct API server")
    print("   • Visit http://localhost:8000/docs for interactive API documentation")
    print("   • Each agent now uses ReAct pattern with specialized tools")
    print("   • Tools provide structured data access instead of raw JSON prompts")
    
    print(f"\n{'ReAct Agents: Reasoning + Acting + Tool Calling = Powerful Claims Processing!':^70}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main()) 
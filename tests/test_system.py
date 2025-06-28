#!/usr/bin/env python3
"""
Test script for the Multi-Agent Auto Insurance Claim Processing System.

This script demonstrates how to use the system with sample claim data.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from src.config import settings
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow


async def test_single_claim(workflow: ClaimProcessingWorkflow, claim_data: dict):
    """Test processing a single claim."""
    print(f"\n{'='*60}")
    print(f"Processing Claim: {claim_data['claim_id']}")
    print(f"{'='*60}")
    
    # Convert to ClaimData model
    claim = ClaimData(**claim_data)
    
    # Print claim summary
    print(f"Driver: {claim.driver_name}")
    print(f"Damage Type: {claim.damage_type}")
    print(f"Repair Estimate: ${claim.repair_estimate:,}")
    print(f"Expected Status: {claim.expected_status}")
    
    # Process the claim
    start_time = time.time()
    try:
        result = await workflow.process_claim(claim)
        processing_time = time.time() - start_time
        
        print(f"\n📋 PROCESSING RESULTS:")
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"\n🎯 FINAL DECISION:")
        print(f"Status: {result.final_decision.status}")
        print(f"Reason: {result.final_decision.reason}")
        print(f"Explanation: {result.final_decision.explanation}")
        
        print(f"\n🔍 AGENT RESPONSES:")
        for response in result.agent_responses:
            status_emoji = {
                "APPROVED": "✅",
                "REJECTED": "❌", 
                "PARTIAL": "⚠️",
                "ESCALATE": "🔴"
            }.get(response.status, "❓")
            
            print(f"{status_emoji} {response.agent}: {response.status} - {response.reason}")
            print(f"   └─ {response.explanation}")
        
        # Compare with expected result
        if claim.expected_status:
            match = result.final_decision.status == claim.expected_status
            match_emoji = "✅" if match else "❌"
            print(f"\n{match_emoji} Expected: {claim.expected_status}, Got: {result.final_decision.status}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing claim: {e}")
        return None


async def test_batch_processing(workflow: ClaimProcessingWorkflow, claims_data: list, batch_size: int = 5):
    """Test batch processing of multiple claims."""
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING TEST ({batch_size} claims)")
    print(f"{'='*60}")
    
    # Take first batch_size claims
    batch_claims = claims_data[:batch_size]
    
    results = []
    start_time = time.time()
    
    # Process claims concurrently
    tasks = []
    for claim_data in batch_claims:
        claim = ClaimData(**claim_data)
        tasks.append(workflow.process_claim(claim))
    
    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    print(f"Batch Processing Time: {total_time:.2f} seconds")
    print(f"Average Time per Claim: {total_time/len(batch_claims):.2f} seconds")
    
    # Analyze results
    status_counts = {"APPROVED": 0, "REJECTED": 0, "PARTIAL": 0, "ESCALATE": 0, "ERROR": 0}
    
    for i, result in enumerate(batch_results):
        if isinstance(result, Exception):
            status_counts["ERROR"] += 1
            print(f"❌ Claim {i+1}: ERROR - {result}")
        else:
            status = result.final_decision.status
            status_counts[status] += 1
            claim_id = batch_claims[i]["claim_id"]
            print(f"📄 {claim_id}: {status} - {result.final_decision.reason}")
    
    print(f"\n📊 BATCH SUMMARY:")
    for status, count in status_counts.items():
        if count > 0:
            emoji = {"APPROVED": "✅", "REJECTED": "❌", "PARTIAL": "⚠️", "ESCALATE": "🔴", "ERROR": "💥"}[status]
            print(f"{emoji} {status}: {count}")
    
    return batch_results


async def test_edge_cases(workflow: ClaimProcessingWorkflow):
    """Test edge cases and error conditions."""
    print(f"\n{'='*60}")
    print("EDGE CASE TESTING")
    print(f"{'='*60}")
    
    # Test case 1: Late submission (> 30 days)
    print("\n🧪 Test Case 1: Late Submission")
    late_claim = {
        "claim_id": "TEST-LATE-001",
        "incident_date": "2024-12-01",
        "report_date": "2025-01-15",  # 45 days later
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
        "driver_name": "Test Driver",
        "driver_license_status": "valid",
        "driver_listed_on_policy": True,
        "driver_excluded": False,
        "driver_under_influence": False,
        "driver_use_type": "personal",
        "vin": "TEST123456",
        "odometer_at_loss": 50000,
        "telematics_odometer": 50000,
        "damage_description": "collision damage",
        "damage_type": "collision",
        "repair_estimate": 5000,
        "actual_cash_value": 15000,
        "aftermarket_mods": False,
        "recall_active": False,
        "police_report_attached": True,
        "loss_location_flood_zone": "low",
        "cat_event_code": None,
        "rental_days_claimed": 5,
        "loss_of_use_daily_rate": 35,
        "at_fault_party": "insured",
        "insured_liability_percent": 100,
        "third_party_insurer": None,
        "injuries_reported": False,
        "primary_med_provider": None
    }
    
    await test_single_claim(workflow, late_claim)
    
    # Test case 2: Driver not listed on policy
    print("\n🧪 Test Case 2: Driver Not Listed")
    unlisted_driver_claim = late_claim.copy()
    unlisted_driver_claim.update({
        "claim_id": "TEST-UNLISTED-001",
        "incident_date": "2025-01-20",
        "report_date": "2025-01-22",
        "driver_listed_on_policy": False
    })
    
    await test_single_claim(workflow, unlisted_driver_claim)


async def main():
    """Main test function."""
    print("🚀 Starting Multi-Agent Auto Insurance Claim Processing System Test")
    print(f"Using OpenAI Model: {settings.openai_model}")
    
    # Check if API key is available
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file or environment variables")
        return
    
    # Initialize the workflow
    print("\n🔧 Initializing workflow...")
    try:
        workflow = ClaimProcessingWorkflow(
            openai_api_key=settings.openai_api_key,
            model_name=settings.openai_model
        )
        print("✅ Workflow initialized successfully")
        print(workflow.get_workflow_visualization())
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        return
    
    # Load sample data
    sample_data_path = Path("dataset/auto_claim_sample_inputs.json")
    if not sample_data_path.exists():
        print(f"❌ Sample data file not found: {sample_data_path}")
        return
    
    try:
        with open(sample_data_path, 'r') as f:
            sample_claims = json.load(f)
        print(f"📁 Loaded {len(sample_claims)} sample claims")
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return
    
    # Test single claim processing
    print("\n" + "="*80)
    print("SINGLE CLAIM PROCESSING TESTS")
    print("="*80)
    
    # Test first 3 claims individually
    for i in range(min(3, len(sample_claims))):
        await test_single_claim(workflow, sample_claims[i])
    
    # Test batch processing
    await test_batch_processing(workflow, sample_claims, batch_size=5)
    
    # Test edge cases
    await test_edge_cases(workflow)
    
    print(f"\n{'='*80}")
    print("🎉 ALL TESTS COMPLETED")
    print(f"{'='*80}")
    print("\nTo run the API server:")
    print("python main.py")
    print("\nThen visit http://localhost:8000/docs for the interactive API documentation")


if __name__ == "__main__":
    asyncio.run(main()) 
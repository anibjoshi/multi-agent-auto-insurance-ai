#!/usr/bin/env python3
"""
Quick Test for ReAct Multi-Agent System

Simple, fast testing for development iteration.
"""

import asyncio
import jsonlines
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow


async def quick_test(dataset_name: str = "consolidated", num_claims: int = 5):
    """Run a quick test with specified dataset."""
    print(f"🔍 Quick Test - {dataset_name} dataset ({num_claims} claims)")
    print("=" * 50)
    
    # Check API key
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found!")
        return
    
    # Set up paths
    datasets_dir = Path("benchmarks/datasets")
    inputs_file = datasets_dir / "inputs" / f"{dataset_name}_inputs.jsonl"
    expected_file = datasets_dir / "expected" / f"{dataset_name}_expected.jsonl"
    
    if not inputs_file.exists():
        print(f"❌ Dataset not found: {inputs_file}")
        return
    
    # Load test claims
    claims = []
    expected = []
    
    with jsonlines.open(inputs_file, 'r') as reader:
        for i, claim in enumerate(reader):
            if i >= num_claims:
                break
            claims.append(claim)
    
    with jsonlines.open(expected_file, 'r') as reader:
        for i, exp in enumerate(reader):
            if i >= num_claims:
                break
            expected.append(exp)
    
    # Initialize workflow
    workflow = ClaimProcessingWorkflow(
        openai_api_key=settings.openai_api_key,
        model_name=settings.openai_model
    )
    
    correct = 0
    
    for i, (claim_dict, exp_dict) in enumerate(zip(claims, expected), 1):
        claim_id = claim_dict['claim_id']
        expected_status = exp_dict['expected_status']
        
        print(f"\n📋 Claim {i}/{num_claims}: {claim_id}")
        print(f"   Expected: {expected_status}")
        
        try:
            # Convert dates
            claim_copy = claim_dict.copy()
            date_fields = ['incident_date', 'report_date', 'policy_start_date', 'policy_end_date']
            for field in date_fields:
                if claim_copy.get(field):
                    claim_copy[field] = datetime.strptime(claim_copy[field], '%Y-%m-%d').date()
            
            optional_date_fields = ['coverage_suspension_start', 'coverage_suspension_end']
            for field in optional_date_fields:
                if claim_copy.get(field):
                    claim_copy[field] = datetime.strptime(claim_copy[field], '%Y-%m-%d').date()
            
            claim_data = ClaimData(**claim_copy)
            
            # Process claim
            result = await workflow.process_claim(claim_data)
            actual_status = result.final_decision.status
            
            if actual_status == expected_status:
                correct += 1
                print(f"   ✅ Actual: {actual_status}")
            else:
                print(f"   ❌ Actual: {actual_status}")
            
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    # Summary
    total = len(claims)
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n🎯 Results: {correct}/{total} correct ({accuracy:.1f}%)")


if __name__ == "__main__":
    # Parse command line arguments
    dataset = "consolidated" 
    num_claims = 5
    
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
    if len(sys.argv) > 2:
        num_claims = int(sys.argv[2])
    
    asyncio.run(quick_test(dataset, num_claims)) 
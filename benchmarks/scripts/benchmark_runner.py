#!/usr/bin/env python3
"""
Simple Benchmark Runner for ReAct Multi-Agent System

Straightforward benchmarking without unnecessary complexity.
"""

import asyncio
import jsonlines
import time
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow


async def run_benchmark(dataset_name: str = "consolidated", max_claims: int = None):
    """Run benchmark on specified dataset."""
    print(f"🎯 Benchmark Runner - {dataset_name}")
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
        
    if not expected_file.exists():
        print(f"❌ Expected answers not found: {expected_file}")
        return
    
    # Load claims
    print(f"📂 Loading claims from {dataset_name}...")
    claims = []
    expected = []
    
    with jsonlines.open(inputs_file, 'r') as reader:
        for i, claim in enumerate(reader):
            if max_claims and i >= max_claims:
                break
            claims.append(claim)
    
    with jsonlines.open(expected_file, 'r') as reader:
        for i, exp in enumerate(reader):
            if max_claims and i >= max_claims:
                break
            expected.append(exp)
    
    total_claims = len(claims)
    print(f"📊 Processing {total_claims} claims...")
    
    # Initialize workflow
    workflow = ClaimProcessingWorkflow(
        openai_api_key=settings.openai_api_key,
        model_name=settings.openai_model
    )
    
    # Process claims
    correct = 0
    errors = 0
    start_time = time.time()
    
    for i, (claim_dict, exp_dict) in enumerate(zip(claims, expected), 1):
        claim_id = claim_dict['claim_id']
        expected_status = exp_dict['expected_status']
        
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
                
            # Progress update every 50 claims
            if i % 50 == 0:
                current_accuracy = (correct / i * 100)
                print(f"   Progress: {i}/{total_claims} ({current_accuracy:.1f}% accurate)")
            
        except Exception as e:
            print(f"   Error processing claim {claim_id}: {e}")
            errors += 1
    
    # Calculate results
    end_time = time.time()
    total_time = end_time - start_time
    accuracy = (correct / total_claims * 100) if total_claims > 0 else 0
    
    # Summary
    print(f"\n🎯 BENCHMARK RESULTS")
    print("=" * 30)
    print(f"Dataset: {dataset_name}")
    print(f"Total claims: {total_claims}")
    print(f"Correct: {correct}")
    print(f"Errors: {errors}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Avg per claim: {total_time/total_claims:.1f} seconds")
    
    # Save simple results
    results_dir = Path("benchmarks/results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = results_dir / f"results_{dataset_name}_{timestamp}.txt"
    
    with open(results_file, 'w') as f:
        f.write(f"Benchmark Results - {dataset_name}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total claims: {total_claims}\n")
        f.write(f"Correct: {correct}\n")
        f.write(f"Errors: {errors}\n")
        f.write(f"Accuracy: {accuracy:.1f}%\n")
        f.write(f"Total time: {total_time/60:.1f} minutes\n")
        f.write(f"Avg per claim: {total_time/total_claims:.1f} seconds\n")
    
    print(f"📄 Results saved to: {results_file}")


if __name__ == "__main__":
    # Parse command line arguments
    dataset = "consolidated"
    max_claims = None
    
    if len(sys.argv) > 1:
        dataset = sys.argv[1]
    if len(sys.argv) > 2:
        max_claims = int(sys.argv[2])
    
    asyncio.run(run_benchmark(dataset, max_claims)) 
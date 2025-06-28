#!/usr/bin/env python3
"""
Quick Accuracy Test for ReAct Multi-Agent System

A lightweight version for rapid testing with a small sample of claims.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from src.config import settings
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow


async def quick_test(num_claims: int = 5):
    """Run a quick accuracy test with a small number of claims."""
    print(f"🔍 Quick Accuracy Test - Processing {num_claims} claims")
    print("=" * 50)
    
    # Check API key
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found!")
        return
    
    # Load sample claims
    try:
        with open('dataset/auto_claim_sample_inputs_450.json', 'r') as f:
            all_claims = json.load(f)
        
        # Take a diverse sample
        test_claims = all_claims[:num_claims]
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Initialize workflow
    workflow = ClaimProcessingWorkflow(
        openai_api_key=settings.openai_api_key,
        model_name=settings.openai_model
    )
    
    correct = 0
    total = 0
    results = []
    
    for i, claim_dict in enumerate(test_claims, 1):
        claim_id = claim_dict['claim_id']
        expected_status = claim_dict['expected_status']
        
        print(f"\n📋 Processing Claim {i}/{num_claims}: {claim_id}")
        print(f"   Expected: {expected_status}")
        
        try:
            # Convert to ClaimData
            claim_copy = claim_dict.copy()
            
            # Convert dates
            date_fields = ['incident_date', 'report_date', 'policy_start_date', 'policy_end_date']
            for field in date_fields:
                if claim_copy[field]:
                    claim_copy[field] = datetime.strptime(claim_copy[field], '%Y-%m-%d').date()
            
            optional_date_fields = ['coverage_suspension_start', 'coverage_suspension_end']
            for field in optional_date_fields:
                if claim_copy[field]:
                    claim_copy[field] = datetime.strptime(claim_copy[field], '%Y-%m-%d').date()
            
            # Remove expected fields
            claim_copy.pop('expected_status', None)
            claim_copy.pop('expected_reason', None)
            
            claim_data = ClaimData(**claim_copy)
            
            # Process claim
            result = await workflow.process_claim(claim_data)
            actual_status = result.final_decision.status
            
            is_correct = actual_status == expected_status
            if is_correct:
                correct += 1
                print(f"   ✅ Actual: {actual_status} - CORRECT")
            else:
                print(f"   ❌ Actual: {actual_status} - INCORRECT")
            
            total += 1
            
            results.append({
                'claim_id': claim_id,
                'expected': expected_status,
                'actual': actual_status,
                'correct': is_correct,
                'reason': result.final_decision.explanation
            })
            
        except Exception as e:
            print(f"   💥 Error: {e}")
            total += 1
    
    # Summary
    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\n🎯 QUICK TEST RESULTS")
    print("=" * 30)
    print(f"Total Claims: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    # Show details
    print(f"\n📊 DETAILED RESULTS:")
    for result in results:
        status = "✅" if result['correct'] else "❌"
        print(f"{status} {result['claim_id']}: {result['expected']} → {result['actual']}")
    
    return accuracy


if __name__ == "__main__":
    asyncio.run(quick_test(5)) 
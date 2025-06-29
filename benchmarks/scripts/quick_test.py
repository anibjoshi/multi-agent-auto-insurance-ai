#!/usr/bin/env python3
"""
Quick Test for ReAct Multi-Agent System with Multi-LLM Support

Simple, fast testing for development iteration with provider selection.
"""

import asyncio
import jsonlines
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow
from src.llm_factory import get_supported_providers, get_provider_info


async def quick_test(dataset_name: str = "consolidated", num_claims: int = 5, provider: str = None):
    """Run a quick test with specified dataset and provider."""
    # Set provider if specified
    if provider:
        if provider not in get_supported_providers():
            print(f"❌ Error: Unsupported provider '{provider}'")
            print(f"   Supported providers: {', '.join(get_supported_providers())}")
            return
        settings.llm_provider = provider
    
    current_provider = settings.llm_provider
    provider_info = get_provider_info()
    provider_name = provider_info.get(current_provider, {}).get("name", current_provider.upper())
    
    print(f"🔍 Quick Test - {dataset_name} dataset ({num_claims} claims)")
    print(f"🤖 Provider: {provider_name}")
    print("=" * 50)
    
    # Check API key for selected provider
    api_key_check = {
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
        "google": settings.google_api_key,
        "groq": settings.groq_api_key
    }
    
    if not api_key_check.get(current_provider):
        env_key = provider_info.get(current_provider, {}).get("env_key", f"{current_provider.upper()}_API_KEY")
        print(f"❌ Error: {env_key} not found!")
        print(f"   Set your API key: export {env_key}=your_key_here")
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
    
    # Initialize workflow with selected provider
    try:
        workflow = ClaimProcessingWorkflow(provider=current_provider)
        print(f"✅ Initialized workflow with {provider_name}")
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        return
    
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
    print(f"🤖 Provider: {provider_name}")


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="Quick test for multi-agent system")
    parser.add_argument("--dataset", "-d", default="consolidated", 
                       help="Dataset name (default: consolidated)")
    parser.add_argument("--claims", "-c", type=int, default=5,
                       help="Number of claims to test (default: 5)")
    parser.add_argument("--provider", "-p", choices=get_supported_providers(),
                       help="LLM provider to use")
    parser.add_argument("--list-providers", action="store_true",
                       help="List available providers and exit")
    
    args = parser.parse_args()
    
    if args.list_providers:
        print("Available LLM Providers:")
        print("=" * 30)
        for provider_id, info in get_provider_info().items():
            print(f"• {provider_id}: {info['name']}")
            print(f"  Default model: {info['default_model']}")
            print(f"  Environment variable: {info['env_key']}")
            print()
        return
    
    asyncio.run(quick_test(args.dataset, args.claims, args.provider))


if __name__ == "__main__":
    main() 
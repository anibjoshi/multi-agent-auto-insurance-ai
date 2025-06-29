#!/usr/bin/env python3
"""
LLM Provider Setup and Testing Script

This script helps you test and configure different LLM providers
for the multi-agent auto insurance claim processing system.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.llm_factory import create_llm, get_supported_providers, get_provider_info
from src.models import ClaimData
from src.workflow import ClaimProcessingWorkflow
from datetime import date


def print_provider_info():
    """Print information about all supported providers."""
    print("🤖 Supported LLM Providers")
    print("=" * 50)
    
    for provider_id, info in get_provider_info().items():
        print(f"\n• {provider_id.upper()}: {info['name']}")
        print(f"  Default Model: {info['default_model']}")
        print(f"  Environment Variable: {info['env_key']}")
        print(f"  Available Models: {', '.join(info['models'])}")


def check_api_keys():
    """Check which API keys are configured."""
    print("\n🔑 API Key Status")
    print("=" * 30)
    
    api_keys = {
        "OpenAI": settings.openai_api_key,
        "Anthropic": settings.anthropic_api_key,
        "Google": settings.google_api_key,
        "Groq": settings.groq_api_key
    }
    
    for provider, key in api_keys.items():
        status = "✅ Configured" if key else "❌ Missing"
        print(f"{provider:<12}: {status}")
    
    configured_count = sum(1 for key in api_keys.values() if key)
    print(f"\nTotal configured: {configured_count}/4 providers")


async def test_provider(provider: str):
    """Test a specific provider with a simple claim."""
    print(f"\n🧪 Testing {provider.upper()} Provider")
    print("-" * 30)
    
    # Check if API key is available
    api_key_map = {
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
        "google": settings.google_api_key,
        "groq": settings.groq_api_key
    }
    
    if not api_key_map.get(provider):
        provider_info = get_provider_info()
        env_key = provider_info.get(provider, {}).get("env_key", f"{provider.upper()}_API_KEY")
        print(f"❌ {env_key} not configured")
        print(f"   Set your API key: export {env_key}=your_key_here")
        return False
    
    try:
        # Create a simple test claim
        test_claim = ClaimData(
            claim_id="TEST-001",
            incident_date=date(2025, 1, 15),
            report_date=date(2025, 1, 16),
            state="CA",
            policy_start_date=date(2024, 6, 1),
            policy_end_date=date(2025, 6, 1),
            per_claim_limit=25000,
            annual_aggregate_limit=50000,
            remaining_aggregate_limit=45000,
            endorsement_rental_days_allowed=15,
            endorsement_rental_daily_cap=40,
            endorsement_um_uim=True,
            endorsement_diminished_value=False,
            endorsement_rideshare_use=False,
            driver_name="Test Driver",
            driver_license_status="valid",
            driver_listed_on_policy=True,
            driver_excluded=False,
            driver_under_influence=False,
            driver_use_type="personal",
            vin="TEST123456789",
            odometer_at_loss=50000,
            telematics_odometer=50000,
            damage_description="minor collision damage",
            damage_type="collision",
            repair_estimate=5000,
            actual_cash_value=20000,
            aftermarket_mods=False,
            recall_active=False,
            police_report_attached=True,
            loss_location_flood_zone="low",
            rental_days_claimed=3,
            loss_of_use_daily_rate=35,
            at_fault_party="insured",
            insured_liability_percent=100,
            injuries_reported=False
        )
        
        # Initialize workflow with specific provider
        workflow = ClaimProcessingWorkflow(provider=provider)
        print(f"✅ Successfully initialized {provider.upper()} workflow")
        
        # Process test claim
        print("🔄 Processing test claim...")
        result = await workflow.process_claim(test_claim)
        
        # Display results
        print(f"✅ Test successful!")
        print(f"   Final Decision: {result.final_decision.status}")
        print(f"   Reason: {result.final_decision.reason}")
        print(f"   Agent Responses: {len(result.agent_responses)} agents")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


async def test_all_providers():
    """Test all configured providers."""
    print("\n🧪 Testing All Configured Providers")
    print("=" * 40)
    
    results = {}
    
    for provider in get_supported_providers():
        success = await test_provider(provider)
        results[provider] = success
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 25)
    
    for provider, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{provider.upper():<12}: {status}")


def create_env_template():
    """Create a .env template file with all provider configurations."""
    env_content = """# Multi-LLM Provider Configuration
# Choose your provider: openai, anthropic, google, groq
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic (Claude) Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google (Gemini) Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-1.5-pro

# Groq (Llama) Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Model Parameters
TEMPERATURE=0.1
MAX_TOKENS=1000

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    env_file = Path(".env.template")
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    print("   Copy this to .env and add your API keys")


async def main():
    """Main function with interactive menu."""
    print("🚀 Multi-LLM Provider Setup and Testing")
    print("=" * 45)
    
    while True:
        print("\nOptions:")
        print("1. Show provider information")
        print("2. Check API key status")
        print("3. Test specific provider")
        print("4. Test all providers")
        print("5. Create .env template")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print_provider_info()
        elif choice == "2":
            check_api_keys()
        elif choice == "3":
            print("\nAvailable providers:")
            for i, provider in enumerate(get_supported_providers(), 1):
                print(f"{i}. {provider}")
            
            try:
                provider_choice = int(input("Select provider (1-4): ")) - 1
                provider = get_supported_providers()[provider_choice]
                await test_provider(provider)
            except (ValueError, IndexError):
                print("❌ Invalid choice")
        elif choice == "4":
            await test_all_providers()
        elif choice == "5":
            create_env_template()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    asyncio.run(main()) 
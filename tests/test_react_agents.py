#!/usr/bin/env python3
"""
Test script for individual ReAct agents in the Multi-Agent Auto Insurance Claim Processing System.

This script tests each agent individually with sample claim data to verify their ReAct behavior.
"""

import asyncio
import pytest
from datetime import datetime, date
from pathlib import Path
from unittest.mock import Mock, patch

from src.models import ClaimData, AgentResponse
from src.tools import (
    set_current_claim_data,
    get_claim_basic_info,
    get_policy_information,
    get_driver_information,
    get_vehicle_information,
    get_coverage_details,
    get_documentation_info,
    get_liability_information,
    get_rental_information,
    get_catastrophe_information,
    check_total_loss_threshold,
    check_mileage_discrepancy,
    calculate_days_between_dates
)
from src.agents import (
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


@pytest.fixture
def sample_claim_data():
    """Create a sample claim for testing."""
    return ClaimData(
        claim_id="TEST-REACT-001",
        incident_date=date(2025, 1, 20),
        report_date=date(2025, 1, 22),
        state="TX",
        policy_start_date=date(2024, 6, 1),
        policy_end_date=date(2025, 6, 1),
        coverage_suspension_start=None,
        coverage_suspension_end=None,
        cancellation_reason=None,
        per_claim_limit=25000,
        annual_aggregate_limit=50000,
        remaining_aggregate_limit=48000,
        endorsement_rental_days_allowed=15,
        endorsement_rental_daily_cap=40,
        endorsement_um_uim=True,
        endorsement_diminished_value=False,
        endorsement_rideshare_use=False,
        driver_name="John Test",
        driver_license_status="valid",
        driver_listed_on_policy=True,
        driver_excluded=False,
        driver_under_influence=False,
        driver_use_type="personal",
        vin="TEST123456789",
        odometer_at_loss=45000,
        telematics_odometer=45000,
        damage_description="Test collision",
        damage_type="collision",
        repair_estimate=15000,
        actual_cash_value=25000,
        aftermarket_mods=False,
        recall_active=False,
        police_report_attached=True,
        loss_location_flood_zone="low",
        cat_event_code=None,
        rental_days_claimed=10,
        loss_of_use_daily_rate=35,
        at_fault_party="insured",
        insured_liability_percent=100,
        third_party_insurer=None,
        injuries_reported=False,
        primary_med_provider=None
    )


class TestReActTools:
    """Test the tools that ReAct agents use."""
    
    def test_set_and_get_claim_data(self, sample_claim_data):
        """Test setting and retrieving claim data through tools."""
        # Set the claim data
        set_current_claim_data(sample_claim_data)
        
        # Test basic info tool
        basic_info = get_claim_basic_info()
        assert sample_claim_data.claim_id in basic_info
        assert sample_claim_data.state in basic_info
        assert sample_claim_data.damage_type in basic_info
        
        # Test policy info tool
        policy_info = get_policy_information()
        assert str(sample_claim_data.policy_start_date) in policy_info
        assert str(sample_claim_data.per_claim_limit) in policy_info
        
        # Test driver info tool
        driver_info = get_driver_information()
        assert sample_claim_data.driver_name in driver_info
        assert sample_claim_data.driver_license_status in driver_info
        
        # Test vehicle info tool
        vehicle_info = get_vehicle_information()
        assert str(sample_claim_data.repair_estimate) in vehicle_info
        assert str(sample_claim_data.actual_cash_value) in vehicle_info
    
    def test_total_loss_threshold_tool(self, sample_claim_data):
        """Test the total loss threshold calculation tool."""
        set_current_claim_data(sample_claim_data)
        
        result = check_total_loss_threshold()
        
        # Should not be total loss (15000 < 80% of 25000)
        assert "is_total_loss" in result
        assert "false" in result.lower()  # Should be false for this test case
    
    def test_mileage_discrepancy_tool(self, sample_claim_data):
        """Test the mileage discrepancy detection tool."""
        set_current_claim_data(sample_claim_data)
        
        result = check_mileage_discrepancy()
        
        # Should not be suspicious (same mileage)
        assert "is_suspicious" in result
        assert "false" in result.lower()  # Should be false for this test case
    
    def test_tools_with_no_claim_data(self):
        """Test tools behavior when no claim data is set."""
        # Clear any existing claim data
        set_current_claim_data(None)
        
        # All tools should return appropriate error messages
        assert "No claim data available" in get_claim_basic_info()
        assert "No claim data available" in get_policy_information()
        assert "No claim data available" in get_driver_information()
        assert "No claim data available" in get_vehicle_information()


class TestReActAgents:
    """Test ReAct agents with mocked LLM responses."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM that returns valid JSON responses."""
        mock = Mock()
        
        # Mock a successful response
        async def mock_ainvoke(input_data):
            mock_response = Mock()
            mock_response.content = '''
I need to analyze this claim using my tools.

Let me first get the basic claim information.

I'll check the policy information to validate timing and limits.

Based on my analysis using the tools, I can make a decision:

{
  "agent": "PolicyValidator",
  "status": "APPROVED",
  "reason": "policy_valid",
  "explanation": "Policy is valid and covers the incident date"
}
'''
            
            return {"messages": [Mock(content=mock_response.content)]}
        
        mock.ainvoke = mock_ainvoke
        return mock
    
    @pytest.mark.asyncio
    async def test_policy_validator_react_agent(self, sample_claim_data, mock_llm):
        """Test PolicyValidator ReAct agent with tools."""
        # Set the claim data for tools to access
        set_current_claim_data(sample_claim_data)
        
        # Create agent with mocked LLM
        with patch('src.agents.policy_validator.create_react_agent') as mock_create:
            mock_create.return_value = mock_llm
            
            agent = PolicyValidatorAgent(llm=Mock())
            
            # Test that agent has the right tools
            assert len(agent.tools) == 3
            tool_names = [tool.__name__ for tool in agent.tools]
            assert "get_claim_basic_info" in tool_names
            assert "get_policy_information" in tool_names
            assert "calculate_days_between_dates" in tool_names
            
            # Process claim
            response = await agent.process_claim()
            
            # Verify response structure
            assert isinstance(response, AgentResponse)
            assert response.agent == "PolicyValidator"
            assert response.status in ["APPROVED", "REJECTED", "PARTIAL", "ESCALATE"]
            assert response.reason is not None
            assert response.explanation is not None
    
    @pytest.mark.asyncio
    async def test_vehicle_damage_evaluator_react_agent(self, sample_claim_data, mock_llm):
        """Test VehicleDamageEvaluator ReAct agent with tools."""
        set_current_claim_data(sample_claim_data)
        
        with patch('src.agents.vehicle_damage_evaluator.create_react_agent') as mock_create:
            mock_create.return_value = mock_llm
            
            agent = VehicleDamageEvaluatorAgent(llm=Mock())
            
            # Test that agent has the right tools
            assert len(agent.tools) == 3
            tool_names = [tool.__name__ for tool in agent.tools]
            assert "get_claim_basic_info" in tool_names
            assert "get_vehicle_information" in tool_names
            assert "check_total_loss_threshold" in tool_names
            
            # Process claim
            response = await agent.process_claim()
            
            # Verify response
            assert isinstance(response, AgentResponse)
            assert response.agent == "VehicleDamageEvaluator"
    
    @pytest.mark.asyncio
    async def test_fraud_detector_react_agent(self, sample_claim_data, mock_llm):
        """Test FraudDetector ReAct agent with tools."""
        set_current_claim_data(sample_claim_data)
        
        with patch('src.agents.fraud_detector.create_react_agent') as mock_create:
            mock_create.return_value = mock_llm
            
            agent = FraudDetectorAgent(llm=Mock())
            
            # Test that agent has the right tools
            assert len(agent.tools) == 6
            tool_names = [tool.__name__ for tool in agent.tools]
            assert "get_claim_basic_info" in tool_names
            assert "get_vehicle_information" in tool_names
            assert "check_mileage_discrepancy" in tool_names
            assert "calculate_days_between_dates" in tool_names
            
            # Process claim
            response = await agent.process_claim()
            
            # Verify response
            assert isinstance(response, AgentResponse)
            assert response.agent == "FraudDetector"
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, sample_claim_data):
        """Test ReAct agent error handling when tools fail."""
        set_current_claim_data(sample_claim_data)
        
        # Create an agent with a mock LLM that raises an exception
        mock_llm = Mock()
        mock_llm.ainvoke.side_effect = Exception("Test error")
        
        with patch('src.agents.policy_validator.create_react_agent') as mock_create:
            mock_create.return_value = mock_llm
            
            agent = PolicyValidatorAgent(llm=Mock())
            
            # Process should handle the error gracefully
            response = await agent.process_claim()
            
            # Should return escalation due to error
            assert response.status == "ESCALATE"
            assert "error" in response.reason.lower()
    
    def test_agent_system_prompts(self):
        """Test that ReAct agents have proper system prompts."""
        mock_llm = Mock()
        
        agents = [
            PolicyValidatorAgent(mock_llm),
            VehicleDamageEvaluatorAgent(mock_llm),
            FraudDetectorAgent(mock_llm)
        ]
        
        for agent in agents:
            prompt = agent.get_system_prompt()
            
            # Should contain ReAct-specific elements
            assert "ReAct" in prompt
            assert "tools" in prompt.lower()
            assert "reasoning" in prompt.lower()
            assert "process:" in prompt.lower()
            assert "json" in prompt.lower()
    
    def test_agent_tool_assignment(self):
        """Test that each agent has appropriate tools assigned."""
        mock_llm = Mock()
        
        # PolicyValidator should have policy-related tools
        policy_agent = PolicyValidatorAgent(mock_llm)
        policy_tools = [tool.__name__ for tool in policy_agent.get_tools()]
        assert "get_policy_information" in policy_tools
        assert "calculate_days_between_dates" in policy_tools
        
        # VehicleDamageEvaluator should have vehicle-related tools
        vehicle_agent = VehicleDamageEvaluatorAgent(mock_llm)
        vehicle_tools = [tool.__name__ for tool in vehicle_agent.get_tools()]
        assert "get_vehicle_information" in vehicle_tools
        assert "check_total_loss_threshold" in vehicle_tools
        
        # FraudDetector should have fraud-detection tools
        fraud_agent = FraudDetectorAgent(mock_llm)
        fraud_tools = [tool.__name__ for tool in fraud_agent.get_tools()]
        assert "check_mileage_discrepancy" in fraud_tools
        assert "get_vehicle_information" in fraud_tools


class TestReActIntegration:
    """Integration tests for the ReAct system."""
    
    @pytest.mark.asyncio
    async def test_tools_integration_with_real_data(self, sample_claim_data):
        """Test that tools work correctly with real claim data."""
        set_current_claim_data(sample_claim_data)
        
        # Test all tools return valid JSON or text
        tools = [
            get_claim_basic_info,
            get_policy_information,
            get_driver_information,
            get_vehicle_information,
            check_total_loss_threshold,
            check_mileage_discrepancy
        ]
        
        for tool in tools:
            result = tool()
            assert result is not None
            assert len(result) > 0
            assert "No claim data available" not in result
    
    def test_claim_data_isolation(self):
        """Test that claim data is properly isolated between different calls."""
        claim1 = ClaimData(
            claim_id="CLAIM-001",
            incident_date=date(2025, 1, 1),
            report_date=date(2025, 1, 2),
            state="CA",
            policy_start_date=date(2024, 1, 1),
            policy_end_date=date(2025, 1, 1),
            coverage_suspension_start=None,
            coverage_suspension_end=None,
            cancellation_reason=None,
            per_claim_limit=10000,
            annual_aggregate_limit=20000,
            remaining_aggregate_limit=20000,
            endorsement_rental_days_allowed=10,
            endorsement_rental_daily_cap=30,
            endorsement_um_uim=False,
            endorsement_diminished_value=False,
            endorsement_rideshare_use=False,
            driver_name="Driver 1",
            driver_license_status="valid",
            driver_listed_on_policy=True,
            driver_excluded=False,
            driver_under_influence=False,
            driver_use_type="personal",
            vin="VIN1",
            odometer_at_loss=10000,
            telematics_odometer=10000,
            damage_description="Damage 1",
            damage_type="collision",
            repair_estimate=5000,
            actual_cash_value=15000,
            aftermarket_mods=False,
            recall_active=False,
            police_report_attached=True,
            loss_location_flood_zone="low",
            cat_event_code=None,
            rental_days_claimed=5,
            loss_of_use_daily_rate=25,
            at_fault_party="insured",
            insured_liability_percent=100,
            third_party_insurer=None,
            injuries_reported=False,
            primary_med_provider=None
        )
        
        claim2 = ClaimData(
            claim_id="CLAIM-002",
            incident_date=date(2025, 1, 10),
            report_date=date(2025, 1, 12),
            state="NY",
            policy_start_date=date(2024, 1, 1),
            policy_end_date=date(2025, 1, 1),
            coverage_suspension_start=None,
            coverage_suspension_end=None,
            cancellation_reason=None,
            per_claim_limit=50000,
            annual_aggregate_limit=100000,
            remaining_aggregate_limit=100000,
            endorsement_rental_days_allowed=20,
            endorsement_rental_daily_cap=50,
            endorsement_um_uim=True,
            endorsement_diminished_value=True,
            endorsement_rideshare_use=True,
            driver_name="Driver 2",
            driver_license_status="valid",
            driver_listed_on_policy=True,
            driver_excluded=False,
            driver_under_influence=False,
            driver_use_type="personal",
            vin="VIN2",
            odometer_at_loss=20000,
            telematics_odometer=20000,
            damage_description="Damage 2",
            damage_type="flood",
            repair_estimate=30000,
            actual_cash_value=40000,
            aftermarket_mods=True,
            recall_active=True,
            police_report_attached=False,
            loss_location_flood_zone="high",
            cat_event_code="FLOOD_2025_001",
            rental_days_claimed=15,
            loss_of_use_daily_rate=45,
            at_fault_party="third_party",
            insured_liability_percent=0,
            third_party_insurer="OtherInsurer",
            injuries_reported=True,
            primary_med_provider="Test Hospital"
        )
        
        # Set first claim and verify
        set_current_claim_data(claim1)
        info1 = get_claim_basic_info()
        assert "CLAIM-001" in info1
        assert "CA" in info1
        
        # Set second claim and verify it replaced the first
        set_current_claim_data(claim2)
        info2 = get_claim_basic_info()
        assert "CLAIM-002" in info2
        assert "NY" in info2
        assert "CLAIM-001" not in info2  # Should not contain old claim data 
import asyncio
from typing import Dict, Any, TypedDict, Annotated, List
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
import time
from .models import ClaimData, AgentResponse, ClaimProcessingState
from .tools import set_current_claim_data
from .config import settings
from .llm_factory import create_llm
from .agents import (
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


class ClaimState(TypedDict):
    """LangGraph state for claim processing workflow."""
    claim_data: Dict[str, Any]
    agent_responses: List[Dict[str, Any]]
    final_decision: Dict[str, Any]
    processing_complete: bool
    current_step: str


class ClaimProcessingWorkflow:
    """Production-grade multi-agent claim processing workflow using LangGraph with multi-LLM support."""
    
    def __init__(self, provider: str = None, api_key: str = None, model_name: str = None):
        """
        Initialize workflow with specified LLM provider.
        
        Args:
            provider: LLM provider ("openai", "anthropic", "google", "groq"). Defaults to config.
            api_key: API key for the provider. Defaults to config.
            model_name: Model name to use. Defaults to config.
        """
        # Update settings if custom parameters provided
        if provider:
            settings.llm_provider = provider
        if api_key:
            if provider == "openai":
                settings.openai_api_key = api_key
            elif provider == "anthropic":
                settings.anthropic_api_key = api_key
            elif provider == "google":
                settings.google_api_key = api_key
            elif provider == "groq":
                settings.groq_api_key = api_key
        if model_name:
            if provider == "openai":
                settings.openai_model = model_name
            elif provider == "anthropic":
                settings.anthropic_model = model_name
            elif provider == "google":
                settings.google_model = model_name
            elif provider == "groq":
                settings.groq_model = model_name
        
        # Create LLM using factory
        self.llm = create_llm(settings)
        self.provider = settings.llm_provider
        
        # Initialize all agents with the LLM
        self.agents = {
            "policy_validator": PolicyValidatorAgent(self.llm),
            "document_validator": DocumentValidatorAgent(self.llm),
            "driver_verifier": DriverVerifierAgent(self.llm),
            "vehicle_damage_evaluator": VehicleDamageEvaluatorAgent(self.llm),
            "coverage_evaluator": CoverageEvaluatorAgent(self.llm),
            "catastrophe_checker": CatastropheCheckerAgent(self.llm),
            "liability_assessor": LiabilityAssessorAgent(self.llm),
            "rental_benefit_checker": RentalBenefitCheckerAgent(self.llm),
            "fraud_detector": FraudDetectorAgent(self.llm),
            "claim_decider": ClaimDeciderAgent(self.llm)
        }
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with proper nodes and edges."""
        workflow = StateGraph(ClaimState)
        
        # Add nodes for processing
        workflow.add_node("claim_decision", self._claim_decision_node)
        
        # Add a sequential processing node for all agents
        workflow.add_node("sequential_processing", self._parallel_processing_node)
        
        # Set entry point and define flow
        workflow.set_entry_point("sequential_processing")
        workflow.add_edge("sequential_processing", "claim_decision")
        workflow.add_edge("claim_decision", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _parallel_processing_node(self, state: ClaimState) -> ClaimState:
        """Process all ReAct agents sequentially to avoid rate limits."""
        claim_data = ClaimData(**state["claim_data"])
        
        # Set the claim data in the tools system for ReAct agents to access
        set_current_claim_data(claim_data)
        
        # Get all processing agents except ClaimDecider
        processing_agents = [
            ("policy_validator", self.agents["policy_validator"]),
            ("document_validator", self.agents["document_validator"]),
            ("driver_verifier", self.agents["driver_verifier"]),
            ("vehicle_damage_evaluator", self.agents["vehicle_damage_evaluator"]),
            ("coverage_evaluator", self.agents["coverage_evaluator"]),
            ("catastrophe_checker", self.agents["catastrophe_checker"]),
            ("liability_assessor", self.agents["liability_assessor"]),
            ("rental_benefit_checker", self.agents["rental_benefit_checker"]),
            ("fraud_detector", self.agents["fraud_detector"])
        ]
        
        agent_responses = []
        
        # Adjust rate limiting based on provider
        delay = self._get_rate_limit_delay()
        
        # Process agents sequentially with rate limiting
        for i, (agent_name, agent) in enumerate(processing_agents):
            try:
                response = await agent.process_claim()
                agent_responses.append(response.model_dump())
                
                # Add delay between agents to avoid rate limits (except for last agent)
                if i < len(processing_agents) - 1:
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                # Create error response for failed agents
                error_response = AgentResponse(
                    agent=agent_name.replace("_", " ").title(),
                    status="ESCALATE",
                    reason="agent_execution_error",
                    explanation=f"Agent execution failed: {str(e)}"
                )
                agent_responses.append(error_response.model_dump())
        
        return {
            **state,
            "agent_responses": agent_responses,
            "current_step": "sequential_processing"
        }
    
    def _get_rate_limit_delay(self) -> float:
        """Get appropriate delay based on LLM provider rate limits."""
        rate_limits = {
            "openai": 0.5,      # 500ms for OpenAI
            "anthropic": 0.3,   # 300ms for Claude
            "google": 0.2,      # 200ms for Gemini
            "groq": 0.1         # 100ms for Groq (fastest)
        }
        return rate_limits.get(self.provider, 0.5)
    
    async def _claim_decision_node(self, state: ClaimState) -> ClaimState:
        """Final claim decision node."""
        agent_responses = [AgentResponse(**resp) for resp in state["agent_responses"]]
        final_decision = await self.agents["claim_decider"].make_final_decision(agent_responses)
        
        return {
            **state,
            "final_decision": final_decision.model_dump(),
            "processing_complete": True,
            "current_step": "claim_decision"
        }
    
    async def process_claim(self, claim_data: ClaimData) -> ClaimProcessingState:
        """Process a claim through the entire LangGraph workflow."""
        initial_state = ClaimState(
            claim_data=claim_data.model_dump(),
            agent_responses=[],
            final_decision={},
            processing_complete=False,
            current_step="start"
        )
        
        # Provide required thread configuration for checkpointer
        config = {"configurable": {"thread_id": f"claim_{claim_data.claim_id}"}}
        
        # Execute the LangGraph workflow with proper configuration
        result = await self.workflow.ainvoke(initial_state, config=config)
        
        # Convert back to ClaimProcessingState
        return ClaimProcessingState(
            claim_data=claim_data,
            agent_responses=[AgentResponse(**resp) for resp in result["agent_responses"]],
            final_decision=AgentResponse(**result["final_decision"]) if result["final_decision"] else None,
            processing_complete=result["processing_complete"]
        )
    
    async def process_claim_with_config(self, claim_data: ClaimData, config: Dict[str, Any] = None) -> ClaimProcessingState:
        """Process a claim with optional LangGraph configuration."""
        if config is None:
            config = {"configurable": {"thread_id": f"claim_{claim_data.claim_id}"}}
        
        initial_state = ClaimState(
            claim_data=claim_data.model_dump(),
            agent_responses=[],
            final_decision={},
            processing_complete=False,
            current_step="start"
        )
        
        # Execute the workflow with config
        result = await self.workflow.ainvoke(initial_state, config=config)
        
        # Convert back to ClaimProcessingState
        return ClaimProcessingState(
            claim_data=claim_data,
            agent_responses=[AgentResponse(**resp) for resp in result["agent_responses"]],
            final_decision=AgentResponse(**result["final_decision"]) if result["final_decision"] else None,
            processing_complete=result["processing_complete"]
        )
    
    def get_workflow_visualization(self) -> str:
        """Get a text representation of the LangGraph ReAct workflow."""
        provider_info = {
            "openai": "OpenAI GPT",
            "anthropic": "Anthropic Claude", 
            "google": "Google Gemini",
            "groq": "Groq Llama"
        }
        current_provider = provider_info.get(self.provider, self.provider.upper())
        
        return f"""
LangGraph ReAct Multi-Agent Auto Insurance Claim Processing Workflow
Provider: {current_provider}

                        START
                          ↓
                PARALLEL ReAct PROCESSING
              ┌─────────────────────────┐
              │ PolicyValidator (ReAct)         │
              │ DocumentValidator (ReAct)       │
              │ DriverVerifier (ReAct)          │
              │ VehicleDamageEvaluator (ReAct)  │  ← All ReAct agents run in parallel
              │ CoverageEvaluator (ReAct)       │    using tools to access claim data
              │ CatastropheChecker (ReAct)      │    powered by {current_provider}
              │ LiabilityAssessor (ReAct)       │
              │ RentalBenefitChecker (ReAct)    │
              │ FraudDetector (ReAct)           │
              └─────────────────────────┘
                          ↓
                CLAIM DECISION (ReAct)
                          ↓
                         END

Multi-LLM Support:
• OpenAI: GPT-4, GPT-3.5-turbo
• Anthropic: Claude-3.5-Sonnet, Claude-3-Opus, Claude-3-Haiku  
• Google: Gemini-1.5-Pro, Gemini-1.5-Flash
• Groq: Llama-3.1-70B, Llama-3.1-8B, Mixtral-8x7B

ReAct Benefits:
• Reasoning and Acting agents with tool calling
• Claim data accessed through specialized tools
• Each agent uses domain-specific tool sets
• Provider-optimized rate limiting
• Advanced reasoning capabilities with step-by-step analysis
• Proper error handling and checkpointing
        """ 
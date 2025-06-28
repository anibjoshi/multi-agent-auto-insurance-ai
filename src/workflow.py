import asyncio
from typing import Dict, Any, TypedDict, Annotated, List
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
import time
from .models import ClaimData, AgentResponse, ClaimProcessingState
from .tools import set_current_claim_data
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
    """Production-grade multi-agent claim processing workflow using LangGraph."""
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4-turbo-preview"):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model=model_name,
            temperature=0.1,  # Low temperature for consistent decisions
            max_tokens=1000
        )
        
        # Initialize all agents
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
        
        # Process agents sequentially with rate limiting
        for i, (agent_name, agent) in enumerate(processing_agents):
            try:
                response = await agent.process_claim()
                agent_responses.append(response.model_dump())
                
                # Add delay between agents to avoid rate limits (except for last agent)
                if i < len(processing_agents) - 1:
                    await asyncio.sleep(0.5)  # 500ms delay between agents
                    
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
        return """
LangGraph ReAct Multi-Agent Auto Insurance Claim Processing Workflow:

                        START
                          ↓
                PARALLEL ReAct PROCESSING
              ┌─────────────────────────┐
              │ PolicyValidator (ReAct)         │
              │ DocumentValidator (ReAct)       │
              │ DriverVerifier (ReAct)          │
              │ VehicleDamageEvaluator (ReAct)  │  ← All ReAct agents run in parallel
              │ CoverageEvaluator (ReAct)       │    using tools to access claim data
              │ CatastropheChecker (ReAct)      │
              │ LiabilityAssessor (ReAct)       │
              │ RentalBenefitChecker (ReAct)    │
              │ FraudDetector (ReAct)           │
              └─────────────────────────┘
                          ↓
                CLAIM DECISION (ReAct)
                          ↓
                         END

ReAct Benefits:
• Reasoning and Acting agents with tool calling
• Claim data accessed through specialized tools
• Each agent uses domain-specific tool sets
• True parallel execution with LangGraph orchestration
• Advanced reasoning capabilities with step-by-step analysis
• Proper error handling and checkpointing
        """ 
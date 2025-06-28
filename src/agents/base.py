from abc import ABC, abstractmethod
from typing import List, Callable, Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from ..models import AgentResponse
from ..prompt_loader import load_agent_prompt
import json


class BaseReActAgent(ABC):
    """Base class for all ReAct claim processing agents."""
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.agent_name = self.__class__.__name__.replace("Agent", "")
        self.tools = self.get_tools()  # Tools are already decorated with @tool
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.get_system_prompt()
        )
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for this ReAct agent loaded from file."""
        try:
            return load_agent_prompt(self.agent_name)
        except FileNotFoundError:
            # Fallback to the implemented method if file doesn't exist
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Fallback prompt if file-based prompt is not available."""
        return f"""You are {self.agent_name}, a ReAct agent for auto insurance claim processing.
        
Use your available tools to gather information and make decisions.
Return your decision in JSON format:
{{
  "agent": "{self.agent_name}",
  "status": "APPROVED | REJECTED | PARTIAL | ESCALATE",
  "reason": "concise_slug_snake_case",
  "explanation": "1-2 sentence human-readable rationale"
}}"""
    
    @abstractmethod
    def get_tools(self) -> List[Callable]:
        """Return the list of tools this agent can use."""
        pass
    
    async def process_claim(self) -> AgentResponse:
        """Process a claim using ReAct pattern and return the agent's decision."""
        try:
            # Create the user message asking for claim analysis
            message = f"""Analyze the claim data using your available tools and make a decision.

You must:
1. Use the appropriate tools to gather relevant information
2. Apply your domain-specific rules and logic
3. Return a final decision in this EXACT JSON format:
{{
  "agent": "{self.agent_name}",
  "status": "APPROVED | REJECTED | PARTIAL | ESCALATE",
  "reason": "concise_slug_snake_case", 
  "explanation": "1-2 sentence human-readable rationale"
}}

Make sure to return only the JSON object, no other text."""

            # Invoke the ReAct agent
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": message}]
            })
            
            # Extract the final response from the agent
            last_message = result["messages"][-1].content
            
            # Try to parse JSON from the response
            try:
                # Look for JSON in the response
                json_start = last_message.find('{')
                json_end = last_message.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = last_message[json_start:json_end]
                    response_dict = json.loads(json_str)
                    return AgentResponse(**response_dict)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback if JSON parsing fails
                return AgentResponse(
                    agent=self.agent_name,
                    status="ESCALATE",
                    reason="agent_parsing_error",
                    explanation=f"Failed to parse agent response: {str(e)}"
                )
                
        except Exception as e:
            # Fallback for any other errors
            return AgentResponse(
                agent=self.agent_name,
                status="ESCALATE", 
                reason="agent_execution_error",
                explanation=f"Agent execution failed: {str(e)}"
            ) 
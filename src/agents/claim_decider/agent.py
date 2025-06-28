from typing import List, Callable
from ..base import BaseReActAgent
from ...models import AgentResponse
import json


def get_agent_responses() -> str:
    """Tool to get all agent responses for final decision making."""
    # This will be populated by the workflow when needed
    return "Agent responses will be provided by the workflow"


class ClaimDeciderAgent(BaseReActAgent):
    """ReAct agent that makes the final claim decision based on all agent responses."""
    
    def get_tools(self) -> List[Callable]:
        """Return tools specific to claim decision making."""
        return [get_agent_responses]
    
# get_system_prompt is now inherited from BaseReActAgent and loads from file
    
    async def make_final_decision(self, agent_responses: list[AgentResponse]) -> AgentResponse:
        """Make final decision based on all agent responses using ReAct reasoning."""
        # Store agent responses in a format the tool can access
        responses_json = json.dumps([resp.model_dump() for resp in agent_responses], indent=2)
        
        # Override the tool to provide actual agent responses
        def get_current_agent_responses() -> str:
            """Get the current agent responses for final decision making."""
            return f"Current agent responses:\n{responses_json}"
        
        # Temporarily replace the tool
        original_tools = self.tools
        self.tools = [get_current_agent_responses]
        
        # Recreate the agent with updated tools
        from langgraph.prebuilt import create_react_agent
        temp_agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.get_system_prompt()
        )
        
        try:
            message = """Analyze all agent responses and make the final claim decision.

Use your available tools to get the agent responses, then apply the decision hierarchy rules to determine the final outcome.

Return your decision in this EXACT JSON format:
{
  "agent": "ClaimDecider",
  "status": "APPROVED | REJECTED | PARTIAL | ESCALATE",
  "reason": "concise_slug_snake_case",
  "explanation": "concise summary mentioning contributing agents and their reasons"
}"""

            result = await temp_agent.ainvoke({
                "messages": [{"role": "user", "content": message}]
            })
            
            # Extract and parse the response
            last_message = result["messages"][-1].content
            json_start = last_message.find('{')
            json_end = last_message.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = last_message[json_start:json_end]
                response_dict = json.loads(json_str)
                return AgentResponse(**response_dict)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            # Fallback decision logic
            statuses = [resp.status for resp in agent_responses]
            if "REJECTED" in statuses:
                rejected_resp = next(resp for resp in agent_responses if resp.status == "REJECTED")
                return AgentResponse(
                    agent="ClaimDecider",
                    status="REJECTED",
                    reason=rejected_resp.reason,
                    explanation=f"Claim rejected by {rejected_resp.agent}: {rejected_resp.explanation}"
                )
            elif "ESCALATE" in statuses:
                escalate_resp = next(resp for resp in agent_responses if resp.status == "ESCALATE")
                return AgentResponse(
                    agent="ClaimDecider",
                    status="ESCALATE",
                    reason=escalate_resp.reason,
                    explanation=f"Claim escalated by {escalate_resp.agent}: {escalate_resp.explanation}"
                )
            elif "PARTIAL" in statuses:
                partial_resp = next(resp for resp in agent_responses if resp.status == "PARTIAL")
                return AgentResponse(
                    agent="ClaimDecider",
                    status="PARTIAL",
                    reason=partial_resp.reason,
                    explanation=f"Partial approval due to {partial_resp.agent}: {partial_resp.explanation}"
                )
            else:
                return AgentResponse(
                    agent="ClaimDecider",
                    status="APPROVED",
                    reason="all_agents_approved",
                    explanation="All agents approved the claim"
                )
        finally:
            # Restore original tools
            self.tools = original_tools 
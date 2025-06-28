"""
Simple prompt loader for ReAct agents.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """Simple utility for loading ReAct agent prompts from files."""
    
    def __init__(self):
        """Initialize the prompt loader."""
        # Prompts are co-located with agent code in organized directories
        current_file = Path(__file__)
        self.prompts_dir = current_file.parent / "agents"
        self._prompt_cache: Dict[str, str] = {}
    
    def load_prompt(self, agent_name: str) -> str:
        """Load a prompt for the specified agent."""
        # Check cache first
        if agent_name in self._prompt_cache:
            return self._prompt_cache[agent_name]
        
        # Convert agent name to directory name (e.g., PolicyValidator -> policy_validator)
        dir_name = self._agent_name_to_dirname(agent_name)
        prompt_file = self.prompts_dir / dir_name / "prompt.md"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
            
            # Cache the prompt
            self._prompt_cache[agent_name] = prompt_text
            return prompt_text
            
        except Exception as e:
            logger.error(f"Error loading prompt for {agent_name}: {e}")
            raise
    
    def list_available_prompts(self) -> list[str]:
        """List all available prompt files."""
        if not self.prompts_dir.exists():
            return []
        
        prompts = []
        # Look for prompt.md files in subdirectories
        for agent_dir in self.prompts_dir.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('.') and not agent_dir.name.startswith('__'):
                prompt_file = agent_dir / "prompt.md"
                if prompt_file.exists():
                    agent_name = self._dirname_to_agent_name(agent_dir.name)
            prompts.append(agent_name)
        
        return sorted(prompts)
    
    def get_prompts_directory(self) -> Path:
        """Get the path to the prompts directory."""
        return self.prompts_dir
    
    def _agent_name_to_dirname(self, agent_name: str) -> str:
        """Convert agent name to directory name (PolicyValidator -> policy_validator)."""
        # Remove 'Agent' suffix if present
        clean_name = agent_name.replace('Agent', '')
        
        # Convert CamelCase to snake_case
        import re
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', clean_name).lower()
        
        return snake_case
    
    def _dirname_to_agent_name(self, dirname: str) -> str:
        """Convert directory name to agent name (policy_validator -> PolicyValidator)."""
        # Convert snake_case to CamelCase
        words = dirname.split('_')
        agent_name = ''.join(word.capitalize() for word in words)
        
        return agent_name


def load_agent_prompt(agent_name: str) -> str:
    """Convenience function to load a prompt for an agent."""
    loader = PromptLoader()
    return loader.load_prompt(agent_name) 
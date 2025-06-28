#!/usr/bin/env python3
"""
Simple Prompt Manager for ReAct Agents
"""

import argparse
from pathlib import Path
from src.prompt_loader import PromptLoader


def list_prompts():
    """List all available prompts."""
    loader = PromptLoader()
    prompts = loader.list_available_prompts()
    
    print(f"📁 Prompts Directory: {loader.get_prompts_directory()}")
    print(f"📋 Available Prompts ({len(prompts)}):")
    
    for prompt_name in sorted(prompts):
        try:
            prompt_text = loader.load_prompt(prompt_name)
            lines = len(prompt_text.split('\n'))
            chars = len(prompt_text)
            print(f"  {prompt_name:<20} ({chars:,} chars, {lines} lines)")
        except Exception as e:
            print(f"  {prompt_name:<20} (Error: {e})")


def show_prompt(agent_name: str):
    """Show the content of a specific prompt."""
    loader = PromptLoader()
    
    try:
        prompt_text = loader.load_prompt(agent_name)
        print(f"Prompt for {agent_name}:")
        print("=" * 60)
        print(prompt_text)
        print("=" * 60)
        print(f"Stats: {len(prompt_text):,} characters, {len(prompt_text.split())} words")
    except FileNotFoundError:
        print(f"❌ Prompt not found for agent: {agent_name}")
        print(f"Available agents: {loader.list_available_prompts()}")
    except Exception as e:
        print(f"❌ Error loading prompt: {e}")


def validate_prompts():
    """Check that all prompts have required sections."""
    loader = PromptLoader()
    prompts = loader.list_available_prompts()
    
    print(f"Validating {len(prompts)} prompts...")
    
    required_sections = ["ReAct", "Role", "Tools", "Rules", "Output Format"]
    
    for agent_name in sorted(prompts):
        try:
            prompt_text = loader.load_prompt(agent_name)
            
            missing = []
            for section in required_sections:
                if section not in prompt_text:
                    missing.append(section)
            
            if missing:
                print(f"❌ {agent_name}: Missing {missing}")
            else:
                print(f"✅ {agent_name}: Valid")
                
        except Exception as e:
            print(f"❌ {agent_name}: Error - {e}")


def main():
    parser = argparse.ArgumentParser(description="Simple ReAct Prompt Manager")
    parser.add_argument("command", choices=["list", "show", "validate"],
                       help="Command to execute")
    parser.add_argument("--agent", "-a", help="Agent name for show command")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_prompts()
    
    elif args.command == "show":
        if not args.agent:
            print("❌ --agent required for show command")
            return
        show_prompt(args.agent)
    
    elif args.command == "validate":
        validate_prompts()


if __name__ == "__main__":
    main() 
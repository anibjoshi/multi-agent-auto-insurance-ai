"""
LLM Factory for Multi-Provider Support

Supports OpenAI, Anthropic (Claude), Google (Gemini), and Groq (Llama) models.
"""

from typing import Union
from langchain_core.language_models import BaseChatModel
from .config import Settings


def create_llm(settings: Settings) -> BaseChatModel:
    """
    Factory function to create LLM instances based on provider configuration.
    
    Args:
        settings: Application settings containing LLM configuration
        
    Returns:
        BaseChatModel: Initialized LLM instance
        
    Raises:
        ValueError: If provider is not supported or API key is missing
        ImportError: If required provider package is not installed
    """
    provider = settings.llm_provider.lower()
    
    if provider == "openai":
        return _create_openai_llm(settings)
    elif provider == "anthropic":
        return _create_anthropic_llm(settings)
    elif provider == "google":
        return _create_google_llm(settings)
    elif provider == "groq":
        return _create_groq_llm(settings)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def _create_openai_llm(settings: Settings) -> BaseChatModel:
    """Create OpenAI ChatGPT instance."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError("langchain-openai is required for OpenAI models. Install with: pip install langchain-openai")
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
    
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )


def _create_anthropic_llm(settings: Settings) -> BaseChatModel:
    """Create Anthropic Claude instance."""
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:
        raise ImportError("langchain-anthropic is required for Anthropic models. Install with: pip install langchain-anthropic")
    
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
    
    return ChatAnthropic(
        api_key=settings.anthropic_api_key,
        model=settings.anthropic_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )


def _create_google_llm(settings: Settings) -> BaseChatModel:
    """Create Google Gemini instance."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        raise ImportError("langchain-google-genai is required for Google models. Install with: pip install langchain-google-genai")
    
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required for Google provider")
    
    return ChatGoogleGenerativeAI(
        google_api_key=settings.google_api_key,
        model=settings.google_model,
        temperature=settings.temperature,
        max_output_tokens=settings.max_tokens
    )


def _create_groq_llm(settings: Settings) -> BaseChatModel:
    """Create Groq Llama instance."""
    try:
        from langchain_groq import ChatGroq
    except ImportError:
        raise ImportError("langchain-groq is required for Groq models. Install with: pip install langchain-groq")
    
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is required for Groq provider")
    
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens
    )


def get_supported_providers() -> list[str]:
    """Return list of supported LLM providers."""
    return ["openai", "anthropic", "google", "groq"]


def get_provider_info() -> dict[str, dict[str, str]]:
    """Return information about supported providers and their models."""
    return {
        "openai": {
            "name": "OpenAI",
            "default_model": "gpt-4-turbo-preview",
            "models": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            "env_key": "OPENAI_API_KEY"
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "default_model": "claude-3-5-sonnet-20241022",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "env_key": "ANTHROPIC_API_KEY"
        },
        "google": {
            "name": "Google Gemini",
            "default_model": "gemini-1.5-pro",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
            "env_key": "GOOGLE_API_KEY"
        },
        "groq": {
            "name": "Groq (Llama)",
            "default_model": "llama-3.1-70b-versatile",
            "models": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "env_key": "GROQ_API_KEY"
        }
    } 
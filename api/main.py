"""
FastAPI server for the multi-agent auto insurance claim processing system
with multi-LLM provider support.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.models import ClaimData, ClaimProcessingState
from src.workflow import ClaimProcessingWorkflow
from src.llm_factory import get_supported_providers, get_provider_info


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent system for auto insurance claim processing with multi-LLM support"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow instance
workflow = None


@app.on_event("startup")
async def startup_event():
    """Initialize the workflow on startup."""
    global workflow
    try:
        workflow = ClaimProcessingWorkflow()
        print(f"🚀 Multi-Agent System initialized with {workflow.provider.upper()} provider")
        print(f"📋 Workflow visualization:\n{workflow.get_workflow_visualization()}")
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "Multi-Agent Auto Insurance Claim Processing API",
        "version": settings.app_version,
        "current_provider": workflow.provider if workflow else "not_initialized",
        "supported_providers": get_supported_providers(),
        "status": "ready" if workflow else "initializing"
    }


@app.get("/providers")
async def get_providers():
    """Get information about supported LLM providers."""
    return {
        "supported_providers": get_supported_providers(),
        "provider_info": get_provider_info(),
        "current_provider": workflow.provider if workflow else None
    }


@app.post("/process-claim")
async def process_claim(
    claim_data: ClaimData,
    provider: Optional[str] = None
) -> ClaimProcessingState:
    """
    Process an insurance claim through the multi-agent system.
    
    Args:
        claim_data: The claim information to process
        provider: Optional LLM provider override ("openai", "anthropic", "google", "groq")
    
    Returns:
        ClaimProcessingState: The final processing result
    """
    if not workflow:
        raise HTTPException(status_code=503, detail="Workflow not initialized")
    
    try:
        # Use different workflow if provider is specified
        if provider and provider != workflow.provider:
            if provider not in get_supported_providers():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported provider: {provider}. Supported: {get_supported_providers()}"
                )
            
            # Create temporary workflow with specified provider
            temp_workflow = ClaimProcessingWorkflow(provider=provider)
            result = await temp_workflow.process_claim(claim_data)
        else:
            # Use default workflow
            result = await workflow.process_claim(claim_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")


@app.get("/workflow-visualization")
async def get_workflow_visualization():
    """Get a visualization of the current workflow."""
    if not workflow:
        raise HTTPException(status_code=503, detail="Workflow not initialized")
    
    return {
        "provider": workflow.provider,
        "visualization": workflow.get_workflow_visualization()
    }


@app.post("/switch-provider")
async def switch_provider(provider: str):
    """
    Switch the default LLM provider.
    
    Args:
        provider: New provider to use ("openai", "anthropic", "google", "groq")
    """
    global workflow
    
    if provider not in get_supported_providers():
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider: {provider}. Supported: {get_supported_providers()}"
        )
    
    try:
        # Create new workflow with specified provider
        workflow = ClaimProcessingWorkflow(provider=provider)
        return {
            "message": f"Successfully switched to {provider} provider",
            "current_provider": workflow.provider,
            "status": "ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching provider: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workflow_ready": workflow is not None,
        "provider": workflow.provider if workflow else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port) 
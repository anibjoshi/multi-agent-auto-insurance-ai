import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
import json

from src.config import settings
from src.models import ClaimData, AgentResponse, ClaimProcessingState
from src.workflow import ClaimProcessingWorkflow

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-grade multi-agent system for auto insurance claim processing using LangGraph",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global workflow instance
workflow: ClaimProcessingWorkflow = None


class ProcessClaimRequest(BaseModel):
    """Request model for claim processing."""
    claim_data: ClaimData
    include_agent_details: bool = True


class ProcessClaimResponse(BaseModel):
    """Response model for claim processing."""
    claim_id: str
    final_decision: AgentResponse
    agent_responses: List[AgentResponse] = None
    processing_time_seconds: float
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    workflow_initialized: bool


@app.on_event("startup")
async def startup_event():
    """Initialize the workflow on startup."""
    global workflow
    
    if not settings.openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise RuntimeError("OpenAI API key is required")
    
    try:
        workflow = ClaimProcessingWorkflow(
            openai_api_key=settings.openai_api_key,
            model_name=settings.openai_model
        )
        logger.info("Multi-agent workflow initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize workflow: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app_version,
        workflow_initialized=workflow is not None
    )


@app.get("/workflow/visualization")
async def get_workflow_visualization():
    """Get a visualization of the workflow."""
    if not workflow:
        raise HTTPException(status_code=503, detail="Workflow not initialized")
    
    return {
        "visualization": workflow.get_workflow_visualization(),
        "agents": list(workflow.agents.keys()),
        "description": "Multi-agent auto insurance claim processing workflow"
    }


@app.post("/claims/process", response_model=ProcessClaimResponse)
async def process_claim(request: ProcessClaimRequest):
    """
    Process an auto insurance claim through the multi-agent system.
    
    This endpoint processes a claim through all specialized agents and returns
    the final decision along with detailed reasoning.
    """
    if not workflow:
        raise HTTPException(status_code=503, detail="Workflow not initialized")
    
    start_time = datetime.now()
    
    try:
        # Process the claim through the workflow
        result = await workflow.process_claim(request.claim_data)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ProcessClaimResponse(
            claim_id=request.claim_data.claim_id,
            final_decision=result.final_decision,
            agent_responses=result.agent_responses if request.include_agent_details else None,
            processing_time_seconds=processing_time,
            timestamp=datetime.now()
        )
        
    except ValidationError as e:
        logger.error(f"Validation error processing claim {request.claim_data.claim_id}: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")
    except Exception as e:
        logger.error(f"Error processing claim {request.claim_data.claim_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/claims/batch-process")
async def batch_process_claims(
    claims: List[ClaimData],
    background_tasks: BackgroundTasks,
    include_agent_details: bool = True
):
    """
    Process multiple claims in batch (asynchronously).
    
    Returns immediately with job ID, actual processing happens in background.
    """
    if not workflow:
        raise HTTPException(status_code=503, detail="Workflow not initialized")
    
    if len(claims) > 100:  # Limit batch size
        raise HTTPException(status_code=422, detail="Batch size cannot exceed 100 claims")
    
    job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(claims)}"
    
    # Add background task
    background_tasks.add_task(
        process_claims_batch,
        claims,
        job_id,
        include_agent_details
    )
    
    return {
        "job_id": job_id,
        "claims_count": len(claims),
        "status": "processing",
        "message": "Batch processing started. Check job status for results."
    }


async def process_claims_batch(claims: List[ClaimData], job_id: str, include_agent_details: bool):
    """Background task to process claims in batch."""
    results = []
    
    for claim in claims:
        try:
            start_time = datetime.now()
            result = await workflow.process_claim(claim)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            results.append({
                "claim_id": claim.claim_id,
                "final_decision": result.final_decision.model_dump(),
                "agent_responses": [r.model_dump() for r in result.agent_responses] if include_agent_details else None,
                "processing_time_seconds": processing_time,
                "status": "completed"
            })
        except Exception as e:
            logger.error(f"Error processing claim {claim.claim_id} in batch {job_id}: {e}")
            results.append({
                "claim_id": claim.claim_id,
                "status": "failed",
                "error": str(e)
            })
    
    # In a production system, you would store these results in a database
    # For now, just log the completion
    logger.info(f"Batch {job_id} completed. Processed {len(claims)} claims.")


@app.post("/claims/validate")
async def validate_claim_data(claim_data: ClaimData):
    """
    Validate claim data structure without processing.
    """
    try:
        # If we reach here, Pydantic validation passed
        return {
            "valid": True,
            "claim_id": claim_data.claim_id,
            "message": "Claim data is valid and ready for processing"
        }
    except ValidationError as e:
        return {
            "valid": False,
            "errors": e.errors(),
            "message": "Claim data validation failed"
        }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Production-grade multi-agent system for auto insurance claim processing",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "process_claim": "/claims/process",
            "batch_process": "/claims/batch-process",
            "validate_claim": "/claims/validate",
            "workflow_visualization": "/workflow/visualization"
        },
        "usage": "Send claim data to /claims/process to get approval/rejection decision"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    ) 
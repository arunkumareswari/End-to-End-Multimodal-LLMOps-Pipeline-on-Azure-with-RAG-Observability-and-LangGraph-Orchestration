import uuid     # Generate unique session IDS
import logging 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize telemetry
from backend.src.api.telemetry import setup_telemetry
setup_telemetry()

# Import workflow graph
from backend.src.graph.workflow import app as compliance_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO 
)
logger = logging.getLogger("api-server")

# Initialize FastAPI app
app = FastAPI(
    # Metadata for auto-generated API documentation (Swagger UI)
    title = "ComplianceGuard AI API",
    description="API for auditing video content against brand compliance rules.",
    version="1.0.0"
)

# Define Data Models (PYDANTIC)

class AuditRequest(BaseModel):
    """ 
    Define the expected structure of incoming API requests.

    Pydantic validates that:
    - The request contains a 'video_url' field
    - The value is a string (not int, list, etc.)
    """
    video_url: str

# Nested Model
class ComplianceIssue(BaseModel):
    category: str
    severity: str
    description: str

# Response Model
class AuditResponse(BaseModel):
    session_id: str
    video_id: str
    status: str
    final_report: str
    compliance_results: List[ComplianceIssue]

# Define main Endpoint
@app.post("/audit", response_model=AuditResponse)
async def audit_video(request: AuditRequest):
    """
    Main API endpoint that triggers the compliance audit workflow.
    """
    # Generate Session ID
    session_id = str(uuid.uuid4())
    video_id_short = f"vid{session_id[:8]}"

    # Log Incoming Request
    logger.info(f"Received Audit Request: {request.video_url} (Session: {session_id})")

    # Prepare Graph input
    initial_inputs = {
        "video_url": request.video_url,
        "video_id": video_id_short,
        "compliance_results": [],
        "errors": []
    }

    try:
        # Invoke LangGraph Workflow
        final_state = compliance_graph.invoke(initial_inputs)

        return AuditResponse(
            session_id=session_id,
            video_id=final_state.get("video_id"),

            status=final_state.get("final_status", "UNKNOWN"),
            final_report = final_state.get("final_report", "No report generated."),
            compliance_results = final_state.get("compliance_results", [])   
        )
    
    except Exception as e:
        logger.error(f"Audit Failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Workflow Execution Failed: {str(e)}"
        )

@app.get("/health")

def health_check():
    return {
        "status": "healthy", 
        "service": "ComplianceGuard AI"
    }
import operator
from typing import Annotated, List, Dict, Optional, Any, TypedDict 

# Define the Schema for a single compliance result
# Error report
class ComplianceIssue(TypedDict):
    category: str
    description: str         # Specific detail of the violation
    severity: str            # "CRITICAL | WARNING"
    timestamp: Optional[str] 

# Define the Global graph state
class VideoAuditState(TypedDict):
    """
    Defines the data Schema for the langGraph execution context.
    Main container: holds all the information about the audit 
    right from initial URL to the final report
    """

    # Input parameters 
    video_url: str
    video_id: str

    # Ingestion and Extraction Data

    local_file_path: Optional[str]
    video_metadata: Dict[str, Any]   # e.g, {"duration": 12, "resolution": 720p} 
    transcript: Optional[str]        # Fully extracted speech to text
    ocr_text: List[str]

    # Analysis Output
    # stores the list of all the violations found by AI
    compliance_results: Annotated[List[ComplianceIssue], operator.add]

    # Final Deliverables
    final_status: str               # "PASS | FAIL"
    final_report: str               # Markdown summary for the frontend

    # System Observability
    errors: Annotated[List[str], operator.add]  # Examples: API timeout, system level errors
"""
Main entry point for the Compliance QA Pipeline.
"""

import uuid     # For generating unique IDs (like session tracking numbers)
import json 
import logging
from pprint import pprint  # Pretty-prints data structures

from dotenv import load_dotenv
load_dotenv(override=True)  #override=True means .env values take priority over system variables

# Import the main workflow graph
from backend.src.graph.workflow import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # Format: timestamp - logger_name -severity - message
)

logger = logging.getLogger("Compliance QA")

def run_cli_simulation():
    """
    Simulates a Video Compliance Audit request.

    This function orchestrates the entire audit process:
    - Creates a unique session ID
    - Prepares the video URL and metadata
    - Runs it through the AI workflow
    - Displays the compliance results
    """

    # GENERATE SESSION ID
    session_id = str(uuid.uuid4()) # Create a unique identifier for this audit session (uuid4() generates random UUID)
    logger.info(f"Starting Audit Session: {session_id}")

    # DEFINE INITIAL STATE
    ## This dictionary contains all the input data for the workflow
    initial_inputs = {
        # The YouTube video to audit
        "video_url": "https://youtu.be/dT7S75eYhcQ",

        # Shortened video ID for easier tracking (first 8 chars of session ID)
        "video_id": f"vid{session_id[:8]}",

        # Empty list that will store compliance violations found
        # Will be populated by the Auditor node
        "compliance_results": [],

        # Empty list for any errors during processing
        # Example: ["Download failed", "Transcript unavailable"]
        "errors": []
    }

    # DISPLAY SECTION: INPUT SUMMARY
    print("\n--- 1.Input Payload: INITIALIZING WORKFLOW ---")
    # json.dumps() converts python dict to formatted JSON string 
    
    print(f"I {json.dumps(initial_inputs, indent=2)}") # indent=2 makes it readable with 2 space indentation

    # EXECUTE GRAPH
    try:
        # It passes through: START -> Indexer -> Auditor -> END
        # Return the final state with all results
        final_state = app.invoke(initial_inputs)

        # DISPLAY SECTION: EXECUTION COMPLETE
        print("\n--- 2. WORKFLOW EXECUTION COMPLETE ---")

        # OUTPUT results
        print("\n=== COMPLIANCE AUDIT REPORT ===")

        # Displays the video ID that was audited
        print(f"Video ID:   {final_state.get('video_id')}")

        # Shows PASS or FAIL status
        print(f"Status:    {final_state.get('final_status')}")

        # VIOLATIONS DETECTED
        print("\n[ VIOLATIONS DETECTED ]")

        # Extract the list of compliance violations
        results = final_state.get('compliance_results', [])

        if results:
            # Loop through each violation and display it
            for issue in results:
                # Each issue is a dict with: severity, category, description
                # Example output: "-[CRITICAL] Misleading Claims: Absolute guarantee detected"
                print(f"- [{issue.get('severity')}] {issue.get('category')}: {issue.get('description')}")
        else:
            # No violations found (clean video)
            print("No violations found.")

        # SUMMARY SECTION
        print("\n[ FINAL SUMMARY ]")
        # Displays the AI-generated natural language summary
        print(final_state.get('final_report'))

    except Exception as e:
        # If anything breaks, log the error
        logger.error(f"Workflow Execution Failed: {str(e)}")
        raise e        

if __name__ == "__main__":
    run_cli_simulation()
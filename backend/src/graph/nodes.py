import json
import os
import logging
import re 
from typing import Dict, Any, List

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

# Import the state schema
from backend.src.graph.state import VideoAuditState, ComplianceIssue

# Import the Service
from backend.src.services.video_indexer import VideoIndexerService

# configure Logger
logger = logging.getLogger("Compliance-QA")
logging.basicConfig(leverl = logging.INFO)

# --- NODE 1: THE INDEXER ---
def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Download the YouTube video, uploads to Azure VI, and extracts insights.
    """

    video_url = state.get("video_url")
    video_id = state.get("video_id", "vid_demo")

    logger.info(f"---- [Node: Indexer] Processing: {video_url} ----")

    local_filename = "temp_audit_video.mp4"

    try:
        vi_service = VideoIndexerService()

        # Download
        if "youtupe.com" in video_url or "youtupe.be" in video_url:
            local_path = vi_service.download_youtupe_video(video_url, output_path = local_filename)
        else:
            raise Exception("Please provide a valid YouTupe URL")

        # Upload
        azure_video_id = vi_service.upload_video(local_path, video_name = video_id_input)
        logger.info(f"Upload Success. Azure ID: {azure_video_id}")

        # Clean up local file
        if os.path.exists(local_path):
            os.remove(local_path)

        # wait 
        raw_insights = vi_service.wait_for_proessing(azure_video_id)
        logger.info("Video Processing Completed")

        # Extract 
        claan_data = vi_service.extract_data(raw_insights)

        logger.info("---- [Node: Indexer] Extraction complete ----")
        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer Failed: {e}")
        return {
            "error": [str(e)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": []
        }

# --- NODE 2: THE COMPLIANCE AUDITOR ---
def audit_content_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Performs Retrieval-Augmented Generation (RAG) to audit the content.
    """
    logger.info("---- [Node: Auditor] querying Knowledge Base & LMM ----")

    transcript = state.get("transcript", "")

    if not transcript:
        logger.warning("No transcript available. Skipping Audit.")
        return {
            "final_status" : "FAIL",
            "final_report": "Audit skipped because video processing failed (No Transcript)."
        }

    # Initialize Clients
    llm = AzureChatOpenAI(
        azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature = 0.0
    )

    # Initialize Embeddings
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment = "text-embedding-2-small",
        openai_api_version = os.genenv("AZURE_OPENAI_API_VERSION")
    )

    # Initialize Vector Store
    vector_store = AzureSearch(
        azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key = os.getenv("AZURE_SEARCH_KEY"),
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function = embeddings.embed_query
    )

    # RAG Retrievel
    ocr_txt = state.get("ocr_text", [])
    query_text = f"{transcript} {' '.join(ocr_text)}"
    docs= vector_store.similarity_search(query_text, k = 3)

    retrieved_rules = "\n\n".join([doc.page_content for doc in docs])

    # UPDATED PROMPT WITH STRICT INSTRUCTIONS
    system_prompt = f"""
    You are a Senior Brand Compliance Auditor.

    OFFICIAL REGULATORY RULES:
    {retrived_rules}

    INSTRUCTIONS:
    1. Analyze the transcript and OCR text.
    2. Identify Any violations of the rules.
    3. Return strictly JSON in the following format:

    {{
        "compliance_results": [
            {{
                "category": "Claim validation",
                "severity" : "High/Medium/Low",
                "description": "Explanation of the violation..."
            }}
        ],
        "status": "PASS/FAIL",
        "final_report": Summary of finding..."
    }}

    If no violations are found, set "status" to "PASS" and "compliance_results" to [].
    """

    user_message = f"""
    VIDEO METADATA: {state.get('video_metadata', {})}
    TRANSCRIPT: {transcript}
    ON-SCREEN TEXT (OCR): {ocr_text}
    """

    try:
        response = llm.invoke([
            SystemMessage(content = System_prompt),
            HumanMessage(content = user_message)
        ])

        # FIX: Clean Markdown if present (```json...```)
        content = response.content
        if "```" in content:
            # Regex to find JSON inside code blocks
            content = re.search(r"```(?:JSON)?(.*)```", content, re.DOTALL).group(1)

        audit_data = json.loads(content.strip())

        return {
            "compliance_results": audit_data.get("complaince_results", []),
            "final_status": audit_data.get("Status","FAIL"),
            "final_report": audit_data.get("final_report", "No report generated.")
        }
    
    except Exception as e:
        logger.error(f"System Error in Auditor Node: {str(e)}")
        # Log the raw response to see what went wrong 
        logger.error(f"Raw LLM Response: {response.content if 'response' in locals() else 'None'}")
        return {
            "errors": [str(e)],
            "final_status":"FAIL"
        }
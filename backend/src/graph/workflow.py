"""
Workflow Definition for the Compliance QA AI.

This module defines the Directed Acyclic Graph (DAG) that orchestrates the
video compliance audit process using LangGraph.
"""

from langgraph.graph import StateGraph, START, END

# Import the State Schema
from backend.src.graph.state import VideoAuditState

# Import the Functional Nodes
from backend.src.graph.nodes import index_video_node, audit_content_node

# Conditional Routing Logic
def check_indexing_status(state: VideoAuditState) -> str:
    """
    Determines whether the indexing step succeeded.

    If transcript exists -> success
    If transcript missing -> failure
    """

    transcript = state.get("transcript")

    if transcript:
        return "success"
    
    return "fail"


def create_graph():
    
    # Initialize the Graph with the State Schema
    workflow = StateGraph(VideoAuditState)

    # Add Nodes 
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    # Define Flow
    workflow.add_edge(START,"indexer")

    # Conditional Routing after indexer
    workflow.add_conditional_edges(
        "indexer",
        check_indexing_status,
        {
            "success": "auditor",
            "fail":END
        }
    )

    workflow.add_edge("auditor", END)

    # Compile the Graph
    app = workflow.compile()

    return app

# Expose the runnable app for import by the API or CLI
app = create_graph()

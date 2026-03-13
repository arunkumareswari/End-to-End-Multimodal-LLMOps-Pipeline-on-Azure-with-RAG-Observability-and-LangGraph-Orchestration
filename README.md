# End-to-End Multimodal LLMOps Pipeline on Azure

![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white) 
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) 
![Azure OpenAI Model](https://img.shields.io/badge/Azure_OpenAI-gpt--4o-F37021?style=flat&logo=openai&logoColor=white) 
![Azure Embeddings](https://img.shields.io/badge/Azure_Embeddings-text--embedding--3--small-0078D4?style=flat&logo=microsoft-azure&logoColor=white) 
![Azure AI Search](https://img.shields.io/badge/Azure_AI_Search-Vector_DB-107C10?style=flat&logo=microsoft-azure&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?style=flat)
![Video Indexer](https://img.shields.io/badge/Azure_Video_Indexer-4B52C3?style=flat&logo=microsoft-azure&logoColor=white)

A highly specialized AI-powered compliance QA pipeline built on Azure, utilizing Retrieval-Augmented Generation (RAG), Observability, and LangGraph orchestration to automatically audit video content against brand and regulatory compliance rules.

## 🌟 Overview

The **Compliance QA Pipeline** simulates a Video Compliance Audit. It ingests video content (e.g., YouTube URLs), extracts multi-modal data (transcripts and on-screen text), and uses a specialized AI agent to evaluate the content against specific regulatory guidelines (such as FTC and YouTube rules) stored in its Knowledge Base. 

The pipeline delivers a detailed, structured JSON report detailing any compliance violations, their severity, and an overall PASS/FAIL status.

## 🏗️ Architecture

The pipeline is orchestrated using **LangGraph** as a Directed Acyclic Graph (DAG) consisting of two primary functional nodes:

1. **Indexer Node**: 
   - Downloads the target video (e.g., from YouTube).
   - Uploads the video to **Azure Video Indexer**.
   - Extracts insights, specifically the audio transcript and OCR (on-screen text).
2. **Auditor Node**: 
   - Retrieves relevant compliance rules from the Knowledge Base using **RAG** (Retrieval-Augmented Generation).
   - Analyzes the multi-modal video data (transcript + OCR text) using an **Azure OpenAI** Chat Model.
   - Generates a structured JSON compliance audit report identifying violations.

### 🧠 The Knowledge Base ("Memory")

The AI operates as a specialized auditor through a dedicated ETL (Extract, Transform, Load) setup script (`index_documents.py`):
- **Extract**: Reads compliance PDFs (e.g., `influencer-guide` and `youtube-ad-specs`).
- **Transform**: Chunks the documents and generates vector embeddings using Azure OpenAI's `text-embedding-3-small` model.
- **Load**: Stores the vector embeddings in **Azure AI Search**, allowing the Auditor Node's RAG system to instantly reference these specific rulebooks during the evaluation over the network.

## 🛠️ Tech Stack

- **Frameworks**: FastAPI, LangChain, LangGraph
- **AI & Machine Learning**: 
  - **Embedding**: Azure OpenAI `text-embedding-3-small`
  - **Model**: Azure OpenAI `gpt-4o`
- **Vector Database**: Azure AI Search
- **Video Processing**: Azure Video Indexer
- **Observability**: Azure Monitor OpenTelemetry
- **Language**: Python 3.11+

## 🚀 Getting Started

### Prerequisites
- Python >= 3.11
- Azure account with configured services: Video Indexer, OpenAI, AI Search, and Application Insights.
- Environment variables configured in a `.env` file containing all Azure endpoints/keys.

### 🔑 Environment Configuration

Create a `.env` file in the root directory and populate it with the following Azure and LangGraph configurations:

| Category | Variable Name | Description |
| :--- | :--- | :--- |
| **Storage** | `AZURE_STORAGE_ACCOUNT_STRING` | Connection string for Azure Storage Account |
| **OpenAI** | `AZURE_OPENAI_API_KEY` | Primary API Key for Azure OpenAI service |
| | `AZURE_OPENAI_ENDPOINT` | Endpoint URL for Azure OpenAI |
| | `AZURE_OPENAI_API_VERSION` | API version (e.g., `2024-12-01-preview`) |
| | `AZURE_OPENAI_CHAT_DEPLOYMENT` | Deployment name for Chat Model (e.g., `gpt-4o`) |
| **Embeddings** | `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Deployment name for Embedding Model |
| | `AZURE_OPENAI_EMBEDDING_ENDPOINT`| Endpoint URL for Embedding service |
| | `AZURE_OPENAI_EMBEDDING_API_KEY` | API Key for Embedding service |
| **AI Search** | `AZURE_SEARCH_API_KEY` | Admin API Key for Azure AI Search |
| | `AZURE_SEARCH_ENDPOINT` | Endpoint URL for Azure AI Search |
| | `AZURE_SEARCH_INDEX_NAME` | Name of the vector index (e.g., `brand-compliance-rules`) |
| **Video Indexer**| `AZURE_VI_NAME` | Azure Video Indexer Account Name |
| | `AZURE_VI_LOCATION` | Region location (e.g., `eastus`) |
| | `AZURE_VI_ACCOUNT_ID` | Video Indexer Account GUID |
| | `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID |
| | `AZURE_RESOURCE_GROUP` | Azure Resource Group name |
| **Observability**| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Azure Application Insights connection string |
| **LangSmith** | `LANGCHAIN_TRACING_V2` | Set to `true` to enable LangSmith tracing |
| | `LANGCHAIN_API_KEY` | Your LangSmith API Key |
| | `LANGCHAIN_PROJECT` | Name of the LangSmith project |

### 🔨 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd ComplianceQAPipeline
   ```

2. **Set up the virtual environment and install dependencies:**
   This project leverages modern environments via `uv` or `pip`. 
   ```bash
   pip install -r requirements.txt
   ```
   *(Alternatively, run `uv sync` if utilizing the `uv.lock` file).*

### System Setup & Execution

1. **Initialize the Knowledge Base:**
   Run the document indexing script to populate Azure AI Search with your compliance PDFs.
   ```bash
   python backend/scripts/index_documents.py
   ```
   *This builds the "Brain" of the compliance application.*

2. **Run the CLI Simulation:**
   Run a standalone audit simulation locally.
   ```bash
   python main.py
   ```
   *This runs through the workflow for a predefined YouTube video, orchestrates the Graph, and logs the final Compliance Audit Report directly to your console.*

3. **Run the FastAPI Server:**
   Start the REST API to expose the workflow as a scalable backend service.
   ```bash
   uvicorn backend.src.api.server:app --reload
   ```
   - **Endpoint**: `POST /audit` (Requires `{"video_url": "..."}`)
   - **Health Check**: `GET /health`

## 📊 Observability

This project integrates **Azure Monitor OpenTelemetry** to track:
- HTTP requests and backend performance.
- LangGraph node execution steps.
- Internal errors or workflow failures.

To enable observability, ensure the `APPLICATIONINSIGHTS_CONNECTION_STRING` is set in your `.env` file. If left out, the telemetry initialization smoothly falls back to a disabled state without crashing the app.

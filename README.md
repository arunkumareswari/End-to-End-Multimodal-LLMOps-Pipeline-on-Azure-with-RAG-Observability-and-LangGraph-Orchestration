# End-to-End Multimodal LLMOps Pipeline on Azure

![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=skyblue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Azure OpenAI Model](https://img.shields.io/badge/Azure_OpenAI-gpt--4o-F37021?style=flat&logo=openai&logoColor=white)
![Azure Embeddings](https://img.shields.io/badge/Azure_Embeddings-text--embedding--3--small-0078D4?style=flat&logo=microsoft-azure&logoColor=white)
![Azure AI Search](https://img.shields.io/badge/Azure_AI_Search-Vector_DB-107C10?style=flat&logo=microsoft-azure&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?style=flat)
![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-FF6B35?style=flat&logo=langchain&logoColor=green)
![Video Indexer](https://img.shields.io/badge/Azure_Video_Indexer-4B52C3?style=flat&logo=microsoft-azure&logoColor=white)

An AI-powered compliance QA pipeline built on Azure that automatically audits video content against brand and regulatory standards. It leverages Retrieval-Augmented Generation (RAG), LangGraph orchestration, and Azure's multimodal services to deliver structured, actionable audit reports.

---

## Overview

The **Compliance QA Pipeline** ingests a video (e.g., a YouTube URL), extracts multimodal data — audio transcripts and on-screen text via OCR — and runs the content through a specialized AI auditor grounded in a regulatory knowledge base (FTC guidelines, YouTube ad specs, etc.).

The final output is a detailed JSON report listing any compliance violations, their severity levels, and an overall **PASS / FAIL** verdict.

---

## Architecture

The pipeline is orchestrated with **LangGraph** as a Directed Acyclic Graph (DAG) with two primary nodes:

### 1. Indexer Node
- Downloads the target video from the provided URL.
- Uploads it to **Azure Video Indexer**.
- Extracts multimodal insights: audio transcript and OCR (on-screen text).

### 2. Auditor Node
- Retrieves relevant compliance rules from the Knowledge Base using **RAG**.
- Analyzes the extracted transcript and OCR text using **Azure OpenAI `gpt-4o`**.
- Outputs a structured JSON compliance audit report with violations and severity.

### Knowledge Base (ETL)

The auditor's intelligence comes from a one-time setup script (`index_documents.py`) that builds the knowledge base:

- **Extract** — Reads compliance PDFs (e.g., `influencer-guide`, `youtube-ad-specs`).
- **Transform** — Chunks documents and generates vector embeddings via Azure OpenAI `text-embedding-3-small`.
- **Load** — Stores embeddings in **Azure AI Search**, enabling real-time RAG retrieval during audits.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| Orchestration | LangGraph, LangChain |
| LLM | Azure OpenAI `gpt-4o` |
| Embeddings | Azure OpenAI `text-embedding-3-small` |
| Vector Store | Azure AI Search |
| Video Processing | Azure Video Indexer |
| Observability | Azure Monitor OpenTelemetry, LangSmith |
| Language | Python 3.11+ |

---

## Getting Started

### Prerequisites

- Python >= 3.11
- An active Azure account with the following services configured:
  - Azure OpenAI (Chat + Embeddings deployments)
  - Azure AI Search
  - Azure Video Indexer
  - Azure Application Insights
- A `.env` file in the project root with all required credentials (see below).

### Environment Configuration

Create a `.env` file in the root directory and populate it with your Azure credentials. The variables are grouped by service:

**Azure Storage**
```
AZURE_STORAGE_ACCOUNT_STRING=<connection string for Azure Storage Account>
```

**Azure OpenAI (Chat)**
```
AZURE_OPENAI_API_KEY=<primary API key>
AZURE_OPENAI_ENDPOINT=<endpoint URL>
AZURE_OPENAI_API_VERSION=<e.g. 2024-12-01-preview>
AZURE_OPENAI_CHAT_DEPLOYMENT=<deployment name, e.g. gpt-4o>
```

**Azure OpenAI (Embeddings)**
```
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=<deployment name>
AZURE_OPENAI_EMBEDDING_ENDPOINT=<endpoint URL>
AZURE_OPENAI_EMBEDDING_API_KEY=<API key>
```

**Azure AI Search**
```
AZURE_SEARCH_API_KEY=<admin API key>
AZURE_SEARCH_ENDPOINT=<endpoint URL>
AZURE_SEARCH_INDEX_NAME=<index name>
```

**Azure Video Indexer**
```
AZURE_VI_NAME=<account name>
AZURE_VI_LOCATION=<region, e.g. eastus>
AZURE_VI_ACCOUNT_ID=<account GUID>
AZURE_SUBSCRIPTION_ID=<subscription ID>
AZURE_RESOURCE_GROUP=<resource group name>
```

**Observability**
```
APPLICATIONINSIGHTS_CONNECTION_STRING=<Azure Application Insights connection string>
```

**LangSmith**
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your LangSmith API key>
LANGCHAIN_PROJECT=<project name>
```

---

### Installation

**1. Clone the repository:**
```bash
git clone <repository_url>
cd ComplianceQAPipeline
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```
> Alternatively, run `uv sync` if using the `uv.lock` file.

---

## Running the Pipeline

**Step 1 — Build the Knowledge Base**

Populate Azure AI Search with your compliance PDFs. Run this once before any audits:
```bash
python backend/scripts/index_documents.py
```

**Step 2 — Run a Local Simulation**

Execute a standalone audit against a predefined YouTube video and view the report in your console:
```bash
python main.py
```

**Step 3 — Start the API Server**

Expose the pipeline as a REST API:
```bash
uvicorn backend.src.api.server:app --reload
```

Available endpoints:
- `POST /audit` — Trigger an audit. Request body: `{"video_url": "..."}`
- `GET /health` — Health check

---

## Observability

The pipeline integrates **Azure Monitor OpenTelemetry** for end-to-end tracing across:
- HTTP requests and API performance
- LangGraph node execution steps
- Internal errors and workflow failures

It also supports **LangSmith** tracing for detailed LangChain/LangGraph run inspection. Set `LANGCHAIN_TRACING_V2=true` and provide your `LANGCHAIN_API_KEY` to enable it.

If `APPLICATIONINSIGHTS_CONNECTION_STRING` is not set, telemetry gracefully falls back to a disabled state without crashing the application.
# Gemini Code Assistant Context

This document provides context for the AI Presentation Factory project.

## Project Overview

This project is a web-based "AI Presentation Factory" that generates professional PowerPoint presentations from PDF documents. It is a Python application built with a client-server architecture.

**Core Functionality:**

1.  **PDF Analysis (Agent 1):** A user uploads PDF documents. The system analyzes the content and creates a structured plan for a presentation (e.g., titles, bullet points, image search terms for each slide).
2.  **PPT Generation (Agent 2):** Based on the plan, the system generates a `.pptx` file. It intelligently selects slide layouts from a template, chooses color schemes, and fetches appropriate images (either from stock photo providers or by generating them with an AI).

**Architecture:**

The application consists of two main services orchestrated by Docker Compose:

1.  **`agent-app` (Streamlit Client):**
    *   The user-facing web interface, built with Streamlit.
    *   It handles file uploads, user configuration (language, number of slides, etc.), and displays the final presentation for download.
    *   The UI and business logic are primarily in German.
    *   Entrypoint: `app.py`

2.  **`mcp-server` (FastAPI Server):**
    *   A "Multi-Capability Provider" (MCP) backend server built with FastAPI.
    *   It acts as a tool provider for the Streamlit client. It exposes functionalities that require direct access to the file system or other resources.
    *   **Tools provided:** Reading PDF files (`read_pdf_file`), listing presentation templates (`list_templates`), analyzing templates (`analyze_template`), and providing template files (`get_template_file`).
    *   Entrypoint: `mcp_server.py`

**Key Technologies:**

*   **Frontend:** Streamlit
*   **Backend:** FastAPI
*   **AI/LLM:** Google Gemini (`gemini-2.5-flash`) via `langchain-google-genai`
*   **PowerPoint Generation:** `python-pptx`
*   **Containerization:** Docker, Docker Compose
*   **Data Validation:** Pydantic

## Building and Running the Project

The project is designed to be run with Docker.

**Prerequisites:**

*   Docker and Docker Compose must be installed.
*   A `.env` file must be present in the root directory, containing at least the `GOOGLE_API_KEY`.

**To start the application:**

```bash
docker-compose up --build
```

This command will:
1.  Build the Docker image as defined in the `Dockerfile`.
2.  Start both the `agent-app` and `mcp-server` containers.

**Accessing the services:**

*   **Streamlit Web App:** `http://localhost:8501`
*   **FastAPI Server (MCP):** `http://localhost:8010` (The server runs on port 8000 inside the container, but is exposed as 8010 on the host).

## Development Conventions

*   **Client-Server Communication:** The Streamlit client communicates with the FastAPI server via Server-Sent Events (SSE). The client does not access the file system directly for tasks like reading PDFs or templates; it calls tools on the `mcp-server`.
*   **Agent-Based Logic:** The core logic is split into two "agents":
    *   **Agent 1 (`agent_logic.py`):** Plans the presentation structure.
    *   **Agent 2 (`ppt_agent.py`):** Builds the presentation file.
*   **Configuration:** The application uses a `.env` file for secrets and environment-specific configuration.
*   **Language:** The user interface and a significant portion of the internal code (prompts, comments) are in German.
*   **Templates:** PowerPoint templates are stored in the `data/templates` directory and are served by the `mcp-server`.
*   **Output:** Generated presentations and other temporary files are stored in the `storage` directory, which is shared between the host and the `agent-app` container.

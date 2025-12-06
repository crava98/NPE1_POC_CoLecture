# Gemini Code Assistant Context

This document provides context for the Gemini Code Assistant to understand the project structure, purpose, and key components.

## Project Overview

This project is a Python-based application that automatically generates PowerPoint presentations from PDF documents. It consists of a Streamlit web interface for user interaction and a FastAPI backend for processing PDF files. The application is designed to be run in a containerized environment using Docker.

The core functionality is powered by the Gemini 1.5 Flash language model, which is used to analyze the content of the uploaded PDFs and generate a structured presentation plan. This plan is then used to create a PowerPoint presentation, including fetching relevant images for each slide.

### Key Technologies

- **Frontend:** Streamlit
- **Backend:** FastAPI, Uvicorn
- **Language Model:** Google Gemini 1.5 Flash (via `langchain-google-genai`)
- **PDF Processing:** `pypdf`
- **Presentation Generation:** `python-pptx`
- **Containerization:** Docker, Docker Compose
- **Communication:** `mcp` library for client-server communication using Server-Sent Events (SSE)
- **Image Generation (optional):** n8n webhook integration

### Architecture

The application is composed of two main services, orchestrated by `docker-compose.yml`:

1.  **`agent-app` (Streamlit Client):**
    -   Provides a web interface for users to upload PDF files, select presentation options (language, number of slides), and download the generated presentation.
    -   Communicates with the `mcp-server` to request PDF content processing.
    -   Calls the Gemini API to generate the presentation structure.
    -   Calls the `ppt_engine` to generate the final `.pptx` file.

2.  **`mcp-server` (FastAPI Backend):**
    -   A "tool provider" server that exposes a single tool: `read_pdf_file`.
    -   This tool reads the text content from a PDF file stored in the `data` volume.
    -   The server listens for requests from the `agent-app` via SSE.

### File Structure

- `app.py`: The main entry point for the Streamlit application.
- `agent_logic.py`: Contains the core logic for orchestrating the PDF analysis and presentation planning. It communicates with both the `mcp-server` and the Gemini API.
- `ppt_engine.py`: Responsible for generating the PowerPoint presentation from the structured data provided by the agent. It also handles fetching images for the slides.
- `mcp_server.py`: The FastAPI application that acts as a tool server for reading PDF files.
- `data_models.py`: Defines the Pydantic data models used for structuring the presentation plan.
- `docker-compose.yml`: Defines the services, networks, and volumes for the containerized application.
- `Dockerfile`: Used to build the Docker image for both the `agent-app` and `mcp-server`.
- `requirements.txt`: Lists the Python dependencies for the project.
- `data/`: A directory for storing data, including uploaded PDFs and generated presentations. It is mounted as a volume in the containers.
- `storage/`: A directory for storing generated files.
- `.env`: A file for storing environment variables, such as API keys.

## Building and Running

To run the application, you need to have Docker and Docker Compose installed.

1.  **Environment Variables:**
    -   Create a `.env` file in the root of the project.
    -   Add your Google API key to the `.env` file:
        ```
        GOOGLE_API_KEY="your_google_api_key"
        ```
    -   (Optional) If you have an n8n webhook for image generation, add it to the `.env` file:
        ```
        N8N_WEBHOOK_URL="your_n8n_webhook_url"
        N8N_AUTH_TOKEN="your_n8n_auth_token"
        ```

2.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

3.  **Access the Application:**
    -   **Streamlit App:** Open your web browser and go to `http://localhost:8501`.
    -   **MCP Server:** The server is accessible at `http://localhost:8010`, but it is primarily used for communication with the `agent-app`.

## Development Conventions

- The application uses type hints and Pydantic models for data validation and structuring.
- The `mcp` library is used for communication between the client and server.
- The `agent_logic.py` file contains the core business logic, separating it from the Streamlit UI code in `app.py`.
- The `ppt_engine.py` file encapsulates the logic for creating the PowerPoint presentation.
- Environment variables are used to manage configuration and secrets.

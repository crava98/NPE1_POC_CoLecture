# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Presentation Factory - A Python application that generates PowerPoint presentations from PDF documents using Google's Gemini LLM and multiple AI agents. The system demonstrates Agent vs. MCP architecture with intelligent PPT generation.

## Architecture

![Sequenzdiagramm](resource/Sequenzdiagram%20PoC.png)

The application consists of two Docker services with a **multi-agent architecture**:

1. **agent-app (Streamlit Client)** - Port 8501
   - Web UI for uploading PDFs and configuring presentations
   - Hosts multiple AI agents
   - Communicates with MCP server via SSE (Server-Sent Events)

2. **mcp-server (FastAPI Backend)** - Port 8010 (internal 8000)
   - Tool provider server with multiple tools
   - PDF Tools: `read_pdf_file`
   - Template Tools: `list_templates`, `analyze_template`, `get_template_file`
   - Communicates via MCP protocol using SSE
   - Templates stored in `/data/templates/` (Docker volume)

### Multi-Agent System

The application uses **3 specialized AI agents**:

#### Agent 1: Content Planning Agent (`agent_logic.py`)
- **Purpose:** Analyzes PDFs and creates presentation structure
- **Tools:** Calls MCP `read_pdf_file` to get PDF content
- **LLM:** Gemini 2.5 Flash with structured output
- **Output:** `PresentationStructure` with slides, bullets, sources

#### Agent 2: PPT Builder Agent (`ppt_agent.py`)
- **Purpose:** Intelligently generates PowerPoint with optimal layouts and images
- **Tools:** Calls MCP `list_templates`, `analyze_template`, `get_template_file`
- **Pure Agent:** NO direct file system access - all data via MCP!
- **Intelligence:**
  - Loads template as Base64-encoded bytes via MCP
  - Analyzes template structure via MCP
  - LLM-based layout selection via `decide_layout_for_slide()`
  - Chooses best layout for each slide based on content type
  - Adapts to any template automatically (no hard-coding)
  - **Image Style Decision:** `decide_image_style_for_slide()` - Agent wählt passenden Bildstil (flat_illustration, fine_line, photorealistic)
  - **Color Decision:** `decide_colors_for_presentation()` - Agent wählt Farbschema basierend auf Thema
- **Output:** Professional PPTX file with AI-generated images

#### Agent 3: QA/Reviewer Agent (Planned)
- **Purpose:** Quality control and validation
- **Future:** Will review generated PPTs and suggest improvements

### Key Workflow

1. User uploads PDFs and selects template via Streamlit UI
2. **Agent 1** calls MCP `read_pdf_file` for each PDF
3. **Agent 1** sends combined text to Gemini → returns `PresentationStructure`
4. **Agent 2** calls MCP `list_templates` and `analyze_template`
5. **Agent 2** uses LLM to decide optimal layout for each slide
6. **Agent 2** generates PPTX with intelligent layout choices
7. User downloads completed presentation

### Agent vs. MCP Philosophy

- **Agents** make intelligent decisions using LLMs (what to do)
- **MCP Server** provides tools and data access (how to do it)
- **Templates** are served via MCP (not hard-coded paths)
- **Scalable:** New templates work automatically without code changes

## Commands

### Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run without rebuilding
docker-compose up

# Stop services
docker-compose down
```

### Access Points

- Streamlit UI: http://localhost:8501
- MCP Server: http://localhost:8010 (internal communication only)

### Environment Variables Required

Create a `.env` file with:
```
GOOGLE_API_KEY="your_google_api_key"
N8N_WEBHOOK_URL="your_n8n_webhook_url"  # Optional
N8N_AUTH_TOKEN="your_n8n_auth_token"     # Optional
MCP_SERVER_URL="http://mcp-server:8000/sse"  # Set in docker-compose
```

## Code Structure

### Core Files

- `app.py` - Streamlit UI with session state management, file upload, and generation workflow
- `agent_logic.py` - Orchestrates PDF reading via MCP and LLM planning via Gemini
- `ppt_engine.py` - PowerPoint generation with template support and image insertion
- `mcp_server.py` - FastAPI/MCP tool server for PDF reading
- `data_models.py` - Pydantic models for structured LLM output

### Data Models (data_models.py)

All models use Pydantic with `default=[]` for optional lists to prevent LLM output errors:

- `Source` - Document references (documentId, pageNumber)
- `BulletItem` - Bullet points with optional sub-bullets
- `ImageColors` - Farbschema mit primary/secondary Hex-Codes
- `CustomerSlide` - Complete slide structure mit zusätzlichen Bildfeldern:
  - `ImageKeywords` - Optional, überschreibt unsplashSearchTerms
  - `style` - Bildstil: "auto", "flat_illustration", "fine_line", "photorealistic"
  - `image_mode` - Bildquelle: "auto", "stock_only", "ai_only"
  - `ai_model` - AI-Modell: "auto", "flux", "banana"
  - `colors` - Optional ImageColors für Farbschema
- `PresentationStructure` - Full presentation with list of slides

### MCP Communication

The MCP server uses SSE transport:
- Client connects via `sse_client(mcp_server_url)`
- Async session calls `call_tool("read_pdf_file", arguments={"filename": ...})`
- Server returns text content wrapped in `types.TextContent`

### Template System

Templates are loaded from `ppt_templates/` directory:
- Supports `.pptx` and `.potx` files
- All existing slides are deleted from template before generation
- Layouts are matched by name: "Title Slide" and "Title and Content"
- Falls back to index-based layout selection if names don't match

### Image Generation (image_providers.py)

Primary: `get_image_from_gurkli()` - Sends slide data to https://langchain.gurk.li/generate-image
Fallback: `get_image_placeholder()` - Uses loremflickr.com for placeholder images

**JSON Payload an Gurkli API:**
```json
{
  "title": "Slide Title",
  "bullets": [{"bullet": "...", "sub": []}],
  "ImageKeywords": ["keyword1", "keyword2"],
  "style": "flat_illustration",
  "image_mode": "auto",
  "ai_model": "auto",
  "colors": {"primary": "#004A7F", "secondary": "#E37222"}
}
```

**Verfügbare Optionen:**
- `style`: "flat_illustration" | "fine_line" | "photorealistic"
- `image_mode`: "auto" | "stock_only" | "ai_only"
- `ai_model`: "auto" | "flux" | "banana"

**Agent-Entscheidungen (wenn "auto"):**
- Style: Agent analysiert Folieninhalt und wählt passenden Stil
  - Reale Industrien (Auto, Handel) → photorealistic
  - Abstrakte Konzepte (Innovation) → flat_illustration
  - Technische Details → fine_line
- Colors: Agent wählt Farbschema basierend auf Präsentationsthema

## Important Implementation Details

### UI Layout (app.py)

Die App hat einen linearen Flow ohne Sidebar:

1. **PDF-Dokumente hochladen** - Drag & Drop oder Dateiauswahl
2. **Sprache und Umfang** - Sprache (Dropdown) + Folienanzahl (Slider 3-20)
3. **Design-Template auswählen** - Grid mit Screenshots (4 Spalten)
   - Screenshots in `data/templates/Screeenshot/`
   - Klick zum Auswählen/Abwählen (Toggle)
4. **Bild-Einstellungen** - 3 Spalten:
   - Bildstil: auto, flat_illustration, fine_line, photorealistic
   - Bildquelle: auto, stock_only, ai_only
   - Eigene Farben: Optional mit Color Picker
5. **Präsentation generieren** - Zusammenfassung + Buttons

### Streamlit Theme (.streamlit/config.toml)

Helles Theme-Konfiguration:
```toml
[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F7FA"
textColor = "#1A1A1A"
font = "sans serif"
```

### Session State Management

Streamlit uses `st.session_state` for:
- `uploaded_files_data` - Current uploaded files
- `saved_pdf_paths` - Paths to saved PDFs in storage
- `cancel_requested` - Flag for canceling generation
- `selected_template_name` - Ausgewähltes Template

### Async/Sync Bridging

`agent_logic.py` uses `asyncio.run()` to call async MCP functions from synchronous Streamlit context:
```python
combined_text = asyncio.run(fetch_pdf_content_via_mcp(pdf_paths_list))
```

### Language Support

The app supports multi-language presentations:
- Languages: Deutsch, English, Français, Italiano, Español
- Language parameter is passed through the entire pipeline
- Affects LLM prompt and source labels in generated PPTX

### LLM Configuration

Gemini is configured with:
- Model: `gemini-2.5-flash`
- Temperature: 0.2
- Structured output via `.with_structured_output(PresentationStructure)`

The prompt instructs Gemini to:
- Create exactly N slides (user-specified)
- Keep bullets extremely concise (3-4 bullets, max 10 words)
- Generate 3 English search terms for images
- Output in specified language

### Volume Mapping

Docker volumes are critical for data sharing:
- `./data:/app/storage` (agent-app) - PDFs uploaded by user
- `./data:/data` (mcp-server) - Same PDFs accessible to server
- Both containers need access to the same files

### Error Handling

Image generation has multiple fallback layers:
1. Try gurk.li API (60s timeout)
2. Fall back to loremflickr placeholder
3. If image insertion fails in template, manually position at fixed coordinates

## Notes for Development

- The MCP server must be running before the agent-app starts (controlled by `depends_on` in docker-compose)
- Session state prevents re-uploading files on every Streamlit rerun
- Cancel button uses callback to set session state flag and `st.stop()` to halt execution
- Template placeholder matching tries by type first, then falls back to idx > 10 for picture placeholders

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Presentation Factory - A Python application that generates PowerPoint presentations from PDF documents using Google's Gemini LLM and multiple AI agents. The system demonstrates Agent vs. MCP architecture with intelligent PPT generation.

## Commands

### Docker Development (Recommended)

```bash
# Build and run all services
docker-compose up --build

# Run without rebuilding
docker-compose up

# Stop services
docker-compose down

# View logs for specific service
docker-compose logs -f agent-app
docker-compose logs -f mcp-server
```

### Running Tests

```bash
# Run all tests
python -m pytest test_*.py

# Run specific test file
python -m pytest test_ppt_agent.py -v

# Run with mock LLM (tests use unittest.mock)
python -m unittest test_ppt_agent.py
```

### Access Points

- Streamlit UI: http://localhost:8501
- MCP Server: http://localhost:8010 (internal: 8000)
- ngrok Dashboard: http://localhost:4040 (external tunnel with basic auth)

### Portainer Deployment

```bash
# 1. Build and tag images for registry
docker build -t ai-presentation-factory/agent-app:latest .
docker build -t ai-presentation-factory/mcp-server:latest .

# 2. Push to your registry (example: Docker Hub)
docker tag ai-presentation-factory/agent-app:latest myregistry/ppt-agent:latest
docker tag ai-presentation-factory/mcp-server:latest myregistry/ppt-mcp:latest
docker push myregistry/ppt-agent:latest
docker push myregistry/ppt-mcp:latest

# 3. In Portainer:
#    - Stacks → Add Stack
#    - Upload docker-compose.portainer.yml
#    - Set environment variables (see .env.example)
#    - Deploy
```

**Required Portainer Environment Variables:**
| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `REGISTRY` | No | Image registry prefix |
| `TAG` | No | Image tag (default: latest) |
| `NGROK_AUTHTOKEN` | No | For external access |
| `NGROK_BASIC_AUTH` | No | Format: `user:pass` |

**Volumes (auto-created):**
- `ppt-data` - Uploaded PDFs and generated presentations
- `ppt-templates` - PowerPoint templates (upload via volume)

### Environment Variables

For local development, create `.env` file (see `.env.example`):
```
GOOGLE_API_KEY="your_google_api_key"
NGROK_AUTHTOKEN="your_ngrok_token"       # Optional
N8N_WEBHOOK_URL="your_n8n_webhook_url"   # Optional
N8N_AUTH_TOKEN="your_n8n_auth_token"     # Optional
```

## Architecture

![Sequenzdiagramm](resource/Sequenzdiagram%20PoC.png)

Three Docker services with multi-agent architecture:

1. **agent-app** (Port 8501) - Streamlit UI + AI agents
2. **mcp-server** (Port 8010→8000) - FastAPI tool provider via MCP/SSE
3. **ngrok** (Port 4040) - External tunnel (auth: Student/hslu5in5rotkreuz)

### Multi-Agent System

**Agent 1: Content Planning** (`agent_logic.py`)
- Reads PDFs via MCP `read_pdf_file`
- Uses Gemini 2.5 Flash with structured output
- Returns `PresentationStructure` with slides, bullets, sources

**Agent 2: PPT Builder** (`ppt_agent.py`)
- NO direct filesystem access - pure MCP agent
- Calls `list_templates`, `analyze_template`, `get_template_file`
- LLM-based layout selection via `decide_layout_for_slide()`
- Image style decision via `decide_image_style_for_slide()`
- Color scheme selection via `decide_colors_for_presentation()`

**Agent 3: QA/Reviewer** (Planned)

### Workflow

1. User uploads PDFs → Agent 1 reads via MCP
2. Agent 1 → Gemini → `PresentationStructure`
3. Agent 2 analyzes template via MCP
4. Agent 2 generates PPTX with intelligent layouts
5. User downloads presentation

### Agent vs. MCP Philosophy

- **Agents**: Make intelligent decisions using LLMs (what to do)
- **MCP Server**: Provides tools and data access (how to do it)
- **Templates**: Served via MCP (not hard-coded paths)

## Code Structure

### Core Files

- `app.py` - Streamlit UI with session state management
- `agent_logic.py` - Agent 1: PDF reading + Gemini planning
- `ppt_agent.py` - Agent 2: Intelligent PPT generation
- `ppt_engine.py` - PowerPoint generation utilities
- `mcp_server.py` - FastAPI/MCP tool server
- `data_models.py` - Pydantic models for structured LLM output
- `image_providers.py` - Image generation (Gurkli API + fallback)

### Data Models (data_models.py)

All models use `default=[]` for optional lists to prevent LLM output errors:

- `PresentationStructure` - Top-level container with list of `CustomerSlide`
- `CustomerSlide` - Slide with title, bullets, sources, image settings:
  - `style`: "auto" | "flat_illustration" | "fine_line" | "photorealistic"
  - `image_mode`: "auto" | "stock_only" | "ai_only"
  - `ai_model`: "auto" | "flux" | "banana"
  - `colors`: Optional `ImageColors` (primary/secondary hex codes)
- `BulletItem` - Bullet with optional sub-bullets
- `Source` - Document reference (documentId, pageNumber)

### MCP Communication

SSE transport pattern:
```python
async with sse_client(mcp_server_url) as streams:
    async with ClientSession(streams[0], streams[1]) as session:
        await session.initialize()
        result = await session.call_tool("tool_name", arguments={...})
```

Sync-to-async bridge in Streamlit context:
```python
combined_text = asyncio.run(fetch_pdf_content_via_mcp(pdf_paths_list))
```

### MCP Tools (mcp_server.py)

| Tool | Description |
|------|-------------|
| `read_pdf_file` | Extract text from PDF in `/data/` |
| `list_templates` | List available `.pptx`/`.potx` templates |
| `analyze_template` | Get layout structure with classified types |
| `get_template_file` | Return template as Base64-encoded bytes |
| `get_template_path` | Return filesystem path (legacy) |

### Template System

- Templates in `data/templates/`, screenshots in `data/templates/Screenshot/`
- Layout classification via `classify_layout()` in `mcp_server.py`
- Categories: "Title and Subtitle", "Title and Content", "Title, Content and Image", "Title Only", "Two Content", "Image Only", "Content Only"

### Image Generation (image_providers.py)

- Primary: `get_image_from_gurkli()` → https://langchain.gurk.li/generate-image (60s timeout)
- Fallback: `get_image_placeholder()` → loremflickr.com

When style="auto", Agent 2 decides based on content:
- Real industries (automotive, trade) → photorealistic
- Abstract concepts (innovation, strategy) → flat_illustration
- Technical details (architecture, specs) → fine_line

## Implementation Details

### UI Flow (app.py)

Linear flow without sidebar:
1. PDF upload (drag & drop)
2. Language + slide count (3-20)
3. Template selection (grid with screenshots from `data/templates/Screenshot/`)
4. Image settings (style, source, colors)
5. Generate button

### Session State Keys

- `uploaded_files_data` - Current uploaded files
- `saved_pdf_paths` - Paths to saved PDFs
- `cancel_requested` - Generation cancellation flag
- `selected_template_name` - Selected template

### Language Support

Languages: Deutsch, English, Français, Italiano, Español
- Passed through entire pipeline
- Affects LLM prompt and source labels

### LLM Configuration

```python
ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,  # Agent 1: 0.2, Agent 2: 0.3
).with_structured_output(PresentationStructure)
```

### Volume Mapping (Critical)

Both containers must access same files:
- `./data:/app/storage` (agent-app) - PDFs uploaded by user
- `./data:/data` (mcp-server) - Same PDFs for MCP tools

### Cancellation

Check in generation loops:
```python
if st.session_state.get('cancel_requested', False):
    raise Exception("Cancelled by user")
```

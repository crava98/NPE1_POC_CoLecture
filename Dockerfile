FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code - explicit copy to ensure files are included
COPY app.py agent_logic.py ppt_agent.py ppt_engine.py mcp_server.py data_models.py image_providers.py ./
COPY .streamlit/ ./.streamlit/
COPY resource/ ./resource/
COPY data/templates/ /data/templates/
COPY data/templates/ /app/storage/templates/

# Debug: List files to verify copy worked
RUN ls -la /app/ && ls -la /data/templates/

# Create directories for runtime data
RUN mkdir -p /app/storage /uploads

# Expose ports (8501 for Streamlit, 8000 for MCP)
EXPOSE 8501 8000

# Healthcheck (works for Streamlit, MCP server will override)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default: Run Streamlit (MCP server overrides via entrypoint)
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

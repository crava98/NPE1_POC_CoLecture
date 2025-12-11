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

# Application code
COPY *.py ./
COPY .streamlit/ ./.streamlit/

# Create directories for runtime data
RUN mkdir -p /app/storage /data/templates

# Expose ports (8501 for Streamlit, 8000 for MCP)
EXPOSE 8501 8000

# Healthcheck (works for Streamlit, MCP server will override)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default: Run Streamlit (MCP server overrides via entrypoint)
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

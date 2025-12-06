import os
from pypdf import PdfReader
from mcp.server import Server
import mcp.types as types
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request

# 1. Server definieren
mcp = Server("pdf-service")
STORAGE_DIR = "/data"

# 2. Tool Definition
@mcp.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_pdf_file",
            description="Liest den Text aus einer PDF-Datei im Speicher.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Der Name der Datei (z.B. bericht.pdf)"}
                },
                "required": ["filename"]
            }
        )
    ]

# 3. Tool Logik
@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "read_pdf_file":
        raise ValueError(f"Unbekanntes Tool: {name}")

    filename = arguments.get("filename")
    file_path = os.path.join(STORAGE_DIR, filename)
    print(f"MCP Server: Lese Datei {file_path}...")
    
    if not os.path.exists(file_path):
        return [types.TextContent(
            type="text",
            text=f"Fehler: Datei {filename} nicht gefunden. (Pfad geprüft: {file_path})"
        )]
    
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        
        full_text = f"--- INHALT VON {filename} ---\n{text}\n--- ENDE {filename} ---"
        return [types.TextContent(type="text", text=full_text)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Fehler: {str(e)}")]

# 4. Web-Server Setup (DER KRITISCHE TEIL)
sse = SseServerTransport("/messages")

async def handle_sse(request: Request):
    # TRICK: Wir geben eine asynchrone Funktion zurück, statt direkt auszuführen.
    # Starlette führt diese Funktion dann mit (scope, receive, send) aus.
    async def asgi_app(scope, receive, send):
        async with sse.connect_sse(scope, receive, send) as streams:
            await mcp.run(streams[0], streams[1], mcp.create_initialization_options())
    
    return asgi_app

async def handle_messages(request: Request):
    # Auch hier: Wir geben die Logik als ASGI-App zurück.
    async def asgi_app(scope, receive, send):
        await sse.handle_post_message(scope, receive, send)
    
    return asgi_app

# 5. App Routes
app = Starlette(routes=[
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/messages", endpoint=handle_messages, methods=["POST"])
])
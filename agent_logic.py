import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from data_models import PresentationStructure

# MCP Client Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://mcp-server:8000/sse")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.2,
    google_api_key=api_key
)

async def fetch_pdf_content_via_mcp(filenames):
    """
    Verbindet sich mit dem MCP Server und ruft das Tool 'read_pdf_file' auf.
    """
    combined_text = ""
    
    # Verbindung zum MCP Server aufbauen (SSE)
    async with sse_client(mcp_server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            # Initialisierung
            await session.initialize()
            
            # (Optional) Wir könnten fragen: Welche Tools hast du?
            # tools = await session.list_tools()
            
            for fname in filenames:
                filename_only = os.path.basename(fname)
                print(f"--> MCP Client: Frage Server nach {filename_only}...")
                
                try:
                    # HIER passiert der Zugriff: Wir rufen das Tool auf dem Server
                    result = await session.call_tool(
                        "read_pdf_file", 
                        arguments={"filename": filename_only}
                    )
                    
                    # Das Ergebnis ist eine Liste von Content-Blöcken
                    if result.content:
                        combined_text += result.content[0].text + "\n"
                        
                except Exception as e:
                    combined_text += f"\nFehler bei MCP Abruf für {fname}: {e}\n"
                    
    return combined_text

def analyze_pdf_and_plan_ppt(pdf_paths_list, num_slides, language):
    """
    Synchrone Wrapper-Funktion für Streamlit.
    """
    
    # 1. Inhalt via MCP holen (Async Code in Sync ausführen)
    print("--> Starte MCP Client Verbindung...")
    try:
        combined_text = asyncio.run(fetch_pdf_content_via_mcp(pdf_paths_list))
    except Exception as e:
        print(f"MCP Critical Error: {e}")
        combined_text = "Kritischer Fehler: Konnte MCP Server nicht erreichen."

    # 2. Gemini beauftragen (wie gehabt)
    structured_llm = llm.with_structured_output(PresentationStructure)
    
    prompt = f"""
    Du bist ein Experte für professionelle Präsentationen.
    Erstelle eine Struktur für {num_slides} Folien.
    
    SPRACHE: {language}
    
    REGELN:
    1. Fasse dich extrem kurz (Max 3-4 Bullets, max 10 Wörter).
    2. 'unsplashSearchTerms': 3 englische Begriffe.
    
    INHALT VOM MCP SERVER:
    {combined_text[:1000000]}
    """
    
    print(f"--> Sende Anfrage an Gemini...")
    return structured_llm.invoke(prompt)
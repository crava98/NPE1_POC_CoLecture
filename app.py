import streamlit as st
import os
from agent_logic import analyze_pdf_and_plan_ppt
from ppt_engine import generate_ppt

st.set_page_config(page_title="PDF zu PPT Generator", layout="wide")

st.title(" AI Presentation Factory")
st.markdown("Lade PDFs hoch, wähle Sprache & Länge und lass den Agenten arbeiten.")

if not os.path.exists("storage"):
    os.makedirs("storage")

# Initialize session state for uploaded files and cancellation
if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = []
if 'cancel_requested' not in st.session_state:
    st.session_state.cancel_requested = False

# Sidebar
with st.sidebar:
    st.header("Einstellungen")
    
    # NEU: Sprachauswahl
    language = st.selectbox(
        "Sprache der Präsentation",
        ("Deutsch", "English", "Français", "Italiano", "Español")
    )
    
    num_slides = st.slider("Anzahl Folien", min_value=3, max_value=20, value=8)
    st.info(f"Ziel: {num_slides} Folien auf {language}.")

# File uploader
new_uploaded_files = st.file_uploader(
    "PDF Dokumente hier ablegen", 
    type="pdf", 
    accept_multiple_files=True,
    key="file_uploader" # Unique key for the uploader
)

# Process new uploaded files only if they are indeed new
if new_uploaded_files:
    # Check if the list of uploaded files has actually changed to avoid reprocessing on rerun
    if new_uploaded_files != st.session_state.uploaded_files_data:
        st.session_state.uploaded_files_data = new_uploaded_files
        saved_paths = []
        for up_file in st.session_state.uploaded_files_data:
            path = os.path.join("storage", up_file.name)
            with open(path, "wb") as f:
                f.write(up_file.getbuffer())
            saved_paths.append(path)
        st.session_state.saved_pdf_paths = saved_paths
        st.success(f"{len(saved_paths)} Dokumente bereit.")

# Display already uploaded files if any
if st.session_state.uploaded_files_data:
    st.write("Bereits hochgeladene Dokumente:")
    for up_file in st.session_state.uploaded_files_data:
        st.write(f"- {up_file.name}")

# Action buttons
col1, col2 = st.columns(2)

with col1:
    if st.button(" Präsentation erstellen", disabled=not st.session_state.uploaded_files_data):
        st.session_state.cancel_requested = False # Reset cancel flag
        
        status_box = st.status("Agent arbeitet...", expanded=True)
        cancel_button_placeholder = status_box.empty()
        
        def cancel_callback():
            st.session_state.cancel_requested = True
        
        # Display cancel button inside the status box
        cancel_button_placeholder.button(" Vorgang abbrechen", on_click=cancel_callback, key="cancel_process")

        try:
            if st.session_state.cancel_requested:
                status_box.update(label="Vorgang abgebrochen", state="error")
                st.info("Präsentationserstellung wurde abgebrochen.")
                cancel_button_placeholder.empty()
                st.stop() # Stop execution for this run
            
            status_box.write("1. Analysiere PDFs via MCP Server...")
            if st.session_state.cancel_requested: st.stop()

            # Visual Proof for MCP
            mcp_tool_calls_str = ""
            for path in st.session_state.saved_pdf_paths:
                mcp_tool_calls_str += f"- read_pdf_file(filename='{os.path.basename(path)}')\n"

            status_box.markdown("**MCP Tool Calls werden ausgeführt:**")
            status_box.code(mcp_tool_calls_str, language="text")

            # WICHTIG: Hier übergeben wir jetzt die 'language' Variable
            plan = analyze_pdf_and_plan_ppt(st.session_state.saved_pdf_paths, num_slides, language)
            if st.session_state.cancel_requested: st.stop()
            
            status_box.write("2. Struktur erstellt! Generiere Bilder & baue PPT...")
            if st.session_state.cancel_requested: st.stop()

            # Wir geben die Sprache auch an den PPT-Builder weiter (für "Quellen" vs "Sources")
            ppt_path = generate_ppt(plan, language)
            
            status_box.update(label="Fertig!", state="complete", expanded=False)
            cancel_button_placeholder.empty() # Remove cancel button on completion
            st.success("Präsentation erfolgreich erstellt!")
            
            with open(ppt_path, "rb") as f:
                st.download_button(
                    label=" Download PPTX",
                    data=f,
                    file_name=f"praesentation_{language}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
        except Exception as e:
            status_box.update(label="Fehler aufgetreten", state="error")
            cancel_button_placeholder.empty() # Remove cancel button on error
            st.error(f"Details: {e}")
            
with col2:
    if st.button(" Neue Präsentation starten"):
        st.session_state.uploaded_files_data = [] # Clear uploaded files
        st.session_state.saved_pdf_paths = [] # Clear saved paths
        st.session_state.cancel_requested = False # Reset cancel flag
        st.rerun()

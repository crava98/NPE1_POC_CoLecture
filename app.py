import streamlit as st
import os
from agent_logic import analyze_pdf_and_plan_ppt
from ppt_engine import generate_ppt

st.set_page_config(page_title="PDF zu PPT Generator", layout="wide")

st.title("🤖 AI Presentation Factory")
st.markdown("Lade PDFs hoch, wähle Sprache & Länge und lass den Agenten arbeiten.")

if not os.path.exists("storage"):
    os.makedirs("storage")

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

uploaded_files = st.file_uploader("PDF Dokumente hier ablegen", type="pdf", accept_multiple_files=True)

if uploaded_files:
    saved_paths = []
    for up_file in uploaded_files:
        path = os.path.join("storage", up_file.name)
        with open(path, "wb") as f:
            f.write(up_file.getbuffer())
        saved_paths.append(path)
    
    st.success(f"{len(saved_paths)} Dokumente bereit.")

    if st.button("🚀 Präsentation erstellen"):
        
        status_box = st.status("Agent arbeitet...", expanded=True)
        
        try:
            status_box.write(f"1. Analysiere PDFs und plane auf {language}...")
            
            # WICHTIG: Hier übergeben wir jetzt die 'language' Variable
            plan = analyze_pdf_and_plan_ppt(saved_paths, num_slides, language)
            
            status_box.write("2. Struktur erstellt! Generiere Bilder & baue PPT...")
            
            # Wir geben die Sprache auch an den PPT-Builder weiter (für "Quellen" vs "Sources")
            ppt_path = generate_ppt(plan, language)
            
            status_box.update(label="Fertig!", state="complete", expanded=False)
            
            st.success("Präsentation erfolgreich erstellt!")
            
            with open(ppt_path, "rb") as f:
                st.download_button(
                    label="📥 Download PPTX",
                    data=f,
                    file_name=f"praesentation_{language}.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                
        except Exception as e:
            status_box.update(label="Fehler aufgetreten", state="error")
            st.error(f"Details: {e}")

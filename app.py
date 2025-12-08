import streamlit as st
import os
import asyncio
from agent_logic import analyze_pdf_and_plan_ppt
from ppt_agent import generate_ppt_with_agent, get_templates_from_mcp

st.set_page_config(
    page_title="AI Presentation Factory",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS - Modernes Styling mit Glassmorphism
# -----------------------------------------------------------------------------
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ed 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Karten-Styling (Glassmorphism) */
    div.css-card {
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 20px;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    div.css-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    /* Section Headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid #3b82f6;
        display: inline-block;
    }

    .section-number {
        background: linear-gradient(45deg, #3b82f6, #2563eb);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 10px;
    }

    /* Template Card Styling */
    .template-card {
        background: white;
        border-radius: 12px;
        padding: 8px;
        border: 2px solid transparent;
        transition: all 0.2s;
        cursor: pointer;
    }

    .template-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }

    .template-card.selected {
        border-color: #3b82f6;
        background: #eff6ff;
    }

    /* Custom Button Styling */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.4);
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, #2563eb, #1d4ed8);
        box-shadow: 0 6px 12px -1px rgba(59, 130, 246, 0.5);
        transform: translateY(-1px);
    }

    .stButton > button:disabled {
        background: #e5e7eb;
        box-shadow: none;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        text-align: center;
    }

    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }

    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 2px dashed #cbd5e1;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #3b82f6;
    }

    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 10px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #cbd5e1, transparent);
        margin: 24px 0;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HILFSFUNKTIONEN
# -----------------------------------------------------------------------------
def card_start():
    st.markdown('<div class="css-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

def section_header(number, title):
    st.markdown(f'<div class="section-header"><span class="section-number">{number}</span>{title}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# STORAGE & SESSION STATE
# -----------------------------------------------------------------------------
if not os.path.exists("storage"):
    os.makedirs("storage")

if 'uploaded_files_data' not in st.session_state:
    st.session_state.uploaded_files_data = []
if 'saved_pdf_paths' not in st.session_state:
    st.session_state.saved_pdf_paths = []
if 'cancel_requested' not in st.session_state:
    st.session_state.cancel_requested = False
if 'selected_template_name' not in st.session_state:
    st.session_state.selected_template_name = None

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
st.markdown("## AI Presentation Factory")
st.markdown("Erstelle professionelle Präsentationen aus PDF-Dokumenten mit KI-Unterstützung.")

with st.container(border=True):
    st.markdown("""
    **Willkommen in der AI Presentation Factory!**

    Diese Anwendung verwandelt Ihre PDF-Dokumente in wenigen Schritten in eine ansprechende PowerPoint-Präsentation.

    **So einfach geht's:**
    1.  **Dokumente hochladen:** Laden Sie ein oder mehrere PDF-Dateien hoch, die als Grundlage für die Präsentation dienen sollen.
    2.  **Anpassen:** Wählen Sie die gewünschte Sprache, die Anzahl der Folien und ein passendes Design-Template aus.
    3.  **Generieren:** Klicken Sie auf "Präsentation erstellen" und lassen Sie die KI die Arbeit machen.

    Das Ergebnis ist eine fertige `.pptx`-Datei, die Sie herunterladen und weiter bearbeiten können.
    """)

st.markdown("---")

# =============================================================================
# SCHRITT 1: PDF-Dateien hochladen
# =============================================================================
card_start()
section_header("1", "PDF-Dokumente hochladen")

new_uploaded_files = st.file_uploader(
    "Ziehe deine PDF-Dateien hierher oder klicke zum Auswählen",
    type="pdf",
    accept_multiple_files=True,
    key="file_uploader"
)

if new_uploaded_files:
    if new_uploaded_files != st.session_state.uploaded_files_data:
        st.session_state.uploaded_files_data = new_uploaded_files
        saved_paths = []
        for up_file in st.session_state.uploaded_files_data:
            path = os.path.join("storage", up_file.name)
            with open(path, "wb") as f:
                f.write(up_file.getbuffer())
            saved_paths.append(path)
        st.session_state.saved_pdf_paths = saved_paths

if st.session_state.uploaded_files_data:
    st.success(f"{len(st.session_state.uploaded_files_data)} Dokument(e) bereit")
    with st.expander("Hochgeladene Dateien anzeigen"):
        for up_file in st.session_state.uploaded_files_data:
            st.write(f"- {up_file.name}")

card_end()

# =============================================================================
# SCHRITT 2: Sprache und Folienanzahl
# =============================================================================
card_start()
section_header("2", "Sprache und Umfang")

col1, col2 = st.columns(2)

with col1:
    language = st.selectbox(
        "Sprache der Präsentation",
        ("Deutsch", "English", "Français", "Italiano", "Español"),
        help="In welcher Sprache soll die Präsentation erstellt werden?"
    )

with col2:
    num_slides = st.slider(
        "Anzahl Folien",
        min_value=3,
        max_value=20,
        value=8,
        help="Wie viele Folien soll die Präsentation haben?"
    )

card_end()

# =============================================================================
# SCHRITT 3: Template auswählen
# =============================================================================
card_start()
section_header("3", "Design-Template auswählen")

try:
    templates_data = asyncio.run(get_templates_from_mcp())

    if templates_data and templates_data.get("templates"):
        templates = templates_data["templates"]
        screenshot_base = "storage/templates/Screeenshot"

        cols = st.columns(4)

        for idx, template in enumerate(templates):
            col = cols[idx % 4]
            template_base_name = template.replace(".pptx", "").replace(".potx", "")
            screenshot_path = f"{screenshot_base}/{template_base_name}.png"

            with col:
                is_selected = (st.session_state.selected_template_name == template)

                if os.path.exists(screenshot_path):
                    st.image(screenshot_path, width="stretch")
                else:
                    st.info("Keine Vorschau")

                short_name = template_base_name[:20] + "..." if len(template_base_name) > 20 else template_base_name

                if st.button(
                    f"{'> ' if is_selected else ''}{short_name}",
                    key=f"template_{idx}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    if st.session_state.selected_template_name == template:
                        st.session_state.selected_template_name = None
                    else:
                        st.session_state.selected_template_name = template
                    st.rerun()

        if st.session_state.selected_template_name:
            st.success(f"Template: {st.session_state.selected_template_name.replace('.pptx', '')}")
        else:
            st.info("Kein Template ausgewählt - Standard-Design wird verwendet")
    else:
        st.warning("Keine Templates verfügbar. Stelle sicher, dass der MCP Server läuft.")
except Exception as e:
    st.error(f"Fehler beim Laden der Templates: {e}")

selected_template_name = st.session_state.selected_template_name

card_end()

# =============================================================================
# SCHRITT 4: Bildeinstellungen
# =============================================================================
card_start()
section_header("4", "Bild-Einstellungen")

col1, col2, col3 = st.columns(3)

with col1:
    image_style = st.selectbox(
        "Bildstil",
        ("auto", "flat_illustration", "fine_line", "photorealistic"),
        index=0,
        help="auto = Agent entscheidet basierend auf Inhalt"
    )
    st.caption({
        "auto": "Agent wählt passenden Stil",
        "flat_illustration": "Flache Illustrationen",
        "fine_line": "Feine Linienzeichnungen",
        "photorealistic": "Fotorealistische Bilder"
    }.get(image_style, ""))

with col2:
    image_mode = st.selectbox(
        "Bildquelle",
        ("auto", "stock_only", "ai_only"),
        index=0,
        help="Woher sollen die Bilder kommen?"
    )
    st.caption({
        "auto": "Automatische Auswahl",
        "stock_only": "Nur Stock-Fotos",
        "ai_only": "Nur KI-generiert"
    }.get(image_mode, ""))

with col3:
    use_custom_colors = st.checkbox(
        "Eigene Farben",
        value=False,
        help="Wenn deaktiviert, wählt der Agent passende Farben"
    )

    image_colors = None
    if use_custom_colors:
        col_a, col_b = st.columns(2)
        with col_a:
            primary_color = st.color_picker("Primär", "#0066CC")
        with col_b:
            secondary_color = st.color_picker("Sekundär", "#00CC66")
        image_colors = {"primary": primary_color, "secondary": secondary_color}
    else:
        st.caption("Agent wählt Farben automatisch")

card_end()

# =============================================================================
# SCHRITT 5: Präsentation erstellen
# =============================================================================
card_start()
section_header("5", "Präsentation generieren")

if st.session_state.uploaded_files_data:
    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.metric("Dokumente", len(st.session_state.uploaded_files_data))
    with summary_cols[1]:
        st.metric("Folien", num_slides)
    with summary_cols[2]:
        st.metric("Sprache", language)
    with summary_cols[3]:
        template_display = st.session_state.selected_template_name
        if template_display:
            template_display = template_display.replace(".pptx", "")[:15] + "..."
        else:
            template_display = "Standard"
        st.metric("Template", template_display)

    st.markdown("")

col1, col2 = st.columns([3, 1])

with col1:
    generate_button = st.button(
        "Präsentation erstellen",
        disabled=not st.session_state.uploaded_files_data,
        use_container_width=True,
        type="primary"
    )

with col2:
    if st.button("Zurücksetzen", use_container_width=True):
        st.session_state.uploaded_files_data = []
        st.session_state.saved_pdf_paths = []
        st.session_state.cancel_requested = False
        st.session_state.selected_template_name = None
        st.rerun()

card_end()

# Generierung starten
if generate_button:
    st.session_state.cancel_requested = False

    status_box = st.status("Agent arbeitet...", expanded=True)
    cancel_placeholder = status_box.empty()

    def cancel_callback():
        st.session_state.cancel_requested = True

    cancel_placeholder.button("Abbrechen", on_click=cancel_callback, key="cancel_btn")

    try:
        if st.session_state.cancel_requested:
            status_box.update(label="Abgebrochen", state="error")
            st.stop()

        status_box.write("Agent 1 analysiert PDFs und erstellt Präsentationsplan...")
        if st.session_state.cancel_requested:
            st.stop()

        plan = analyze_pdf_and_plan_ppt(st.session_state.saved_pdf_paths, num_slides, language)
        if st.session_state.cancel_requested:
            st.stop()

        status_box.write("Agent 2 generiert PowerPoint mit Bildern...")

        ppt_path = generate_ppt_with_agent(
            plan,
            language,
            template_name=selected_template_name,
            image_style=image_style,
            image_mode=image_mode,
            image_colors=image_colors
        )

        if st.session_state.cancel_requested:
            st.stop()

        status_box.update(label="Fertig!", state="complete", expanded=False)
        cancel_placeholder.empty()

        st.success("Präsentation erfolgreich erstellt!")

        with open(ppt_path, "rb") as f:
            st.download_button(
                label="Download PPTX",
                data=f,
                file_name=f"praesentation_{language}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )

    except Exception as e:
        status_box.update(label="Fehler", state="error")
        cancel_placeholder.empty()
        st.error(f"Fehler: {e}")

# Architektur-Diagramm am Ende
st.markdown("---")
with st.expander("Architektur und Ablauf"):
    st.image("resource/Sequenzdiagram PoC.png", caption="AI Presentation Factory - Sequenzdiagramm", width="stretch")

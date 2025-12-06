import os
from pptx import Presentation
from pptx.util import Inches, Pt
from image_providers import get_image_from_gurkli

def generate_ppt(presentation_data, language="Deutsch"):
    # Template Logik
    if os.path.exists("template.pptx"):
        prs = Presentation("template.pptx")
    else:
        prs = Presentation()
        prs.slide_width = Inches(16)
        prs.slide_height = Inches(9)

    labels = {
        "Deutsch": "Quellen", "English": "Sources", 
        "Français": "Sources", "Italiano": "Fonti", "Español": "Fuentes"
    }
    source_label = labels.get(language, "Sources")

    for slide_data in presentation_data.slides:
        # Layout Title + Content
        layout = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
        slide = prs.slides.add_slide(layout)
        
        # Titel
        if slide.shapes.title:
            slide.shapes.title.text = slide_data.title
        
        # Text Body
        tf = None
        for shape in slide.placeholders:
            if shape.placeholder_format.idx == 1:
                tf = shape.text_frame
                break
        
        if tf:
            tf.clear()
            if not os.path.exists("template.pptx"):
                tf.width = Inches(8.5)

            for item in slide_data.bullets:
                p = tf.add_paragraph()
                p.text = item.bullet
                p.level = 0
                if p.font: p.font.size = Pt(18)

                for sub in item.sub:
                    ps = tf.add_paragraph()
                    ps.text = sub
                    ps.level = 1
                    if ps.font: ps.font.size = Pt(16)

        # BILD EINFÜGEN (HIER IST DIE ÄNDERUNG)
        if slide_data.unsplashSearchTerms:
            # Wir übergeben jetzt das GANZE slide_data Objekt
            image_path = get_image_from_gurkli(slide_data)
            
            if image_path:
                left = Inches(10.0) 
                top = Inches(2.0)
                width = Inches(5.5)
                try:
                    slide.shapes.add_picture(image_path, left, top, width=width)
                except Exception as e:
                    print(f"PPT Bild Fehler: {e}")

        # Quellen
        if slide_data.sources and slide.has_notes_slide:
            notes_slide = slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            sources_text = f"{source_label}:\n" + "\n".join([f"- {s.documentId} (p. {s.pageNumber})" for s in slide_data.sources])
            text_frame.text = sources_text

    output_path = os.path.join("storage", f"generated_presentation_{language}.pptx")
    prs.save(output_path)
    return output_path
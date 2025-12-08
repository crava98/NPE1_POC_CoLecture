#!/usr/bin/env python3
"""
Test das neue professionelle Design ohne Bilder.
"""
from data_models import PresentationStructure, CustomerSlide, BulletItem, Source
from ppt_engine import generate_ppt

# Erstelle Test-Daten
test_presentation = PresentationStructure(
    slides=[
        CustomerSlide(
            title="Modern Corporate Präsentation",
            sources=[],
            unsplashSearchTerms=["business", "corporate", "office"],
            bullets=[
                BulletItem(
                    bullet="Professionelles Design mit Navy Blue",
                    sub=["Moderne Farbpalette", "Klare Typografie"]
                ),
                BulletItem(
                    bullet="Verkaufsfertige Qualität",
                    sub=["Visuelle Akzente", "Geometrische Elemente"]
                )
            ]
        ),
        CustomerSlide(
            title="Hauptfeatures der Präsentation",
            sources=[Source(documentId="Test.pdf", pageNumber="1")],
            unsplashSearchTerms=["technology", "innovation"],
            bullets=[
                BulletItem(
                    bullet="Navy Blue Akzentfarben (#003366)",
                    sub=["Top Accent Bar", "Vertikale Linien"]
                ),
                BulletItem(
                    bullet="Light Blue Highlights (#E6F0FF)",
                    sub=["Subtile Hintergründe", "Moderne Ästhetik"]
                ),
                BulletItem(
                    bullet="Professionelle Typografie",
                    sub=["Calibri Font", "Optimale Schriftgrößen"]
                )
            ]
        ),
        CustomerSlide(
            title="Zusätzliche Design-Elemente",
            sources=[],
            unsplashSearchTerms=["design", "modern", "professional"],
            bullets=[
                BulletItem(
                    bullet="Slide-Nummern automatisch",
                    sub=[]
                ),
                BulletItem(
                    bullet="Visuelle Platzhalter für Bilder",
                    sub=["Wenn API noch nicht verfügbar"]
                ),
                BulletItem(
                    bullet="Konsistente Layouts",
                    sub=["Title Slide und Content Slides"]
                )
            ]
        )
    ]
)

print("Generiere professionelle Test-Präsentation...")
print("-" * 60)

# Generiere ohne Template (zeigt reines Code-Design)
output_path = generate_ppt(test_presentation, language="Deutsch", template_path=None)

print("-" * 60)
print(f"✓ Präsentation erstellt: {output_path}")
print("\nÖffne die Datei, um das neue professionelle Design zu sehen!")
print("\nDesign-Features:")
print("  • Navy Blue Top Accent Bar auf jeder Slide")
print("  • Vertikale Akzentlinien (Links)")
print("  • Professionelle Farbpalette (#003366, #E6F0FF)")
print("  • Moderne Typografie mit Calibri")
print("  • Slide-Nummern unten rechts")
print("  • Visuelle Platzhalter für Bilder")

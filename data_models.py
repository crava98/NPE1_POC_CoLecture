from typing import List, Optional
from pydantic import BaseModel, Field

class Source(BaseModel):
    documentId: str = Field(description="Name der Quelldatei")
    pageNumber: str = Field(description="Geschätzte Seitennummer oder Abschnitt")

class BulletItem(BaseModel):
    bullet: str = Field(description="Der Hauptpunkt (Level 0)")
    # WICHTIGE ÄNDERUNG HIER: default=[] hinzufügen
    # Das erlaubt Gemini, das Feld wegzulassen, ohne dass es abstürzt.
    sub: List[str] = Field(default=[], description="Unterpunkte (Level 1, max 3)")

class CustomerSlide(BaseModel):
    title: str = Field(description="Titel der Folie")
    # Auch hier ist default=[] sicherer, falls mal keine Quellen da sind
    sources: List[Source] = Field(default=[], description="Quellenangaben für diese Folie")
    # Auch hier default=[]
    unsplashSearchTerms: List[str] = Field(default=[], description="3 englische Schlagwörter für die Bildsuche")
    bullets: List[BulletItem] = Field(description="Liste der Inhalte")

class PresentationStructure(BaseModel):
    slides: List[CustomerSlide]
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

class Source(BaseModel):
    documentId: str = Field(description="Name der Quelldatei")
    pageNumber: str = Field(description="Geschätzte Seitennummer oder Abschnitt")

class BulletItem(BaseModel):
    bullet: str = Field(description="Der Hauptpunkt (Level 0)")
    # WICHTIGE ÄNDERUNG HIER: default=[] hinzufügen
    # Das erlaubt Gemini, das Feld wegzulassen, ohne dass es abstürzt.
    sub: List[str] = Field(default=[], description="Unterpunkte (Level 1, max 3)")

class ImageColors(BaseModel):
    """Farbschema für die Bildgenerierung"""
    primary: str = Field(default="#0066CC", description="Primärfarbe als Hex-Code")
    secondary: str = Field(default="#00CC66", description="Sekundärfarbe als Hex-Code")

class CustomerSlide(BaseModel):
    title: str = Field(description="Titel der Folie")
    # Auch hier ist default=[] sicherer, falls mal keine Quellen da sind
    sources: List[Source] = Field(default=[], description="Quellenangaben für diese Folie")
    # Auch hier default=[]
    unsplashSearchTerms: List[str] = Field(default=[], description="3 englische Schlagwörter für die Bildsuche")
    bullets: List[BulletItem] = Field(description="Liste der Inhalte")

    # Neue Felder für Gurkli-Bildgenerierung
    ImageKeywords: Optional[List[str]] = Field(default=None, description="Optionale Keywords für Bildsuche, überschreibt unsplashSearchTerms")
    style: Literal["auto", "flat_illustration", "fine_line", "photorealistic"] = Field(default="auto", description="Bildstil: auto (Agent entscheidet), flat_illustration, fine_line, oder photorealistic")
    image_mode: Literal["stock_only", "ai_only", "auto"] = Field(default="auto", description="Bildquelle: stock_only, ai_only oder auto")
    ai_model: Literal["auto", "flux", "banana"] = Field(default="auto", description="AI-Modell: auto (=flux), flux, oder banana/imagen")
    colors: Optional[ImageColors] = Field(default=None, description="Farbschema für Bildgenerierung")

class PresentationStructure(BaseModel):
    slides: List[CustomerSlide]
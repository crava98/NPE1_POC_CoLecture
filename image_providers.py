import os
import requests
import json
import uuid

# Webhook & Token aus .env laden
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
N8N_AUTH_TOKEN = os.environ.get("N8N_AUTH_TOKEN")

def get_local_error_placeholder():
    """
    Gibt den Pfad zum lokalen Fallback-Bild zurück.
    """
    placeholder_path = "resource/Gemini_Generated_Image_yj7jhnyj7jhnyj7j.png"
    print(f"--> API-Fehler. Verwende lokalen Platzhalter: {placeholder_path}")
    # Prüfen, ob die Datei existiert, um Fehler zu vermeiden
    if os.path.exists(placeholder_path):
        return placeholder_path
    # Wenn selbst der lokale Platzhalter fehlt, geben wir nichts zurück
    print(f"--> WARNUNG: Lokaler Platzhalter nicht gefunden unter {placeholder_path}")
    return None


def get_image_from_gurkli(slide_data):
    """
    Sendet das KOMPLETTE Slide-Objekt als JSON an die gurk.li/generate-image API.
    Erwartet ein JSON mit einer URL zum Bild als Antwort zurück.

    Unterstützte Felder im slide_data:
    - title: Titel der Folie
    - bullets: Liste der Bullet-Punkte
    - ImageKeywords: Optional, überschreibt unsplashSearchTerms für Bildsuche
    - style: Liste von Stil-Präferenzen (z.B. ["flat_illustration", "minimal"])
    - image_mode: "stock_only" | "ai_only" | "auto"
    - ai_model: "auto" (=flux) | "flux" | "banana"
    - colors: {"primary": "#hex", "secondary": "#hex"}
    """
    GURKLI_API_URL = "https://langchain.gurk.li/generate-image"

    # Convert BulletItem objects to dictionaries
    bullets_as_dicts = [b.model_dump() for b in slide_data.bullets]
    # Convert Source objects to dictionaries
    sources_as_dicts = [s.model_dump() for s in slide_data.sources]

    # ImageKeywords überschreibt unsplashSearchTerms wenn vorhanden
    image_keywords = slide_data.ImageKeywords if slide_data.ImageKeywords else slide_data.unsplashSearchTerms

    # Colors aus slide_data oder Default-Werte
    colors_dict = None
    if slide_data.colors:
        colors_dict = slide_data.colors.model_dump()
    else:
        colors_dict = {"primary": "#0066CC", "secondary": "#00CC66"}

    payload = {
        "title": slide_data.title,
        "sources": sources_as_dicts,
        "bullets": bullets_as_dicts,
        "ImageKeywords": image_keywords,
        "style": slide_data.style,
        "image_mode": slide_data.image_mode,
        "ai_model": slide_data.ai_model,
        "colors": colors_dict
    }

    print("\n" + "="*40)
    print(f"--> DEBUG: SENDE DIESES JSON AN gurk.li:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("="*40 + "\n")

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            GURKLI_API_URL,
            data=json.dumps(payload),
            headers=headers,
            timeout=60 # Increased timeout for image generation
        )

        if response.status_code == 200:
            print("--> gurk.li Erfolg! JSON-Antwort empfangen.")
            response_data = response.json()
            
            image_url = response_data.get("url")
            if not image_url:
                print("gurk.li Fehler: Kein 'url' Feld im JSON gefunden.")
                return get_local_error_placeholder()

            print(f"--> Lade Bild von URL: {image_url[:50]}...")
            image_response = requests.get(image_url, timeout=30)

            if image_response.status_code == 200:
                safe_name = "slide_img"
                if image_keywords:
                    safe_name = "".join(x for x in image_keywords[0] if x.isalnum())

                filename = f"img_{safe_name}_gurkli.jpg"
                path = os.path.join("storage", filename)

                with open(path, "wb") as f:
                    f.write(image_response.content)
                return path
            else:
                print(f"Fehler beim Download des Bildes von gurk.li: {image_response.status_code}")
                return get_local_error_placeholder()
        else:
            print(f"gurk.li Fehler: {response.status_code} - {response.text}")
            return get_local_error_placeholder()

    except Exception as e:
        print(f"gurk.li Exception: {e}")
        return get_local_error_placeholder()
import os
import requests
import json
import uuid

# Webhook & Token aus .env laden
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
N8N_AUTH_TOKEN = os.environ.get("N8N_AUTH_TOKEN")

def get_image_placeholder(terms):
    """Fallback: Lädt ein Platzhalterbild von loremflickr."""
    search_term = "business"
    if terms and len(terms) > 0:
        search_term = terms[0]
    
    url = f"https://loremflickr.com/800/450/{search_term},work"
    print(f"--> Hole Platzhalter-Bild für: {search_term}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            filename = f"placeholder_{search_term}.jpg"
            path = os.path.join("storage", filename)
            with open(path, "wb") as f:
                f.write(response.content)
            return path
    except Exception:
        pass
    return None

def get_image_from_n8n(slide_data):
    """
    Sendet das KOMPLETTE Slide-Objekt als JSON an n8n.
    Erwartet ein JSON mit einer URL zum Bild als Antwort zurück.
    """
    # 1. Prüfen ob URL da ist
    if not N8N_WEBHOOK_URL:
        print("n8n URL fehlt -> Platzhalter.")
        return get_image_placeholder(slide_data.unsplashSearchTerms)

    # 2. Das Payload bauen (Das volle Objekt!)
    payload = slide_data.model_dump() # type: ignore
    
    # NEU: Korrelations-ID für Tracing hinzufügen
    correlation_id = str(uuid.uuid4())
    payload['correlation_id'] = correlation_id
    print(f"--> Korrelations-ID für n8n-Trace: {correlation_id}")

    # --- DEBUGGING: ZEIGT DIR DAS JSON IM TERMINAL AN ---
    print("\n" + "="*40)
    print(f"--> DEBUG: SENDE DIESES JSON AN N8N:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("="*40 + "\n")
    # ----------------------------------------------------

    headers = {
        "hslu": N8N_AUTH_TOKEN,
        "Content-Type": "application/json" 
    }

    try:
        # Wir senden JSON und erwarten JSON zurück
        response = requests.post(
            N8N_WEBHOOK_URL,
            data=json.dumps(payload), # Manuell enkodieren
            headers=headers,
            timeout=45
        )

        # 3. Antwort verarbeiten
        if response.status_code == 200:
            print("--> n8n Erfolg! JSON-Antwort empfangen.")
            
            # JSON parsen
            response_data = response.json()
            
            # URL extrahieren
            image_url = response_data[0].get("url")
            if not image_url:
                print("n8n Fehler: Kein 'url' Feld im JSON gefunden.")
                return get_image_placeholder(slide_data.unsplashSearchTerms)

            # Bild von der URL herunterladen
            print(f"--> Lade Bild von URL: {image_url[:50]}...")
            image_response = requests.get(image_url, timeout=30)
            
            if image_response.status_code == 200:
                # Dateinamen basteln
                terms = slide_data.unsplashSearchTerms
                safe_name = "slide_img"
                if terms:
                    safe_name = "".join(x for x in terms[0] if x.isalnum())
                
                filename = f"img_{safe_name}.jpg"
                path = os.path.join("storage", filename)

                # Das Bild speichern (Binary Content)
                with open(path, "wb") as f:
                    f.write(image_response.content)
                return path
            else:
                print(f"Fehler beim Download des Bildes: {image_response.status_code}")
                return get_image_placeholder(slide_data.unsplashSearchTerms)
            
        else:
            print(f"n8n Fehler: {response.status_code} - {response.text}")
            return get_image_placeholder(slide_data.unsplashSearchTerms)

    except Exception as e:
        print(f"n8n Exception: {e}")
        return get_image_placeholder(slide_data.unsplashSearchTerms)

def get_image_from_gurkli(slide_data):
    """
    Sendet das KOMPLETTE Slide-Objekt als JSON an die gurk.li/generate-image API.
    Erwartet ein JSON mit einer URL zum Bild als Antwort zurück.
    """
    GURKLI_API_URL = "https://langchain.gurk.li/generate-image"

    # Hardcoded values for testing as per request
    style_preference = ["modern", "minimal", "professional"]
    image_mode_preference = "ai_only"
    ai_model_preference = "banana"
    colors_preference = {
        "primary": "#0066CC",
        "secondary": "#00CC66"
    }

    # Convert BulletItem objects to dictionaries
    bullets_as_dicts = [b.model_dump() for b in slide_data.bullets]
    # Convert Source objects to dictionaries
    sources_as_dicts = [s.model_dump() for s in slide_data.sources]

    payload = {
        "title": slide_data.title,
        "sources": sources_as_dicts,
        "unsplashSearchTerms": slide_data.unsplashSearchTerms,
        "bullets": bullets_as_dicts,
        "image_mode": image_mode_preference,
        "ai_model": ai_model_preference,
        "style": style_preference,
        "colors": colors_preference
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
                return get_image_placeholder(slide_data.unsplashSearchTerms)

            print(f"--> Lade Bild von URL: {image_url[:50]}...")
            image_response = requests.get(image_url, timeout=30)
            
            if image_response.status_code == 200:
                terms = slide_data.unsplashSearchTerms
                safe_name = "slide_img"
                if terms:
                    safe_name = "".join(x for x in terms[0] if x.isalnum())
                
                filename = f"img_{safe_name}_gurkli.jpg"
                path = os.path.join("storage", filename)

                with open(path, "wb") as f:
                    f.write(image_response.content)
                return path
            else:
                print(f"Fehler beim Download des Bildes von gurk.li: {image_response.status_code}")
                return get_image_placeholder(slide_data.unsplashSearchTerms)
        else:
            print(f"gurk.li Fehler: {response.status_code} - {response.text}")
            return get_image_placeholder(slide_data.unsplashSearchTerms)

    except Exception as e:
        print(f"gurk.li Exception: {e}")
        return get_image_placeholder(slide_data.unsplashSearchTerms)

import csv
import time
import re
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Configurazione
INPUT_FILE = "assets/data/festivals.csv"
OUTPUT_FILE = "assets/data/festivals_geocoded.csv"

geolocator = Nominatim(user_agent="science_festivals_map")

def clean_tags(value):
    """Pulisce i tag: rimuove duplicati, spazi extra, normalizza separatori."""
    if not value:
        return ""
    # Rimuove virgolette esterne
    value = value.strip().strip('"')
    # Sostituisce "science; science" (duplicato comune) con "science"
    value = re.sub(r'\bscience;\s*science\b', 'science', value)
    # Divide per punto e virgola
    tags = [t.strip().lower() for t in value.split(";")]
    # Rimuove duplicati mantenendo l'ordine
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag and tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    return ";".join(unique_tags)

def clean_field(value):
    """Rimuove spazi iniziali e finali da un campo."""
    return value.strip() if value else ""

def geocode(address, retries=3):
    """Converte un indirizzo in coordinate lat/lon."""
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return round(location.latitude, 6), round(location.longitude, 6)
            else:
                return None, None
        except GeocoderTimedOut:
            print(f"  Timeout per: {address}, tentativo {attempt+1}/{retries}")
            time.sleep(2)
        except GeocoderServiceError as e:
            print(f"  Errore servizio: {e}")
            return None, None
    return None, None

def main():
    results = []
    failed = []

    with open(INPUT_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    total = len(rows)
    print(f"Trovati {total} festival. Inizio geocoding...\n")

    for i, row in enumerate(rows):
        name = clean_field(row.get("name", ""))
        location = clean_field(row.get("location", ""))
        country = clean_field(row.get("country", ""))
        theme = clean_tags(row.get("theme", ""))
        period = clean_field(row.get("period", ""))
        public = clean_field(row.get("public", "").strip('"'))
        website = clean_field(row.get("website", ""))
        organization = clean_field(row.get("organization", ""))
        contacts = clean_field(row.get("contacts", ""))

        print(f"[{i+1}/{total}] {name}")

        lat, lon = geocode(location)

        if lat is None:
            # Fallback: prova con solo città e paese
            fallback = f"{country}"
            print(f"  Fallback con: {fallback}")
            lat, lon = geocode(fallback)

        if lat is None:
            failed.append(name)
            print(f"  ❌ Non trovato")
        else:
            print(f"  ✅ {lat}, {lon}")

        results.append({
            "name": name,
            "website": website,
            "country": country,
            "location": location,
            "theme": theme,
            "period": period,
            "public": public,
            "organization": organization,
            "contacts": contacts,
            "lat": lat if lat else "",
            "lon": lon if lon else ""
        })

        # Pausa per rispettare i limiti di Nominatim (1 req/sec)
        time.sleep(1.1)

    # Salva il CSV risultante
    fieldnames = ["name", "website", "country", "location", "theme", "period", "public", "organization", "contacts", "lat", "lon"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ File salvato in: {OUTPUT_FILE}")
    print(f"✅ Geocodificati con successo: {total - len(failed)}/{total}")

    if failed:
        print(f"\n❌ Non geocodificati ({len(failed)}):")
        for name in failed:
            print(f"  - {name}")
        print("\nPer questi festival aggiungi le coordinate manualmente.")

if __name__ == "__main__":
    main()

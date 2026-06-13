import csv
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Configurazione
INPUT_FILE = "assets/data/festivals.csv"
OUTPUT_CSV = "assets/data/festivals_geocoded.csv"

geolocator = Nominatim(user_agent="science_festivals_map")

def geocode(address, retries=3):
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return round(location.latitude, 6), round(location.longitude, 6)
            else:
                return None, None
        except GeocoderTimedOut:
            print(f"  Timeout, tentativo {attempt+1}/{retries}")
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
        name = row.get("name", "").strip()
        location = row.get("location", "").strip()
        country = row.get("country", "").strip()

        print(f"[{i+1}/{total}] {name}")

        lat, lon = geocode(location)

        if lat is None:
            print(f"  Fallback con paese: {country}")
            lat, lon = geocode(country)

        if lat is None:
            failed.append(name)
            print(f"  ❌ Non trovato")
        else:
            print(f"  ✅ {lat}, {lon}")

        results.append({
            "name": name,
            "website": row.get("website", "").strip(),
            "country": country,
            "location": location,
            "theme": row.get("theme", "").strip(),
            "tags": row.get("tags", "").strip(),
            "period": row.get("period", "").strip(),
            "public": row.get("public", "").strip(),
            "organization": row.get("organization", "").strip(),
            "contacts": row.get("contacts", "").strip(),
            "lat": lat if lat else "",
            "lon": lon if lon else "",
        })

        time.sleep(1.1)

    fieldnames = ["name", "website", "country", "location", "theme", "tags", "period", "public", "organization", "contacts", "lat", "lon"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ File salvato in: {OUTPUT_CSV}")
    print(f"✅ Geocodificati: {total - len(failed)}/{total}")

    if failed:
        print(f"\n❌ Non geocodificati ({len(failed)}):")
        for name in failed:
            print(f"  - {name}")

if __name__ == "__main__":
    main()

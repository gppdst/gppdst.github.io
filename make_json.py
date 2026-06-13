import csv
import json

INPUT_FILE = "assets/data/festivals_geocoded.csv"
OUTPUT_FILE = "assets/data/festivals.json"

results = []

with open(INPUT_FILE, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        try:
            lat = float(row["lat"])
            lon = float(row["lon"])
            if not (30 <= lat <= 72 and -10 <= lon <= 40):
                print(f"  ⚠️  Coordinate fuori range: {row['name']} ({lat}, {lon})")
                continue
        except:
            print(f"  ⚠️  Coordinate mancanti: {row['name']}")
            continue

        results.append({
            "name": row["name"].strip(),
            "website": row["website"].strip(),
            "country": row["country"].strip(),
            "location": row["location"].strip(),
            "theme": row["theme"].strip(),
            "tags": [t.strip() for t in row["tags"].split(";") if t.strip()],
            "period": row["period"].strip(),
            "public": [p.strip() for p in row["public"].strip().strip('"').split(";") if p.strip()],
            "organization": row["organization"].strip(),
            "contacts": row["contacts"].strip(),
            "lat": lat,
            "lon": lon,
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✅ {len(results)} festival esportati in {OUTPUT_FILE}")

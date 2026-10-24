# Generate Real Training Data
# Yeh file _data/cities.py ki saari cities pe real satellite data nikalti hai
# Output: ek CSV jisse classify_city.py aur physics_ml.py REAL data se train ho sakein

import sys
import os
import json

sys.path.append(os.path.abspath('../_ai_engine/drivers'))
from driver_analysis import extract_all_drivers
from cities import INDIAN_CITIES


def generate_dataset(output_path='training_data.json'):
    """
    Saari cities (cities.py mein) pe real satellite data nikalo
    aur ek file mein save karo
    
    Yeh data baad mein classify_city.py aur physics_ml.py
    train karne ke liye use hoga - HARDCODED nahi, REAL hai
    """
    dataset = []

    total = len(INDIAN_CITIES)
    for idx, (city_name, info) in enumerate(INDIAN_CITIES.items(), 1):
        print(f"[{idx}/{total}] {city_name} ka data nikal rahe hain...")

        try:
            drivers = extract_all_drivers(
                longitude=info['lon'],
                latitude=info['lat']
            )

            record = {
                'city': city_name,
                'state': info['state'],
                'climate_label': info['climate'],  # ground truth - cities.py se
                'lst': drivers['lst'],
                'ndvi': drivers['vegetation_ndvi'],
                'ndbi': drivers['builtup_ndbi'],
                'ndwi': drivers['water_ndwi'],
                'bsi': drivers['baresoil_bsi'],
            }

            dataset.append(record)
            print(f"    LST={record['lst']}°C, NDVI={record['ndvi']}, NDBI={record['ndbi']}")

        except Exception as e:
            print(f"    SKIP - error: {e}")
            continue

    # Save karo JSON mein
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)

    print(f"\nDone! {len(dataset)} cities ka REAL data save hua: {output_path}")
    return dataset


def load_dataset(path='training_data.json'):
    """Saved dataset load karo"""
    with open(path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    print("Real satellite data generate kar rahe hain saari cities ke liye...")
    print("Yeh 2-3 minute le sakta hai (20 cities)\n")

    dataset = generate_dataset()

    print("\nSample records:")
    for record in dataset[:3]:
        print(f"  {record}")
import os
import re
import glob
import csv

try:
    from supabase import create_client
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'supabase'])
    from supabase import create_client

SUPABASE_URL = "https://sitmziehzhvqeftydtdr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdG16aWVoemh2cWVmdHlkdGRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDY3OTg2NywiZXhwIjoyMDk2MjU1ODY3fQ.BwH-Hm3o2TidtoueJDPtVkYWvd1rwh2Ljy_IUIHbDy0"

# Dossier contenant tous les CSV
CSV_DIR = r"C:\Users\Mebrouk Hassan\Desktop\infodigcats"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================
# Mapping coordonnees → ville
# ============================================================
COORD_CITY_MAP = [
    (-33.87, 151.21, 'Sydney',     'NSW'),
    (-37.81, 144.96, 'Melbourne',  'VIC'),
    (-27.47, 153.03, 'Brisbane',   'QLD'),
    (-31.95, 115.86, 'Perth',      'WA'),
    (-34.93, 138.60, 'Adelaide',   'SA'),
    (-27.99, 153.43, 'Gold Coast', 'QLD'),
    (-35.28, 149.13, 'Canberra',   'ACT'),
    (-42.88, 147.33, 'Hobart',     'TAS'),
    (-12.46, 130.85, 'Darwin',     'NT'),
]

def detect_city_state(lat, lng):
    try:
        lat, lng = float(lat), float(lng)
    except Exception:
        return None, None
    best, best_dist = None, 9999
    for clat, clng, city, state in COORD_CITY_MAP:
        dist = ((lat - clat)**2 + (lng - clng)**2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best = (city, state)
    if best_dist < 2.0:
        return best
    return None, None

# ============================================================
# Mapping category CSV → category Supabase
# ============================================================
CATEGORY_MAP = {
    'vétérinaire': 'vet',
    'veterinaire': 'vet',
    'clinique vétérinaire': 'vet',
    'clinique veterinaire': 'vet',
    'urgences vétérinaires': 'vet',
    'urgences veterinaires': 'vet',
    'toiletteur': 'groomer',
    'groomer': 'groomer',
    'refuge': 'shelter',
    'shelter': 'shelter',
    'association caritative': 'shelter',
    'pet shop': 'pet_shop',
    'animalerie': 'pet_shop',
    'service de garde': 'shelter',
}

def map_category(cat_str):
    if not cat_str:
        return 'vet'
    c = cat_str.lower().strip()
    for k, v in CATEGORY_MAP.items():
        if k in c:
            return v
    return 'vet'

def clean_rating(r):
    if not r:
        return None
    r = r.replace(',', '.').strip()
    try:
        val = float(r)
        return round(val, 1) if 0 <= val <= 5 else None
    except Exception:
        return None

def make_slug(name, city):
    text = f"{name} {city}".lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:100]

def clean_phone(phone):
    if not phone:
        return None
    return phone.strip().replace(' ', '')

def clean_website(url):
    if not url:
        return None
    url = url.strip()
    if not url.startswith('http'):
        url = 'https://' + url
    return url

# ============================================================
# Lire tous les CSV
# ============================================================
all_records = []
csv_files = glob.glob(os.path.join(CSV_DIR, '*.csv'))
print(f"Found {len(csv_files)} CSV files")

for csv_file in csv_files:
    try:
        with open(csv_file, encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_records.append(row)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

print(f"Total rows across all CSVs: {len(all_records)}")

# ============================================================
# Traiter et déduplicer
# ============================================================
seen_names = set()
services = []

for row in all_records:
    name = row.get('Name', '').strip()
    if not name or name in seen_names:
        continue

    lat = row.get('Lat', '').strip()
    lng = row.get('Long', '').strip()

    # Détecter ville/état depuis coordonnées
    city, state = detect_city_state(lat, lng)

    # Si pas de ville depuis coords, essayer l'adresse
    if not city:
        address = row.get('Address', '')
        for _, _, c, s in [(None, None, 'Sydney', 'NSW'),
                           (None, None, 'Melbourne', 'VIC'),
                           (None, None, 'Brisbane', 'QLD'),
                           (None, None, 'Perth', 'WA'),
                           (None, None, 'Adelaide', 'SA'),
                           (None, None, 'Gold Coast', 'QLD'),
                           (None, None, 'Canberra', 'ACT'),
                           (None, None, 'Hobart', 'TAS'),
                           (None, None, 'Darwin', 'NT')]:
            if c.lower() in address.lower():
                city, state = c, s
                break

    # Skip si toujours pas de ville australienne
    if not city:
        continue

    # Skip si fermé
    if row.get('Permanently Closed', '').strip().lower() == 'yes':
        continue

    category = map_category(row.get('Category', ''))
    slug = make_slug(name, city)

    # Éviter doublons de slug
    if slug in seen_names:
        slug = slug + '-' + city.lower()
    seen_names.add(name)
    seen_names.add(slug)

    services.append({
        'name': name,
        'slug': slug,
        'category': category,
        'address': row.get('Street Address', '').strip() or row.get('Address', '').strip()[:200],
        'city': city,
        'state': state,
        'postcode': row.get('ZipCode', '').strip() or None,
        'phone': clean_phone(row.get('Phone', '')),
        'website': clean_website(row.get('Website', '')),
        'description': row.get('Description', '').strip()[:500] or None,
        'rating': clean_rating(row.get('Rating', '')),
        'latitude': float(lat) if lat else None,
        'longitude': float(lng.replace('16', '')) if lng else None,
        'is_active': True,
    })

print(f"\nValid Australian services: {len(services)}")

# Stats par ville
from collections import Counter
cities = Counter(s['city'] for s in services)
cats = Counter(s['category'] for s in services)
print("\nBy city:")
for city, count in sorted(cities.items()):
    print(f"  {city}: {count}")
print("\nBy category:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# ============================================================
# Uploader vers Supabase
# ============================================================
confirm = input(f"\nUpload {len(services)} services to Supabase? (yes/no): ").strip().lower()
if confirm != 'yes':
    print("Cancelled.")
    exit()

# Vider la table d'abord (optionnel)
clear = input("Clear existing local_services first? (yes/no): ").strip().lower()
if clear == 'yes':
    sb.from_('local_services').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print("Table cleared.")

# Insérer par batches
BATCH = 50
success = 0
errors = 0

for i in range(0, len(services), BATCH):
    batch = services[i:i+BATCH]
    try:
        sb.from_('local_services').insert(batch).execute()
        success += len(batch)
        print(f"Batch {i//BATCH+1}: {success}/{len(services)} inserted")
    except Exception as e:
        print(f"Batch error: {e}")
        # Try one by one
        for s in batch:
            try:
                sb.from_('local_services').insert([s]).execute()
                success += 1
            except Exception as e2:
                print(f"  Skip '{s['name']}': {str(e2)[:80]}")
                errors += 1

print(f"\nDone! Success: {success} | Errors: {errors}")

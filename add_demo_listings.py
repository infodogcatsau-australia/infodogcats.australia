import os
import re

try:
    from supabase import create_client
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'supabase'])
    from supabase import create_client

SUPABASE_URL = "https://sitmziehzhvqeftydtdr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdG16aWVoemh2cWVmdHlkdGRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDY3OTg2NywiZXhwIjoyMDk2MjU1ODY3fQ.BwH-Hm3o2TidtoueJDPtVkYWvd1rwh2Ljy_IUIHbDy0"
IMAGES_DIR = r"C:\Users\Mebrouk Hassan\Desktop\infodigcats\proper-photon\public\images"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

LISTINGS = [
    {"img": "infodogcats com (1).jpg", "title": "Adorable Maine Coon Kittens Ready Now", "breed": "Maine Coon", "price": 1800, "age_months": 3, "city": "Sydney", "state": "NSW", "description": "Beautiful Maine Coon kittens, vet checked, vaccinated and microchipped. Parents on site. Ready for their forever homes. Very sociable and great with children.", "contact_phone": "0412 XXX XXX", "contact_email": "s***@gmail.com", "status": "active"},
    {"img": "infodogcats com (2).jpg", "title": "Pure Ragdoll Kittens Blue Eyes", "breed": "Ragdoll", "price": 2200, "age_months": 10, "city": "Melbourne", "state": "VIC", "description": "Stunning Ragdoll kittens with gorgeous blue eyes. TICA registered breeder. Both parents fully health tested. Desexed, vaccinated, microchipped. Will melt your heart!", "contact_phone": "0438 XXX XXX", "contact_email": "r***@hotmail.com", "status": "active"},
    {"img": "infodogcats com (3).jpg", "title": "British Shorthair Silver Tabby", "breed": "British Shorthair", "price": 1500, "age_months": 4, "city": "Brisbane", "state": "QLD", "description": "Classic silver tabby British Shorthair. Calm temperament, perfect for apartments. Fully vaccinated, wormed and vet checked. Comes with health guarantee.", "contact_phone": "0421 XXX XXX", "contact_email": "b***@yahoo.com", "status": "active"},
    {"img": "infodogcats com (4).jpg", "title": "Siamese Kittens Seal Point", "breed": "Siamese", "price": 1200, "age_months": 3, "city": "Perth", "state": "WA", "description": "Traditional seal point Siamese kittens. Very talkative and loving. Great with other cats and kids. Vaccinated, microchipped, litter trained. Pick up Perth.", "contact_phone": "0455 XXX XXX", "contact_email": "p***@gmail.com", "status": "active"},
    {"img": "infodogcats com (5).jpg", "title": "Burmese Kittens Brown and Blue", "breed": "Burmese", "price": 1400, "age_months": 3, "city": "Adelaide", "state": "SA", "description": "Gorgeous Burmese kittens available. Brown and blue colours. Parents are AQFA registered. Very affectionate breed, loves cuddles. Ready to go now.", "contact_phone": "0467 XXX XXX", "contact_email": "a***@gmail.com", "status": "active"},
    {"img": "infodogcats com (6).jpg", "title": "Persian Kitten White Fluffy Baby", "breed": "Persian", "price": 1600, "age_months": 4, "city": "Gold Coast", "state": "QLD", "description": "Stunning white Persian kitten, show quality. Doll face type. Eyes vet checked, no breathing issues. Vaccinated, microchipped, desexed. Sweet calm nature.", "contact_phone": "0443 XXX XXX", "contact_email": "g***@outlook.com", "status": "active"},
    {"img": "infodogcats com (7).jpg", "title": "Devon Rex Hypoallergenic Breed Canberra", "breed": "Devon Rex", "price": 1300, "age_months": 5, "city": "Canberra", "state": "ACT", "description": "Playful Devon Rex kitten, great for allergy sufferers. Curly coat, big ears and huge personality. Vaccinated, desexed, microchipped. Loves being around people.", "contact_phone": "0411 XXX XXX", "contact_email": "c***@gmail.com", "status": "active"},
    {"img": "infodogcats com (8).jpg", "title": "Abyssinian Kittens Active and Curious", "breed": "Abyssinian", "price": 1100, "age_months": 3, "city": "Hobart", "state": "TAS", "description": "Lively Abyssinian kittens, the athletes of the cat world! Ticked coat, stunning green eyes. Vet checked, vaccinated and wormed. Ready for active families.", "contact_phone": "0478 XXX XXX", "contact_email": "h***@gmail.com", "status": "active"},
    {"img": "infodogcats com (9).jpg", "title": "Sphynx Kittens Hairless and Loving", "breed": "Sphynx", "price": 2500, "age_months": 4, "city": "Sydney", "state": "NSW", "description": "Rare Sphynx kittens available from registered breeder. Unique and affectionate breed. Come with full vet check, microchip and vaccination. Extremely social cats.", "contact_phone": "0402 XXX XXX", "contact_email": "s***@icloud.com", "status": "active"},
    {"img": "infodogcats com (10).jpg", "title": "Free to Good Home Domestic Shorthair Melbourne", "breed": "Domestic Shorthair", "price": 0, "age_months": 24, "city": "Melbourne", "state": "VIC", "description": "Lovely 2 year old domestic shorthair, must rehome due to moving overseas. Very gentle, great with kids and dogs. Already desexed, vaccinated and microchipped. FREE to approved home only.", "contact_phone": "0431 XXX XXX", "contact_email": "m***@gmail.com", "status": "active"},
    {"img": "infodogcats com (11).jpg", "title": "Scottish Fold Kittens Folded Ears Brisbane", "breed": "Scottish Fold", "price": 2800, "age_months": 3, "city": "Brisbane", "state": "QLD", "description": "Adorable Scottish Fold kittens with perfect folded ears. DNA tested parents, no health issues. TICA registered. Vaccinated, microchipped and vet cleared. Stunning babies.", "contact_phone": "0449 XXX XXX", "contact_email": "b***@yahoo.com.au", "status": "active"},
    {"img": "infodogcats com (12).jpg", "title": "Bengal Kittens Spotted and Rosetted Perth", "breed": "Bengal", "price": 2000, "age_months": 3, "city": "Perth", "state": "WA", "description": "Stunning Bengal kittens with wild leopard markings. TIBCS registered breeder. Parents fully health tested. Vaccinated, microchipped. Very active and intelligent cats.", "contact_phone": "0456 XXX XXX", "contact_email": "p***@gmail.com", "status": "sold"},
    {"img": "infodogcats com (13).jpg", "title": "Norwegian Forest Cat Kittens Adelaide", "breed": "Norwegian Forest Cat", "price": 1700, "age_months": 4, "city": "Adelaide", "state": "SA", "description": "Majestic Norwegian Forest Cat kittens. Thick double coat, perfect for cooler Adelaide winters. Registered breeder. Vaccinated, wormed, microchipped. Gentle giants.", "contact_phone": "0462 XXX XXX", "contact_email": "a***@hotmail.com", "status": "active"},
    {"img": "infodogcats com (14).jpg", "title": "Tonkinese Kittens Mink Pattern Sydney", "breed": "Tonkinese", "price": 1250, "age_months": 3, "city": "Sydney", "state": "NSW", "description": "Beautiful Tonkinese kittens in mink pattern. Cross between Burmese and Siamese — best of both breeds! Playful, affectionate and chatty. Vet checked and vaccinated.", "contact_phone": "0415 XXX XXX", "contact_email": "s***@gmail.com", "status": "active"},
    {"img": "infodogcats com (15).jpg", "title": "Rescue Kitten Adopted Melbourne Shelter", "breed": "Domestic Longhair", "price": 150, "age_months": 2, "city": "Melbourne", "state": "VIC", "description": "Sweet rescue kitten from local shelter. Desexed, vaccinated, microchipped and ready for a loving home. Adoption fee covers vet costs. Very affectionate little girl.", "contact_phone": "0439 XXX XXX", "contact_email": "r***@rescue.org.au", "status": "sold"},
    {"img": "infodogcats com (16).jpg", "title": "Birman Kittens Sacred Cat of Burma Gold Coast", "breed": "Birman", "price": 1800, "age_months": 4, "city": "Gold Coast", "state": "QLD", "description": "Exquisite Birman kittens with white gloves and silky coats. FASA registered breeder. Health guaranteed. Vaccinated, microchipped, desexed. Perfect family cats.", "contact_phone": "0444 XXX XXX", "contact_email": "g***@bigpond.com", "status": "active"},
    {"img": "infodogcats com (17).jpg", "title": "Somali Kittens Fox Like and Playful Canberra", "breed": "Somali", "price": 1350, "age_months": 3, "city": "Canberra", "state": "ACT", "description": "Rare Somali kittens — the long-haired Abyssinian. Bushy tail, ticked coat and huge personality. Registered breeder, health tested parents. Vaccinated and microchipped.", "contact_phone": "0413 XXX XXX", "contact_email": "c***@gmail.com", "status": "active"},
    {"img": "infodogcats com (18).jpg", "title": "Ocicat Kittens Wild Look Domestic Soul Darwin", "breed": "Ocicat", "price": 1500, "age_months": 4, "city": "Darwin", "state": "NT", "description": "Striking Ocicat kittens with wild spotted coat but 100% domestic temperament. Very dog-like personality, can be leash trained. Vaccinated, microchipped, vet checked.", "contact_phone": "0472 XXX XXX", "contact_email": "d***@gmail.com", "status": "active"},
    {"img": "infodogcats com (19).jpg", "title": "Russian Blue Kittens Hypoallergenic Sydney", "breed": "Russian Blue", "price": 1600, "age_months": 3, "city": "Sydney", "state": "NSW", "description": "Elegant Russian Blue kittens with plush blue-grey coat and vivid green eyes. Low allergen breed. FASA registered. Both parents health tested. Quiet and gentle temperament.", "contact_phone": "0408 XXX XXX", "contact_email": "s***@icloud.com", "status": "active"},
    {"img": "infodogcats com (20).jpg", "title": "Exotic Shorthair Teddy Bear Face Melbourne", "breed": "Exotic Shorthair", "price": 2200, "age_months": 5, "city": "Melbourne", "state": "VIC", "description": "Adorable Exotic Shorthair kittens, like a Persian but with easy-care short coat. Flat face, round eyes — the teddy bear of cats. Vaccinated, desexed, microchipped.", "contact_phone": "0435 XXX XXX", "contact_email": "m***@outlook.com", "status": "active"},
    {"img": "infodogcats com (21).jpg", "title": "Burmilla Kittens Silver Shimmering Coat Brisbane", "breed": "Burmilla", "price": 1400, "age_months": 3, "city": "Brisbane", "state": "QLD", "description": "Rare Australian-originated Burmilla kittens with stunning silver-tipped coat. Playful Burmese personality with Persian looks. Registered breeder. Vet checked and vaccinated.", "contact_phone": "0451 XXX XXX", "contact_email": "b***@gmail.com", "status": "active"},
    {"img": "infodogcats com (22).jpg", "title": "Munchkin Kittens Short Legs Big Heart Perth", "breed": "Munchkin", "price": 1900, "age_months": 4, "city": "Perth", "state": "WA", "description": "Cute Munchkin kittens with their signature short legs. Full of energy and personality despite their small stature. Vaccinated, microchipped, vet health checked.", "contact_phone": "0458 XXX XXX", "contact_email": "p***@bigpond.com", "status": "active"},
    {"img": "infodogcats com (23).jpg", "title": "Turkish Angora Long White Coat Adelaide", "breed": "Turkish Angora", "price": 1300, "age_months": 6, "city": "Adelaide", "state": "SA", "description": "Graceful Turkish Angora kitten with silky white coat. One of the oldest natural breeds. Very intelligent and agile. Vaccinated, microchipped and in perfect health.", "contact_phone": "0463 XXX XXX", "contact_email": "a***@gmail.com", "status": "active"},
    {"img": "infodogcats com (24).jpg", "title": "Free Kittens Domestic Mix Hobart", "breed": "Domestic Shorthair", "price": 0, "age_months": 2, "city": "Hobart", "state": "TAS", "description": "Three adorable mixed breed kittens looking for loving homes. 8 weeks old, eating solid food. Mother is a gentle tabby. FREE to good homes. Call or text.", "contact_phone": "0479 XXX XXX", "contact_email": "h***@gmail.com", "status": "active"},
    {"img": "infodogcats com (25).jpg", "title": "Nebelung Kittens Russian Blue Long Hair Sydney", "breed": "Nebelung", "price": 1700, "age_months": 3, "city": "Sydney", "state": "NSW", "description": "Rare Nebelung kittens — long-haired Russian Blue. Silky blue-grey coat, gentle and quiet personality. Registered breeder, health tested parents. Limited availability.", "contact_phone": "0417 XXX XXX", "contact_email": "s***@yahoo.com", "status": "active"},
    {"img": "infodogcats com (26).jpg", "title": "Savannah Kittens F3 Generation Melbourne", "breed": "Savannah", "price": 4500, "age_months": 4, "city": "Melbourne", "state": "VIC", "description": "Rare F3 Savannah kittens. Tall, athletic and incredibly intelligent. Legal to own in VIC. TICA registered breeder. Health tested, vaccinated and microchipped. Serious enquiries only.", "contact_phone": "0436 XXX XXX", "contact_email": "m***@gmail.com", "status": "active"},
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:80] + '-demo-' + str(abs(hash(text)) % 9999)

def get_mime(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}.get(ext, 'image/jpeg')

print("=" * 55)
print("  Adding 26 Demo Cat Listings to Supabase")
print("=" * 55)

existing = sb.from_('cats').select('slug').like('slug', '%-demo-%').execute()
existing_slugs = {r['slug'] for r in (existing.data or [])}
print(f"Existing demo listings: {len(existing_slugs)}")

success = 0
errors = 0

for i, listing in enumerate(LISTINGS):
    img_file = listing['img']
    img_path = os.path.join(IMAGES_DIR, img_file)

    if not os.path.exists(img_path):
        print(f"[{i+1:2}] Image not found: {img_file}")
        errors += 1
        continue

    slug = slugify(listing['title'])

    if slug in existing_slugs:
        print(f"[{i+1:2}] Already exists: {slug[:50]}")
        continue

    print(f"[{i+1:2}] Processing: {listing['title'][:45]}", end=' ', flush=True)

    cat_data = {
        'title':         listing['title'],
        'slug':          slug,
        'breed':         listing['breed'],
        'price':         listing['price'],
        'age_months':    listing.get('age_months'),
        'description':   listing['description'],
        'city':          listing['city'],
        'state':         listing['state'],
        'contact_phone': listing['contact_phone'],
        'contact_email': listing['contact_email'],
        'status':        listing['status'],
        'is_approved':   True,
        'currency':      'AUD',
    }

    try:
        cat_result = sb.from_('cats').insert(cat_data).select().execute()
        cat_id = cat_result.data[0]['id']
    except Exception as e:
        print(f"DB error: {str(e)[:60]}")
        errors += 1
        continue

    storage_path = f"demo/{i+1:02d}-{re.sub(r'[^a-z0-9]+', '-', listing['breed'].lower())}.jpg"
    mime = get_mime(img_file)

    try:
        with open(img_path, 'rb') as f:
            img_data = f.read()
        sb.storage.from_('cat-images').upload(
            path=storage_path,
            file=img_data,
            file_options={"content-type": mime, "upsert": "true"}
        )
    except Exception as e:
        err = str(e)
        if 'already exists' not in err.lower():
            print(f"Upload warn: {err[:40]}", end=' ')

    try:
        sb.from_('cat_images').insert({
            'cat_id':       cat_id,
            'storage_path': storage_path,
            'is_primary':   True,
            'sort_order':   0,
        }).execute()
    except Exception as e:
        print(f"Image record warn: {str(e)[:40]}", end=' ')

    kb = os.path.getsize(img_path) // 1024
    status_label = 'SOLD' if listing['status'] == 'sold' else 'Active'
    price_label = 'FREE' if listing['price'] == 0 else f"A${listing['price']:,}"
    print(f"OK | {price_label} | {status_label} | {kb}KB")
    success += 1
    existing_slugs.add(slug)

print(f"\n{'='*55}")
print(f"Done! Added: {success} | Errors: {errors}")
print(f"Go to localhost:4321/cats-for-sale to see listings!")
"""
fix_images_from_zip.py
-----------------------
1. Parse WordPress XML → extrait les URLs d'images utilisées dans les posts
2. Lit les images depuis le ZIP local (pas de téléchargement depuis internet)
3. Upload vers Supabase Storage bucket 'cat-images'
4. Met à jour post.content et featured_image_path dans 'posts'

Usage:
    pip install supabase requests
    python fix_images_from_zip.py
"""

import re
import os
import time
import zipfile
import xml.etree.ElementTree as ET
from supabase import create_client

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://sitmziehzhvqeftydtdr.supabase.co"
SUPABASE_SERVICE_ROLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdG16aWVoemh2cWVmdHlkdGRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDY3OTg2NywiZXhwIjoyMDk2MjU1ODY3fQ.BwH-Hm3o2TidtoueJDPtVkYWvd1rwh2Ljy_IUIHbDy0"
XML_PATH = r"C:\Users\Mebrouk Hassan\Desktop\infodigcats\australiancatbreeds.WordPress.2026-06-05.xml"
ZIP_PATH = ZIP_PATH = r"C:\Users\Mebrouk Hassan\Desktop\infodigcats\2023.zip"  # ← chemin du ZIP
BUCKET = "cat-images"
FOLDER = "wp-images"
# ──────────────────────────────────────────────────────────────────────────────

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

MIME_TYPES = {
    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
    'png': 'image/png', 'webp': 'image/webp', 'gif': 'image/gif'
}

def extract_wp_image_urls(xml_path):
    """Extrait toutes les URLs wp-content/uploads depuis le XML."""
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'https?://[^"\'<>\s]+/wp-content/uploads/[^"\'<>\s]+'
    urls = list(set(re.findall(pattern, content)))
    urls = [u for u in urls if re.search(r'\.(jpg|jpeg|png|webp|gif)(\?.*)?$', u, re.I)]
    print(f"✅ {len(urls)} images trouvées dans le XML")
    return urls

def url_to_zip_path(url):
    """
    Convertit une URL WordPress en chemin dans le ZIP.
    URL: https://infodogcats.com/wp-content/uploads/2026/05/image.png
    ZIP path: 2026/05/image.png
    """
    match = re.search(r'/wp-content/uploads/(.+?)(\?.*)?$', url)
    if match:
        return match.group(1)
    return None

def get_storage_path(zip_internal_path):
    """Chemin de stockage dans Supabase."""
    return f"{FOLDER}/{zip_internal_path}"

def get_public_url(storage_path):
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"

def upload_to_supabase(data, storage_path, mime_type):
    try:
        sb.storage.from_(BUCKET).upload(
            path=storage_path,
            file=data,
            file_options={"content-type": mime_type, "upsert": "true"}
        )
        return True
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            return True  # Déjà uploadé
        print(f"  ⚠️ Upload error: {e}")
        return False

def update_posts_content(url_mapping):
    print(f"\n📝 Mise à jour des posts dans Supabase...")
    result = sb.table('posts').select('id, content, featured_image_path').execute()
    posts = result.data
    print(f"  → {len(posts)} posts trouvés")

    updated = 0
    for post in posts:
        content = post.get('content', '') or ''
        featured = post.get('featured_image_path', '') or ''
        new_content = content
        new_featured = featured

        for old_url, new_url in url_mapping.items():
            new_content = new_content.replace(old_url, new_url)
            new_featured = new_featured.replace(old_url, new_url)

        if new_content != content or new_featured != featured:
            update_data = {}
            if new_content != content:
                update_data['content'] = new_content
            if new_featured != featured:
                update_data['featured_image_path'] = new_featured
            sb.table('posts').update(update_data).eq('id', post['id']).execute()
            updated += 1

    print(f"  ✅ {updated} posts mis à jour")

def main():
    print("=" * 60)
    print("🐱 InfoDogCats — Image Migration from ZIP")
    print("=" * 60)

    # 1. Extraire les URLs du XML
    urls = extract_wp_image_urls(XML_PATH)

    # 2. Ouvrir le ZIP
    print(f"\n📦 Ouverture du ZIP: {ZIP_PATH}")
    if not os.path.exists(ZIP_PATH):
        print(f"❌ ZIP introuvable: {ZIP_PATH}")
        return

    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        zip_files = set(zf.namelist())
        print(f"  → {len(zip_files)} fichiers dans le ZIP")

        url_mapping = {}
        success = 0
        not_found = 0
        failed = 0

        for i, url in enumerate(urls, 1):
            # Nettoyer l'URL (enlever les variantes de taille)
            clean_url = re.sub(r'-\d+x\d+(\.\w+)$', r'\1', url)
            
            zip_path = url_to_zip_path(url)
            clean_zip_path = url_to_zip_path(clean_url)

            # Chercher dans le ZIP (avec ou sans variante de taille)
            found_path = None
            for candidate in [zip_path, clean_zip_path]:
                if candidate and candidate in zip_files:
                    found_path = candidate
                    break

            if not found_path:
                not_found += 1
                continue

            print(f"[{i}/{len(urls)}] {found_path.split('/')[-1]}")

            # Lire depuis le ZIP
            data = zf.read(found_path)
            ext = found_path.split('.')[-1].lower()
            mime = MIME_TYPES.get(ext, 'image/jpeg')
            storage_path = get_storage_path(found_path)

            # Upload
            if upload_to_supabase(data, storage_path, mime):
                new_url = get_public_url(storage_path)
                url_mapping[url] = new_url
                if clean_url != url:
                    url_mapping[clean_url] = new_url
                print(f"  ✅ Uploadé")
                success += 1
            else:
                failed += 1

            time.sleep(0.2)

    print(f"\n{'='*60}")
    print(f"📊 Résultats:")
    print(f"  ✅ Uploadées: {success}")
    print(f"  ⚠️  Non trouvées dans ZIP: {not_found}")
    print(f"  ❌ Échecs upload: {failed}")

    if url_mapping:
        update_posts_content(url_mapping)
        with open('url_mapping.txt', 'w', encoding='utf-8') as f:
            for old, new in url_mapping.items():
                f.write(f"{old}\n  → {new}\n")
        print(f"\n💾 Mapping sauvegardé dans url_mapping.txt")

    print("\n✅ Migration terminée!")

if __name__ == '__main__':
    main()

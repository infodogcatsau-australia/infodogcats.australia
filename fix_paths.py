from supabase import create_client
import re

sb = create_client(
    'https://sitmziehzhvqeftydtdr.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdG16aWVoemh2cWVmdHlkdGRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDY3OTg2NywiZXhwIjoyMDk2MjU1ODY3fQ.BwH-Hm3o2TidtoueJDPtVkYWvd1rwh2Ljy_IUIHbDy0'
)

# جلب كل المقالات التي فيها URL كامل
r = sb.from_('posts').select('id, slug, featured_image_path').not_.is_('featured_image_path', 'null').execute()

fixed = 0
for post in r.data:
    path = post['featured_image_path']
    if not path or not path.startswith('http'):
        continue

    # استخرج المسار النسبي من URL
    # من: https://xxx.supabase.co/storage/v1/object/public/cat-images/blog/...
    # إلى: blog/...
    match = re.search(r'/public/cat-images/(.+?)(\?|$)', path)
    if not match:
        # جرب bucket اسمه cats
        match = re.search(r'/public/cats/(.+?)(\?|$)', path)
        if match:
            relative = 'manual/' + match.group(1)
        else:
            print(f'❌ Cannot parse: {path}')
            continue
    else:
        relative = match.group(1)

    sb.from_('posts').update({'featured_image_path': relative}).eq('id', post['id']).execute()
    print(f'✅ {post["slug"][:45]:45} → {relative}')
    fixed += 1

print(f'\nFixed: {fixed} posts')
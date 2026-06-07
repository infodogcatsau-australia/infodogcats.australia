from supabase import create_client

sb = create_client(
    'https://sitmziehzhvqeftydtdr.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdG16aWVoemh2cWVmdHlkdGRyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDY3OTg2NywiZXhwIjoyMDk2MjU1ODY3fQ.BwH-Hm3o2TidtoueJDPtVkYWvd1rwh2Ljy_IUIHbDy0'
)

r = sb.from_('posts').select('slug, title, featured_image_path').is_('featured_image_path', 'null').execute()
print(f'Posts missing image: {len(r.data)}')
for p in r.data:
    print(f"  {p['slug']}")
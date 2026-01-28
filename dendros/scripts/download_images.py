import requests
from pathlib import Path
BASE = Path(__file__).parent.parent
IMG_DIR = BASE / 'images'
IMG_DIR.mkdir(exist_ok=True)
urls_file = BASE / 'data' / 'image_urls_full.txt'
if not urls_file.exists():
    print('data/image_urls_full.txt not found')
    raise SystemExit(1)
lines = [l for l in urls_file.read_text(encoding='utf-8').splitlines() if l.strip()]
for i, url in enumerate(lines, start=1):
    try:
        r = requests.get(url, timeout=20); r.raise_for_status()
        ext = url.split('?')[0].split('.')[-1]
        if ext.lower() not in ('jpg','jpeg','png','webp'):
            ext = 'jpg'
        fname = IMG_DIR / f'photo_{i}.{ext}'
        with open(fname, 'wb') as f:
            f.write(r.content)
        print('Saved', fname)
    except Exception as e:
        print('Error saving', url, e)

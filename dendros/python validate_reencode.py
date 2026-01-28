# validate_reencode.py
from PIL import Image, UnidentifiedImageError
from pathlib import Path
import shutil

IMAGES_DIR = Path(r"C:\Users\bekta\Downloads\Dendro_full_improved\images")
BACKUP_DIR = IMAGES_DIR / "backup_before_reencode"
BACKUP_DIR.mkdir(exist_ok=True)

def find_image_path(i: int):
    for ext in ("jpg", "jpeg", "png"):
        p = IMAGES_DIR / f"{i}.{ext}"
        if p.exists():
            return p
    return None

for i in range(1, 11):
    p = find_image_path(i)
    if not p:
        print(f"[MISSING] {i}.* not found")
        continue

    try:
        with Image.open(p) as im:
            print(f"[OPEN] {p.name}: mode={im.mode}, size={im.size}, format={im.format}, bytes={p.stat().st_size}")
            # если не RGB или JPEG — перекодируем в RGB JPEG
            needs_reencode = (im.mode != "RGB") or (im.format not in ("JPEG", "PNG"))
            if needs_reencode or p.suffix.lower() not in (".jpg", ".jpeg"):
                out = IMAGES_DIR / f"{i}_fixed.jpg"
                # backup original
                shutil.copy2(p, BACKUP_DIR / p.name)
                rgb = im.convert("RGB")
                rgb.save(out, format="JPEG", quality=90, optimize=True)
                print(f"  -> reencoded to {out.name}")
            else:
                print(f"  -> ok, no reencode needed")
    except UnidentifiedImageError:
        print(f"[CORRUPT] {p.name} — UnidentifiedImageError, attempting force re-open")
        try:
            # попытка форсированной перекодировки (может упасть)
            with Image.open(p) as im:
                rgb = im.convert("RGB")
                out = IMAGES_DIR / f"{i}_fixed.jpg"
                shutil.copy2(p, BACKUP_DIR / p.name)
                rgb.save(out, format="JPEG", quality=90, optimize=True)
                print(f"  -> reencoded to {out.name}")
        except Exception as e:
            print(f"  FAILED reencode {p.name}: {e}")
    except Exception as e:
        print(f"[ERROR] {p.name}: {e}")
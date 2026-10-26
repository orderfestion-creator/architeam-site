#!/usr/bin/env python3
"""Turn a photo from _blog/photos-inbox/ into web-ready images for the site.

Usage (one photo at a time, after LOOKING at it to name and describe it honestly):
  python3 _blog/photos.py <file-in-inbox> <descriptive-slug> "<short description in ME>"

What it does:
  - opens JPG / PNG / WEBP / HEIC (HEIC needs: pip install --break-system-packages pillow-heif)
  - rotates by EXIF, removes all metadata (incl. GPS location), converts to sRGB
  - writes <IMG_DIR>/<slug>.webp (long side max 1600 px) and <slug>-600.webp (600 px wide)
  - deletes the original from the inbox (git rm it in the commit)
  - appends "slug.webp — description" to _blog/PHOTOS.md so later runs know what each photo shows
Requires Pillow (pip install --break-system-packages pillow).
"""
import os
import re
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.environ.get("IMG_DIR", "img/blog")
INBOX = os.path.join(ROOT, "_blog", "photos-inbox")
CATALOG = os.path.join(ROOT, "_blog", "PHOTOS.md")


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    src, slug, desc = sys.argv[1], sys.argv[2], sys.argv[3].strip()
    if not os.path.isabs(src):
        src = src if os.path.exists(src) else os.path.join(INBOX, src)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit(f"bad slug {slug!r}: use lowercase latin words joined by '-'")
    out_dir = os.path.join(ROOT, IMG_DIR)
    os.makedirs(out_dir, exist_ok=True)
    big = os.path.join(out_dir, f"{slug}.webp")
    if os.path.exists(big):
        raise SystemExit(f"{IMG_DIR}/{slug}.webp already exists; choose another slug")
    if src.lower().endswith((".heic", ".heif")):
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            raise SystemExit("HEIC photo: run  pip install --break-system-packages pillow-heif  first")
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    full = im.copy()
    full.thumbnail((1600, 1600), Image.LANCZOS)
    full.save(big, "WEBP", quality=80, method=6)
    small = im.copy()
    small.thumbnail((600, 10000), Image.LANCZOS)
    small.save(os.path.join(out_dir, f"{slug}-600.webp"), "WEBP", quality=78, method=6)
    os.remove(src)
    new = not os.path.exists(CATALOG)
    with open(CATALOG, "a", encoding="utf-8") as f:
        if new:
            f.write("# Photos added from the inbox\n\nOne line per photo: file — what it really shows. Use these in articles where they match the topic.\n\n")
        f.write(f"- {slug}.webp ({full.width}x{full.height}) — {desc}\n")
    print(f"ok: {IMG_DIR}/{slug}.webp {full.width}x{full.height} + {slug}-600.webp")


if __name__ == "__main__":
    main()

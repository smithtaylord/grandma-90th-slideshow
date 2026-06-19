"""
Batch convert HEIC/HEIF images to JPG, copy JPGs, resize for web, and update config.json.

Usage:
    python scripts/convert_photos.py

Scans SOURCE_DIR for all image files.
- HEIC/HEIF files are converted to JPG and saved to OUTPUT_DIR
- JPG/JPEG files are re-saved as JPG into OUTPUT_DIR
- All images are resized to max MAX_WIDTH pixels wide (preserving aspect ratio)
- All output files are renamed sequentially: photo001.jpg, photo002.jpg, etc.
- config.json is auto-updated with all photos (preserving existing captions)
- Any old photoXXX.jpg files in OUTPUT_DIR from a previous run are removed

Re-run this script whenever you add new photos to SOURCE_DIR.
"""

import os
import json
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

SOURCE_DIR = r"C:\Users\smith\OneDrive\Desktop\Grandmas 90th"
PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "public", "photos")
CONFIG_PATH = os.path.join(PROJECT_DIR, "public", "config.json")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".heic", ".heif"}
MAX_WIDTH = 1920
JPEG_QUALITY = 85


def get_images(source_dir):
    files = []
    for f in sorted(os.listdir(source_dir)):
        ext = Path(f).suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            files.append(Path(source_dir) / f)
    return files


def convert_and_copy(source_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for old in Path(output_dir).glob("photo*.jpg"):
        old.unlink()

    images = get_images(source_dir)

    if not images:
        print("No image files found in source directory.")
        return []

    print(f"Found {len(images)} images to process:\n")

    output_names = []

    for i, img_path in enumerate(images, start=1):
        ext = img_path.suffix.lower()
        out_name = f"photo{i:03d}.jpg"
        out_path = os.path.join(output_dir, out_name)

        image = Image.open(img_path)
        image = ImageOps.exif_transpose(image)
        if image.mode != "RGB":
            image = image.convert("RGB")

        if image.width > MAX_WIDTH:
            ratio = MAX_WIDTH / image.width
            new_height = int(image.height * ratio)
            image = image.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            print(f"  [{i}/{len(images)}] {'Converting' if ext in {'.heic', '.heif'} else 'Copying   '} {img_path.name} -> {out_name} (resized to {MAX_WIDTH}px wide)")
        else:
            print(f"  [{i}/{len(images)}] {'Converting' if ext in {'.heic', '.heif'} else 'Copying   '} {img_path.name} -> {out_name}")

        image.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        output_names.append(out_name)

    print(f"\nDone! {len(images)} images saved to {os.path.abspath(output_dir)}")
    return output_names


def update_config(output_names, config_path):
    existing = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            existing = json.load(f)
        old_photos = {
            p["file"]: {
                "caption": p.get("caption", ""),
                "excludedFromMusic": p.get("excludedFromMusic", False),
            }
            for p in existing.get("photos", [])
        }
    else:
        old_photos = {}

    photos = []
    for name in output_names:
        old = old_photos.get(name, {})
        photos.append({
            "file": name,
            "caption": old.get("caption", ""),
            "excludedFromMusic": old.get("excludedFromMusic", False),
        })

    config = {
        "songTitle": "Ninety Years of Liz",
        "defaultDuration": 5,
        "transitionDuration": 1,
        "transitionStyle": "crossfade",
        "photos": photos,
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Updated config.json with {len(photos)} photos")


if __name__ == "__main__":
    names = convert_and_copy(SOURCE_DIR, OUTPUT_DIR)
    if names:
        update_config(names, CONFIG_PATH)
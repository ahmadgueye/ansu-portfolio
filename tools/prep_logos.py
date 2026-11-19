"""Recadre les logos clients au ras de leur contenu (retire les marges blanches ou transparentes).

Usage : python3 tools/prep_logos.py   →  écrit img/logos/trim/<nom>.png
Les SVG sont copiés tels quels (leur cadre est déjà serré).
"""
import pathlib, shutil
from PIL import Image, ImageChops

src = pathlib.Path("img/logos"); out = src / "trim"; out.mkdir(exist_ok=True)
for f in sorted(src.iterdir()):
    if f.is_dir(): continue
    if f.suffix == ".svg":
        shutil.copy(f, out / f.name); print(f.name, "svg"); continue
    im = Image.open(f).convert("RGBA")
    # fond = transparent, ou proche du blanc
    alpha = im.getchannel("A")
    rgb = im.convert("RGB")
    white = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(rgb, white).convert("L").point(lambda v: 255 if v > 24 else 0)
    mask = ImageChops.multiply(diff, alpha.point(lambda v: 255 if v > 16 else 0))
    box = mask.getbbox() or (0, 0, *im.size)
    pad = max(2, int(0.02 * max(box[2] - box[0], box[3] - box[1])))
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
    im.crop(box).save(out / (f.stem + ".png"), optimize=True)
    print(f.name, im.size, "->", (box[2] - box[0], box[3] - box[1]))

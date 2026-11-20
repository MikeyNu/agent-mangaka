#!/usr/bin/env python3
"""Inventory image bytes and prepare overview tiles for actual visual inspection.

Writing a contact sheet is not visual review. Never mark an asset inspected
merely because this program could decode it.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps


def inspect(paths, output, tile_height=1400, scale=0.5, columns=4):
    if tile_height < 100 or not 0 < scale <= 1 or not 1 <= columns <= 8:
        raise ValueError("Invalid tile, scale, or column setting")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    records, hashes = [], {}
    for index, path in enumerate(paths):
        path = Path(path)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as source:
            source.load()
            im = ImageOps.exif_transpose(source).convert("RGBA")
            alpha = im.getchannel("A")
            transparent = alpha.getextrema()[0] < 255
            count = math.ceil(im.height/tile_height)
            width, height = max(1, round(im.width*scale)), max(1, round(tile_height*scale))
            overview = Image.new("RGB", (columns*width, math.ceil(count/columns)*(height+26)), "#dedede")
            draw = ImageDraw.Draw(overview)
            tile_ranges = []
            for tile in range(count):
                y0, y1 = tile*tile_height, min(im.height, (tile+1)*tile_height)
                crop = im.crop((0, y0, im.width, y1))
                crop.thumbnail((width, height))
                x, y = (tile % columns)*width, (tile//columns)*(height+26)
                overview.paste(crop, (x, y+26), crop)
                draw.text((x+4, y+4), f"{index:03d} y={y0}:{y1}", fill="black")
                tile_ranges.append([0, y0, im.width, y1])
            name = f"{index:03d}-{sha[:12]}.jpg"
            overview.save(output/name, quality=92)
            record = {"source": str(path), "sha256": sha, "size": list(im.size),
                      "mode": source.mode, "has_transparent_pixels": transparent,
                      "duplicate_of": hashes.get(sha), "overview": name,
                      "overview_scale": scale, "tiles": tile_ranges,
                      "coordinate_space": "EXIF-oriented source pixels",
                      "visual_review": "not_performed"}
            hashes.setdefault(sha, str(path))
            records.append(record)
    (output/"inventory.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    return records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--tile-height", type=int, default=1400)
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--columns", type=int, default=4)
    args = ap.parse_args()
    paths = []
    for p in args.inputs:
        paths.extend(sorted(f for f in p.iterdir() if f.suffix.lower() in
                            {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}) if p.is_dir() else [p])
    records = inspect(paths, args.out, args.tile_height, args.scale, args.columns)
    print(json.dumps({"files": len(records), "unique": len({r["sha256"] for r in records}),
                      "inventory": str(args.out/"inventory.json"),
                      "notice": "Open the images and native detail crops before recording a visual verdict."}))


if __name__ == "__main__":
    main()

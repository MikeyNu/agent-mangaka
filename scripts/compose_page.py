#!/usr/bin/env python3
"""Compose reviewed comic panels and exact ledger text into editable layers.

Usage: python compose_page.py layout.json output-directory [--overwrite]
See references/compositing.md for the intentionally separate layout contract.
This program validates review attestations; it cannot perform visual art review.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import struct
import tempfile
from typing import Any
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFont, features


SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
XML = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", XLINK)
KINDS = {"speech", "thought", "caption", "offscreen", "sfx"}
SHAPES = {"ellipse", "rect", "rounded", "thought", "burst"}
CHECKS = {"identity", "narrative", "continuity", "emotion", "anatomy", "style", "composition"}
EXPORTS = ("composite.png", "lettering.png", "page.svg", "page.ora", "render_manifest.json")


class CompositionError(ValueError):
    """A contract or rendering failure that must not be silently repaired."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise CompositionError(message)


def number(value: Any, label: str) -> float:
    need(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label}: expected a number")
    need(math.isfinite(value), f"{label}: number must be finite")
    return float(value)


def integer(value: Any, label: str, minimum: int = 1) -> int:
    n = number(value, label)
    need(n.is_integer() and n >= minimum, f"{label}: expected an integer >= {minimum}")
    return int(n)


def unique(items: list[dict], key: str, label: str) -> dict[str, dict]:
    need(isinstance(items, list), f"{label}: expected a list")
    result = {}
    for item in items:
        need(isinstance(item, dict), f"{label}: each item must be an object")
        value = item.get(key)
        need(isinstance(value, str) and bool(value), f"{label}: missing {key}")
        need(value not in result, f"{label}: duplicate {key} {value}")
        result[value] = item
    return result


def read_json(path: Path) -> Any:
    need(path.is_file(), f"Missing reference: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CompositionError(f"Cannot read JSON {path}: {exc}") from exc


def resolve(base: Path, value: Any, label: str) -> Path:
    need(isinstance(value, str) and bool(value), f"{label}: file path is required")
    path = Path(value)
    path = path if path.is_absolute() else base / path
    need(path.is_file(), f"{label}: missing reference {path}")
    return path.resolve()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba(value: Any, label: str) -> tuple[int, int, int, int]:
    need(isinstance(value, str), f"{label}: expected a CSS color string")
    try:
        return ImageColor.getcolor(value, "RGBA")
    except ValueError as exc:
        raise CompositionError(f"{label}: invalid color {value!r}") from exc


def color_attrs(value: str, name: str) -> dict[str, str]:
    r, g, b, a = rgba(value, name)
    return {name: f"#{r:02x}{g:02x}{b:02x}", f"{name}-opacity": f"{a / 255:.8g}"}


def point(value: Any, label: str) -> tuple[float, float]:
    need(isinstance(value, list) and len(value) == 2, f"{label}: expected [x, y]")
    return number(value[0], label), number(value[1], label)


def rect(value: Any, label: str) -> tuple[float, float, float, float]:
    need(isinstance(value, list) and len(value) == 4, f"{label}: expected [x, y, width, height]")
    x, y, w, h = (number(v, label) for v in value)
    need(w > 0 and h > 0, f"{label}: width and height must be positive")
    return x, y, w, h


def cross(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(a, b, p) -> bool:
    return abs(cross(a, b, p)) < 1e-8 and min(a[0], b[0]) - 1e-8 <= p[0] <= max(a[0], b[0]) + 1e-8 and min(a[1], b[1]) - 1e-8 <= p[1] <= max(a[1], b[1]) + 1e-8


def intersects(a, b, c, d) -> bool:
    q = [cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)]
    if q[0] * q[1] < 0 and q[2] * q[3] < 0:
        return True
    return on_segment(a, b, c) or on_segment(a, b, d) or on_segment(c, d, a) or on_segment(c, d, b)


def polygon(frame: dict, size: tuple[int, int], label: str) -> list[tuple[float, float]]:
    need(isinstance(frame, dict), f"{label}: frame must be an object")
    need(set(frame) in ({"rect"}, {"polygon"}), f"{label}: specify exactly rect or polygon")
    if "rect" in frame:
        x, y, w, h = rect(frame["rect"], label)
        points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    else:
        need(isinstance(frame["polygon"], list), f"{label}: polygon must be a list")
        points = [point(p, label) for p in frame["polygon"]]
    need(len(points) >= 3 and len(set(points)) == len(points), f"{label}: polygon needs distinct vertices, without repeating the closing point")
    need(all(0 <= x <= size[0] and 0 <= y <= size[1] for x, y in points), f"{label}: frame extends outside page")
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1])) / 2
    need(abs(area) >= 1, f"{label}: polygon has zero or negligible area")
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            need(not intersects(points[i], points[(i + 1) % n], points[j], points[(j + 1) % n]), f"{label}: self-intersecting polygon")
    for i in range(n):
        a, b, c = points[i - 1], points[i], points[(i + 1) % n]
        need(not (abs(cross(a, b, c)) < 1e-8 and on_segment(a, c, b) is False), f"{label}: overlapping adjacent edges")
    return points


def poly_mask(size: tuple[int, int], points: list[tuple[float, float]]) -> Image.Image:
    # Supersample only the local bounding box, not a full giant page.
    x0 = max(0, math.floor(min(p[0] for p in points)))
    y0 = max(0, math.floor(min(p[1] for p in points)))
    x1 = min(size[0], math.ceil(max(p[0] for p in points)))
    y1 = min(size[1], math.ceil(max(p[1] for p in points)))
    local = Image.new("L", ((x1 - x0) * 4, (y1 - y0) * 4), 0)
    ImageDraw.Draw(local).polygon([((x - x0) * 4, (y - y0) * 4) for x, y in points], fill=255)
    mask = Image.new("L", size, 0)
    mask.paste(local.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS), (x0, y0))
    return mask


def box_mask(size, box) -> Image.Image:
    x, y, w, h = box
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((math.floor(x), math.floor(y), math.ceil(x + w) - 1, math.ceil(y + h) - 1), fill=255)
    return mask


def png_bytes(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def svg_element(parent: ET.Element, name: str, attrs: dict | None = None, text: str | None = None) -> ET.Element:
    element = ET.SubElement(parent, f"{{{SVG}}}{name}", {str(k): str(v) for k, v in (attrs or {}).items()})
    element.text = text
    return element


def points_text(points) -> str:
    return " ".join(f"{x:.8g},{y:.8g}" for x, y in points)


def check_acceptance(panel: dict, art: Path, base: Path) -> dict:
    record = read_json(resolve(base, panel.get("acceptance"), f"Panel {panel['id']} acceptance"))
    need(isinstance(record, dict), f"Panel {panel['id']}: acceptance must be an object")
    need(record.get("status") == "accepted", f"Panel {panel['id']}: art is not accepted")
    need(record.get("panel_id") == panel["id"], f"Panel {panel['id']}: acceptance belongs to another panel")
    need(record.get("art_sha256") == sha256(art), f"Panel {panel['id']}: acceptance hash does not match art")
    need(isinstance(record.get("reviewed_by"), str) and bool(record["reviewed_by"].strip()), f"Panel {panel['id']}: missing reviewer attestation")
    checks = record.get("checks", {})
    need(isinstance(checks, dict) and CHECKS <= checks.keys(), f"Panel {panel['id']}: incomplete acceptance checks")
    for name in CHECKS:
        value = checks[name]
        if isinstance(value, str):
            need(value == "pass", f"Panel {panel['id']}: {name} must pass, or give an explicit not_applicable reason")
        else:
            need(isinstance(value, dict) and value.get("status") in {"pass", "not_applicable"}, f"Panel {panel['id']}: unresolved {name} check")
            need(isinstance(value.get("reason"), str) and bool(value["reason"].strip()), f"Panel {panel['id']}: {name} requires a reason")
            if name in {"identity", "emotion", "anatomy"} and panel.get("subjects"):
                need(value["status"] == "pass", f"Panel {panel['id']}: visible subjects require a passed {name} check")
    return record


class FontCoverage:
    """Read Unicode cmap 4/12/13 from a supplied TTF/OTF without extra libraries."""

    def __init__(self, path: Path):
        self.data = path.read_bytes()
        self.tables = []
        try:
            need(self.data[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true"), "Use a single TTF/OTF font, not a collection or webfont")
            count = struct.unpack_from(">H", self.data, 4)[0]
            cmap = None
            for i in range(count):
                tag, _, offset, _ = struct.unpack_from(">4sIII", self.data, 12 + i * 16)
                if tag == b"cmap":
                    cmap = offset
                    break
            need(cmap is not None, "Font has no Unicode cmap")
            count = struct.unpack_from(">H", self.data, cmap + 2)[0]
            for i in range(count):
                platform, encoding, offset = struct.unpack_from(">HHI", self.data, cmap + 4 + i * 8)
                start = cmap + offset
                kind = struct.unpack_from(">H", self.data, start)[0]
                if (platform == 0 or (platform == 3 and encoding in {1, 10})) and kind in {4, 12, 13}:
                    self.tables.append((kind, start))
            need(bool(self.tables), "Font Unicode cmap format is unsupported; use a TTF/OTF with cmap 4, 12, or 13")
        except (struct.error, IndexError) as exc:
            raise CompositionError(f"Malformed font: {path}") from exc

    def has(self, code: int) -> bool:
        d = self.data
        for kind, start in self.tables:
            if kind in {12, 13}:
                for i in range(struct.unpack_from(">I", d, start + 12)[0]):
                    first, last, glyph = struct.unpack_from(">III", d, start + 16 + i * 12)
                    if first <= code <= last:
                        if (glyph if kind == 13 else glyph + code - first) != 0:
                            return True
            elif code <= 0xFFFF:
                n = struct.unpack_from(">H", d, start + 6)[0] // 2
                for i in range(n):
                    end = struct.unpack_from(">H", d, start + 14 + 2 * i)[0]
                    first = struct.unpack_from(">H", d, start + 16 + 2 * n + 2 * i)[0]
                    if first <= code <= end:
                        delta = struct.unpack_from(">h", d, start + 16 + 4 * n + 2 * i)[0]
                        offset_pos = start + 16 + 6 * n + 2 * i
                        offset = struct.unpack_from(">H", d, offset_pos)[0]
                        if offset == 0:
                            glyph = (code + delta) % 65536
                        else:
                            glyph = struct.unpack_from(">H", d, offset_pos + offset + 2 * (code - first))[0]
                            glyph = (glyph + delta) % 65536 if glyph else 0
                        if glyph:
                            return True
        return False


def requires_shaping(text: str) -> bool:
    # Bidi, combining sequences, Indic, Thai, Khmer, Myanmar and related scripts.
    return any(unicodedata.bidirectional(c) in {"R", "AL", "AN"} or unicodedata.combining(c) or 0x0900 <= ord(c) <= 0x109F or 0x1780 <= ord(c) <= 0x17FF for c in text)


def wrap_text(text: str, font, width: float, direction: str) -> list[str]:
    """Wrap at spaces without dropping punctuation or source whitespace."""
    need(isinstance(text, str), "Dialogue text must be a string")
    need(not any(unicodedata.category(c) == "Cc" and c != "\n" for c in text), "Dialogue contains unsupported control characters; tabs and carriage returns need explicit source correction")
    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for token in re.findall(r"\S+|[^\S\n]+", paragraph):
            need(measure.textlength(token, font=font, direction=direction) <= width + 1e-6, "Text overflow: an unbroken word or whitespace run exceeds the balloon interior")
            candidate = line + token
            if line and measure.textlength(candidate, font=font, direction=direction) > width + 1e-6:
                lines.append(line)
                line = token
            else:
                line = candidate
        lines.append(line)
    return lines


def burst_points(box, count: int = 12):
    x, y, w, h = box
    result = []
    for i in range(count * 2):
        angle = -math.pi / 2 + i * math.pi / count
        radius = 1 if i % 2 == 0 else 0.82
        result.append((x + w / 2 + math.cos(angle) * w / 2 * radius, y + h / 2 + math.sin(angle) * h / 2 * radius))
    return result


def draw_body(layer, group, box, style) -> Image.Image:
    x, y, w, h = box
    shape = style["shape"]
    fill, stroke = style.get("fill", "#ffffff"), style.get("stroke", "#111111")
    sw = integer(style.get("stroke_width", 2), "Balloon stroke width", 0)
    draw = ImageDraw.Draw(layer)
    mask = Image.new("L", layer.size, 0)
    md = ImageDraw.Draw(mask)
    attrs = {**color_attrs(fill, "fill"), **color_attrs(stroke, "stroke"), "stroke-width": sw}
    bbox = (x, y, x + w, y + h)
    if shape in {"rect", "rounded"}:
        radius = number(style.get("corner_radius", min(w, h) * 0.16 if shape == "rounded" else 0), "corner radius")
        need(0 <= radius <= min(w, h) / 2, "Invalid corner radius")
        draw.rounded_rectangle(bbox, radius, fill=rgba(fill, "fill"), outline=rgba(stroke, "stroke"), width=sw)
        md.rounded_rectangle(bbox, radius, fill=255)
        svg_element(group, "rect", {"x": x, "y": y, "width": w, "height": h, "rx": radius, **attrs})
    elif shape in {"burst", "thought"}:
        count = integer(style.get("points", 12), "Contour points", 6)
        need(count <= 40, "Contour points must be <= 40")
        if shape == "burst":
            pts = burst_points(box, count)
        else:
            # A single scalloped boundary avoids overlapping circle outlines.
            pts = []
            for i in range(count * 16):
                angle = i * math.tau / (count * 16)
                radius = 0.94 + 0.06 * math.cos(count * angle)
                pts.append((x + w / 2 + math.cos(angle) * w / 2 * radius,
                            y + h / 2 + math.sin(angle) * h / 2 * radius))
        draw.polygon(pts, fill=rgba(fill, "fill"))
        if sw:
            draw.line(pts + pts[:1], fill=rgba(stroke, "stroke"), width=sw, joint="curve")
        md.polygon(pts, fill=255)
        svg_element(group, "polygon", {"points": points_text(pts), **attrs})
    else:
        draw.ellipse(bbox, fill=rgba(fill, "fill"), outline=rgba(stroke, "stroke"), width=sw)
        md.ellipse(bbox, fill=255)
        svg_element(group, "ellipse", {"cx": x + w / 2, "cy": y + h / 2, "rx": w / 2, "ry": h / 2, **attrs})
    return mask


def draw_tail(layer, group, box, style, tail):
    x, y, w, h = box
    tx, ty = point(tail["target"], "Tail target")
    cx, cy = x + w / 2, y + h / 2
    dx, dy = tx - cx, ty - cy
    distance = math.hypot(dx, dy)
    need(distance > 1, "Tail target cannot be balloon center")
    if style["shape"] in {"ellipse", "thought"}:
        t = 1 / math.sqrt((dx / (w / 2)) ** 2 + (dy / (h / 2)) ** 2)
    else:
        t = min(w / (2 * abs(dx)) if dx else math.inf, h / (2 * abs(dy)) if dy else math.inf)
    need(t < 1, "Tail target is inside its balloon")
    bx, by = cx + dx * t * 0.94, cy + dy * t * 0.94
    if "base" in tail:
        bx, by = point(tail["base"], "Tail base")
        need(x <= bx <= x + w and y <= by <= y + h, "Tail base must be within balloon box")
    reach = number(tail.get("reach", style.get("tail_reach", 0.55)), "Tail reach")
    need(0 < reach <= 1, "Tail reach must be greater than 0 and at most 1")
    # The target is an attribution/aim anchor, not a required contact point.
    tdx, tdy = tx - bx, ty - by
    target_distance = math.hypot(tdx, tdy)
    gap = number(style.get("tail_gap", 5), "Tail gap")
    need(0 <= gap < target_distance, "Tail gap must be nonnegative and shorter than the target distance")
    actual_reach = min(reach, 1 - gap / target_distance)
    ex, ey = bx + tdx * actual_reach, by + tdy * actual_reach
    if style["shape"] in {"ellipse", "thought"}:
        outside_body = ((ex - cx) / (w / 2)) ** 2 + ((ey - cy) / (h / 2)) ** 2 > 1
    else:
        outside_body = ex < x or ex > x + w or ey < y or ey > y + h
    need(outside_body, "Tail reach is too short to leave the balloon body")
    fill, stroke = style.get("fill", "#ffffff"), style.get("stroke", "#111111")
    sw = integer(style.get("stroke_width", 2), "Tail stroke width", 0)
    attrs = {**color_attrs(fill, "fill"), **color_attrs(stroke, "stroke"), "stroke-width": sw}
    draw = ImageDraw.Draw(layer)
    if tail["kind"] == "thought":
        for fraction, radius in ((0.3, 6), (0.65, 4), (1.0, 2.5)):
            px, py = bx + (ex - bx) * fraction, by + (ey - by) * fraction
            radius *= number(style.get("thought_dot_scale", 1), "Thought dot scale")
            need(radius > 0, "Thought dot scale must be positive")
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=rgba(fill, "fill"), outline=rgba(stroke, "stroke"), width=sw)
            svg_element(group, "circle", {"cx": px, "cy": py, "r": radius, **attrs})
    else:
        width = number(style.get("tail_width", 16), "Tail width")
        need(width > 0, "Tail width must be positive")
        px, py = -tdy / target_distance * width / 2, tdx / target_distance * width / 2
        pts = [(bx + px, by + py), (ex, ey), (bx - px, by - py)]
        draw.polygon(pts, fill=rgba(fill, "fill"))
        if sw:
            draw.line(pts + pts[:1], fill=rgba(stroke, "stroke"), width=sw, joint="curve")
        svg_element(group, "polygon", {"points": points_text(pts), **attrs})
    return {"kind": tail["kind"], "target": [tx, ty], "base": [bx, by],
            "drawn_tip": [ex, ey], "requested_reach": reach, "actual_reach": actual_reach}


def text_inner(box, style):
    x, y, w, h = box
    shrink = math.sqrt(0.5) if style["shape"] in {"ellipse", "thought"} else 0.57 if style["shape"] == "burst" else 1
    x, y, w, h = x + w * (1 - shrink) / 2, y + h * (1 - shrink) / 2, w * shrink, h * shrink
    padding = style.get("padding", 12)
    if isinstance(padding, list):
        need(len(padding) == 4, "Padding must be [top,right,bottom,left]")
        top, right, bottom, left = (number(v, "padding") for v in padding)
    else:
        top = right = bottom = left = number(padding, "padding")
    need(min(top, right, bottom, left) >= 0, "Padding cannot be negative")
    need(w > left + right and h > top + bottom, "Text overflow: padding consumes balloon")
    return x + left, y + top, w - left - right, h - top - bottom


def compose_page(layout_path: str | Path, output_dir: str | Path, overwrite: bool = False) -> dict:
    layout_path = Path(layout_path).resolve()
    base, layout = layout_path.parent, read_json(layout_path)
    need(isinstance(layout, dict) and layout.get("version") == 1, "layout.version must be 1")
    page = layout.get("page", {})
    need(isinstance(page.get("id"), str) and bool(page["id"]), "page.id is required")
    size = integer(page.get("width"), "page.width"), integer(page.get("height"), "page.height")
    need(size[0] * size[1] <= 40_000_000, "Page exceeds 40 million pixels; compose smaller delivery strips or pages")
    minimum = integer(page.get("min_font_size"), "page.min_font_size")
    out = Path(output_dir).resolve()
    if not overwrite:
        need(not any((out / name).exists() for name in EXPORTS), "Output exists; use --overwrite explicitly")
    ledger_path = resolve(base, layout.get("ledger"), "ledger")
    ledger = read_json(ledger_path)
    need(isinstance(ledger, dict), "Ledger must be an object")
    all_dialogue = unique(ledger.get("dialogue"), "dialogue_id", "Ledger")
    page_rows = [r for r in all_dialogue.values() if r.get("page_id") == page["id"]]
    for row in all_dialogue.values():
        need(isinstance(row.get("page_id"), str) and bool(row["page_id"]), "Every ledger row must have page_id")
        need(row.get("kind") in KINDS and isinstance(row.get("text"), str), "Every ledger row needs a supported kind and exact text string")
        need(bool(row["text"]), "Empty dialogue must not create a balloon")
    panels = unique(layout.get("panels"), "id", "Panels")
    need(bool(panels), "At least one accepted panel is required")
    balloons = unique(layout.get("balloons", []), "id", "Balloons")
    assignments = [b.get("dialogue_id") for b in balloons.values()]
    need(len(assignments) == len(set(assignments)), "Duplicate dialogue assignment")
    need(set(assignments) == {r["dialogue_id"] for r in page_rows}, "Omitted or unexpected dialogue assignment for this page")
    if any("reading_order" in r for r in page_rows):
        orders = [integer(r.get("reading_order"), "reading_order") for r in page_rows]
        need(len(orders) == len(set(orders)), "Duplicate reading_order")
        page_rows = sorted(page_rows, key=lambda r: r["reading_order"])
    need(assignments == [r["dialogue_id"] for r in page_rows], "Balloon order must follow ledger reading order")

    root = ET.Element(f"{{{SVG}}}svg", {"width": str(size[0]), "height": str(size[1]), "viewBox": f"0 0 {size[0]} {size[1]}"})
    defs = svg_element(root, "defs")
    styles_node = svg_element(defs, "style", {"type": "text/css"})
    fonts, font_css = {}, []
    background = rgba(page.get("background", "#ffffff"), "Page background")
    page_layer = Image.new("RGBA", size, background)
    layers = [("Page", page_layer)]
    svg_element(svg_element(root, "g", {"id": "page"}), "rect", {"width": size[0], "height": size[1], **color_attrs(page.get("background", "#ffffff"), "fill")})
    art_group = svg_element(root, "g", {"id": "panel-art"})
    borders = Image.new("RGBA", size)
    border_group = svg_element(root, "g", {"id": "panel-borders"})
    critical = []
    critical_art = []
    panel_info = {}
    panel_manifest = []
    for i, panel in enumerate(panels.values()):
        art = resolve(base, panel.get("art"), f"Panel {panel['id']} art")
        acceptance = check_acceptance(panel, art, base)
        try:
            with Image.open(art) as opened:
                need(getattr(opened, "n_frames", 1) == 1, "Panel art must be a still image")
                image = opened.convert("RGBA")
                need(image.getchannel("A").getbbox() is not None, "Panel art is fully transparent")
        except OSError as exc:
            raise CompositionError(f"Cannot decode panel art: {art}") from exc
        pts = polygon(panel.get("frame"), size, f"Panel {panel['id']}")
        mask = poly_mask(size, pts)
        x, y = min(p[0] for p in pts), min(p[1] for p in pts)
        w, h = max(p[0] for p in pts) - x, max(p[1] for p in pts) - y
        crop = rect(panel.get("crop", [0, 0, *image.size]), f"Panel {panel['id']} crop")
        cx, cy, cw, ch = crop
        need(all(v.is_integer() for v in crop), "Crop coordinates must be integer source pixels")
        need(cx >= 0 and cy >= 0 and cx + cw <= image.width and cy + ch <= image.height, f"Panel {panel['id']}: invalid source crop")
        fit = panel.get("fit", "cover")
        need(fit in {"cover", "contain"}, "Panel fit must be cover or contain, never stretch")
        ax, ay = point(panel.get("align", [0.5, 0.5]), "Panel alignment")
        need(0 <= ax <= 1 and 0 <= ay <= 1, "Panel alignment must be in [0,1]")
        scale = (max if fit == "cover" else min)(w / cw, h / ch)
        ox, oy = x + (w - cw * scale) * ax, y + (h - ch * scale) * ay
        cropped = image.crop((int(cx), int(cy), int(cx + cw), int(cy + ch)))
        transformed = cropped.transform(size, Image.Transform.AFFINE, (1 / scale, 0, -ox / scale, 0, 1 / scale, -oy / scale), resample=Image.Resampling.BICUBIC)
        transformed.putalpha(ImageChops.multiply(transformed.getchannel("A"), mask))
        need(transformed.getchannel("A").getbbox() is not None, f"Panel {panel['id']}: selected crop and mask contain no visible art")
        for region_name, protected in critical_art:
            overlap = ImageChops.multiply(protected, transformed.getchannel("A"))
            need(overlap.getbbox() is None, f"Panel {panel['id']}: later panel art hides critical region {region_name}")
        layers.append((f"Panel {panel['id']}", transformed))
        clip_id = f"clip-{i}"
        svg_element(svg_element(defs, "clipPath", {"id": clip_id}), "polygon", {"points": points_text(pts)})
        svg_element(svg_element(art_group, "g", {"id": f"panel-{i}", "data-panel-id": panel["id"], "clip-path": f"url(#{clip_id})"}), "image", {"x": ox, "y": oy, "width": cw * scale, "height": ch * scale, "preserveAspectRatio": "xMidYMid meet", f"{{{XLINK}}}href": "data:image/png;base64," + base64.b64encode(png_bytes(cropped)).decode("ascii")})
        border = panel.get("border", {})
        bw = integer(border.get("width", 2), "Panel border width", 0)
        bc = border.get("color", "#111111")
        if bw:
            ImageDraw.Draw(borders).line(pts + pts[:1], fill=rgba(bc, "Panel border"), width=bw, joint="curve")
            svg_element(border_group, "polygon", {"points": points_text(pts), "fill": "none", **color_attrs(bc, "stroke"), "stroke-width": bw, "stroke-linejoin": "round"})
        subjects = unique(panel.get("subjects", []), "character_id", f"Panel {panel['id']} subjects")
        for subject in subjects.values():
            for anchor_name in ("mouth", "thought_anchor"):
                if anchor_name in subject:
                    sx, sy = point(subject[anchor_name], anchor_name)
                    need(0 <= sx < size[0] and 0 <= sy < size[1] and mask.getpixel((int(sx), int(sy))) > 127, f"Panel {panel['id']}: subject anchor lies outside panel")
        for region in panel.get("critical_regions", []):
            rx, ry, rw, rh = rect(region.get("rect"), "Critical source region")
            need(rx >= cx and ry >= cy and rx + rw <= cx + cw and ry + rh <= cy + ch, f"Panel {panel['id']}: crop hides critical region {region.get('name', '')}")
            projected = (ox + (rx - cx) * scale, oy + (ry - cy) * scale, rw * scale, rh * scale)
            region_mask = box_mask(size, projected)
            need(projected[0] >= 0 and projected[1] >= 0 and projected[0] + projected[2] <= size[0] and projected[1] + projected[3] <= size[1], f"Panel {panel['id']}: critical region leaves page")
            cut = ImageChops.subtract(region_mask, mask).point(lambda v: 255 if v > 127 else 0)
            need(cut.getbbox() is None, f"Panel {panel['id']}: panel mask hides critical region {region.get('name', '')}")
            critical_art.append((f"{panel['id']}/{region.get('name', 'unnamed')}", region_mask))
            if region.get("protect_from_lettering", True):
                critical.append((f"{panel['id']}/{region.get('name', 'unnamed')}", region_mask))
        panel_info[panel["id"]] = {"mask": mask, "subjects": subjects}
        panel_manifest.append({"panel_id": panel["id"], "art_sha256": sha256(art), "reviewed_by": acceptance["reviewed_by"], "crop": list(crop), "scale": scale, "offset": [ox, oy]})
    for region_name, protected in critical_art:
        overlap = ImageChops.multiply(protected, borders.getchannel("A"))
        need(overlap.getbbox() is None, f"Panel borders hide critical region {region_name}")
    layers.append(("Panel borders", borders))

    tails, bodies, texts, sfx = (Image.new("RGBA", size) for _ in range(4))
    tails_group = svg_element(root, "g", {"id": "balloon-tails"})
    bodies_group = svg_element(root, "g", {"id": "balloon-bodies"})
    texts_group = svg_element(root, "g", {"id": "dialogue-text"})
    sfx_group = svg_element(root, "g", {"id": "sfx"})
    style_map = layout.get("styles", {})
    need(isinstance(style_map, dict), "styles must be an object")
    text_manifest = []
    for balloon in balloons.values():
        need("text" not in balloon, "Balloon text must come only from the immutable ledger")
        row = all_dialogue[balloon["dialogue_id"]]
        pid = balloon.get("panel_id")
        need(pid in panels and pid == row.get("panel_id"), f"Balloon {balloon['id']}: panel does not match ledger")
        style_id = balloon.get("style")
        need(style_id in style_map, f"Balloon {balloon['id']}: missing style reference")
        style = style_map[style_id]
        need(isinstance(style, dict) and style.get("shape") in SHAPES, f"Balloon {balloon['id']}: unsupported custom shape; provide a supported authored style or use a manual editor")
        allowed = style.get("allowed_kinds")
        need(isinstance(allowed, list) and set(allowed) <= KINDS and row["kind"] in allowed, f"Balloon {balloon['id']}: style does not allow {row['kind']}")
        policy = style.get("tail_policy")
        need(policy in {"optional", "required", "none"}, "Style tail_policy must be optional, required, or none")
        tail = balloon.get("tail")
        tail_info = None
        need(not (policy == "required" and not tail) and not (policy == "none" and tail), f"Balloon {balloon['id']}: tail violates project grammar")
        box = rect(balloon.get("box"), f"Balloon {balloon['id']} box")
        bx, by, bw, bh = box
        need(bx >= 0 and by >= 0 and bx + bw <= size[0] and by + bh <= size[1], "Balloon extends outside page")
        speaker = row.get("speaker_id")
        if row["kind"] in {"speech", "thought", "offscreen"}:
            need(isinstance(speaker, str) and bool(speaker), f"Dialogue {row['dialogue_id']}: speaker_id is required")
        if row["kind"] in {"caption", "sfx"}:
            need(not tail, f"Dialogue {row['dialogue_id']}: caption/SFX cannot invent a speaking tail; use narration or spatial text")
        if tail:
            need(isinstance(tail, dict) and tail.get("kind") in {"on_panel", "thought", "offscreen"}, "Unsupported tail kind")
            need(tail.get("character_id") == speaker, f"Dialogue {row['dialogue_id']}: tail speaker mismatch")
            tx, ty = point(tail.get("target"), "Tail target")
            need(0 <= tx <= size[0] and 0 <= ty <= size[1], "Tail target lies outside page")
            if tail["kind"] == "offscreen":
                need(row["kind"] == "offscreen", "Offscreen tail requires offscreen ledger kind")
                if row.get("source_id"):
                    need(tail.get("source_id") == row["source_id"], "Offscreen tail source mismatch")
            else:
                need(row["kind"] != "offscreen", "Offscreen dialogue cannot point to a visible mouth")
                subject = panel_info[pid]["subjects"].get(speaker)
                need(subject is not None, f"Dialogue {row['dialogue_id']}: missing visible speaker reference")
                anchor = subject.get("thought_anchor" if tail["kind"] == "thought" else "mouth")
                need(anchor is not None, f"Dialogue {row['dialogue_id']}: missing speaker anchor")
                sx, sy = point(anchor, "Speaker anchor")
                need(math.hypot(tx - sx, ty - sy) <= 2, f"Dialogue {row['dialogue_id']}: tail target does not match speaker anchor")
            tail_layer = Image.new("RGBA", size)
            tail_info = draw_tail(tail_layer, svg_element(tails_group, "g", {"data-dialogue-id": row["dialogue_id"]}), box, style, tail)
            for region_name, protected in critical_art:
                overlap = ImageChops.multiply(protected, tail_layer.getchannel("A"))
                need(overlap.getbbox() is None, f"Balloon {balloon['id']}: tail or thought trail overlaps critical region {region_name}")
            tails.alpha_composite(tail_layer)
        body_group = svg_element(bodies_group, "g", {"data-dialogue-id": row["dialogue_id"]})
        body_mask = draw_body(bodies, body_group, box, style)
        for region_name, protected in critical:
            overlap = ImageChops.multiply(protected, body_mask)
            need(overlap.getbbox() is None, f"Balloon {balloon['id']}: lettering hides critical region {region_name}")
        font_path = resolve(base, style.get("font_path", layout.get("font_path")), "Font")
        fs = integer(style.get("font_size"), "font_size")
        need(fs >= minimum, f"Font size {fs} is below page minimum {minimum}; enlarge/reflow, never silently shrink")
        direction = style.get("direction", "ltr")
        need(direction in {"ltr", "rtl"}, "Text direction must be ltr or rtl")
        shaped = requires_shaping(row["text"]) or direction == "rtl"
        has_raqm = features.check_feature("raqm")
        need(not shaped or has_raqm, "Complex shaping requires Pillow with libraqm; use a shaping-aware editor or runtime")
        key = str(font_path), fs, has_raqm
        if key not in fonts:
            engine = ImageFont.Layout.RAQM if has_raqm else ImageFont.Layout.BASIC
            font = ImageFont.truetype(str(font_path), fs, layout_engine=engine)
            coverage = FontCoverage(font_path)
            family = f"MangakaFont{len(fonts)}"
            mime = "font/otf" if font_path.suffix.lower() == ".otf" else "font/ttf"
            font_css.append(f"@font-face{{font-family:'{family}';src:url(data:{mime};base64,{base64.b64encode(font_path.read_bytes()).decode('ascii')});}}")
            fonts[key] = font, coverage, family
        font, coverage, family = fonts[key]
        need(all(c == "\n" or coverage.has(ord(c)) for c in row["text"]), f"Dialogue {row['dialogue_id']}: supplied font is missing one or more glyphs")
        inner = text_inner(box, style)
        ix, iy, iw, ih = inner
        # Direction arguments require libraqm even for Latin; omit for BASIC.
        text_direction = direction if has_raqm else None
        lines = wrap_text(row["text"], font, iw, text_direction)
        ascent, descent = font.getmetrics()
        spacing = number(style.get("line_spacing", 1.12), "line_spacing")
        need(spacing >= 1, "line_spacing must be >= 1")
        line_height = math.ceil((ascent + descent) * spacing)
        total_height = (len(lines) - 1) * line_height + ascent + descent
        need(total_height <= ih, f"Text overflow in {row['dialogue_id']}: {total_height}px required, {ih:.1f}px available")
        align = style.get("text_align", "center")
        need(align in {"left", "center", "right"}, "text_align must be left, center, or right")
        x_text = ix + (0 if align == "left" else iw if align == "right" else iw / 2)
        anchor = {"left": "ls", "center": "ms", "right": "rs"}[align]
        svg_anchor = {"left": "start", "center": "middle", "right": "end"}[align]
        # SVG text-anchor is logical for RTL, while Pillow anchors are physical.
        if direction == "rtl" and align != "center":
            svg_anchor = {"left": "end", "right": "start"}[align]
        baseline = iy + (ih - total_height) / 2 + ascent
        text_color = style.get("text_color", "#111111")
        text_layer = Image.new("RGBA", size)
        draw = ImageDraw.Draw(text_layer)
        parent = sfx_group if row["kind"] == "sfx" else texts_group
        text_group = svg_element(parent, "g", {"data-dialogue-id": row["dialogue_id"], "data-speaker-id": speaker or "", "data-narrator-id": row.get("narrator_id") or ""})
        for i, line in enumerate(lines):
            yy = baseline + i * line_height
            draw.text((x_text, yy), line, font=font, fill=rgba(text_color, "Text color"), anchor=anchor, direction=text_direction)
            svg_element(text_group, "text", {"x": x_text, "y": yy, "font-family": family, "font-size": fs, "text-anchor": svg_anchor, "direction": direction, "unicode-bidi": "plaintext", f"{{{XML}}}space": "preserve", **color_attrs(text_color, "fill")}, line)
        outside = ImageChops.subtract(text_layer.getchannel("A"), body_mask)
        need(outside.getbbox() is None, f"Text overflow in {row['dialogue_id']}: rendered glyphs leave balloon shape")
        (sfx if row["kind"] == "sfx" else texts).alpha_composite(text_layer)
        text_manifest.append({"dialogue_id": row["dialogue_id"], "speaker_id": speaker, "narrator_id": row.get("narrator_id"), "kind": row["kind"], "text": row["text"], "rendered_lines": lines, "style": style_id, "font_sha256": sha256(font_path), "font_size": fs, "tail": tail_info})

    layers.extend([("Balloon tails", tails), ("Balloon bodies", bodies), ("Dialogue text", texts), ("Sound effects", sfx)])
    composite = Image.new("RGBA", size)
    for _, layer in layers:
        composite.alpha_composite(layer)
    lettering = Image.new("RGBA", size)
    for layer in (tails, bodies, texts, sfx):
        lettering.alpha_composite(layer)
    styles_node.text = "\n".join(font_css)
    manifest = {"version": 1, "page_id": page["id"], "ledger_sha256": sha256(ledger_path), "layout_sha256": sha256(layout_path), "panels": panel_manifest, "dialogue": text_manifest, "layers_bottom_to_top": [name for name, _ in layers], "review_limit": "Acceptance records are attestations, not proof of truthful visual review. Inspect exports at reading size and enlarged detail."}
    svg_element(root, "metadata", text=json.dumps(manifest, ensure_ascii=False))
    svg_data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    ora_data = io.BytesIO()
    ora_root = ET.Element("image", {"w": str(size[0]), "h": str(size[1]), "name": page["id"], "version": "0.0.3"})
    stack = ET.SubElement(ora_root, "stack")
    with zipfile.ZipFile(ora_data, "w") as archive:
        archive.writestr("mimetype", "image/openraster", compress_type=zipfile.ZIP_STORED)
        for i, (name, layer) in enumerate(reversed(layers)):
            file = f"data/layer{i:03d}.png"
            archive.writestr(file, png_bytes(layer), compress_type=zipfile.ZIP_DEFLATED)
            ET.SubElement(stack, "layer", {"name": name, "src": file, "x": "0", "y": "0", "opacity": "1.0", "visibility": "visible", "composite-op": "svg:src-over"})
        archive.writestr("stack.xml", ET.tostring(ora_root, encoding="utf-8", xml_declaration=True), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("mergedimage.png", png_bytes(composite), compress_type=zipfile.ZIP_DEFLATED)
        thumb = composite.copy()
        thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
        archive.writestr("Thumbnails/thumbnail.png", png_bytes(thumb), compress_type=zipfile.ZIP_DEFLATED)
    payloads = {"composite.png": png_bytes(composite), "lettering.png": png_bytes(lettering), "page.svg": svg_data, "page.ora": ora_data.getvalue(), "render_manifest.json": (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")}
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".compose-", dir=out) as temporary:
        for name, data in payloads.items():
            Path(temporary, name).write_bytes(data)
        for name in EXPORTS:
            os.replace(Path(temporary, name), out / name)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("layout", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        result = compose_page(args.layout, args.output, args.overwrite)
    except (CompositionError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"Composition failed: {exc}\n")
    print(json.dumps({"page_id": result["page_id"], "panels": len(result["panels"]), "dialogue": len(result["dialogue"]), "output": str(args.output.resolve())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

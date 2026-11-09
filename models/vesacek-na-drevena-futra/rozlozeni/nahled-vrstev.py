#!/usr/bin/env python3
"""Očíslovaný náhled skutečných extruzních drah vybraných vrstev ze 3MF."""
import json
from pathlib import Path
import re
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT = HERE / "podlozka-01-kobra-x-pla-projekt.3mf"
OUTPUT = HERE / "nahled-kritickych-vrstev.png"
REPORT = HERE / "kontrola-rezani.json"
SELECTED = {
    1: "První vrstva a brim",
    33: "Kořeny háčků v desce",
    40: "Konec desky / otvor",
    55: "Háčky nad deskou",
    270: "Hlavní háček u špičky",
    290: "Koncová vrstva",
}
COLORS = {
    "Brim": "#bc6251", "Outer wall": "#173e50",
    "Inner wall": "#357487", "Internal solid infill": "#8cb3bd",
    "Gap infill": "#8cb3bd", "Top surface": "#c58e5c",
    "Bottom surface": "#9ab8c0", "Sparse infill": "#aec9d0",
}


def paths_by_layer():
    with ZipFile(PROJECT) as archive:
        gcode = archive.read("Metadata/plate_1.gcode").decode("utf-8", errors="replace")
    paths = {number: [] for number in SELECTED}
    x = y = e = 0.0
    relative_xyz = relative_e = False
    layer, role = 0, ""
    for line in gcode.splitlines():
        if line.startswith(";LAYER_CHANGE"):
            layer += 1
        elif line.startswith(";TYPE:"):
            role = line[6:].strip()
        code = line.split(";", 1)[0].strip()
        if code == "G90": relative_xyz = False
        elif code == "G91": relative_xyz = True
        elif code == "M82": relative_e = False
        elif code == "M83": relative_e = True
        if code.startswith("G92"):
            for key, value in re.findall(r"\b([XYE])([+-]?\d*\.?\d+)", code):
                if key == "X": x = float(value)
                elif key == "Y": y = float(value)
                elif key == "E": e = float(value)
        if not code.startswith(("G0 ", "G1 ")):
            continue
        args = {key: float(value) for key, value in re.findall(
            r"\b([XYE])([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)", code)}
        next_x = (x + args.get("X", 0)) if relative_xyz else args.get("X", x)
        next_y = (y + args.get("Y", 0)) if relative_xyz else args.get("Y", y)
        next_e = args.get("E", e)
        extruded = "E" in args and (next_e > 0 if relative_e else next_e > e)
        if layer in paths and extruded and (next_x != x or next_y != y) and role != "Custom":
            paths[layer].append((x, y, next_x, next_y, role))
        x, y = next_x, next_y
        if "E" in args:
            e = e + next_e if relative_e else next_e
    assert all(paths.values()), {k: len(v) for k, v in paths.items()}
    return paths


def render(paths):
    panel_w, panel_h = 520, 605
    image = Image.new("RGB", (panel_w * 3, panel_h * 2 + 72), "#f6f9fa")
    draw = ImageDraw.Draw(image)
    font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title = ImageFont.truetype(font_file, 26)
    small = ImageFont.truetype(font_file, 18)
    draw.text((32, 17), "KOBRA X  ·  SKUTEČNÉ DRÁHY Z NASTAVENÉHO 3MF",
              fill="#173e50", font=title)
    for index, (layer, caption) in enumerate(SELECTED.items()):
        col, row = index % 3, index // 3
        ox, oy = col * panel_w, row * panel_h + 72
        draw.rounded_rectangle((ox + 12, oy + 8, ox + panel_w - 12, oy + panel_h - 8),
                               radius=12, fill="white", outline="#cfdae0", width=2)
        draw.text((ox + 30, oy + 26), "%03d  ·  %s" % (layer, caption),
                  fill="#173e50", font=title)
        draw.text((ox + 30, oy + 62), "Z = %.1f mm" % (layer * 0.2),
                  fill="#5c7480", font=small)
        x0, x1, y0, y1 = 92, 168, 75, 185
        scale = 4.10
        left = ox + (panel_w - (x1 - x0) * scale) / 2
        top = oy + 100
        right = left + (x1 - x0) * scale
        bottom = top + (y1 - y0) * scale
        draw.rectangle((left, top, right, bottom), fill="#edf2f4", outline="#bacbd1")
        xy = lambda x, y: (left + (x - x0) * scale, bottom - (y - y0) * scale)
        for x, y, nx, ny, role in paths[layer]:
            draw.line((*xy(x, y), *xy(nx, ny)), fill=COLORS.get(role, "#7693a0"), width=2)
        draw.text((ox + 30, oy + panel_h - 40), "%d extruzních úseků" % len(paths[layer]),
                  fill="#5c7480", font=small)
    image.save(OUTPUT)


def main():
    paths = paths_by_layer()
    render(paths)
    report = json.loads(REPORT.read_text())
    report["layer_preview"] = OUTPUT.name
    report["previewed_layers"] = {
        str(layer): {"z_mm": layer * 0.2, "caption": caption,
                     "extrusion_segments": len(paths[layer])}
        for layer, caption in SELECTED.items()}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("VESACEK_LAYER_PREVIEW_OK", {k: len(v) for k, v in paths.items()}, flush=True)


if __name__ == "__main__":
    main()

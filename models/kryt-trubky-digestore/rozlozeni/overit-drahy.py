#!/usr/bin/env python3
"""Audit skutečných drah uvnitř nařezaného 3MF a náhled první vrstvy.

Přepíše jen zdejší kontrola-drah.json a prvni-vrstva-01.png.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT = HERE / "kryt-podlozka-01-nastaveny-projekt.3mf"
NUM = re.compile(r"([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")

def require(value, message):
    if not value:
        raise RuntimeError(message)

def main():
    with ZipFile(PROJECT) as archive:
        gcode = archive.read("Metadata/plate_1.gcode").decode(errors="replace")
    image = Image.new("RGB", (960, 1040), "#fafbfc")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
    title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    draw.text((56, 24), "Podložka 01 · skutečná první vrstva", fill="#17333f", font=title)
    scale, margin = 3.25, 58
    xy = lambda x, y: (margin + scale * x, margin + scale * (260-y))
    draw.rectangle([xy(0,260), xy(260,0)], fill="#ecf0f1", outline="#526b76", width=3)
    draw.line([xy(0,0), xy(260,0)], fill="#b75647", width=5)

    role = "Custom"
    owner = None
    layer = -1
    absolute_xyz, relative_e = True, True
    pos = dict(X=0.0, Y=0.0, Z=0.0, E=0.0)
    roles = Counter()
    by_layer = defaultdict(int)
    first_bounds = [float("inf"), float("inf"), -float("inf"), -float("inf")]
    model_bounds = [float("inf"), float("inf"), -float("inf"), -float("inf")]
    brim_count = 0
    max_z = 0.0
    for line in gcode.splitlines():
        if line.startswith(";LAYER_CHANGE"):
            layer += 1
        elif line.startswith(";TYPE:"):
            role = line.split(":", 1)[1].strip()
        elif line.startswith("EXCLUDE_OBJECT_START NAME="):
            owner = line.split("NAME=", 1)[1]
        elif line.startswith("EXCLUDE_OBJECT_END"):
            owner = None
        command = line.split(";", 1)[0].strip()
        if not command:
            continue
        kind = command.split()[0]
        values = {key: float(value) for key, value in NUM.findall(command)}
        if kind == "G90":
            absolute_xyz = True
        elif kind == "G91":
            absolute_xyz = False
        elif kind == "M83":
            relative_e = True
        elif kind == "M82":
            relative_e = False
        elif kind == "G92":
            pos.update(values)
        elif kind in ("G0", "G1"):
            old = pos.copy()
            for axis in "XYZ":
                if axis in values:
                    pos[axis] = values[axis] if absolute_xyz else pos[axis]+values[axis]
            extruded = values.get("E", 0) if relative_e else values.get("E", pos["E"])-pos["E"]
            if "E" in values:
                pos["E"] = pos["E"]+values["E"] if relative_e else values["E"]
            if extruded <= 0 or (old["X"],old["Y"]) == (pos["X"],pos["Y"]) or role == "Custom":
                continue
            require(owner is not None, "Extrusion without cover object")
            require(0 < pos["X"] < 260 and 0 < pos["Y"] < 260,
                    "Extrusion path outside bed")
            roles[role] += 1
            by_layer[layer] += 1
            max_z = max(max_z, pos["Z"])
            for x, y in ((old["X"],old["Y"]),(pos["X"],pos["Y"])):
                bounds = first_bounds if layer == 0 else model_bounds
                bounds[0] = min(bounds[0], x)
                bounds[1] = min(bounds[1], y)
                bounds[2] = max(bounds[2], x)
                bounds[3] = max(bounds[3], y)
            if layer == 0:
                color = "#479d87" if role == "Brim" else "#213f4b"
                draw.line([xy(old["X"],old["Y"]),xy(pos["X"],pos["Y"])],
                          fill=color, width=2)
                if role == "Brim":
                    brim_count += 1

    require(layer + 1 == 490, f"Unexpected layer count {layer+1}")
    require(set(by_layer) == set(range(490)), "Missing extrusion layer")
    require(brim_count > 100, "Missing effective brim")
    require(not any("support" in name.lower() or "bridge" in name.lower()
                    for name in roles), "Unexpected supports or bridges")
    require(97.9 < max_z < 98.1, f"Unexpected printed height {max_z}")
    require(all(0 < v < 260 for v in first_bounds), "First layer outside bed")
    draw.text((58, 918), "Tmavě: kryt · zeleně: 5mm lem · výška řezu 98 mm", fill="#26424e", font=font)
    draw.text((58, 950), "Podpory ani mosty v G-code nejsou.", fill="#526b76", font=font)
    image.save(HERE / "prvni-vrstva-01.png")
    result = {"status": "toolpaths audited; no physical print",
              "layers": layer+1, "max_extrusion_z_mm": max_z,
              "roles_segments": dict(roles), "brim_segments_on_first_layer": brim_count,
              "first_layer_extrusion_bounds_xy_mm": first_bounds,
              "other_layers_extrusion_bounds_xy_mm": model_bounds,
              "all_layers_have_extrusion": True,
              "support_segments": sum(n for key, n in roles.items() if "support" in key.lower()),
              "bridge_segments": sum(n for key, n in roles.items() if "bridge" in key.lower()),
              "preview": "prvni-vrstva-01.png"}
    (HERE / "kontrola-drah.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("DUCT_COVER_PATHS_OK", result["layers"], result["brim_segments_on_first_layer"])

if __name__ == "__main__":
    main()

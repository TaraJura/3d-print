#!/usr/bin/env python3
"""Audit actual sliced G-code and render first/critical layer previews.

Reads the delivered configured 3MF. It does not touch the printer. The
checks concern file integrity, printable extent and generated paths; physical
fit, load, wall fixing, support removal and print quality remain unverified.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROJECT = HERE / "podlozka-01-nastaveny-projekt.3mf"
SLICE_AUDIT = HERE / "overeni-rezu.json"
RESULT = HERE / "kontrola-drah.json"
FIRST = HERE / "prvni-vrstva-01.png"
CRITICAL = HERE / "kriticke-vrstvy-01.png"
BED = 260.0
EXPECTED_HEIGHT = 80.0
NUM = re.compile(r"([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")
TARGET_Z = (18.2, 29.2, 48.0, 73.0)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extend(bounds, x, y):
    bounds[0] = min(bounds[0], x)
    bounds[1] = min(bounds[1], y)
    bounds[2] = max(bounds[2], x)
    bounds[3] = max(bounds[3], y)


def main():
    require(PROJECT.is_file() and SLICE_AUDIT.is_file(), "Configured project or slice audit missing")
    sliced = json.loads(SLICE_AUDIT.read_text())
    require(sha(PROJECT) == sliced["delivered"]["sha256"],
            "Configured project changed after slicing")
    with ZipFile(PROJECT) as archive:
        require(archive.testzip() is None, "Corrupt configured project")
        gcode = archive.read("Metadata/plate_1.gcode").decode(errors="replace")
    require(hashlib.sha256(gcode.encode()).hexdigest() == sliced["delivered"]["gcode_sha256"],
            "G-code does not match slicing audit")

    font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_file, 18)
    title = ImageFont.truetype(font_file, 28)
    first = Image.new("RGB", (1040, 1120), "#fafbfc")
    first_draw = ImageDraw.Draw(first)
    first_draw.text((66, 24), "Podložka 01 · skutečná první vrstva", fill="#183640", font=title)
    scale, left, top = 3.5, 65, 90
    xy_first = lambda x, y: (left + scale * x, top + scale * (BED - y))
    first_draw.rectangle((xy_first(0, BED), xy_first(BED, 0)),
                         fill="#e9eef0", outline="#55717b", width=3)
    first_draw.line((xy_first(0, 0), xy_first(BED, 0)), fill="#b85042", width=5)

    critical = Image.new("RGB", (1450, 490), "#fafbfc")
    critical_draw = ImageDraw.Draw(critical)
    critical_draw.text((37, 17), "Podložka 01 · skutečné dráhy v kritických výškách", fill="#183640", font=title)
    critical_xy = []
    for i, target in enumerate(TARGET_Z):
        ox, oy, s = 36 + i * 350, 76, 1.2
        xy = lambda x, y, ox=ox, oy=oy, s=s: (ox + s * x, oy + s * (BED - y))
        critical_xy.append(xy)
        critical_draw.rectangle((xy(0, BED), xy(BED, 0)),
                                fill="#e9eef0", outline="#55717b", width=2)
        critical_draw.text((ox, 404), f"Z ≈ {target:g} mm", fill="#263f49", font=font)
    critical_draw.text((36, 448), "Tmavě: model · oranžově: most · zeleně: podpora", fill="#536871", font=font)

    role = "Custom"
    owner = None
    layer = -1
    absolute_xyz, relative_e = True, True
    pos = dict(X=0.0, Y=0.0, Z=0.0, E=0.0)
    roles = Counter()
    by_layer = Counter()
    bridge_by_layer = Counter()
    support_by_layer = Counter()
    first_bounds = [float("inf"), float("inf"), -float("inf"), -float("inf")]
    other_bounds = [float("inf"), float("inf"), -float("inf"), -float("inf")]
    global_bounds = [float("inf"), float("inf"), -float("inf"), -float("inf")]
    max_z = 0.0
    unknown_extrusion = 0
    owner_names = set()
    for line in gcode.splitlines():
        if line.startswith(";LAYER_CHANGE"):
            layer += 1
        elif line.startswith(";TYPE:"):
            role = line.split(":", 1)[1].strip()
        elif line.startswith("EXCLUDE_OBJECT_START NAME="):
            owner = line.split("NAME=", 1)[1]
            owner_names.add(owner)
        elif line.startswith("EXCLUDE_OBJECT_END"):
            owner = None
        command = line.split(";", 1)[0].strip()
        if not command:
            continue
        kind = command.split()[0]
        values = {axis: float(value) for axis, value in NUM.findall(command)}
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
                    pos[axis] = values[axis] if absolute_xyz else pos[axis] + values[axis]
            extruded = values.get("E", 0) if relative_e else values.get("E", pos["E"]) - pos["E"]
            if "E" in values:
                pos["E"] = pos["E"] + values["E"] if relative_e else values["E"]
            if extruded <= 0 or (old["X"], old["Y"]) == (pos["X"], pos["Y"]) or role == "Custom":
                continue
            require(owner is not None, "Model extrusion outside an object")
            require(layer >= 0, "Model extrusion before first layer")
            roles[role] += 1
            by_layer[layer] += 1
            max_z = max(max_z, pos["Z"])
            if "support" in role.lower():
                support_by_layer[layer] += 1
            if "bridge" in role.lower() or "overhang" in role.lower():
                bridge_by_layer[layer] += 1
            for x, y in ((old["X"], old["Y"]), (pos["X"], pos["Y"])):
                require(0 < x < BED and 0 < y < BED,
                        f"Extrusion outside bed on layer {layer}: {(x, y)}")
                extend(global_bounds, x, y)
                extend(first_bounds if layer == 0 else other_bounds, x, y)
            if layer == 0:
                color = "#55a483" if role == "Brim" else "#243e48"
                first_draw.line((xy_first(old["X"], old["Y"]),
                                 xy_first(pos["X"], pos["Y"])), fill=color, width=2)
            for target, xy in zip(TARGET_Z, critical_xy):
                if abs(pos["Z"] - target) <= 0.105:
                    color = ("#55a483" if "support" in role.lower() else
                             "#c77239" if "bridge" in role.lower() or "overhang" in role.lower()
                             else "#243e48")
                    critical_draw.line((xy(old["X"], old["Y"]),
                                        xy(pos["X"], pos["Y"])), fill=color, width=1)
        elif kind in ("G2", "G3") and "E" in values and values["E"] > 0:
            unknown_extrusion += 1

    layers = layer + 1
    require(unknown_extrusion == 0, "Unparsed arc extrusion found")
    require(layers > 1 and set(by_layer) == set(range(layers)), "Missing extrusion layer")
    require(len(owner_names) == 1, f"Expected one physical object, found {len(owner_names)}")
    require(abs(max_z - EXPECTED_HEIGHT) <= 0.11, f"Unexpected extruded height {max_z}")
    require(roles["Brim"] > 100, "Configured brim is absent in toolpaths")
    support_segments = sum(n for r, n in roles.items() if "support" in r.lower())
    bridge_segments = sum(n for r, n in roles.items()
                          if "bridge" in r.lower() or "overhang" in r.lower())
    if sliced["supports_requested"]:
        require(support_segments > 0, "Supports enabled but no support paths generated")
    else:
        require(support_segments == 0, "Support paths generated despite disabled supports")

    first_draw.text((66, 1020), "Tmavě: model · zeleně: 5mm brim · červená: přední hrana podložky",
                    fill="#263f49", font=font)
    first_draw.text((66, 1052),
                    f"{layers} vrstev · nejmenší okraj skutečné extruze {min(global_bounds[0], global_bounds[1], BED-global_bounds[2], BED-global_bounds[3]):.1f} mm",
                    fill="#536871", font=font)
    first.save(FIRST)
    critical.save(CRITICAL)
    result = {"status": "actual local toolpaths audited; physical print and load unverified",
              "project_sha256": sha(PROJECT), "gcode_sha256": sliced["delivered"]["gcode_sha256"],
              "parts": len(owner_names), "layers": layers, "max_extrusion_z_mm": max_z,
              "all_layers_have_extrusion": True, "roles_segments": dict(roles),
              "brim_segments": roles["Brim"], "support_segments": support_segments,
              "bridge_or_overhang_segments": bridge_segments,
              "bridge_or_overhang_layer_range": [min(bridge_by_layer), max(bridge_by_layer)] if bridge_by_layer else None,
              "support_layer_range": [min(support_by_layer), max(support_by_layer)] if support_by_layer else None,
              "first_layer_bounds_xy_mm": first_bounds,
              "other_layers_bounds_xy_mm": other_bounds,
              "all_extrusion_bounds_xy_mm": global_bounds,
              "minimum_extrusion_edge_margin_mm": min(global_bounds[0], global_bounds[1],
                                                       BED-global_bounds[2], BED-global_bounds[3]),
              "warnings": sliced["delivered"].get("warnings", []),
              "first_layer_preview": FIRST.name, "critical_layers_preview": CRITICAL.name,
              "support_removal_and_horizontal_hole_fit": "not physically verified"}
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("RFID_HOLDER_TOOLPATHS_OK", layers, support_segments, bridge_segments)


if __name__ == "__main__":
    main()

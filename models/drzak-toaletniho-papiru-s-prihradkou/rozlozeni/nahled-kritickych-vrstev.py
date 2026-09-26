#!/usr/bin/env python3
"""Vykreslí vrstvy před vnitřním přemostěním a samotné dráhy z dodaných 3MF.

Čte uložený G-code, nepočítá nový řez ani nekomunikuje s tiskárnou.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
NUMBER = re.compile(r"([XYZE])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")
CASES = [
    (1, "01_Schránka", 4.0, 4.2, "Schránka, zadní stěna"),
    (1, "01_Schránka", 119.0, 119.2, "Schránka, přední hrana"),
    (2, "04_Zásuvka", 3.0, 3.2, "Zásuvka, dno"),
    (2, "04_Zásuvka", 42.0, 42.2, "Zásuvka, horní čelo"),
]
KEEP_ROLES = {
    "Internal Bridge", "Sparse infill", "Internal solid infill", "Top surface",
    "Outer wall", "Inner wall",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def collect(plate, gcode):
    targets = {(owner, z) for p, owner, previous, current, _ in CASES
               if p == plate for z in (previous, current)}
    segments = {key: [] for key in targets}
    position = dict(X=0.0, Y=0.0, Z=0.0, E=0.0)
    absolute_xyz, relative_e = True, False
    owner, role = None, "Custom"
    for line in gcode.decode(errors="replace").splitlines():
        if line.startswith(";TYPE:"):
            role = line[6:].strip()
        elif line.startswith("EXCLUDE_OBJECT_START NAME="):
            owner = line.split("NAME=", 1)[1].split("_id_", 1)[0]
        elif line.startswith("EXCLUDE_OBJECT_END"):
            owner = None
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        args = {axis: float(value) for axis, value in NUMBER.findall(code)}
        if command == "G90":
            absolute_xyz = True
        elif command == "G91":
            absolute_xyz = False
        elif command == "M83":
            relative_e = True
        elif command == "M82":
            relative_e = False
        elif command == "G92":
            position.update(args)
        elif command in ("G0", "G1"):
            previous = position.copy()
            for axis in "XYZ":
                if axis in args:
                    position[axis] = args[axis] if absolute_xyz else position[axis] + args[axis]
            extrusion = args.get("E", 0.0) if relative_e else args.get("E", position["E"]) - position["E"]
            if "E" in args:
                position["E"] = position["E"] + args["E"] if relative_e else args["E"]
            key = (owner, position["Z"])
            if (extrusion > 0 and key in segments and role in KEEP_ROLES and
                    (position["X"] != previous["X"] or position["Y"] != previous["Y"])):
                segments[key].append((previous["X"], previous["Y"], position["X"], position["Y"], role))
    return segments


def main():
    audited = json.loads((HERE / "overeni-rezu.json").read_text())
    found = {}
    sources = {}
    for plate in (1, 2):
        project = HERE / f"drzak-podlozka-{plate:02d}-nastaveny-projekt.3mf"
        expected = audited["plates"][plate - 1]["delivered"]
        require(hashlib.sha256(project.read_bytes()).hexdigest() == expected["sha256"],
                "Project changed since slicing")
        with ZipFile(project) as archive:
            gcode = archive.read("Metadata/plate_1.gcode")
        require(hashlib.sha256(gcode).hexdigest() == expected["gcode_sha256"],
                "G-code changed since audit")
        found.update({(plate, *key): value for key, value in collect(plate, gcode).items()})
        sources[str(plate)] = {"project_sha256": expected["sha256"],
                               "gcode_sha256": expected["gcode_sha256"]}

    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 23)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    image = Image.new("RGB", (1600, 1900), "#ffffff")
    draw = ImageDraw.Draw(image)
    results = []
    for index, (plate, owner, previous, current, title) in enumerate(CASES):
        row, column = divmod(index, 2)
        x_base, y_base = 40 + column * 800, 40 + row * 930
        draw.text((x_base, y_base), f"{title}: Z={previous:.1f} / {current:.1f} mm",
                  font=title_font, fill="#172e3a")
        counts = {}
        maxima = {}
        for half, z in enumerate((previous, current)):
            top = y_base + 60 + half * 400
            draw.rectangle((x_base, top, x_base + 745, top + 360), outline="#b6c7cc", width=2)
            draw.text((x_base + 10, top + 5), f"Z={z:.1f} mm", font=font, fill="#28424b")
            xy = lambda x, y: (x_base + 15 + (x - 10) * 3.2,
                               top + 340 - (y - 8) * 2.3)
            segments = found[(plate, owner, z)]
            counts[str(z)] = dict(Counter(segment[4] for segment in segments))
            for x1, y1, x2, y2, role in segments:
                if role == "Internal Bridge":
                    color, width = "#dc5b37", 2
                    maxima[str(z)] = max(maxima.get(str(z), 0.0), math.hypot(x2 - x1, y2 - y1))
                elif role == "Sparse infill":
                    color, width = "#6392a1", 1
                elif role in ("Internal solid infill", "Top surface"):
                    color, width = "#8a999d", 1
                else:
                    color, width = "#203943", 1
                draw.line((xy(x1, y1), xy(x2, y2)), fill=color, width=width)
        require(counts[str(previous)].get("Sparse infill", 0) > 0,
                f"No infill before bridge for {owner}")
        require(counts[str(current)].get("Internal Bridge", 0) > 0,
                f"No internal bridge in inspected layer for {owner}")
        draw.text((x_base, y_base + 875),
                  "Oranžově vnitřní most; modře výplň; tmavě stěny.",
                  font=font, fill="#36505a")
        results.append({"plate": plate, "object": owner, "previous_z_mm": previous,
                        "bridge_z_mm": current, "roles_by_z": counts,
                        "max_internal_bridge_segment_mm": maxima[str(current)]})
    preview = HERE / "kriticke-vrstvy.png"
    image.save(preview)
    result = {"source": sources, "cases": results, "preview": preview.name,
              "interpretation": "Previous sparse infill and next-layer internal-bridge paths shown. Visual check is required; internal bridge length is not free unsupported span."}
    (HERE / "kriticke-vrstvy.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cases": len(results), "preview": preview.name}, ensure_ascii=False))


if __name__ == "__main__":
    main()

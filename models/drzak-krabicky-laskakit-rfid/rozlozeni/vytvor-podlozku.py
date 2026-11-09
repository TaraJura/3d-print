#!/usr/bin/env python3
"""Place the single holder STL on a Kobra X plate and export geometry-only 3MF.

Run only after the CAD/STL orientation and envelope have been approved. Writes
the geometry-only plate, its numbered real-mesh preview, and a layout audit in
this directory. It never calls the slicer or a printer.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import re
import struct
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
STL = HERE.parent / "stl/drzak.stl"
GEOMETRY = HERE / "podlozka-01-geometrie.3mf"
PREVIEW = HERE / "podlozka-01.png"
AUDIT = HERE / "overeni-rozlozeni.json"
BED = 260.0
MIN_EDGE_MARGIN = 8.0  # geometric margin; a 5 mm brim is added by the process
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_stl():
    require(STL.is_file(), f"Missing CAD export: {STL}")
    raw = STL.read_bytes()
    require(len(raw) >= 84, "STL too short")
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) == 84 + 50 * count:
        points = []
        for i in range(count):
            values = struct.unpack_from("<12fH", raw, 84 + 50 * i)
            points.extend(tuple(float(v) for v in values[j:j + 3]) for j in (3, 6, 9))
    else:
        require(raw.lstrip().startswith(b"solid"), "Unsupported STL encoding")
        points = [tuple(float(n) for n in triple)
                  for triple in re.findall(rb"\bvertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)", raw)]
        require(len(points) % 3 == 0, "Malformed ASCII STL")
    require(len(points) >= 12, "Empty or implausibly small STL")
    vertices, lookup, triangles = [], {}, []
    for i in range(0, len(points), 3):
        face = []
        for p in points[i:i + 3]:
            require(all(math.isfinite(x) for x in p), "Non-finite STL coordinate")
            key = tuple(round(x, 6) for x in p)
            if key not in lookup:
                lookup[key] = len(vertices)
                vertices.append(p)
            face.append(lookup[key])
        require(len(set(face)) == 3, "Degenerate STL triangle")
        triangles.append(tuple(face))
    return vertices, triangles


def verify_mesh(vertices, triangles):
    first_face = {}
    edge_counts = Counter()
    parent = list(range(len(triangles)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for face_index, tri in enumerate(triangles):
        a, b, c = (vertices[i] for i in tri)
        cross = ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
                 (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
                 (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        require(sum(n * n for n in cross) > 1e-12, "Zero-area STL triangle")
        for j in range(3):
            edge = tuple(sorted((tri[j], tri[(j + 1) % 3])))
            edge_counts[edge] += 1
            if edge in first_face:
                parent[root(face_index)] = root(first_face[edge])
            else:
                first_face[edge] = face_index
    require(all(n == 2 for n in edge_counts.values()), "STL is not a closed 2-manifold")
    components = len({root(i) for i in range(len(triangles))})
    require(components == 1, f"Expected one connected part, found {components}")
    lo = [min(p[i] for p in vertices) for i in range(3)]
    hi = [max(p[i] for p in vertices) for i in range(3)]
    size = [hi[i] - lo[i] for i in range(3)]
    require(all(n > 0 for n in size), "STL has a zero-size axis")
    return lo, hi, size, components


def preview(vertices, triangles, translation, size, margin):
    image = Image.new("RGB", (1040, 1120), "#fafbfc")
    draw = ImageDraw.Draw(image)
    font_file = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title = ImageFont.truetype(font_file, 28)
    font = ImageFont.truetype(font_file, 19)
    number = ImageFont.truetype(font_file, 22)
    draw.text((66, 24), "Podložka 01 · Kobra X · 260 × 260 mm", fill="#19333d", font=title)
    scale, left, top = 3.5, 65, 90
    xy = lambda x, y: (left + scale * x, top + scale * (BED - y))
    draw.rectangle((xy(0, BED), xy(BED, 0)), fill="#e9eef0", outline="#55717b", width=3)
    draw.line((xy(0, 0), xy(BED, 0)), fill="#b85042", width=5)

    # Real STL triangle projection viewed from above. Higher faces cover lower
    # faces; the open centre remains visible when the actual STL has no floor.
    ordered = sorted(triangles, key=lambda t: sum(vertices[i][2] for i in t))
    zmin = min(p[2] for p in vertices)
    zspan = max(size[2], 1e-9)
    for tri in ordered:
        a, b, c = (vertices[i] for i in tri)
        z = ((a[2] + b[2] + c[2]) / 3 - zmin) / zspan
        tone = int(96 + 45 * z)
        fill = (round(tone * 0.55), round(tone * 0.90), tone)
        draw.polygon([xy(p[0] + translation[0], p[1] + translation[1])
                      for p in (a, b, c)], fill=fill)

    draw.rounded_rectangle((left + 15, top + 15, left + 58, top + 53), radius=7,
                           fill="white", outline="#29434d", width=2)
    draw.text((left + 25, top + 20), "01", fill="#18343d", font=number)
    draw.text((66, 1020), "1 fyzický díl · projekce skutečného STL · měřítko 1:1", fill="#263f49", font=font)
    draw.text((66, 1052), f"Půdorys {size[0]:.1f} × {size[1]:.1f} mm · okraj min. {margin:.1f} mm", fill="#536871", font=font)
    image.save(PREVIEW)


def xml_bytes(node):
    return ET.tostring(node, encoding="utf-8", xml_declaration=True)


def main():
    vertices, triangles = read_stl()
    lo, hi, size, components = verify_mesh(vertices, triangles)
    require(size[0] + 2 * MIN_EDGE_MARGIN <= BED and
            size[1] + 2 * MIN_EDGE_MARGIN <= BED and size[2] < BED,
            f"STL envelope {size} mm leaves insufficient Kobra X bed/brim margin")
    translation = (BED / 2 - (lo[0] + hi[0]) / 2,
                   BED / 2 - (lo[1] + hi[1]) / 2, -lo[2])
    placed_lo = [lo[i] + translation[i] for i in range(3)]
    placed_hi = [hi[i] + translation[i] for i in range(3)]
    margin = min(placed_lo[0], placed_lo[1], BED - placed_hi[0], BED - placed_hi[1])
    require(margin >= MIN_EDGE_MARGIN and abs(placed_lo[2]) < 1e-5, "Incorrect plate placement")

    ET.register_namespace("", NS)
    model = ET.Element(f"{{{NS}}}model", {"unit": "millimeter",
                                             "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, "metadata", {"name": "Title"}).text = "Držák krabičky LaskaKit RFID – podložka 01, pouze geometrie"
    ET.SubElement(model, "metadata", {"name": "Description"}).text = (
        "Jeden díl 1:1, bez tiskového procesu, filamentu a G-code. "
        "Nekombinujte s nastavenou variantou téže podložky."
    )
    resources = ET.SubElement(model, "resources")
    obj = ET.SubElement(resources, "object", {"id": "1", "type": "model", "name": "01 Držák krabičky RFID"})
    mesh = ET.SubElement(obj, "mesh")
    verts = ET.SubElement(mesh, "vertices")
    faces = ET.SubElement(mesh, "triangles")
    for p in vertices:
        ET.SubElement(verts, "vertex", {a: format(v, ".12g") for a, v in zip("xyz", p)})
    for tri in triangles:
        ET.SubElement(faces, "triangle", {f"v{i + 1}": str(v) for i, v in enumerate(tri)})
    build = ET.SubElement(model, "build")
    transform = (1, 0, 0, 0, 1, 0, 0, 0, 1, *translation)
    ET.SubElement(build, "item", {"objectid": "1", "transform": " ".join(map(str, transform))})
    types = ET.Element("Types", {"xmlns": "http://schemas.openxmlformats.org/package/2006/content-types"})
    ET.SubElement(types, "Default", {"Extension": "rels",
                                     "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(types, "Default", {"Extension": "model",
                                     "ContentType": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"})
    rels = ET.Element("Relationships", {"xmlns": "http://schemas.openxmlformats.org/package/2006/relationships"})
    ET.SubElement(rels, "Relationship", {"Target": "/3D/3dmodel.model", "Id": "rel0",
                                        "Type": "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"})
    with ZipFile(GEOMETRY, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", xml_bytes(types))
        archive.writestr("_rels/.rels", xml_bytes(rels))
        archive.writestr("3D/3dmodel.model", xml_bytes(model))
    with ZipFile(GEOMETRY) as archive:
        require(archive.testzip() is None, "Corrupt geometry 3MF")
        reloaded = ET.fromstring(archive.read("3D/3dmodel.model"))
        require(len(reloaded.findall(f"{{{NS}}}build/{{{NS}}}item")) == 1, "Wrong part count")
    preview(vertices, triangles, translation, size, margin)
    result = {"status": "geometry-only; process, supports, slice and print unverified",
              "printer": "Anycubic Kobra X 0.4 nozzle", "bed_mm": [BED, BED, BED],
              "parts": 1, "stl": str(STL), "stl_sha256": sha(STL),
              "stl_bounds_mm": {"min": lo, "max": hi, "size": size},
              "mesh_vertices": len(vertices), "mesh_triangles": len(triangles),
              "connected_components": components, "closed_manifold": True,
              "plate": {"file": GEOMETRY.name, "sha256": sha(GEOMETRY),
                        "translation_mm": translation, "placed_min_mm": placed_lo,
                        "placed_max_mm": placed_hi, "edge_margin_mm": margin,
                        "preview": PREVIEW.name}}
    AUDIT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("RFID_HOLDER_GEOMETRY_PLATE_OK", size, margin)


if __name__ == "__main__":
    main()

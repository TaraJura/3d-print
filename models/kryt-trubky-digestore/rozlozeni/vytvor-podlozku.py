#!/usr/bin/env python3
"""Jedna 3MF podložka pouze s geometrií, jedním kusem a očíslovaným náhledem.

Čte ../stl/kryt.stl. Přepíše pouze zdejší *-geometrie.3mf,
podlozka-01.png a kontrola-rozlozeni.json. Bez komunikace s tiskárnou.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
STL = ROOT / "stl/kryt.stl"
GEOMETRY = HERE / "kryt-podlozka-01-geometrie.3mf"
TRANSLATION = (55.0, 92.5, 0.0)

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_binary_stl():
    raw = STL.read_bytes()
    count = struct.unpack_from("<I", raw, 80)[0]
    require(len(raw) == 84 + 50 * count, "Expected binary STL")
    vertices, lookup, triangles = [], {}, []
    for i in range(count):
        values = struct.unpack_from("<12fH", raw, 84 + 50 * i)
        triangle = []
        for start in (3, 6, 9):
            point = tuple(float(n) for n in values[start:start + 3])
            key = tuple(round(n, 6) for n in point)
            if key not in lookup:
                lookup[key] = len(vertices)
                vertices.append(point)
            triangle.append(lookup[key])
        triangles.append(tuple(triangle))
    require(len(vertices) > 100 and all(len(set(tri)) == 3 for tri in triangles),
            "Degenerate or empty mesh")
    edges = Counter(tuple(sorted((tri[i], tri[(i+1) % 3])))
                    for tri in triangles for i in range(3))
    require(all(n == 2 for n in edges.values()), "STL is not watertight/manifold")
    lo = [min(p[i] for p in vertices) for i in range(3)]
    hi = [max(p[i] for p in vertices) for i in range(3)]
    require(all(abs(n) < 0.01 for n in lo), f"Unexpected STL origin {lo}")
    require(all(abs(hi[i] - expected) < 0.01
                for i, expected in enumerate((150, 75, 98))), f"Unexpected STL bounds {hi}")
    return vertices, triangles, lo, hi

def xml_bytes(element):
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)

def preview():
    image = Image.new("RGB", (960, 1040), "#fafbfc")
    draw = ImageDraw.Draw(image)
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title = ImageFont.truetype(font, 30)
    small = ImageFont.truetype(font, 18)
    number = ImageFont.truetype(font, 23)
    draw.text((55, 24), "Podložka 01 · Kobra X · 260 × 260 mm", fill="#19303b", font=title)
    scale, margin = 3.25, 58
    xy = lambda x, y: (margin + scale * x, margin + scale * (260 - y))
    draw.rectangle([xy(0, 260), xy(260, 0)], fill="#ebf0f2", outline="#526978", width=3)
    draw.line([xy(0, 0), xy(260, 0)], fill="#bb604d", width=5)
    # Skutečný půlkruhový půdorys podle parametrů CAD, umístěný na podložce.
    import math
    cx, cy = 75, 75
    outer = [(cx + 75 * math.cos(t), cy - 75 * math.sin(t))
             for t in [math.pi * i / 100 for i in range(101)]]
    inner = [(cx + 72 * math.cos(t), cy - 72 * math.sin(t))
             for t in [math.pi * i / 100 for i in range(100, -1, -1)]]
    polygon = [xy(x + TRANSLATION[0], y + TRANSLATION[1]) for x, y in outer + inner]
    draw.polygon(polygon, fill="#557f8c")
    draw.line(polygon + polygon[:1], fill="#29414b", width=2, joint="curve")
    x, y = xy(130, 123)
    draw.rounded_rectangle((x - 25, y - 22, x + 25, y + 22), radius=7,
                           fill="white", outline="#29414b", width=2)
    draw.text((x - 14, y - 17), "01", fill="#17303b", font=number)
    draw.text((58, 916), "01  Zaoblený kryt: 1 kus · tisk nastojato", fill="#2c434d", font=small)
    draw.text((58, 948), "Červená hrana = přední strana podložky.", fill="#526978", font=small)
    image.save(HERE / "podlozka-01.png")

def main():
    vertices, triangles, lo, hi = read_binary_stl()
    placed_lo = [lo[i] + TRANSLATION[i] for i in range(3)]
    placed_hi = [hi[i] + TRANSLATION[i] for i in range(3)]
    require(all(0 < placed_lo[i] and placed_hi[i] < 260 for i in range(2))
            and placed_lo[2] == 0 and placed_hi[2] < 260, "Outside Kobra X volume")

    ET.register_namespace("", NS)
    model = ET.Element(f"{{{NS}}}model", {"unit": "millimeter",
                                         "{http://www.w3.org/XML/1998/namespace}lang": "cs-CZ"})
    ET.SubElement(model, "metadata", {"name": "Title"}).text = "Kryt trubky digestoře – podložka 01, pouze geometrie"
    ET.SubElement(model, "metadata", {"name": "Description"}).text = (
        "1 kus 1:1, bez tiskového procesu, filamentu a G-code. K tisku použijte nastavený projekt."
    )
    resources = ET.SubElement(model, "resources")
    obj = ET.SubElement(resources, "object", {"id": "1", "type": "model", "name": "01 Zaoblený kryt"})
    mesh = ET.SubElement(obj, "mesh")
    verts = ET.SubElement(mesh, "vertices")
    tris = ET.SubElement(mesh, "triangles")
    for p in vertices:
        ET.SubElement(verts, "vertex", {a: format(v, ".12g") for a, v in zip("xyz", p)})
    for t in triangles:
        ET.SubElement(tris, "triangle", {f"v{k+1}": str(idx) for k, idx in enumerate(t)})
    build = ET.SubElement(model, "build")
    transform = (1, 0, 0, 0, 1, 0, 0, 0, 1, *TRANSLATION)
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
        require(archive.testzip() is None, "Corrupt 3MF")
        reloaded = ET.fromstring(archive.read("3D/3dmodel.model"))
        require(len(reloaded.findall(f"{{{NS}}}build/{{{NS}}}item")) == 1,
                "Wrong number of physical copies")
    preview()
    result = {"status": "geometry-only; no profile or G-code",
              "printer": "Anycubic Kobra X 0.4 nozzle", "bed_mm": [260, 260],
              "physical_pieces": 1, "plates": 1,
              "plate": {"number": 1, "file": GEOMETRY.name, "sha256": sha(GEOMETRY),
                        "copies": 1, "stl_sha256": sha(STL),
                        "translation_mm": TRANSLATION, "placed_min_mm": placed_lo,
                        "placed_max_mm": placed_hi, "mesh_vertices": len(vertices),
                        "mesh_triangles": len(triangles),
                        "edge_margin_mm": min(placed_lo[0], placed_lo[1],
                                              260-placed_hi[0], 260-placed_hi[1]),
                        "preview": "podlozka-01.png"}}
    (HERE / "kontrola-rozlozeni.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print("DUCT_COVER_PLATE_OK", result["plate"]["edge_margin_mm"])

if __name__ == "__main__":
    main()
